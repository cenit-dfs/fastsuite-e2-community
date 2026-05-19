"""
COPYRIGHT Cenit AG Q2/2024
   Production ready FANUC arc welding downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off            YES
      touch sensing in base frame direction:       NO
      touch sensing in surface direction:          YES
      touch sensing with wire:                     YES
      wire check for touch with wire:              NO
      touch sensing with nozzle:                   NO
      seam search in surface direction:            NO (should work equal to touch sensing, but not evaluated)
      seam finding:                                NO
      seam tracking:                               YES
      arc sensing TRACK TAST                       YES
      robot team/synchronized multi robot motions: NO

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
"""
import math, importlib

from centypes import *
from cenpylib import FileUtility
from cenpyolpcore import *
from cenpydownload import *
import ctypes

import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

def ensure_module_is_updated(module_name):
      if module_name in sys.modules:
         importlib.reload(sys.modules[module_name])
      else:
         importlib.import_module(module_name)

# import base class and define class name of the current download
ensure_module_is_updated('Fanuc') #  <---- Perform module force-reload in order to apply hot changes

# import base class and define class name of the current download
#################### CONSTANTS ####################
# name of the download class
DOWNLOAD_CLASS_NAME = "Fanuc_Arc_Welding"
from Fanuc import Fanuc

class Fanuc_Arc_Welding(Fanuc):
   """Fanuc arc welding downloader
   Base robot vendor downloader
   Derived from: Base downloader
   """
   # attribute name of the work method to get the workmethod name
   WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"
   # stitching work method name
   WM_NAME_STICH = "StitchWeldingWorkMethod"
   # touch sensing operation name
   WM_NAME_TOUCH = "TouchSensingWorkMethod"
   # seam search operation name
   WM_NAME_SEAM = "SeamSearchWorkMethod"
   # seam search operation name
   WM_NAME_SEAM_FIND = "SeamFindingWorkMethod"
   # continues welding operation name
   WM_NAME_CONTINUES = "ContourPointWorkMethod"

   # connection type between touch sensing and welding operation (operation-start/end-shortest distance)
   AW_TOUCHSENSE_CONNECT_TYPE = "TSConnectionType"
   # touch sensing cycle type, touch in base frame direction or touch normal to surface
   AW_TOUCHSENS_CYCLE_TYPE = "TSCycleType"
   AW_TOUCHSENS_CYCLE_LITERALS = ["Base frame direction", "Normal to surface"]

   # identifiers are events added to the touch sensing points in the within the touch sensing cycle.
   TS_POINT_IDENTIFIER_START_APP = "TouchPointStartAppEvent"
   TS_POINT_IDENTIFIER_COLLISION = "TouchPointCollisionEvent"
   TS_POINT_IDENTIFIER_END = "TouchPointEndEvent"
   TS_POINT_IDENTIFIER_START_RET = "TouchPointStartRetEvent"

   AW_CONNECT_TOUCH_PROCESS_TYPE = "ConnectTouchProcessType"
   # touch operation attribute
   AW_SEAM_CALIBRATION_METHOD = 'SeamCalibrationMethod'
   AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
   AW_WELDING_GROUP_TOUCH_ID = "TouchId"
   AW_TOUCHSENS_SENSING_SPEED = "SensingSpeed"
   # touch sensing digital output
   AW_TOUCHSENS_DIGITAL_INPUT = "TSDigitalInput"
   # touch sensing sensor output
   AW_TOUCHSENS_DIGITAL_OUTPUT = "TSDigitalOutput"
   # "ConnectTouchProcessPointEvent" event attribute
   AW_EVT_TOUCH_ID = "TouchId"
   AW_EVT_TOUCH_COUNTER = "Touch_Cntr"
   AW_EVT_TOUCH_ID_VIACIR = "TouchID_ViaCir"
   # Arc Weld
   AW_WELD_SPEED_TYPE = "WeldSpeedType"
   AW_WELD_SPEED_TYPE_LITERALS = ["Value", "WELD_SPEED"]
   # Weaving
   # AW_WEAVING_DEFINE = "UseWeaveDefine"
   # AW_WEAVING_PATTERN = "WeavePattern"
   # AW_WEAVING_USE_SCHEDULE = "WeaveUseSchedule"
   # AW_WEAVING_SCHEDULE = "WeaveSchedule"
   # Thru Arc Seam Tracking (ArcSensor)
   AW_ARCSENSE = "ArcSense"
   AW_ARCSENSE_SCHEDULE = "ArcSenseSchedule"
   AW_ARCSENSE_CARRY_ON = "ArcSenseCarryOn"
   AW_ARCSENSE_CARRY_ON_SCHEDULE = "ArcSenseCarryOnSchedule"
   # Laser Tracking
   AW_LASER_TRACKER_ONOFF = "SeamTrackingOnOff"
   AW_LASER_TRACKER_ID = "LaserTrackerId"
   AW_LASER_TRACKER_SCHEDULE = "LaserTrackerSchedule"
   AW_LASER_TRACKER_POS_REGISTER = "LaserTrackerPosRegister"
   AW_LASER_TRACKER_DELAY = "LaserTrackerDelay"

#################### BASE FUNCTIONS ####################

   def __init__(self):
      super().__init__()
      # arc welding specific attribute names
      self.SeamCalibrationMethod = ""
      # save which calibration methods is used
      self.UseFanucTouchBaseFrame = False
      self.UseTouchSensingSurface = False
      # touch counter is used to store the maximum number of combined touch sensing operations
      self.TouchCounter = 0
      # define the position register number to store the start point coordinates of touch sensing
      self.TouchPointStartAppPositionRegister = 1
      # define the position register number to store the collision point coordinates
      self.TouchCollisionPointPositionRegister = 2
      # store the currently used touch sensing register
      self.TouchIdPositionRegister = 20
      # to detect a new touch sensing cycle and reset the touch offset
      self.LastTouchSensingSequenceID = 0
      # used for operation naming
      self.TouchSensingSequencingCounter = 0
      # Touch sensing offset
      # 1 = Reset offset in touch sensing macro
      # 0 = sum up offset by touch sensing sequence
      self.ResetTouchSensingOffset = 1
      # Flag to track state of "Touch Offset"
      self.TouchOffsetActive = False
      # name of the touch sensing macro
      self.TouchSensingMacroName = 'E2_TOUCH'
      # string array with touch sensing macro
      self.TouchSensingMacro = []
      # data type of the touch sensing input signal.
      # Can be overridden in customizing. No E2 attribute
      self.TouchSensingInputSignalType = 'DI'
      # data type of the touch sensing output signal.
      # Can be overridden in customizing. No E2 attribute
      self.TouchSensingOutputSignalType = 'DO'
      # touch sensing input signal number. Must be defined in Setup touch sensing "Touch input"
      self.TouchSensingInput = 0
      # touch sensing output signal number. Must be defined in Setup touch sensing "Touch output"
      self.TouchSensingOutput = 0
      # save touch sensing speed to output it in the touch sensing macro
      self.TouchSensingSpeed = 10 # mm/sec
      # save the output path
      self.OutputFilePathTouchSensing = ''
      # welding program number
      self.WeldingProgramNumber = 1
      # save if weaving was turned on while arc on
      self.WeavingOn = False
      # Weld Sequence
      self.WeldSequence = 0
      # Weld Speed Type
      self.WeldSpeedType = ''
      # use Arc Sense
      self.ArcSense = False
      # Arc Sense schedule
      self.ArcSenseSchedule = 0
      # use Arc Sense Carry On
      self.ArcSenseCarryOn = False
      # Arc Sense Carry On schedule
      self.ArcSenseCarryOnSchedule = 0
      # Arc Sense Carry On active flag to force linear motion instead of P2P
      self.ArcSenseCarryOnIsActive = False
      # Laser Tracker On/Off
      self.LaserTrackerOnOff = False
      # Laser Tracker ID Sense
      self.LaserTrackerId = 0
      # Laser Tracker schedule
      self.LaserTrackerSchedule = 0
      # Laser Tracker Position Register Carry On
      self.LaserTrackerPosRegister = 0
      # Laser Tracken On Delay
      self.LaserTrackerDelay = 0
      # Next linear move is to the searched position reguster PR[]
      self.SeamTrackingPosition = False
      # Flag to distinguish between SeamFinding for start or endpoint
      self.SeamFindingEndLocation = False
      # Set seam finding flag for stitch welding WM
      self.SeamFindingIsActive = False
      # Seam Finding Position Register PR[]
      self.SeamFindingPR = 0
      # save current workmethod name of the operation
      self.WorkmethodName = ''

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Program start

      Args:
         operator: download operator
         program: access to the program object
      """
      # get logging operator
      logger = operator.GetLogOperator()

      # add arc welding specific technology implementation to source header
      self.SourceHeader.insert(0, 'ARC Welding Equipment : 1,*,*,*,*;')
      self.SourceHeader.insert(0, '/APPL')

      self.SeamCalibrationMethod = program.GetLiteral(self.AW_SEAM_CALIBRATION_METHOD, False)

      # get the calibration method and store which methods are used
      touchSensingCycleTypeIndex = program.GetLiteral(self.AW_TOUCHSENS_CYCLE_TYPE, False)
      # check if attribute exist
      if touchSensingCycleTypeIndex == None:
         self.UseTouchSensingSurface = False
         self.UseFanucTouchBaseFrame = False
         logger.LogError('Could not found touch sensing cycle type selection. E2 will be used as default.')

      # touch direction normal to surfaced
      elif touchSensingCycleTypeIndex == 'Normal to surface':
         self.UseTouchSensingSurface = True
         self.UseFanucTouchBaseFrame = False
         # get touch signal input
         self.TouchSensingInput = program.GetInteger(self.AW_TOUCHSENS_DIGITAL_INPUT, True)
         # get touch signal output
         self.TouchSensingOutput = program.GetInteger(self.AW_TOUCHSENS_DIGITAL_OUTPUT, True)
         # store global attribute for touch sensing speed to add this to the macro
         tempSpeed = program.GetDouble(self.AW_TOUCHSENS_SENSING_SPEED, True) * 1000
         if not math.isnan(tempSpeed):
            self.TouchSensingSpeed = int(tempSpeed)

         hint1 = '!!! PLEASE CHECK !!!'
         hint2 = 'TOUCH SPEED in E2_TOUCH.tp'
         self.OutputFanucComment(operator, hint1)
         self.OutputFanucComment(operator, hint2)

      # touch direction in base frame direction
      elif touchSensingCycleTypeIndex == 'Base frame direction':
         self.UseTouchSensingSurface = False
         self.UseFanucTouchBaseFrame = True
         logger.LogInfo('Selected touch sensing method is not supported')

      # Seam Finding or Tracking
      else:
         self.UseTouchSensingSurface = False
         self.UseFanucTouchBaseFrame = False

      # Laser Tracker On/Off
      self.LaserTrackerOnOff=program.GetBool('SeamTrackingOnOff', True)
      # use Laser Tracker ID
      self.LaserTrackerId=program.GetInteger('LaserTrackerId', True)
      # Laser Tracker schedule
      self.LaserTrackerSchedule=program.GetInteger('LaserTrackerSchedule', True)
      # Laser Tracker 1st Position Register
      self.LaserTrackerPosRegister=program.GetInteger('LaserTrackerPosRegister', True)
      # Laser Tracker start delaz
      self.LaserTrackerDelay=program.GetDouble('LaserTrackerDelay', True)
      # Reset Seam Finding PR
      self.SeamFindingPR = self.LaserTrackerPosRegister - 1

      # call method from parent class
      super().ProgramStart(operator, program)

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Operation start

      Args:
         operator: download operator
         operation: access to the operation
      """
      # call method from derived class
      super().OperationStart(operator, operation)
      # get workmethod name
      self.WorkmethodName = operation.GetString(self.WORKMETHOD_NAME, False)

      # welding operation
      if self.WorkmethodName == self.WM_NAME_CONTINUES:
         self.OutputFanucComment(operator, '#OP:%s' % (operation.GetName()))

      # stich welding operation
      elif self.WorkmethodName == self.WM_NAME_STICH:
         self.OutputFanucComment(operator, '#OP:%s' % (operation.GetName()))
         # # Weaving pattern
         # self.WeavePattern = operation.GetInteger('WeavePattern', True)
         # # Weaving use schedule
         # self.WeaveUseSchedule = operation.GetBool('WeaveUseSchedule', True)
         # # Weaving schedule #
         # self.WeaveSchedule = operation.GetInteger('WeaveSchedule', True)
         # use Arc Sense
         self.ArcSense=operation.GetBool('ArcSense', True)
         # Arc Sense schedule
         self.ArcSenseSchedule=operation.GetInteger('ArcSenseSchedule', True)
         # use Arc Sense Carry On
         self.ArcSenseCarryOn=operation.GetBool('ArcSenseCarryOn', True)
         # Arc Sense Carry On schedule
         self.ArcSenseCarryOnSchedule=operation.GetInteger('ArcSenseCarryOnSchedule', True)
         # Weld Speed Type
         self.WeldSpeedType=operation.GetLiteral('WeldSpeedType', True)

      # seam search operation
      elif self.WorkmethodName == self.WM_NAME_SEAM:
         self.OutputFanucComment(operator, '#OP:%s' % (operation.GetName()))

      # touch sensing operation
      elif self.WorkmethodName == self.WM_NAME_TOUCH:
         self.OutputFanucComment(operator, '#OP:%s' % (operation.GetName()))
         if self.UseTouchSensingSurface:
            self.TouchIdPositionRegister = operation.GetInteger(self.AW_WELDING_GROUP_TOUCH_ID, False)
            # check for a new touch sensing sequence
            if self.TouchIdPositionRegister != self.LastTouchSensingSequenceID:
               self.ResetTouchSensingOffset = True
               self.TouchSensingSequencingCounter = 0
            else:
               self.ResetTouchSensingOffset = False
            # override last touch sequence ID with current ID
            self.LastTouchSensingSequenceID = self.TouchIdPositionRegister

            # increment touch sensing sequencing counter
            self.TouchSensingSequencingCounter += 1
            # add some comment for touch start
            self.OutputFanucComment(operator, '#TS:%d-%d' % (self.LastTouchSensingSequenceID, self.TouchSensingSequencingCounter))

            # reset offset before new touch sense sequence starts. Otherwise first point is wrong.
            if self.ResetTouchSensingOffset:
               self.AddLineToSource('  PR[%d]=PR[%d]-PR[%d]' % (self.TouchIdPositionRegister, self.TouchIdPositionRegister, self.TouchIdPositionRegister))
      # touch sensing operation
      elif self.WorkmethodName == self.WM_NAME_SEAM_FIND:
         self.OutputFanucComment(operator, '#OP:%s' % (operation.GetName()))
         self.SeamFindingEndLocation = operation.GetBool('SeamFindingEndLocation', True)
         self.SeamFindingPR = self.LaserTrackerPosRegister

   def HandleEvent(self, operator: DULPythonDownloadOperator, currentMotion: DULPythonMotion, event: DULPythonEvent):
      """Handle event

      Args:
         operator: download operator
         event: access to the event object
      """
      # check if TOUCH SENSING event
      if event.GetName() == 'TouchSensingEvent':
         # output E2 touch sensing
         if self.UseTouchSensingSurface:
            self.OutputTouchSensingE2(operator, event)
         elif self.UseFanucTouchBaseFrame:
            pass
         else:
            pass
         # return to avoid potential double handling
         return

      #
      elif event.GetName() == 'ConnectTouchProcessPointEvent':
         # output E2 touch sensing
         if self.UseTouchSensingSurface:
            self.OutputConnectTouchProcessPointEvent(operator, currentMotion, event)
         elif self.UseFanucTouchBaseFrame:
            # currently not supported. Please use the available downloader defined in custom definition
            pass
         else:
            pass
         # return to avoid potential double handling
         return

      # check if ARC ON event
      elif event.GetName() == 'ArcOnEvent':
         # remove the ; in the row before adding a new line
         temp = self.RemoveLastCharInStringArray(self.Source)
         self.OutputArcOnEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # check if ARC OFF event
      elif event.GetName() == 'ArcOffEvent':
         temp = self.RemoveLastCharInStringArray(self.Source)
         self.OutputArcOffEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # check if Seam tracking On event
      elif (event.GetName() == 'SeamTrackingEvent') or event.GetName() == 'SeamFindingScanEvent':
         # remove the ; in the row before adding a new line
         temp = self.RemoveLastCharInStringArray(self.Source)
         self.OutputSeamTrackingOnEvent(operator, currentMotion, event)
         if event.GetName() == 'SeamFindingScanEvent':
            self.SeamFindingIsActive = True
         # return to avoid postential double handling
         return

      # check if Seam tracking Off event
      elif event.GetName() == 'SeamTrackingOffEvent':
         # remove the ; in the row before adding a new line
         temp = self.RemoveLastCharInStringArray(self.Source)
         self.OutputSeamTrackingOffEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # call method from derived class
      super().HandleEvent(operator, currentMotion, event)

   def OperationEnd(self, operator: DULPythonDownloadOperator, operation):
      """Operation end

      Args:
         operator: download operator
         operation: access to the operation
      """
      # welding operation
      if self.WorkmethodName == self.WM_NAME_CONTINUES:
         # add empty line after operation to increase readability
         self.AddEmptyLineToSource()
      # stich welding operation
      elif self.WorkmethodName == self.WM_NAME_STICH:
         # add empty line after operation to increase readability
         if self.TouchOffsetActive:
            # disable touch offset at the end of the program
            self.AddLineToSource('  Touch Offset End')
            self.TouchOffsetActive = False
         self.AddEmptyLineToSource()
      # seam search operation
      elif self.WorkmethodName == self.WM_NAME_SEAM:
         # add empty line after operation to increase readability
         self.AddEmptyLineToSource()
      # touch sensing operation
      elif self.WorkmethodName == self.WM_NAME_TOUCH:
         if self.UseTouchSensingSurface:
            # add empty line after operation to increase readability
            self.AddEmptyLineToSource()
      # call method from derived class
      super().OperationEnd(operator, operation)

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      """Called at the end of each the program

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      if self.ArcSenseCarryOn:
         self.AddLineToSource('  Track End')
      # call method from derived class
      super().ProgramEnd(operator, program)

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Create output file

      Args:
         operator: download operator
      """
      if self.UseTouchSensingSurface:
         # get output directory
         outputDir = self.GetOutputDirectory(operator)
         # define output path
         self.OutputFilePathTouchSensing = outputDir + "\\" + self.TouchSensingMacroName + self.FILE_EXTENSION
         # create touch sensing macro
         self.CreateTouchSensingMacro(operator)
      # call method from derived class
      super().CreateOutputFile(operator)

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
         """Write output file

         Args:
            operator: download operator
         """
         if self.UseTouchSensingSurface:
            # write touch sensing macro file
            self.FileUtil.AppendTextArrayToFile(self.OutputFilePathTouchSensing, self.TouchSensingMacro)
         # call method from derived class
         super().WriteOutputFile(operator)

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
            if self.SeamFindingIsActive and self.WorkmethodName == self.WM_NAME_STICH:
               sourcePosition = self.OutputSourceSeamTrackingPosition(operator, motion)
               self.SeamFindingPR += 1
            elif self.SeamTrackingPosition and self.WorkmethodName == self.WM_NAME_STICH:
               sourcePosition = self.OutputSourceSeamTrackingPosition(operator, motion)
               self.SeamTrackingPosition = False
            else:
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
            # only linear motion allowed when Track TAST carry on is active
            if self.ArcSenseCarryOnIsActive:
               # create LIN source string
               sourcePosition = self.OutputSourceLin(operator, motion)
            else:
               # create PTP source string
               sourcePosition = self.OutputSourcePtp(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition, self.NEW_LINE_NUMBER_PREFIX)

   def OutputSourceSeamTrackingPosition(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output linear motion to previously tracked position
      L PR[20] 30mm/sec FINE;

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

      #L P[1] 100mm/sec FINE ACC80;
      return('L PR[%d:Tracked Position] %dmm/sec %s%s' % (self.SeamFindingPR, self.CurrentLinFeedrate, accuracy, acceleration))

#################### EVENTS ####################

   def OutputTouchSensingE2(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Create touch sensing motion

      Target Output:
      6:   !### TOUCH #1;
      7:   SKIP CONDITION DI[10:TOUCH IO]=ON;
      8: J P[1] 50% FINE Offset,PR[20]; <- Start point
      9:   PR[1]=P[1]; <- Start point
      10:  PR[2]=P[2]; <- Collision Point
      11:  CALL E2_SEARCH3(1,2,20,0);
      12:L P[3] 30mm/sec FINE Offset,PR[20]; <- Touch end point
      13:  SKIP CONDITION DI[10:TOUCH IO]=OFF;

      Args:
         operator: download operator
         event: touch sensing event
      """
      # get logger
      logger = operator.GetLogOperator()
      # get motions of the event
      motions = event.GetMotions()
      # check if motions exists
      if motions == None:
         logger.LogError("Touch sensing event doesn't contain points.")

      # enable skip condition for touch sensing (tactile search)
      self.AddLineToSource('  SKIP CONDITION %s[%d]=ON' % (self.TouchSensingInputSignalType, self.TouchSensingInput))

      # handle each MOTION of the touch sensing event
      for motion in motions:
         # check for build-in events like speed, accuracy, ...
         eventsBefore = motion.GetEventsBefore()
         for eventBefore in eventsBefore:
            # handle speed accuracy, ...
            self.HandleBuildInEvents(operator, eventBefore)
         # handel TOUCH sensing start APPROACH point
         for eventBefore in eventsBefore:
            if eventBefore.GetName() == 'TouchPointStartAppEvent':
               self.HandleSourceSection(operator, motion)
               self.HandleDataSection(operator, motion)
               # add Offset to source line
               self.AddOffsetToSourceDefinition(operator, self.TouchIdPositionRegister)
               # write approach start point coordinates to position register
               self.AddLineToSource('  PR[%d]=P[%d]' % (self.TouchPointStartAppPositionRegister, self.PointCounter))
            # handel COLLISION point
            if eventBefore.GetName() == 'TouchPointCollisionEvent':
               # collision point needs only output in data section
               self.HandleDataSection(operator, motion, True)
               # write collision point coordinates to position register
               self.AddLineToSource('  PR[%d]=P[%d]' % (self.TouchCollisionPointPositionRegister, self.PointCounter))
               # call touch sensing macro
               self.AddLineToSource('  CALL %s(%d,%d,%d,%d)' % (self.TouchSensingMacroName, self.TouchPointStartAppPositionRegister, self.TouchCollisionPointPositionRegister, self.TouchIdPositionRegister, self.ResetTouchSensingOffset))
            # handel TOUCH sensing start RETRACT point
            if eventBefore.GetName() == 'TouchPointStartRetEvent':
               self.HandleSourceSection(operator, motion)
               self.HandleDataSection(operator, motion)
               # add Offset to source line
               self.AddOffsetToSourceDefinition(operator, self.TouchIdPositionRegister)

         # check for build-in events like speed, accuracy, ...
         eventsAfter = motion.GetEventsAfter()
         for eventAfter in eventsAfter:
            self.HandleBuildInEvents(operator, eventAfter)

      # disable skip condition for touch sensing (tactile search)
      self.AddLineToSource('  SKIP CONDITION %s[%d]=OFF' % (self.TouchSensingInputSignalType, self.TouchSensingInput))

   def OutputConnectTouchProcessPointEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """
      """
      logger = operator.GetLogOperator()

      # init attributes
      touchId = 0
      touchIdVia = False
      touchCounter = 0
      # get all attributes from event
      attributes = event.GetAttributes()
      # iterate through attribute list
      for attribute in attributes:
         # touch ID
         if attribute.GetName() == self.AW_EVT_TOUCH_ID:
            touchId = attribute.GetValue()
         # is the touch ID for the next via point
         if attribute.GetName() == self.AW_EVT_TOUCH_ID_VIACIR:
            touchIdVia = attribute.GetValue()
         # how much touch operations does belong together
         if attribute.GetName() == self.AW_EVT_TOUCH_COUNTER:
            touchCounter = attribute.GetValue()
      # plausibility check
      if (touchId == 0):
         logger.LogError('Touch ID is 0 in "ConnectTouchProcessPointEvent". Check download')
         self.AddLineToSource('ERROR touch ID is 0')
         return
      # set new touch sensing offset
      self.OutputEnableTouchOffsetForWelding(operator, int(touchId))

   def OutputArcOnEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Fanuc arc on command

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # get log operator
      logger = operator.GetLogOperator()
      # variable definition
      weaveFrequency = 0.0
      weaveWidth = 0.0
      weaveTime1 = 0.0
      weaveTime2 = 0.0
      # get all attributes
      attributes = event.GetAttributes()
      for attribute in attributes:
         # get welding ID
         if attribute.GetName() == 'ProgNumber':
            self.WeldingProgramNumber = attribute.GetValue()
         # get weaving on/off
         elif attribute.GetName() == 'WeaveOnOff':
            self.WeavingOn = attribute.GetValue()
         # get weave frequency
         elif attribute.GetName() == 'WeaveFrequenz':
            weaveFrequency=attribute.GetValue()
         # get weave width
         elif attribute.GetName() == 'WeaveWidth':
            weaveWidth=attribute.GetValue() * 1000
         # get weave time 1
         elif attribute.GetName() == 'WeaveTime1':
            weaveTime1=attribute.GetValue()
         # get weave time 2
         elif attribute.GetName() == 'WeaveTime2':
            weaveTime2=attribute.GetValue()
         # get weave pattern
         elif attribute.GetName() == 'WeavePattern':
            weavePattern=str(attribute.GetValue())
         # get weave use schedule
         elif attribute.GetName() == 'WeaveUseSchedule':
            weaveUseSchedule=attribute.GetValue()
         # get weave schedule
         elif attribute.GetName() == 'WeaveSchedule':
            weaveSchedule=attribute.GetValue()
         elif attribute.GetName() == 'WeldSequence':
            self.WeldSequence=attribute.GetValue()

      if (self.WeldingProgramNumber < 1) or (self.WeldingProgramNumber > 99):
         logger.LogError('Welding program number needs to be within the range of 1-99. Check download for further information')
         self.AddLineToSource('WELD START ERROR - NUMBER BETWEEN 1-99 EXPECTED')

      # add arc on instruction
      if self.WeldSequence == 0:
         self.AddLineToSource(' Weld Start[%d]' % (self.WeldingProgramNumber), self.NO_NEW_LINE_NUMBER_PREFIX)
      else:
         self.AddLineToSource(' Weld Start[%d,%d]' % (self.WeldingProgramNumber, self.WeldSequence), self.NO_NEW_LINE_NUMBER_PREFIX)

      # check if weaving is enabled
      if self.WeavingOn:
         # add weaving on instruction
         if weaveUseSchedule:
            self.AddLineToSource('  Weave %s[%d]' % (weavePattern,weaveSchedule), self.NEW_LINE_NUMBER_PREFIX)
         else:
            self.AddLineToSource('  Weave Sine[%.1fHz,%.1fmm,%.1fs,%.1fs]' % (weaveFrequency, weaveWidth, weaveTime1, weaveTime2), self.NEW_LINE_NUMBER_PREFIX)
         # use Arc Sense
         self.ArcSenseCarryOnIsActive = False
         if self.ArcSense:
            # add TRACK TAST instruction
            self.AddLineToSource('  Track TAST [%d]' % (self.ArcSenseSchedule), self.NEW_LINE_NUMBER_PREFIX)
      if self.LaserTrackerOnOff:
         self.AddLineToSource(' Track SENSOR[%d]' % (self.LaserTrackerSchedule), self.NO_NEW_LINE_NUMBER_PREFIX)

      # set speed output during welding
      if self.WeldSpeedType != 'Value':
         self.Tech.SpeedType = self.WeldSpeedType
         self.Tech.SpeedOutput = self.WeldSpeedType

   def OutputArcOffEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Arc off and track off instructions

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # add arc off instruction
      if self.WeldSequence == 0:
         self.AddLineToSource(' Weld End[%d]' % (self.WeldingProgramNumber), self.NO_NEW_LINE_NUMBER_PREFIX)
      else:
         self.AddLineToSource(' Weld End[%d,%d]' % (self.WeldingProgramNumber, self.WeldSequence), self.NO_NEW_LINE_NUMBER_PREFIX)
      # check if weaving is enabled
      if self.WeavingOn:
         # add weaving end instruction
         self.AddLineToSource('  Weave End', self.NEW_LINE_NUMBER_PREFIX)
         if self.ArcSense:
            # add TRACK TAST instruction
            if self.ArcSenseCarryOn:
               self.AddLineToSource('  Track TAST [%d]' % (self.ArcSenseCarryOnSchedule), self.NEW_LINE_NUMBER_PREFIX)
               self.ArcSenseCarryOnIsActive = True
            else:
               self.AddLineToSource('  Track End', self.NEW_LINE_NUMBER_PREFIX)
      #
      if not self.ArcSense:
         self.AddLineToSource('  Track End', self.NEW_LINE_NUMBER_PREFIX)
      # Turn seamfinding output PR[] off
      self.SeamFindingIsActive = False
      self.SeamTrackingPosition = False
      # reset speed output to 'value'
      self.Tech.SpeedType = 'Value'

   def OutputSeamTrackingOnEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Fanuc laser tracker on command

      Target Output:
         6:  SENSOR ON[1] ;
         7:  SENSOR SEARCH START PR[1] ;
         8:  SENSOR SEARCH POINT[5]    ;
         9:  SENSOR SEARCH END ;
        10:  SENSOR OFF ;

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # get log operator
      logger = operator.GetLogOperator()
      # variable definition

      if self.SeamFindingIsActive and self.SeamFindingEndLocation:
         self.SeamFindingPR = self.LaserTrackerPosRegister + 1
      elif self.SeamFindingIsActive and not(self.SeamFindingEndLocation):
         self.SeamFindingPR = self.LaserTrackerPosRegister
      else:
         self.SeamFindingPR += 1

      # add laser tracker on instructions
      self.AddLineToSource(' SENSOR ON[%d]' % (self.LaserTrackerId), self.NO_NEW_LINE_NUMBER_PREFIX)
      self.AddLineToSource(' SENSOR SEARCH START[%d]' % (self.SeamFindingPR), self.NO_NEW_LINE_NUMBER_PREFIX)
      self.AddLineToSource(' SENSOR SEARCH POINT[%d]' % (self.LaserTrackerSchedule), self.NO_NEW_LINE_NUMBER_PREFIX)
      self.AddLineToSource(' SENSOR SEARCH END', self.NO_NEW_LINE_NUMBER_PREFIX)
      self.AddLineToSource(' SENSOR OFF', self.NO_NEW_LINE_NUMBER_PREFIX)
      # add empty line after operation to increase readability
      self.AddEmptyLineToSource()
      # Next linear move is to the searched position reguster PR[]
      self.SeamTrackingPosition = True

   def OutputSeamTrackingOffEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Fanuc laser tracker on command

      Target Output:
        10:  Track End ;

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # add laser tracker off instruction
      self.AddLineToSource('  Track End', self.NEW_LINE_NUMBER_PREFIX)
      self.AddLineToSource('  !TEST =============================', self.NEW_LINE_NUMBER_PREFIX)
      self.SeamTrackingPosition = False

#################### HELPER ####################

   def AddOffsetToSourceDefinition(self, operator: DULPythonDownloadOperator, positionRegisterNumber: int):
      """Add touch offset to a point definition in source section
      J P[7] 50% FINE Offset,PR[20];
                     --------------

      Args:
         operator: Download operator gives access to the complete program, controller and resources
         positionRegisterNumber: number of position register with calculated touch offset
      """
      # remove ; from last line
      self.RemoveLastCharInStringArray(self.Source)
      # create offset string
      offsetString = ' Offset,PR[%d]' % (positionRegisterNumber)
      # add string at the end of the current source line
      self.AddTextToLastLineOfArray(self.Source, offsetString)

   def OutputEnableTouchOffsetForWelding(self, operator: DULPythonDownloadOperator, positionRegisterNumber: int):
      """Enables new touch offset for welding
      Touch Offset PR[20];

      Args:
         operator: Download operator gives access to the complete program, controller and resources
         positionRegisterNumber: number of position register with calculated touch offset
      """
      # add string at the end of the current source line
      self.AddLineToSource('  Touch Offset PR[%d]' % (int(positionRegisterNumber)))
      self.TouchOffsetActive = True

   def CreateTouchSensingMacro(self, operator: DULPythonDownloadOperator):
      """Create a separated file with touch sensing macro

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      self.AddLineToTouchSensingMarco('/PROG  %s' % (self.TouchSensingMacroName))
      self.AddLineToTouchSensingMarco('/ATTR')
      self.AddLineToTouchSensingMarco('OWNER           = MNEDITOR;')
      self.AddLineToTouchSensingMarco('COMMENT         = "OLP BY CENIT";')
      self.AddLineToTouchSensingMarco('PROG_SIZE       = 921;')
      # get the Fanuc specific date
      date = self.GetFanucDate()
      # get the Fanuc specific time
      time = self.GetFanucTime()
      
      # prevent Date/Time Differences during Test Run
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      #self.AddLineToHeader('REM "GetWindowsEnvironmentVariable(CPOST_TESTLAUF_CENIT)=%s"' % (ktaTest))
      if ktaTest == "TRUE":
         date = "KTA"
         time = "TEST"
         
      #CREATE          = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToTouchSensingMarco('CREATE          = DATE %s TIME %s;' % (date, time))
      #MODIFIED        = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToTouchSensingMarco('MODIFIED        = DATE %s TIME %s;' % (date, time))
      self.AddLineToTouchSensingMarco('FILE_NAME	= ;')
      self.AddLineToTouchSensingMarco('VERSION		= 0;')
      self.AddLineToTouchSensingMarco('LINE_COUNT	= 32;')
      self.AddLineToTouchSensingMarco('MEMORY_SIZE     = 1309;')
      self.AddLineToTouchSensingMarco('PROTECT         = READ_WRITE;')
      self.AddLineToTouchSensingMarco('TCD: STACK_SIZE      = 0,')
      self.AddLineToTouchSensingMarco('     TASK_PRIORITY   = 50,')
      self.AddLineToTouchSensingMarco('     TIME_SLICE      = 0,')
      self.AddLineToTouchSensingMarco('     BUSY_LAMP_OFF   = 0,')
      self.AddLineToTouchSensingMarco('     ABORT_REQUEST   = 0,')
      self.AddLineToTouchSensingMarco('     PAUSE_REQUEST   = 0;')
      self.AddLineToTouchSensingMarco('DEFAULT_GROUP   = 1,*,*,*,*;')
      self.AddLineToTouchSensingMarco('CONTROL_CODE    = 00000000 00000000;')
      self.AddLineToTouchSensingMarco('LOCAL_REGISTERS	= 0,0,0;')
      self.AddLineToTouchSensingMarco('/APPL')
      self.AddLineToTouchSensingMarco('  ARC Welding Equipment : 1,*,*,*,*;')
      self.AddLineToTouchSensingMarco('/MN')
      # self.AddLineToTouchSensingMarco('   1:  !THIS PROGRAM WAS GENERATED ON;')
      # self.AddLineToTouchSensingMarco('   1:  !THE BASIS OF PARAMETERS.;')
      # self.AddLineToTouchSensingMarco('   1:  !PLEASE CHECK BEFORE IMPORTING!;')
      self.AddLineToTouchSensingMarco('   1:  !AR1=Touch start;')
      self.AddLineToTouchSensingMarco('   2:  !AR2=Col. point;')
      self.AddLineToTouchSensingMarco('   3:  !AR3=Offset register;')
      self.AddLineToTouchSensingMarco('   4:  !AR4=Reset offset;')
      self.AddLineToTouchSensingMarco('   5:  ;')
      self.AddLineToTouchSensingMarco('   6:  !Touch dig. output;')
      self.AddLineToTouchSensingMarco('   7:  %s[%d]=ON ;' % (self.TouchSensingOutputSignalType, self.TouchSensingOutput))
      self.AddLineToTouchSensingMarco('   7:  ;')
      self.AddLineToTouchSensingMarco('   8:  !Reset offset;')
      self.AddLineToTouchSensingMarco('   9:  IF (AR[4]=1) THEN;')
      self.AddLineToTouchSensingMarco('  10:  PR[AR[3]]=PR[AR[3]]-PR[AR[3]];')
      self.AddLineToTouchSensingMarco('  11:  ENDIF;')
      self.AddLineToTouchSensingMarco('  12:  ;')
      self.AddLineToTouchSensingMarco('  13:  !Calc. end pos.;')
      self.AddLineToTouchSensingMarco('  14:  PR[GP1:AR[1],1]=(PR[GP1:AR[2],1]+PR[GP1:AR[2],1]-PR[GP1:AR[1],1]);')
      self.AddLineToTouchSensingMarco('  15:  PR[GP1:AR[1],2]=(PR[GP1:AR[2],2]+PR[GP1:AR[2],2]-PR[GP1:AR[1],2]);')
      self.AddLineToTouchSensingMarco('  16:  PR[GP1:AR[1],3]=(PR[GP1:AR[2],3]+PR[GP1:AR[2],3]-PR[GP1:AR[1],3]);')
      self.AddLineToTouchSensingMarco('  17:  ;')
      self.AddLineToTouchSensingMarco('  18:  !Touch to surface;')
      self.AddLineToTouchSensingMarco('  19:  L PR[AR[1]] %dmm/sec FINE Skip,LBL[5],PR[100]=LPOS Offset,PR[AR[3]];' % (self.TouchSensingSpeed))
      self.AddLineToTouchSensingMarco('  20:  ;')
      self.AddLineToTouchSensingMarco('  21:  !Add offset;')
      self.AddLineToTouchSensingMarco('  22:  PR[GP1:AR[3],1]=(PR[GP1:100,1]-PR[GP1:AR[2],1]);')
      self.AddLineToTouchSensingMarco('  23:  PR[GP1:AR[3],2]=(PR[GP1:100,2]-PR[GP1:AR[2],2]);')
      self.AddLineToTouchSensingMarco('  24:  PR[GP1:AR[3],3]=(PR[GP1:100,3]-PR[GP1:AR[2],3]);')
      self.AddLineToTouchSensingMarco('  25:  ;')
      self.AddLineToTouchSensingMarco('  26:  JMP LBL[6] ;')
      self.AddLineToTouchSensingMarco('  27:  LBL[5] ;')
      self.AddLineToTouchSensingMarco('  28:  UALM[1] ;')
      self.AddLineToTouchSensingMarco('  29:  LBL[6] ;')
      self.AddLineToTouchSensingMarco('  30:  ;')
      self.AddLineToTouchSensingMarco('  31:  !Touch dig. output;')
      self.AddLineToTouchSensingMarco('  32:  %s[%d]=OFF ;' % (self.TouchSensingOutputSignalType, self.TouchSensingOutput))
      self.AddLineToTouchSensingMarco('  33:  ;')
      self.AddLineToTouchSensingMarco('/POS')
      self.AddLineToTouchSensingMarco('/END')

   def AddLineToTouchSensingMarco(self, newline: str):
      """Add a new line to the touch sensing macro

      Args:
         newline (str): string of the line
      """
      # add new line to the array
      self.TouchSensingMacro.append(newline)