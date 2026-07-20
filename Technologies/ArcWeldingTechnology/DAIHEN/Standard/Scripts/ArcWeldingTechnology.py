# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customisation for OTC-DAIHEN
# Debug info: E2@localhost:5254
# Author: Cenit AG 2025
# Changelog:
#     Version: 1.0
#        Changed by: Berauer
#        Date: 2024-11-20
#
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import csv
import ctypes

# -------------------------------------------------------------------------------------------
# Global definitions
FILE_NAME = "ArcWeldingTechnology.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug-Technology) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug-Technology) initialization of manufacturing geometry ended."

DEBUG_PREV_EXECUTE_RECIPE_START = "(Debug-Technology) prev execute recipe started."
DEBUG_PREV_EXECUTE_RECIPE_END = "(Debug-Technology) prev execute recipe ended."

DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START = "(Debug-Technology) post process operation group attributes started."
DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END = "(Debug-Technology) post process operation group attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) post on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

DEBUG_POST_TECH_UPDATE_START = "(Debug-Technology) post technology update started."
DEBUG_POST_TECH_UPDATE_END = "(Debug-Technology) post technology update ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."
ERROR_ON_ATTRIB_CHANGE = "(Error) Could not change attribute in OnAttribChange = "

SYS_ATT_PROCESSFLOWDIRECTION = "Sys_Att_ProcessFlowDirection"

# Attribute definition technology
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
OTC_POWER_SOURCE_NUMBER = "OTC_POWER_SOURCE_NUMBER"
OTC_CELL_UNIT  = "OTC_CELL_UNIT"
OTC_UNIT_NAME  = "OTC_UNIT_NAME"
OTC_ARC_ON_CODE   = "OTC_ARC_ON_CODE"
OTC_ARC_OFF_CODE  = "OTC_ARC_OFF_CODE"
OTC_UNIT_MECHS = "OTC_UNIT_MECHS"
OTC_SMOOTHNESS = "OTC_SMOOTHNESS"
# Rule event attributes in tech
OTC_WELD_CHARACTER_DEF   = "OTC_WELD_CHARACTER_DEF"
OTC_CURRENT_DEF  = "OTC_CURRENT_DEF"
OTC_VOLTAGE_DEF  = "OTC_VOLTAGE_DEF"
OTC_WIRE_FEED_DEF  = "OTC_WIRE_FEED_DEF"
OTC_WELD_PRGNR_DEF = "OTC_WELD_PRGNR_DEF"
OTC_WELD_OFF_PRGNR_DEF = "OTC_WELD_OFF_PRGNR_DEF"
OTC_USE_WEAVE_DEF = "OTC_USE_WEAVE_DEF"
OTC_WEAVE_COND_NR_DEF  = "OTC_WEAVE_COND_NR_DEF"
#Stitch-Pulse ASS
OTC_STITCH_PULSE_AS_COND_DEF = "OTC_STITCH_PULSE_AS_COND_DEF"
OTC_STITCH_PULSE_AE_COND_DEF = "OTC_STITCH_PULSE_AE_COND_DEF"
OTC_STITCH_PULSE_ENABLED_DEF = "OTC_STITCH_PULSE_ENABLED_DEF"
OTC_STITCH_PULSE_WELDING_TIME_DEF = "OTC_STITCH_PULSE_WELDING_TIME_DEF"
OTC_STITCH_PULSE_COOLING_TIME_DEF = "OTC_STITCH_PULSE_COOLING_TIME_DEF"
OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF = "OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF"
OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF = "OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF"
# event attributes
OTC_WELD_CHARACTER   = "OTC_WELD_CHARACTER"
OTC_CURRENT  = "OTC_CURRENT"
OTC_VOLTAGE  = "OTC_VOLTAGE"
OTC_WIRE_FEED  = "OTC_WIRE_FEED"
OTC_WELD_PRGNR = "OTC_WELD_PRGNR"
OTC_WELD_OFF_PRGNR = "OTC_WELD_OFF_PRGNR"
OTC_USE_WEAVE = "OTC_USE_WEAVE"
OTC_WEAVE_COND_NR  = "OTC_WEAVE_COND_NR"
#Stitch-Pulse ASS
OTC_STITCH_PULSE_AS_COND = "OTC_STITCH_PULSE_AS_COND"
OTC_STITCH_PULSE_AE_COND = "OTC_STITCH_PULSE_AE_COND"
OTC_STITCH_PULSE_ENABLED = "OTC_STITCH_PULSE_ENABLED"
OTC_STITCH_PULSE_WELDING_TIME = "OTC_STITCH_PULSE_WELDING_TIME"
OTC_STITCH_PULSE_COOLING_TIME = "OTC_STITCH_PULSE_COOLING_TIME"
OTC_STITCH_PULSE_MOVEMENT_PITCH = "OTC_STITCH_PULSE_MOVEMENT_PITCH"
OTC_STITCH_PULSE_MOVE_COND_NUMBER = "OTC_STITCH_PULSE_MOVE_COND_NUMBER"
# Thru Arc Seam Tracking (ArcSensor) Define
AW_ARCSENSE_ST_SENSOR_ID = "ArcSensorId"
AW_ARCSENSE_DEF = "ArcSenseStDef"
AW_ARCSENSE_ST_COND_FILE_DEF = "ArcSenseStCondFileDef"
AW_ARCSENSE_ST_SAMPLE_DATA_DEF = "ArcSenseStSampleDataDef"
AW_ARCSENSE_ET_COND_FILE_DEF = "ArcSenseEtCondFileDef"
# Thru Arc Seam Tracking (ArcSensor)
AW_ARCSENSE = "ArcSenseSt"
AW_ARCSENSE_ST_COND_FILE = "ArcSenseStCondFile"
AW_ARCSENSE_ST_SAMPLE_DATA = "ArcSenseStSampleData"
AW_ARCSENSE_ET_COND_FILE = "ArcSenseEtCondFile"
#Touch Sense
MAX_INTEGER = 2147483647
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMTRACKING_OFF_EVENT_ACTIVE = "SeamTrackingOffEventActive"
AW_SEAMSEARCHING = "SeamSearching"
AW_SEAMFINDING = "SeamFinding"   
AW_SEAMTRACKING = "SeamTracking"
# Laser Tracking Start - ZT
AW_LASER_SENSOR_ID = "LaserSensorId"
AW_LASER_FOV_X = "LaserFovX"
AW_LASER_FOV_Y = "LaserFovY"
AW_LASER_FOV_Z = "LaserFovZ"
AW_LASER_FOV_RX = "LaserFovA"
AW_LASER_FOV_RY = "LaserFovB"
AW_LASER_FOV_RZ = "LaserFovC"
AW_LASER_ZT_GFF = "LaserZtGFF"
AW_LASER_ZT_LSR = "LaserZtLSR"
AW_LASER_ZT_POS_REGISTER = "LaserZtPosRegister"
AW_LASER_ZT_POSTURE = "LaserZtPosture"
# Laser Tracking End - ZE
AW_LASER_ZE_STORE_NUMBER = "LaserZeStoreNumber"
AW_LASER_ZE_STORE_COORDINATE = "LaserZeStoreCoordinate"
AW_LASER_ZE_OVER_DEV_RANGE = "LaserZeOverDevRange"
# Laser Start - ZF
AW_LASER_ZF_ON = "LaserZfOn"
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
AW_LASER_ZN_ON = "LaserZnOn"
AW_LASER_ZN_GFF = "LaserZnGFF"
AW_LASER_ZN_LSR = "LaserZnLSR"
AW_LASER_ZN_OFFSET = "LaserZnOffset"
AW_LASER_ZN_SEARCH_RANGE = "LaserZnSearchRange"
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

AW_DOWNLOAD_JOINTS_ONLY = "DownloadJointsOnly"
# 
# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator: CENPyOlpTech_AttribInitOperator):
   # Get Logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   calibMethod = attribGetter.GetAttributeByName(AW_SEAM_CALIBRATION_METHOD)
   calibMethod.SetOlpProperty(OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)

   attribCreator.AddInteger(OTC_POWER_SOURCE_NUMBER, 1, 1, 2, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, OTC_POWER_SOURCE_NUMBER)
   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 501, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   # attribCreator.AddDouble('FlybyWelding', 50, 0, 100, 10, USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_PERCENT, 'FlybyWelding')
   attribCreator.AddInteger(OTC_SMOOTHNESS, 0, 0, 3, USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_SMOOTHNESS)

   # Read the DAIHEN Weld Power Source data
   path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
   filename = 'CellDefaults.csv'
   # check it by PlugIn Manager
   csvPath = Operator.GetTechTabFolder("CellDefaults.csv")
   
   if os.path.exists(csvPath):
      cellDefaultsFile = csvPath
   else:
      cellDefaultsFile = path + filename

   try:
      # creating empty lists
      OTC_CELL_UNIT_LIST=[]
      OTC_ARC_ON_LIST=[]
      OTC_ARC_OFF_LIST=[]
      OTC_UNIT_NAME_LIST=[]
      OTC_WIRE_FEED_LIST=[]
      OTC_CURRENT_LIST=[]
      OTC_VOLTAGE_LIST=[]
      OTC_WELD_CHARACTER_LIST=[]
      OTC_UNIT_MECHS_LIST=[]
      
      # read content from the file

      with open(cellDefaultsFile, 'r') as csvfile:
         csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
         # ignore the first line
         next(csv_reader)
         # reading line by line until the end of the file
         # the content is added to the end of the list, until everyting in read
         for row in csv_reader:
            OTC_CELL_UNIT_LIST.append(row[0])
            OTC_ARC_ON_LIST.append(row[1])
            OTC_ARC_OFF_LIST.append(row[2])
            OTC_UNIT_NAME_LIST.append(row[3])
            OTC_WIRE_FEED_LIST.append(row[4])
            OTC_CURRENT_LIST.append(row[5])
            OTC_VOLTAGE_LIST.append(row[6])
            OTC_WELD_CHARACTER_LIST.append(row[7])
            OTC_UNIT_MECHS_LIST.append(row[8])

   except:
      print('Error Reading CSV File')

   # Create DAIHEN WELD Power SOurce ENUM attribute
   att1 = attribCreator.AddInteger(OTC_WELD_PRGNR_DEF, 2, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_PRGNR)
   att1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att2 = attribCreator.AddInteger(OTC_WELD_OFF_PRGNR_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_OFF_PRGNR)
   att2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attWM1 = attribCreator.AddEnum(OTC_CELL_UNIT, OTC_CELL_UNIT_LIST, OTC_CELL_UNIT_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_CELL_UNIT)
   attWM1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM1.SetReadOnly(False)
   attWM1.SetVisibility(True)

   attWM2 = attribCreator.AddString(OTC_ARC_ON_CODE, OTC_ARC_ON_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_ARC_ON_CODE)
   attWM2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   attWM2.SetReadOnly(True)
   attWM2.SetVisibility(True)

   attWM3 = attribCreator.AddString(OTC_ARC_OFF_CODE, OTC_ARC_OFF_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_ARC_OFF_CODE)
   attWM3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   attWM3.SetReadOnly(True)
   attWM3.SetVisibility(False)
   
   attWM4 = attribCreator.AddString(OTC_UNIT_NAME, OTC_UNIT_NAME_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_UNIT_NAME)
   attWM4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   attWM4.SetReadOnly(True)
   # attWM4.SetVisibility(True)

   attWM8 = attribCreator.AddInteger(OTC_WELD_CHARACTER_DEF, 4, 1, 10, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_CHARACTER)
   attWM8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM8.SetReadOnly(False)
   # attWM8.SetVisibility(True)

   attWM5 = attribCreator.AddInteger(OTC_WIRE_FEED_DEF, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WIRE_FEED)
   attWM5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM5.SetReadOnly(False)
   # attWM5.SetVisibility(True)

   attWM6 = attribCreator.AddInteger(OTC_CURRENT_DEF, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_CURRENT)
   attWM6.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM6.SetReadOnly(False)
   # attWM6.SetVisibility(True)

   attWM7 = attribCreator.AddInteger(OTC_VOLTAGE_DEF, 0, 0, 9999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_VOLTAGE)
   attWM7.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM7.SetReadOnly(False)
   # attWM7.SetVisibility(True)

   attWM8 = attribCreator.AddString(OTC_UNIT_MECHS, OTC_UNIT_MECHS_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_UNIT_MECHS)
   attWM8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWM8.SetReadOnly(True)
   attWM8.SetVisibility(True)

   stitchPulseAsCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AS_COND_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AS_COND)
   stitchPulseAsCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseAeCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AE_COND_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AE_COND)
   stitchPulseAeCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseEnabled = attribCreator.AddBool(OTC_STITCH_PULSE_ENABLED_DEF, False, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_ENABLED)
   stitchPulseEnabled.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseWeldingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_WELDING_TIME_DEF,0.7, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_WELDING_TIME)
   stitchPulseWeldingTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseCoolingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_COOLING_TIME_DEF,0.2, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_COOLING_TIME)
   stitchPulseCoolingTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseMovementTime = attribCreator.AddDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF,0.004, 0.0, 0.1, 0.001, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, OTC_STITCH_PULSE_MOVEMENT_PITCH)
   stitchPulseMovementTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   stitchPulseMoveCondNumber = attribCreator.AddInteger(OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF, 0, 0, 999, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_MOVE_COND_NUMBER)
   stitchPulseMoveCondNumber.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
   attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | USER_ATTRIBUTE)
   attConnectionType.SetVisibility(True)

   # Weave condition
   useWeave = attribCreator.AddBool(OTC_USE_WEAVE_DEF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_USE_WEAVE)
   useWeave.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveCond = attribCreator.AddInteger(OTC_WEAVE_COND_NR_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WEAVE_COND_NR)
   weaveCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Arc Sensing (FD-AR) attributes
   arcSensorId = attribCreator.AddInteger(AW_ARCSENSE_ST_SENSOR_ID, 1, 1, 12, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_SENSOR_ID)
   arcSense = attribCreator.AddBool(AW_ARCSENSE_DEF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE)
   arcSense.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcSenseStCondFile = attribCreator.AddInteger(AW_ARCSENSE_ST_COND_FILE_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_COND_FILE)
   arcSenseStCondFile.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcSenseStSampleData = attribCreator.AddInteger(AW_ARCSENSE_ST_SAMPLE_DATA_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_SAMPLE_DATA)
   arcSenseStSampleData.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   ArcSenseEtCondFile = attribCreator.AddInteger(AW_ARCSENSE_ET_COND_FILE_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ET_COND_FILE)
   ArcSenseEtCondFile.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Laser Tracking Start - ZT
   laserSensorId = attribCreator.AddInteger(AW_LASER_SENSOR_ID, 1, 1, 12, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SENSOR_ID)
   laserFovX = attribCreator.AddDouble(AW_LASER_FOV_X,0.05, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_X)
   laserFovY = attribCreator.AddDouble(AW_LASER_FOV_Y,0.0, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Y)
   laserFovZ = attribCreator.AddDouble(AW_LASER_FOV_Z,-0.04, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Z)
   laserFovA = attribCreator.AddDouble(AW_LASER_FOV_RX,0.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RX)
   laserFovB = attribCreator.AddDouble(AW_LASER_FOV_RY,20.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RY)
   laserFovC = attribCreator.AddDouble(AW_LASER_FOV_RZ,0.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RZ)
   laserZtGFF = attribCreator.AddInteger(AW_LASER_ZT_GFF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_GFF)
   laserZtLSR = attribCreator.AddInteger(AW_LASER_ZT_LSR, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_LSR)
   laserZtPosRegister = attribCreator.AddInteger(AW_LASER_ZT_POS_REGISTER, 1, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_POS_REGISTER)
   laserZtPosture = attribCreator.AddInteger(AW_LASER_ZT_POSTURE, 0, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_POSTURE)

   # Laser Tracking End - ZE
   laserZeStoreNumber = attribCreator.AddInteger(AW_LASER_ZE_STORE_NUMBER, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZE_STORE_NUMBER)
   laserZeStoreCoordinate = attribCreator.AddInteger(AW_LASER_ZE_STORE_COORDINATE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZE_STORE_COORDINATE)
   laserZeOverDevRange = attribCreator.AddDouble(AW_LASER_ZE_OVER_DEV_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZE_OVER_DEV_RANGE)

   # Laser Seam Start Search - ZF
   laserZfOn = attribCreator.AddBool(AW_LASER_ZF_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_ON)
   laserZfGFF = attribCreator.AddInteger(AW_LASER_ZF_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_GFF)
   laserZfLSR = attribCreator.AddInteger(AW_LASER_ZF_LSR, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_LSR)
   laserZfPosRegister = attribCreator.AddInteger(AW_LASER_ZF_POS_REGISTER, 1, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_POS_REGISTER)
   laserZfPosture = attribCreator.AddInteger(AW_LASER_ZF_POSTURE, 0, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_POSTURE)
   laserZfStoreNumber = attribCreator.AddInteger(AW_LASER_ZF_STORE_NUMBER, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_STORE_NUMBER)
   laserZfStoreCoordinate = attribCreator.AddInteger(AW_LASER_ZF_STORE_COORDINATE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_STORE_COORDINATE)
   laserZfSearchRange = attribCreator.AddDouble(AW_LASER_ZF_SEARCH_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_SEARCH_RANGE)
   laserZfOffset = attribCreator.AddDouble(AW_LASER_ZF_OFFSET,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_OFFSET)
   laserZfSpeed = attribCreator.AddDouble(AW_LASER_ZF_SPEED,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_SPEED)

   # Laser Seam Start Search - ZF
   laserZnOn = attribCreator.AddBool(AW_LASER_ZN_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_ON)
   laserZnGFF = attribCreator.AddInteger(AW_LASER_ZN_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_GFF)
   laserZnLSR = attribCreator.AddInteger(AW_LASER_ZN_LSR, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_LSR)
   laserZnOffset = attribCreator.AddDouble(AW_LASER_ZN_OFFSET,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZN_OFFSET)
   laserZnSearchRange = attribCreator.AddDouble(AW_LASER_ZN_SEARCH_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZN_SEARCH_RANGE)


   # Laser Seam Search - ZJ
   laserZjOn = attribCreator.AddBool(AW_LASER_ZJ_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_ON)
   laserZjOn.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   laserZjGFF = attribCreator.AddInteger(AW_LASER_ZJ_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GFF)
   laserZjGAP = attribCreator.AddInteger(AW_LASER_ZJ_GAP, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GAP)
   laserZjStoreNumber = attribCreator.AddInteger(AW_LASER_ZJ_STORE_NUMBER, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_NUMBER)
   laserZjBasePositionY = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Y, 0.0, -0.10, 0.10, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Y)
   laserZjBasePositionY.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserZjBasePositionZ = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Z, 0.0, -0.10, 0.10, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Z)
   laserZjBasePositionZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserZjSearchWaitDelay = attribCreator.AddDouble(AW_LASER_ZJ_SEARCH_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_SEARCH_DELAY)
   laserZjSearchStableDelay = attribCreator.AddDouble(AW_LASER_ZJ_STABLE_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_STABLE_DELAY)

   laserZjStoreCoordinates = attribCreator.AddEnum(AW_LASER_ZJ_STORE_COORDINATES, AW_LASER_ZJ_STORE_LIT, AW_LASER_ZJ_STORE_LIT[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_COORDINATES)
   
   laserZjDevComposition = attribCreator.AddBool(AW_LASER_ZJ_DEV_COMPOSITION, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_DEV_COMPOSITION)
   laserZjAutoManualModify = attribCreator.AddBool(AW_LASER_ZJ_AUTO_MANUAL_MODIFY, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_AUTO_MANUAL_MODIFY)
   
   laserZjDeviationLength = attribCreator.AddDouble(AW_LASER_ZJ_DEVIATION_LENGTH, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_DEVIATION_LENGTH)
   laserZjMinDepthValue = attribCreator.AddDouble(AW_LASER_ZJ_MIN_DEPTH_VALUE, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_MIN_DEPTH_VALUE)
   laserZjGapWatchRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MAX, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MAX)
   laserZjGapWatchRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MIN, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MIN)
   laserZjAngleOneRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX)
   laserZjAngleOneRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN)
   laserZjAngleTwoRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX)
   laserZjAngleTwoRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN)
   
   # set all linear flyby attribs maximum to 100mm AKA %
   flyByLinMax = 0.1 # m=100mm=100%
   fb1 = attribGetter.GetAttributeDoubleByName("FlybyWelding")
   if fb1.IsValid():
      fb1.SetMinimum(0.0)
      fb1.SetMaximum(flyByLinMax)
      fb1.SetValue(0.002)
   #fb3 = attribGetter.GetAttributeDoubleByName("FlybyRetract")
   #if fb3.IsValid():
   #   fb3.SetMinimum(0.0)
   #   fb3.SetMaximum(flyByLinMax)
   #   fb3.SetValue(0.002)
   speed = attribGetter.GetAttributeDoubleByName('Speed')
   if speed.IsValid():
      #logging.LogInfo('.................................SetOlpPropertySpeed')
      speed.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)

   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   # Download Flag for output all Positions in JOINT Mode
   dlJointsOnly = attribCreator.AddBool(AW_DOWNLOAD_JOINTS_ONLY, False, GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_DOWNLOAD_JOINTS_ONLY)
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
def PostTechInitEvents(Operator):
    #    # get logger
    logging = Operator.GetLoggerOperator()
    #    # debug logging
    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

    #    # YOUR CODE
    Operator.RegisterPyTechnologyEvent('UploadEvent.py')
    Operator.RegisterPyTechnologyEvent('UploadTSMotionEvent.py')
    Operator.RegisterPyTechnologyEvent("ZJEvent")
    Operator.RegisterPyTechnologyEvent("SF3Event")
    Operator.RegisterPyTechnologyEvent("SF4Event")
    Operator.RegisterPyTechnologyEvent("SF8Event")

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)


# -------------------------------------------------------------------------------------------
# Technology post event rule initialization
# def PostTechInitRules(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)


# -------------------------------------------------------------------------------------------
# Technology post manufacturing geometry initialization
# def PostInitManufacturingGeometry(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_END)

# # -------------------------------------------------------------------------------------------
# # Technology prev execute recipe
# def PrevExecuteRecipe(Operator: CENPyOlpTech_RecipeOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)

# # -------------------------------------------------------------------------------------------
# # Technology post process operation group attributes
# def PostProcessOperationGroupAttributes(Operator: CENPyOlpTech_POGAttribOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

   # get attribute getter
   # attribGetter = Operator.GetAttribGetter()
   # attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
   # attConnectionType.SetVisibility(False)

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator: CENPyOlpTech_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)
   
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute setter
   controller = Operator.GetController()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   attribName = changedAttrib.GetName()

   # show/hide ConnectionType Attribute due to CalibrationMethod

   # Get relevant flags
   
   
   if (attribName == AW_SEAM_CALIBRATION_METHOD):
      calibrationMethod=''
      calibrationMethodAttrib=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD)
      #logging.LogInfo('..................found Calibration Method Attribute AW_SEAM_CALIBRATION_METHOD=' + str(calibrationMethodAttrib))
      if calibrationMethodAttrib.IsValid():
         #logging.LogInfo('.............................Calibration Method Attribute AW_SEAM_CALIBRATION_METHOD  IsValid')
         calibrationMethod=calibrationMethodAttrib.GetValue()
         #logging.LogInfo('.....................................Calibration Method = ' + str(calibrationMethod))
         if (calibrationMethod == AW_SEAMSEARCHING) or (calibrationMethod == AW_TOUCHSENSE_BY_POINT) or (calibrationMethod == AW_TOUCHSENSE_AUTOMATIC):
            attrVisi=True
         else:
            attrVisi=False
         attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
         if attConnectionType.IsValid():
            #logging.LogInfo('.....................................AW_TOUCHSENS_CONNECT_TYPE.SetVisibility = ' + str(attrVisi))
            attConnectionType.SetVisibility(attrVisi)

   if (attribName == AW_SEAM_CALIBRATION_METHOD) or (attribName == OTC_USE_WEAVE_DEF) or (attribName == AW_ARCSENSE_DEF) or (attribName == AW_LASER_ZF_ON) or (attribName == AW_LASER_ZN_ON) or (attribName == AW_LASER_ZJ_ON) or (attribName == OTC_STITCH_PULSE_ENABLED_DEF):
      
      calibrationMethod=''
      calibrationMethodAttrib=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD)
      #logging.LogInfo('..................found Calibration Method Attribute AW_SEAM_CALIBRATION_METHOD=' + str(calibrationMethodAttrib))
      if calibrationMethodAttrib.IsValid():
         #logging.LogInfo('.............................Calibration Method Attribute AW_SEAM_CALIBRATION_METHOD  IsValid')
         calibrationMethod=calibrationMethodAttrib.GetValue()

      laserZfOn = attribGetter.GetAttributeByName(AW_LASER_ZF_ON)
      laserZnOn = attribGetter.GetAttributeByName(AW_LASER_ZN_ON)
      laserZjOn = attribGetter.GetAttributeByName(AW_LASER_ZJ_ON)
      useLaserZfOn = attribGetter.GetBool(AW_LASER_ZF_ON)
      useLaserZnOn = attribGetter.GetBool(AW_LASER_ZN_ON)
      useLaserZjOn = attribGetter.GetBool(AW_LASER_ZJ_ON)
      laserZfOn.SetReadOnly(False)
      laserZnOn.SetReadOnly(False)
      laserZjOn.SetReadOnly(False)
      laserZfOn.SetVisibility(True)
      laserZnOn.SetVisibility(True)
      laserZjOn.SetVisibility(True)
      # if useLaserZjOn:
      #    laserZfOn.SetReadOnly(True)
      #    laserZnOn.SetReadOnly(True)
      #    laserZjOn.SetReadOnly(False)
      # elif useLaserZfOn or useLaserZnOn:
      #    laserZfOn.SetReadOnly(False)
      #    laserZnOn.SetReadOnly(False)
      #    laserZjOn.SetReadOnly(True)
      # else:
      #    laserZfOn.SetReadOnly(False)
      #    laserZnOn.SetReadOnly(False)
      #    laserZjOn.SetReadOnly(False)

      # Laser Tracking Start - ZT
      laserSensorId = attribGetter.GetAttributeByName(AW_LASER_SENSOR_ID)
      laserZtGFF = attribGetter.GetAttributeByName(AW_LASER_ZT_GFF)
      laserZtLSR = attribGetter.GetAttributeByName(AW_LASER_ZT_LSR)
      laserZtPosRegister = attribGetter.GetAttributeByName(AW_LASER_ZT_POS_REGISTER)
      laserZtPosture = attribGetter.GetAttributeByName(AW_LASER_ZT_POSTURE)
      # Laser Tracking End - ZE
      laserZeStoreNumber = attribGetter.GetAttributeByName(AW_LASER_ZE_STORE_NUMBER)
      laserZeStoreCoordinate = attribGetter.GetAttributeByName(AW_LASER_ZE_STORE_COORDINATE)
      laserZeOverDevRange = attribGetter.GetAttributeByName(AW_LASER_ZE_OVER_DEV_RANGE)
      # Laser Seam Start Search - ZF
      laserZfGFF = attribGetter.GetAttributeByName(AW_LASER_ZF_GFF)
      laserZfLSR = attribGetter.GetAttributeByName(AW_LASER_ZF_LSR)
      laserZfPosRegister = attribGetter.GetAttributeByName(AW_LASER_ZF_POS_REGISTER)
      laserZfPosture = attribGetter.GetAttributeByName(AW_LASER_ZF_POSTURE)
      laserZfStoreNumber = attribGetter.GetAttributeByName(AW_LASER_ZF_STORE_NUMBER)
      laserZfStoreCoordinate = attribGetter.GetAttributeByName(AW_LASER_ZF_STORE_COORDINATE)
      laserZfSearchRange = attribGetter.GetAttributeByName(AW_LASER_ZF_SEARCH_RANGE)
      laserZfOffset = attribGetter.GetAttributeByName(AW_LASER_ZF_OFFSET)
      laserZfSpeed = attribGetter.GetAttributeByName(AW_LASER_ZF_SPEED)
      # Laser Seam End Search - ZN
      laserZnGFF = attribGetter.GetAttributeByName(AW_LASER_ZN_GFF)
      laserZnLSR = attribGetter.GetAttributeByName(AW_LASER_ZN_LSR)
      laserZnOffset = attribGetter.GetAttributeByName(AW_LASER_ZN_OFFSET)
      laserZnSearchRange = attribGetter.GetAttributeByName(AW_LASER_ZN_SEARCH_RANGE)
      # Laser Seam Search - ZJ
      laserZjGFF = attribGetter.GetAttributeByName(AW_LASER_ZJ_GFF)
      laserZjGAP = attribGetter.GetAttributeByName(AW_LASER_ZJ_GAP)
      laserZjStoreNumber = attribGetter.GetAttributeByName(AW_LASER_ZJ_STORE_NUMBER)
      laserZjBasePositionY = attribGetter.GetAttributeByName(AW_LASER_ZJ_BASE_POS_Y)
      laserZjBasePositionZ = attribGetter.GetAttributeByName(AW_LASER_ZJ_BASE_POS_Z)
      laserZjSearchWaitDelay = attribGetter.GetAttributeByName(AW_LASER_ZJ_SEARCH_DELAY)
      laserZjSearchStableDelay = attribGetter.GetAttributeByName(AW_LASER_ZJ_STABLE_DELAY)
      
      laserZjStoreCoordinates = attribGetter.GetAttributeByName(AW_LASER_ZJ_STORE_COORDINATES)
      laserZjDevComposition = attribGetter.GetAttributeByName(AW_LASER_ZJ_DEV_COMPOSITION)
      laserZjAutoManualModify = attribGetter.GetAttributeByName(AW_LASER_ZJ_AUTO_MANUAL_MODIFY)
      laserZjDeviationLength = attribGetter.GetAttributeByName(AW_LASER_ZJ_DEVIATION_LENGTH)
      laserZjMinDepthValue = attribGetter.GetAttributeByName(AW_LASER_ZJ_MIN_DEPTH_VALUE)
      laserZjGapWatchRangeMax = attribGetter.GetAttributeByName(AW_LASER_ZJ_GAP_WATCH_RANGE_MAX)
      laserZjGapWatchRangeMin = attribGetter.GetAttributeByName(AW_LASER_ZJ_GAP_WATCH_RANGE_MIN)
      laserZjAngleOneRangeMax = attribGetter.GetAttributeByName(AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX)
      laserZjAngleOneRangeMin = attribGetter.GetAttributeByName(AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN)
      laserZjAngleTwoRangeMax = attribGetter.GetAttributeByName(AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX)
      laserZjAngleTwoRangeMin = attribGetter.GetAttributeByName(AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN)

      arcSensorId = attribGetter.GetAttributeByName(AW_ARCSENSE_ST_SENSOR_ID)
      # have additional position before arc off only when tracking ZT and End point search ZN is on
      if (calibrationMethod == AW_SEAMTRACKING) and useLaserZnOn:
         attribSetter.SetBool(AW_SEAMTRACKING_OFF_EVENT_ACTIVE, True)
      else:
         attribSetter.SetBool(AW_SEAMTRACKING_OFF_EVENT_ACTIVE, False)

      if (calibrationMethod == AW_SEAMTRACKING) or (calibrationMethod == AW_SEAMFINDING):
         laserSensorId.SetVisibility(True)
         # No ArcSense when seam tracking or finding
         attribSetter.SetBool(AW_ARCSENSE_DEF, False)
         if (calibrationMethod == AW_SEAMFINDING):
            attribSetter.SetBool(AW_LASER_ZF_ON, False)
            attribSetter.SetBool(AW_LASER_ZN_ON, False)
            attribSetter.SetBool(AW_LASER_ZJ_ON, True)
            useLaserZfOn = attribGetter.GetBool(AW_LASER_ZF_ON)
            useLaserZnOn = attribGetter.GetBool(AW_LASER_ZN_ON)
            useLaserZjOn = attribGetter.GetBool(AW_LASER_ZJ_ON)
 
            laserZtGFF.SetVisibility(False)
            laserZtLSR.SetVisibility(False)
            laserZtPosRegister.SetVisibility(False)
            laserZtPosture.SetVisibility(False)

            laserZeStoreNumber.SetVisibility(False)
            laserZeStoreCoordinate.SetVisibility(False)
            laserZeOverDevRange.SetVisibility(False)
         else:
            laserZtGFF.SetVisibility(True)
            laserZtLSR.SetVisibility(True)
            laserZtPosRegister.SetVisibility(True)
            laserZtPosture.SetVisibility(True)

            laserZeStoreNumber.SetVisibility(True)
            laserZeStoreCoordinate.SetVisibility(True)
            laserZeOverDevRange.SetVisibility(True)
         laserZfOn.SetVisibility(True)
         laserZnOn.SetVisibility(True)
         laserZjOn.SetVisibility(True)
         # Hide/Show Laser Seam Start Search - ZF
         laserZfGFF.SetVisibility(useLaserZfOn)
         laserZfLSR.SetVisibility(useLaserZfOn)
         laserZfPosRegister.SetVisibility(useLaserZfOn)
         laserZfPosture.SetVisibility(useLaserZfOn)
         laserZfStoreNumber.SetVisibility(useLaserZfOn)
         laserZfStoreCoordinate.SetVisibility(useLaserZfOn)
         laserZfSearchRange.SetVisibility(useLaserZfOn)
         laserZfOffset.SetVisibility(useLaserZfOn)
         laserZfSpeed.SetVisibility(useLaserZfOn)
         # Hide/ShowLaser Seam End Search - ZN
         laserZnGFF.SetVisibility(useLaserZnOn)
         laserZnLSR.SetVisibility(useLaserZnOn)
         laserZnOffset.SetVisibility(useLaserZnOn)
         laserZnSearchRange.SetVisibility(useLaserZnOn)

         # Hide/ShowLaser Seam Find - ZJ
         laserZjGFF.SetVisibility(+6)
         laserZjGAP.SetVisibility(useLaserZjOn)
         laserZjStoreNumber.SetVisibility(useLaserZjOn)
         laserZjBasePositionY.SetVisibility(useLaserZjOn)
         laserZjBasePositionZ.SetVisibility(useLaserZjOn)
         laserZjSearchWaitDelay.SetVisibility(useLaserZjOn)
         laserZjSearchStableDelay.SetVisibility(useLaserZjOn)
         laserZjStoreCoordinates.SetVisibility(useLaserZjOn)
         laserZjDevComposition.SetVisibility(useLaserZjOn)
         laserZjAutoManualModify.SetVisibility(useLaserZjOn)
         laserZjDeviationLength.SetVisibility(useLaserZjOn)
         laserZjMinDepthValue.SetVisibility(useLaserZjOn)
         laserZjGapWatchRangeMax.SetVisibility(useLaserZjOn)
         laserZjGapWatchRangeMin.SetVisibility(useLaserZjOn)
         laserZjAngleOneRangeMax.SetVisibility(useLaserZjOn)
         laserZjAngleOneRangeMin.SetVisibility(useLaserZjOn)
         laserZjAngleTwoRangeMax.SetVisibility(useLaserZjOn)
         laserZjAngleTwoRangeMin.SetVisibility(useLaserZjOn)

         arcSensorId.SetVisibility(False)
      else:
         laserSensorId.SetVisibility(False)
         laserZtGFF.SetVisibility(False)
         laserZtLSR.SetVisibility(False)
         laserZtPosRegister.SetVisibility(False)
         laserZtPosture.SetVisibility(False)

         laserZeStoreNumber.SetVisibility(False)
         laserZeStoreCoordinate.SetVisibility(False)
         laserZeOverDevRange.SetVisibility(False)

         laserZfOn.SetVisibility(False)
         laserZnOn.SetVisibility(False)
         laserZjOn.SetVisibility(False)

         # Laser Seam Start Search - ZF
         laserZfGFF.SetVisibility(False)
         laserZfLSR.SetVisibility(False)
         laserZfPosRegister.SetVisibility(False)
         laserZfPosture.SetVisibility(False)
         laserZfStoreNumber.SetVisibility(False)
         laserZfStoreCoordinate.SetVisibility(False)
         laserZfSearchRange.SetVisibility(False)
         laserZfOffset.SetVisibility(False)
         laserZfSpeed.SetVisibility(False)
         # Laser Seam End Search - ZF
         laserZnGFF.SetVisibility(False)
         laserZnLSR.SetVisibility(False)
         laserZnOffset.SetVisibility(False)
         laserZnSearchRange.SetVisibility(False)

         laserZjGFF.SetVisibility(False)
         laserZjGAP.SetVisibility(False)
         laserZjStoreNumber.SetVisibility(False)
         laserZjBasePositionY.SetVisibility(False)
         laserZjBasePositionZ.SetVisibility(False)
         laserZjSearchWaitDelay.SetVisibility(False)
         laserZjSearchStableDelay.SetVisibility(False)
         laserZjStoreCoordinates.SetVisibility(False)
         laserZjDevComposition.SetVisibility(False)
         laserZjAutoManualModify.SetVisibility(False)
         laserZjDeviationLength.SetVisibility(False)
         laserZjMinDepthValue.SetVisibility(False)
         laserZjGapWatchRangeMax.SetVisibility(False)
         laserZjGapWatchRangeMin.SetVisibility(False)
         laserZjAngleOneRangeMax.SetVisibility(False)
         laserZjAngleOneRangeMin.SetVisibility(False)
         laserZjAngleTwoRangeMax.SetVisibility(False)
         laserZjAngleTwoRangeMin.SetVisibility(False)
         arcSensorId.SetVisibility(True)

   if (attribName == OTC_USE_WEAVE_DEF) or (attribName == AW_ARCSENSE_DEF):
      # Weaving and Thru the arc sensing attributes
      # elif (attribName == "UseWeaveDefine") or (attribName == AW_ARCSENSE):
      useWeaving = attribGetter.GetBool(OTC_USE_WEAVE_DEF)
      useArcSense = attribGetter.GetBool(AW_ARCSENSE_DEF)
      arcSense = attribGetter.GetAttributeByName(AW_ARCSENSE_DEF)
      sense1 = attribGetter.GetAttributeByName(AW_ARCSENSE_ST_COND_FILE_DEF)
      sense2 = attribGetter.GetAttributeByName(AW_ARCSENSE_ST_SAMPLE_DATA_DEF)
      sense3 = attribGetter.GetAttributeByName(AW_ARCSENSE_ET_COND_FILE_DEF)
      if useWeaving:
         # Weaving
         attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR_DEF).SetVisibility(True)
         arcSense.SetVisibility(True)
         if (calibrationMethod == AW_SEAMTRACKING):
            useArcSense = attribSetter.SetBool(AW_ARCSENSE_DEF, False)
            arcSense.SetReadOnly(True)
         else:
            arcSense.SetReadOnly(False)
         if useArcSense:
            sense1.SetVisibility(True)
            sense2.SetVisibility(True)
            sense3.SetVisibility(True)
         else:
            sense1.SetVisibility(False)
            sense2.SetVisibility(False)
            sense3.SetVisibility(False)
      else:
         attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR_DEF).SetVisibility(False)
         # arcSense.SetVisibility(False)
         useArcSense = attribSetter.SetBool(AW_ARCSENSE_DEF, False)
         sense1.SetVisibility(False)
         sense2.SetVisibility(False)
         sense3.SetVisibility(False)

      if useArcSense and useWeaving:
         # arcSense.SetVisibility(True)
         sense1.SetVisibility(useArcSense)
         sense2.SetVisibility(useArcSense)
         sense3.SetVisibility(useArcSense)

   # Stitch-Pulse
   useStitchPulse = attribGetter.GetBool(OTC_STITCH_PULSE_ENABLED_DEF)
   if (attribName == OTC_STITCH_PULSE_ENABLED_DEF):
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_AS_COND_DEF).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_AE_COND_DEF).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_WELDING_TIME_DEF).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_COOLING_TIME_DEF).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF).SetVisibility(useStitchPulse)

   # Weld Program or Manual Entries
   if (attribName == OTC_WELD_PRGNR_DEF):
      OtcWeldPrgnrDef = attribGetter.GetInteger(OTC_WELD_PRGNR_DEF)
      dataSet = getRelatedDataSet(Operator, OtcWeldPrgnrDef)
      if len(dataSet) > 13:
         feed = dataSet[10]
         attribSetter.SetDouble("Speed", feed)
      else:
         attribSetter.SetDouble("Speed", 0.03)
      OtcWeldCharacter = attribGetter.GetAttributeByName(OTC_WELD_CHARACTER_DEF)
      OtcWireFeed = attribGetter.GetAttributeByName(OTC_WIRE_FEED_DEF)
      OtcCurrent = attribGetter.GetAttributeByName(OTC_CURRENT_DEF)
      OtcVoltage = attribGetter.GetAttributeByName(OTC_VOLTAGE_DEF)
      if (OtcWeldPrgnrDef < 1):
         OtcWeldCharacter.SetVisibility(True)
         OtcWireFeed.SetVisibility(True)
         OtcCurrent.SetVisibility(True)
         OtcVoltage.SetVisibility(True)
      else:
         OtcWeldCharacter.SetVisibility(False)
         OtcWireFeed.SetVisibility(False)
         OtcCurrent.SetVisibility(False)
         OtcVoltage.SetVisibility(False)

   if (attribName == OTC_CELL_UNIT):
      # Read the DAIHEN Weld Power Source data
      path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
      filename = 'CellDefaults.csv'
      # check it by PlugIn Manager
      csvPath = Operator.GetTechTabFolder("CellDefaults.csv")
      
      if os.path.exists(csvPath):
         cellDefaultsFile = csvPath
      else:
         cellDefaultsFile = path + filename
      
      try:
         # creating empty lists
         OTC_CELL_UNIT_LIST=[]
         OTC_ARC_ON_LIST=[]
         OTC_ARC_OFF_LIST=[]
         OTC_UNIT_NAME_LIST=[]
         OTC_WIRE_FEED_LIST=[]
         OTC_CURRENT_LIST=[]
         OTC_VOLTAGE_LIST=[]
         OTC_WELD_CHARACTER_LIST=[]
         OTC_UNIT_MECHS_LIST=[]
         
         # read content from the file

         with open(cellDefaultsFile, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
            # ignore the first line
            next(csv_reader)
            # reading line by line until the end of the file
            # the content is added to the end of the list, until everyting in read
            for row in csv_reader:
               OTC_CELL_UNIT_LIST.append(row[0])
               OTC_ARC_ON_LIST.append(row[1])
               OTC_ARC_OFF_LIST.append(row[2])
               OTC_UNIT_NAME_LIST.append(row[3])
               OTC_WIRE_FEED_LIST.append(row[4])
               OTC_CURRENT_LIST.append(row[5])
               OTC_VOLTAGE_LIST.append(row[6])
               OTC_WELD_CHARACTER_LIST.append(row[7])
               OTC_UNIT_MECHS_LIST.append(row[8])

      except:
         print('Error Reading CSV File')

      try:
         WPSIndex = attribGetter.GetEnumIndex(OTC_CELL_UNIT)
         # WPSValue = attribGetter.GetAttributeEnumByName(OTC_CELL_UNIT).GetValue()
      except:
         logging.LogError('Cannot get the Attribute OTC_CELL_UNIT!')

      try:
         attribSetter.SetString(OTC_ARC_ON_CODE, OTC_ARC_ON_LIST[WPSIndex])
      except:
         logging.LogError('Cannot set the Attribute OTC_ARC_ON_CODE!')

      try:
         attribSetter.SetString(OTC_ARC_OFF_CODE, OTC_ARC_OFF_LIST[WPSIndex])
      except:
         logging.LogError('Cannot set the Attribute OTC_ARC_OFF_CODE!')

      try:
         attribSetter.SetString(OTC_UNIT_NAME, OTC_UNIT_NAME_LIST[WPSIndex])
      except:
         logging.LogError('Cannot set the Attribute OTC_UNIT_NAME!')

      try:
         attribSetter.SetInteger(OTC_WELD_CHARACTER_DEF, int(OTC_WELD_CHARACTER_LIST[WPSIndex]))
      except:
         logging.LogError('Cannot set the Attribute OTC_WELD_CHARACTER!')

      try:
         attribSetter.SetInteger(OTC_WIRE_FEED_DEF, int(OTC_WIRE_FEED_LIST[WPSIndex]))
      except:
         logging.LogError('Cannot set the Attribute OTC_WIRE_FEED!')

      try:
         attribSetter.SetInteger(OTC_CURRENT_DEF, int(OTC_CURRENT_LIST[WPSIndex]))
      except:
         logging.LogError('Cannot set the Attribute OTC_CURRENT!')

      try:
         attribSetter.SetInteger(OTC_VOLTAGE_DEF, int(OTC_VOLTAGE_LIST[WPSIndex]))
      except:
         logging.LogError('Cannot set the Attribute OTC_VOLTAGE!')

      try:
         attribSetter.SetString(OTC_UNIT_MECHS, OTC_UNIT_MECHS_LIST[WPSIndex])
      except:
         logging.LogError('Cannot set the Attribute OTC_UNIT_MECHS!')

# Customizing End

# -------------------------------------------------------------------------------------------
# Technology post on frame change
# def PostTechOnFrameChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
#    # attribGetter = Operator.GetAttribGetter()
#    # attribSetter = Operator.GetAttribSetter()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   # Released version numbers should be increased by 100 to leave enough versions for
   # customizations and make upgrades of customizations to a newer release easier.
   # 100 = R2024.2.2
   return 110

# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator : CENPyOlpTech_UpdateOperator):
   logging = Operator.GetLoggerOperator()
   #logging.LogInfo('####################################################')
   #logging.LogInfo('------------------ ArcWeldingTechnology PostTechUpdate -------------------')
   logging.LogDebug("(Debug) Post tech update started.")
   lastVersion = Operator.GetLastSavedPythonTechnologyVersion()
   currentVersion = GetPythonTechnologyVersion()
   logging.LogInfo('Last script version: ' + str(lastVersion) + '. Current script version: ' + str(currentVersion))
   program = Operator.GetOlpProgram()
   attribGetter = Operator.GetAttribGetter(program)
   attribSetter = Operator.GetAttribSetter(program)
   attribCreator = Operator.GetAttribCreator(program)
   
   if (lastVersion < 100):
      # attribGetter = Operator.GetAttribGetter(program)
      # RemoveAttribute(Operator,program,'ArcWeldingGlobalPortTouch')

      # arcOnCode = attribGetter.GetAttributeByName(OTC_ARC_ON_CODE)
      # arcOnCode.SetVisibility(True)
      # arcOffCode = attribGetter.GetAttributeByName(OTC_ARC_OFF_CODE)
      # arcOffCode.SetVisibility(True)

      #logging.LogInfo('...........................GetAttributeByName(Speed)')
      speed = attribGetter.GetAttributeDoubleByName('Speed')
      if speed.IsValid():
         #logging.LogInfo('.................................SetOlpPropertySpeed')
         speed.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
      #logging.LogInfo('...........................')
      
      #logging.LogInfo('...........................GetAttributeDoubleByName(FlybyWelding)' )
      flybyWelding = attribGetter.GetAttributeDoubleByName("FlybyWelding")
      if flybyWelding.IsValid():
         #logging.LogInfo('.................................SetOlpProperty FlybyWelding')
         flybyWelding.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
      #logging.LogInfo('...........................')
      
      # OTC_WEAVE_COND_NR is only Event Attrib (not _DEF !)
      #logging.LogInfo('...........................GetAttributeDoubleByName(OTC_WEAVE_COND_NR)')
      weaveConditionNr = attribGetter.GetAttributeIntegerByName(OTC_WEAVE_COND_NR)
      if weaveConditionNr.IsValid():
         #logging.LogInfo('.................................SetVisibility OTC_WEAVE_COND_NR')
         weaveConditionNr.SetVisibility(False)
      #logging.LogInfo('...........................')

      #logging.LogInfo('...........................GetAttributeDoubleByName(FlybyRetract)')
      #flybyRetract = attribGetter.GetAttributeDoubleByName("FlybyRetract")
      #if flybyRetract.IsValid():
      #   logging.LogInfo('.................................SetOlpProperty FlybyRetract')
      #   flybyRetract.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
      #logging.LogInfo('...........................')
      
      childs = program.GetChildComponents()
      for child in childs:
          # loop through Program-Components...
          typOpGr = child.GetType()
          #logging.LogInfo(",,,,,,,, PROGRAM - CHILD.GetType = " + str(typOpGr))
          # ...getting OpGroups
          if typOpGr == 2:
              # ----------- set attribute on OpGroup ---------------------------------------------------------
              childAttribGetter = Operator.GetAttribGetter(child)
              # set Attribute AW_SEAM_CALIBRATION_METHOD
              try:
                 calibMethod = childAttribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD)
                 if calibMethod.IsValid():
                   logging.LogInfo('Update on Group AW_SEAM_CALIBRATION_METHOD : SetOlpProperty : OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE')
                   calibMethod.SetOlpProperty(OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
              except:
                 logging.LogError("-----------CANNOT set Attribute ''AW_SEAM_CALIBRATION_METHOD'' ")
              # ----------- set attribute on OpGroup ---------------------------------------------------------
              
              # Get OpGroup Componenets
              opchilds = child.GetChildComponents()
              for opchild in opchilds:
                 # loop through OpGroup-Components...
                 typOp = opchild.GetType()
                 #logging.LogInfo(",,,,,,,,..... OPGROUP - CHILD.GetType = " + str(typOp))
                 # ...getting Operations
                 if typOp == 3:
                     # ----------- set attribute on Operation ---------------------------------------------------------
                     childAttribGetter = Operator.GetAttribGetter(opchild)
                     # set Attribute AW_SEAM_CALIBRATION_METHOD
                     try:
                       calibMethod = childAttribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD)
                       if calibMethod.IsValid():
                          logging.LogInfo('Update on Operation AW_SEAM_CALIBRATION_METHOD : SetOlpProperty : OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE')
                          calibMethod.SetOlpProperty(OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
                     except:
                        logging.LogError("-----------CANNOT set Attribute ''AW_SEAM_CALIBRATION_METHOD'' ")
                     # ----------- set attribute on Operation ---------------------------------------------------------
      
      attribCreator.AddInteger(OTC_POWER_SOURCE_NUMBER, 1, 1, 2, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, OTC_POWER_SOURCE_NUMBER)
      attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 501, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
      # attribCreator.AddDouble('FlybyWelding', 50, 0, 100, 10, USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_PERCENT, 'FlybyWelding')
      attribCreator.AddInteger(OTC_SMOOTHNESS, 0, 0, 3, USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_SMOOTHNESS)

      # Read the DAIHEN Weld Power Source data
      path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
      filename = 'CellDefaults.csv'

      # check it by PlugIn Manager
      csvPath = Operator.GetTechTabFolder("CellDefaults.csv")
      
      if os.path.exists(csvPath):
         cellDefaultsFile = csvPath
      else:
         cellDefaultsFile = path + filename

      try:
         # creating empty lists
         OTC_CELL_UNIT_LIST=[]
         OTC_ARC_ON_LIST=[]
         OTC_ARC_OFF_LIST=[]
         OTC_UNIT_NAME_LIST=[]
         OTC_WIRE_FEED_LIST=[]
         OTC_CURRENT_LIST=[]
         OTC_VOLTAGE_LIST=[]
         OTC_WELD_CHARACTER_LIST=[]
         OTC_UNIT_MECHS_LIST=[]
         
         # read content from the file

         with open(cellDefaultsFile, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
            # ignore the first line
            next(csv_reader)
            # reading line by line until the end of the file
            # the content is added to the end of the list, until everyting in read
            for row in csv_reader:
               OTC_CELL_UNIT_LIST.append(row[0])
               OTC_ARC_ON_LIST.append(row[1])
               OTC_ARC_OFF_LIST.append(row[2])
               OTC_UNIT_NAME_LIST.append(row[3])
               OTC_WIRE_FEED_LIST.append(row[4])
               OTC_CURRENT_LIST.append(row[5])
               OTC_VOLTAGE_LIST.append(row[6])
               OTC_WELD_CHARACTER_LIST.append(row[7])
               OTC_UNIT_MECHS_LIST.append(row[8])

      except:
         print('Error Reading CSV File')

      # Create DAIHEN WELD Power SOurce ENUM attribute
      att1 = attribCreator.AddInteger(OTC_WELD_PRGNR_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_PRGNR)
      att1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      att2 = attribCreator.AddInteger(OTC_WELD_OFF_PRGNR_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_OFF_PRGNR)
      att2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      attWM1 = attribCreator.AddEnum(OTC_CELL_UNIT, OTC_CELL_UNIT_LIST, OTC_CELL_UNIT_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_CELL_UNIT)
      attWM1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM1.SetReadOnly(False)
      attWM1.SetVisibility(True)

      attWM2 = attribCreator.AddString(OTC_ARC_ON_CODE, OTC_ARC_ON_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_ARC_ON_CODE)
      attWM2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      attWM2.SetReadOnly(True)
      attWM2.SetVisibility(True)

      attWM3 = attribCreator.AddString(OTC_ARC_OFF_CODE, OTC_ARC_OFF_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_ARC_OFF_CODE)
      attWM3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      attWM3.SetReadOnly(True)
      attWM3.SetVisibility(False)
      
      attWM4 = attribCreator.AddString(OTC_UNIT_NAME, OTC_UNIT_NAME_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_UNIT_NAME)
      attWM4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      attWM4.SetReadOnly(True)
      attWM4.SetVisibility(True)

      attWM8 = attribCreator.AddInteger(OTC_WELD_CHARACTER_DEF, 4, 1, 10, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_CHARACTER)
      attWM8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM8.SetReadOnly(False)
      attWM8.SetVisibility(False)

      attWM5 = attribCreator.AddInteger(OTC_WIRE_FEED_DEF, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WIRE_FEED)
      attWM5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM5.SetReadOnly(False)
      attWM5.SetVisibility(False)

      attWM6 = attribCreator.AddInteger(OTC_CURRENT_DEF, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_CURRENT)
      attWM6.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM6.SetReadOnly(False)
      attWM6.SetVisibility(False)

      attWM7 = attribCreator.AddInteger(OTC_VOLTAGE_DEF, 0, 0, 9999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_VOLTAGE)
      attWM7.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM7.SetReadOnly(False)
      attWM7.SetVisibility(False)

      attWM8 = attribCreator.AddString(OTC_UNIT_MECHS, OTC_UNIT_MECHS_LIST[0], GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_UNIT_MECHS)
      attWM8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attWM8.SetReadOnly(True)
      attWM8.SetVisibility(True)

      stitchPulseAsCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AS_COND_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AS_COND)
      stitchPulseAsCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseAsCond.SetVisibility(False)
      stitchPulseAeCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AE_COND_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AE_COND)
      stitchPulseAeCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseAeCond.SetVisibility(False)
      stitchPulseEnabled = attribCreator.AddBool(OTC_STITCH_PULSE_ENABLED_DEF, False, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_ENABLED)
      stitchPulseEnabled.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseEnabled.SetVisibility(True)
      stitchPulseWeldingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_WELDING_TIME_DEF,0.7, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_WELDING_TIME)
      stitchPulseWeldingTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseWeldingTime.SetVisibility(False)
      stitchPulseCoolingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_COOLING_TIME_DEF,0.2, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_COOLING_TIME)
      stitchPulseCoolingTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseCoolingTime.SetVisibility(False)
      stitchPulseMovementTime = attribCreator.AddDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF,0.004, 0.0, 0.1, 0.001, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, OTC_STITCH_PULSE_MOVEMENT_PITCH)
      stitchPulseMovementTime.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseMovementTime.SetVisibility(False)
      stitchPulseMoveCondNumber = attribCreator.AddInteger(OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF, 0, 0, 999, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_MOVE_COND_NUMBER)
      stitchPulseMoveCondNumber.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      stitchPulseMoveCondNumber.SetVisibility(False)
      
      #logging.LogInfo('...........................GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)')
      attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
      attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | USER_ATTRIBUTE)
      attConnectionType.SetVisibility(True)
      #logging.LogInfo('...........................')

      # Weave condition
      useWeave = attribCreator.AddBool(OTC_USE_WEAVE_DEF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_USE_WEAVE)
      useWeave.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      weaveCond = attribCreator.AddInteger(OTC_WEAVE_COND_NR_DEF, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WEAVE_COND_NR)
      weaveCond.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      weaveCond.SetVisibility(False)

      # Hide original Weave attributes
      #logging.LogInfo('...........................GetAttributeByName(UseWeaveDefine)')
      weave = attribGetter.GetAttributeByName('UseWeaveDefine')
      weave.SetVisibility(False)
      #logging.LogInfo('...........................')

      # Arc Sensing (FD-AR) attributes
      arcSensorId = attribCreator.AddInteger(AW_ARCSENSE_ST_SENSOR_ID, 1, 1, 12, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_SENSOR_ID)
      arcSense = attribCreator.AddBool(AW_ARCSENSE_DEF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE)
      arcSense.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      arcSenseStCondFile = attribCreator.AddInteger(AW_ARCSENSE_ST_COND_FILE_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_COND_FILE)
      arcSenseStCondFile.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      arcSenseStSampleData = attribCreator.AddInteger(AW_ARCSENSE_ST_SAMPLE_DATA_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_SAMPLE_DATA)
      arcSenseStSampleData.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      ArcSenseEtCondFile = attribCreator.AddInteger(AW_ARCSENSE_ET_COND_FILE_DEF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ET_COND_FILE)
      ArcSenseEtCondFile.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      # Laser Tracking Start - ZT
      laserSensorId = attribCreator.AddInteger(AW_LASER_SENSOR_ID, 1, 1, 12, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SENSOR_ID)
      laserFovX = attribCreator.AddDouble(AW_LASER_FOV_X,0.05, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_X)
      laserFovY = attribCreator.AddDouble(AW_LASER_FOV_Y,0.0, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Y)
      laserFovZ = attribCreator.AddDouble(AW_LASER_FOV_Z,-0.04, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Z)
      laserFovA = attribCreator.AddDouble(AW_LASER_FOV_RX,0.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RX)
      laserFovB = attribCreator.AddDouble(AW_LASER_FOV_RY,20.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RY)
      laserFovC = attribCreator.AddDouble(AW_LASER_FOV_RZ,0.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RZ)
      laserZtGFF = attribCreator.AddInteger(AW_LASER_ZT_GFF, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_GFF)
      laserZtLSR = attribCreator.AddInteger(AW_LASER_ZT_LSR, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_LSR)
      laserZtPosRegister = attribCreator.AddInteger(AW_LASER_ZT_POS_REGISTER, 1, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_POS_REGISTER)
      laserZtPosture = attribCreator.AddInteger(AW_LASER_ZT_POSTURE, 0, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZT_POSTURE)

      # Laser Tracking End - ZE
      laserZeStoreNumber = attribCreator.AddInteger(AW_LASER_ZE_STORE_NUMBER, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZE_STORE_NUMBER)
      laserZeStoreCoordinate = attribCreator.AddInteger(AW_LASER_ZE_STORE_COORDINATE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZE_STORE_COORDINATE)
      laserZeOverDevRange = attribCreator.AddDouble(AW_LASER_ZE_OVER_DEV_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZE_OVER_DEV_RANGE)

      # Laser Seam Start Search - ZF
      laserZfOn = attribCreator.AddBool(AW_LASER_ZF_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_ON)
      laserZfGFF = attribCreator.AddInteger(AW_LASER_ZF_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_GFF)
      laserZfLSR = attribCreator.AddInteger(AW_LASER_ZF_LSR, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_LSR)
      laserZfPosRegister = attribCreator.AddInteger(AW_LASER_ZF_POS_REGISTER, 1, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_POS_REGISTER)
      laserZfPosture = attribCreator.AddInteger(AW_LASER_ZF_POSTURE, 0, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_POSTURE)
      laserZfStoreNumber = attribCreator.AddInteger(AW_LASER_ZF_STORE_NUMBER, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_STORE_NUMBER)
      laserZfStoreCoordinate = attribCreator.AddInteger(AW_LASER_ZF_STORE_COORDINATE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZF_STORE_COORDINATE)
      laserZfSearchRange = attribCreator.AddDouble(AW_LASER_ZF_SEARCH_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_SEARCH_RANGE)
      laserZfOffset = attribCreator.AddDouble(AW_LASER_ZF_OFFSET,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_OFFSET)
      laserZfSpeed = attribCreator.AddDouble(AW_LASER_ZF_SPEED,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZF_SPEED)

      # Laser Seam Start Search - ZF
      laserZnOn = attribCreator.AddBool(AW_LASER_ZN_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_ON)
      laserZnGFF = attribCreator.AddInteger(AW_LASER_ZN_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_GFF)
      laserZnLSR = attribCreator.AddInteger(AW_LASER_ZN_LSR, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZN_LSR)
      laserZnOffset = attribCreator.AddDouble(AW_LASER_ZN_OFFSET,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZN_OFFSET)
      laserZnSearchRange = attribCreator.AddDouble(AW_LASER_ZN_SEARCH_RANGE,0.0, 0.0, 0.999, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZN_SEARCH_RANGE)


      # Laser Seam Search - ZJ
      laserZjOn = attribCreator.AddBool(AW_LASER_ZJ_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_ON)
      laserZjOn.SetReComputeEnterState(ENTERSTATE_COMPLETE)
      laserZjGFF = attribCreator.AddInteger(AW_LASER_ZJ_GFF, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GFF)
      laserZjGAP = attribCreator.AddInteger(AW_LASER_ZJ_GAP, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GAP)
      laserZjStoreNumber = attribCreator.AddInteger(AW_LASER_ZJ_STORE_NUMBER, 0, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_NUMBER)
      laserZjBasePositionY = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Y, 0.0, -0.10, 0.10, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Y)
      laserZjBasePositionY.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserZjBasePositionZ = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Z, 0.0, -0.10, 0.10, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Z)
      laserZjBasePositionZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserZjSearchWaitDelay = attribCreator.AddDouble(AW_LASER_ZJ_SEARCH_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_SEARCH_DELAY)
      laserZjSearchStableDelay = attribCreator.AddDouble(AW_LASER_ZJ_STABLE_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_STABLE_DELAY)
      
      laserZjStoreCoordinates = attribCreator.AddEnum(AW_LASER_ZJ_STORE_COORDINATES, AW_LASER_ZJ_STORE_LIT, AW_LASER_ZJ_STORE_LIT[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_COORDINATES)
   
      laserZjDevComposition = attribCreator.AddBool(AW_LASER_ZJ_DEV_COMPOSITION, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_DEV_COMPOSITION)
      laserZjAutoManualModify = attribCreator.AddBool(AW_LASER_ZJ_AUTO_MANUAL_MODIFY, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_AUTO_MANUAL_MODIFY)
   
      laserZjDeviationLength = attribCreator.AddDouble(AW_LASER_ZJ_DEVIATION_LENGTH, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_DEVIATION_LENGTH)
      laserZjMinDepthValue = attribCreator.AddDouble(AW_LASER_ZJ_MIN_DEPTH_VALUE, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_MIN_DEPTH_VALUE)
      laserZjGapWatchRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MAX, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MAX)
      laserZjGapWatchRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MIN, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MIN)
      laserZjAngleOneRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX)
      laserZjAngleOneRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN)
      laserZjAngleTwoRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX)
      laserZjAngleTwoRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN, 0.0, 0.0, 360.0, 1.0, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN)
   
   if (lastVersion < 101):
      # --------------------------------------------------------------------------------------------
      # Download Flag for output all Positions in JOINT Mode
      attrib = attribGetter.GetAttributeByName(AW_DOWNLOAD_JOINTS_ONLY)
      if not attrib.IsValid():
         attribCreator.AddBool(AW_DOWNLOAD_JOINTS_ONLY, False, GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_DOWNLOAD_JOINTS_ONLY)
         #logging.LogInfo('...........................Python Update : created AW_DOWNLOAD_JOINTS_ONLY = "DownloadJointsOnly"')
      else:
         attrib.SetOlpProperty(GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
         #logging.LogInfo('...........................Python Update : already exist AW_DOWNLOAD_JOINTS_ONLY = "DownloadJointsOnly", set OlpProperty GlobalProcessUser')

   if (lastVersion < 110):
      
      #logging.LogInfo('...........................GetAttributeByName(Speed)')
      speed = attribGetter.GetAttributeDoubleByName('Speed')
      if speed.IsValid():
         #logging.LogInfo('.................................SetOlpPropertySpeed')
         speed.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)

   completeRecomputeNeeded = True   

   return completeRecomputeNeeded

def RemoveAttribute(Operator: CENPyOlpTech_UpdateOperator, component, Name):
   if component.GetType() < 4:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttribute(Operator, childComponent, Name)


def RemoveAttributeFromWM(Operator: CENPyOlpTech_UpdateOperator, component, Name, CreatorName):
   if component.GetType() < 4 and component.GetCreatorName()==CreatorName:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttributeFromWM(Operator, childComponent, Name, CreatorName)

   # ==               ==========================================================================================
def getRelatedDataSet(Operator, pgmnr):
   '''
   Check and returns if there is a related DataSet where the Program number fits.
   
   Args:
      Operator: the CENPyOlpProgramModifyOperator
      pgmnr : the Welding Program Number
      
   Returns:
      list: the List of the related DataSet or default
   '''
   controller = Operator.GetController()
   techTableList = controller.GetWeldingDataSetsFromDataBase()
   
   row = []
   if len(techTableList) > 0:
      for tableRow in techTableList:
         #self.__logging.LogInfo("....................tableRow:" + str(tableRow))
         if pgmnr == tableRow[0]:
            return tableRow
   return row