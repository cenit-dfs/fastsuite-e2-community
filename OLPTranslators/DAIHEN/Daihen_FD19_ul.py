"""
COPYRIGHT Cenit AG 2025
   Production ready OTC-DAIHEN Uploader
"""

import sys
from cenpyupload import *
from cenpyolpcore import *
from cenpydownload import *
from dataclasses import dataclass, field
import re
from io import TextIOWrapper
from enum import Enum

UPLOAD_CLASS_NAME = "DaihenFD19Uploader"

#MotionType
MOTIONTYPE_LIN = 1
MOTIONTYPE_CIR = 2
MOTIONTYPE_PTP = 3

#TargetType
TARGETTYPE_CARTESIAN = 0
TARGETTYPE_JOINT     = 1

#Event insert Position
TPINSERTPOS_INSERTBEFORE = 0
TPINSERTPOS_INSERTAFTER  = 1
TPINSERTPOS_INSERTNONE   = 2
TPINSERTPOS_INHERIT      = 3

MULTILINETEXT_FLUSH_BEFORE = 0
MULTILINETEXT_FLUSH_AFTER = 1
MULTILINETEXT_FLUSH_ALL = 3

class AttributeLevel(Enum):
    Program = 1,
    Group = 2,
    Operation = 3,
    Event =4


@dataclass
class MovexLine():
   def __init__(self, line: str):
      """
      Analysis the MOVEX Command Line and write all on an Object
      """
      # MOVEX A=8,AC=0,SM=0,M1X,L,(357.335, 340.000, 40.487, 0.00, -20.00, 135.00),S=60.0,H=1,MS...
      self.isValid = False
      self.accuracyValue = int(5)
      self.accuracyHasP = False
      self.accelerationValue = int(99)
      self.smoothValue = int(88)
      self.hasHM = False
      self.groupNumber = int(1)
      self.targetType = "W"
      self.motionType = "L"
      self.coordinates = [0.0,0.0,0.0,0.0,0.0,0.0]
      self.coordGroupsDict = {}
      self.speedType = "S"
      self.speedValue = 120.0
      self.toolIndex = int(99)
      self.hasMS = False
      restOfLine = ""
      checkValue = 0
      # search MOVEX__A=8,
      pattern = re.compile(r'^MOVEX.*?A=(\d+)(P)?,')
      match = pattern.search(line)
      if match:
         self.accuracyValue = int(match.group(1))
         self.accuracyHasP = match.group(2) is not None
      # search MOVEX___,AC=0,
      pattern = re.compile(r'^MOVEX.*?,AC=(\d+),')
      match = pattern.search(line)
      if match:
         self.accelerationValue = int(match.group(1))
      # search MOVEX___,SM=0,
      pattern = re.compile(r'^MOVEX.*?,SM=(\d+)')
      match = pattern.search(line)
      if match:
         self.smoothValue = int(match.group(1))
      # search MOVEX___,SM,
      pattern = re.compile(r'^MOVEX(?=.*HM,)')
      match = pattern.search(line)
      if match:
         self.hasHM = True
      # search MOVEX___,M1X,
      pattern = re.compile(r'^MOVEX.*?,M(\d+)(XW?|J),')
      match = pattern.search(line)
      if match:
         self.groupNumber = int(match.group(1))
         self.targetType = match.group(2)
      # search MOVEX___,L,
      pattern = re.compile(r'^MOVEX.*?,([PL]),')
      match = pattern.search(line)
      if match:
         self.motionType = match.group(1)
      pattern = re.compile(r'^MOVEX.*?,C1,')
      match = pattern.search(line)
      if match:
         self.motionType = 'C1'
      pattern = re.compile(r'^MOVEX.*?,C2,')
      match = pattern.search(line)
      if match:
         self.motionType = 'C2'
      # search MOVEX___,(357.335, 340.000, 40.487, 0.00, -20.00, 135.00),
      pattern = re.compile(r'^MOVEX.*?,\s*\(([^)]+)\),')
      match = pattern.search(line)
      if match:
         self.coordinates = [float(x.strip()) for x in match.group(1).split(',')]
         self.coordGroupsDict[self.groupNumber] = self.coordinates
         checkValue += 1
      # search MOVEX___,S=60.0,
      pattern = re.compile(r'^MOVEX.*?,([RS])=([\d.]+),')
      match = pattern.search(line)
      if match:
         self.speedType = match.group(1)
         self.speedValue = float(match.group(2))
      # search MOVEX___,H=1,(restOfLine)
      pattern = re.compile(r'^MOVEX.*?,H=(-?\d+),')
      match = pattern.search(line)
      if match:
         self.toolIndex = int(match.group(1))
         restOfLine = line[match.end():]
      # search MOVEX___,MS,
      pattern = re.compile(r'^MOVEX(?=.*MS,)')
      match = pattern.search(line)
      if match:
         self.hasMS = True
      
      if checkValue < 1:
          return  # if not even Coordinates appearing, return
      
      self.isValid = True

      # ...MS,M2J,P,(0.0),R=1.0,H=1,M4J,P,(0.0, 0.00),R=1,H=1,M5J,P,(-817.59, 234.33, -617.95),R=1,H=1
      # loop max. 10*
      for i in range(1, 11):
         pattern = re.compile(
            r'M(\d+)[XWJ],P,\s*\(([^)]+)\)(.*)'  # M4J,P,(...), then rest of line
         )
         match = pattern.search(restOfLine)
         if match:
            groupValue = int(match.group(1))  # '4'
            coordinates = [float(x.strip()) for x in match.group(2).split(',')]
            restOfLine = match.group(3).strip()
            self.coordGroupsDict[groupValue] = coordinates
         else:
               break
         
# ------------------------------------------------------------------------------------------------------------

@dataclass
class ThisMotion():
   def __init__(self):
      """
      Create a Motion Object and write all on it for later output
      """
      self.motionName = "Point"
      self.motionMotionType = MotionType.Linear
      self.positionProcessType = ProcessType.Auxiliary
      self.positionTargetType = TargetType.Joint
      self.positionIsCircular = False
      self.positionXYZ = []
      self.positionOrientation = []
      self.positionMainJoints = []
      self.positionExternalJoints = []
      self.positionConfig = ""
      self.positionTurn = ""
      self.viaPositionName = "ViaPoint"
      self.viaPositionProcessType = ProcessType.ViaPoint
      self.viaPositionTargetType = TargetType.Joint
      self.viaPositionXYZ = []
      self.viaPositionOrientation = []
      self.viaPositionConfig = ""
      self.viaPositionTurn = ""
      self.viaPositionMainJoints = []
      self.viaPositionExternalJoints = []
      self.motionEventsBefore = []
      self.motionEventsAfter = []

# ============================================================================================================

class DaihenFD19Uploader(Uploader):

#region Uploader Base method overrides

   def __init__(self):
      super().__init__()
      self._programList = []
      self._prgBaseName = ""
      self._unitMechanism = ""

      self._baseProfileList = []
      self._toolProfileList = []
      self._allJointsList = []
      self._opgBaseFrame = ""
      self._opgToolFrame = ""

      self._lines = []
      self._lineCounter = -1

      # special Handling 7-Axer
      self._7AxRobot = False
      self._7AxExchange = [[1,2,1],[2,1,1]]  # [Group1, ValueToReplace, PlaceToInsert], [Group2, ValueToReplace, PlaceToInsert]
      self._last7AxSyncJointValue = 0.0

      self._jointsMain = []
      self._jointsSyncOnRobot = []
      self._jointsEndEffector = []
      self._jointsRail = []
      self._jointsWPPositioner = []

      self._currentProgram = None
      self._currentOperationGroup = None
      self._currentOperation = None
      self._currentMotion = None
      self._currentMotionObject = None
      self._firstMotion = None
      self._motionCounter = 1
      self._config = 'LAN'
      self._turn = '0,0,0'
      self._operationMarker = ["Arc Spot:",
                               "Arc Weld:",
                               "SeamSearch ID:",
                               "SeamFind:",
                               "Touch ID:",
                               "Operation:"]
      self._ulPointCounter = 0
      self._currentEvent = None
      self._currentEventPosition = TPINSERTPOS_INSERTBEFORE
      self._eventsBefore = []
      self._mlTextEventBefore = []
      self._mlTextEventAfter = []
      self._openingUploadEvent = None
      self._eventMarker = ["ZJ",
                           "ZON",
                           "DELAY",
                           "ASDP",
                           "AEDP",
                           "ASWBPL",
                           "AEWBPL",
                           "SF1",
                           "SF3",
                           "SF4",
                           "SF8"]
      self._technoONMarker = ["ASDP",
                              "ASWBPL"]
      self._technoOFFMarker = ["AEDP",
                               "AEWBPL"]
      self._currentARCMode = False
      self._maxTCPFeedrate = 2.4
      self._currentPTPSpeed = 0.0
      self._currentLINSpeed = 0.0
      self._currentSpeedUnit = 0
      self._currentAccuracyValue = -1.0
      self._currentAccuracyType = False
      self._currentAccelerationValue = -1.0
      self._lastMOVEXLine = ""
      self._lastMOVEXViaLine = ""
      self._logging = None
      # en-/disable Development/Debug prints to LogWindow 
      # -1 = no
      #  0 = all
      #  1 = read Lines, initialize PRG, OPG, OP
      #  2 = BF, TF, Joints
      #  4 = Ops BF, TF
      #  8 = Motion Info
      # 16 = Events Info
      # 32 = checkAddMotion
      self._outputLogInfo = -1

# ===================================================================================================================
   def loggingInfo(self, stage: int, info:str):
      if self._logging!= None and self._outputLogInfo > -1:
         if self._outputLogInfo == 0 or (self._outputLogInfo & stage) != 0:
            self._logging.LogInfo(info)


   def Initialize(self, operator : ULPythonUploadOperator):
      self._logging = operator.GetLogOperator()
      for i in range(1, 3):
         self.loggingInfo(1,"=")
      self.loggingInfo(1,"========================= DaihenFD19Uploader INITIALIZE called ==============================")

      controller = operator.GetController()
      
      self._baseProfileList = controller.GetBaseProfiles()
      self._toolProfileList = controller.GetToolProfiles()
      self._allJointsList = controller.GetConnectedJoints()
      resources = controller.GetResources()
      for resource in resources:
         if (resource.GetItemType().name=='Production'):
            if (resource.GetItemSubType().name=='MachineRobot'):
               self._maxTCPFeedrate = resource.GetMaxSpeed()

      # log all BaseFrame, ToolFrame, Joints
      if self._outputLogInfo == 0 or (self._outputLogInfo & 2) != 0:
         self.debugToolBaseJoints()
      
      for joint in self._allJointsList:
         # fill the Joint-Role-Groups
         jointRole = joint.GetJointRole()
         if jointRole == JointConstellationRole.Main:
            self._jointsMain.append(joint)
         elif jointRole == JointConstellationRole.EndEffector:
            self._jointsEndEffector.append(joint)
         elif jointRole == JointConstellationRole.Rail:
            self._jointsRail.append(joint)
         elif jointRole == JointConstellationRole.WorkpiecePositioner:
            self._jointsWPPositioner.append(joint)
         elif jointRole == JointConstellationRole.SynchronousOnRobot:
            self._jointsSyncOnRobot.append(joint)
      
      # check for 7-Axis Robot (6 Main & 1 SyncOnRobot)
      if len(self._jointsMain) == 6 and len(self._jointsSyncOnRobot) == 1:
          self._7AxRobot = True
          


   def debugToolBaseJoints(self):
      """
      writing BaseFrames/ToolFrames/Joints Information to LogWindow
      """
      self.loggingInfo(2,"==================== BASEFRAMES ======================")
      for base_frame in self._baseProfileList:
          self.loggingInfo(2,"----------baseFrame:     " + str(base_frame.GetName()) + "    ------------------------")
          self.loggingInfo(2,"----------      baseIndex:" + str(base_frame.GetIndex()))
          position = base_frame.GetXYZ()
          self.loggingInfo(2,"----------      pos:X" + str(position[0]) + " Y" + str(position[1]) + " Z" + str(position[2]))
          position = base_frame.GetXYZ()
          self.loggingInfo(2,"----------      ori:R" + str(position[0]) + " S" + str(position[1]) + " T" + str(position[2]))
          refBase = base_frame.GetReferenceProfile()
          if refBase:
             self.loggingInfo(2,"----------      reference-baseFrame:" + str(refBase.GetName()))
      self.loggingInfo(2,"==================== TOOLFRAMES ======================")
      for tool_frame in self._toolProfileList:
          self.loggingInfo(2,"----------toolFrame:     " + str(tool_frame.GetName()) + "    ------------------------")
          self.loggingInfo(2,"----------      toolIndex:" + str(tool_frame.GetIndex()))
          self.loggingInfo(2,"----------      toolType:" + str(tool_frame.GetToolType()))
          self.loggingInfo(2,"----------      VisionFrm:" + str(tool_frame.IsVisionFrame()))
          position = tool_frame.GetXYZ()
          self.loggingInfo(2,"----------      pos:X" + str(position[0]) + " Y" + str(position[1]) + " Z" + str(position[2]))
          position = tool_frame.GetOrientation()
          self.loggingInfo(2,"----------      ori:R" + str(position[0]) + " S" + str(position[1]) + " T" + str(position[2]))
      self.loggingInfo(2,"==================== JOINTS ======================")
      for joint in self._allJointsList:
         self.loggingInfo(2,"----------DofNr :     " + str(joint.GetDofNumber()) + "    ------------------------")
         self.loggingInfo(2,"----------      Jnt.Name :" + str(joint.GetName()))
         self.loggingInfo(2,"----------      Jnt.Idx :" + str(joint.GetJointIndex()))
         self.loggingInfo(2,"----------      Grp.Idx :" + str(joint.GetJointGroupIndex()))
         self.loggingInfo(2,"----------      Unit :" + str(joint.GetUnit()))
         self.loggingInfo(2,"----------      PortName :" + str(joint.GetPortName()))
         self.loggingInfo(2,"----------      IsExtern :" + str(joint.IsExternal()))
         self.loggingInfo(2,"----------      Jnt.Role :" + str(joint.GetJointRole()))
         self.loggingInfo(2,"----------      Jnt.Type :" + str(joint.GetJointType()))
         #self.loggingInfo(2,"----------      Name :" + str(joint.GetName()))
      self.loggingInfo(2,"======================================================")


   def ParseFile(self, operator : ULPythonUploadOperator, fileObject : TextIOWrapper):
      self._logging = operator.GetLogOperator()
      self._logging.LogDebug("DaihenFD19Uploader ParseFile called")
      # getting all Upload-File Lines ...
      lines = fileObject.readlines()
      # ...and loop through them
      self.parseLines(operator, lines)
       # flushes last collected Motion Object (if END failed)
      self.flushMotionObject(operator)


   def Finalize(self, operator : ULPythonUploadOperator):
      self._logging = operator.GetLogOperator()
      self.loggingInfo(1,"========================= DaihenFD19Uploader FINALIZE called ==============================")

#endregion

# ============================================================= END OF INITIALIZING / START OF LOOP PROGRAM LINES ==================================

   def parseLines(self, operator : ULPythonUploadOperator, lines: list):
      """
      Looping through the Lines of the Program and analysing the Content
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         lines (str:list): All Upload-File Lines.
      """

      # Holds a list with all the events found before the motion
      self._eventsBefore = []
      lineIterator = iter(lines)
      
      self._lines = lines
      
      for line in lineIterator:
         # ------------------------------------------------------------------------------------------------------
         self._lineCounter += 1
         self.loggingInfo(1,".....Line Iteration is found: " + str(line))
         
         if len(line) < 2:
             continue # empty Line \n
         
         # Parse the Program
         program = self.parseProgram(operator, line)
         if program:
            self._currentProgram = program
            continue
         
         # Parse the Operation Group
         operationGroup = self.parseOperationGroup(operator, line)
         if operationGroup:
            self.checkStructure(operator, 1) # check if the Program is set
            self.flushMotionObject(operator) # flushes last collected Motion Object, if OPG appears
            self._currentOperationGroup = operationGroup
            if self._currentProgram:
               self._currentProgram.AddOperationGroup(operationGroup)
               self._currentOperation = None # reset to force a new Operation
                # empty possible previously collected Stuff
               self._eventsBefore.clear()
               self._mlTextEventBefore.clear()
               self._mlTextEventAfter.clear()
            continue
         
         # Parse the Operation
         operation = self.parseOperation(operator, line)
         if operation:
            self.checkStructure(operator, 2) # check if a OperationGroup is set
            self.flushMotionObject(operator) # flushes last collected Motion Object, if OP appears
            self._currentOperation = operation
            if self._currentOperationGroup:
               self._currentOperationGroup.AddOperation(operation)
               self._currentEventPosition = TPINSERTPOS_INSERTBEFORE
            continue

         # Parse the END line to flush last Motion
         end = self.parseEnd(operator, line)
         if end:
            self.flushMotionObject(operator) # flushes last collected Motion Object

         # Parse the Motion, fill up _currentMotionObject
         motion = self.parseMotion(operator, line, lineIterator)
         if motion:
            self.checkStructure(operator, 3) # check if a Operation is set
            if self._currentOperation:
               if self._motionCounter == 1 and self._openingUploadEvent is not None:
                     # insert UploadEvent on first Motion
                     self._currentMotionObject.motionEventsBefore.append(self._openingUploadEvent)
               for beforeEvent in self._eventsBefore:
                  # if there are EventsBefore, put them on _currentMotionObject.motionEventsBefore
                  self._currentMotionObject.motionEventsBefore.append(beforeEvent)
               self._eventsBefore.clear()
               self._currentEventPosition = TPINSERTPOS_INSERTAFTER # upcoming Events until next Motion/Op/OpG : insert after
               self._motionCounter += 1
            continue
         
         # Parse the Comment (as MultiLine-Text)
         comment = self.parseComment(line)
         if comment:
            continue

         # Parse the Events
         event, eventPosition = self.parseEvent(operator, line)
         if event:
            if eventPosition == TPINSERTPOS_INSERTBEFORE:
               # store on _eventsBefore to flush if _currentMotionObject is set
               self._eventsBefore.append(event)
            if eventPosition == TPINSERTPOS_INSERTAFTER:
               # _currentMotionObject is set, append right now
               self._currentMotionObject.motionEventsAfter.append(event)
            continue
         
         continue


   def checkStructure(self, operator : ULPythonUploadOperator, level: int):
      """
      Determines if the Program/OperationGroup/Operation Objects already set,\n
      and creates necessary Objects with default Names if not exist.\n
      1 = check for Program\n
      2 = check for OperationGroup\n
      3 = check for Operation
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         level (int): The Level to which should be checked PRG/OPGRP/OP.
      """
      if level > 0:
         if self._currentProgram is None:
            self._currentProgram = self.parseProgram(operator, 'REM "PROGRAM NAME  : DUMMYPGMNAME.UPLOAD"')
            self.loggingInfo(1,".......DAIHEN Upload set ProgramName after Check : >UPLOAD<")
      if level > 1:
         if self._currentOperationGroup is None:
            self._currentOperationGroup = self.parseOperationGroup(operator, 'REM "Operation Group: GRPUPLOAD"')
            if self._currentProgram:
               self._currentProgram.AddOperationGroup(self._currentOperationGroup)
               self.loggingInfo(1,"...........DAIHEN Upload add OperationGroup after Check : >GRPUPLOAD<")
      if level > 2:
         if self._currentOperation is None:
            self._currentOperation = self.parseOperation(operator, 'REM "Operation: OPUPLOAD"')
            if self._currentOperationGroup:
               self._currentOperationGroup.AddOperation(self._currentOperation)
               self.loggingInfo(1,"...............DAIHEN Upload set Operation after Check : >OPUPLOAD<")
               
# ============================================================= END OF LOOP PROGRAM LINES  / START OF PARSING ==================================

   def parseProgram(self, operator : ULPythonUploadOperator, line: str):
      """
      Determines if the program line was found. If so it will create the python object and fill it 
      with the necessary data

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.

      Returns:
         ULPythonProgram: The program object if created, None otherwise
      """
      #   REM "PROGRAM NAME  : UNIT1-A.ZJTEST"
      #program_pattern = re.compile(r'^REM\s+"PROGRAM NAME\s*:\s*([\x20-\x7E]+?)\.(\w+)"$')
      program_pattern = re.compile(r'^REM\s+"PROGRAM NAME\s*:\s*([\x20-\x7E]+?)\.([\x20-\x7E]+?)"$')
      program = program_pattern.match(line)
      if program :
         self._prgBaseName = program.group(1).strip()
         program_name = program.group(2).strip()
         newProgram = operator.CreateEmptyProgram()
         newProgram.SetName(program_name)
         newProgram.SetIsMainProgram(True)
         self.loggingInfo(1,"PRG ### .... Setting DAIHEN Upload PROGRAM: >" + str(program_name) + "<")

         # create UploadEvent for Output before 1st Motion
         ulEvtDict = {"ProgramBaseName": {"Value": self._prgBaseName, "Type": str}}
         self._openingUploadEvent = self.addUploadEvent(operator,ulEvtDict, TPINSERTPOS_INSERTBEFORE)

         return newProgram
      return None
            
   def parseOperationGroup(self, operator : ULPythonUploadOperator, line: str):
      """
      Determines if the operation group line was found. If so it will create the python object and fill it 
      with the necessary data

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.

      Returns:
         ULPythonOperationGroup: The operation group object if created, None otherwise
      """
      #   REM "Operation Group: GRP001"
      operation_group_pattern = re.compile(r'^REM\s+"Operation Group:\s*(\w+)"$')
      operationGroup = operation_group_pattern.match(line)
      if operationGroup:
         group_Name = operationGroup.group(1).strip()
         ulOperationGroup = operator.CreateEmptyOperationGroup()
         ulOperationGroup.SetName(group_Name)
         self.loggingInfo(1,"OPG ### ........ Setting DAIHEN Upload OPERATION GROUP: >" + str(group_Name) + "<")
         return ulOperationGroup
      return None

   def parseOperation(self, operator : ULPythonUploadOperator, line: str):
      """
      Determines if the operation line was found. If so it will create the python object and fill it 
      with the necessary data

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.

      Returns:
         ULPythonOperation: The operation object if created, None otherwise
      """
      #   REM " SeamFind: FindingAtEnd1"
      operation_pattern = re.compile(r'^REM\s+"([^"]+)"$')
      operation = operation_pattern.search(line)
      if operation :
         operation_name = operation.group(1).strip()
         if any(marker in operation_name for marker in self._operationMarker):
            ulOperation = operator.CreateEmptyOperation()
            ulOperation.SetName(operation_name)
            self.loggingInfo(1,"OP   ### ................ Setting DAIHEN Upload OPERATION: >" + str(operation_name) + "<")
            controller = operator.GetController()
            baseProfile = self.parseForBaseProfile(controller)
            if baseProfile is not None:
               ulOperation.SetUsedBaseProfile(baseProfile)
            toolProfile = self.parseForToolProfile(controller)
            if toolProfile is not None:
               ulOperation.SetUsedToolProfile(toolProfile)
            return ulOperation
         # else:
         #    if self._currentOperation is not None:
         #       self.loggingInfo(1,"...............DAIHEN Upload just a Comment XXXXXXXXXXXXXXXXX : >" + str(operation_name) + "<")
      return None
    
   def parseEnd(self, operator : ULPythonUploadOperator, line: str):
      """
      Determines if the END line was found. Necessary to output last Motion-Object
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.

      Returns:
         True/False if the Element was found or not
      """
      end_pattern = re.compile(r'^END\s*$')
      end = end_pattern.search(line)
      if end:
         return True
      return False

   def parseEvent(self, operator : ULPythonUploadOperator, line):
      """
      Determines if the event line was found. If so it will create the python object and fill it 
      with the necessary data.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.

      Returns:
         ULPythonEvent: The event object if created, None otherwise
         TPINSERTPOS (int): its insert Position
      """
      eventPos = self._currentEventPosition
      ulEvent = None
      # AEWBPL 1,1,0,0,0,0,0,0,0,0,0,0,0,0,0
      event_pattern = re.compile(r'^(\w+)\s+(.*)$')
      match = event_pattern.match(line.strip())

      if match:
         commandName = match.group(1)       # 'AEWBPL'
         restOfLine = match.group(2)     # '1,1,0,0,0,...'
         if any(marker in commandName for marker in self._technoONMarker):
            # Arc ON Events "ASDP","ASWBPL"
            self.flushMultiLineTextEvent(operator) # flushes MULTILINE-EVENT before "real" Event follows
            eventPos = TPINSERTPOS_INSERTAFTER
            ulEvent = self.addArcOnEvent(operator, commandName, restOfLine, eventPos)
         elif any(marker in commandName for marker in self._technoOFFMarker):
            # Arc OFF Events "AEDP","AEWBPL"
            self.flushMultiLineTextEvent(operator) # flushes MULTILINE-EVENT before "real" Event follows
            eventPos = TPINSERTPOS_INSERTAFTER
            ulEvent = self.addArcOffEvent(operator, commandName, restOfLine, eventPos)
         # elif commandName == "HUBBA":
         #    # Template for any further Events
         #    self.flushMultiLineTextEvent(operator) # flushes MULTILINE-EVENT before "real" Event follows
         #    eventPos = TPINSERTPOS_INSERTAFTER
         #    ulEvent = self.hubbaEvent(operator, commandName, restOfLine, eventPos)
         elif any(marker in commandName for marker in self._eventMarker):
            # !!! all other Events were currently handled as Text-Events (just pass them as they are) !!!
            # technology Events "ZJ","ZON","DELAY","SF3","SF4","SF8"
            text = commandName + " " + restOfLine
            self.storeMultiLineTextEvent(text)
            return None, None # just stired as ML-Text (flushed later)
         return ulEvent, eventPos # successfully created Event
      return None, eventPos # no Match

   def parseComment(self, line: str):
      """
      Determines if a Comment line was found and stores it as a ML-Text (flushed later)
      Parameters:
         line (str): The current line to be parsed.

      Returns:
         True/False if the Line was recognized as a Comment
      """
      #   REM " This is really a usual Comment"
      comment_pattern = re.compile(r'^REM\s+"([^"]+)"$')
      comment = comment_pattern.search(line)
      if comment:
         self.storeMultiLineTextEvent(line)
         return True
      return False
   
# ============================================================= END OF PARSING  / START OF MOTION HANDLING ==================================

   def parseTarget(self, movexItem: MovexLine):
      """
      Determines if the target line was found. If found it will read the data and fill the position object with it

      Parameters:
         ulPosition (ULPythonPosition): parent position
         movexItem: MovexLine : the parsed Movex-Line Object
      """
      
      total_items = sum(len(value_list) for value_list in movexItem.coordGroupsDict.values())
      if total_items != len(self._allJointsList):
          self._logging.LogWarn("Number of all Joints (" + str(len(self._allJointsList)) + ") is NOT equal to the Number of incoming Coordinates (" + str(total_items) + ") .")
      
      if self._currentMotionObject.positionTargetType == int(TargetType.Cartesian):
         coords = movexItem.coordinates
         if movexItem.motionType == "C1":
            self._currentMotionObject.viaPositionXYZ = (float(coords[0]/1000), float(coords[1]/1000), float(coords[2]/1000))
            self._currentMotionObject.viaPositionOrientation = (float(coords[5]), float(coords[4]), float(coords[3])) # !!! Z-Y-X / 5-4-3
         else:
            self._currentMotionObject.positionXYZ = (float(coords[0]/1000), float(coords[1]/1000), float(coords[2]/1000))
            self._currentMotionObject.positionOrientation = (float(coords[5]), float(coords[4]), float(coords[3])) # !!! Z-Y-X / 5-4-3
         # in Case of 7Axis Robot, uploaded Values needs to be ordered
         if self._7AxRobot == True:
            mechGroupTwo = movexItem.coordGroupsDict.get(2,[0.0])
            mechGroupTwo[0] = self._last7AxSyncJointValue   # ....hard coded yet, to be clearified what to do with Cartesian Motions on 7-Axis
            self._logging.LogWarn("Synchronious Joint cound NOT be gotten on Cartesian Motion. Its Value will be set with last gotten Value to " + str(self._last7AxSyncJointValue) + ". Please validate.")
      else:
         # in Case of 7Axis Robot, uploaded Values needs to be ordered
         if self._7AxRobot == True:
            self.handle7AxJoints(movexItem)

      # ...continue with Joint, ...check anyway, possible External Axis also for Cartesian
      mainJointsList = []
      externalJointsList = []
      for joint in self._allJointsList:
         try:
            coordList = movexItem.coordGroupsDict.get(joint.GetJointGroupIndex(),[])  # get the CoordinatesList to the related UnitGroup
         except:
            self._logging.LogWarn("No Coordinates found for Group Unit.")
         
         message = "...........JointCoord " + str(joint.GetDofNumber()) + " G" + str(joint.GetJointGroupIndex()) + "/J" + str(joint.GetJointIndex())
         if len(coordList) > 0:
            if joint.GetJointIndex() > len(coordList):
               jointCoord = 888.0
               message += " : NO MATCHING JOINT INDEX FOUND !!!"
            else:
               jointCoord = coordList[joint.GetJointIndex()-1]  # get the Coordinate of the related JointIndex
               message += "=\t" + str(joint.GetName()) + "\t" + str(jointCoord)
         else:
            jointCoord = 123.0
            message +=  " : NO MATCHING UNIT GROUP FOUND !!!"
         self.loggingInfo(8,message)
         if joint.GetUnit() != 'deg':
             jointCoord /= 1000
         target_list = externalJointsList if joint.IsExternal() else mainJointsList
         target_list.append((joint, self.convertValue(jointCoord, 'float')))
         
      
      if movexItem.motionType == "C1":
         # set the Main Via-Joints
         self._currentMotionObject.viaPositionMainJoints = mainJointsList
         # set the External Via-Joints
         if len(externalJointsList) > 0:
            self._currentMotionObject.viaPositionExternalJoints = externalJointsList
      else:
         # set the Main Joints
         self._currentMotionObject.positionMainJoints = mainJointsList
         # set the External Joints
         if len(externalJointsList) > 0:
            self._currentMotionObject.positionExternalJoints = externalJointsList
   
   def handle7AxJoints(self, movexItem: MovexLine):
      """Change joints in case of 7-Axis Robot"""
      # Unpack configuration for both groups
      # self._7AxExchange = [[1,2,1],[2,1,1]]  # [Group1, ValueToReplace, PlaceToInsert], [Group2, ValueToReplace, PlaceToInsert]
      (groupA, jointA, insertA), (groupB, jointB, insertB) = [
         (g, j - 1, i - 1) for g, j, i in self._7AxExchange
      ]
      # Get coordinate lists safely
      firstGroup = movexItem.coordGroupsDict.get(groupA, [])
      secondGroup = movexItem.coordGroupsDict.get(groupB, [])
      self.loggingInfo(8,f"Before swap: {firstGroup} | {secondGroup}")
      # Swap logic
      if firstGroup and secondGroup:
         replaceJoint = firstGroup[jointA]
         syncJoint = secondGroup[jointB]
         # Remove old joint and insert new one
         firstGroup.pop(jointA)
         firstGroup.insert(insertA, syncJoint)
         # Replace in second group
         secondGroup[insertB] = replaceJoint
         self._last7AxSyncJointValue = replaceJoint
      
      self.loggingInfo(8,f"After swap: {firstGroup} | {secondGroup}")

   def parsePosition(self, operator : ULPythonUploadOperator, movexItem: MovexLine, movexItemVia: MovexLine):
      """
      Determines if the position line was found. If so it will create the python object and fill it 
      with the necessary data

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem: MovexLine : the parsed Movex-Line Object
         movexItemVia: MovexLine : the parsed Movex-Line VIA Object

      Returns:
         Pair of ULPythonPositions: First - the motion position
                                    Second - motion via point position if motion is circular
      """
      
      if movexItem.isValid:
         # check for Arc On/Off appearing and set ProcessType
         self.checkForProcessType()
         if self._currentARCMode == True:
            self._currentMotionObject.positionProcessType = getattr(ProcessType,"ProcessCurve")
         else:
            self._currentMotionObject.positionProcessType = getattr(ProcessType,"Auxiliary")

         target_map = {
            "X": TARGETTYPE_CARTESIAN,
            "W": TARGETTYPE_CARTESIAN,
            "J": TARGETTYPE_JOINT
         }
         iTargetType = target_map.get(movexItem.targetType, 0)
         self._currentMotionObject.positionTargetType = iTargetType
         self._currentMotionObject.positionConfig = self._config
         self._currentMotionObject.positionTurn = self._turn

         # If the motion type is circular we need to take care of the viaPoint position as well
         if movexItemVia is not None:
            if movexItemVia.isValid:
               self._currentMotionObject.positionIsCircular = True
               self._currentMotionObject.viaPositionProcessType = getattr(ProcessType,"ViaPoint")
               self._currentMotionObject.viaPositionTargetType = iTargetType
               self._currentMotionObject.viaPositionConfig = self._config
               self._currentMotionObject.viaPositionTurn = self._turn
               return True, True
         return True, False
      return False, False  

   def checkForProcessType(self):
      """check if current TPE has a TechoON before next MOVEX to set its ProcessType (ToolOnEvent after)"""
      # ASWBPL 1,1,0,0,0,0,0,0,0,0,0,0,0,0,0
      for i in range(1, 11):
         if len(self._lines) > (self._lineCounter + i):
            line = self._lines[self._lineCounter + i]
            if line == "END":
               break
            pattern = re.compile(r'^MOVEX.*?,M(\d+)([XWJ]),') # MOVEX.....,M1X,...
            match = pattern.search(line)
            if match:
               break # next MOVEX Line, break
            event_pattern = re.compile(r'^(\w+)\s+(.*)$')
            match = event_pattern.match(line.strip())
            if match:
               eventName = match.group(1)       # 'ASWBPL ....'
               if any(marker in eventName for marker in self._technoONMarker):
                  self._currentARCMode = True
                  break # found a TechnoON Command


   def parseMotion(self, operator : ULPythonUploadOperator, line: str, lineIterator):
      """
      Determines if the motion line was found. If so it will create the python motion object and fill it 
      with the necessary data

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         line (str): The current line to be parsed.
         lineIterator (): line interator it will be used to advance the line

      Returns:
         True/False if the Line was recognized as a Motion (MOVEX) Line
      """
      # first check if this is a TouchSensing Move : SF1....,MOVEX,M1X,(...),....
      if self._motionCounter > 1:
         isTSMovex, newLine = self.touchSensingMovexLine(operator, line)
         if isTSMovex == True:
            line = newLine   # exchange the TouchSensing Line to a normal MOVEX and create it as a usual Motion
      if self._motionCounter > 9:
         iDummy = 0
      # analyse and parse the MOVEX Line into its Components
      movexItem = MovexLine(line)
      if movexItem.isValid:

         # ****** handle the Motion Object ******************
         self.flushMotionObject(operator) # flushes last collected Motion Object
         self._currentMotionObject = None
         self._currentMotionObject = ThisMotion() # create a empty Motion Object
         self.flushMultiLineTextEvent(operator, MULTILINETEXT_FLUSH_BEFORE) # there might be some BEFORE MULTILINE-EVENT(s)
         # **************************************************
         self.loggingInfo(8 | 32,"---------------------------- Motion Start -------------------------------")
         self.loggingInfo(8 | 32,".....Line Iteration is found: " + str(line))

         motion_map = {
            "L": MOTIONTYPE_LIN,
            "C1": MOTIONTYPE_CIR,
            "C2": MOTIONTYPE_CIR,
            "P": MOTIONTYPE_PTP
         }
         iMotionType = motion_map.get(movexItem.motionType, 1)
         self._currentMotionObject.motionMotionType = iMotionType
         
         movexItemVia = None
         vialine = ""
         if iMotionType == MOTIONTYPE_CIR:
             vialine = line
             movexItemVia = movexItem   # C1 on CIR first is the VIA Point
             line = next(lineIterator, '')  # C2 is next Line is CIR End
             movexItem = MovexLine(line)

         position, viaPosition = self.parsePosition(operator, movexItem, movexItemVia)
         if viaPosition == True:
               self._ulPointCounter += 1
               self._currentMotionObject.viaPositionName = f"UL_P{self._ulPointCounter:04d}"
               self.parseTarget(movexItemVia)
               self.loggingInfo(8 | 32,".....ViaMtn " + str(self._ulPointCounter) + " : " + str(vialine))
               self._motionCounter += 1
               self._lastMOVEXViaLine = vialine
         if position == True:
               self._ulPointCounter += 1
               self._currentMotionObject.motionName = f"UL_P{self._ulPointCounter:04d}"
               self.parseTarget(movexItem)
               self.loggingInfo(8 | 32,".....Motion " + str(self._ulPointCounter) + " : " + str(line))
               self._lastMOVEXLine = line
         
         # Technology Events Speed/Accuracy/Acceleration
         self.setAccelerationEvent(operator, movexItem)
         if self._motionCounter == -1:
            self.setStartConditionsEvent(operator, movexItem) # set first Speed and Accuracy as StartConditionEvent on 1st Motion
         else:
            self.setAccuracyEvent(operator, movexItem) # normal Speed and Accuracy Events
            self.setSpeedEvent(operator, movexItem)
         
         # set the Mechanism for compare in UploadEvent
         if self._unitMechanism == "":
            self.setUnitMechanism(operator, movexItem)
         
         return True
      return False
    
   def setUnitMechanism(self, operator, movexItem: MovexLine):
      """
      Set the Mechanism (Robot, 7thAxis, Rail, WorkpiecePositioner) as String for comparing Layout and uploaded Program in UploadEvent
      e.g "1" or "1,2" or "1,2,4,5"
      """
      unitMechs = ",".join(str(key) for key in movexItem.coordGroupsDict.keys())
      attribute = self.create_attribute(operator, "UnitMechanism", {"Value": unitMechs, "Type": str})
      self._openingUploadEvent.AddAttribute(attribute)

   def touchSensingMovexLine(self, operator : ULPythonUploadOperator, line: str):
      """
      check and convert if TouchSensing Motion (SF1......MOVEX,M1X,(...),....)
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
      """
      # does it contains MOVEX ?
      matchA = re.search(r'^(?=SF1\b).*?(?=MOVEX\b)', line)
      if not matchA:
         return False, ""
      # get the Parameters from SF1 to MOVEX
      preParams = matchA.group(0).strip() # SF1 1,1,1,2,1,0,0,3...
      
      # 1) Extract coords from SF1-MOVEX Line after MOVEX
      matchB = re.search(r'MOVEX\b.*?\(\s*([^()]*)\s*\)', line)
      if not matchB:
         self._logging.LogError("Could not find coordinate tuple in LineB after 'MOVEX'.")
         return False, ""
      sf1Coords = matchB.group(1)  # e.g., "925.507, -54.504, 5.994, -90.00, 0.00, -45.00"
      # get the Parameters from Coords to End of Line
      postParams = line[matchB.end():].strip()   # ...,1,11,1,-1,-0.55,0,...

      # 2) Replace coords in lastMOVEXLine for a new Line (use all given Parameters, Accuracy, Acceleration, etc.)
      newLine = re.sub(
         r'(M\d+[XJ][^()]*)\(\s*[^()]*\s*\)',
         r'\1(' + sf1Coords + ')',
         self._lastMOVEXLine,
         count=1
      )
      self.loggingInfo(8,"------------ TouchSensing Motion---------------------")
      self.loggingInfo(8,".............MOVEX  pre :" + self._lastMOVEXLine)
      self.loggingInfo(8,".............MOVEX new :" + newLine)
      self.loggingInfo(8,".............MOVEX  xyz :" + sf1Coords)
      ulTSMotionEvent = self.create_event_with_attributes(
               operator,
               "UploadTSMotionEvent",
               TPINSERTPOS_INSERTBEFORE,
               {
                  "IsTouchSensingMotion": {"Value": True, "Type": bool},
                  "PreParameters": {"Value": preParams, "Type": str},
                  "PostParameters": {"Value": postParams, "Type": str},
               },
               )
      if ulTSMotionEvent is not None:
         self.loggingInfo(8,".............UploadTSMotionEvent added to TouchSens Motion.")
         self._eventsBefore.append(ulTSMotionEvent)
      self.loggingInfo(8,"--------------------------------------------------------------------")
      return True, newLine

# ============================================================= END OF MOTION HANDLING  / START OF TEXT/ARCONOFF EVENTS ==================================

   def flushMotionObject(self, operator : ULPythonUploadOperator):
      """
      Builds the current Motion from Motion Object for Output to current Operation
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
      """
      if self._currentMotionObject is None:
         return
      
       # there might be some AFTER MULTILINE-EVENT(s), add as TextEvent
      self.flushMultiLineTextEvent(operator, MULTILINETEXT_FLUSH_AFTER)
      # create the Motion
      uploadMotion = operator.CreateEmptyMotion()
      if not uploadMotion:
         return None
      uploadMotion.SetName(self._currentMotionObject.motionName)
      uploadMotion.SetMotionType(self._currentMotionObject.motionMotionType)
      # create the Motion Position
      uploadPosition = operator.CreateEmptyPosition()
      if not uploadPosition:
         return None
      uploadMotion.SetPosition(uploadPosition)
      uploadPosition.SetName(self._currentMotionObject.motionName)
      #uploadPosition.SetMotion(uploadMotion)
      uploadPosition.SetProcessType(self._currentMotionObject.positionProcessType)
      uploadPosition.SetTargetType(self._currentMotionObject.positionTargetType)
      uploadPosition.SetConfig(self._currentMotionObject.positionConfig)
      uploadPosition.SetTurn(self._currentMotionObject.positionTurn)
      if self._currentMotionObject.positionTargetType == int(TargetType.Cartesian):
         uploadPosition.SetXYZ(self._currentMotionObject.positionXYZ)
         uploadPosition.SetOrientation(self._currentMotionObject.positionOrientation)
      # set the Main Joints
      uploadPosition.SetExplicitMainJointValues(self._currentMotionObject.positionMainJoints)
      if len(self._currentMotionObject.positionExternalJoints) > 0:
         # set the Externals (also for Cartesian)
         uploadPosition.SetExplicitExternalJointValues(self._currentMotionObject.positionExternalJoints)
      
      # create the Motion VIA- Position (if necessary)
      if self._currentMotionObject.positionIsCircular == True:
         uploadPositionVia = operator.CreateEmptyPosition()
         if not uploadPositionVia:
            return None
         uploadMotion.SetViaPosition(uploadPositionVia)
         uploadPositionVia.SetName(self._currentMotionObject.viaPositionName)
         #uploadPositionVia.SetMotion(uploadMotion)
         uploadPositionVia.SetProcessType(self._currentMotionObject.viaPositionProcessType)
         uploadPositionVia.SetTargetType(self._currentMotionObject.viaPositionTargetType)
         uploadPositionVia.SetConfig(self._currentMotionObject.viaPositionConfig)
         uploadPositionVia.SetTurn(self._currentMotionObject.viaPositionTurn)
         if self._currentMotionObject.viaPositionTargetType == int(TargetType.Cartesian):
            uploadPositionVia.SetXYZ(self._currentMotionObject.viaPositionXYZ)
            uploadPositionVia.SetOrientation(self._currentMotionObject.viaPositionOrientation)
         # set the Main Joints
         #uploadPosition.SetExplicitMainJointValues(self._currentMotionObject.positionMainJoints)
         uploadPositionVia.SetExplicitMainJointValues(self._currentMotionObject.viaPositionMainJoints)
         if len(self._currentMotionObject.positionExternalJoints) > 0:
            # set the Externals (also for Cartesian)
            #uploadPosition.SetExplicitExternalJointValues(self._currentMotionObject.positionExternalJoints)
            uploadPositionVia.SetExplicitExternalJointValues(self._currentMotionObject.viaPositionExternalJoints)
      
      # add all belonging Events before & after
      uploadMotion.SetEventsBefore(self._currentMotionObject.motionEventsBefore) # flush collected Before-Events...
      uploadMotion.SetEventsAfter(self._currentMotionObject.motionEventsAfter) # flush collected After-Events...
      
      if self._currentOperation is not None:
         # add the Motion to the current Operation and clear some Stuff
         if self._motionCounter > 12:
            iDummy = 0
         self._currentOperation.AddMotion(uploadMotion)
         self._currentMotionObject = None
         self._mlTextEventBefore.clear()
         self._mlTextEventAfter.clear()
         if self._outputLogInfo == 0 or (self._outputLogInfo & 32) != 0:
            self.checkTheMotion(uploadMotion)
         self.loggingInfo(8 | 32,"---------------------------- Motion End ---------------------------------")


   def checkTheMotion(self, motion: ULPythonMotion):
      """Check the created Motion"""
      name = motion.GetName()
      self.loggingInfo(32,".")
      viaPos = motion.GetViaPosition()
      
      if viaPos:
         vname = viaPos.GetName()
         vmjs = viaPos.GetAllJointValues()
         vmxs = viaPos.GetExternalJointValues()
         t = ""
         for vmj in vmjs:
            t += str(vmj[1]) + ", "
         x = ""
         if vmxs:
            for vmx in vmxs:
               x += str(vmx[1]) + ", "
         vcartesian = viaPos.GetXYZ()
         vori = viaPos.GetOrientation()
         vtar = viaPos.GetTargetType()
         vcon = viaPos.GetConfig()
         vturn = viaPos.GetTurn()
         vjnts = "vjoints : " + t
         vexts = "vextrns : " + x
         self.loggingInfo(32,".....Check-Via : " + str(self._lastMOVEXViaLine))
         self.loggingInfo(32,"...........ViaMotion : " + str(vtar) + " | " + str(vcon) + " | " + str(vturn) + " | ")
         self.loggingInfo(32,"...........ViaCartesian : " + str(vcartesian))
         self.loggingInfo(32,"...........ViaOrient : " + str(vori))
         self.loggingInfo(32,"...........ViaJoints : " + str(vjnts))
         self.loggingInfo(32,"...........ViaExtnls : " + str(vexts))

      pos = motion.GetPosition()
      if pos:
         name = pos.GetName()
         mjs = pos.GetAllJointValues()
         mxs = pos.GetExternalJointValues()
         t = ""
         for mj in mjs:
            t += str(mj[1]) + ", "
         x = ""
         if mxs:
            for mx in mxs:
               x += str(mx[1]) + ", "
         cartesian = pos.GetXYZ()
         ori = pos.GetOrientation()
         tar = pos.GetTargetType()
         con = pos.GetConfig()
         turn = pos.GetTurn()
         jnts = "joints : " + t
         exts = "extrns : " + x
         self.loggingInfo(32,".....Check-Line : " + str(self._lastMOVEXLine))
         self.loggingInfo(32,"...........Motion : " + str(tar) + " | " + str(con) + " | " + str(turn) + " | ")
         self.loggingInfo(32,"...........Cartesian : " + str(cartesian))
         self.loggingInfo(32,"...........Orient : " + str(ori))
         self.loggingInfo(32,"...........Joints : " + str(jnts))
         self.loggingInfo(32,"...........Extnls : " + str(exts))

      dummy = 1


# ============================================================= END OF MOTION HANDLING  / START OF TEXT/ARCONOFF EVENTS ==================================

   def addUploadEvent(self, operator : ULPythonUploadOperator, attributes: dict, insertPos: int):
      """
      Creates a Upload Event to set anything what can't be controlled from here
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         attributes (dict): the Events Attributes to pass e.g.  {"ProgramBaseName": {"Value": "UNIT-1A", "Type": str}}
         insertPos (int): the Event's insert Position

      Returns:
         ULPythonEvent: The event object if created, None otherwise
      """
      uploadEvent = self.create_event_with_attributes(
               operator,
               "UploadEvent",
               insertPos,
               attributes
               )
      return uploadEvent


   def storeMultiLineTextEvent(self, text: str):
      """
      Collect and stores a Text in dedicated List for MultiLine-TextEvent-Output
      Parameters:
         text (str): the Text to be stored
      """
      if self._currentEventPosition == TPINSERTPOS_INSERTBEFORE:
         self._mlTextEventBefore.append(text)
      elif self._currentEventPosition == TPINSERTPOS_INSERTAFTER:
         self._mlTextEventAfter.append(text)

   def flushMultiLineTextEvent(self, operator: ULPythonUploadOperator, position: int = MULTILINETEXT_FLUSH_ALL):
      """
      Flushes collected Text to a MultiLine-TextEvent
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         position (int, opt.): if a desired List needs to be flushed, else the _currentEventPosition
      """
      localPosition = self._currentEventPosition
      if position is not MULTILINETEXT_FLUSH_ALL:
         localPosition = position
      # write collected Text(s) to MultiLineTextEvent and clear the List
      if localPosition == TPINSERTPOS_INSERTBEFORE and self._mlTextEventBefore:
         self.addMultiLineTextEvent(operator, self._mlTextEventBefore, TPINSERTPOS_INSERTBEFORE)
         self._mlTextEventBefore.clear()
      elif localPosition == TPINSERTPOS_INSERTAFTER and self._mlTextEventAfter:
         self.addMultiLineTextEvent(operator, self._mlTextEventAfter, TPINSERTPOS_INSERTAFTER)
         self._mlTextEventAfter.clear()

   def addMultiLineTextEvent(self, operator: ULPythonUploadOperator, events: list, evtPosition:int = TPINSERTPOS_INSERTBEFORE):
      """
      Creates a Text Event
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         events (str list): the stored Text Events to be set in the MultiLine-TextEvent
         evtPosition : the desired insert Position

      Returns:
         ULPythonEvent
      """
      textEvent = None
      if len(events):
         text = "|".join(events[:])
         if "|" in text:
               isMultiLine = True
               mes = "ML:True"
         else:
               isMultiLine = False
               mes = "ML:False"
         
         if evtPosition == TPINSERTPOS_INSERTBEFORE:
            mes += " Before"
         else:
            mes += " After"

         textEvent = self.create_event_with_attributes(
               operator,
               "TextEvent",
               evtPosition,
               {
                  "Text": {"Value": text, "Type": str},
                  "IsMultiLine": {"Value": isMultiLine, "Type": bool},
                  "MultiLineSeparator": {"Value": "|", "Type": str},
               },
               )
         if evtPosition == TPINSERTPOS_INSERTBEFORE:
            if self._currentOperationGroup is not None and textEvent is not None:
                   self._eventsBefore.append(textEvent) # collect BeforeEvents for the next Motion
                   self.loggingInfo(16,".......----->>> flush addMultiLineTextEvent._eventsBefore : " + str(mes) + " >>>" + str(text))
         if evtPosition == TPINSERTPOS_INSERTAFTER:
            if self._currentOperation is not None and self._currentMotionObject is not None and textEvent is not None:
                   self._currentMotionObject.motionEventsAfter.append(textEvent) # immediately store Event to Motion Object
                   self.loggingInfo(16,".......----->>> flush addMultiLineTextEvent.motionEventsAfter : " + str(mes) + " >>>" + str(text))
         return True
      return False

   def addArcOnEvent(self, operator : ULPythonUploadOperator, commandName: str, params: str, insertPos: int):
      """
      Creates the AcrOn Event and stores the Command Name to the Upload Event
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         commandName (str): the Name of the OTC ArcOn Command
         parameters (str): text
         insertPos (int): its desired insert Position

      Returns:
         ULPythonEvent: The event object if created, None otherwise
      """
      #OTC_ARCON_JSON
      text = '{"OTC_WELD_PRGNR": "1"'
      text += ', "OTC_WELD_OFF_PRGNR": "1"'
      text += ', "OTC_WELD_CHARACTER": "4"'
      text += ', "OTC_WIRE_FEED": "900"'
      text += ', "OTC_CURRENT": "220"'
      text += ', "OTC_VOLTAGE": "28"'
      text += ', "OTC_USE_WEAVE": false'
      text += ', "OTC_WEAVE_COND_NR": "1"'
      text += ', "ArcSenseSt": false'
      text += ', "ArcSenseStCondFile": "1"'
      text += ', "ArcSenseStSampleData": "1"'
      text += ', "ArcSenseEtCondFile": "1"'
      text += ', "OTC_STITCH_PULSE_ENABLED": false'
      text += ', "OTC_STITCH_PULSE_AS_COND": "1"'
      text += ', "OTC_STITCH_PULSE_AE_COND": "1"'
      text += ', "OTC_STITCH_PULSE_WELDING_TIME": "0.7"'
      text += ', "OTC_STITCH_PULSE_COOLING_TIME": "1.0"'
      text += ', "OTC_STITCH_PULSE_MOVEMENT_PITCH": "4.0"'
      text += ', "OTC_STITCH_PULSE_MOVE_COND_NUMBER": "0.0"'
      text += ', "ruleEvent": "True"}'
      # self.loggingInfo(16,"...................ARC ON Event Params : >" + str(text) + "<")
      arcOnEvent = self.create_event_with_attributes(
               operator,
               "ArcOnEvent",
               insertPos,
               {
                  "OTC_ARCON_JSON": {"Value": text, "Type": str}
               }
               )
      
      # store this in the UploadEvent
      attribute = self.create_attribute(operator, "ArcOnCode", {"Value": commandName, "Type": str})
      self._openingUploadEvent.AddAttribute(attribute)

      return arcOnEvent
   
   def addArcOffEvent(self, operator : ULPythonUploadOperator, commandName: str, params: str, insertPos: int):
      """
      Creates the AcrOff Event and stores the Command Name to the Upload Event
      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         commandName (str): the Name of the OTC ArcOff Command
         parameters (str): text
         insertPos (int): its desired insert Position

      Returns:
         ULPythonEvent: The event object if created, None otherwise
      """
      self._currentARCMode = False
      
      arcOffEvent = self.create_event_with_attributes(
               operator,
               "ArcOffEvent",
               insertPos,
               None
               )
      
      # store this in the UploadEvent
      attribute = self.create_attribute(operator, "ArcOffCode", {"Value": commandName, "Type": str})
      self._openingUploadEvent.AddAttribute(attribute)

      return arcOffEvent
   
# =========================================== END OF MOTION HANDLING  / START OF SPEED/ACCURACY/ACCELERATION EVENTS =========================

   def setStartConditionsEvent(self, operator, movexItem: MovexLine):
      """
      Set on the first Motion the Speed and Accuracy as a StartConditions-Event before.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      """
      # self._maxTCPFeedrate
      executeEvent, speed, sPathType, sUnit = self.checkForSpeedEvent(operator, movexItem)
      executeEvent, accuracy, aPathType, criteria, aUnit = self.checkForAccuracyEvent(operator, movexItem)
      if sUnit == 28: # %
         speedP = speed
         speedL = (speed/100) * self._maxTCPFeedrate
      else: # mm/min
         speedP = (speed/self._maxTCPFeedrate)*100
         speedL = speed
      if criteria == 0:
         accuracy = 0
      # save Values
      self._currentSpeedUnit = sUnit
      self._currentPTPSpeed = speedP
      self._currentLINSpeed = speedL
      self._currentAccuracyValue = movexItem.accuracyValue
      self._currentAccuracyType = movexItem.accuracyHasP

      start_condition_event = self.create_event_with_attributes(
            operator,
            "StartConditionsEvent",
            TPINSERTPOS_INSERTBEFORE,
            {
               "EventStartSetFlag": {"Value": True , "Type": bool},
               "EventStartPtpFeedRate": {"Value": speedP , "Type": float},  # Speed in %
               "EventStartLinFeedRate": {"Value": speedL , "Type": float},  # Speed in mm/min
               "EventStartPtpAccuracy": {"Value": accuracy , "Type": float},  # Acc in %
               "EventStartLinAccuracy": {"Value": accuracy*0.001 , "Type": float},
               "EventStartPtpAcceleration": {"Value": 1.0 , "Type": float},
               "EventStartLinAcceleration": {"Value": 1.0 , "Type": float}
            },
            )
      self._eventsBefore.append(start_condition_event)


   def setAccuracyEvent(self, operator, movexItem: MovexLine):
      """
      Set on the current Motion an Accuracy-Event before, if necessary.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      """
      executeEvent, accuracy, pathType, criteria, unit = self.checkForAccuracyEvent(operator, movexItem)
      if executeEvent == False:
         return
      accuracy_event = self.create_event_with_attributes(
            operator,
            "Accuracy",
            TPINSERTPOS_INSERTBEFORE,
            {
               "Value": {"Value": accuracy , "Type": float},
               "PathType": {"Value": pathType, "Type": str},
               "Criteria": {"Value": criteria, "Type": int},
               "ValueUnitType": {"Value": unit, "Type": int}
            },
            )
      self._eventsBefore.append(accuracy_event)

   def setSpeedEvent(self, operator, movexItem: MovexLine):
      """
      Set on the current Motion a Speed-Event before, if necessary.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      """
      executeEvent, speed, pathType, unit = self.checkForSpeedEvent(operator, movexItem)
      if executeEvent == False:
         return
      speed_event = self.create_event_with_attributes(
            operator,
            "Speed",
            TPINSERTPOS_INSERTBEFORE,
            {
               "Value": {"Value": speed , "Type": float},
               "PathType": {"Value": pathType, "Type": str},
               "ValueUnitType": {"Value": unit, "Type": int},
            },
            )
      self._eventsBefore.append(speed_event)


   def checkForAccuracyEvent(self, operator, movexItem: MovexLine):
      """
      Analyse and set the Values for an Accuracy Event and check for Activation.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      Returns:
         executeEvent (bool): True/False if the Event needs to be output
         accuracy (float): the Accuracy Value in %
         pathType (str): the PathType to be used on ("PointToPoint" or "Contour")
         criteria (int): the Accuracy Criteria (Off=0, JointDistance=2)
         unit (int): the Value's Unit (Percent=28)
      """

      executeEvent = False
      unit = 28 # 'Percent'
      
      if movexItem.accuracyHasP:
          criteria = 0 # Off
          #criteria = 3 # Distance
      else:
          criteria = 2 # JointDistance

      if movexItem.motionType == "P":
          pathType = 'PointToPoint'
      else:
          pathType = 'Contour'
      
      if movexItem.accuracyValue == 1:
          accuracy = 0.0
      elif movexItem.accuracyValue == 2:
          accuracy = 5.0
      elif movexItem.accuracyValue == 3:
          accuracy = 10.0
      elif movexItem.accuracyValue == 4:
          accuracy = 15.0
      elif movexItem.accuracyValue == 5:
          accuracy = 25.0
      elif movexItem.accuracyValue == 6:
          accuracy = 50.0
      elif movexItem.accuracyValue == 7:
          accuracy = 75.0
      else:
          accuracy = 100.0
      
      if abs(self._currentAccuracyValue - movexItem.accuracyValue) > 0.1 or self._currentAccuracyType != movexItem.accuracyHasP :
         executeEvent = True
         self._currentAccuracyValue = movexItem.accuracyValue
         self._currentAccuracyType = movexItem.accuracyHasP

      if self._currentAccuracyType == False and movexItem.accuracyValue == 1 and accuracy < 0.001:
         accuracy = 1.0
      
      return executeEvent, accuracy, pathType, criteria, unit
   

   def checkForSpeedEvent(self, operator, movexItem: MovexLine):
      """
      Analyse and set the Values for a Speed Event and check for Activation.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      Returns:
         executeEvent (bool): True/False if the Event needs to be output
         speed (float): the Speed Value
         pathType (str): the PathType to be used on ("PointToPoint" or "Contour")
         unit (int): the Value's Unit (mm/s=7 or Percent=28)
      """

      executeEvent = False

      if movexItem.speedType == "R":
          unit = 28 # 'Percent'
          speed = movexItem.speedValue
      else:
          unit = 7 # 'Speed'
          speed = movexItem.speedValue / 1000
      
      if self._currentSpeedUnit != unit:
         executeEvent = True # if Type changed, execute anyway
      self._currentSpeedUnit = unit

      if movexItem.motionType == "P":
          pathType = 'PointToPoint'
          if abs(self._currentPTPSpeed - speed) > 0.001:
              executeEvent = True
              self._currentPTPSpeed = speed
      else:
          pathType = 'Contour'
          if abs(self._currentLINSpeed - speed) > 0.001:
              executeEvent = True
              self._currentLINSpeed = speed
      
      return executeEvent, speed, pathType, unit
   

   def setAccelerationEvent(self, operator, movexItem: MovexLine):
      """
      Set on the current Motion a Acceleration-Event before, if necessary.

      Parameters:
         operator (ULPythonUploadOperator): The python upload operator
         movexItem (MovexLine): python Object that holds all Components of the MOVEX Line
      """

      executeEvent = False
      unit = 28 # 'Percent'
      
      if movexItem.motionType == "P":
          pathType = 'PointToPoint'
      else:
          pathType = 'Contour'
      
      if abs(self._currentAccelerationValue - movexItem.accelerationValue) > 0.1:
         executeEvent = True
         self._currentAccelerationValue = movexItem.accelerationValue

      if executeEvent == False:
          return
      
      if movexItem.accelerationValue == 3:
          acceleration = 0.0
      elif movexItem.accelerationValue == 2:
          acceleration = 25.0
      elif movexItem.accelerationValue == 1:
          acceleration = 50.0
      else:
          acceleration = 100.0

      acceleration_event = self.create_event_with_attributes(
            operator,
            "Acceleration",
            TPINSERTPOS_INSERTBEFORE,
            {
               "Value": {"Value": acceleration , "Type": float},
               "PathType": {"Value": pathType, "Type": str},
               "ValueUnitType": {"Value": unit, "Type": int},
            },
            )
      self._eventsBefore.append(acceleration_event)

# ======================================== END OF SPEED/ACCURACY/ACCELERATION EVENTS / START OF BASE/TOOL FRAME HANDLING =====================

   def parseForToolProfile(self, controller):
      """
      Determines the tool profile.

      Parameters:
         controller (ULPythonController): The Contoller to be checked.

      Returns:
         ULPythonToolProfile: The tool profile object if created, None otherwise
      """

      # Select Tool frame, might be set as User Attribute
      uploadRefToolFrame = ""
      uploadRefToolFrame = controller.GetString('UploadRefToolFrame', False)
      if uploadRefToolFrame != "":
         for tool_frame in self._toolProfileList:
            if tool_frame.GetName() == uploadRefToolFrame:
               self.loggingInfo(4,".....ToolFrame : Reference Tool frame named '" + uploadRefToolFrame + "' found.")
               return tool_frame
      
      # Search for the ToolIndex in the next MOVEX Command : MOVEX.....,H=1,...
      toolIndex = self.getToolIndex()

      for tool_frame in self._toolProfileList:
         self.loggingInfo(4,"..................._toolProfileList : >" + str(tool_frame.GetName()) + "<   Idx:" + str(tool_frame.GetIndex()))

      for tool_frame in self._toolProfileList:
         if tool_frame.GetName() == self._opgToolFrame:
            self.loggingInfo(4,".....ToolFrame : Getting Tool by OpGroup Comment : " + str(tool_frame.GetName()) + " = " + str(self._opgToolFrame))
            return tool_frame

      # Search the Tool List by Index Nr.
      for tool_frame in self._toolProfileList:
         if tool_frame.GetIndex() == toolIndex:
            self.loggingInfo(4,".....ToolFrame : Getting Tool by ToolIndex" + str(toolIndex) + " : " + str(tool_frame.GetName()) + " = Idx " + str(tool_frame.GetIndex()))
            return tool_frame

      # ...or get from the Tool List simply the Index
      if 0 <= toolIndex < len(self._toolProfileList):
         self.loggingInfo(4,".....ToolFrame : Getting Tool Index from MOVEX : H=" + str(toolIndex) + " : " + str(self._toolProfileList[toolIndex].GetName()))
         return self._toolProfileList[toolIndex]


      # Fallback to the first available tool profile if no match was found
      if self._toolProfileList:
            self.loggingInfo(4,".....ToolFrame : Reference Tool frame not found. Using first available Tool frame [1] " + str(self._toolProfileList[1].GetName()))
            return self._toolProfileList[1]
      
      return None
   
   def getToolIndex(self):
      """ 
      Search the next MOVEX Line to get the ToolIndex H=xxx from it
      """
      toolIndex = 1
      for i in range(1, 21):
         if len(self._lines) > (self._lineCounter + i):
            line = self._lines[self._lineCounter + i]
            if line == "END":
               break
            # self.loggingInfo(4,".\t line getToolIndex = " + str(line))
            pattern = re.compile(r'^MOVEX.*?,H=(-?\d+),') # MOVEX.....,H=1,...
            match = pattern.search(line)
            if match:
               toolIndex = int(match.group(1))  # '1'
               break
      return toolIndex


   def parseForBaseProfile(self, controller):
      """
      Determines the Base profile.

      Parameters:
         controller (ULPythonController): The Contoller to be checked.

      Returns:
         ULPythonBaseProfile: The base profile object if created, None otherwise
      """

      # Select Base frame, might be set as User Attribute
      uploadRefBaseFrame = ""
      uploadRefBaseFrame = controller.GetString('UploadRefBaseFrame', False)
      if uploadRefBaseFrame != "":
         for base_frame in self._baseProfileList:
            if base_frame.GetName() == uploadRefBaseFrame:
               self.loggingInfo(4,".....BaseFrame : Reference Base frame from UserAttribute ''UploadRefBaseFrame'' named '" + uploadRefBaseFrame + "' found.")
               return base_frame
      
      isBFOnWPPositioner = self.getBaseFrameOnWPPositioner()
      currentBaseFrame = None
      baseIndex = 0
      for base_frame in self._baseProfileList:
         self.loggingInfo(4,"..................._baseProfileList 1 : >" + str(base_frame.GetName()) + "<   Idx:" + str(base_frame.GetIndex()))
         if base_frame.GetName() == 'World':
            continue # 'World' frame is not allowed as reference frame in OLP
         elif base_frame.GetName() == '':
            continue # Unnamed frames are most likely OLP frames and are not allowed as reference frames in OLP
         elif isBFOnWPPositioner == True and base_frame.GetName().startswith("W"):
            self.loggingInfo(4,".....BaseFrame : Getting a BaseFrame on Workpiece Positioner : BF:" + str(base_frame.GetName()) + " = Idx " + str(base_frame.GetIndex()))
            return base_frame
      
      for base_frame in self._baseProfileList:
         if base_frame.GetName() == self._opgBaseFrame:
            self.loggingInfo(4,".....BaseFrame : Getting Base by OpGroup Comment : " + str(base_frame.GetName()) + " = " + str(self._opgBaseFrame))
            return base_frame

      for base_frame in self._baseProfileList:
         self.loggingInfo(4,"..................._baseProfileList 2 : >" + str(base_frame.GetName()) + "<   Idx:" + str(base_frame.GetIndex()))
         if base_frame.GetIndex() == baseIndex:
            self.loggingInfo(4,".....BaseFrame : Getting BaseFrame by BaseIndex" + str(baseIndex) + " : BF:" + str(base_frame.GetName()) + " = Idx " + str(base_frame.GetIndex()))
            return base_frame
         
      if currentBaseFrame == None and len(self._baseProfileList) > 1:
         self.loggingInfo(4,".....BaseFrame : Reference Base frame not found. Using first available Base frame [1] " + str(self._baseProfileList[1].GetName()))
         return self._baseProfileList[1]

      return currentBaseFrame
   
   def getBaseFrameOnWPPositioner(self):
      """ 
      Search the next MOVEX Line and check if Motion is related to a Workpiece Positioner BaseFrame (...,M1W,...)
      """
      for i in range(1, 21):
         if len(self._lines) > (self._lineCounter + i):
            line = self._lines[self._lineCounter + i]
            if line == "END":
               break
            # self.loggingInfo(4,".\t line getToolIndex = " + str(line))
            pattern = re.compile(r'^MOVEX.*?,M(\d+)W,')
            match = pattern.search(line)
            if match:
               self.loggingInfo(4,".....................BaseFrame seems to be on Workpiece Positioner ...,M1W,...")
               return True
      return False

# ============================================= END OF BASE/TOOL FRAME HANDLING / START OF UTILITIES EVENTS CREATION =========================

   def convertValue(self, value : str, targetType : str):
      """
      Coverts the input string value to the target type e.g. string to int or double etc...

      Parameters:
         value (str): Value to be converted
         targetType (str): target for conversion

      Returns:
         Converted value, in case of error we raise ValueError
      """
      max_unsigned_int = 2**32 - 1
      double_max = sys.float_info.max
      double_min = sys.float_info.min

      execptional_values = {
         "float min negative: -1.7976931348623157e+308": double_min,
         "float max: 1.7976931348623157e+308": double_max,
         "notDefined": max_unsigned_int
      }
      
      try:
         if targetType == 'int':
               return int(value)
         elif targetType == 'bool':
               if isinstance(value, str) and value.strip().lower() == 'true':
                  return True
               return False
         elif targetType == 'float':
               return round(float(value), 6)
         elif targetType == 'string':
               return str(value)
         else:
               raise ValueError(f"Unsupported target type: {targetType}")
      except (ValueError, TypeError):
         # If conversion fails, check if the value is in the dictionary
         if value in execptional_values:
               return execptional_values[value]
         else:
               raise ValueError(f"Unable to convert or find value: {value} with target type {targetType}")

   @classmethod
   def create_event_with_attributes(cls, operator: ULPythonUploadOperator, event_name, insert_pos, attributes: dict):
      event: ULPythonEvent = operator.CreateEmptyEvent()
      event.SetName(event_name)
      event.SetInsertPosition(insert_pos)
      if attributes is None:
         attributes = {}
      
      unit = 0
      for name, attribute_data in attributes.items():
         if name == "ValueUnitType":
            unit = attribute_data["Value"]
      for name, attribute_data in attributes.items():
         attribute = cls.create_attribute(operator, name, attribute_data, unit)
         event.AddAttribute(attribute)
      return event
   
   @classmethod
   def create_attribute(cls, operator: ULPythonUploadOperator, name: str, attribute_data: dict = None, unit: int = 0):
      if attribute_data is None:
         attribute_data = {"Value": None, "Type": str}
      value = attribute_data["Value"]
      attribute_type = attribute_data["Type"]
      attribute_creator: OlpCorePythonAttributeSetterOperator = operator.GetAttributeSetterOperator()
      attribute_creator_map = {
         float: attribute_creator.CreateWritingDoubleAttributesObject,
         int: attribute_creator.CreateWritingIntAttributesObject,
         str: attribute_creator.CreateWritingStringAttributesObject,
         bool: attribute_creator.CreateWritingBoolAttributesObject,
         enumerate: attribute_creator.CreateWritingLiteralAttributesObject,
      }
      if attribute_type not in attribute_creator_map:
         raise TypeError(f"Unsupported attribute type: {attribute_type}")
      attribute = attribute_creator_map[attribute_type]()
      if attribute_type == enumerate and "Values" in attribute_data:
         values = attribute_data["Values"]
         attribute.SetValues(values)
      attribute.SetName(name)
      attribute.SetValue(value)
      if name == "Value":
         attribute.SetValueUnitType(unit)
      return attribute
