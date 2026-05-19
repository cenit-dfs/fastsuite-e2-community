"""
COPYRIGHT Cenit AG Q1/2024
   FANUC downloader

   This downloader* SUPPORTs:
      Motion commands J/L/C                        YES
      tool & base frame mapping                    YES
      motion events                                YES
      controller ports (bool only)                 YES
      resource ports:                              NO

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
"""
import sys, inspect, os
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
sys.dont_write_bytecode = True

from datetime import datetime
from centypes import *
from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *
from dataclasses import dataclass


#################### CONSTANTS ####################
@dataclass
class Tech():
   # Global Technology placeholder and flag attribs
   SpeedType: str = 'Value'
   SpeedOutput: str = ''

# name of the download class
DOWNLOAD_CLASS_NAME = "Fanuc"

class Fanuc(Downloader):
   """Fanuc downloader
   Base robot vendor downloader
   Derived from: Base downloader
   """

   # kinematic 
   DRIVEN_JOINT = 0
   SYNCHRONOUS_JOINT = 1
   # joint object array
   JOINT_DATA_TYPE = 0
   JOINT_VALUE = 1

   NEW_LINE_NUMBER_PREFIX = True
   NO_NEW_LINE_NUMBER_PREFIX = False

   FILE_EXTENSION = '.ls'

   FANUC_TRUE = 'ON'
   FANUC_FALSE = 'OFF'

#################### BASE FUNCTIONS ####################

   def __init__(self) -> None:
      """Class initialization
      """
      super().__init__()

      # Initialize the Tech class and assign it to an instance variable
      self.Tech = Tech()
      #
      self.FileUtil = FileUtility()
      # output file path
      self.OutputFilePath = ''

      # store the program name
      self.ProgramName = ''

      # array to store header content
      self.Header = []
      # array to store application command
      # e.g. arc welding equipment
      self.SourceHeader = []
      # array to store motion commands
      self.Source = []
      self.Source.append('/MN')
      # array to store motion commands
      self.DataHeader = []
      self.DataHeader.append('/POS')
      # array to store point coordinates and joints
      self.Data = []
      # program footer text
      self.Footer = []

      # store the currently used base frame index
      # min = 0; max = 9
      self.CurrentBaseFrameIndex = -1
      self.BaseFrameMinIndex = 0
      self.BaseFrameMaxIndex = 30
      # store the currently used tool frame index
      # min = 0; max = 10
      self.CurrentToolFrameIndex = -1
      self.ToolFrameMinIndex = 0
      self.ToolFrameMaxIndex = 30
      
      # store the currently used speed; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpFeedrate = 50
      # store the currently used speed; expected unit = [mm/sec]
      self.CurrentLinFeedrate = 100
      # store the currently used accuracy; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpAccuracy = 0
      # store the currently used accuracy; expected unit = [%]
      # min = 0; max = 100
      self.CurrentLinAccuracy = 0
      self.CurrentAccuracyActive = False
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 150
      self.CurrentPtpAcceleration = 100
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 150
      self.CurrentLinAcceleration = 100
      # maximum character for comments
      self.MaxCharComments = 32

      # point counter to connect source point and data point
      self.PointCounter = int(0)
      # line counter for motion instruction (source section)
      self.SourceLineCounter = 0

      # string for program header to define used motion groups
      self.UsedGroups = ""

      # used language in user interface
      self.Language = ""
   
   def Initialize(self, operator : DULPythonDownloadOperator):
      """Translator initialization.
      Called only once per download, even when downloading sub programs

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # get log operator
      self.Language = operator.GetCurrentLanguage()
      pass

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
      """
      # get program name
      self.ProgramName = program.GetName()

      # get logging operator
      logger = operator.GetLogOperator()
      # write used motion groups string for header output
      motionGroupOne = '*,'
      motionGroupTwo = '*,'
      motionGroupThree = '*,'
      motionGroupFour = '*,'
      motionGroupFive = '*;'
      # get controller
      controller = operator.GetController()
      # get active program
      program = controller.GetActiveProgram()
      # get operation groups
      operationGroups = program.GetOperationGroups()
      for operationGroup in operationGroups:
         # get operations
         operations = operationGroup.GetOperations()
         for operation in operations:
            # get motions
            motions = operation.GetMotions()
            for motion in motions:
               # get position
               positionObject = motion.GetPosition()
               # get joints
               joints = positionObject.GetAllJointValues()
               for joint in joints:
                  # get motion group index
                  motionGroupIndex = joint[self.JOINT_DATA_TYPE].GetJointGroupIndex()
                  # add motion group index to the list
                  if motionGroupIndex == 1:
                     motionGroupOne = '1,'
                  elif motionGroupIndex == 2:
                     motionGroupTwo = '1,'
                  elif motionGroupIndex == 3:
                     motionGroupThree = '1,'
                  elif motionGroupIndex == 4:
                     motionGroupFour = '1,'
                  elif motionGroupIndex == 5:
                     motionGroupFive = '1,'
                  else:
                     logger.LogError('Motion group defined in port mapping in layout builder is out of range. Max is 5')
               break
            break
         break
      # create string for header output
      self.UsedGroups = motionGroupOne + motionGroupTwo + motionGroupThree + motionGroupFour + motionGroupFive

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Operation start

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator gives access to the current operation
      """
      logger = operator.GetLogOperator()

      # get base frame index
      baseFrameProfile = operation.GetUsedBaseProfile()
      baseFrameName = baseFrameProfile.GetName()
      baseFrameIndex = baseFrameProfile.GetIndex()
      # check if index is within range and update base frame
      self.CheckAndUpdateBaseFrame(operator, logger, baseFrameIndex, baseFrameName)

      # get tool frame index
      toolFrameProfile = operation.GetUsedToolProfile()
      toolFrameName = toolFrameProfile.GetName()
      toolFrameIndex = toolFrameProfile.GetIndex()

      # check if index is within range and update tool frame
      self.CheckAndUpdateToolFrame(operator, logger, toolFrameIndex, toolFrameName)

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
      # handle data section of the motion
      self.HandleDataSection(operator, motion)

      # handle events, inserted after. Do not handle events which to change toolpath element output
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         self.HandleEvent(operator, motion, event)

   def SubprogramStart(self, operator : DULPythonDownloadOperator, subProgram : DULPythonSubprogram):
      """called when a sub program is called

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         subprogram (DULPythonSubprogram): sub program operator gives access to the complete sub program
      """
      # get sub program name
      subProgramName = subProgram.GetName()
      # add call in program
      self.AddLineToSource('CALL %s' % subProgramName)

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      """Called at the end of each the program 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      self.AddLineToFooter("/END")

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Create output file
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # get output directory
      outputDir = self.GetOutputDirectory(operator)
      # get active program name
      # programName = self.GetActiveProgramName(operator)
      # define output path
      self.OutputFilePath = outputDir + "\\" + self.ProgramName + self.FILE_EXTENSION
      # create Header
      self.CreateHeader(operator)

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Write output file
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # create file and output the program
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Data)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Footer)

      self.Header.clear()
      self.SourceHeader.clear()
      self.Source.clear()
      self.DataHeader.clear()
      self.Data.clear()
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

      # check if the motion is a reference motion or if the motion was already processed
      if not isRef:
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # create LIN source string
            sourcePosition = self.OutputSourceLin(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition, self.NEW_LINE_NUMBER_PREFIX)
         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string
            sourcePosition = self.OutputSourceCirc(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition, self.NEW_LINE_NUMBER_PREFIX)
         # check if the motion is of type point to point
         else:
            # create PTP source string
            sourcePosition = self.OutputSourcePtp(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition, self.NEW_LINE_NUMBER_PREFIX)

   def OutputSourcePtp(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output point to point motion
      J P[1] 50% FINE ACC80;

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += int(1)

      # E2 point name is used as point comment
      # point comment only support up to 16 character
      comment = self.CheckPointCommentLength(motion.GetName())

      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentPtpAccuracy == 0:
         # exact stop
         accuracy = 'FINE'
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'CNT' + str(self.CurrentPtpAccuracy)

      # check if acceleration is programmed
      if self.CurrentPtpAcceleration == 100:
         acceleration = ''
      else:
         acceleration = ' ACC%d' % self.CurrentPtpAcceleration

      #J P[1] 50% FINE ACC80;
      return ('J P[%d%s] %d%% %s%s' % (self.PointCounter, comment, self.CurrentPtpFeedrate, accuracy, acceleration))

   def OutputSourceLin(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output linear motion
      L P[1] 30mm/sec FINE ACC80;

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += 1

      # E2 point name is used as point comment
      # point comment only support up to 16 character
      comment = self.CheckPointCommentLength(motion.GetName())

      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentLinAccuracy == 0:
         # exact stop
         accuracy = 'FINE'
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'CNT' + str(self.CurrentLinAccuracy)

      # check if acceleration is programmed
      if self.CurrentLinAcceleration == 100:
         acceleration = ''
      else:
         acceleration = ' ACC%d' % self.CurrentLinAcceleration

      if self.Tech.SpeedType == 'Value':
         #L P[1] 100mm/sec FINE ACC80;
         return('L P[%d%s] %dmm/sec %s%s' % (self.PointCounter, comment, self.CurrentLinFeedrate, accuracy, acceleration))
      else:
         #L P[1] WELD_SPEED FINE ACC80;
         return('L P[%d%s] %s %s%s' % (self.PointCounter, comment, self.Tech.SpeedOutput, accuracy, acceleration))
   
   def OutputSourceCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output circular motion
      C P[1] P[2] 30mm/sec FINE ACC80;

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # increment point counter
      self.PointCounter += 1
      pointCounterVia = self.PointCounter
      self.PointCounter += 1
      pointCounterProcess = self.PointCounter
      # E2 point name is used as point comment
      # point comment only support up to 16 character
      commentVia = self.CheckPointCommentLength(motion.GetViaPosition().GetName())
      commentProcess = self.CheckPointCommentLength(motion.GetName())
      # check if robot motion is exact stop or accuracy is enabled
      if self.CurrentLinAccuracy == 0:
         # exact stop
         accuracy = 'FINE'
      else:
         # accuracy value programmed (0-100%)
         accuracy = 'CNT' + str(self.CurrentLinAccuracy)

      # check if acceleration is programmed
      if self.CurrentLinAcceleration == 100:
         acceleration = ''
      else:
         acceleration = ' ACC%d' % self.CurrentLinAcceleration

      if self.Tech.SpeedType == 'Value':
         #C P[1] P[2] 100mm/sec FINE ACC80;
         return ('C P[%d%s] P[%d%s] %dmm/sec %s%s' % (pointCounterVia, commentVia, pointCounterProcess, commentProcess, self.CurrentLinFeedrate, accuracy, acceleration))
      else:
         #C P[1] P[2] WELD_SPEED FINE ACC80;
         return ('C P[%d%s] P[%d%s] %s %s%s' % (pointCounterVia, commentVia, pointCounterProcess, commentProcess, self.Tech.SpeedOutput, accuracy, acceleration))


#################### DATA SECTION ####################

   def HandleDataSection(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      """Handles the output of the motion dependent on motion type to the source section

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
      """
      # contains data section of multiple motion groups
      dataPositions = []
      # complete data section of one motion group
      dataPosition = []

      # check if motion pre processing necessary and if the normal/general motion output must be skipped
      isRef = motion.IsReferenceMotion()

      # check if the motion is a reference motion or if the motion was already processed
      if not isRef:
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # create LIN source string
            dataPosition = self.OutputDataLin(operator, motion, dataOutputOnly)
            for line in dataPosition:
               # add string to data array
               self.AddLineToData(line)
         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string
            dataPositions = self.OutputDataCirc(operator, motion, dataOutputOnly)
            for dataPosition in dataPositions:
               for line in dataPosition:
                  # add string to data array
                  self.AddLineToData(line)
         # check if the motion is of type point to point
         else:
            # create PTP source string
            dataPosition = self.OutputDataPtp(operator, motion, dataOutputOnly)
            for line in dataPosition:
                  # add string to data array
                  self.AddLineToData(line)

   def OutputDataPtp(self,operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      """Output point to point position in data section
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
         
      Return:
         returns the string of the data section for the point to point motion"""
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      if dataOutputOnly:
         # increment point counter
         self.PointCounter += int(1)

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType:TargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      # check if motion target type is of type cartesian or joint
      if motionTargetType == TargetType.Cartesian:
         return self.MotionTargetTypeCartesian(operator, motionGroups, motion.GetName(), self.PointCounter)
      else:
         return self.MotionTargetTypeJoint(operator, motionGroups, motion.GetName(), self.PointCounter)

   def OutputDataLin(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      """Output linear position in data section
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
         
      Return:
         returns the string of the data section for the point to point motion"""
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      if dataOutputOnly:
         # increment point counter
         self.PointCounter += int(1)
      
      # get position of motion
      position = motion.GetPosition()
      # get motion target type 
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      # check if motion target type is of type cartesian or joint
      if motionTargetType == TargetType.Cartesian:
         return self.MotionTargetTypeCartesian(operator, motionGroups, motion.GetName(), self.PointCounter)
      else:
         return self.MotionTargetTypeJoint(operator, motionGroups, motion.GetName(), self.PointCounter)

   def OutputDataCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      """Output linear position in data section
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
         
      Return:
         returns the string of the data section for the point to point motion"""
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      if dataOutputOnly:
         # increment point counter for via point and end point
         self.PointCounter += 2

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroupsViaPoint = self.CreateMotionGroupStructure(operator, motion.GetViaPosition())
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      data = []

      if motionTargetType == TargetType.Cartesian:
         # output via point
         data.append(self.MotionTargetTypeCartesian(operator, motionGroupsViaPoint, motion.GetViaPosition().GetName(), self.PointCounter - 1))
         # output position
         data.append(self.MotionTargetTypeCartesian(operator, motionGroups, motion.GetPosition().GetName(), self.PointCounter))
         return data
      else:
         # output via point
         data.append(self.MotionTargetTypeJoint(operator, motionGroupsViaPoint, motion.GetViaPosition().GetName(), self.PointCounter - 1))
         # output position
         data.append(self.MotionTargetTypeJoint(operator, motionGroups, motion.GetPosition().GetName(), self.PointCounter))
         return data

   def MotionTargetTypeCartesian(self, operator: DULPythonDownloadOperator, motionGroups, pointName: str, pointCounter: int):
      """Manages the data section if motion target type is cartesian.
      
      Args:
         operator: download operator
         motionGroup: motion group with all joints
         pointName: point name
         pointCounter: calculated point number
      """
      dataArray = []
      stringArray = []
      # add point definition
      dataArray.append('P[%d]{' % pointCounter)
      # iterate through the motion groups
      for motionGroup in motionGroups:
         if motionGroup.HasDrivenJoints():
            # check if motion group has driven joints, then group output must include cartesian coordinates and orientation
            stringArray = self.OutputMotionGroupCartesianWithDrivenJoints(operator, motionGroup)
            for string in stringArray:
               dataArray.append(string)
         else:
            # else output the group with joint values
            stringArray = self.OutputMotionGroupWithJointsOnly(operator, motionGroup)
            for string in stringArray:
               dataArray.append(string)

      # close point data output
      dataArray.append('};')
      return dataArray

   def MotionTargetTypeJoint(self, operator: DULPythonDownloadOperator, motionGroups, pointName: str, pointCounter: int):
      """Manages the data section if motion target type is joint.
      
      Args:
         operator: download operator
         motionGroup: motion group with all joints
         pointName: point name
         pointCounter: calculated point number
      """
      dataArray = []
      stringArray = []
      # add point definition
      dataArray.append('P[%d]{' % pointCounter)
      # iterate through the motion groups
      for motionGroup in motionGroups:
         # check if motion group has driven joints, then group output must include cartesian coordinates and orientation
         stringArray = self.OutputMotionGroupWithJointsOnly(operator, motionGroup)
         for string in stringArray:
               dataArray.append(string)

      # close point data output
      dataArray.append('};')
      return dataArray

   def OutputMotionGroupCartesianWithDrivenJoints(self, operator: DULPythonDownloadOperator, motionGroup):
      """Output the motion group with cartesian coordinates
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      stringArray = []
      # add group definition
      stringArray.append('   GP%d:' % (int(motionGroup.MotionGroupIndex)))
      #  UF : 0, UT : 0, CONFIG : 'F   U   P, 0,0,0',
      stringArray.append("    UF : %d, UT : %d, CONFIG : '%s, %s'," % (motionGroup.BaseIndex, motionGroup.ToolIndex, motionGroup.Configuration, motionGroup.Turn))

      #  X = 381.837 mm,  Y = -670.968 mm,  Z = 2196.193 mm,
      #  W = 0.000 deg,  P = 45.000 deg,  R = -156.262 deg,
      #  E1 = 2109.941 mm,  E2 = 2055.019 mm,  E3 = 815.400 mm
      stringArray.append('    X = %.3f mm,  Y = %.3f mm,  Z = %.3f mm,' % (motionGroup.X, motionGroup.Y, motionGroup.Z))
      stringArray.append('    W = %.3f deg,  P = %.3f deg,  R = %.3f deg,' % (motionGroup.W, motionGroup.P, motionGroup.R))
      # External axis
      joints = motionGroup.GetAllSynchronousJoints()

      if len(joints):
         # check if external axis is available
         # group every three joint together to a list
         # from joints [1,2,3,4,5,6,7,8] --> [[1,2,3], [4,5,6], [7,8]]
         slicedJointList = [joints[i:i+3] for i in range(0, len(joints), 3)]

         for jointList in slicedJointList:
            jointLine = ""
            # iterate through the sliced joint sections
            for lineCounter, joint in enumerate(jointList):
               # check the kinematic type of the joint
               if joint.KinematicType == JointKinematicType.Prismatic:
                  jointMovementType = 'mm'
               else: 
                  jointMovementType = 'deg'
               # generate joint string
               jointLine += '    %s%d = %.3f %s,' % ('E', lineCounter + 1, joint.Value, jointMovementType)
            stringArray.append(jointLine)

      # remove comma
      stringArray = self.RemoveLastCharInStringArray(stringArray)
      # return generated string
      return stringArray

   def OutputMotionGroupWithJointsOnly(self, operator: DULPythonDownloadOperator, motionGroup):
      """Output the motion group with joint values

      Args:
         operator: download operator
         motionGroup: motion group with all joints
      """
      stringArray = []
      # group definition
      stringArray.append('   GP%d:' % (int(motionGroup.MotionGroupIndex)))

      #  UF : 0, UT : 0,
      stringArray.append('    UF : %d, UT : %d,' % (motionGroup.BaseIndex, motionGroup.ToolIndex))

      # get all joints
      joints = motionGroup.GetAllJoints()

      # group every three joint together to a list
      # from joints [1,2,3,4,5,6,7,8] --> [[1,2,3], [4,5,6], [7,8]]
      slicedJointList = [joints[i:i+3] for i in range(0, len(joints), 3)]

      # iterate through the sliced joint list
      for jointList in slicedJointList:
         jointLine = ""
         # create a line of up to three joints, e.g.
         #  J1 = -0.000 deg,  J2 = 0.000 deg,  J3 = -33.378 deg,
         for lineCounter, joint in enumerate(jointList):
            # if the joint type is of type rotation, use J as prefix and deg as unit
            if joint.KinematicType == JointKinematicType.Prismatic:
               jointMovementType = 'mm'
            # if the joint type is of type linear, use E as prefix and mm as unit
            else:
               jointMovementType = 'deg'
            jointLine += '    %s%d = %.3f %s,' % ('J', joint.Index, joint.Value, jointMovementType)
         
         stringArray.append(jointLine)
      # remove comma
      stringArray = self.RemoveLastCharInStringArray(stringArray)
      return stringArray

   def CreateMotionGroupStructure(self, operator: DULPythonDownloadOperator, position: DULPythonPosition):
      """Create the motion group structure depending on axes mapping in layout builder

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         position (DULPythonPosition): Position operator gives access to the position object. The position object is equal to an tool path element.

      Return:
         returns the motion groups for the position object
      """
      # read configuration
      configuration = position.GetConfig()
      # read turn value
      turn = position.GetTurn()
      # read coordinates
      cartesian = position.GetXYZ()
      # read orientation 
      orientation = position.GetOrientation()
      # read motion target type
      motionTargetType = position.GetTargetType()

      # get all joints
      joints = position.GetAllJointValues()
      motionGroups = []
      for joint in joints:
         # get motion group index
         # joint is an array
         #     0: joint object itself
         #     1: joint value
         groupIndex = joint[self.JOINT_DATA_TYPE].GetJointGroupIndex()
         motionGroup = self.GetMotionGroupByIndex(motionGroups, groupIndex)
         # check if motion group exist
         if motionGroup is None:
            # create a new motion group
            motionGroup = self.MotionGroup(motionTargetType, groupIndex, configuration, turn, self.CurrentBaseFrameIndex, self.CurrentToolFrameIndex, cartesian, orientation)
            motionGroups.append(motionGroup)

         # get the joint index
         jointIndex = joint[self.JOINT_DATA_TYPE].GetJointIndex()
         # get the kinematic type, linear or rotation
         jointKinematicType = joint[self.JOINT_DATA_TYPE].GetJointType()
         # check if driven joint (robot) or external joint (synchronous)
         isExternalJoint = joint[self.JOINT_DATA_TYPE].IsExternal()
         # to which type of resource belongs the joint
         jointRole = joint[self.JOINT_DATA_TYPE].GetJointRole()
         if isExternalJoint:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.SYNCHRONOUS_JOINT, jointRole, joint[self.JOINT_VALUE])
         else:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.DRIVEN_JOINT, jointRole, joint[self.JOINT_VALUE])
      
      # return the motion groups
      return motionGroups

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
         # check for index
         if motionGroup.MotionGroupIndex == index:
            # return if motion group was found
            return motionGroup
      # return None in case of error.
      return None


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
      # # 
      # if event.GetName() == 'SetResourcePort':
      #    self.LogicPortEvent(operator, event)
      # # 
      # if event.GetName() == 'WaitForResourcePort':
      #    self.LogicPortEvent(operator, event)

   def SetSpeed(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set the current speed from speed event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # variable initialization
      pathtype = ''
      speed = 0.0
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get speed value
         if attribute.GetName() == 'Value':
            speed = attribute.GetValue()
         # get path type
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      # check if path type is contour
      if pathtype == 'Contour':
         self.CurrentLinFeedrate = int(speed * 1000)
      # else path type is point to point
      else:
         self.CurrentPtpFeedrate = int(speed)
   
   def SetAccuracy(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set current accuracy from accuracy event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get log operator
      logger = operator.GetLogOperator()
      # variable initialization
      pathtype= ''
      accuracy = -1
      criteria = ''
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get accuracy value
         if attribute.GetName() == 'Value':
            accuracy = attribute.GetValue()
         # get path type
         if attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
         # get criteria On/Off/Distance/JointDistance/
         if attribute.GetName() == 'Criteria':
            criteria = attribute.GetValue()
      # check if criteria is On
      if criteria =='On':
         self.CurrentAccuracyActive = True
         if accuracy > 0.0:
            # distinguish between contour and point to point
            if pathtype == 'Contour':
               self.CurrentLinAccuracy = int(accuracy * 1000)
               if self.CurrentLinAccuracy > 100:
                  logger.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
                  self.CurrentLinAccuracy = 100
            else:
               self.CurrentPtpAccuracy = int(accuracy)
      # check if criteria is OFF
      elif criteria == 'Off':
         self.CurrentAccuracyActive = False
         self.CurrentLinAccuracy = 0
      # check if criteria is distance
      elif criteria == 'Distance':
         self.CurrentLinAccuracy = int(accuracy * 1000)
         if self.CurrentLinAccuracy > 100:
            logger.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
            self.CurrentLinAccuracy = 100
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      # check if criteria is joint distance
      elif criteria == 'JointDistance':
         self.CurrentPtpAccuracy = int(accuracy)
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      
   def SetAcceleration(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set the current acceleration from acceleration event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get log operator
      logger = operator.GetLogOperator()
      # variable initialization
      pathtype = ''
      acceleration = 0.0
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get acceleration value
         if attribute.GetName() == 'Value':
            acceleration = attribute.GetValue()
         # get path type
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinAcceleration = int(acceleration * 100)
         if self.CurrentLinAcceleration > 150:
            logger.LogError('Acceleration value for point to point is out of range (%d). Max value is 150.' % (self.CurrentLinAcceleration))
            self.CurrentLinAcceleration = 150
      else:
         self.CurrentPtpAcceleration = int(acceleration)
         if self.CurrentPtpAcceleration > 150:
            logger.LogError('Acceleration value for linear is out of range (%d). Max value is 150.' % (self.CurrentPtpAcceleration))
            self.CurrentPtpAcceleration = 150

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
         # get flag is text is a comment (True) or command (False)
         elif attribute.GetName() == 'IsComment':
            isComment = attribute.GetValue()
      # check if comment
      if isComment:
         # create string and add it to source string array
         self.OutputFanucComment(operator, text)
      else:
         self.AddLineToSource(text)

   def OutputFanucComment(self, operator: DULPythonDownloadOperator, comment: str):
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
      self.AddLineToSource('  !%s' % (comment), self.NEW_LINE_NUMBER_PREFIX)

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
      self.AddLineToSource('  WAIT %.3f(sec)' % (time), self.NEW_LINE_NUMBER_PREFIX)

   def LogicPortEvent(self, operator: DULPythonDownloadOperator, event):
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
         elif attribute.GetName() == 'SignalName':
            signalName = attribute.GetValue()
         # address is the automatically generated stirring of the signal address (e.g. DO3)
         elif attribute.GetName() == 'SignalAddress':
            signalAddress = attribute.GetValue()
            try:
               # cut DI or DO and convert the number to an integer
               signalNumber = int(signalAddress[2:])
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
         self.OutputFanucComment(operator, '#%s' % (signalName))
         self.AddLineToSource('  DO[%d] = %s' % (signalNumber, self.FANUC_TRUE), self.NEW_LINE_NUMBER_PREFIX)
      else:
         self.OutputFanucComment(operator, '#%s' % (signalName))
         self.AddLineToSource('  DO[%d] = %s' % (signalNumber, self.FANUC_FALSE), self.NEW_LINE_NUMBER_PREFIX)

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
         self.OutputFanucComment(operator, '#%s' % (signalName))
         self.AddLineToSource('  WAIT DI[%d] = %s' % (signalNumber, self.FANUC_TRUE), self.NEW_LINE_NUMBER_PREFIX)
      else:
         self.OutputFanucComment(operator, '#%s' % (signalName))
         self.AddLineToSource('  WAIT DI[%d] = %s' % (signalNumber, self.FANUC_FALSE), self.NEW_LINE_NUMBER_PREFIX)


#################### HELPER ####################

   def CreateHeader(self, operator: DULPythonDownloadOperator):
      """Create program header.
      Separated function, because some information doesn't exist at the beginning

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
      """
      self.AddLineToHeader('/PROG %s' % (self.ProgramName))
      self.AddLineToHeader('/ATTR')
      self.AddLineToHeader('OWNER           = MNEDITOR;')
      self.AddLineToHeader('COMMENT         = "OLP BY CENIT";')
      self.AddLineToHeader('PROG_SIZE       = 0;')
      # TODO test with other languages
      date = self.GetFanucDate()
      time = self.GetFanucTime()
      
      # prevent Date/Time Differences during Test Run
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      #self.AddLineToHeader('REM "GetWindowsEnvironmentVariable(CPOST_TESTLAUF_CENIT)=%s"' % (ktaTest))
      if ktaTest == "TRUE":
         date = "KTA"
         time = "TEST"
         
      #CREATE          = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToHeader('CREATE          = DATE %s TIME %s;' % (date, time))
      #MODIFIED        = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToHeader('MODIFIED        = DATE %s TIME %s;' % (date, time))
      self.AddLineToHeader('FILE_NAME       = %s%s;' % (self.ProgramName, self.FILE_EXTENSION))
      self.AddLineToHeader('VERSION         = 0;')
      self.AddLineToHeader('LINE_COUNT      = %d;' % (self.SourceLineCounter))
      self.AddLineToHeader('MEMORY_SIZE     = 0;')
      self.AddLineToHeader('PROTECT         = READ_WRITE;')
      self.AddLineToHeader('TCD: STACK_SIZE      = 0,')
      self.AddLineToHeader('     TASK_PRIORITY   = 50,')
      self.AddLineToHeader('     TIME_SLICE      = 0,')
      self.AddLineToHeader('     BUSY_LAMP_OFF   = 0,')
      self.AddLineToHeader('     ABORT_REQUEST   = 0,')
      self.AddLineToHeader('     PAUSE_REQUEST   = 0;')
      #DEFAULT_GROUP   = 1,1,1,*,*;'
      self.AddLineToHeader('DEFAULT_GROUP   = %s' % (self.UsedGroups))
      self.AddLineToHeader('CONTROL_CODE    = 00000000 00000000;')

   def CheckAndUpdateBaseFrame(self, operator: DULPythonDownloadOperator, logger, index: int, name: str):
      """Checks if base frame index is within range and generate a output line

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         logger (_type_): log operator to give user feedback
         index (int): index of the base frame
         name (str): name of the base frame
      """      
      if self.CurrentBaseFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.BaseFrameMinIndex, self.BaseFrameMaxIndex)
         comment = 'BF:%s' % name
         self.OutputFanucComment(operator, comment)
         if frameRangeCheck == True:
            self.CurrentBaseFrameIndex = index
            self.AddLineToSource('  UFRAME_NUM = %d' % (self.CurrentBaseFrameIndex), self.NEW_LINE_NUMBER_PREFIX)
         else:
            self.AddLineToSource('UFRAME_NUM = OUT_OF_RANGE', self.NEW_LINE_NUMBER_PREFIX)
            logger.LogError('Base frame index out of range')
         # add empty line after operation to increase readability
         self.AddEmptyLineToSource()

   def CheckAndUpdateToolFrame(self, operator: DULPythonDownloadOperator, logger, index: int, name: str):
      """Checks if tool frame index is within range and generate a output line

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         logger (_type_): log operator to give user feedback
         index (int): index of the tool frame
         name (str): name of the tool frame
      """      
      if self.CurrentToolFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.ToolFrameMinIndex, self.ToolFrameMaxIndex)
         comment = 'TF:%s' % name
         self.OutputFanucComment(operator, comment)
         if frameRangeCheck == True:
            self.CurrentToolFrameIndex = index
            self.AddLineToSource('  UTOOL_NUM = %d' % (self.CurrentToolFrameIndex), self.NEW_LINE_NUMBER_PREFIX)
         else:
            self.AddLineToSource('UTOOL_NUM = OUT_OF_RANGE', self.NEW_LINE_NUMBER_PREFIX)
            logger.LogError('Tool frame index out of range')
         # add empty line after operation to increase readability
         self.AddEmptyLineToSource()

   def CheckPointCommentLength(self, e2PointName: str):
      """Check and cut the point comment to 16 characters
      
      Return:
         Returns the checked/cut string
      """
      comment = ':' + e2PointName[:16]
      return comment

   def RemoveLastCharInStringArray(self, stringArray):
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

   def AddTextToLastLineOfArray(self, stringArray, text: str):
      """Removes the last character in the last string array position.
      e.g. remove the comma at the end

      Args:
         stringArray: array with strings containing the data section of a position
         text: add text at the end of last line in string array

      Return:
         returns the modified string
      """
      # get the length of the string array
      dataArrayLength = len(stringArray) - 1
      # remove comma
      stringArray[dataArrayLength] += text + ';'
      # return the modified string
      return stringArray[dataArrayLength]

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
         return None

   def AddLineToHeader(self, newline: str):
      """Add a line to the program header

      Args:
         newline (str): add string line to the header 
      """      
      self.Header.append(newline)

   def AddLineToSourceHeader(self, newline: str):
      """Add a line to the source header

      Args:
         newline (str): add string line to the source header 
      """      
      self.SourceHeader.append(newline)

   def AddLineToSource(self, newline: str, newLineNumberPrefix = True):
      """Add a new line to the source section and add the line number optional

      Args:
         newline (str): add string line to the source section
         newLineNumberPrefix (bool, optional): a new line starts with a new number of the line. Defaults to True.
      """
      # e.g add a technology command in a new line. No new line number necessary
      if newLineNumberPrefix == False:
         self.Source.append("    : %s;" % (newline))
         return
      # increase line number
      self.SourceLineCounter += 1
      # check for number of digits
      if self.SourceLineCounter <= 9:
         self.Source.append("   %d:%s;" % (self.SourceLineCounter, newline))
      elif self.SourceLineCounter <= 99:
         self.Source.append("  %d:%s;" % (self.SourceLineCounter, newline))
      elif self.SourceLineCounter <= 999:
         self.Source.append(" %d:%s;" % (self.SourceLineCounter, newline))
      else:
         self.Source.append("%d:%s;" % (self.SourceLineCounter, newline))

   def AddEmptyLineToSource(self):
      """Add an empty line as separator to the source section
      "  ;"
      """
      self.AddLineToSource('  ')

   def AddLineToDataHeader(self, newline: str):
      """Add a new line to the data header section

      Args:
         newline (str): string added to the data header section
      """      
      self.DataHeader.append(newline)

   def AddLineToData(self, newline: str):
      """Add a new line to the data section

      Args:
         newline (str): string added to the data section
      """      
      self.Data.append(newline)

   def AddLineToFooter(self, newline: str):
      """Add a new line to the footer section

      Args:
         newline (str): string added to the footer section
      """
      self.Footer.append(newline)

   def GetFanucDate(self):
      """Get the time string for the header specifically for Fanuc

      Return:
         Returns the date for Fanuc header
      """
      date = datetime.today().strftime('%Y-%m-%d')
      # cut the first two number to fit to Fanuc date format
      newDate = date[2:]
      # return current date
      return newDate

   def GetFanucTime(self):
      """Get the time string for the header specifically for Fanuc
      
      Return:
         Returns the time for Fanuc header
      """
      # return current time
      return datetime.today().strftime('%H:%M:%S')

   def GetOutputDirectory(self, operator: DULPythonDownloadOperator):
      """Return the output directory without file name
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program

      Return:
         returns the output directory path defined in FASTSUITE
      """
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


#################### HELPER CLASS (MOTION GROUP & JOINT) ####################

   class MotionGroup():
      """Class that emulates the Fanuc Data section and thus simplifies output/customizing.
      A motion group contains one or more joints.
      """

      # Motion target
      MOTION_TARGET_TYPE_CARTESIAN = 0
      MOTION_TARGET_TYPE_JOINT = 1
      # kinematic type
      JOINT_TYPE_LINEAR = 0
      JOINT_TYPE_ROTATION = 1
      # kinematic 
      DRIVEN_JOINT = 0
      SYNCHRONOUS_JOINT = 1
      # joint object array
      JOINT_DATA_TYPE = 0
      JOINT_VALUE = 1

      def __init__(self, motionTargetType, motionGroupIndex, configuration, turn, baseIndex, toolIndex, cartesian = [0.0, 0.0, 0.0], orientation = [0.0, 0.0, 0.0]):
         """Class initialization
         """
         # if configuration and turn are empty,
         # motion group doesn't contain a robot and
         # configuration and turn must not be outputted.
         self.MotionGroupIndex = int(motionGroupIndex)
         # motion target type
         self.MotionTargetType = motionTargetType
         # point configuration
         self.Configuration = str(configuration)
         # turn
         self.Turn = str(turn)
         # tool frame index
         self.ToolIndex = int(toolIndex)
         # base frame index
         self.BaseIndex =int(baseIndex)
         # coordinates
         self.X = cartesian[0] * 1000 # X
         self.Y = cartesian[1] * 1000 # Y
         self.Z = cartesian[2] * 1000 # Z
         # orientation
         self.W = orientation[0] # W (Rx)
         self.P = orientation[1] # P (Ry)
         self.R = orientation[2] # R (Rz)
         # list with joints
         self.Joints = []

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
         return joint
      
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
         # iterate through joint list to find all synchronous joints
         for joint in self.Joints:
            if joint.ResourceJointType == self.SYNCHRONOUS_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def GetAllDrivenJoints(self):
         """Get all synchronous joints from motion group

         Return:
            Returns a list of all synchronous joints of the motion group
         """
         synchronousJoints = []
         # iterate through joint list to find all driven joints
         for joint in self.Joints:
            if joint.ResourceJointType == self.DRIVEN_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def HasDrivenJoints(self):
         """Check if a robot/machine is part of the motion group

         Return:
            - True if the motion group has driven joints
            - False if the motion groups has no driven joints
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
      
      class Joint():
         """Joint class to store important joint information in a separated object
         """
         # kinematic type
         JOINT_TYPE_LINEAR = 0
         JOINT_TYPE_ROTATION = 1

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
            if kinematicType.value == self.JOINT_TYPE_ROTATION:
               self.Value = value
            else:
               # if linear joint, multiply by 1000 to get mm
               self.Value = value * 1000