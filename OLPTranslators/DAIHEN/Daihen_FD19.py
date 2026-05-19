"""
COPYRIGHT Cenit AG 2025
   Production ready OTC-DAIHEN Downloader
"""

import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from datetime import datetime
from dataclasses import dataclass

from cenpylib import FileUtility
from cenpyolpcore import *
from cenpydownload import *
from cenpyunits import Converter
from cenpyunits import Length


import locale
locale.setlocale(locale.LC_NUMERIC,'C')

# CONSTANTS
COMMA = ","
DOWNLOAD_CLASS_NAME = "Daihen_FD19"

# kinematic    
DRIVEN_JOINT = 0
SYNCHRONOUS_JOINT = 1
# joint object array
JOINT_DATA_TYPE = 0
JOINT_VALUE = 1

@dataclass
class Daihen_FD19(Downloader):
   """DAIHEN_FD19 downloader
   Base robot vendor downloader
   Derived from: Base downloader
   """
   
#################### BASE FUNCTIONS ####################

   def __init__(self) -> None:
      """Class initialization
      """
      super().__init__()
      #
      self.FileUtil = FileUtility()
      self.OnDev=False
      # output file path
      self.OutputFilePath = ""

      # store the program name
      self.ProgramName = ""
      # store the OTC Unit
      self.ProgramUnit = ""
      # store the OTC Mechanisms in Unit
      self.MechsInUnit = ""
      # store the OTC Controller series
      self.OtcCtrlSeries = ""
      # store the OTC Controller manufacturer
      self.OtcCtrlMfg = ""
      # store the OTC Smoothness
      self.OtcSmoothness = ""
      # array to store header content
      self.Header = []
      # array to store application command
      # e.g. arc welding equipment
      self.SourceHeader = []
      # array to store motion commands
      self.Source = []
      self.Source.append('')
      # array to store motion commands
      self.DataHeader = []
      self.DataHeader.append('')
      # array to store point coordinates and joints
      self.Data = []
      # program Footer text
      self.Footer = []
      
      self.LastOrientation = [0.0, 0.0, 0.0]

      # store the currently used base frame index
      # min = 0; max = 9
      self.CurrentBaseFrameIndex = -1
      self.BaseFrameMinIndex = 0
      self.BaseFrameMaxIndex = 9
      # store the currently used tool frame index
      # min = 0; max = 10
      self.CurrentToolFrameIndex = -1
      self.ToolFrameMinIndex = 0
      self.ToolFrameMaxIndex = 10
      
      self.HasWorkpiecePositioner = False
      self.BaseTargetMode = 'X'
      
      # store the currently used feedrate; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpFeedrate = 50
      # store the currently used feedrate; expected unit = [mm/sec]
      self.CurrentLinFeedrate = 100
      # max. FeedRate of the Robot Resource
      self.MaxTCPFeedrate = 1.0
      # store the currently used accuracy; expected unit = [%]
      # min = 0; max = 100
      self.CurrentOutAccuracy = 0
      self.CurrentOutAccuracyLevel = "8"
      self.CurrentAccuracyActive = True
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpAcceleration = 100
      self.CurrentPtpAccelerationLevel = ""
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 100
      self.CurrentLinAcceleration = 100
      self.CurrentLinAccelerationLevel = ""
      # maximum character for comments
      self.MaxCharComments = 128

      # point counter
      self.PointCounter = int(0)
      # line counter for motion instruction
      self.SourceLineCounter = 0

      # Group indexes of mechanisms
      self.GroupRobot = -1
      self.GroupEndEffector = -1
      self.GroupRail = -1
      self.GroupWpPosition = -1
      self.SynchronousOnRobot = -1
      
      self.GroupRobotMainList = []
      self.GroupEndEffectorList = []
      self.GroupRailList = []
      self.GroupWpPositionList = []
      
      # special Handling 7-Axer
      self.SevenAxisRobot = False
      self.Ax7Robot7thAxName = "D1"
      self.Ax7RobotAxisOrder = ["D1","D2","D3","D4","D5","D6","D7"]

      # Special motion treatment flag
      self.SpecialMotion = False

      # Resource attributes
      self.CENOlpSuppressConfig  = False

      # used language in user interface
      self.Language = ""

      self.IsUploadedOperation = False

      self.Logging = None

#################### BASE FUNCTIONS ####################

   def DevLogging(self, info):
      if self.OnDev == True and self.Logging != None:
         self.Logging.LogInfo(info)

   def Initialize(self, operator : DULPythonDownloadOperator):
      """Translator initialization.
      Called only once per download, even when downloading sub programs

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # get language
      self.Language = operator.GetCurrentLanguage()
      
      # global Logger
      self.Logging = operator.GetLogOperator()

      self.DevLogging('============================= DOWNLOAD DAIHEN FD 19 START ===================================')

      # Get robot resource and its attributes
      controller = operator.GetController()
      resources=controller.GetResources()
      for resource in resources:
         if (resource.GetItemType().name=='Production'):
            if (resource.GetItemSubType().name=='MachineRobot'):
               robot=resource
               robotAttributes=robot.GetAttributes()
               for att in robotAttributes:
                  # OTC suppress CONF statement in output
                  if att.GetName() == 'CENOlpSuppressConfig':
                     self.CENOlpSuppressConfig = robot.GetBool('CENOlpSuppressConfig',1)
               self.MaxTCPFeedrate = resource.GetMaxSpeed()
            if (resource.GetItemSubType().name=='WorkpiecePositioner'):
               self.DevLogging('............Resource WorkpiecePositioner found.')
               self.HasWorkpiecePositioner = True

   def CheckFrame(self, frameName):
      '''Check the current Frame Name for W or W1..9 or anything else'''
      if frameName == "W":
        return True
      elif len(frameName) == 2 and frameName[0] == "W" and frameName[1].isdigit() and 1 <= int(frameName[1]) <= 9:
         return True
      else:
         return False

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
         """
      # get program name
      self.ProgramName = program.GetName()
      # get OTC programmed unit name
      progAttribs = program.GetAttributes()
      for attrib in progAttribs:
         if attrib.GetName() == 'OTC_UNIT_NAME':
            self.ProgramUnit=attrib.GetValue()
         if attrib.GetName() == 'OTC_UNIT_MECHS':
            self.MechsInUnit=attrib.GetValue()
         if attrib.GetName() == 'OTC_SMOOTHNESS':
            self.OtcSmoothness=str(attrib.GetValue())
         if attrib.GetName() == 'CONTROLLER_SERIES':
            self.OtcCtrlSeries=attrib.GetValue()
         if attrib.GetName() == 'CONTROLLER_MANUFACTURER':
            self.OtcCtrlMfg=attrib.GetValue()
      if self.ProgramUnit == '':
         self.ProgramUnit='NB6-A'
      if self.MechsInUnit == '':
         self.MechsInUnit='1'
      
      profile = program.GetUsedBaseProfile()
      if profile:
         refProfile = profile.GetReferenceProfile()
         refName = 'None'
         if refProfile:
            refName = refProfile.GetName()
         self.DevLogging('............Program BaseFrame : ' + str(profile.GetName()) + ' | index : ' + str(profile.GetIndex()) + ' | referenceFrame : ' + str(refName))
      if profile.GetIndex() > 0 and self.HasWorkpiecePositioner == True and self.CheckFrame(str(profile.GetName())):
            self.BaseTargetMode = 'XW' # or profile.GetName()
            self.DevLogging('................TargetMode set to "' + str(self.BaseTargetMode) + '"')
            self.Logging.LogWarn('Due to the selected BaseFrame, the Download Taget Mode is set to "' + self.BaseTargetMode + '" e.g. ...,M1' + self.BaseTargetMode + ',...')
      
      self.DownloadJointsOnly = program.GetBool('DownloadJointsOnly', True)
      #self.DevLogging(".......found AW_DOWNLOAD_JOINTS_ONLY = DownloadJointsOnly = " + str(self.DownloadJointsOnly))

   def OperationGroupStart(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      """Operation Group start

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operationGroup (DULPythonOperationGroup):operation group operator gives access to the current operation group
      """
      logger = operator.GetLogOperator()

      # get base frame index
      baseProfile = operationGroup.GetUsedBaseProfile()
      baseIndex = baseProfile.GetIndex()
      # check if index is within range and update base frame
      self.CheckAndUpdateBaseFrame(logger, baseIndex)

      # get tool frame index
      toolProfile = operationGroup.GetUsedToolProfile()
      toolIndex = toolProfile.GetIndex()



      # check if index is within range and update tool frame
      self.CheckAndUpdateToolFrame(logger, toolIndex)

      # Add operation group name
      operationGroupName = 'REM "Operation Group: ' + operationGroup.GetName() + '"'
      if operationGroupName != "":
         self.AddLineToSource(operationGroupName)
      opgroupFrames = 'REM "BaseFrame: ' + str(baseProfile.GetName()) + ' ToolFrame: ' + str(toolProfile.GetName())
      #self.AddLineToSource(opgroupFrames)
      self.OtcSmoothness=str(operationGroup.GetInteger('OTC_SMOOTHNESS',1))

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Operation start

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator gives access to the current operation
      """
      logger = operator.GetLogOperator()

      if operation.GetOperationType().name == "Upload":
         self.IsUploadedOperation = True
      else:
         self.IsUploadedOperation = False

      # get base frame index
      baseProfile = operation.GetUsedBaseProfile()
      baseIndex = baseProfile.GetIndex()
      # check if index is within range and update base frame
      self.CheckAndUpdateBaseFrame(logger, baseIndex)

      # get tool frame index
      toolProfile = operation.GetUsedToolProfile()
      toolIndex = toolProfile.GetIndex()

      # check if index is within range and update tool frame
      self.CheckAndUpdateToolFrame(logger, toolIndex)

      if toolIndex < self.ToolFrameMinIndex or toolIndex > self.ToolFrameMaxIndex:
         tpName = toolProfile.GetName()
         controller = operator.GetController()
         toolProfileList = controller.GetToolProfiles()
         iC = 0
         for tool_frame in toolProfileList:
            iC += 1
            if tpName == tool_frame.GetName():
               if toolIndex < self.ToolFrameMinIndex or toolIndex > self.ToolFrameMaxIndex:
                  self.CurrentToolFrameIndex = iC

      # # Add operation name
      # operationName = "'   Operation: " + operation.GetName()
      # if operationName != "":
      #    self.AddLineToSource(operationName)
      self.OtcSmoothness=str(operation.GetInteger('OTC_SMOOTHNESS',1))

   def HandleMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Evaluation of toolpath elements and events

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # handle events, inserted before. Do not handle events which to change toolpath element output
      eventsBefore = motion.GetEventsBefore()
      # iterate through events
      for event in eventsBefore:
         self.HandleEvent(operator, motion, event)

      # handle source section of the motion
      self.HandleSourceSection(operator, motion)

      # handle events, inserted after. Do not handle events which to change toolpath element output
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         self.HandleEvent(operator, motion, event)

   def SubprogramStart(self, operator: DULPythonDownloadOperator, subProgram : DULPythonSubprogram):
      """called when a sup program is called

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         subprogram (DULPythonSubprogram): sub program operator gives access to the complete sub program
      """
      # get sub program name
      subProgramName = subProgram.GetName()
      # add call in program
      self.AddLineToSource('CALLP %s;' % subProgramName)

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      """Called at the end of each the program 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      self.AddLineToFooter("END")

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Create output file
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # get controller
      controller = operator.GetController()
      # get controller
      program = controller.GetActiveProgram()

      logger = operator.GetLogOperator()

      # validate if program name confirms to Daihen rules
      if not self.checkOtcProgramName(self.ProgramName):
         logger.LogError('Invalid Program name: Has to be only digits and 3-4 characters long.')

      # get output directory
      outputDir = controller.GetOutputDirectory()
      # define output path
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      upload = self.IsUploadedOperation
      if ktaTest == "TRUE" and upload == True:
         self.OutputFilePath = outputDir + "\\upload.prg"
      else:
         self.OutputFilePath = outputDir + "\\" + self.ProgramUnit + "." + self.ProgramName
      # create Header
      self.CreateHeader(operator)

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Write output file

      Args:
         operator: download operator
      """
      # create file and output the program
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Footer)

      self.Header.clear()
      self.SourceHeader.clear()
      self.Source.clear()
      self.Footer.clear()

      operator.AddOutputFilePath(self.OutputFilePath)
      
#################### SOURCE SECTION ####################

   def HandleSourceSection(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Handles the output of the motion dependent on motion type to the source section

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # contains the string of one source line.
      sourcePosition = ''
      # check if motion pre processing necessary and if the normal/general motion output must be skipped
      isRef = motion.IsReferenceMotion()
      # motion.GetPosition().GetXYZ()
      # check if the motion is a reference motion or if the motion was already processed
      if not isRef and not self.SpecialMotion:
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # create LIN source string
            sourcePosition = self.OutputSourceLin(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string
            sourcePosition = self.OutputSourceCirc(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

         # check if the motion is of type point to point
         else:
            # create PTP source string
            sourcePosition = self.OutputSourcePtp(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

      if self.SpecialMotion:
         # create reference position output if needed
         sourcePosition = self.OutputSourceSpecialMotion(operator, motion)
         # add string to source array
         if not (sourcePosition == ''):
            self.AddLineToSource(sourcePosition)
         self.SpecialMotion = False

      # reset skip source creation
      self.SpecialMotion = False

   def OutputSourceSpecialMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output reference position if needed in technology versions of this base downloader
      e.g. cycle centerpoint or No-Sim-Download-Only

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """

      return('')

   def OutputSourcePtp(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output point to point motion
      MOVEX A=1P,AC=0,SM=0,M1J,P,(-3.56, 41.65, 11.93, 33.56, 132.76, -157.18),R=50,H=0,MS,M2J,P,(2250.00, 0.00, 185.00),R=50,H=0,M3J,P,(90.00, 0.00),R=50,H=0
      MOVEX A=1P,AC=0,SM=0,M1X,P,(1698.56, -366.73, 1123.17, 21.93, 40.34, 31.88),CONF=1020,R=50,H=0,MS,M2J,P,(2250.00, 851.62, 185.00),R=50,H=0,M3J,P,(90.00, 0.00),R=50,H=0

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += int(1)

      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentAccuracyActive:
         # exact stop
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel)
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel) + 'P'

      # check if acceleration is programmed
      if self.CurrentPtpAcceleration == 100:
         acceleration = 'AC=0'
      else:
         acceleration = 'AC=%s' % self.CurrentPtpAccelerationLevel

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()
      # forced Joint Output
      if self.DownloadJointsOnly == True:
         motionTargetType = TargetType.Joint

      # create motion group structure but skip non-Unit mechanisms
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

      sOutput = "MOVEX " + accuracy + "," + acceleration + "," + 'SM=' + self.OtcSmoothness
      
      if motionGroupRobot != None:
         targetConfig = motionGroupRobot.Config

         if motionTargetType == TargetType.Cartesian:
            targetMode = self.BaseTargetMode
         else:
            targetMode = "J"

         sOutput = sOutput  + ","

         if self.GroupRail > 0 or self.GroupWpPosition > 0:
            sOutput = sOutput + ""
         else:
            sOutput = sOutput + ""

         # #Robot mechanism joints/cartesian target
         sOutput = sOutput + "M" + str(self.GroupRobot) + targetMode + ",P,"
         sOutput = sOutput + motionGroupRobot.TargetOutput
         sOutput = sOutput + ",R=" + f'{self.CurrentPtpFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex) + ",MS"
         if not self.CENOlpSuppressConfig:
            sOutput = sOutput + targetConfig
         if self.SevenAxisRobot == True:
            sOutput = sOutput + ",M" + str(self.SynchronousOnRobot) + "J,P," + motionGroupRobot.TargetOutputSecond
            sOutput = sOutput + ",R=" + f'{self.CurrentPtpFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex)
      
      # further Axis (Rail, WP, etc.)
      sOutput = sOutput + self.OutputSourceExternalJointsOnly(operator, motionGroups, accuracy, acceleration)

      return('%s' % (sOutput))

   def OutputSourceLin(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output linear motion
      MOVEX A=2P,AC=0,SM=0,M1X,L,(1822.33, -471.92, 1362.38, 21.93, 40.34, 31.88),CONF=1020,S=200,H=0,MS,M2J,P,(2250.00, 851.62, 185.00),S=200,H=0,M3J,P,(90.00, 0.00),S=200,H=0
      MOVEX A=2P,AC=0,SM=0,M1J,L,(11.27, 36.04, 48.04, 21.85, 111.82, -188.45),S=500,H=0,MS,M2J,P,(2250.00, 851.62, 185.00),S=500,H=0,M3J,P,(90.00, 0.00),S=500,H=0

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += 1

      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentAccuracyActive:
         # exact stop
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel)
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel) + 'P'

      # check if acceleration is programmed
      if self.CurrentLinAcceleration == 100:
         acceleration = 'AC=0'
      else:
         acceleration = 'AC=%s' % self.CurrentLinAccelerationLevel

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()
      # forced Joint Output
      if self.DownloadJointsOnly == True:
         motionTargetType = TargetType.Joint

      # create motion group structure but skip non-Unit mechanisms
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

      sOutput = "MOVEX " + accuracy + "," + acceleration + "," + 'SM=' + self.OtcSmoothness

      if motionGroupRobot != None:
         targetConfig = motionGroupRobot.Config

         if motionTargetType == TargetType.Cartesian:
            targetMode = self.BaseTargetMode
         else:
            targetMode = "J"

         sOutput = sOutput  + ","

         if self.GroupRail > 0 or self.GroupWpPosition > 0:
            sOutput = sOutput + "HM,"
         else:
            sOutput = sOutput + ""

         # #Robot mechanism joints/cartesian target
         sOutput = sOutput + "M" + str(self.GroupRobot) + targetMode + ",L,"
         sOutput = sOutput + motionGroupRobot.TargetOutput
         sOutput = sOutput + ",S=" + f'{self.CurrentLinFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex) + ",MS"
         if not self.CENOlpSuppressConfig:
            sOutput = sOutput + targetConfig
         if self.SevenAxisRobot == True:
            sOutput = sOutput + ",M" + str(self.SynchronousOnRobot) + "J,P," + motionGroupRobot.TargetOutputSecond
            sOutput = sOutput + ",R=" + f'{self.CurrentPtpFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex)
      
      # further Axis (Rail, WP, etc.)
      sOutput = sOutput + self.OutputSourceExternalJointsOnly(operator, motionGroups, accuracy, acceleration)

      return('%s' % (sOutput))

   def OutputSourceCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output circular motion
      MOVEX A=3P,AC=0,SM=0,M1X,C1,(280.64, -49.05, 2397.42, -160.19, 45.0, -0.72),CONF=1020,S=30,H=0,MS,M2J,P,(882.77, 668.81, 785.53),S=30,H=0,M3J,P,(0.0, 0.00),S=30,H=0
      MOVEX A=3P,AC=0,SM=0,M1X,C2,(302.35, -98.03, 2397.42, -152.99, 45.0, 0.02),CONF=1020,S=30,H=0,MS,M2J,P,(882.77, 668.81, 785.53),S=30,H=0,M3J,P,(0.0, 0.00),S=30,H=0

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += 1
      self.PointCounter += 1

      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentAccuracyActive:
         # exact stop
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel)
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'A=' + str(self.CurrentOutAccuracyLevel) + 'P'

      # check if acceleration is programmed
      if self.CurrentLinAcceleration == 100:
         acceleration = 'AC=0'
      else:
         acceleration = 'AC=%s' % self.CurrentLinAccelerationLevel

      # get via position
      positionVia = motion.GetViaPosition()
      # get Cir end position
      positionCir = motion.GetPosition()
      # get motion target type
      motionTargetType = positionVia.GetTargetType()
      # forced Joint Output
      if self.DownloadJointsOnly == True:
         motionTargetType = TargetType.Joint

      # create motion group structure but skip non-Unit mechanisms
      motionGroupsVia = self.CreateMotionGroupStructure(operator, positionVia)
      motionGroupsCir = self.CreateMotionGroupStructure(operator, positionCir)
      motionGroupCir = self.GetMotionGroupByIndex(motionGroupsCir, self.GroupRobot)
      motionGroupVia = self.GetMotionGroupByIndex(motionGroupsVia, self.GroupRobot)

      sOutput = "MOVEX " + accuracy + "," + acceleration + "," + 'SM=' + self.OtcSmoothness

      if motionGroupVia != None and motionGroupCir != None:
         targetConfig = motionGroupCir.Config

         if motionTargetType == TargetType.Cartesian:
            targetMode = self.BaseTargetMode
         else:
            targetMode = "J"
         sOutput = sOutput  + ","
         if self.GroupRail > 0 or self.GroupWpPosition > 0:
            sOutput = sOutput + "HM,"
         else:
            sOutput = sOutput + ""
            pass

         # #Robot mechanism joints/cartesian target
         sOutputVia = sOutput + "M" + str(self.GroupRobot) + targetMode + ",C1,"
         sOutputVia = sOutputVia + motionGroupVia.TargetOutput
         if not self.CENOlpSuppressConfig:
            sOutputVia = sOutputVia + targetConfig
         sOutputVia = sOutputVia + ",S=" + str(self.CurrentLinFeedrate) + ",H=" + str(self.CurrentToolFrameIndex) + ",MS"
         if self.SevenAxisRobot == True:
            sOutputVia = sOutputVia + ",M" + str(self.SynchronousOnRobot) + "J,P," + motionGroupVia.TargetOutputSecond
            sOutputVia = sOutputVia + ",R=" + f'{self.CurrentPtpFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex)
         
         sOutputCir = sOutput + "M" + str(self.GroupRobot) + targetMode + ",C2,"
         sOutputCir = sOutputCir + motionGroupCir.TargetOutput
         if not self.CENOlpSuppressConfig:
            sOutputCir = sOutputCir + targetConfig
         sOutputCir = sOutputCir  + ",S=" + str(self.CurrentLinFeedrate) + ",H=" + str(self.CurrentToolFrameIndex) + ",MS"
         if self.SevenAxisRobot == True:
            sOutputCir = sOutputCir + ",M" + str(self.SynchronousOnRobot) + "J,P," + motionGroupCir.TargetOutputSecond
            sOutputCir = sOutputCir + ",R=" + f'{self.CurrentPtpFeedrate:.1f}' + ",H=" + str(self.CurrentToolFrameIndex)
      
      # further Axis (Rail, WP, etc.)
      sOutputVia = sOutputVia + self.OutputSourceExternalJointsOnly(operator, motionGroupsVia, accuracy, acceleration)
      sOutputCir = sOutputCir + self.OutputSourceExternalJointsOnly(operator, motionGroupsCir, accuracy, acceleration)

      sOutput = sOutputVia + "\n" + sOutputCir
      return('%s' % (sOutput))

   def OutputSourceExternalJointsOnly(self, operator: DULPythonDownloadOperator, motionGroups, accuracy, acceleration):
      """Output the external motion groups with joint values

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motionGroup: motion groups with all joints
      """
      sOutputRobot = ""
      sOutputEndeffector = ""
      sOutputRail = ""
      sOutputWpPosi = ""
      # 7-axis robot mechanism joints target
      # TODO: output joint 7 of robot when robot target is cartesian
      motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

      # Assign external axes groups if present
      if self.GroupEndEffector > 0:
         for grpIdx in self.GroupEndEffectorList:
            motionGroupEndeffector = self.GetMotionGroupByIndex(motionGroups, grpIdx)
            sOutputEndeffector += ",M" + str(grpIdx) + "J,P,"
            sOutputEndeffector += motionGroupEndeffector.TargetOutput + ",R=" + str(self.CurrentPtpFeedrate) + ",H=" + str(self.CurrentToolFrameIndex)
      if self.GroupRail > 0:
         for grpIdx in self.GroupRailList:
            motionGroupRail = self.GetMotionGroupByIndex(motionGroups, grpIdx)
            sOutputRail += ",M" + str(grpIdx) + "J,P,"
            sOutputRail += motionGroupRail.TargetOutput + ",R=" + str(self.CurrentPtpFeedrate) + ",H=" + str(self.CurrentToolFrameIndex)
      if self.GroupWpPosition > 0:
         for grpIdx in self.GroupWpPositionList:
            motionGroupWpPosi = self.GetMotionGroupByIndex(motionGroups, grpIdx)
            sOutputWpPosi += ",M" + str(grpIdx) + "J,P,"
            sOutputWpPosi += motionGroupWpPosi.TargetOutput + ",R=" + str(self.CurrentPtpFeedrate) + ",H=" + str(self.CurrentToolFrameIndex)

      # Concatenate the mechanism groups in the correct order
      sOutput = sOutputRobot + sOutputEndeffector
      if self.GroupRail < self.GroupWpPosition:
         sOutput = sOutput + sOutputRail + sOutputWpPosi
      else:
         sOutput = sOutput + sOutputWpPosi + sOutputRail

      return('%s' % (sOutput))

#################### EVENTS ####################

   def HandleEvent(self, operator: DULPythonDownloadOperator, currentMotion: DULPythonMotion, event: DULPythonEvent):
      """Handle event
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # handle build in events like speed, accuracy
      self.HandleBuildInEvents(operator, event)
      
      # get motions of the event
      motions = event.GetMotions()
      # handle each motion of the event
      for motion in motions:
         self.HandleMotion(operator, motion)

   def HandleBuildInEvents(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handle build in events like speed, accuracy, ...

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # check if speed event
      if event.GetName() == 'Speed':
         self.SetSpeed(operator, event)
      # check if accuracy event
      elif event.GetName() == 'Accuracy':
         self.SetAccuracy(operator, event)
      # check if acceleration event
      elif event.GetName() == 'Acceleration':
         self.SetAcceleration(operator, event)
      # text event
      elif event.GetName() == 'TextEvent':
         self.TextEvent(operator, event)
      # dwell event
      elif event.GetName() == 'Dwell':
         self.OutputDwellEvent(operator, event)
      # logic port event
      if event.GetName() == 'LogicPort':
         self.LogicPortEvent(operator, event)
      # 
      if event.GetName() == 'SetResourcePort':
         self.ResourcePortEvent(operator, event)
      # 
      if event.GetName() == 'WaitForResourcePort':
         self.ResourcePortEvent(operator, event)

   def SetSpeed(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set the current feedrate from speed event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      pathtype = ''
      speed = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            speed=attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype=attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinFeedrate = int(speed * 1000)
      else:
         if speed <= self.MaxTCPFeedrate:
            self.CurrentPtpFeedrate = int((speed / self.MaxTCPFeedrate) * 100) # PTP m/s --> %
         else:
            self.CurrentPtpFeedrate = int(speed) # PTP  % = %
   
   def SetAccuracy(self, operator, event):
      """Set current accuracy from accuracy event

      Args:
         operator: download operator
         event: event object
      """
      logger = operator.GetLogOperator()
      pathtype= ''
      accuracy = -1
      criteria = ''
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            accuracy = attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
         if attribute.GetName() == 'Criteria':
            criteria = attribute.GetValue()
      if criteria =='On':
         self.CurrentAccuracyActive = True
         if accuracy > 0.0:
            # distinguish between contour and point to point
            if pathtype == 'Contour':
               self.CurrentLinAccuracy = int(accuracy * 1000)
               if self.CurrentLinAccuracy > 100:
                  logger.LogInfo('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
                  self.CurrentLinAccuracy = 100
            else:
               self.CurrentPtpAccuracy = int(accuracy)
      if criteria == 'Off':
         self.CurrentAccuracyActive = False
         if self.IsUploadedOperation == True:
            self.CurrentOutAccuracy = accuracy
      if criteria == 'Distance':
         self.CurrentOutAccuracy = int(accuracy * 1000)
         if self.CurrentOutAccuracy > 100:
            logger.LogInfo('Accuracy value for linear motion is out of range (%d). Accuracy is set to max value of 100.' % (self.CurrentOutAccuracy))
            self.CurrentOutAccuracy = 100
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      if criteria == 'JointDistance':
         self.CurrentOutAccuracy = int(accuracy)
         if self.CurrentOutAccuracy > 100:
            logger.LogInfo('Accuracy value for PTP motion is out of range (%d). Accuracy is set to max value of 100.' % (self.CurrentOutAccuracy))
            self.CurrentOutAccuracy = 100
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      self.CurrentOutAccuracyLevel = self.AccuToNearestLevel(self.CurrentOutAccuracy)
      self.CurrentOutAccuracyLevel = self.AccuToNearestLevel(self.CurrentOutAccuracy)
      #logger.LogInfo('Acceleration PTP %s ' % (self.CurrentOutAccuracyLevel))
      #logger.LogInfo('Acceleration LIN %s ' % (self.CurrentOutAccuracyLevel))

   def AccuMapToLevel(self, percentage):
      """Map current accuracy percentage level

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      if percentage == 0:
         return '1'
      elif percentage <= 5:
         return '2'
      elif percentage <= 10:
         return '3'
      elif percentage <= 15:
         return '4'
      elif percentage <= 25:
         return '5'
      elif percentage <= 50:
         return '6'
      elif percentage <= 75:
         return '7'
      elif percentage <= 100:
         return '8'
      else:
         return '8'

   def AccuToNearestLevel(self, percentage):
      """Compute correct current accuracy percentage level

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      level = self.AccuMapToLevel(percentage)
      if level == 'Invalid Percentage':
         return level
      else:
         lower_percentage = [0, 5, 10, 15, 25, 50, 75]
         higher_percentage = [5, 10, 15, 25, 50, 75, 100]
         for idx, (lower, higher) in enumerate(zip(lower_percentage, higher_percentage)):
               if lower <= percentage < higher:
                  if percentage - lower < higher - percentage:
                     return f'{idx+1}'
                  else:
                     return f'{idx+2}'
         return level

   def SetAcceleration(self, operator, event):
      """Set the current acceleration from acceleration event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      pathtype = ''
      acceleration = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            acceleration = attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinAcceleration = int(acceleration * 100)
         if self.CurrentLinAcceleration > 100:
            logger.LogInfo('Acceleration value for point to point is out of range (%d). Max value is 100.' % (self.CurrentLinAcceleration))
            self.CurrentLinAcceleration = 100
         self.CurrentLinAccelerationLevel = self.AccelToNearestLevel(self.CurrentLinAcceleration)
      else:
         self.CurrentPtpAcceleration = int(acceleration)
         if self.CurrentPtpAcceleration > 100:
            logger.LogInfo('Acceleration value for linear is out of range (%d). Max value is 100.' % (self.CurrentPtpAcceleration))
            self.CurrentPtpAcceleration = 100
         self.CurrentPtpAccelerationLevel = self.AccelToNearestLevel(self.CurrentPtpAcceleration)

   def AccelMapToLevel(self, percentage):
      """Map current accuracy percentage level

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      if percentage == 0:
         return '3'
      elif percentage <= 33:
         return '2'
      elif percentage <= 66:
         return '1'
      elif percentage <= 100:
         return '0'
      else:
         return '0'

   def AccelToNearestLevel(self, percentage):
      """Compute correct current accuracy percentage level

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      level = self.AccelMapToLevel(percentage)
      if level == 'Invalid Percentage':
         return level
      else:
         lower_percentage = [0, 33, 66]
         higher_percentage = [33, 66, 100]
         for idx, (lower, higher) in enumerate(zip(lower_percentage, higher_percentage)):
               if lower <= percentage < higher:
                  if percentage - lower < higher - percentage:
                     return f'{idx+1}'
                  else:
                     return f'{idx+2}'
         return level

   def TextEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """text event implementation

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get all attributes
      attributes = event.GetAttributes()
      # initialize variables
      text = ''
      isComment = True
      # iterate through attributes
      for attribute in attributes:
         # get text
         if attribute.GetName() == 'Text':
            text = attribute.GetValue()
            textItems = text.split("|")
         # get flag is text is a comment (True) or command (False)
         elif attribute.GetName() == 'IsComment':
            isComment = attribute.GetValue()
      # check if comment
      for textItem in textItems:
         if isComment:
            # create string and add it to source string array
            self.OutputOtcComment(operator, textItem)
         else:
            self.AddLineToSource(textItem)

   def OutputOtcComment(self, operator: DULPythonDownloadOperator, comment: str):
      """Output a comment in source section of Fanuc robot program

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         comment (str): string containing the comment
      """
      # get logger operator
      logger = operator.GetLogOperator()
      # plausibility check for string length
      if len(comment) > self.MaxCharComments:
         logger.LogInfo('value of text event is too long. Max 16 character. Value: %s' % (comment))
         comment = comment[:self.MaxCharComments]
      # add comment to source section
      self.AddLineToSource('REM "%s' % (comment) + '"')

   def OutputDwellEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Output wait n seconds command

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get logging operator
      logger = operator.GetLogOperator()
      # init variable
      time = -1.0
      # get all attributes
      attributes = event.GetAttributes()
      # iterate through attributes
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            # get time in second
            time = attribute.GetValue()
      # Plausibility check
      if time == -1.0:
         logger.LogError("Couldn't get time value from Dwell event. Check download")
         self.AddLineToSource('ERROR DWELL EVENT')
      # add dwell command
      self.AddLineToSource('DELAY %.1f' % (time))

   def LogicPortEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set signal bool event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get logging operator
      logger = operator.GetLogOperator()
      # init variables
      eventType = ''
      signalName = ''
      signalAddress = ''
      signalNumber = 0
      # get list opf attributes
      attributes = event.GetAttributes()
      # iterate through attribute list
      for attribute in attributes:
         # get event type, could be following values:
         # - CENE2SetSignal
         # - CENE2SetSignalInt <- not supported in default
         # - CENE2SetSignalFloat <- not supported in default
         # - CENE2SetSignalByte <- not supported in default
         # - CENE2SetSignalShortInt <- not supported in default
         # - CENE2WaitForSignal
         # - CENE2WaitForSignalInt <- not supported in default
         # - CENE2WaitForSignalFloat <- not supported in default
         # - CENE2WaitForSignalByte <- not supported in default
         # - CENE2WaitForSignalShortInt <- not supported in default
         if attribute.GetName() == 'EventType':
            eventType = attribute.GetValue()
         # get the signal name
         if attribute.GetName() == 'SignalName':
            signalName = attribute.GetValue()
         # address is the automatically generated stirring of the signal address (e.g. DO3)
         elif attribute.GetName() == 'SignalAddress':
            signalAddress = attribute.GetValue()
            try:
               # cut DI or DO and convert the number to an integer
               signalNumber = int(signalAddress[1:])
            except:
               logger.LogError("DOWNLOADER EXCEPTION: couldn't convert signal address to signal number. Check download")
               self.AddLineToSource('ERROR converting signal address to signal number.')
         # get the signal value. Can be bool, int, float, ...
         elif attribute.GetName() == 'SignalValue':
            signalValue = attribute.GetValue() 
      
      try:
         # check if value is of type bool
         if isinstance(signalValue, bool):
            # SET BOOL
            if eventType == 'CENE2SetSignal':
               # output set bool signal event
               self.OutputSetSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            # WAIT FOR BOOL
            elif eventType == 'CENE2WaitForSignal':
               # output wait for bol signal event
               self.OutputWaitForSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            else:
               logger.LogInfo('DOWNLOADER F: Used event type not supported. Check download.')
               self.AddLineToSource('EVENT TYPE NOT SUPPORTED')
            # add empty line as separator
            self.AddEmptyLineToSource()
      except:
         logger.LogError('DOWNLOADER EXCEPTION: Set or wait for signal event.')

   def ResourcePortEvent(self, operator: DULPythonDownloadOperator, event : DULPythonEvent):
      """Set signal bool event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get logging operator
      logger = operator.GetLogOperator()
      # init variables
      eventType = ''
      signalName = ''
      signalAddress = ''
      signalNumber = 0
      # get event type, could be following values:
      eventType = event.GetName()
      # get list opf attributes
      attributes = event.GetAttributes()
      # iterate through attribute list
      for attribute in attributes:
         # get the signal name
         if attribute.GetName() == 'SignalName':
            signalName = attribute.GetValue()
         # address is the automatically generated stirring of the signal address (e.g. DO3)
         elif attribute.GetName() == 'SignalAddress':
            signalAddress = attribute.GetValue()
            try:
               # cut DI or DO and convert the number to an integer
               signalNumber = int(signalAddress[1:])
            except:
               logger.LogError("DOWNLOADER EXCEPTION: couldn't convert signal address to signal number. Check download")
               self.AddLineToSource('ERROR converting signal address to signal number.')
         # get the signal value. Can be bool, int, float, ...
         elif attribute.GetName() == 'SignalValue':
            signalValue = attribute.GetValue() 
      
      try:
         # check if value is of type bool
         if isinstance(signalValue, bool):
            # SET RESOURCE PORT BOOL
            if eventType == 'SetResourcePort':
               # output set bool signal event
               self.OutputSetSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            # WAIT FOR RESOURCE PORT BOOL
            elif eventType == 'WaitForResourcePort':
               # output wait for bol signal event
               self.OutputWaitForSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            else:
               logger.LogInfo('DOWNLOADER F: Used event type not supported. Check download.')
               self.AddLineToSource('EVENT TYPE NOT SUPPORTED')
            # add empty line as separator
            self.AddEmptyLineToSource()
      except:
         logger.LogError('DOWNLOADER EXCEPTION: Set or wait for signal event.')

   def OutputSetSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool):
      """Output set signal command in Fanuc robot program.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         signalName (str): Signal name, used for comment
         signalNumber (int): Signal number
         signalValue (bool): Signal value (True/False)
      """
      # check if signal is true/false
      if signalValue == True:
         self.OutputOtcComment(operator, 'Set %s = ON' % (signalName))
         self.AddLineToSource('SET O%d' % (signalNumber))
      else:
         self.OutputOtcComment(operator, 'Set %s = OFF' % (signalName))
         self.AddLineToSource('RESET O%d' % (signalNumber))

   def OutputWaitForSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool):
      """Output wait for signal command in Fanuc robot program.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         signalName (str): Signal name, used for comment
         signalNumber (int): Signal number
         signalValue (bool): Signal value (True/False)
      """
      # check if wait for signal true/false
      if signalValue == True:
         self.OutputOtcComment(operator, 'Wait for %s = ON' % (signalName))
         self.AddLineToSource('WAITI I%d' % (signalNumber))
      else:
         self.OutputOtcComment(operator, 'Wait for %s = OFF' % (signalName))
         self.AddLineToSource('WAITJ I%d' % (signalNumber))

#################### HELPER ####################

   def CreateHeader(self, operator: DULPythonDownloadOperator):
      """Create program header.
      Separated function, because some information doesn't exist at the beginning

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      self.AddLineToHeader('REM "PROGRAM NAME  : %s.%s' % (self.ProgramUnit, self.ProgramName) + '"')
      date = datetime.today().strftime('%Y-%m-%d')
      time = datetime.today().strftime('%H:%M:%S')
      #CREATE          = DATE 23-12-12 TIME 17:03:19;# prevent Date/Time Differences during Test Run
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      #self.AddLineToHeader('REM "GetWindowsEnvironmentVariable(CPOST_TESTLAUF_CENIT)=%s"' % (ktaTest))
      if ktaTest == "TRUE":
         self.AddLineToHeader('REM "Download Date : 25-01-01 Time : 10:00:00"')
      else:
         self.AddLineToHeader('REM "Download Date : %s Time : %s' % (date[2:], time) + '"')
      self.AddLineToHeader('REM "Version       : 1"')

   def AdjustOrientation(self, orientation):
      '''prevent -0.00 or +/- 180 degree output'''
      tempOrientation = self.LastOrientation
      self.LastOrientation = [
         0.0 if abs(ax) < 0.005 else
         180.0 if ax < -179.999 and tempOrientation[iC] > 179.999 else
         -180.0 if ax > 179.999 and tempOrientation[iC] < -179.999 else ax
        for iC, ax in enumerate(orientation)
      ]
      return self.LastOrientation
         
   def CreateMotionGroupStructure(self, operator: DULPythonDownloadOperator, positionObject: DULPythonPosition):
      """Create the motion group structure depending on axes mapping in layout builder

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         position (DULPythonPosition): Position operator gives access to the position object. The position object is equal to an tool path element.

      Return:
         returns the motion groups for the position object
      """
   
      # read configuration
      configuration = positionObject.GetConfig()
      # compute config
      config = ""
      # read turn value
      turn = positionObject.GetTurn()
      # read coordiantes
      cartesian = positionObject.GetXYZ()
      # read orientation 
      orientation = self.AdjustOrientation(positionObject.GetOrientation())
      # read motion target type
      motionTargetType = positionObject.GetTargetType()
      targetOutput = "(" + f'{cartesian[0]*1000:.3f}' + ", " + f'{cartesian[1]*1000:.3f}' + ", " + f'{cartesian[2]*1000:.3f}' + ", " + f'{orientation[2]:.2f}' + ", " + f'{orientation[1]:.2f}' + ", " + f'{orientation[0]:.2f}' + ")"

      # get all joints
      joints = positionObject.GetAllJointValues()

      #self.SevenAxisRobot = False
      #self.Ax7Robot7thAxName = "D1"
      #self.Ax7RobotAxisOrder = ["D1","D2",....]
      # if it's a 7-AxisRobot take second MechGroup into account
      jCounts = self.GetRobotsAllMainJoints(joints)
      if jCounts == 7:
         self.SevenAxisRobot = True

      self.DevLogging("______Position : " + str(positionObject.GetName()))
      self.DevLogging(".............TargetType : "+ str(motionTargetType))
      self.DevLogging(".............Nr. Joints : "+ str(len(joints)))
      motionGroups = []
      for joint in joints:
         # get motion group index
         tmpString = ''
         groupIndex = joint[JOINT_DATA_TYPE].GetJointGroupIndex()
         tmpString += ' GrpIdx:' + str(groupIndex)
         # Is Mechanism # part of current joint part of selected controller UNIT?
         if str(groupIndex) in self.MechsInUnit:
            if self.SevenAxisRobot == True:
               # if it's a 7Axis and the Role is SynchronousOnRobot add this to the Robot MotionGroup
               jointRole = joint[JOINT_DATA_TYPE].GetJointRole()
               if jointRole == JointConstellationRole.SynchronousOnRobot:
                  self.SynchronousOnRobot = groupIndex
                  groupIndex = self.GroupRobot
            motionGroup = self.GetMotionGroupByIndex(motionGroups, groupIndex)
            # check if motion group exist
            if motionGroup is None:
               # create a new motion group
               motionGroup = self.MotionGroup(motionTargetType, groupIndex, configuration, config, turn, 0, 0, cartesian, orientation, targetOutput, self.DownloadJointsOnly)
               motionGroups.append(motionGroup)
               self.DevLogging(".............*[newMotionGroup]*")
               if self.SevenAxisRobot == True:
                  # pass 7Ax Stuff to MotionGroup
                  motionGroup.SetSevenAxisJoints(joints, self.Ax7Robot7thAxName, self.Ax7RobotAxisOrder)
            # get the joint index
            jointIndex = joint[JOINT_DATA_TYPE].GetJointIndex()
            tmpString += ' | JIdx:' + str(jointIndex)
            # get the kinematic type, linear or rotation
            jointKinematicType = joint[JOINT_DATA_TYPE].GetJointType()
            tmpString += ' | JKinTyp:' + str(jointKinematicType)
            # check if driven joint (robot) or external joint (synchronous)
            isExternalJoint = joint[JOINT_DATA_TYPE].IsExternal()
            tmpString += ' | JIsExt:' + str(isExternalJoint)
            # to which type of resouce belongs the joint
            jointRole = joint[JOINT_DATA_TYPE].GetJointRole()
            tmpString += ' | JRole:' + str(jointRole)
            # set group flags
            if jointRole == JointConstellationRole.Main:
               self.GroupRobot = groupIndex
               if not groupIndex in self.GroupRobotMainList:
                  self.GroupRobotMainList.append(groupIndex)
            elif jointRole == JointConstellationRole.EndEffector:
               self.GroupEndEffector = groupIndex
               if not groupIndex in self.GroupEndEffectorList:
                  self.GroupEndEffectorList.append(groupIndex)
            elif jointRole == JointConstellationRole.Rail:
               self.GroupRail = groupIndex
               if not groupIndex in self.GroupRailList:
                  self.GroupRailList.append(groupIndex)
            elif jointRole == JointConstellationRole.WorkpiecePositioner:
               self.GroupWpPosition = groupIndex
               if not groupIndex in self.GroupWpPositionList:
                  self.GroupWpPositionList.append(groupIndex)
            elif jointRole == JointConstellationRole.SynchronousOnRobot:
               self.SynchronousOnRobot = self.SynchronousOnRobot
               if not groupIndex in self.GroupRobotMainList:
                  self.GroupRobotMainList.append(groupIndex)

            if isExternalJoint:
               motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, SYNCHRONOUS_JOINT, jointRole, joint[JOINT_VALUE])
            else:
               motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, DRIVEN_JOINT, jointRole, joint[JOINT_VALUE])

            motionGroup.GetTargetOutput(motionTargetType, cartesian, orientation, targetOutput, jointRole, self.SevenAxisRobot)
            motionGroup.ComputeCartesianConfig(motionTargetType, configuration, joints, jointRole)
         else:
            tmpString += ' *********** NONE ***********'
         self.DevLogging(".............Joint : "  + str(joint[JOINT_DATA_TYPE].GetName()) + " = " + str(joint[JOINT_VALUE]) + tmpString)
      return motionGroups

   def GetRobotsAllMainJoints(self, joints):
      '''Check for Main and SynchronOnRobot for 7-Axis
      Args:
         joints : all Layout Joints
      Return
         the Number of the Robots Main Joints (Main & SynchronousOnRobot)
         '''
      iCount = 0
      mainInMechList = 0
      syncOnRobotList = ''
      tmp = self.MechsInUnit
      for joint in joints:
         groupIndex = joint[JOINT_DATA_TYPE].GetJointGroupIndex()
         jointRole = joint[JOINT_DATA_TYPE].GetJointRole()
         # if jointRole == JointConstellationRole.Main or jointRole == JointConstellationRole.SynchronousOnRobot:
         #    iCount += 1
         #    if not str(groupIndex) in self.MechsInUnit:
         #       # maybe the MechsInUnit needs to be extended for Main&SyncOnRob to be sure that it will be taken in JointsLoop
         #       #self.MechsInUnit += ',' + str(groupIndex)
         #       iDummy = 1
               
         if jointRole == JointConstellationRole.Main:
            iCount += 1
            if str(groupIndex) in self.MechsInUnit:
               mainInMechList = 1 # Flag, if Main is listed in MechsInUnit
               
         if jointRole == JointConstellationRole.SynchronousOnRobot:
            iCount += 1
            if not str(groupIndex) in self.MechsInUnit:
               # maybe the MechsInUnit needs to be extended for Main&SyncOnRob to be sure that it will be taken in JointsLoop
               syncOnRobotList += ',' + str(groupIndex)
      
      if mainInMechList == 1 and len(syncOnRobotList):
         self.MechsInUnit += syncOnRobotList  # add SyncOnRobot Mechanism to MechList

      self.DevLogging(".................. found joints : " + str(iCount) + "......self.MechsInUnit b/a :<" + tmp + "|" + self.MechsInUnit + ">")
      return iCount

   def GetMotionGroupByIndex(self, motionGroups, index: int):
      """Get the motion group by index
      
      Args:
         motionGroups: list with motion groups
         index: Index of the searched motion group

      Return:
         if motion group exist, return the motion group
         if motion group doesn't exist, return None
         """
      # iterate through motion groups
      for motionGroup in motionGroups:
         if motionGroup.MotionGroupIndex == index:
            return motionGroup
      return None

   def RemoveLastCharInDataStringArray(self, stringArray):

      """Removes the last character in the last string array position.
      e.g. remove the comma at the end

      Args:
         stringArray: array with strings containing the data section of a position

      Return:
         returns the modified string
      """
      # get the length of the string array
      dataArrayLength = len(stringArray) - 1
      # get the entry
      lastString = stringArray[dataArrayLength]
      # remove comma
      lastString = lastString[:-1]
      # write changed string
      stringArray[dataArrayLength] = lastString
      # return the modified string
      return stringArray

   def CheckAndUpdateBaseFrame(self, logger, index: int):
      """Checks if base frame index is within range and generate a output line

      Args:
         logger (_type_): log operator to give user feedback
         index (int): index of the base frame
      """      
      if self.CurrentBaseFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.BaseFrameMinIndex, self.BaseFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentBaseFrameIndex = index
         else:
            logger.LogError('Base frame index out of range')

   def CheckAndUpdateToolFrame(self, logger, index: int):
      """Checks if tool frame index is within range and generate a output line

      Args:
         logger (_type_): log operator to give user feedback
         index (int): index of the tool frame
      """      
      if self.CurrentToolFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.ToolFrameMinIndex, self.ToolFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentToolFrameIndex = index
         else:
            logger.LogError('Tool frame index out of range')

   def RangeCheck(self, value, min, max):
      """Check if the value is in range

      Return:
         Returns True if the value is in range
         Returns False is the value is not in range
      """
      try:
         # if frame index is smaller then minimum frame index value, return ERROR
         if value < min:
            return False
         # if frame index is higher then maximum frame index value, return ERROR
         elif max < value:
            return False
         # frame index is within range
         else:
            return True
      except: 
         pass

   def AddLineToHeader(self, newline):
      """Add a line to the program header
      """
      self.Header.append(newline)

   def AddLineToSourceHeader(self, newline: str):
      """Add a new line to the source header section
      """
      self.SourceHeader.append(newline)

   def AddLineToSource(self, newline: str):
      """Add a new line to the source section
      """
      self.Source.append(newline)

   def AddLineToFooter(self, newline: str):
      """Add a new line to the footer section
      """
      self.Footer.append(newline)

   def AddEmptyLineToSource(self):
      """Adds an empty line to the source section"""
      self.Source.append('')

   def GetOutputDirectory(self, operator: DULPythonDownloadOperator):
      """Return the output directory without file name
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program

      Return:
         returns the output directory path defined in FASTSUITE"""
      # get controller
      controller = operator.GetController()
      # get output directory
      outputDir = controller.GetOutputDirectory()
      # return output directory
      return outputDir

   def GetActiveProgramName(self, operator: DULPythonDownloadOperator):
      """Return the name of the active program
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program

      Return:
         returns the name of the active program"""
      # get controller
      controller = operator.GetController()
      # get active program
      program = controller.GetActiveProgram()
      # return active program name
      return program.GetName()

   def checkOtcProgramName(self, programName):
      """Check the OTC programm name: 3 or 4 char lon, digits only
      
      Args:
         progranName: String

      Return:
         returns True for correct name"""
      
      # 3 or 4 characters long?
      if len(programName) < 3 or len(programName) > 4:
         return False
      
      # All digits?
      for char in programName:
         if not char.isdigit():
               return False
      
      return True

#################### HELPER CLASS (MOTION GROUP & JOINT) ####################

   @dataclass
   class MotionGroup():
      """Class that emulates the Daihen Data section and thus simplifies output/customizing.
      A motion group contains one or more joints.
      """
      def __init__(self, motionTargetType, motionGroupIndex, configuration="", config="", turn="", toolIndex=0, baseIndex=0, cartesian = [0.0, 0.0, 0.0], orientation = [0.0, 0.0, 0.0], targetOutput="", downloadOnlyJoints = False):
         """Class initialization
         """
         # if configuration and turn are empty,
         # motion group doesn't contain a robot and
         # configuration and turn must not be outputted.
         self.MotionGroupIndex = int(motionGroupIndex)
         # motion target type
         self.MotionTargetType = motionTargetType
         # point configuration C4/C6
         self.Configuration = str(configuration)
         # computed point configuration CONFIG=0100
         self.Config = str(config)
         # turn
         self.Turn = str(turn)
         # tool frame index
         self.ToolIndex = int(toolIndex)
         # base frame index
         self.BaseIndex =int(baseIndex)
         # coordinates
         self.X = Converter.ConvertDefaultToUnit(cartesian[0], Length.Millimeter()) # X
         self.Y = Converter.ConvertDefaultToUnit(cartesian[1], Length.Millimeter()) # Y
         self.Z = Converter.ConvertDefaultToUnit(cartesian[2], Length.Millimeter()) # Z
         # orientation
         self.W = orientation[0] # W (Rx)
         self.P = orientation[1] # P (Ry)
         self.R = orientation[2] # R (Rz)
         # string of cartesian or joint values
         self.TargetOutput = str(targetOutput)
         # output all Positions in Joints by Users Request
         self.DownloadOnlyJoints = downloadOnlyJoints
         # string of joint values of second RobotGroup
         self.TargetOutputSecond = ""
         # list with joints
         self.Joints = []
         self.JointDict = {}
         self.Ax7Robot7thAxName = "D1"  # handle this Joint seperately in Output M1J/M2J
         self.Ax7RobotAxisOrder = ["D1","D2","D3","D4","D5","D6","D7"]

      def AddJointToMotionGroup(self, index, kinematicType, resourceJointType, jointRole, value):
         """Add a joint to the motion group

         Args:
            index: joint index from port mapping in layout builder
            kinematicType: linear or rotation
            resourceJointType: driven or synchronous joint
            jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
            value: joint value

         Return:
            return the new created joint object
         """
         joint = self.Joint(index, kinematicType, resourceJointType, jointRole, value)
         self.Joints.append(joint)
         self.Joints = sorted(self.Joints, key=lambda joint: joint.Index)
         return joint
      
      def SetSevenAxisJoints(self, allJoints, seventhAxisName, seventhAxisOrder):
         '''Sets the Axis Names for a SevenAxis Robot, the Axis Order and a Dictonary of all Joint Names/Values'''
         self.Ax7Robot7thAxName = seventhAxisName
         self.Ax7RobotAxisOrder = seventhAxisOrder
         for jnt in allJoints:
            self.JointDict[jnt[JOINT_DATA_TYPE].GetName()] = jnt[JOINT_VALUE]

      def GetAllJoints(self):
         """get all joints of the motion group

         Return:
            Returns a list of all joint of the motion group
         """
         return self.Joints
      
      def GetAllSynchronousJoints(self):
         """Get all synchronous joints from motion group

         Return:
            Returns a list of all synchronous joints of the motion group
         """
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == SYNCHRONOUS_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def GetAllDrivenJoints(self):
         """Get all synchronous joints from motion group

         Return:
            Returns a list of all synchronous joints of the motion group
         """
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == DRIVEN_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def HasDrivenJoints(self):
         """Check if a robot/machine is part of the motion group

         Return:
            returns True if the motion group has driven joints
            returns False if the motion groups has no driven joints
         """
         # get all driven joints
         drivenJoints = self.GetAllDrivenJoints()
         # check the length of the list
         if len(drivenJoints) > 0:
            # motion group has driven joints (robot)
            return True
         else:
            # motion group has NO driven joints (robot)
            return False
      
      def ComputeCartesianConfig(self, motionTargetType, configuration, joints, jointRole):
         # Compute robot's config flags
         config = ""
         correctRole = False
         if jointRole == JointConstellationRole.Main or jointRole == JointConstellationRole.SynchronousOnRobot:
            correctRole = True   # set the Config String for jointRole Main & SynchronousOnRobot
         if self.DownloadOnlyJoints == True:
            correctRole = False   # forced Joint Output, no config
         if correctRole == True and motionTargetType == TargetType.Cartesian:
            joint1 = joints[0][1]
            joint5 = joints[4][1]
            jointAX = joints[5][1]
            if joint5 > 0:
               flag5 = "1"
            else:
               flag5 = "0"
            if configuration == "C6":
               flag3 = "1"
            else:
               flag3 = "0"
            if joint1 > -45 and joint1 < 45:
               flag1 = "2"
            elif joint1 < -45:
               flag1 = "1"
            elif joint1 > 45:
               flag1 = "0"
            
            if jointAX >= -180.0 and jointAX <= 180.0:
               flagAX = "0"
            elif jointAX > 180.0:
               flagAX = "1"
            elif jointAX < -180.0:
               flagAX = "2"
            else:
               flagAX = "0"
            
            config = ",CONF=" + flag5 + flag3 + flag1 + flagAX
         self.Config = config
         
      def GetTargetOutput(self, motionTargetType, cartesian, orientation, targetOutput, jointRole, sevenAxis = False):
         """Write target output for joint-target-type motion group - robot and external mechanisms
         """
         if self.DownloadOnlyJoints == True:
            motionTargetType = TargetType.Joint   # force Joint Output

         if sevenAxis == True and (jointRole == JointConstellationRole.Main or jointRole == JointConstellationRole.SynchronousOnRobot):
            # write the Joints-String at 7-Axis for jointRole Main & SynchronousOnRobot
            # taken into account which Axis are MainMachUnit and SynchronousOnRobotMechUnit
            targetOutputTmp = "("
            targetOutputTmp2nd = "("
            for chk in self.Ax7RobotAxisOrder:
               if chk != self.Ax7Robot7thAxName:
                  targetOutputTmp += str(round(self.JointDict[chk], 2)) + ", "
               else:
                  targetOutputTmp2nd += str(round(self.JointDict[chk], 2)) + ", "
            
            targetOutputTmp = targetOutputTmp[:-2]
            targetOutputTmp2nd = targetOutputTmp2nd[:-2]
            targetOutputTmp += ")"
            targetOutputTmp2nd += ")"
            if motionTargetType == TargetType.Joint:
               self.TargetOutput = targetOutputTmp
            self.TargetOutputSecond = targetOutputTmp2nd
            
         else:
            if (jointRole == JointConstellationRole.Main and motionTargetType == TargetType.Joint) or jointRole != JointConstellationRole.Main:
               targetOutputTmp = ""
               for joint in self.Joints:
                  if joint.Value < 0.0 and joint.Value > -0.01:
                     joint.Value = 0.0
                  if targetOutputTmp == "":
                     targetOutputTmp = "(" + str(round(joint.Value, 2))
                  else:
                     targetOutputTmp = targetOutputTmp + ", " + ("%.2f" % joint.Value)
               self.TargetOutput = targetOutputTmp + ")"

      @dataclass
      class Joint():
         """Joint class to store important joint information in a separated object
         """
         def __init__(self, index, kinematicType, resourceJointType, jointRole, value):
            """Class initialization

            Args:
               index: joint index from port mapping in layout builder
               kinematicType: linear or rotation
               resourceJointType: driven or synchronous joint
               jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
               value: joint value
            """
            self.Index = index
            # movement type is linear or rotation
            self.KinematicType = kinematicType
            # resource joint type can be driven or synchronous
            self.ResourceJointType = resourceJointType
            # to which type of resource does the joint belong (robot, workpiece positioner, rail, ...)
            self.JointRole = jointRole
            # check if joint is of type rotation
            if kinematicType == JointKinematicType.Revolute:
               self.Value = value
            else:
               # if linear joint, multiply by 1000 to get mm
               self.Value = Converter.ConvertDefaultToUnit(value, Length.Millimeter())
