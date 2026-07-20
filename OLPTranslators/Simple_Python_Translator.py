from enum import Enum
import sys
from cenpylib import FileUtility

from cenpydownload import DULPythonAccuracyProfile, DULPythonBaseProfile, DULPythonJoint, DULPythonMotionProfile, DULPythonSubprogram
from cenpydownload import DULPythonProgram
from cenpydownload import DULPythonDownloadOperator
from cenpydownload import Downloader

from cenpydownload import DULPythonOperationGroup
from cenpydownload import DULPythonOperation
from cenpydownload import DULPythonEvent
from cenpydownload import DULPythonMotion
from cenpydownload import DULPythonPosition
from cenpydownload import DULPythonController
from cenpydownload import DULPythonToolProfile
from cenpyolpcore import OlpCorePythonBoolAttribute, OlpCorePythonResource, OlpCorePythonTechnology
from cenpyolpcore import OlpCorePythonIntegerAttribute
from cenpyolpcore import OlpCorePythonIntegerArrayAttribute
from cenpyolpcore import OlpCorePythonDoubleAttribute
from cenpyolpcore import OlpCorePythonDoubleArrayAttribute
from cenpyolpcore import OlpCorePythonStringAttribute
from cenpyolpcore import OlpCorePythonStringArrayAttribute
from cenpyolpcore import OlpCorePythonLiteralAttribute
from cenpyolpcore import OlpCorePythonAttribute
from cenpyolpcore import AttributeProperties

DOWNLOAD_CLASS_NAME = "SimplePython"

class Level(Enum):
   Program = 1
   Group = 2
   Operation = 3

class AttributeCache:

   def __init__(self, name: str, overrideLevel: Level, type: str):
      self._name = name
      self._overrideLevel = overrideLevel
      self._type = type

   def GetName(self):
      return self._name
   
   def GetOverrideLevel(self):
      return self._overrideLevel
   
   def GetType(self):
      return self._type
   
   def __str__(self):
        return self._name + " " + str(self._overrideLevel.name)

class SimplePython(Downloader):

   def __init__(self) -> None:
      super().__init__()
      self._outputFilePath = ""
      self._fileUtil = FileUtility()
      self._currentProgram = None
      self._currentGroup = None
      self._currentOperation = None
      self._restoreAttributeMap: list[AttributeCache] = []

   attrPropertiesMap = {
      AttributeProperties.Unset: "NoneValue",
      AttributeProperties.UserAttribute: "UserAttribute",
      AttributeProperties.ProcessAttribute: "ProcessAttribute",
      AttributeProperties.OperationAttribute: "OperationAttribute",
      AttributeProperties.OperationGroupAttribute: "OperationGroupAttribute",
      AttributeProperties.GlobalAttribute: "GlobalAttribute",
      AttributeProperties.ReadOnlyAttribute: "ReadOnlyAttribute",
      AttributeProperties.ControllerAttribute: "ControllerAttribute"
      }
   
   def bitFlagsToString(self, enum, bitMaskStringMap):
    stringFlags = ""
    number = int(enum)
    for key, value in bitMaskStringMap.items():
        if number & int(key):
            stringFlags += value + " | "
     
    if(len(stringFlags)) > 3:
       stringFlags = stringFlags[:-3]
       
    return stringFlags
   
   def keyValueString(self, key, value):
      epsilon = 1e-7
      max_unsigned_int = 2**32 - 1
     
      if isinstance(value, float):
         if (value <= epsilon - sys.float_info.max):
            stringValue = "float min negative: -1.7976931348623157e+308"
         elif (value >= sys.float_info.max - epsilon):
            stringValue = "float max: 1.7976931348623157e+308"
         else:
            stringValue = "{:.6f}".format(value)
      elif isinstance(value, list):
         # Convert the list to a string representation
         stringValue = ', '.join(map(str, value))
      # note: isinstance(value, Enum) condition does not work for Python 3.12.4 + Pybind11 2.13.1,
      # fallback solution hasattr(value, "name") will do the job for now.
      elif isinstance(value, Enum): 
         stringValue = value.name
      elif hasattr(value, "name"):
         stringValue = value.name   
      else:
          if value == max_unsigned_int: # #numpy.iinfo(numpy.uint32).max:
            stringValue = "notDefined"
          else:
            stringValue = str(value)

      quatationMark = '"'
      result = " " + key + " =" + " " + quatationMark + stringValue + quatationMark + ";"
      return result  
   
   def IsOverrideAttribute(self, operator: DULPythonDownloadOperator, attribute: OlpCorePythonAttribute, level: Level):
      attributeProperties = int(attribute.GetOlpProperty().value)
      if level == Level.Operation and ((attributeProperties & int(AttributeProperties.OperationGroupAttribute) == int(AttributeProperties.OperationGroupAttribute)) or (attributeProperties & int(AttributeProperties.GlobalAttribute) == int(AttributeProperties.GlobalAttribute))):
         return True
      if level == Level.Group and (attributeProperties & int(AttributeProperties.GlobalAttribute) == int(AttributeProperties.GlobalAttribute)):
         return True

      return False
   
   def AlreadyCached(self, name: str, level: Level):
      for cache in self._restoreAttributeMap:
         if cache.GetName() == name and cache.GetOverrideLevel() == level:
            return True
      return False

   def GetCachedAttributes(self, level: Level):
      cachedAttributes: list[AttributeCache] = []
      for cache in self._restoreAttributeMap:
         if cache.GetOverrideLevel() == level:
            cachedAttributes.append(cache)

      return cachedAttributes
   
   def GetAttributeByName(self, operator: DULPythonDownloadOperator, attributeName: str,  attributeType: str, olpObject):
      
      logger = operator.GetLogOperator()      
      logger.LogDebug("attribute type: " + attributeType)

      if OlpCorePythonBoolAttribute.__name__ in attributeType:
         return olpObject.GetBoolAttribute(attributeName, True)

      elif OlpCorePythonIntegerAttribute.__name__ in attributeType:
         return olpObject.GetIntegerAttribute(attributeName, True)
         
      elif OlpCorePythonIntegerArrayAttribute.__name__ in attributeType:
         return olpObject.GetIntegerArrayAttribute(attributeName, True)
         
      elif OlpCorePythonDoubleAttribute.__name__ in attributeType:
         return olpObject.GetDoubleAttribute(attributeName, True)
      
      elif OlpCorePythonDoubleArrayAttribute.__name__ in attributeType:
         return olpObject.GetDoubleArrayAttribute(attributeName, True)
         
      elif OlpCorePythonStringAttribute.__name__ in attributeType:
         return olpObject.GetStringAttribute(attributeName, True)
         
      elif OlpCorePythonStringArrayAttribute.__name__ in attributeType:
         return olpObject.GetStringArrayAttribute(attributeName, True)
         
      elif OlpCorePythonLiteralAttribute.__name__ in attributeType:
         return olpObject.GetLiteralAttribute(attributeName, True)
      else:
         return None
      
   def OverrideAndCacheAttribute(self, operator: DULPythonDownloadOperator, attribute, level: Level):
      logger = operator.GetLogOperator()
      overridden = self.IsOverrideAttribute(operator, attribute, level)
      if overridden:
         logger.LogDebug("Overriding Attribute " + attribute.GetName())
         if not self.AlreadyCached(attribute.GetName(), level):
            self._restoreAttributeMap.append(AttributeCache(attribute.GetName(), level, str(type(attribute))))
            logger.LogDebug("".join([str(s) for s in self._restoreAttributeMap]))
      return overridden

   def ResetAttributes(self, operator: DULPythonDownloadOperator, attributesToReset: list[AttributeCache], numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("".join([str(s) for s in attributesToReset]))
      for resetAttribute in attributesToReset:
         logger.LogDebug("reset attribute of type" + str(type(resetAttribute)))
         oldAttribute = self.GetAttributeByName(operator, resetAttribute.GetName(), resetAttribute.GetType(), self._currentProgram)
         if oldAttribute is not None:            
            self.OutputAttribute(operator, oldAttribute, numSpaces)
            self._restoreAttributeMap = list(filter(lambda cache: cache.GetName() != resetAttribute.GetName(), self._restoreAttributeMap))

   def AttributeHandler(self, operator, olpAttributeObject, level: Level, numSpaces):
      if operator is None:
         return
      
      if olpAttributeObject is None:
         return

      attributes = olpAttributeObject.GetAttributes()
      cachedAttributes = self.GetCachedAttributes(level)

      if len(attributes) == 0 and len(cachedAttributes) == 0:
         return

      resetAttributes: list[AttributeCache] = cachedAttributes
      self._fileUtil.AppendTextToFile(self._outputFilePath, " " + level._name_ + " attributes")
      if len(attributes) > 0:
         for attribute in attributes:
            self.OverrideAndCacheAttribute(operator, attribute, level)
            self.OutputAttribute(operator, attribute, numSpaces)

            resetCache = next((x for x in cachedAttributes if x.GetName() == attribute.GetName()), None)
            if resetCache is not None:
               resetAttributes = list(filter(lambda cache: cache.GetName() != attribute.GetName() and cache.GetOverrideLevel() != level, resetAttributes))

      self.ResetAttributes(operator, resetAttributes, numSpaces)
      
      self._fileUtil.AppendTextToFile(self._outputFilePath, " " + "End of attributes for " + level._name_)


   def ProgramStart(self, operator: DULPythonDownloadOperator, program : DULPythonProgram):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython ProgramStart called")
      logger.LogDebug(program.GetName())

      self._currentProgram = program
      self._fileUtil.AppendTextToFile(self._outputFilePath, "")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: program.GetName() / IsMainProgram() / GetUsedBaseProfile() / GetUsedToolProfile() / GetAttributes() → DULPythonProgram]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Program:" + " " + program.GetName() + " " + "IsMainProgram = " + str(program.IsMainProgram()))

      numSpaces =  " "

      usedBaseProfile = program.GetUsedBaseProfile()
      if usedBaseProfile:
         self.OutputBaseProfile(operator, usedBaseProfile, numSpaces)

      usedToolProfile = program.GetUsedToolProfile()
      if usedToolProfile:
         self.OutputToolProfile(operator, usedToolProfile, numSpaces)

      attributes = program.GetAttributes()
      if(len(attributes) > 0):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Program attributes")
         for attribute in attributes:
            self.OutputAttribute(operator, attribute, 2*" " + numSpaces)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End of attributes for program")

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython ProgramEnd called")
      logger.LogDebug(program.GetName())
      self._currentProgram = None

   def OperationGroupStart(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationGroupStart called")
      logger.LogDebug(operationGroup.GetName())
      self._currentGroup = operationGroup

      self._fileUtil.AppendTextToFile(self._outputFilePath, "\n" + "Operation group: "+ " " + operationGroup.GetName())
      
      numSpaces = " " * 2

      groupTechnology = operationGroup.GetTechnology()
      if groupTechnology:
        self.OutputTechnology(operator, groupTechnology, numSpaces)

      usedBaseProfile = operationGroup.GetUsedBaseProfile()
      if usedBaseProfile:
         self.OutputBaseProfile(operator, usedBaseProfile, numSpaces)

      usedToolProfile = operationGroup.GetUsedToolProfile()
      if usedToolProfile:
         self.OutputToolProfile(operator, usedToolProfile, numSpaces)

      self.AttributeHandler(operator, operationGroup, Level.Group, numSpaces)

   def OperationGroupEnd(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationGroupEnd called")
      logger.LogDebug(operationGroup.GetName())
      self._currentGroup = None

   def OperationStart(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationStart called")
      logger.LogDebug(operation.GetName())
      self._currentOperation = operation
      numSpaces = " " * 3

      self._fileUtil.AppendTextToFile(self._outputFilePath, "\n" + numSpaces + "Operation: " + operation.GetName() + " " + "OperationType = " + operation.GetOperationType().name)

      usedBaseProfile = operation.GetUsedBaseProfile()
      if usedBaseProfile:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " " + "Operation used base profile:")
         self.OutputBaseProfile(operator, usedBaseProfile, numSpaces)

      usedToolProfile = operation.GetUsedToolProfile()
      if usedToolProfile:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " " + "Operation used tool profile:")
         self.OutputToolProfile(operator, usedToolProfile, numSpaces)
      
      self.AttributeHandler(operator, operation, Level.Operation, numSpaces)

   def OperationEnd(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationEnd called")
      logger.LogDebug(operation.GetName())
      self._currentOperation = None

   def SubprogramStart(self, operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython SubprogramStart called")
      logger.LogDebug(subprogram.GetName())

   def SubProgramEnd(self, operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationEnd called")
      logger.LogDebug(subprogram.GetName())
       
   def HandleEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython HandleEvent called")
      logger.LogDebug(event.GetName())

      self.OutputEvent(operator, event)

      motions = event.GetMotions()
      for motion in motions:
         self.HandleMotion(operator, motion)

      numSpaces = " " * 5 
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "EventEnd")

   def HandleMotion(self, operator : DULPythonDownloadOperator, motion : DULPythonMotion):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython HandleMotion called")
      logger.LogDebug(motion.GetName()) 

      numSpaces = " " * 4
      eventsBefore = motion.GetEventsBefore()
      if len(eventsBefore) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Events before " + motion.GetName() + " motion")
         for event in eventsBefore:
            self.HandleEvent(operator, event)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End Events before " + motion.GetName() + " motion")

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: motion.GetMotionType() → MotionType, motion.GetPosition() → DULPythonPosition]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Motion: " + motion.GetName() + "; " + self.keyValueString("MotionType", motion.GetMotionType()))
      positionObject = motion.GetPosition()
   
      # output position info
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("PositionName", positionObject.GetName()) + 
                                                            self.keyValueString("ProcessType", positionObject.GetProcessType()) + 
                                                            self.keyValueString("TargetType", positionObject.GetTargetType()))
      if not motion.IsReferenceMotion():      
         if motion.IsLinearMotion():
            self.OutputPositonData(operator, positionObject)
         elif motion.IsCircularMotion():
            self.OutputCirc(operator, motion.GetViaPosition(), positionObject)
         else:
            self.OutputPositonData(operator, positionObject)
      
      eventsAfter = motion.GetEventsAfter()
      if len(eventsAfter) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Events after " + motion.GetName() + " motion")
         for event in eventsAfter:
            self.HandleEvent(operator, event)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End Events after " + motion.GetName() + " motion")

   def OutputPositonData(self, operator : DULPythonDownloadOperator, position : DULPythonPosition):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputPositonData called")
      logger.LogDebug(str(position.GetTargetType().name))
      logger.LogDebug(str(position.GetName()))
      
      numSpaces = " " * 5
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: position.GetXYZ() → tuple(x,y,z)] [unit: METERS — multiply by 1000 for mm]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: position.GetOrientation() → tuple(rx,ry,rz)] [unit: degrees]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Cartesian target:")

      numSpaces = numSpaces + " "
      self.OutputCoordinates(numSpaces, position.GetXYZ(), position.GetOrientation())
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Config", position.GetConfig()) + 
                                                                        self.keyValueString("Turn", position.GetTurn()))
      
      numSpaces = " " * 5
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: position.GetMainJointValues() → list[(DULPythonJoint, float)]] [unit: degrees]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: position.GetExternalJointValues() → list[(DULPythonJoint, float)]] [unit: degrees or meters for prismatic]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Joint target:")
      numSpaces = numSpaces + " "
      self.OutputJointTarget(operator, numSpaces, position.GetMainJointValues(), position.GetExternalJointValues())

   def OutputCirc(self, operator : DULPythonDownloadOperator, viaPoint : DULPythonPosition, endPoint : DULPythonPosition):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputCirc called")

      self.OutputPositonData(operator, endPoint)     
      numSpaces = " " * 4
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Via Point Position", viaPoint.GetName()))
      self.OutputPositonData(operator, viaPoint)

   def OutputEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputEvent called")
      numSpaces = " " * 5  
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: event.GetEventType() → str, event.GetInsertPosition() → InsertPosition, event.GetAttributes() → list]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("EventName", event.GetName()) + 
                                                            self.keyValueString("EventGroupName", event.GetGroupName()) + 
                                                            self.keyValueString("InsertPosition", event.GetInsertPosition()) +
                                                            self.keyValueString("EventType", event.GetEventType()))
      
      
      attributes = event.GetAttributes()
      if len(attributes) > 0:
        self._fileUtil.AppendTextToFile(self._outputFilePath, " "*6 + "Attributes set on event:")
        for attribute in attributes:
            self.OutputAttribute(operator, attribute, " "*7)
        self._fileUtil.AppendTextToFile(self._outputFilePath, " "*6 + "End of attributes for event")

   def Initialize(self, operator : DULPythonDownloadOperator):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython Initialize called")
        
      controller = operator.GetController()
      program = controller.GetActiveProgram()
      outputDir = controller.GetOutputDirectory()
      self._outputFilePath = outputDir + "\\" + program.GetName() + ".txt" 
      logger.LogDebug(self._outputFilePath)
   
   def OutputHeader(self, operator : DULPythonDownloadOperator, controller : DULPythonController):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputHeader called")

      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: operator.GetCurrentLanguage() → str]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Current language: " + operator.GetCurrentLanguage())

      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: operator.GetController() → DULPythonController]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Controller: " + controller.GetName())
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Model: " + controller.GetModel())
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Series: " + controller.GetSeries())
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Manufacturer: " + controller.GetManufacturer())
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Controller Type: " + controller.GetControllerType().name)
      
      activeProgramName = "None"
      activeProgram = controller.GetActiveProgram()
      if(activeProgram):
         activeProgramName = activeProgram.GetName()
      
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Active program: " + activeProgramName)


      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetConnectedJoints() → list[DULPythonJoint]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Controller connected joints: ")
      numSpaces = " "
      connectedJoints = controller.GetConnectedJoints()
      for joint in connectedJoints:
        jointNameKey = "JointName"
        if joint.IsExternal():
            jointNameKey = "AuxJointName"
        self.OutputJointInfo(operator, joint, jointNameKey, numSpaces, "")
          
      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetToolProfiles() → list[DULPythonToolProfile]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Tool profiles: ")
      toolProfiles = controller.GetToolProfiles()
      for toolProfile in toolProfiles:
         self.OutputToolProfile(operator, toolProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetBaseProfiles() → list[DULPythonBaseProfile]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Base profiles: ")
      baseProfiles = controller.GetBaseProfiles()
      for baseProfile in baseProfiles:
         self.OutputBaseProfile(operator, baseProfile, numSpaces)
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetAccuracyProfiles() → list[DULPythonAccuracyProfile]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Accuracy profiles: ")
      accuracyProfiles = controller.GetAccuracyProfiles()
      for accuracyProfile in accuracyProfiles:
         self.OutputAccuracyProfile(operator, accuracyProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetMotionProfiles() → list[DULPythonMotionProfile]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Motion profiles: ")
      motionProfiles = controller.GetMotionProfiles()
      for motionProfile in motionProfiles:
          self.OutputMotionProfile(operator, motionProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetAttributes() → list[OlpCorePythonAttribute]]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Controller attributes: ")
      attributes = controller.GetAttributes()
      for attribute in attributes:
         self.OutputAttribute(operator, attribute, numSpaces)
      self._fileUtil.AppendTextToFile(self._outputFilePath, " End of Controller attributes")
      resources = controller.GetResources()
      if len(resources) > 0:
         logger.LogDebug("Number of resources " + str(len(resources)))

         self._fileUtil.AppendTextToFile(self._outputFilePath, "# [API: controller.GetResources() → list[OlpCorePythonResource]]")
         self._fileUtil.AppendTextToFile(self._outputFilePath, " Controller resources list: ")

         for resource in resources:
            self.OutputResource(operator, resource, numSpaces)

            attributes = resource.GetAttributes()
            if len(attributes) > 0:
               for attribute in attributes:
                  self._fileUtil.AppendTextToFile(self._outputFilePath, " Attributes:")
                  self.OutputAttribute(operator, attribute, numSpaces + " ")
   
   def OutputJointInfo(self, operator : DULPythonDownloadOperator, joint : DULPythonJoint, jointType, numSpaces, value: str):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputJointInfo called")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString(jointType, joint.GetName()) + 
                                                            self.keyValueString("GroupIndex", joint.GetJointGroupIndex()) + 
                                                            self.keyValueString("DOFNumber", joint.GetDofNumber()) + 
                                                            self.keyValueString("JointIndex", joint.GetJointIndex()) + 
                                                            self.keyValueString("PortName", joint.GetPortName()) +
                                                            self.keyValueString("Role", joint.GetJointRole()) +
                                                            self.keyValueString("Unit", joint.GetUnit())+
                                                            self.keyValueString("Value", value) )
      
   def CreateOutputFile(self, operator : DULPythonDownloadOperator):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython CreateOutputFile called")


   def CloseOutputFile(self, operator : DULPythonDownloadOperator):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython CloseOutputFile called")
      operator.AddOutputFilePath(self._outputFilePath)

   def OutputCoordinates(self, motionTypePrefix, xyz, angles):
      
      self._fileUtil.AppendTextToFile(self._outputFilePath,  motionTypePrefix + self.keyValueString ("X", xyz[0]) + self.keyValueString ("Y", xyz[1]) + self.keyValueString ("Z", xyz[2]) +
                                                              self.keyValueString ("Rx", angles[0]) + self.keyValueString ("Ry", angles[1]) + self.keyValueString ("Rz", angles[2]))

   def OutputJointTarget(self, operator : DULPythonDownloadOperator, numSpaces, mainJointsValues, extJointValues):
     for joint in mainJointsValues:
         self.OutputJointInfo(operator, joint[0], "MainJoint", numSpaces, joint[1])

     for ext in extJointValues:
         self.OutputJointInfo(operator, ext[0], "ExtJoint", numSpaces, ext[1])

   def OutputAttribute(self, operator : DULPythonDownloadOperator, attribute, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputAttribute called")    

      numSpaces += " "
      stringOlpProperty = self.bitFlagsToString(attribute.GetOlpProperty(), self.attrPropertiesMap)
      
      if OlpCorePythonBoolAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValue()) + 
                                                               self.keyValueString("Type", "BoolAttribute") + 
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))

      elif OlpCorePythonIntegerAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValue()) + 
                                                               self.keyValueString("Type", "IntAttribute") +
                                                               self.keyValueString("Min", attribute.GetMinimum()) + 
                                                               self.keyValueString("Max", attribute.GetMaximum()) +
                                                               self.keyValueString("StepSize", attribute.GetStepSize()) + 
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
         
      elif OlpCorePythonIntegerArrayAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValues()) + 
                                                               self.keyValueString("Type", "IntArrayttribute") +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
         
      elif OlpCorePythonDoubleAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValue()) + 
                                                               self.keyValueString("Type", "DoubleAttribute") +
                                                               self.keyValueString("Min", attribute.GetMinimum()) + 
                                                               self.keyValueString("Max", attribute.GetMaximum()) +
                                                               self.keyValueString("StepSize", attribute.GetStepSize()) +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
      
      elif OlpCorePythonDoubleArrayAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValues()) + 
                                                               self.keyValueString("Type", "DoubleArrayAttribute") +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
         
      elif OlpCorePythonStringAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValue()) + 
                                                               self.keyValueString("Type", "StringAttribute") +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
         
      elif OlpCorePythonStringArrayAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValues()) + 
                                                               self.keyValueString("Type", "StringArrayAttribute") +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", attribute.GetOlpProperty()))
         
      elif OlpCorePythonLiteralAttribute.__name__ in str(type(attribute)):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Name", attribute.GetName()) + 
                                                               self.keyValueString("Value", attribute.GetValue()) + 
                                                               self.keyValueString("Type", "LiteralAttribute") +
                                                               self.keyValueString("Values", attribute.GetValues()) +
                                                               self.keyValueString("Index", attribute.GetIndex()) +
                                                               self.keyValueString("GroupName", attribute.GetGroupName()) + 
                                                               self.keyValueString("ReadOnly", attribute.GetReadOnly()) +
                                                               self.keyValueString("ValueUnitType", attribute.GetValueUnitType()) +
                                                               self.keyValueString("GetOlpProperty", stringOlpProperty))
      else:
         logger.LogDebug("SimplePython could not output attribute")
        
   def OutputToolProfile(self, operator : DULPythonDownloadOperator, profile : DULPythonToolProfile, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputToolProfile called")

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: profile.GetXYZ() / GetOrientation() → DULPythonToolProfile] [XYZ: meters, Angles: degrees]")
      position = profile.GetXYZ()
      orientation = profile.GetOrientation()
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString ("ToolProfile", profile.GetName()) + 
                                                                        self.keyValueString ("ProfileIndex", profile.GetIndex()) + 
                                                                        self.keyValueString ("ToolType", profile.GetToolType()) + 
                                                                        self.keyValueString ("X", position[0]) + self.keyValueString ("Y", position[1]) + self.keyValueString ("Z", position[2]) +
                                                                        self.keyValueString ("Rx", orientation[0]) + self.keyValueString ("Ry", orientation[1]) + self.keyValueString ("Rz", orientation[2])) 
      
      
   def OutputBaseProfile(self, operator : DULPythonDownloadOperator, profile : DULPythonBaseProfile, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputBaseProfile called")
      
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: profile.GetXYZ() / GetOrientation() → DULPythonBaseProfile] [XYZ: meters, Angles: degrees]")
      position = profile.GetXYZ()
      orientation = profile.GetOrientation()

      refeProfileName = "None"
      referenceProfile = profile.GetReferenceProfile()
      if referenceProfile:
         refeProfileName = referenceProfile.GetName()

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString ("BaseProfile", profile.GetName()) + 
                                                                        self.keyValueString ("ProfileIndex", profile.GetIndex()) + 
                                                                        self.keyValueString ("ReferenceProfile", refeProfileName) + 
                                                                        self.keyValueString ("X", position[0]) + self.keyValueString ("Y", position[1]) + self.keyValueString ("Z", position[2]) +
                                                                        self.keyValueString ("Rx", orientation[0]) + self.keyValueString ("Ry", orientation[1]) + self.keyValueString ("Rz", orientation[2])) 
      

   def OutputAccuracyProfile(self, operator : DULPythonDownloadOperator, profile : DULPythonAccuracyProfile, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython AccuracyProfile called")
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: profile.GetValue() / GetUnit() → DULPythonAccuracyProfile] [value: meters]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("AccuracyProfile", profile.GetName()) + 
                                                                        self.keyValueString("AccuracyCriteria", profile.GetAccuracyCriteria()) + 
                                                                        self.keyValueString("FlyBy", profile.GetProfileFlyBy()) + 
                                                                        self.keyValueString("Value", profile.GetValue()) + 
                                                                        self.keyValueString("Unit", profile.GetUnit())) 
      
   def OutputMotionProfile(self, operator : DULPythonDownloadOperator, profile : DULPythonMotionProfile, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputMotionProfile called")
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "# [API: profile.GetSpeedValue() / GetAccelValue() → DULPythonMotionProfile] [speed: m/s or %, accel: %]")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("MotionProfile", profile.GetName()) + 
                                                                        self.keyValueString("MotionProfileBasis", profile.GetMotionProfileBasis()) + 
                                                                        self.keyValueString("ProfileType", profile.GetMotionProfileType()) + 
                                                                        self.keyValueString("SpeedValue", profile.GetSpeedValue()) + 
                                                                        self.keyValueString("SpeedUnit", profile.GetSpeedUnit()) +
                                                                        self.keyValueString("AccelerationValue", profile.GetAccelValue()) + 
                                                                        self.keyValueString("AccelerationUnit", profile.GetAccelUnit())) 
      
   def OutputTechnology(self, operator : DULPythonDownloadOperator, technology : OlpCorePythonTechnology, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputTechnology called") 

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("TechnologyName", technology.GetName()))
         
   def OutputResource(self, operator : DULPythonDownloadOperator, resource : OlpCorePythonResource, numSpaces):
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputResource called") 
        
      resName = resource.GetName()
      logger.LogDebug(resName) 

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("ResourceName", resource.GetName()) +
                                                                        self.keyValueString("ItemType", resource.GetItemType()) +
                                                                        self.keyValueString("ItemSubType", resource.GetItemSubType()) +
                                                                        self.keyValueString("Manufacturer", resource.GetManufacturer()) +
                                                                        self.keyValueString("Model", resource.GetModel()) +
                                                                        self.keyValueString("Series", resource.GetSeries()))
       
      resourceAttributes = resource.GetAttributes()
      if(len(resourceAttributes) > 0):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Resource Attributes:")
         numSpaces += " "
         for attribute in resourceAttributes:
            self.OutputAttribute(operator, attribute, numSpaces)
                                                  
   def WriteOutputFile(self, operator : DULPythonDownloadOperator):
      pass
