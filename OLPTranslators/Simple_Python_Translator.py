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
from cenpyolpcore import AttributeProperties

DOWNLOAD_CLASS_NAME = "SimplePython"

class SimplePython(Downloader):

   def __init__(self) -> None:
      super().__init__()
      self._outputFilePath = ""
      self._fileUtil = FileUtility()

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
   
   def ProgramStart(self, Operator: DULPythonDownloadOperator, program : DULPythonProgram):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython ProgramStart called")
      logger.LogDebug(program.GetName())

      self._fileUtil.AppendTextToFile(self._outputFilePath, "")
      self._fileUtil.AppendTextToFile(self._outputFilePath, "Program:" + " " + program.GetName() + " " + "IsMainProgram = " + str(program.IsMainProgram()))

      numSpaces =  " "

      usedBaseProfile = program.GetUsedBaseProfile()
      if usedBaseProfile:
         self.OutputBaseProfile(Operator, usedBaseProfile, numSpaces)

      usedToolProfile = program.GetUsedToolProfile()
      if usedToolProfile:
         self.OutputToolProfile(Operator, usedToolProfile, numSpaces)

      attributes = program.GetAttributes()
      if(len(attributes) > 0):
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Program attributes")
         for attribute in attributes:
            self.OutputAttribute(Operator, attribute, 2*" " + numSpaces)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End of attributes for program")

   def ProgramEnd(self, Operator : DULPythonDownloadOperator, program : DULPythonProgram):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython ProgramEnd called")
      logger.LogDebug(program.GetName())

   def OperationGroupStart(self, Operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationGroupStart called")
      logger.LogDebug(operationGroup.GetName())

      self._fileUtil.AppendTextToFile(self._outputFilePath, "\n" + "Operation group: "+ " " + operationGroup.GetName())
      
      numSpaces = " " * 2

      groupTechnology = operationGroup.GetTechnology()
      if groupTechnology:
        self.OutputTechnology(Operator, groupTechnology, numSpaces)

      usedBaseProfile = operationGroup.GetUsedBaseProfile()
      if usedBaseProfile:
         self.OutputBaseProfile(Operator, usedBaseProfile, numSpaces)

      usedToolProfile = operationGroup.GetUsedToolProfile()
      if usedToolProfile:
         self.OutputToolProfile(Operator, usedToolProfile, numSpaces)

      attributes = operationGroup.GetAttributes()
      if len(attributes) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, " " + "Group attributes")
         for attribute in attributes:
            self.OutputAttribute(Operator, attribute, numSpaces)
            
         self._fileUtil.AppendTextToFile(self._outputFilePath, " " + "End of attributes for operation group")

   def OperationGroupEnd(self, Operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationGroupEnd called")
      logger.LogDebug(operationGroup.GetName())

   def OperationStart(self, Operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationStart called")
      logger.LogDebug(operation.GetName())
      numSpaces = " " * 3

      self._fileUtil.AppendTextToFile(self._outputFilePath, "\n" + numSpaces + "Operation: " + operation.GetName() + " " + "OperationType = " + operation.GetOperationType().name)

      usedBaseProfile = operation.GetUsedBaseProfile()
      if usedBaseProfile:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " " + "Operation used base profile:")
         self.OutputBaseProfile(Operator, usedBaseProfile, numSpaces)

      usedToolProfile = operation.GetUsedToolProfile()
      if usedToolProfile:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " " + "Operation used tool profile:")
         self.OutputToolProfile(Operator, usedToolProfile, numSpaces)
      
      attributes = operation.GetAttributes()
      if len(attributes) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, " " + "Operation Attributes:")
         for attribute in attributes:
            self.OutputAttribute(Operator, attribute, numSpaces)
            
         self._fileUtil.AppendTextToFile(self._outputFilePath, " " + "End of attributes for operation")

   def OperationEnd(self, Operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationEnd called")
      logger.LogDebug(operation.GetName())

   def SubprogramStart(self, Operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython SubprogramStart called")
      logger.LogDebug(subprogram.GetName())

   def SubProgramEnd(self, Operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OperationEnd called")
      logger.LogDebug(subprogram.GetName())
       
   def HandleEvent(self, Operator : DULPythonDownloadOperator, event : DULPythonEvent):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython HandleEvent called")
      logger.LogDebug(event.GetName())

      self.OutputEvent(Operator, event)

      motions = event.GetMotions()
      for motion in motions:
         self.HandleMotion(Operator, motion)

      numSpaces = " " * 5 
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "EventEnd")

   def HandleMotion(self, Operator : DULPythonDownloadOperator, motion : DULPythonMotion):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython HandleMotion called")
      logger.LogDebug(motion.GetName()) 

      #self._fileUtil.AppendTextToFile(self._outputFilePath, "")

      numSpaces = " " * 4
      eventsBefore = motion.GetEventsBefore()
      if len(eventsBefore) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Events before " + motion.GetName() + " motion")
         for event in eventsBefore:
            self.HandleEvent(Operator, event)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End Events before " + motion.GetName() + " motion")

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Motion: " + motion.GetName() + "; " + self.keyValueString("MotionType", motion.GetMotionType()))
      positionObject = motion.GetPosition()
   
      # output position info
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("PositionName", positionObject.GetName()) + 
                                                            self.keyValueString("ProcessType", positionObject.GetProcessType()) + 
                                                            self.keyValueString("TargetType", positionObject.GetTargetType()))
      if not motion.IsReferenceMotion():      
         if motion.IsLinearMotion():
            self.OutputPositonData(Operator, positionObject)
         elif motion.IsCircularMotion():
            self.OutputCirc(Operator, motion.GetViaPosition(), positionObject)
         else:
            self.OutputPositonData(Operator, positionObject)
      
      eventsAfter = motion.GetEventsAfter()
      if len(eventsAfter) > 0:
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " Events after " + motion.GetName() + " motion")
         for event in eventsAfter:
            self.HandleEvent(Operator, event)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + " End Events after " + motion.GetName() + " motion")

   def OutputPositonData(self, Operator : DULPythonDownloadOperator, position : DULPythonPosition):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputPositonData called")
      logger.LogDebug(str(position.GetTargetType().name))
      logger.LogDebug(str(position.GetName()))
      
      numSpaces = " " * 5
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Cartesian target:")

      numSpaces = numSpaces + " "
      self.OutputCoordinates(numSpaces, position.GetXYZ(), position.GetOrientation())
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Config", position.GetConfig()) + 
                                                                        self.keyValueString("Turn", position.GetTurn()))
      
      numSpaces = " " * 5
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + "Joint target:")
      numSpaces = numSpaces + " "
      self.OutputJointTarget(Operator, numSpaces, position.GetMainJointValues(), position.GetExternalJointValues())

   def OutputCirc(self, Operator : DULPythonDownloadOperator, viaPoint : DULPythonPosition, endPoint : DULPythonPosition):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputCirc called")
   
      numSpaces = " " * 5
      self.OutputPositonData(Operator, viaPoint)
      self.OutputPositonData(Operator, endPoint)

   def OutputEvent(self, Operator : DULPythonDownloadOperator, event : DULPythonEvent):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputEvent called")
      numSpaces = " " * 5  
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("EventName", event.GetName()) + 
                                                            self.keyValueString("EventGroupName", event.GetGroupName()) + 
                                                            self.keyValueString("InsertPosition", event.GetInsertPosition()) +
                                                            self.keyValueString("EventType", event.GetEventType()))
      
      
      attributes = event.GetAttributes()
      if len(attributes) > 0:
        self._fileUtil.AppendTextToFile(self._outputFilePath, " "*6 + "Attributes set on event:")
        for attribute in attributes:
            self.OutputAttribute(Operator, attribute, " "*7)
        self._fileUtil.AppendTextToFile(self._outputFilePath, " "*6 + "End of attributes for event")

   def Initialize(self, Operator : DULPythonDownloadOperator):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython Initialize called")
        
      controller = Operator.GetController()
      program = controller.GetActiveProgram()
      outputDir = controller.GetOutputDirectory()
      self._outputFilePath = outputDir + "\\" + program.GetName() + ".txt" 
      logger.LogDebug(self._outputFilePath)
   
   def OutputHeader(self, Operator : DULPythonDownloadOperator, controller : DULPythonController):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputHeader called")

      self._fileUtil.AppendTextToFile(self._outputFilePath, "Current language: " + Operator.GetCurrentLanguage())

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


      self._fileUtil.AppendTextToFile(self._outputFilePath, "Controller connected joints: ")
      numSpaces = " "
      connectedJoints = controller.GetConnectedJoints()
      for joint in connectedJoints:
        jointNameKey = "JointName"
        if joint.IsExternal():
            jointNameKey = "AuxJointName"
        self.OutputJointInfo(Operator, joint, jointNameKey, numSpaces)
          
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Tool profiles: ")
      toolProfiles = controller.GetToolProfiles()
      for toolProfile in toolProfiles:
         self.OutputToolProfile(Operator, toolProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, " Base profiles: ")
      baseProfiles = controller.GetBaseProfiles()
      for baseProfile in baseProfiles:
         self.OutputBaseProfile(Operator, baseProfile, numSpaces)
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, " Accuracy profiles: ")
      accuracyProfiles = controller.GetAccuracyProfiles()
      for accuracyProfile in accuracyProfiles:
         self.OutputAccuracyProfile(Operator, accuracyProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, " Motion profiles: ")
      motionProfiles = controller.GetMotionProfiles()
      for motionProfile in motionProfiles:
          self.OutputMotionProfile(Operator, motionProfile, numSpaces)

      self._fileUtil.AppendTextToFile(self._outputFilePath, " Controller attributes: ")
      attributes = controller.GetAttributes()
      for attribute in attributes:
         self.OutputAttribute(Operator, attribute, numSpaces)
      self._fileUtil.AppendTextToFile(self._outputFilePath, " End of Controller attributes")
      resources = controller.GetResources()
      if len(resources) > 0:
         logger.LogDebug("Number of resources " + str(len(resources)))

         self._fileUtil.AppendTextToFile(self._outputFilePath, " Controller resources list: ")

         for resource in resources:
            self.OutputResource(Operator, resource, numSpaces)

      #TODO: handle resource ports
      # ports = resource.GetPorts()
      # if len(ports) > 0:
      #       self._fileUtil.AppendTextToFile(self._outputFilePath, " Ports:")

      attributes = resource.GetAttributes()
      if len(attributes) > 0:
         for attribute in attributes:
            self._fileUtil.AppendTextToFile(self._outputFilePath, " Attributes:")
            self.OutputAttribute(Operator, attribute, numSpaces + " ")
   
   def OutputJointInfo(self, Operator : DULPythonDownloadOperator, joint : DULPythonJoint, jointType, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputJointInfo called")
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString(jointType, joint.GetName()) + 
                                                            self.keyValueString("GroupIndex", joint.GetJointGroupIndex()) + 
                                                            self.keyValueString("DOFNumber", joint.GetDofNumber()) + 
                                                            self.keyValueString("JointIndex", joint.GetJointIndex()) + 
                                                            self.keyValueString("PortName", joint.GetPortName()) +
                                                            self.keyValueString("Role", joint.GetJointRole()) +
                                                            self.keyValueString("Unit", joint.GetUnit()))
      
   def CreateOutputFile(self, Operator : DULPythonDownloadOperator):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython CreateOutputFile called")


   def CloseOutputFile(self, Operator : DULPythonDownloadOperator):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython CloseOutputFile called")
      Operator.AddOutputFilePath(self._outputFilePath)

   def OutputCoordinates(self, motionTypePrefix, xyz, angles):
      
      self._fileUtil.AppendTextToFile(self._outputFilePath,  motionTypePrefix + self.keyValueString ("X", xyz[0]) + self.keyValueString ("Y", xyz[1]) + self.keyValueString ("X", xyz[2]) +
                                                              self.keyValueString ("Rx", angles[0]) + self.keyValueString ("Ry", angles[1]) + self.keyValueString ("Rz", angles[2]))
      #self._fileUtil.AppendTextToFile(self._outputFilePath, "")

   def OutputJointTarget(self, Operator : DULPythonDownloadOperator, numSpaces, mainJointsValues, extJointValues):
     for joint in mainJointsValues:
         self.OutputJointInfo(Operator, joint[0], "MainJoint", numSpaces)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Value", joint[1]))

     for ext in extJointValues:
         self.OutputJointInfo(Operator, ext[0], "ExtJoint", numSpaces)
         self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("Value", ext[1]))


   def OutputAttribute(self, Operator : DULPythonDownloadOperator, attribute, numSpaces):
      logger = Operator.GetLogOperator()
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
                                                               self.keyValueString("ReaOnly", attribute.GetReadOnly()) +
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
                                                               self.keyValueString("ReaOnly", attribute.GetReadOnly()) +
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
        
   def OutputToolProfile(self, Operator : DULPythonDownloadOperator, profile : DULPythonToolProfile, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputToolProfile called")

      position = profile.GetXYZ()
      orientation = profile.GetOrientation()
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString ("ToolProfile", profile.GetName()) + 
                                                                        self.keyValueString ("ProfileIndex", profile.GetIndex()) + 
                                                                        self.keyValueString ("ToolType", profile.GetToolType()) + 
                                                                        self.keyValueString ("X", position[0]) + self.keyValueString ("Y", position[1]) + self.keyValueString ("Z", position[2]) +
                                                                        self.keyValueString ("Rx", orientation[0]) + self.keyValueString ("Ry", orientation[1]) + self.keyValueString ("Rz", orientation[2])) 
      
      
   def OutputBaseProfile(self, Operator : DULPythonDownloadOperator, profile : DULPythonBaseProfile, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputBaseProfile called")
      
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
      

   def OutputAccuracyProfile(self, Operator : DULPythonDownloadOperator, profile : DULPythonAccuracyProfile, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython AccuracyProfile called")
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("AccuracyProfile", profile.GetName()) + 
                                                                        self.keyValueString("AccuracyCriteria", profile.GetAccuracyCriteria()) + 
                                                                        self.keyValueString("FlyBy", profile.GetProfileFlyBy()) + 
                                                                        self.keyValueString("Value", profile.GetValue()) + 
                                                                        self.keyValueString("Unit", profile.GetUnit())) 
      
   def OutputMotionProfile(self, Operator : DULPythonDownloadOperator, profile : DULPythonMotionProfile, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputMotionProfile called")
   
      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("MotionProfile", profile.GetName()) + 
                                                                        self.keyValueString("MotionProfileBasis", profile.GetMotionProfileBasis()) + 
                                                                        self.keyValueString("ProfileType", profile.GetMotionProfileType()) + 
                                                                        self.keyValueString("SpeedValue", profile.GetSpeedValue()) + 
                                                                        self.keyValueString("SpeedUnit", profile.GetSpeedUnit()) +
                                                                        self.keyValueString("AccelerationValue", profile.GetAccelValue()) + 
                                                                        self.keyValueString("AccelerationUnit", profile.GetAccelUnit())) 
      
   def OutputTechnology(self, Operator : DULPythonDownloadOperator, technology : OlpCorePythonTechnology, numSpaces):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputTechnology called") 

      self._fileUtil.AppendTextToFile(self._outputFilePath, numSpaces + self.keyValueString("TechnologyName", technology.GetName()))
         
   def OutputResource(self, Operator : DULPythonDownloadOperator, resource : OlpCorePythonResource, numSpaces):
      logger = Operator.GetLogOperator()
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
            self.OutputAttribute(Operator, attribute, numSpaces)
                                                  
   def WriteOutputFile(self, Operator : DULPythonDownloadOperator):
      pass
