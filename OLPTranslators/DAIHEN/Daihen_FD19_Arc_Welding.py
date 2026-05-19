"""
COPYRIGHT Cenit AG 2025
   Production ready OTC-DAIHEN Arc Welding Downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off:           YES
      touch sensing in surface direction:          YES (SF1)
      touch sensing with wire:                     YES (SF1)
      wire check for touch with wire:              NO
      touch sensing with nozzle:                   NO
      seam search in surface direction:            NO
      seam finding:                                NO
      seam tracking:                               YES (ZT/ZE ZF/ZN ZJ)
      arc sensing:                                 YES (ST/ET)
      robot team/synchronized multi robot motions: NO

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
"""

from cenpydownload import *
from cenpyolpcore import *
from centypes import *

import importlib
import sys, inspect, os, json
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from dataclasses import dataclass, field
from typing import Dict
from collections import namedtuple
# Daihen_FD19_Arc_Defaults contains various data classes incl. their default values
# The default values can be adjusted to the customers needs. 
# Some of those attributes are then changed by technology attributes
from Daihen_FD19_Arc_Classes import *

import math
PI = math.pi
DEGTORAD = PI/180.0

def ensure_module_is_updated(module_name):
      if module_name in sys.modules:
         importlib.reload(sys.modules[module_name])
      else:
         importlib.import_module(module_name)

# import base class and define class name of the current download
ensure_module_is_updated('Daihen_FD19') #  <---- Perform module force-reload in order to apply hot changes


@dataclass
class ZJCycleParams():
   zjSensor: int = 1 
   zjMechanism: int = 1
   zjDEV: int = 1
   zjGAP: int = 1
   zjGFF: int = 1  
   zjStoreCoordinates: int = 0   # ["World", "Tool", "Machine"]
   zjDevComposition: bool = False
   zjAutoManualModify: bool = False
   zjBasePointMemory: bool = False
   zjSearchWaitDelay: float = 0.3
   zjSearchStableDelay: float = 0.5 
   zjStoreNumber: int = 0  
   zjBasePositionX: float = 0.0
   zjBasePositionY: float = 0.0
   zjBasePositionZ: float = 0.049
   zjDeviationLength: float = 0.050 
   zjGapWatchRangeMax: float = 0.02
   zjGapWatchRangeMin: float = -0.02   
   zjMinDepthValue: float = 0.005
   zjAngleOneRangeMax: float = 180.0
   zjAngleOneRangeMin: float = 0.0   
   zjAngleTwoRangeMax: float = 90.0
   zjAngleTwoRangeMin: float = 0.0
   zjPulseString: str = '0.0,0.0,0.0'
   zjBaseOffset: str = '0.0,0.0,0.0'
   zjPulseValue: str = '0.0'

@dataclass
class SF3CycleParams():
   sf3MechanismNr: int = 1     # P01
   sf3VersionNr: int = 2       # P02
   sf3CallNr: int = 1          # P03
   sf3Section: int = 0         # P04   ["Start", "End", "All End"]
   sf3PostureCalling: bool = False   # P05
   sf3DEVFileOffsetX: float = 0.0   # P06
   sf3DEVFileOffsetY: float = 0.0   # P07
   sf3DEVFileOffsetZ: float = 0.0   # P08
   sf3NumericalShiftDistanceX: float = 0.0   # P09
   sf3NumericalShiftDistanceY: float = 0.0   # P10
   sf3NumericalShiftDistanceZ: float = 0.0   # P11
   sf3ShiftMethod: int = 0      # P12   ["DEV.file"]
   sf3BaseCoordSystem: int = 0  # P13 ["Machine", "Tool", "World", "Work", "User"]
   sf3BCSUser: int = 1          # P14
   sf3Comment: str = "Offset"   # PComment
   sf3MainDEVNr: str = "0"         # P--
   sf3AuxiliaryDEVNr1: str = "0"   # P--
   sf3AuxiliaryDEVNr2: str = "1"   # P--
   sf3AuxiliaryDEVNr3: str = "1"   # P--

@dataclass
class SF4CycleParams():
   sf4MechanismNr: int = 1      # P--
   sf4VersionNr: int = 1        # P01
   sf4DevFileOne: int = 1       # P02
   sf4RateOne: int = 100        # P03
   sf4DevFileTwo: int = 0       # P04
   sf4RateTwo: int = 100        # P05
   sf4DevFileThree: int = 0     # P06
   sf4RateThree: int = 100      # P07
   sf4DevStoreNr: int = 1       # P08
   sf4Comment: str = "Offset"   # PComment

# import base class and define class name of the current download
BASE_DL_NAME = "Daihen_FD19"
from Daihen_FD19 import Daihen_FD19
DOWNLOAD_CLASS_NAME = "Daihen_FD19_Arc_Welding"

class Daihen_FD19_Arc_Welding(Daihen_FD19):
   """DAIHEN_FD19 arc welding downloader 
   Base robot vendor downloader
   Derived from: Daihen_FD19 base downloader
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
   # Upload WorkMethod name
   WM_NAME_UPLOAD = "DefaultUploadMethod"

   # connection type between touch sensing and welding operation (operation-start/end-shortest distance)
   AW_TOUCHSENSE_CONNECT_TYPE = "TSConnectionType"

   # identifiers are events added to the touch sensing points in the within the touch sensing cycle.
   TS_POINT_IDENTIFIER_START_APP = "TouchPointStartAppEvent"
   TS_POINT_IDENTIFIER_COLLISION = "TouchPointCollisionEvent"
   TS_POINT_IDENTIFIER_END = "TouchPointEndEvent"
   TS_POINT_IDENTIFIER_START_RET = "TouchPointStartRetEvent"

   AW_CONNECT_TOUCH_PROCESS_TYPE = "ConnectTouchProcessType"
   # touch operation attribute
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
   # Calibration methods
   AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
   AW_SEAMSEARCHING = "SeamSearching"
   AW_SEAMFINDING = "SeamFinding"   
   AW_SEAMTRACKING = "SeamTracking"
   # ArcOn attribues JSON
   OTC_ARCON_JSON = "OTC_ARCON_JSON"
   OTC_WELD_SPEED = "Speed"
   # Weaving
   AW_WEAVE_SCHEDULE_DEFINE = "WeaveScheduleDefine"
   # Thru Arc Seam Tracking (ArcSensor)
   AW_ARCSENSE = "ArcSenseSt"
   AW_ARCSENSE_ST_SENSOR_ID = "ArcSensorId"
   AW_ARCSENSE_ST_COND_FILE = "ArcSenseStCondFile"
   AW_ARCSENSE_ST_SAMPLE_DATA = "ArcSenseStSampleData"
   AW_ARCSENSE_ET_COND_FILE = "ArcSenseEtCondFile"
   # Laser Tracking Start - ZT
   AW_LASER_TRACKER_ONOFF = "SeamTrackingOnOff"
   AW_LASER_SENSOR_ID = "LaserSensorId"
   AW_LASER_ZT_GFF = "LaserZtGFF"
   AW_LASER_ZT_LSR = "LaserZtLSR"
   AW_LASER_ZT_POS_REGISTER = "LaserZtPosRegister"
   AW_LASER_ZT_POSTURE = "LaserZtPosture"
   # Laser Tracking End - ZE
   AW_LASER_ZE_STORE_NUMBER = "LaserZeStoreNumber"
   AW_LASER_ZE_STORE_COORDINATE = "LaserZeStoreCoordinate"
   AW_LASER_ZE_OVER_DEV_RANGE = "LaserZeOverDevRange"
   # Laser Seam Search - ZJ
   AW_LASER_ZJ_ON  = "LaserZjOn"
   AW_LASER_ZJ_GFF = "LaserZjGFF"
   AW_LASER_ZJ_GAP = "LaserZjGAP"
   AW_LASER_ZJ_STORE_NUMBER = "LaserZjStoreNumber"
   AW_LASER_ZJ_BASE_POS_Y = "LaserZjBasePositionY"
   AW_LASER_ZJ_BASE_POS_Z = "LaserZjBasePositionZ"
   AW_LASER_ZJ_SEARCH_DELAY = "LaserZjSearchWaitDelay"
   AW_LASER_ZJ_STABLE_DELAY = "LaserZjSearchStableDelay"
   AW_LASER_ZJ_STORE_COORDINATES = "LaserZjStoreCoordinates"
   AW_LASER_ZJ_STORE_LIT = [ "Machine","Base","Tool","User","Absolute","Workpiece"]
   AW_LASER_ZJ_DEV_COMPOSITION = "LaserZjDevComposition"
   AW_LASER_ZJ_AUTO_MANUAL_MODIFY = "LaserZjAutoManualModify"
   AW_LASER_ZJ_DEVIATION_LENGTH = "LaserZjDeviationLength"
   AW_LASER_ZJ_MIN_DEPTH_VALUE = "LaserZjMinDepthValue"
   AW_LASER_ZJ_GAP_WATCH_RANGE_MAX = "LaserZjGapWatchRangeMax"
   AW_LASER_ZJ_GAP_WATCH_RANGE_MIN = "LaserZjGapWatchRangeMin"
   AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX = "LaserZjAngleOneRangeMax"
   AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN = "LaserZjAngleOneRangeMin"
   AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX = "LaserZjAngleTwoRangeMax"
   AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN = "LaserZjAngleTwoRangeMin"

   # Laser ZF/ZN On
   AW_LASER_ZF_ON = "LaserZfOn"
   AW_LASER_ZN_ON = "LaserZnOn"
   # Laser Start - ZF
   AW_LASER_ZF_GFF = "LaserZfGFF"
   AW_LASER_ZF_LSR = "LaserZfLSR"
   AW_LASER_ZF_POS_REGISTER = "LaserZfPosRegister"
   AW_LASER_ZF_POSTURE = "LaserZfPosture"
   AW_LASER_ZF_STORE_NUMBER = "LaserZfStoreNumber"
   AW_LASER_ZF_STORE_COORDINATE = "LaserZfStoreCoordinate"
   AW_LASER_ZF_SEARCH_RANGE = "LaserZfSearchRange"
   AW_LASER_ZF_OFFSET = "LaserZfOffset"
   AW_LASER_ZF_SPEED = "LaserZfSpeed"
   # Laser End - ZE
   AW_LASER_ZN_GFF = "LaserZnGFF"
   AW_LASER_ZN_LSR = "LaserZnLSR"
   AW_LASER_ZN_OFFSET = "LaserZnOffset"
   AW_LASER_ZN_SEARCH_RANGE = "LaserZnSearchRange"
   # OTC Arc on/off attributes
   OTC_POWER_SOURCE_NUMBER = "OTC_POWER_SOURCE_NUMBER"
   OTC_ARC_ON_CODE = "OTC_ARC_ON_CODE"
   OTC_ARC_OFF_CODE = "OTC_ARC_OFF_CODE"
   OTC_WELD_CHARACTER = "OTC_WELD_CHARACTER"
   OTC_WIRE_FEED = "OTC_WIRE_FEED"
   OTC_CURRENT = "OTC_CURRENT"
   OTC_VOLTAGE = "OTC_VOLTAGE"
   OTC_WELD_PRGNR_DEF = "OTC_WELD_PRGNR_DEF"
   WeaveOnOff = "WeaveOnOff"
   OTC_WEAVE_COND_NR = "OTC_WEAVE_COND_NR"
   # OTC touch-sense SF1 specific attributes (touch single point)
   SF1_P01_MECHNO = "SF1_P01_MECHNO"
   SF1_P02_STORENR = "SF1_P02_STORENR"
   SF1_P03_IDX_STORE_COORD = "SF1_P03_IDX_STORE_COORD"
   SF1_P04_DUMMY = "SF1_P04_DUMMY"
   SF1_P05_STORE_POS_START = "SF1_P05_STORE_POS_START"
   SF1_P06_DEV_COMP = "SF1_P06_DEV_COMP"
   SF1_P07_TOUCH_LOGIC = "SF1_P07_TOUCH_LOGIC"
   SF1_P08_SEARCH_SPEED = "SF1_P08_SEARCH_SPEED"
   SF1_P09_S_RANGE_MAX = "SF1_P09_S_RANGE_MAX"
   SF1_P10_S_RANGE_MIN = "SF1_P10_S_RANGE_MIN"
   SF1_P11_OVER_DEV_RANGE = "SF1_P11_OVER_DEV_RANGE"
   SF1_P12_IDX_STORE_COORD = "SF1_P12_IDX_STORE_COORD"
   SF1_P13_DUMMY = "SF1_P13_DUMMY"
   # OTC touch-sense SF3 specific attributes (activate offset)
   SF3_P03_CALL_POS = "SF3_P03_CALL_POS"
   SF3_P04_SF3_SECTION = "SF3_P04_SF3_SECTION"
   SF3_P04_OPTIONS = ["End","Start","All End"]
   SF3_P05_POSTURE_CALL_0 = "SF3_P05_POSTURE_CALL_0"
   SF3_P06_OFFSET_X = "SF3_P06_OFFSET_X"
   SF3_P07_OFFSET_Y = "SF3_P07_OFFSET_Y"
   SF3_P08_OFFSET_Z = "SF3_P08_OFFSET_Z"
   # OTC touch-sense SF4 specific attributes (combine multiple touch offsets into one)
   SF4_OUTPUT = "SF4_OUTPUT"
   SF4_P2_DEVPOS_1 = "SF4_P2_DEVPOS_1"
   SF4_P3_RATIO_1 = "SF4_P3_RATIO_1"
   SF4_P4_DEVPOS_2 = "SF4_P4_DEVPOS_2"
   SF4_P5_RATIO_2 = "SF4_P5_RATIO_2"
   SF4_P6_DEVPOS_3 = "SF4_P6_DEVPOS_3"
   SF4_P7_RATIO_3 = "SF4_P7_RATIO_3"
   SF4_P8_DEVPOS_COMB = "SF4_P8_DEVPOS_COMB"

#################### BASE FUNCTIONS ####################

   def __init__(self):
      """Class initialization
      """
      super().__init__()

      # Initialize the data classes and assign it to an instance variable
      self.ArcOnInfo = ArcOnInfo()
      self.ArcOnWBPL = ArcOnWBPL()
      self.ArcOffWBPL = ArcOffWBPL()
      self.ArcOnDPAX = ArcOnDPAX()
      self.ArcOffDPAX = ArcOffDPAX()
      self.ArcOnDA = ArcOnDA()
      self.ArcOffDA = ArcOffDA()
      self.ArcOnST = ArcOnST()
      self.ArcOffET = ArcOffET()

      # arc welding specific attribute names
      # variable top store if and which calibration methods
      self.UseTouchSensingSurface = True
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
      self.ResetTouchSensingOffset = True
      # save touch sensing speed to output it in the touch sensing macro
      self.TouchSensingSpeed = 10 # mm/sec
      # save the output path
      self.OutputFilePathTouchSensing = ""
      # welding speed
      self.WeldingSpeed = 30
      # welding program number
      self.WeldingProgramNumber = 1
      # save if weaving was turned on while arc on
      self.WeavingOn = False
      # save current workmethod name of the operation
      self.WorkmethodName = ''
      # Calibration Method
      self.SeamCalibrationMethod = ''
      self.SeamSearching = 0
      # Flag to distinguish between SeamFinding for start or endpoint
      self.SeamFindingEndLocation = False
      self.SeamFindingId = 0
      self.SeamFindingIdSet = False

      self.SeamFindingStartId = 0
      self.SeamFindingEndId = 0
      # Set seam finding flag for stitch welding WM
      self.SeamFindingIsActive = False
      # 
      self.SeamTracking = 0
		# Weaving
      self.WeaveScheduleDefine = 0
		# Thru Arc Seam Tracking (ArcSensor)
      self.ArcSenseSt = False
      self.ArcSensorId = 0
      self.ArcSenseStCondFile = 0
      self.ArcSenseStSampleData = 0
      self.ArcSenseEtCondFile = 0
		# Laser Tracking Start - ZT
      self.LaserTrackerOnOff=False
      self.LaserSensorId = 0
      self.LaserSensorIsOn = False
      self.LaserZtGFF = 0
      self.LaserZtLSR = 0
      self.LaserZtPosRegister = 0
      self.LaserZtPosture = 0
		# Laser Tracking End - ZE
      self.LaserZeStoreNumber = 0
      self.LaserZeStoreCoordinate = 0
      self.LaserZeOverDevRange = 0

      # Laser Start - ZF
      self.LaserZfOn = False
      self.LaserZfGFF = 0
      self.LaserZfLSR = 0
      self.LaserZfPosRegister = 0
      self.LaserZfPosture = 0
      self.LaserZfStoreNumber = 0
      self.LaserZfStoreCoordinate = 0
      self.LaserZfSearchRange = 0
      self.LaserZfOffset = 0
      self.LaserZfSpeed = 0
      # Laser End - ZE
      self.LaserZnOn = False
      self.LaserZnGFF = 0
      self.LaserZnLSR = 0
      self.LaserZnOffset = 0
      self.LaserZnSearchRange = 0
		# Laser Seam Search - ZJ
      self.LaserZjOn = False
      self.LaserZjGFF = 0
      self.LaserZjGAP = 0
      self.LaserZjBasePositionY = 0
      self.LaserZjBasePositionZ = 0
      self.LaserZjSearchWaitDelay = 0
      self.LaserZjSearchStableDelay = 0
      self.LaserZjStoreCoordinates = "World"
      self.LaserZjDevComposition = True
      self.LaserZjAutoManualModify = True
      self.LaserZjDeviationLength = 10.0
      self.LaserZjMinDepthValue = 5.0
      self.LaserZjGapWatchRangeMax = 10.0
      self.LaserZjGapWatchRangeMin = 0.0
      self.LaserZjAngleOneRangeMax = 180.0
      self.LaserZjAngleOneRangeMin = 0.0
      self.LaserZjAngleTwoRangeMax = 90.0
      self.LaserZjAngleTwoRangeMin = 0.0

      # OTC Arc on/off
      self.otcPowerSourceNumber:str = ''
      self.otcArcOn = ''
      self.otcArcOff = ''
      # self.otcWeldProgramNumber = 0
      # self.otcWeldCharacter = 0
      # self.otcWireFeed = 0
      # self.otcCurrent = 0
      # self.otcVoltage = 0
      # # OTC Weaving attributes
      # self.otcWeaveOnOff = False
      # self.otcWeaveConditionNumber = 0
      # OTC touch-sense SF1 specific attributes (touch single point)
      self.sf1P01MechanismNumber = 1
      self.sf1P02StoreNumber = 0
      self.sf1P03IndexStoreCoord = 0
      self.st1P04Dummy = 0
      self.sf1P05StorePositionStart = 0
      self.sf1P05TouchId=0
      self.sf1P06DeviationComposition = 0
      self.sf1P07TouchLogic = 0
      self.sf1P08SearchSpeed = 42
      self.sf1P09SearchRangeMax = 0.1
      self.sf1P10SearchRangeMin = 0.0
      self.sf1P11OverDeviationRange = 0.015
      self.sf1P12IndexStoreCoordinate = 2
      self.sf1P13Dummy = 1
      # OTC touch-sense SF3 specific attributes (activate offset)
      self.sf3P03CallPosition = 500
      self.sf3P04Section = 0
      self.sf3P04Options = ["End","Start","All End"]
      self.sf3P05PostureCall0 = 0
      self.sf3P06OffsetX = 0.0
      self.sf3P07OffsetY = 0.0
      self.sf3P08OffsetZ = 0.0
      self.sf3EventActivated = False
      self.sf3Flag = False
      self.sf3TouchId = 0
      self.sf3CancelCommand = "SF3 1,2,%s,2,0,0,0,0,0.0,0.0,0.0,0.0,1,1,0 'Cancel Offset"
      # OTC touch-sense SF4 specific attributes (combine multiple touch offsets into one)
      self.sf4P2DeviationPosition1 = 10
      self.sf4P3Ratio1 = 1
      self.sf4P4DeviationPosition2 = 11
      self.sf4P5Ratio2 = 1
      self.sf4P6DeviationPosition3 = 12
      self.sf4P7Ratio3 = 1
      self.sf4P8DeviationPositionCombined = 500
      self.SequenceList = [0,0,0]
      # LaserTracker attributes
      self.LaserTrackerZF = False
      self.LaserTrackerZJ = False
      # OTC Encoder Pulse values for ZJ Laser Search
      self.CENOlpJointPulseConstantValues = '-1460253;-1460253;1418531.5;-834430.3;844860.6;-531949.3'
      self.CENOlpJointStdPosAngleValues = '0.0;90.0;0.0;0.0;-90.0;0.0'
      self.CENOlpJointStdPosEncoderValues = '8388608;8388608;8388608;8388608;8388608;8388608'
      self.CENOlpJoint56CouplingFactor = 0.01961

      self._operationMarker = ["Arc Spot:",
                               "Arc Weld:",
                               "SeamSearch ID:",
                               "SeamFind:",
                               "Touch ID:",
                               "Operation:"]
      
      self.OTCDeburringMethod=False
      self.OTCDeburringSpeed=400.0
      self.DownloadJointsOnly = False
      self.LoggingAW = None
      self.OnDevAW = False

#################### BASE FUNCTIONS ####################

   def DevLoggingAW(self, info):
      if self.OnDevAW == True and self.LoggingAW != None:
         self.LoggingAW.LogInfo(info)

   def Initialize(self, operator : DULPythonDownloadOperator):
      """Translator initialization.
      Called only once per download, even when downloading sub programs

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      super().Initialize(operator)

      # global Logger
      self.LoggingAW = operator.GetLogOperator()

      # Get robot resource and its attributes
      controller = operator.GetController()
      resources=controller.GetResources()
      
      jointPulseConstantSet = False
      jointStdPosAngleSet = False
      jointStdPosEncoderSet = False
      joint56CouplingFactorSet = False

      for resource in resources:
         if (resource.GetItemType().name == 'Production'):
            if (resource.GetItemSubType().name == 'MachineRobot'):
               robot=resource
               robotAttributes=robot.GetAttributes()
               for att in robotAttributes:
                  # OTC Encoder Pulse Constant Values for ZJ Laser Search
                  if att.GetName() == 'XXX_CENOlpJointStepFactorValues':
                     self.CENOlpJointPulseConstantValues = robot.GetString('CENOlpJointStepFactorValues',1)
                     jointPulseConstantSet = True
                  elif att.GetName() == 'PulseConstantValues':
                     self.CENOlpJointPulseConstantValues = robot.GetString('PulseConstantValues',1)
                     jointPulseConstantSet = True
                  # OTC Encoder Std Pos Angle Values for ZJ Laser Search
                  elif att.GetName() == 'XXX_CENOlpJointZeroOffsetValues':
                     self.CENOlpJointStdPosAngleValues = robot.GetString('CENOlpJointZeroOffsetValues',1)
                     jointStdPosAngleSet = True
                  elif att.GetName() == 'StdPosAngleValues':
                     self.CENOlpJointStdPosAngleValues = robot.GetString('StdPosAngleValues',1)
                     jointStdPosAngleSet = True
                  # OTC Encoder Std Pos Encoder Values for ZJ Laser Search
                  elif att.GetName() == 'YYY_CENOlpJointStdPosEncoderValues':
                     self.CENOlpJointStdPosEncoderValues = robot.GetString('CENOlpJointStdPosEncoderValues',1)
                     jointStdPosEncoderSet = True
                  elif att.GetName() == 'StdPosEncoderValues':
                     self.CENOlpJointStdPosEncoderValues = robot.GetString('StdPosEncoderValues',1)
                     jointStdPosEncoderSet = True
                  # OTC Encoder Link coef.inv.6 for ZJ Laser Search
                  elif att.GetName() == 'XXX_CENOlpJoint56CouplingFactor':
                     self.CENOlpJoint56CouplingFactor = float(robot.GetString('CENOlpJoint56CouplingFactor',1))
                     joint56CouplingFactorSet = True
                  elif att.GetName() == 'LinkCoefInv6Factor':
                     self.CENOlpJoint56CouplingFactor = float(robot.GetString('LinkCoefInv6Factor',1))
                     joint56CouplingFactorSet = True

      if jointPulseConstantSet == False:
         self.LoggingAW.LogWarn('Download Warning : "PulseConstantValues" not set. Taken Default : ' + self.CENOlpJointPulseConstantValues)
      if jointStdPosAngleSet == False:
         self.LoggingAW.LogWarn('Download Warning : "StdPosAngleValues" not set. Taken Default : ' + self.CENOlpJointStdPosAngleValues)
      if jointStdPosEncoderSet == False:
         self.LoggingAW.LogWarn('Download Warning : "StdPosEncoderValues" not set. Taken Default : ' + self.CENOlpJointStdPosEncoderValues)
      if joint56CouplingFactorSet == False:
         self.LoggingAW.LogWarn('Download Warning : "LinkCoefInv6Factor" not set. Taken Default : ' + str(self.CENOlpJoint56CouplingFactor))

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
      if operation.GetOperationType().name == "Upload":
         self.WorkmethodName = "DefaultUploadMethod"

      temp = '_______OperationStart ========' + str(operation.GetName()) + ' ======= '
      self.DevLoggingAW(temp)
      temp = '_______OperationType ========' + str(operation.GetOperationType().name) + ' ======= '
      self.DevLoggingAW(temp)

      # Laser Tracker On/Off
      self.LaserTrackerOnOff=operation.GetBool('SeamTrackingOnOff', True)

      self.OTCDeburringMethod=operation.GetBool('ArcDeburringMethod', True)
      self.OTCDeburringSpeed=operation.GetDouble('ArcDeburringSpeed', True)
      
      self.DownloadJointsOnly = operator.GetController().GetActiveProgram().GetBool('DownloadJointsOnly', True)
      #self.LoggingAW.LogInfo(".......Daihen_FD19_Arc_Welding.py : found AW_DOWNLOAD_JOINTS_ONLY = DownloadJointsOnly = " + str(self.DownloadJointsOnly))

      # get Arc on/off attributes
      self.otcPowerSourceNumber = str(operation.GetInteger(self.OTC_POWER_SOURCE_NUMBER, True))
      self.otcArcOn = operation.GetString(self.OTC_ARC_ON_CODE, True)
      self.otcArcOff = operation.GetString(self.OTC_ARC_OFF_CODE, True)
      self.WeldingSpeed = operation.GetDouble(self.OTC_WELD_SPEED, True)
      
      # self.otcWeldCharacter = operation.GetInteger(self.OTC_WELD_CHARACTER, True)
      # self.otcWireFeed = operation.GetInteger(self.OTC_WIRE_FEED, True)
      # self.otcCurrent = operation.GetInteger(self.OTC_CURRENT, True)
      # self.otcVoltage = operation.GetInteger(self.OTC_VOLTAGE, True)

      # Calibration methods
      self.SeamCalibrationMethod = operation.GetLiteral(self.AW_SEAM_CALIBRATION_METHOD,True)
      if self.SeamCalibrationMethod == '':
         if self.WorkmethodName == 'SeamFindingWorkMethod':
            self.SeamCalibrationMethod = self.AW_SEAMFINDING

      if (self.SeamCalibrationMethod == self.AW_SEAMTRACKING) or (self.SeamCalibrationMethod == self.AW_SEAMFINDING):
         # Laser Tracker On/Off
         self.LaserTrackerOnOff=operation.GetBool('SeamTrackingOnOff', True)
         # Laser Tracking Start - ZT
         self.LaserSensorId = operation.GetInteger(self.AW_LASER_SENSOR_ID, True)
         self.LaserZtGFF = operation.GetInteger(self.AW_LASER_ZT_GFF, True)
         self.LaserZtLSR = operation.GetInteger(self.AW_LASER_ZT_LSR, True)
         self.LaserZtPosRegister = operation.GetInteger(self.AW_LASER_ZT_POS_REGISTER, True)
         self.LaserZtPosture = operation.GetInteger(self.AW_LASER_ZT_POSTURE, True)

         # Laser Tracking End - ZE
         self.LaserZeStoreNumber = operation.GetInteger(self.AW_LASER_ZE_STORE_NUMBER, True)
         self.LaserZeStoreCoordinate = operation.GetInteger(self.AW_LASER_ZE_STORE_COORDINATE, True)
         self.LaserZeOverDevRange = int(operation.GetDouble(self.AW_LASER_ZE_OVER_DEV_RANGE, True)*1000)

         # Laser Seam Start Search - ZF
         self.LaserZfOn = operation.GetBool(self.AW_LASER_ZF_ON, True)
         self.LaserZfGFF = operation.GetInteger(self.AW_LASER_ZF_GFF, True)
         self.LaserZfLSR = operation.GetInteger(self.AW_LASER_ZF_LSR, True)
         self.LaserZfPosRegister = operation.GetInteger(self.AW_LASER_ZF_POS_REGISTER, True)
         self.LaserZfPosture = operation.GetInteger(self.AW_LASER_ZF_POSTURE, True)
         self.LaserZfStoreNumber = operation.GetInteger(self.AW_LASER_ZF_STORE_NUMBER, True)
         self.LaserZfStoreCoordinate = operation.GetInteger(self.AW_LASER_ZF_STORE_COORDINATE, True)
         self.LaserZfSearchRange = operation.GetDouble(self.AW_LASER_ZF_SEARCH_RANGE, True)
         self.LaserZfOffset = operation.GetDouble(self.AW_LASER_ZF_OFFSET, True)
         self.LaserZfSpeed = operation.GetDouble(self.AW_LASER_ZF_SPEED, True)

         # Laser Seam End Search - ZF                                             
         self.LaserZnOn = operation.GetBool(self.AW_LASER_ZN_ON, True)
         self.LaserZnGFF = operation.GetInteger(self.AW_LASER_ZN_GFF, True)
         self.LaserZnLSR = operation.GetInteger(self.AW_LASER_ZN_LSR, True)
         self.LaserZnOffset = operation.GetDouble(self.AW_LASER_ZN_OFFSET, True)
         self.LaserZnSearchRange = operation.GetDouble(self.AW_LASER_ZN_SEARCH_RANGE, True)

         # Laser Seam Search - ZJ
         self.LaserZjOn = operation.GetBool(self.AW_LASER_ZJ_ON, True)
         self.LaserZjGFF = operation.GetInteger(self.AW_LASER_ZJ_GFF, True)
         self.LaserZjGAP = operation.GetInteger(self.AW_LASER_ZJ_GAP, True)
         if self.SeamFindingIdSet == False:
            self.SeamFindingId = self.LaserZjGAP - 1
            self.SeamFindingIdSet = True
            
         self.LaserZjStoreNumber = operation.GetInteger(self.AW_LASER_ZJ_STORE_NUMBER, True)
         self.LaserZjBasePositionY = operation.GetDouble(self.AW_LASER_ZJ_BASE_POS_Y, True)
         self.LaserZjBasePositionZ = operation.GetDouble(self.AW_LASER_ZJ_BASE_POS_Z, True)
         self.LaserZjSearchWaitDelay = operation.GetDouble(self.AW_LASER_ZJ_SEARCH_DELAY, True)
         self.LaserZjSearchStableDelay = operation.GetDouble(self.AW_LASER_ZJ_STABLE_DELAY, True)

         self.LaserZjStoreCoordinates = operation.GetLiteral(self.AW_LASER_ZJ_STORE_COORDINATES, True)
         self.LaserZjDevComposition = operation.GetBool(self.AW_LASER_ZJ_DEV_COMPOSITION, True)
         self.LaserZjAutoManualModify = operation.GetBool(self.AW_LASER_ZJ_AUTO_MANUAL_MODIFY, True)
         self.LaserZjDeviationLength = operation.GetDouble(self.AW_LASER_ZJ_DEVIATION_LENGTH, True)
         self.LaserZjMinDepthValue = operation.GetDouble(self.AW_LASER_ZJ_MIN_DEPTH_VALUE, True)
         self.LaserZjGapWatchRangeMax = operation.GetDouble(self.AW_LASER_ZJ_GAP_WATCH_RANGE_MAX, True)
         self.LaserZjGapWatchRangeMin = operation.GetDouble(self.AW_LASER_ZJ_GAP_WATCH_RANGE_MIN, True)
         self.LaserZjAngleOneRangeMax = operation.GetDouble(self.AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX, True)
         self.LaserZjAngleOneRangeMin = operation.GetDouble(self.AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN, True)
         self.LaserZjAngleTwoRangeMax = operation.GetDouble(self.AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX, True)
         self.LaserZjAngleTwoRangeMin = operation.GetDouble(self.AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN, True)

		# Weaving
      self.WeaveScheduleDefine = operation.GetInteger(self.AW_WEAVE_SCHEDULE_DEFINE, True)

		# Thru Arc Seam Tracking (ArcSensor)
      self.ArcSenseSt = operation.GetBool(self.AW_ARCSENSE, True)
      self.ArcSensorId = operation.GetInteger(self.AW_ARCSENSE_ST_SENSOR_ID, True)
      self.ArcSenseStCondFile = operation.GetInteger(self.AW_ARCSENSE_ST_COND_FILE, True)
      self.ArcSenseStSampleData = operation.GetInteger(self.AW_ARCSENSE_ST_SAMPLE_DATA, True)
      self.ArcSenseEtCondFile = operation.GetInteger(self.AW_ARCSENSE_ET_COND_FILE, True)


      # ArcSpot operation
      if self.WorkmethodName == self.WM_NAME_CONTINUES:
         self.OutputOtcComment(operator, ' Arc Spot: %s' % (operation.GetName()))
         # Output offset at Start of weld
         if self.SeamFindingStartId != 0:
            # Activate SF3 Offset
            paraString = "%d,3,%d,1,0,0,0,0,0,0,0,0,1,1,0 'Activate Offset"  % \
                                 (self.sf1P01MechanismNumber,self.SeamFindingStartId)
            sOutput = self.passSF3Params(paraString)
            self.AddLineToSource(sOutput)

            self.SeamFindingStartId = 0
      # stich welding operation
      elif self.WorkmethodName == self.WM_NAME_STICH:
         self.OutputOtcComment(operator, ' Arc Weld: %s' % (operation.GetName()))
         # Output offset at Start of weld
         if self.SeamFindingStartId != 0:
            # Activate SF3 Offset
            paraString = "%d,3,%d,1,0,0,0,0,0,0,0,0,1,1,0 'Activate Offset"  % \
                                 (self.sf1P01MechanismNumber,self.SeamFindingStartId)
            sOutput = self.passSF3Params(paraString)
            self.AddLineToSource(sOutput)

            self.SeamFindingStartId = 0

      # seam search operation
      elif self.WorkmethodName == self.WM_NAME_SEAM:
         self.OutputOtcComment(operator, ' SeamSearch ID: %s' % (operation.GetName()))

      elif self.WorkmethodName == self.WM_NAME_SEAM_FIND:
         self.OutputOtcComment(operator, ' SeamFind: %s' % (operation.GetName()))
         self.SeamFindingEndLocation = operation.GetBool('SeamFindingEndLocation', True)
         # self.SeamFindingId = operation.GetInteger('SeamFindingId', True)
         self.SeamFindingId += 1
         if self.SeamFindingEndLocation:
            self.SeamFindingEndId = self.SeamFindingId
         else:
            self.SeamFindingStartId = self.SeamFindingId
         pass
      # touch sensing operation
      elif self.WorkmethodName == self.WM_NAME_TOUCH:
         # OTC touch-sense specific attributes
         # OTC TouchSense attributes
         self.TouchSensingSpeed = operation.GetDouble(self.AW_TOUCHSENS_SENSING_SPEED,True)*1000
         self.sf1P01MechanismNumber = operation.GetInteger(self.SF1_P01_MECHNO,False)
         self.sf1P02StoreNumber = operation.GetInteger(self.SF1_P02_STORENR,False)
         self.sf1P03IndexStoreCoord = operation.GetInteger(self.SF1_P03_IDX_STORE_COORD,False)
         self.st1P04Dummy = operation.GetInteger(self.SF1_P04_DUMMY,False)
         self.sf1P05StorePositionStart = operation.GetInteger(self.SF1_P05_STORE_POS_START,False)
         self.sf1P05TouchId += 1
         self.sf1P06DeviationComposition = int(operation.GetBool(self.SF1_P06_DEV_COMP,False))
         self.sf1P07TouchLogic = int(operation.GetBool(self.SF1_P07_TOUCH_LOGIC,False))
         self.sf1P08SearchSpeed = operation.GetInteger(self.SF1_P08_SEARCH_SPEED,False)
         self.sf1P09SearchRangeMax = operation.GetDouble(self.SF1_P09_S_RANGE_MAX,False)*1000
         self.sf1P10SearchRangeMin = operation.GetDouble(self.SF1_P10_S_RANGE_MIN,False)*1000
         self.sf1P11OverDeviationRange = operation.GetDouble(self.SF1_P11_OVER_DEV_RANGE,False)*1000
         self.sf1P12IndexStoreCoordinate = operation.GetInteger(self.SF1_P12_IDX_STORE_COORD,False)
         self.sf1P13Dummy = operation.GetInteger(self.SF1_P13_DUMMY,False)

         self.sf3P03CallPosition = operation.GetInteger(self.SF3_P03_CALL_POS,False)
         self.sf3P04Section = self.sf3P04Options.index(operation.GetLiteral(self.SF3_P04_SF3_SECTION,False))
         self.sf3P05PostureCall0 = operation.GetInteger(self.SF3_P05_POSTURE_CALL_0,False)
         self.sf3P06OffsetX = operation.GetDouble(self.SF3_P06_OFFSET_X,False)
         self.sf3P07OffsetY = operation.GetDouble(self.SF3_P07_OFFSET_Y,False)
         self.sf3P08OffsetZ = operation.GetDouble(self.SF3_P08_OFFSET_Z,False)

         self.sf4P2DeviationPosition1 = operation.GetInteger(self.SF4_P2_DEVPOS_1,False)
         self.sf4P3Ratio1 = operation.GetDouble(self.SF4_P3_RATIO_1,False) * 100
         self.sf4P4DeviationPosition2 = operation.GetInteger(self.SF4_P4_DEVPOS_2,False)
         self.sf4P5Ratio2 = operation.GetDouble(self.SF4_P5_RATIO_2,False) * 100
         self.sf4P6DeviationPosition3 = operation.GetInteger(self.SF4_P6_DEVPOS_3,False)
         self.sf4P7Ratio3 = operation.GetDouble(self.SF4_P7_RATIO_3,False) * 100
         self.sf4P8DeviationPositionCombined = operation.GetInteger(self.SF4_P8_DEVPOS_COMB,False)
         # get Touch connect ID
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
         self.OutputOtcComment(operator, ' Touch ID:%d-%d' % (self.LastTouchSensingSequenceID, self.TouchSensingSequencingCounter))
      else:
         if any(marker in operation.GetName() for marker in self._operationMarker):
            self.OutputOtcComment(operator, ' %s' % (operation.GetName()))
         else:
            self.OutputOtcComment(operator, ' Operation: %s' % (operation.GetName()))

   def HandleEvent(self, operator: DULPythonDownloadOperator, currentMotion: DULPythonMotion, event: DULPythonEvent):
      """Handle event

      Args:
         operator: download operator
         event: access to the event object
      """   
      # check if TOUCH SENSING event
      if event.GetName() == 'TouchSensingEvent':
         
         # might be cancel before
         if self.sf3Flag == True and self.sf3TouchId != 0 and self.sf3TouchId != self.TouchIdPositionRegister:
            self.sf3Flag = False
            cancelLine = self.sf3CancelCommand % self.sf3TouchId
            #self.AddLineToSource("%s IDold %d  IDnew %d" %(self.sf3CancelCommand, self.sf3TouchId, self.TouchIdPositionRegister))
            self.AddLineToSource("%s" %(cancelLine))
         
         # output touch sensing
         self.OutputTouchSensingE2(operator, event)
         # return to avoid potential double handling
         return

      # 
      elif event.GetName() == 'ConnectTouchProcessPointEvent':
         # output E2 touch sensing
         if self.UseTouchSensingSurface:
            self.OutputConnectTouchProcessPointEvent(operator, currentMotion, event)
         else:
            pass
         # return to avoid potential double handling
         return
      
      # check if ARC ON event
      elif event.GetName() == 'ArcOnEvent':
         self.OutputArcOnEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return
      
      # check if ARC OFF event
      elif event.GetName() == 'ArcOffEvent':
         self.OutputArcOffEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # check if SeamFinding event
      elif event.GetName() == 'SeamFindingScanEvent':
         self.SeamFindingIsActive = True
         self.SpecialMotion = False
         self.LaserTrackerZJ = True
         self.OutputSeamFindingEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # check if SeamTracking event
      elif event.GetName() == 'SeamTrackingEvent':
         self.OutputSeamTrackingEvent(operator, currentMotion, event)
         if self.LaserZfOn:
            self.SpecialMotion = True
            self.LaserTrackerZF = True
         # return to avoid postential double handling
         return

      # check if SeamTrackingZJEvent
      elif event.GetName() == 'SeamTrackingZJEvent':
         self.SpecialMotion = True
         self.LaserTrackerZJ = True
         # return to avoid postential double handling
         return
      
      # check if SeamTrackingOffEvent event
      elif event.GetName() == 'SeamTrackingOffEvent':
         self.OutputSeamTrackingOffEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return

      # check if SeamTrackerOffEvent event after retract
      elif event.GetName() == 'SeamTrackerOffEvent':
         self.OutputSeamTrackerOffEvent(operator, currentMotion, event)
         # return to avoid postential double handling
         return
      
      # check if SeamTrackerOffEvent event after retract
      elif event.GetName() == 'UploadTSMotionEvent':
         self.OutputUploadedTouchSensingEvent(operator, currentMotion, event)
         self.SpecialMotion = True
         # return to avoid postential double handling
         return
      
      # ***manual*** ZJ, SF3, SF4, SF8 Events ( !!! output Cycle seperatly to NOT affect current Outputs !!! )
      elif event.GetName() == 'ZJEvent':
         self.OutputManualZJEvent(operator, currentMotion, event)
         return
      elif event.GetName() == 'SF3Event':
         self.OutputManualSF3Event(operator, currentMotion, event)
         return
      elif event.GetName() == 'SF4Event':
         self.OutputManualSF4Event(operator, currentMotion, event)
         return
      elif event.GetName() == 'SF8Event':
         self.OutputManualSF8Event(operator, currentMotion, event)
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
         self.AddLineToSource('  ')
      # stich welding operation
      elif self.WorkmethodName == self.WM_NAME_STICH:
         # add empty line after operation to increase readability
         self.AddLineToSource('  ')
      # seam search operation
      elif self.WorkmethodName == self.WM_NAME_SEAM:
         # add empty line after operation to increase readability
         self.AddLineToSource('  ')
      # touch sensing operation
      elif self.WorkmethodName == self.WM_NAME_TOUCH:
         if self.UseTouchSensingSurface:
            # add empty line after operation to increase readability
            self.AddLineToSource('  ')
      elif self.WorkmethodName == self.WM_NAME_UPLOAD:
         # add empty line after operation to increase readability
         self.AddLineToSource('  ')
      # call method from derived class
      super().OperationEnd(operator, operation)

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      """Called at the end of each the program 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      # disable touch offset at the end of the program if one was acivated before
      if self.sf3EventActivated:
         # Activate SF3 Offset
         paraString = "%d,2,%d,2,%d,%d,%d,%d,0.0,0.0,0.0,0.0,1,1,0 'Cancel Offset"  % \
                           (self.sf1P01MechanismNumber,self.TouchIdPositionRegister,\
                           self.sf3P05PostureCall0,self.sf3P06OffsetX,\
                           self.sf3P07OffsetY,self.sf3P08OffsetZ)
         sOutput = self.passSF3Params(paraString)
         self.AddLineToSource(sOutput)

         self.sf3EventActivated = False
      # call method from derived class
      super().ProgramEnd(operator, program)

#################### SOURCE SECTION ####################

   def OutputSourceSpecialMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Output reference position if needed in technology versions of this base downloader
      e.g. cycle centerpoint or No-Sim-Download-Only

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # get logger
      logger = operator.GetLogOperator()

      # increment point counter
      self.PointCounter += int(1)
      sOutput = ""

      # Laser Tracker ZJ command
      if self.LaserTrackerZJ:
         # create motion group structure but skip non-Unit mechanisms
         motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
         motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

         robotJointTarget = ""
         joints = []
         for joint in motionGroupRobot.Joints:
            if robotJointTarget == "":
               robotJointTarget = "(" + str(round(joint.Value, 2))
               joints.append(joint.Value)
            else:
               robotJointTarget = robotJointTarget + ", " + ("%.2f" % joint.Value)
               joints.append(joint.Value)
         robotJointTarget = robotJointTarget + ")"

         zjPulseString, zjPulseValue0 = self.SetZJPulseString(joints)
      
         self.LaserZjStoreNumber = self.SeamFindingId
         
         # ----------------------------------------------
         self.ZJCycleParams = ZJCycleParams()
         self.ZJCycleParams.zjSensor = self.LaserSensorId
         self.ZJCycleParams.zjMechanism = 1
         self.ZJCycleParams.zjDEV = self.LaserZjStoreNumber
         self.ZJCycleParams.zjGAP = self.LaserZjGAP
         self.ZJCycleParams.zjGFF = self.LaserZjGFF
         self.ZJCycleParams.zjStoreCoordinates = self.GetZjStoreCoordIdx(self.LaserZjStoreCoordinates)  # ["World", "Tool", "Machine"]
         self.ZJCycleParams.zjDevComposition = self.LaserZjDevComposition
         self.ZJCycleParams.zjAutoManualModify = self.LaserZjAutoManualModify
         self.ZJCycleParams.zjBasePointMemory = False
         self.ZJCycleParams.zjSearchWaitDelay = self.LaserZjSearchWaitDelay
         self.ZJCycleParams.zjSearchStableDelay = self.LaserZjSearchStableDelay
         self.ZJCycleParams.zjStoreNumber = self.LaserZjStoreNumber
         self.ZJCycleParams.zjBasePositionX = 0.0
         self.ZJCycleParams.zjBasePositionY = self.LaserZjBasePositionY
         self.ZJCycleParams.zjBasePositionZ = self.LaserZjBasePositionZ
         self.ZJCycleParams.zjDeviationLength = self.LaserZjDeviationLength
         self.ZJCycleParams.zjGapWatchRangeMax = self.LaserZjGapWatchRangeMax
         self.ZJCycleParams.zjGapWatchRangeMin = self.LaserZjGapWatchRangeMin
         self.ZJCycleParams.zjMinDepthValue = self.LaserZjMinDepthValue
         self.ZJCycleParams.zjAngleOneRangeMax = self.LaserZjAngleOneRangeMax
         self.ZJCycleParams.zjAngleOneRangeMin = self.LaserZjAngleOneRangeMin
         self.ZJCycleParams.zjAngleTwoRangeMax = self.LaserZjAngleTwoRangeMax
         self.ZJCycleParams.zjAngleTwoRangeMin = self.LaserZjAngleTwoRangeMin
         self.ZJCycleParams.zjPulseString = zjPulseString
         zjBaseOffset = '%s,%s,%s' % (self.formatDbl(self.ZJCycleParams.zjBasePositionX*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionY*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionZ*1000))
         self.ZJCycleParams.zjBaseOffset = zjBaseOffset
         self.ZJCycleParams.zjPulseValue = zjPulseValue0
         sOutput = self.OutputZJCycle(self.ZJCycleParams)
         #self.AddLineToSource(sOutput)
         # ----------------------------------------------

         self.LaserTrackerZJ = False

      # Laser Tracker Zf command
      if self.LaserZfOn:
         # create motion group structure but skip non-Unit mechanisms
         motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
         motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

         robotJointTarget = ""
         for joint in motionGroupRobot.Joints:
            if robotJointTarget == "":
               robotJointTarget = "(" + str(round(joint.Value, 2))
            else:
               robotJointTarget = robotJointTarget + ", " + ("%.2f" % joint.Value)
         robotJointTarget = robotJointTarget + ")"

         sOutput = "ZF %d,%d,1,%d,%d,%d,%d,5,-1,1,%d,%d,0,5,1,%d,MOVEX,M1J,%s,11,1,-1,0,%d,%d" % \
            (self.GroupRobot,self.LaserSensorId,self.LaserZfStoreCoordinate,self.LaserZfStoreNumber,self.LaserZfGFF,self.LaserZfSpeed,\
            self.LaserZfPosRegister,self.LaserZfSearchRange,self.LaserZfOffset,robotJointTarget,self.LaserZfLSR,self.LaserZfPosture)

         self.LaserTrackerZF = False

      return('%s' % (sOutput))

#################### EVENTS ####################

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
      # might be cancel before
      if self.sf3Flag == True:
         self.sf3Flag = False
         #self.AddLineToSource("%s" %(self.sf3CancelCommand))
         cancelLine = self.sf3CancelCommand % self.sf3TouchId
         self.AddLineToSource("%s" %(cancelLine))
      self.OutputEnableTouchOffsetForWelding(operator, int(touchId))

   def OutputWBPLOn(self, operator: DULPythonDownloadOperator):
      """
      """
      logger = operator.GetLogOperator()

      if self.ArcOnInfo.OTC_WELD_PRGNR != "0":
         # add arc on instruction
         arcOnString = "%s %s,%s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % \
                              (self.otcArcOn,self.otcPowerSourceNumber,self.ArcOnInfo.OTC_WELD_PRGNR,self.ArcOnWBPL.Retry)
         # arcOnString = "%s %s,%s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % \
         #                      (self.otcArcOn,self.otcPowerSourceNumber,self.ArcOnWBPL.AS_Cond_file,self.ArcOnWBPL.Retry)
      else:
         # assign E2 attributes
         self.ArcOnWBPL.Welding_speed = str(self.WeldingSpeed)
         if self.ArcOnWBPL.Welding_speed == "nan":
            logger.LogWarn('ArcOnWBPL.Welding_speed is set to 0.01')
            self.ArcOnWBPL.Welding_speed = "0.01"

         # Set Current or Wire Feed mode
         if self.ArcOnInfo.OTC_CURRENT == 0:
            self.ArcOnWBPL.Voltage_adjustment_method = '0'
            self.ArcOnWBPL.Welding_current_High = self.ArcOnInfo.OTC_WIRE_FEED
         else:
            self.ArcOnWBPL.Voltage_adjustment_method = '1'
            self.ArcOnWBPL.Welding_current_High = self.ArcOnInfo.OTC_CURRENT
         # format string
         arcOnString = self.otcArcOn + "," + self.otcPowerSourceNumber + "," + self.ArcOnWBPL.AS_Cond_file + "," + self.ArcOnWBPL.Retry + "," + \
         self.ArcOnWBPL.Characteristic_data_registration_number + "," + \
         self.ArcOnWBPL.Welding_process + "," + \
         self.ArcOnWBPL.Current_condition_type + "," + \
         self.ArcOnWBPL.Voltage_adjustment_method + "," + \
         self.ArcOnWBPL.Slope_condition_type + "," + \
         self.ArcOnWBPL.Welding_control_type + "," + \
            "0" + "," + \
         self.ArcOnWBPL.Cold_tandem + "," + \
         self.ArcOnWBPL.Robot_RS_file_number + "," + \
         self.ArcOnWBPL.Robot_operating_condition_number + "," + \
         self.ArcOnWBPL.Melt_adjustment + "," + \
         self.ArcOnWBPL.Welding_current + "," + \
         self.ArcOnWBPL.Welding_current_High + "," + \
         self.ArcOnWBPL.Welding_voltage + "," + \
         self.ArcOnWBPL.Welding_voltage_High + "," + \
         self.ArcOnWBPL.Welding_speed + "," + \
         self.ArcOnWBPL.Arc_characteristics_short + "," + \
         self.ArcOnWBPL.Arc_characteristics_short_High + "," + \
         self.ArcOnWBPL.Arc_characteristics_arc + "," + \
         self.ArcOnWBPL.Arc_characteristics_arc_High + \
            ",0,0,0,0,0,0,40,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",0,0,0,150,0,70,0"
      return arcOnString

   def OutputWBPLOff(self, operator: DULPythonDownloadOperator):
      """
      """
      logger = operator.GetLogOperator()

      if self.ArcOnInfo.OTC_WELD_OFF_PRGNR != "0":
         # add arc on instruction
         arcOffString = "%s %s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % \
                              (self.otcArcOff,self.otcPowerSourceNumber,self.ArcOnInfo.OTC_WELD_OFF_PRGNR)
         # arcOffString = "%s %s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % \
         #                      (self.otcArcOff,self.otcPowerSourceNumber,self.ArcOffWBPL.AE_Cond_file)
      else:
         # Set Current or Wire Feed mode
         if self.ArcOnInfo.OTC_CURRENT == 0:
            self.ArcOffWBPL.Voltage_adjustment_method = '0'
         else:
            self.ArcOffWBPL.Voltage_adjustment_method = '1'
         # format string
         arcOffString = self.otcArcOff + "," + self.otcPowerSourceNumber + "," + \
         self.ArcOffWBPL.AE_Cond_file + "," + \
         self.ArcOffWBPL.Version + "," + \
         self.ArcOffWBPL.Characteristic_data_registration + "," + \
         self.ArcOffWBPL.Welding_process + "," + \
         self.ArcOffWBPL.Current_condition_type + "," + \
         self.ArcOffWBPL.Voltage_adjustment_method + "," + \
         self.ArcOffWBPL.Slope_condition_type + "," + \
         self.ArcOffWBPL.Wire_retract + "," + \
         self.ArcOffWBPL.Welding_current + "," + \
         self.ArcOffWBPL.Crater_voltage + "," + \
         self.ArcOffWBPL.Crater_time + "," + \
         self.ArcOffWBPL.Post_flow_time + "," + \
         self.ArcOffWBPL.Pulse_arc_characteristic + "," + \
         self.ArcOffWBPL.Arc_characteristic_1_Short + "," + \
         self.ArcOffWBPL.Arc_characteristic_2_Arc + "," + \
            ",0,0,0,40,0,0,0,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",0,0,0,0,0,0,0,0,0,0" + \
            ",70,0,150,0,0,0,0,0,0,0" + \
            ",0,0,0,0,0"
      return arcOffString

   def OutputArcOnEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Daihen arc on command

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      logger = operator.GetLogOperator()

      # get all ArcOn attributes from event 
      try:
         arcOnStr = event.GetStringAttribute(self.OTC_ARCON_JSON, False).GetValue()
         #logger.LogInfo("~~~~~~~~~~~~~~~~~~~self.OTC_ARCON_JSON = " + str(arcOnStr))
      except:
         logger.LogError("Downloader Error: Can't access attribute: " + self.OTC_ARCON_JSON)
         logger.LogError("Downloader Error: Matching Daihen Arc Weld Technology plugin missing?")
      
      # ********************** DEBURRING **********************
      if self.OTCDeburringMethod == True:
         # ASSIG 1,0,2,0,999,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
         self.AddLineToSource("%s %s,0,2,0,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % (self.otcArcOn, self.otcPowerSourceNumber, format(self.OTCDeburringSpeed*1000, ".1f")))
         return
         # ============= no further on Deburring ==============
      
      # Convert JSON string back to JSON and fill class attributes
      data = json.loads(arcOnStr)
      for key, value in data.items():
         setattr(self.ArcOnInfo, key, value)

      if self.ArcOnInfo.OTC_STITCH_PULSE_ENABLED:
         # ASS 1,2,353,0,0.7,0.2,3.81,0,1,0,0,0,0,0,0,0,0,0,0,0.7,0,0,0,0
         self.AddLineToSource("ASS %s,2,%s,0,%s,%s,%s,%s,1,0,0,0,0,0,0.7,0,0,0,0,0,0,0,0,0" % (self.otcPowerSourceNumber, \
            self.ArcOnInfo.OTC_STITCH_PULSE_AS_COND, \
            self.ArcOnInfo.OTC_STITCH_PULSE_WELDING_TIME, \
            self.ArcOnInfo.OTC_STITCH_PULSE_COOLING_TIME, \
            self.ArcOnInfo.OTC_STITCH_PULSE_MOVEMENT_PITCH, \
            self.ArcOnInfo.OTC_STITCH_PULSE_MOVE_COND_NUMBER))
      elif "WPBL" in self.otcArcOn:
         self.AddLineToSource(self.OutputWBPLOn(operator))
      else:
         # todo: implement other power sources
         self.AddLineToSource(self.OutputWBPLOn(operator))
                  
      # check if weaving is enabled
      if self.ArcOnInfo.OTC_USE_WEAVE:
         # add weaving on instruction
         self.AddLineToSource("WFP 1,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % (self.ArcOnInfo.OTC_WEAVE_COND_NR))

         # Start arc tracking ST
         if self.ArcOnInfo.ArcSenseSt:
            self.AddLineToSource("ST %d,%d,%s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2" % (self.GroupRobot,self.ArcSensorId,self.ArcOnInfo.ArcSenseStCondFile,self.ArcOnInfo.ArcSenseStSampleData))

      # Output offset at End of weld
      if self.SeamFindingEndId != 0:
         # Activate SF3 Offset
         paraString = "%d,3,%d,1,0,0,0,0,0,0,0,0,1,1,0 'Activate Offset"  % \
                              (self.sf1P01MechanismNumber,self.SeamFindingEndId)
         sOutput = self.passSF3Params(paraString)
         self.AddLineToSource(sOutput)

         self.SeamFindingEndId = 0

      # Start seam tracking
      # if self.SeamCalibrationMethod == self.AW_SEAMTRACKING:
      if self.LaserTrackerOnOff:
         self.AddLineToSource("ZT %d,%d,1,%d,0,0,0,0,0,0,%d,%d,%d" % (self.GroupRobot,self.LaserSensorId,self.LaserZtGFF, self.LaserZtPosRegister,self.LaserZtPosture,self.LaserZtLSR))

   def OutputArcOffEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Set the current speed from speed event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """

      # ********************** DEBURRING **********************
      if self.OTCDeburringMethod == True:
         # ASSIG 1,0,2,0,999,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
         #self.AddLineToSource("AESIG 1,0,2,0,%d,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % (self.OTCDeburringSpeed))
         #self.AddLineToSource("%s %s,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % (self.otcArcOff, self.otcPowerSourceNumber))
         self.AddLineToSource("%s %s,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" % (self.otcArcOff, self.otcPowerSourceNumber))
         return
         # ============= no further on Deburring ==============
      
      # End arc tracking ET
      if self.ArcOnInfo.ArcSenseSt and self.ArcOnInfo.OTC_USE_WEAVE:
         self.AddLineToSource("ET %d,%d,%s,999,0,0,0,1,1,0" % (self.GroupRobot,self.ArcSensorId,self.ArcOnInfo.ArcSenseEtCondFile))

      # check if weaving is enabled
      if self.ArcOnInfo.OTC_USE_WEAVE:
         # add weaving off instruction
         self.AddLineToSource("WE 1")

      # Stop seam tracking
      # if self.SeamCalibrationMethod == self.AW_SEAMTRACKING:
      if self.LaserTrackerOnOff:
         self.AddLineToSource("ZE %d,1,1,%d,1,%d,0,%d,-1,0" % (self.GroupRobot,self.LaserZeStoreNumber,self.LaserZeStoreCoordinate, self.LaserZeOverDevRange))

      if self.ArcOnInfo.OTC_STITCH_PULSE_ENABLED:
         # AES 1,0,350
         self.AddLineToSource("AES %s,0,%s" % (self.otcPowerSourceNumber, self.ArcOnInfo.OTC_STITCH_PULSE_AE_COND))
      elif "WPBL" in self.otcArcOn:
         self.AddLineToSource(self.OutputWBPLOff(operator))
      else:
         # todo: implement other power sources
         self.AddLineToSource(self.OutputWBPLOff(operator))

   def OutputSeamTrackingEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Turn Seam tracker on if it's not on already

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """

      # check if tracker is already on
      if not self.LaserSensorIsOn:
         # add laser on instruction
         self.AddLineToSource("ZON 1,"+str(self.LaserSensorId))
         self.AddLineToSource("DELAY 4")
         self.LaserSensorIsOn = True
      if self.LaserZfOn:
         self.LaserTrackerZF = True


   def OutputSeamFindingEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Take a ZJ scan at the current position

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # get logger
      logger = operator.GetLogOperator()

      if not self.LaserSensorIsOn:
         # add laser on instruction
         self.AddLineToSource("ZON 1,"+str(self.LaserSensorId))
         self.AddLineToSource("DELAY 4")
         self.LaserSensorIsOn = True

      # Laser Tracker ZJ command
      if self.LaserTrackerZJ:
         # create motion group structure but skip non-Unit mechanisms
         motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
         motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

         robotJointTarget = ""
         joints = []
         for joint in motionGroupRobot.Joints:
            if robotJointTarget == "":
               robotJointTarget = "(" + str(round(joint.Value, 2))
               joints.append(joint.Value)
            else:
               robotJointTarget = robotJointTarget + ", " + ("%.2f" % joint.Value)
               joints.append(joint.Value)
         robotJointTarget = robotJointTarget + ")"

         zjPulseString, zjPulseValue0 = self.SetZJPulseString(joints)
      
         self.LaserZjStoreNumber = self.SeamFindingId
         
         # ----------------------------------------------
         self.ZJCycleParams = ZJCycleParams()
         self.ZJCycleParams.zjSensor = self.LaserSensorId
         self.ZJCycleParams.zjMechanism = 1
         self.ZJCycleParams.zjDEV = self.LaserZjStoreNumber
         self.ZJCycleParams.zjGAP = self.LaserZjGAP
         self.ZJCycleParams.zjGFF = self.LaserZjGFF
         self.ZJCycleParams.zjStoreCoordinates = self.GetZjStoreCoordIdx(self.LaserZjStoreCoordinates)  # ["World", "Tool", "Machine"]
         self.ZJCycleParams.zjDevComposition = self.LaserZjDevComposition
         self.ZJCycleParams.zjAutoManualModify = self.LaserZjAutoManualModify
         self.ZJCycleParams.zjBasePointMemory = False
         self.ZJCycleParams.zjSearchWaitDelay = self.LaserZjSearchWaitDelay
         self.ZJCycleParams.zjSearchStableDelay = self.LaserZjSearchStableDelay
         self.ZJCycleParams.zjStoreNumber = self.LaserZjStoreNumber
         self.ZJCycleParams.zjBasePositionX = 0.0
         self.ZJCycleParams.zjBasePositionY = self.LaserZjBasePositionY
         self.ZJCycleParams.zjBasePositionZ = self.LaserZjBasePositionZ
         self.ZJCycleParams.zjDeviationLength = self.LaserZjDeviationLength
         self.ZJCycleParams.zjGapWatchRangeMax = self.LaserZjGapWatchRangeMax
         self.ZJCycleParams.zjGapWatchRangeMin = self.LaserZjGapWatchRangeMin
         self.ZJCycleParams.zjMinDepthValue = self.LaserZjMinDepthValue
         self.ZJCycleParams.zjAngleOneRangeMax = self.LaserZjAngleOneRangeMax
         self.ZJCycleParams.zjAngleOneRangeMin = self.LaserZjAngleOneRangeMin
         self.ZJCycleParams.zjAngleTwoRangeMax = self.LaserZjAngleTwoRangeMax
         self.ZJCycleParams.zjAngleTwoRangeMin = self.LaserZjAngleTwoRangeMin
         self.ZJCycleParams.zjPulseString = zjPulseString
         zjBaseOffset = '%s,%s,%s' % (self.formatDbl(self.ZJCycleParams.zjBasePositionX*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionY*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionZ*1000))
         self.ZJCycleParams.zjBaseOffset = zjBaseOffset
         self.ZJCycleParams.zjPulseValue = zjPulseValue0
         cycleString = self.OutputZJCycle(self.ZJCycleParams)
         self.AddLineToSource(cycleString)
         # ----------------------------------------------

         self.LaserTrackerZJ = False
   
   def formatDbl(self, value):
      rounded = round(value, 3)
      formatted = f"{rounded:.3f}".rstrip('0').rstrip('.')
      if '.' not in formatted:
         formatted += '.0'
      return formatted

   def GetZjStoreCoordIdx(self, type):
      if type == "Machine":
         return 1
      if type == "Base":
         return 6
      if type == "Tool":
         return 2
      if type == "User":
         return 3
      if type == "World":
         return 4
      if type == "Work":
         return 5
      return 1
   
   def GetSF3SectionIdx(self, type):
      # ["Start", "End", "All End"]
      if type == "Start":
         return 0
      if type == "End":
         return 1
      if type == "All End":
         return 2
      return 0
   
   def GetSF3ShiftMethodIdx(self, type):
      # ["DEV.file", "Num.Input", "Man.Operation"]
      if type == "DEV.file":
         return 0
      if type == "Num.Input":
         return 1
      if type == "Man.Operation":
         return 2
      return 0
      
   def GetSF8StoringDirectionIdx(self, type):
      # ["Register->File", "File->Register"]
      if type == "Register->File":
         return 0
      if type == "File->Register":
         return 1
      return 0

   def GetSF8RegisterIdx(self, type):
      # ["Local", "Global"]
      if type == "Local":
         return 0
      if type == "Global":
         return 1
      return 0      

   def GetSF8BaseCoordSystemIdx(self, type):
      # ["Machine", "Tool", "World", "Work", "User"]
      if type == "Machine":
         return 1
      if type == "Tool":
         return 2
      if type == "World":
         return 4
      if type == "Work":
         return 5
      if type == "User":
         return 3
      return 0      
   
   def OutputSeamTrackingOffEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Search for end point ZN

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """

      # Add ZN endpoint search
      if self.LaserZnOn:
         # add ZN instruction
         self.AddLineToSource("ZN %d,%d,1,%d,1,0,%d,%d,0,I0,0,%d" % \
                              (self.GroupRobot,self.LaserSensorId,self.LaserZnGFF,self.LaserZnOffset,self.LaserZnSearchRange,self.LaserZnLSR))

   def OutputSeamTrackerOffEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Turn laser tracker and SF3 offset off after retract

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """

      if self.LaserZjOn:
         # Activate SF3 Offset
         paraString = "%d,1,%d,2,0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1,1,0 'Deactivate Offset"  % \
                              (self.sf1P01MechanismNumber,self.LaserZjStoreNumber)
         sOutput = self.passSF3Params(paraString)
         self.AddLineToSource(sOutput)

         self.LaserZjOn = False

      self.AddLineToSource("ZOF 1,"+str(self.LaserSensorId))
      self.LaserSensorIsOn = False

   # -------------------------------------------------------------------------------------------------------------------
   def OutputManualZJEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """
      Outputs the manual set ZJEvent

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)
      joints = []
      for joint in motionGroupRobot.Joints:
         joints.append(joint.Value)

      zjPulseString, zjPulseValue0 = self.SetZJPulseString(joints)
      
      # ----------------------------------------------
      self.ZJCycleParams = ZJCycleParams()
      self.ZJCycleParams.zjSensor = event.GetIntegerAttribute('LaserZjEvtSensorNr', True).GetValue()
      self.ZJCycleParams.zjMechanism = event.GetIntegerAttribute('LaserZjEvtMechanismNr', True).GetValue()
      self.ZJCycleParams.zjDEV = event.GetIntegerAttribute('LaserZjEvtDEV', True).GetValue()
      self.ZJCycleParams.zjGAP = event.GetIntegerAttribute('LaserZjEvtGAP', True).GetValue()
      self.ZJCycleParams.zjGFF = event.GetIntegerAttribute('LaserZjEvtGFF', True).GetValue() 
      self.ZJCycleParams.zjStoreCoordinates = self.GetZjStoreCoordIdx(event.GetLiteralAttribute('LaserZjEvtStoreCoordinates', True).GetValue())  # ["World", "Tool", "Machine"]
      self.ZJCycleParams.zjDevComposition = event.GetBoolAttribute('LaserZjEvtDevComposition', True).GetValue()
      self.ZJCycleParams.zjAutoManualModify = event.GetBoolAttribute('LaserZjEvtAutoManualModify', True).GetValue()
      self.ZJCycleParams.zjBasePointMemory = event.GetBoolAttribute('LaserZjBasePointMemory', True).GetValue()
      self.ZJCycleParams.zjSearchWaitDelay = event.GetDoubleAttribute('LaserZjEvtSearchWaitDelay', True).GetValue()
      self.ZJCycleParams.zjSearchStableDelay = event.GetDoubleAttribute('LaserZjEvtSearchStableDelay', True).GetValue()
      self.ZJCycleParams.zjStoreNumber = event.GetIntegerAttribute('LaserZjEvtStoreNumber', True).GetValue()
      self.ZJCycleParams.zjBasePositionX = event.GetDoubleAttribute('LaserZjEvtBasePositionX', True).GetValue()
      self.ZJCycleParams.zjBasePositionY = event.GetDoubleAttribute('LaserZjEvtBasePositionY', True).GetValue()
      self.ZJCycleParams.zjBasePositionZ = event.GetDoubleAttribute('LaserZjEvtBasePositionZ', True).GetValue()
      self.ZJCycleParams.zjDeviationLength = event.GetDoubleAttribute('LaserZjEvtDeviationLength', True).GetValue()
      self.ZJCycleParams.zjGapWatchRangeMax = event.GetDoubleAttribute('LaserZjEvtGapWatchRangeMax', True).GetValue()
      self.ZJCycleParams.zjGapWatchRangeMin = event.GetDoubleAttribute('LaserZjEvtGapWatchRangeMin', True).GetValue()
      self.ZJCycleParams.zjMinDepthValue = event.GetDoubleAttribute('LaserZjEvtMinDepthValue', True).GetValue()
      self.ZJCycleParams.zjAngleOneRangeMax = event.GetDoubleAttribute('LaserZjEvtAngleOneRangeMax', True).GetValue()
      self.ZJCycleParams.zjAngleOneRangeMin = event.GetDoubleAttribute('LaserZjEvtAngleOneRangeMin', True).GetValue()  
      self.ZJCycleParams.zjAngleTwoRangeMax = event.GetDoubleAttribute('LaserZjEvtAngleTwoRangeMax', True).GetValue()
      self.ZJCycleParams.zjAngleTwoRangeMin = event.GetDoubleAttribute('LaserZjEvtAngleTwoRangeMin', True).GetValue()
      self.ZJCycleParams.zjPulseString = zjPulseString
      zjBaseOffset = '%s,%s,%s' % (self.formatDbl(self.ZJCycleParams.zjBasePositionX*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionY*1000), self.formatDbl(self.ZJCycleParams.zjBasePositionZ*1000))
      self.ZJCycleParams.zjBaseOffset = zjBaseOffset
      self.ZJCycleParams.zjPulseValue = zjPulseValue0
      cycleString = self.OutputZJCycle(self.ZJCycleParams)
      self.AddLineToSource(cycleString)
      # -------------------------------------------------------------------------------------------------------------------------------
      # #                         1         5     7          11 12 13    15 16 17 18 19 20 21 22 28 34 37    40 43 44     46  47 48 49
      # self.AddLineToSource("ZJ %d,%d,4,2,%d,%d,%d,%d,%d,%d,%s,%s,%d,-1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0,0,%s,9,2000,0,200,%s,%s,0" % \
      

   # -------------------------------------------------------------------------------------------------------------------
   def passSF3Params(self, inputString):
      paramList = SF3CycleParams()
      numeric_part, text_part = inputString.split(" '", 1)
      numbers = list(map(float, numeric_part.split(',')))
      text = text_part.strip()
      paramList.sf3MechanismNr = numbers[0]             # P01
      paramList.sf3VersionNr = numbers[1]               # P02
      paramList.sf3CallNr = numbers[2]                  # P03
      paramList.sf3Section = numbers[3]                 # P04
      paramList.sf3PostureCalling = numbers[4]          # P05
      paramList.sf3DEVFileOffsetX = numbers[5]          # P06
      paramList.sf3DEVFileOffsetY = numbers[6]          # P07
      paramList.sf3DEVFileOffsetZ = numbers[7]          # P08
      paramList.sf3NumericalShiftDistanceX = numbers[8] # P09
      paramList.sf3NumericalShiftDistanceY = numbers[9] # P10
      paramList.sf3NumericalShiftDistanceZ = numbers[10] # P11
      paramList.sf3ShiftMethod = numbers[11]             # P12
      paramList.sf3BaseCoordSystem = numbers[12]         # P13
      paramList.sf3BCSUser = numbers[13]                 # P14
      paramList.sf3Comment = text                      # Comment
      cycleString = self.OutputSF3Cycle(paramList)
      return cycleString
   # -------------------------------------------------------------------------------------------------------------------
   def OutputManualSF3Event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """
      Outputs the manual set SF3Event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      self.SF3CycleParams = SF3CycleParams()
      self.SF3CycleParams.sf3MechanismNr = event.GetIntegerAttribute('LaserSF3EvtMechanismNr', True).GetValue()
      self.SF3CycleParams.sf3VersionNr = event.GetIntegerAttribute('LaserSF3EvtVersionNr', True).GetValue()
      self.SF3CycleParams.sf3Section = self.GetSF3SectionIdx(event.GetLiteralAttribute('LaserSF3EvtSection', True).GetValue())  # ["Start", "End", "All End"]
      self.SF3CycleParams.sf3ShiftMethod = self.GetSF3ShiftMethodIdx(event.GetLiteralAttribute('LaserSF3EvtShiftMethod', True).GetValue())  # ["DEV.file"]
      self.SF3CycleParams.sf3CallNr = event.GetIntegerAttribute('LaserSF3EvtCallNr', True).GetValue()
      self.SF3CycleParams.sf3PostureCalling = event.GetBoolAttribute('LaserSF3EvtPostureCalling', True).GetValue()
      self.SF3CycleParams.sf3BaseCoordSystem = self.GetZjStoreCoordIdx(event.GetLiteralAttribute('LaserSF3EvtBaseCoordSystem', True).GetValue())  # ["Machine", "Tool", "World", "Work", "User"]
      self.SF3CycleParams.sf3BCSUser = event.GetIntegerAttribute('LaserSF3EvtBCSUser', True).GetValue()
      self.SF3CycleParams.sf3DEVFileOffsetX = event.GetDoubleAttribute('LaserSF3EvtDEVFileOffsetX', True).GetValue()
      self.SF3CycleParams.sf3DEVFileOffsetY = event.GetDoubleAttribute('LaserSF3EvtDEVFileOffsetY', True).GetValue()
      self.SF3CycleParams.sf3DEVFileOffsetZ = event.GetDoubleAttribute('LaserSF3EvtDEVFileOffsetZ', True).GetValue()
      self.SF3CycleParams.sf3NumericalShiftDistanceX = event.GetDoubleAttribute('LaserSF3EvtNumericalShiftDistanceX', True).GetValue()
      self.SF3CycleParams.sf3NumericalShiftDistanceY = event.GetDoubleAttribute('LaserSF3EvtNumericalShiftDistanceY', True).GetValue()
      self.SF3CycleParams.sf3NumericalShiftDistanceZ = event.GetDoubleAttribute('LaserSF3EvtNumericalShiftDistanceZ', True).GetValue()
      self.SF3CycleParams.sf3MainDEVNr = event.GetStringAttribute('LaserSF3EvtMainDEVNr', True).GetValue()
      self.SF3CycleParams.sf3AuxiliaryDEVNr1 = event.GetStringAttribute('LaserSF3EvtAuxiliaryDEVNr1', True).GetValue()
      self.SF3CycleParams.sf3AuxiliaryDEVNr2 = event.GetStringAttribute('LaserSF3EvtAuxiliaryDEVNr2', True).GetValue()
      self.SF3CycleParams.sf3AuxiliaryDEVNr3 = event.GetStringAttribute('LaserSF3EvtAuxiliaryDEVNr3', True).GetValue()
      self.SF3CycleParams.sf3Comment = 'Offset-Event'
      cycleString = self.OutputSF3Cycle(self.SF3CycleParams)
      self.AddLineToSource(cycleString)
      # ----------------------------------------------------------------------------------------
      #                            1  2  3  4  5  6  7  8  9 10 11 12    14 15
      # self.AddLineToSource("SF3 %d,%d,%d,%d,%d,%s,%s,%s,%s,%s,%s,%d,%d,%d,0 'Offset-Event"  % \
   
   
   # -------------------------------------------------------------------------------------------------------------------
   def passSF4Params(self, inputString):
      paramList = SF4CycleParams()
      numeric_part, text_part = inputString.split(" '", 1)
      numbers = list(map(float, numeric_part.split(',')))
      text = text_part.strip()
      paramList.sf4VersionNr   = numbers[0]     # P01
      paramList.sf4DevFileOne  = numbers[1]     # P02
      paramList.sf4RateOne     = numbers[2]     # P03
      paramList.sf4DevFileTwo  = numbers[3]     # P04
      paramList.sf4RateTwo     = numbers[4]     # P05
      paramList.sf4DevFileThree= numbers[5]     # P06
      paramList.sf4RateThree   = numbers[6]     # P07
      paramList.sf4DevStoreNr  = numbers[7]     # P08
      paramList.sf4Comment     = text           # PComment
      cycleString = self.OutputSF4Cycle(paramList)
      return cycleString
   # -------------------------------------------------------------------------------------------------------------------
   def OutputManualSF4Event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """
      Outputs the manual set SF4Event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      self.SF4CycleParams = SF4CycleParams()
      self.SF4CycleParams.sf4VersionNr = event.GetIntegerAttribute('LaserSF4EvtVersionNr', True).GetValue()
      self.SF4CycleParams.sf4DevFileOne = event.GetIntegerAttribute('LaserSF4EvtDevFileOne', True).GetValue()
      self.SF4CycleParams.sf4RateOne = event.GetIntegerAttribute('LaserSF4EvtRateOne', True).GetValue()
      self.SF4CycleParams.sf4DevFileTwo = event.GetIntegerAttribute('LaserSF4EvtDevFileTwo', True).GetValue()
      self.SF4CycleParams.sf4RateTwo = event.GetIntegerAttribute('LaserSF4EvtRateTwo', True).GetValue()
      self.SF4CycleParams.sf4DevFileThree = event.GetIntegerAttribute('LaserSF4EvtDevFileThree', True).GetValue()
      self.SF4CycleParams.sf4RateThree = event.GetIntegerAttribute('LaserSF4EvtRateThree', True).GetValue()
      self.SF4CycleParams.sf4DevStoreNr = event.GetIntegerAttribute('LaserSF4EvtDevStoreNr', True).GetValue()
      self.SF4CycleParams.sf4Comment = 'Calculate Offset-Event'
      cycleString = self.OutputSF4Cycle(self.SF4CycleParams)
      self.AddLineToSource(cycleString)
      # ----------------------------------------------------------------------------------------
      #                            1  2  3  4  5  6  7  8
      # self.AddLineToSource("SF4 %d,%d,%d,%d,%d,%d,%d,%d 'Calculate Offset-Event"  % \
      
      
         # -------------------------------------------------------------------------------------------------------------------
   def OutputManualSF8Event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """
      Outputs the manual set SF8Event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      sf8EvtStoringDirection = event.GetLiteralAttribute('LaserSF8EvtStoringDirection', True).GetValue() # ["Register->File", "File->Register"]      
      sf8EvtRegister = event.GetLiteralAttribute('LaserSF8EvtRegister', True).GetValue() # ["Local", "Global"]
      sf8EvtNo = event.GetIntegerAttribute('LaserSF8EvtNo', True).GetValue()
      sf8EvtCallNr = event.GetIntegerAttribute('LaserSF8EvtCallNr', True).GetValue()
      sf8EvtMechanismNr = event.GetIntegerAttribute('LaserSF8EvtMechanismNr', True).GetValue()
      sf8EvtBaseCoordSystem = event.GetLiteralAttribute('LaserSF8EvtBaseCoordSystem', True).GetValue()  # ["Machine", "Tool", "World", "Work", "User"]
      sf8EvtPostureDeviation = event.GetBoolAttribute('LaserSF8EvtPostureDeviation', True).GetValue()
      sf8EvtPositionMax = event.GetDoubleAttribute('LaserSF8EvtPositionMax', True).GetValue()
      sf8EvtPositionMin = event.GetDoubleAttribute('LaserSF8EvtPositionMin', True).GetValue()
      sf8EvtPostureMax = event.GetDoubleAttribute('LaserSF8EvtPostureMax', True).GetValue()
      sf8EvtPostureMin = event.GetDoubleAttribute('LaserSF8EvtPostureMin', True).GetValue()
      
      #                              1               -1
      #                            1 2  3  4  5  6  7 8  9  10 11 12 13
      # self.AddLineToSource("SF8 %d,1,%d,%d,%d,%d,%d,-1,%d,%s,%s,%s,%s"  % \
      self.AddLineToSource("SF8 %d,1,%s,%s,%d,%d,%s,-1,%d,%s,%s,%s,%s" % (
      sf8EvtMechanismNr,  #P1 \
      # sf8EvtStoringDirection,  #P3 \
      self.GetSF8StoringDirectionIdx(sf8EvtStoringDirection), #P3 \
      # sf8EvtRegister,  #P4 \
      self.GetSF8RegisterIdx(sf8EvtRegister), #P4 \
      sf8EvtNo,  #P5 \
      sf8EvtCallNr, #P6 \
      # sf8EvtBaseCoordSystem,  #P7 \
      self.GetSF8BaseCoordSystemIdx(sf8EvtBaseCoordSystem),  #P7 \
      sf8EvtPostureDeviation,  #P9 \
      self.formatDbl(sf8EvtPositionMax*1000),  #P10 \
      self.formatDbl(sf8EvtPositionMin*1000),  #P11 \
      sf8EvtPostureMax,  #P12 \
      sf8EvtPostureMin,  #P13 \
      ))
      iDummy = 0

   # -------------------------------------------------------------------------------------------------------------------
   def OutputZJCycle(self, paramList: ZJCycleParams):
      """
      Outputs the manual set ZJEvent

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      cycleString = ("ZJ %d,%d,4,2,%d,%d,%d,%d,%d,%d,%s,%s,%d,-1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0,0,%s,9,2000,0,200,%s,%s,0" % \
      (paramList.zjSensor, #P1 \
      paramList.zjMechanism, #P2 \
      paramList.zjGFF,  #P5 \
      paramList.zjDEV,  #P6 \
      paramList.zjGAP,  #P7 \
      paramList.zjDevComposition,  #P8 Bool \
      paramList.zjAutoManualModify,  #P9 Bool \
      paramList.zjBasePointMemory,  #P10 Bool \
      self.formatDbl(paramList.zjSearchWaitDelay),  #P11 \
      self.formatDbl(paramList.zjSearchStableDelay),  #P12 \
      paramList.zjStoreCoordinates,  #P13 \
      self.formatDbl(paramList.zjDeviationLength*1000),  #P15 \
      self.formatDbl(paramList.zjGapWatchRangeMax*1000*10),  #P16 \
      self.formatDbl(paramList.zjGapWatchRangeMin*1000*10),  #P17 \
      self.formatDbl(paramList.zjAngleOneRangeMax*1.0*100),  #P18 ? \
      self.formatDbl(paramList.zjAngleOneRangeMin*1.0*100),  #P19 ? \
      self.formatDbl(paramList.zjAngleTwoRangeMax*1.0*100),  #P20 ? \
      self.formatDbl(paramList.zjAngleTwoRangeMin*1.0*100),  #P21 ? \
      paramList.zjPulseString,paramList.zjPulseString, #P22-27-33 TeachPos6,BasePos6 \
      paramList.zjBaseOffset,paramList.zjBaseOffset, #P34-39 ReplyPos3+3 \
      paramList.zjPulseValue,paramList.zjPulseValue)) #P40-42 BasePos
      
      return cycleString
   
   # -------------------------------------------------------------------------------------------------------------------
   def OutputSF3Cycle(self, paramList: SF3CycleParams):
      """
      Outputs the manual set SF3Event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      cycleString = "SF3"
      #                    1  2  3  4  5  6  7  8  9 10 11 12    14 15
      cycleString = ("SF3 %d,%d,%d,%d,%d,%s,%s,%s,%s,%s,%s,%d,%d,%d,0 '%s"  % \
      (paramList.sf3MechanismNr,  # P1\
      paramList.sf3VersionNr,  # P2\
      paramList.sf3CallNr,  # P3\
      paramList.sf3Section,  # P4\
      paramList.sf3PostureCalling,  # P5\
      self.formatDbl(paramList.sf3DEVFileOffsetX*1000),  #P6 \
      self.formatDbl(paramList.sf3DEVFileOffsetY*1000),  #P7 \
      self.formatDbl(paramList.sf3DEVFileOffsetZ*1000),  #P8 \
      self.formatDbl(paramList.sf3NumericalShiftDistanceX*1.000),  #P9 \
      self.formatDbl(paramList.sf3NumericalShiftDistanceY*1.000),  #P10 \
      self.formatDbl(paramList.sf3NumericalShiftDistanceZ*1.000),  #P11 \
      paramList.sf3ShiftMethod,  # P12\
      paramList.sf3BaseCoordSystem,  #P13 \
      paramList.sf3BCSUser,  # P14 \
      paramList.sf3Comment
      ))
      return cycleString
   
   # -------------------------------------------------------------------------------------------------------------------
   def OutputSF4Cycle(self, paramList: SF4CycleParams):
      """
      Outputs the manual set SF4Event

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      cycleString = ("SF4 %d,%d,%d,%d,%d,%d,%d,%d '%s"  % \
      (paramList.sf4VersionNr,  # P01 \
      paramList.sf4DevFileOne,  # P02 \
      paramList.sf4RateOne,     # P03 \
      paramList.sf4DevFileTwo,  # P04 \
      paramList.sf4RateTwo,     # P05 \
      paramList.sf4DevFileThree,  # P06 \
      paramList.sf4RateThree,     # P07 \
      paramList.sf4DevStoreNr,  # P08 \
      paramList.sf4Comment))
      
      return cycleString
   
#################### HELPER ####################
   def GettingZJPulseValues(self):
      """Getting all related Pulse Values for calculating ZJ-Encoder Values
         zjStdPosAngleValues, zjPulseConstantValues, zjStdPosEncoderValues = self.GettingZJPulseValues()
         Return : str, str, str : StdPosAngleValues, PulseConstantValues, StdPosEncoderValues
      """
      
      if self.CENOlpJointStdPosAngleValues == '':
         self.LoggingAW.LogError("ZJ Laser Search command is missing attribute CENOlpJointZeroOffsetValues/StdPosAngleValues. Check Downloader documentation for detail")
      else:
         zjStdPosAngleValues = [float(x) for x in self.CENOlpJointStdPosAngleValues.split(';')]
      
      if self.CENOlpJointPulseConstantValues == '':
         self.LoggingAW.LogError("ZJ Laser Search command is missing attribute CENOlpJointStepFactorValues/PulseConstantValues. Check Downloader documentation for detail")
      else:
         zjPulseConstantValues = [float(x) for x in self.CENOlpJointPulseConstantValues.split(';')]

      if self.CENOlpJointStdPosEncoderValues == '':
         self.LoggingAW.LogError("ZJ Laser Search command is missing attribute CENOlpJointStdPosEncoderValues/StdPosEncoderValues. Check Downloader documentation for detail")
      else:
         zjStdPosEncoderValues = [float(x) for x in self.CENOlpJointStdPosEncoderValues.split(';')]
      
      if self.CENOlpJoint56CouplingFactor == 0.0:
            self.LoggingAW.LogError("ZJ Laser Search command is missing attribute CENOlpJoint56CouplingFactor/LinkCoefInv6Factor. Check Downloader documentation for detail")

      return zjStdPosAngleValues, zjPulseConstantValues, zjStdPosEncoderValues
   
   def SetZJPulseString(self, joints):
      """Setting the Pulse String for ZJ Cycle
      zjPulseString, zjPulseValue0 = self.SetZJPulseString(joints)
      Return : str, str : zjPulseString, zjPulseValues[0]
      """
      # getting all the Pulse Encoder Values
      zjZeroOffsets, zjPulseFactors, zjEncoderValues = self.GettingZJPulseValues()

      # if joints[0] > 9.99 and joints[0] < 10.01:
      #     joints = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
      # self.LoggingAW.LogInfo("==============  SetZJPulseString  =================")
      # self.LoggingAW.LogInfo("..................... zjZeroOffsets = " + str(zjZeroOffsets))
      # self.LoggingAW.LogInfo("..................... zjPulseFactors = " + str(zjPulseFactors))
      # self.LoggingAW.LogInfo("..................... zjEncoderValues = " + str(zjEncoderValues))
      # self.LoggingAW.LogInfo("..................... joints = " + str(joints))

      # calculate Values
      zjPulseValues = []
      for i in range(6):
         if i == 5:
            val = ( ((joints[i] * DEGTORAD) - (zjZeroOffsets[i] * DEGTORAD)) + (((joints[i-1] * DEGTORAD) - (zjZeroOffsets[i-1] * DEGTORAD)) * self.CENOlpJoint56CouplingFactor) ) * zjPulseFactors[i]
         else:
            val = ((joints[i] * DEGTORAD) - (zjZeroOffsets[i] * DEGTORAD)) * zjPulseFactors[i]
         zjPulseValues.append(str(round(zjEncoderValues[i] + val )))
      # writing the String
      zjPulseString = ''
      for i in range(6):
         zjPulseString = zjPulseString + zjPulseValues[i] + ','
      zjPulseString = zjPulseString[:-1]  # cut last Comma

      # self.LoggingAW.LogInfo("-------- PulseString = " + str(zjPulseString))
      # self.LoggingAW.LogInfo("===================================================\n")

      return zjPulseString, zjPulseValues[0]
   

   def OutputTouchSensingE2(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Create touch sensing motion

      Target Output:
      SF1 1,1,4,2,1,0,0,7.0,80.0,0.0,15.0,1,-1,MOVEX,M1X,(614.89, 347.00, 1812.81, -90.00, 45.00, -0.00),1,11,1,-1,-0.55,0,0,0,0,0,0,0,0,0,0,0,0,0,0
      SF4 1,1,100,0,100,0,100,501 'Calculate  Offset
      SF3 1,2,501,1,0,0.000000,0.000000,0.000000,0.0,0.0,0.0,0.0,1,1,0 'Activate Offset

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
      #self.AddLineToSource('  SKIP CONDITION %s[%d]=ON' % (self.TouchSensingInputSignalType, self.TouchSensingInput))

      # handle each MOTION of the event
      for motion in motions:

         # check for build-in events like speed, accuracy, ...
         eventsBefore = motion.GetEventsBefore()
         for eventBefore in eventsBefore:
            # handle speed accuracy, ...
            self.HandleBuildInEvents(operator, eventBefore)

            # handle TOUCH sensing start APPROACH point
            if eventBefore.GetName() == 'TouchPointStartAppEvent':
               self.HandleSourceSection(operator, motion)

            # handle COLLISION point
            if eventBefore.GetName() == 'TouchPointCollisionEvent':
               #self.HandleSourceSection(operator, motion)
               # create motion group structure but skip non-Unit mechanisms
               motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
               motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)

               targetType = "M1X"
               frstJnt = "-0.55"
               #self.LoggingAW.LogInfo("...........................motionGroupRobot.Joints=" + str(nrJnts))
               #frstJnt = str(round(motionGroupRobot.Joints[0].Value, 2))
               #frstJnt = str(round(motionGroupRobot.X, 2))
               #self.LoggingAW.LogInfo("...........................motionGroupRobot.X=" + str(round(motionGroupRobot.X, 2)))
               nrJnts = len(motionGroupRobot.Joints)
               if nrJnts == 7:
                  frstJnt = str(round(motionGroupRobot.Joints[0].Value, 2))
                  #self.LoggingAW.LogInfo("...........................motionGroupRobot.Joint=" + str(frstJnt))
               if self.DownloadJointsOnly == True and nrJnts == 7:
                  targetType = "M1J"

               # write collision point coordinates to position register
               self.AddLineToSource('SF1 %d,%d,%d,%d,%d,%d,%d,%.3f,%d,%d,%d,%d,%d,MOVEX,%s,%s,1,11,1,-1,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0' % \
                                    (self.sf1P01MechanismNumber,self.sf1P02StoreNumber,self.sf1P03IndexStoreCoord,\
                                    self.st1P04Dummy,self.sf1P05TouchId,self.sf1P06DeviationComposition,\
                                    self.sf1P07TouchLogic,self.TouchSensingSpeed/27,self.sf1P09SearchRangeMax,\
                                    self.sf1P10SearchRangeMin,self.sf1P11OverDeviationRange,self.sf1P12IndexStoreCoordinate,\
                                    self.sf1P13Dummy, targetType, motionGroupRobot.TargetOutput, frstJnt))
               temp = '_______TouchPointCollisionEvent : %d,%d,%d,%d,%d,%d,%d,%.3f,%d,%d,%d,%d,%d,%s' % \
                                    (self.sf1P01MechanismNumber,self.sf1P02StoreNumber,self.sf1P03IndexStoreCoord,\
                                    self.st1P04Dummy,self.sf1P05TouchId,self.sf1P06DeviationComposition,\
                                    self.sf1P07TouchLogic,self.TouchSensingSpeed/27,self.sf1P09SearchRangeMax,\
                                    self.sf1P10SearchRangeMin,self.sf1P11OverDeviationRange,self.sf1P12IndexStoreCoordinate,\
                                    self.sf1P13Dummy,motionGroupRobot.TargetOutput)
               self.DevLoggingAW(temp)
               # Clear list for new TouchID - up to 3 touches per TouchIdPositionRegister can be combined
               if self.ResetTouchSensingOffset:
                  self.SequenceList = [0,0,0]
                  self.ResetTouchSensingOffset = False

               # Store current sf1P05TouchId to be combined into TouchIdPositionRegister
               temp = '_______self.SequenceList[' + str(self.TouchSensingSequencingCounter-1) + '] = ' + str(self.sf1P05TouchId)
               self.DevLoggingAW(temp)
               if self.TouchSensingSequencingCounter > 3:
                  logger.LogError('More than three Touch sensing operations detected for the same Touch ID (' + str(self.TouchIdPositionRegister) + '). Operation will be ignored. Please analyse the program.')
               else:
                  self.SequenceList[self.TouchSensingSequencingCounter-1] = self.sf1P05TouchId
               
               # Activate SF4 Calculation
               paraString = "%d,%d,%d,%d,%d,%d,%d,%d 'Calculate Offset"  % \
                                    (self.sf1P01MechanismNumber,self.SequenceList[0],\
                                    self.sf4P3Ratio1,self.SequenceList[1],self.sf4P5Ratio2,\
                                    self.SequenceList[2],self.sf4P7Ratio3,self.TouchIdPositionRegister)
               sOutput = self.passSF4Params(paraString)
               self.AddLineToSource(sOutput)
               
               # Activate SF3 Offset
               paraString = "%d,2,%d,%d,%d,%d,%d,%d,0.0,0.0,0.0,0.0,1,1,0 'Activate Offset"  % \
                                    (self.sf1P01MechanismNumber,self.TouchIdPositionRegister,\
                                    self.sf3P04Section,self.sf3P05PostureCall0,self.sf3P06OffsetX,\
                                    self.sf3P07OffsetY,self.sf3P08OffsetZ)
               sOutput = self.passSF3Params(paraString)
               self.AddLineToSource(sOutput)

               self.sf3Flag = True
               self.sf3TouchId = self.TouchIdPositionRegister
 
               # self.AddLineToSource('  PR[%d]=P[%d]' % (self.TouchCollisionPointPositionRegister, self.PointCounter))
               # call touch sensing macro
               # self.AddLineToSource('  CALL %s(%d,%d,%d)' % (self.TouchPointStartAppPositionRegister, self.TouchCollisionPointPositionRegister, self.TouchIdPositionRegister, self.ResetTouchSensingOffset))

            # handle TOUCH sensing start RETRACT point
            if eventBefore.GetName() == 'TouchPointStartRetEvent':
               self.HandleSourceSection(operator, motion)

         # check for build-in events like speed, accuracy, ...
         eventsAfter = motion.GetEventsAfter()
         for eventAfter in eventsAfter:
            self.HandleBuildInEvents(operator, eventAfter)

   def OutputEnableTouchOffsetForWelding(self, operator: DULPythonDownloadOperator, positionRegisterNumber: int):
      """Enables new touch offset for welding
      SF3 1,2,501,2,0,0.000000,0.000000,0.000000,0.0,0.0,0.0,0.0,1,1,0 'Cancel Deviations

      Args:
         operator: Download operator gives access to the complete program, controller and resources
         positionRegisterNumber: number of position register with calculated touch offset
      """
      # add string at the end of the current source line
      # Activate SF3 Offset
      paraString = "%d,2,%d,%d,%d,%d,%d,%d,0.0,0.0,0.0,0.0,1,1,0 'Activate Offset"  % \
                           (self.sf1P01MechanismNumber,positionRegisterNumber,\
                           self.sf3P04Section,self.sf3P05PostureCall0,self.sf3P06OffsetX,\
                           self.sf3P07OffsetY,self.sf3P08OffsetZ)
      sOutput = self.passSF3Params(paraString)
      self.AddLineToSource(sOutput)

      self.sf3EventActivated = True

   def OutputUploadedTouchSensingEvent(self, operator, currentMotion, event):
      """
      Output an uploaded Touchsensing Motion
      """
      # get all attributes from event
      attributes = event.GetAttributes()
      # iterate through attribute list
      for attribute in attributes:
         # touch ID
         if attribute.GetName() == "IsTouchSensingMotion":
            isTSMotion = attribute.GetValue()
         # is the touch ID for the next via point
         if attribute.GetName() == "PreParameters":
            preParameters = attribute.GetValue()
         # how much touch operations does belong together
         if attribute.GetName() == "PostParameters":
            postParameters = attribute.GetValue()
      
      if isTSMotion == True:
         
         # create motion group structure but skip non-Unit mechanisms
         motionGroups = self.CreateMotionGroupStructure(operator, currentMotion.GetPosition())
         motionGroupRobot = self.GetMotionGroupByIndex(motionGroups, self.GroupRobot)
         line = preParameters +  "MOVEX,M" + str(self.GroupRobot) + "X," + motionGroupRobot.TargetOutput + postParameters
         self.AddLineToSource(line)