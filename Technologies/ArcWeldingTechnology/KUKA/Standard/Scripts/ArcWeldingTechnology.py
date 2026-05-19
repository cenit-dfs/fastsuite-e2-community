# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customization for KUKA KRC4/5
# Debug info: E2@localhost:5254
# Author: CENIT
# Changelog:
#     Version: 1.0
#        Changed by: Berauer
#        Date: 2024-07-25
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
import json
from pathlib import Path

# Define paths to TechTabs folder and JSON files
TECH_TABS_PATH = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
SEAMFIND_RECIPES_PATH = TECH_TABS_PATH + "SeamFind_Recipes.json"
SEAMFIND_PROFILES_PATH = TECH_TABS_PATH + "SeamFind_Sensor_Profiles.json"

# Load JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Populate SeamFinding constants
def SeamFindingPopulateConstants():
    global KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS, KUKA_SEAM_FINDING_RECIPE_LITERALS

    # Load data from JSON files
    recipes = load_json(SEAMFIND_RECIPES_PATH)
    profiles = load_json(SEAMFIND_PROFILES_PATH)["profiles"]

    # Extract names for literals
    KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS = [profile["name"] for profile in profiles]
    KUKA_SEAM_FINDING_RECIPE_LITERALS = [recipe["name"] for recipe in recipes]

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

# Attribute definition
AW_GLOBAL_TOUCH_COUNTER   = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
AW_TOUCHSENS_TOUCH_ID     = "TouchId"
AW_TOUCHSENS_FRAME_PT     = "FramePt"
MAX_INTEGER = 2147483647
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN ="TSSpeedFromCycleLin"
AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP ="TSSpeedFromCyclePtp"
AW_OPERATION_SORTED = "TSOperationsSorted"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_TOUCHSENSE_LINKED_TOUCH = "TSLinkedTouch"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"
AW_SEAM_CALIB_CAD_MASTERED = "SeamCalibCadMastered"

AW_KUKA_TECH_TAB_FOLDER = "KUKATechTabFolder"

ATTRIBUTE_GLOBAL_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_GROUP_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE

#ArcTech Global settings
KUKA_POWER_SOURCE = "KukaPowerSource"
KUKA_POWER_SOURCE_LIST = ["Standard","Fronius"]
KUKA_SINGLE_WDAT = "KukaSingleWDat"
KUKA_ADD_WDAT_INDEX = "KukaAddWDatIndex"
KUKA_ARCTECH_ADV = "KukaArcTechAdv"
KUKA_WEAVE_TYPE = "KukaWeaveType"
KUKA_WEAVE_TYPE_LIST = ["Weave length","Weave frequency"]
KUKA_SORT_DAT = "KukaSortDat"
KUKA_POWER_SOURCE_JOB_CANNEL = "KukaPowerSourceJobChannel"
KUKA_TRACK_ARCSENSE = "KukaTrackArcSense"
#Sensor Tool Types and related attribs
AW_SENSOR_TOOL_TYPE = "SensorToolType"
AW_SENSOR_TOOL_TYPE_LITERALS = ["Touch Sensor", "Point Laser", "Line Laser"]
AW_SENSOR_ID_TOUCH = "SensorIdTouch"
AW_SENSOR_ID_POINT = "SensorIdPoint"
AW_SENSOR_ID_LINE = "SensorIdLine"
AW_TOUCH_METHOD = "TSTouchMethod"
AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE = "TouchDifferenceAngleNozzle"
AW_TOUCH_DIFF_ANGLE = "TouchDifferenceAngle"
#Laser Scanner attribs
AW_SEARCH_DEVICE = "SearchDev"
AW_SEARCH_DEVICE_LIST = ["Touch","LineLaser","PointLaser"]
AW_LASER_FOV_X = "LaserFovX"
AW_LASER_FOV_Y = "LaserFovY"
AW_LASER_FOV_Z = "LaserFovZ"
AW_LASER_FOV_RX = "LaserFovA"
AW_LASER_FOV_RY = "LaserFovB"
AW_LASER_FOV_RZ = "LaserFovC"
#SeamFinding related attribs
KUKA_SEAM_FINDING_MOUNT_TYPE = "KukaSeamFindingMountType"
KUKA_SEAM_FINDING_RECIPE = "KukaSeamFindingRecipe"
SeamFindingPopulateConstants()
# KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS = []
# KUKA_SEAM_FINDING_RECIPE_LITERALS = []
#The following constants are being used to both Technology *Define and Event * naming
#ArcOn Ignition definitions
KUKA_IGNITION_PROGRAM_NUMBER = "KukaIgnitionProgNumber"
KUKA_IGNITION_PARAM_SET = "KukaIgnitionParmSet"
KUKA_PRE_FLOW_TIME = "KukaPreflowTime"
KUKA_ON_THE_FLY_ACTIVE = "KukaOnTheFlyActive"
KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME = "KukaOnTheFlyGasPreflowTime"
KUKA_WAIT_TIME_AFTER_IGNITION = "KukaWaitTimeAfterIgnition"
#ArcOn Weld definitions
KUKA_WELD_JOB_NUMBER = "KukaProgNumber"
KUKA_WELD_PARAM_SET = "KukaWeldParmSet"
KUKA_ROBOT_VELOCITY_1 = "KukaRobotVelocity1"
#ArcOn Weaving definition
KUKA_WEAVE_PATTERN = "KukaWeavePattern"
KUKA_WEAVE_LENGTH = "KukaWeaveLength"
KUKA_WEAVE_FREQUENCY = "KukaWeaveFrequency"
KUKA_WEAVE_DEFLECTION="KukaWeaveDeflection"
KUKA_WEAVE_ANGLE="KukaWeaveAngle"
#ArcSense Definition
KUKA_ARCSENSE = "KukaArcSense"
KUKA_ARCSENSE_PATTERN = "KukaArcSensePattern"
KUKA_ARCSENSE_PATTERN_LIST = ["None","Trapecoid","Triangle"]
KUKA_ARCSENSE_LATCTRLGAIN = "KukaArcSenseLatCtrlGain"
KUKA_ARCSENSE_HEIGHTCTRL = "KukaArcSenseHeightCtrl"
KUKA_ARCSENSE_LATBIAS = "KukaArcSenseLatBias"
KUKA_ARCSENSE_MAXCORR = "KukaArcSenseMaxCorr"
KUKA_ARCSENSE_FINDCENTER = "KukaArcSenseFindCenter"
KUKA_ARCSENSE_ACTIVDELAY = "KukaArcSenseActivDelay"
#ArcOff Definition
KUKA_ARC_OFF_JOB_NUMBER = "KukaArcOffJobNumber"
KUKA_END_CRATER_TIME = "KukaEndCraterTime"
KUKA_ARC_OFF_PARAM_SET = "KukaArcOffParmSet"
KUKA_POST_FLOW_TIME = "KukaPostFlowTime"

#The following constants are being used to define the attribute names in Technology only. Event attributes come without the *Define
#ArcOn definitions
KUKA_IGNITION_PROGRAM_NUMBER_DEFINE = "KukaIgnitionProgNumberDefine"
KUKA_IGNITION_PARAM_SET_DEFINE = "KukaIgnitionParmSetDefine"
KUKA_PRE_FLOW_TIME_DEFINE = "KukaPreflowTimeDefine"
KUKA_ON_THE_FLY_ACTIVE_DEFINE = "KukaOnTheFlyActiveDefine"
KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE = "KukaOnTheFlyGasPreflowTimeDefine"
KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE = "KukaWaitTimeAfterIgnitionDefine"
KUKA_WELD_JOB_NUMBER_DEFINE = "KukaProgNumberDefine"
KUKA_WELD_PARAM_SET_DEFINE = "KukaWeldParmSetDefine"
KUKA_ROBOT_VELOCITY_1_DEFINE = "KukaRobotVelocity1Define"
#Weaving definition
KUKA_WEAVE_PATTERN_DEFINE = "KukaWeavePatternDefine"
# KUKA_WEAVE_PATTERN_LIST = ["None","Spiral","Trapecoid","Triangle","UnsymetricTrapecoid","On Seam"]
KUKA_WEAVE_PATTERN_LIST = ["None","Spiral","Trapecoid","Triangle","UnsymetricTrapecoid","Spiral", "Double8", "OnSeam", "EdgeBottom", "EdgeTop", "UserDefined1", "UserDefined2"]
KUKA_WEAVE_LENGTH_DEFINE = "KukaWeaveLengthDefine"
KUKA_WEAVE_FREQUENCY_DEFINE = "KukaWeaveFrequencyDefine"
KUKA_WEAVE_DEFLECTION_DEFINE = "KukaWeaveDeflectionDefine"
KUKA_WEAVE_ANGLE_DEFINE = "KukaWeaveAngleDefine"
#ArcSense Definition
KUKA_ARCSENSE_DEFINE = "KukaArcSenseDefine"
KUKA_ARCSENSE_PATTERN_DEFINE = "KukaArcSensePatternDefine"
KUKA_ARCSENSE_LATCTRLGAIN_DEFINE = "KukaArcSenseLatCtrlGainDefine"
KUKA_ARCSENSE_HEIGHTCTRL_DEFINE = "KukaArcSenseHeightCtrlDefine"
KUKA_ARCSENSE_LATBIAS_DEFINE = "KukaArcSenseLatBiasDefine"
KUKA_ARCSENSE_MAXCORR_DEFINE = "KukaArcSenseMaxCorrDefine"
KUKA_ARCSENSE_FINDCENTER_DEFINE = "KukaArcSenseFindCenterDefine"
KUKA_ARCSENSE_ACTIVDELAY_DEFINE = "KukaArcSenseActivDelayDefine"
#ArcOff Definition
KUKA_ARC_OFF_JOB_NUMBER_DEFINE = "KukaArcOffJobNumberDefine"
KUKA_END_CRATER_TIME_DEFINE = "KukaEndCraterTimeDefine"
KUKA_ARC_OFF_PARAM_SET_DEFINE = "KukaArcOffParmSetDefine"
KUKA_POST_FLOW_TIME_DEFINE = "KukaPostFlowTimeDefine"

#Spline Definition
KUKA_SPTP_SLIN = "SPtpSLin"

#SeamFinding Definition
KUKA_SEAMFIND_ID = "SeamFindingId"
# ToDo: move to method and script for auto Literal addition from Backup/Onsite-IP "..KRC\R1\TP\SeamTechFinding\Sensor\bfs_interface.dat"
KUKA_SEAMFIND_JOINTTYPE = "SeamFindingJointType"
# KUKA_SEAMFIND_JOINTTYPE_LIST=["255-Calibration-D3","2-KEHL_ST_WIG-4","5-ECK_ALU_2mm-4","9-STUMPF_VA_1mm_ohne_Spalt-3","10-STUMPF_ST_1mm_ohne_Spalt-3","11-ECK_VA_WIG-4","21-ECK_ST_MAG-4","31-KEHL_ST_MAG-4","41-ECK_ST_WIG-4"]
KUKA_SEAMFIND_JOINTTYPE_LIST=["1-Corner joint-4","2-Fillet joint-4","3-Butt joint-3","4-Lap joint-3","5-V Groove joint-3","6-Half V Groove joint-3","7-J Groove joint-3","8-TWB join-3","9-Melt run-2","10-Dot-1","42-CENIT Corner-4"]

KUKA_SEAMTRACK_SEARCH_START = "SeamTrackSearchStart"
KUKA_SEAMTRACK_SEARCH_SPEED = "SeamTrackSearchSpeed"

# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator: CENPyOlpTech_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   # attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 0, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   # sf02 = attribCreator.AddInteger(AW_TOUCHSENS_TOUCH_ID, 0,0,999, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_TOUCHSENS_TOUCH_ID)
   # sf02.SetVisibility(True)
   # sf03 = attribCreator.AddInteger(AW_TOUCHSENS_FRAME_PT, 0,0,3, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_TOUCHSENS_FRAME_PT)
   # sf03.SetVisibility(True)
   
   #ArcTech Global settings
   attribInteger = attribCreator.AddInteger(KUKA_POWER_SOURCE_JOB_CANNEL,1,1,8,ATTRIBUTE_GLOBAL_LEVEL,KUKA_POWER_SOURCE_JOB_CANNEL)
   attribBool = attribCreator.AddBool(KUKA_SORT_DAT,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_SORT_DAT)
   attribIntENM = attribCreator.AddEnum(KUKA_POWER_SOURCE,KUKA_POWER_SOURCE_LIST,KUKA_POWER_SOURCE_LIST[1],ATTRIBUTE_GLOBAL_LEVEL,KUKA_POWER_SOURCE)
   attribBool = attribCreator.AddBool(KUKA_SINGLE_WDAT,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_SINGLE_WDAT)
   attribBool = attribCreator.AddBool(KUKA_ADD_WDAT_INDEX,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_ADD_WDAT_INDEX)
   attribIntENM = attribCreator.AddEnum(KUKA_WEAVE_TYPE,KUKA_WEAVE_TYPE_LIST,KUKA_POWER_SOURCE_LIST[1],ATTRIBUTE_GLOBAL_LEVEL,KUKA_WEAVE_TYPE)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_ARCTECH_ADV,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_ARCTECH_ADV)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_TRACK_ARCSENSE,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_TRACK_ARCSENSE)

   # attribIntENM = attribCreator.AddEnum(AW_SEARCH_DEVICE,AW_SEARCH_DEVICE_LIST,AW_SEARCH_DEVICE_LIST[1],ATTRIBUTE_LEVEL,AW_SEARCH_DEVICE)
   # attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # LaserScanner settings
   laserFovX = attribCreator.AddDouble(AW_LASER_FOV_X,0.0, -0.999, 0.999, 0.001, ATTRIBUTE_LEVEL, ATTRIB_LENGTH, AW_LASER_FOV_X)
   laserFovX.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserFovY = attribCreator.AddDouble(AW_LASER_FOV_Y,0.005, -0.999, 0.999, 0.001, ATTRIBUTE_LEVEL, ATTRIB_LENGTH, AW_LASER_FOV_Y)
   laserFovY.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserFovZ = attribCreator.AddDouble(AW_LASER_FOV_Z,-0.028, -0.999, 0.999, 0.001, ATTRIBUTE_LEVEL, ATTRIB_LENGTH, AW_LASER_FOV_Z)
   laserFovZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserFovA = attribCreator.AddDouble(AW_LASER_FOV_RX,0, -90, 90, 5, ATTRIBUTE_LEVEL, ATTRIB_ANGLE, AW_LASER_FOV_RX)
   laserFovA.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserFovB = attribCreator.AddDouble(AW_LASER_FOV_RY,0.0, -90, 90, 5, ATTRIBUTE_LEVEL, ATTRIB_ANGLE, AW_LASER_FOV_RY)
   laserFovB.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   laserFovC = attribCreator.AddDouble(AW_LASER_FOV_RZ,0.0, -90, 90, 5, ATTRIBUTE_LEVEL, ATTRIB_ANGLE, AW_LASER_FOV_RZ)
   laserFovC.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   #ArcOn definitions
   attribDouble = attribCreator.AddDouble(KUKA_PRE_FLOW_TIME_DEFINE,0.0,-100,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_PRE_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attOnTheFly = attribCreator.AddBool(KUKA_ON_THE_FLY_ACTIVE_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ON_THE_FLY_ACTIVE)
   attOnTheFly.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_WAIT_TIME_AFTER_IGNITION)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(KUKA_IGNITION_PROGRAM_NUMBER_DEFINE,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_IGNITION_PROGRAM_NUMBER)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_IGNITION_PARAM_SET_DEFINE,'Set1',ATTRIBUTE_LEVEL,KUKA_IGNITION_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(KUKA_WELD_JOB_NUMBER_DEFINE,1,0, MAX_INTEGER, ATTRIBUTE_LEVEL,KUKA_WELD_JOB_NUMBER)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_WELD_PARAM_SET_DEFINE,'Set1',ATTRIBUTE_LEVEL,KUKA_WELD_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ROBOT_VELOCITY_1_DEFINE,0.5,0,99,0.1,ATTRIBUTE_LEVEL,ATTRIB_STANDARD,KUKA_ROBOT_VELOCITY_1)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(KUKA_WEAVE_PATTERN_DEFINE,KUKA_WEAVE_PATTERN_LIST,KUKA_WEAVE_PATTERN_LIST[0],ATTRIBUTE_LEVEL,KUKA_WEAVE_PATTERN)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_LENGTH_DEFINE,0.004,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH, KUKA_WEAVE_LENGTH)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_FREQUENCY_DEFINE,1.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_FREQUENCY, KUKA_WEAVE_FREQUENCY)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_DEFLECTION_DEFINE,0.002,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH, KUKA_WEAVE_DEFLECTION)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_ANGLE_DEFINE,0.0,-90,90,1,ATTRIBUTE_LEVEL,ATTRIB_ANGLE, KUKA_WEAVE_ANGLE)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble.SetVisibility(False)

   #ArcSense Definition
   attribBool = attribCreator.AddBool(KUKA_ARCSENSE_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ARCSENSE)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(KUKA_ARCSENSE_PATTERN_DEFINE,KUKA_ARCSENSE_PATTERN_LIST,KUKA_ARCSENSE_PATTERN_LIST[0],ATTRIBUTE_LEVEL,KUKA_ARCSENSE_PATTERN)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATCTRLGAIN_DEFINE,50.0,0.0,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_LATCTRLGAIN)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_HEIGHTCTRL_DEFINE,50.0,0.0,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_HEIGHTCTRL)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATBIAS_DEFINE,50.0,-100,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_LATBIAS)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_MAXCORR_DEFINE,0.025,0.001,0.3,0.001,ATTRIBUTE_LEVEL, ATTRIB_LENGTH, KUKA_ARCSENSE_MAXCORR)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_ARCSENSE_FINDCENTER_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ARCSENSE_FINDCENTER)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_ACTIVDELAY_DEFINE,0.0,0.0,10.0,1,ATTRIBUTE_LEVEL, ATTRIB_TIME, KUKA_ARCSENSE_ACTIVDELAY)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   #ArcOff definitions
   attribInteger = attribCreator.AddInteger(KUKA_ARC_OFF_JOB_NUMBER_DEFINE,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_ARC_OFF_JOB_NUMBER)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_ARC_OFF_PARAM_SET_DEFINE,'Set2',ATTRIBUTE_LEVEL,KUKA_ARC_OFF_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_END_CRATER_TIME_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_END_CRATER_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_SPTP_SLIN,False,ATTRIBUTE_LEVEL,KUKA_SPTP_SLIN)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_POST_FLOW_TIME_DEFINE,0.0,-100,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_POST_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   #SeamFinding Definition
   attribInteger = attribCreator.AddInteger(KUKA_SEAMFIND_ID,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_SEAMFIND_ID)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(KUKA_SEAMFIND_JOINTTYPE,KUKA_SEAMFIND_JOINTTYPE_LIST,KUKA_SEAMFIND_JOINTTYPE_LIST[0],ATTRIBUTE_LEVEL,KUKA_SEAMFIND_JOINTTYPE)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribENM = attribCreator.AddEnum(KUKA_SEAM_FINDING_MOUNT_TYPE,KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS,KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS[1],ATTRIBUTE_LEVEL,KUKA_SEAM_FINDING_MOUNT_TYPE)
   attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribENM = attribCreator.AddEnum(KUKA_SEAM_FINDING_RECIPE,KUKA_SEAM_FINDING_RECIPE_LITERALS,KUKA_SEAM_FINDING_RECIPE_LITERALS[1],ATTRIBUTE_LEVEL,KUKA_SEAM_FINDING_RECIPE)
   attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # User CAD coordinates as mastering position, if not set, the program will force the used to touch-up the calibration points
   attribBool = attribCreator.AddBool(AW_SEAM_CALIB_CAD_MASTERED,True,ATTRIBUTE_GLOBAL_LEVEL,AW_SEAM_CALIB_CAD_MASTERED)

   #Connection Types
   attConnectionType = attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE)
   attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
   attConnectionType.AddLiteral("Frame3pConnect")

   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN,0.5,0.0,1,0.1,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED,AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
   attribDouble.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP,50,0.0,100,5,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_PERCENT,AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP)
   attribBool = attribCreator.AddBool(AW_TOUCHSENSE_LINKED_TOUCH,False,USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_TOUCHSENSE_LINKED_TOUCH)

   sensorType_index = attribCreator.AddEnum(AW_SENSOR_TOOL_TYPE, AW_SENSOR_TOOL_TYPE_LITERALS, "Touch Sensor", USER_ATTRIBUTE|PROCESS_ATTRIBUTE|GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE, AW_SENSOR_TOOL_TYPE)
   sensorType_index.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_TOUCH,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_TOUCH)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_POINT,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_POINT)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_LINE,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_LINE)

   #Seam tracking
   attribSeamTrackSearchStart = attribCreator.AddBool(KUKA_SEAMTRACK_SEARCH_START, True, ATTRIBUTE_LEVEL, KUKA_SEAMTRACK_SEARCH_START)
   attribSeamTrackSearchStart.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribSeamTrackSearchSpeed = attribCreator.AddDouble(KUKA_SEAMTRACK_SEARCH_SPEED,0.01,0.0,1,0.01,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED,KUKA_SEAMTRACK_SEARCH_SPEED)
   attribSeamTrackSearchStart.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Technology post event initialization
def PostTechInitEvents(Operator: CENPyOlpTech_EventInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   # YOUR CODE
   # Operator.RegisterPyTechnologyEvent("ArcSwitchEvent.py")
   Operator.RegisterPyTechnologyEvent("SPTP_SLIN.py")

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)
   pass

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


# -------------------------------------------------------------------------------------------
# Technology PrevExecuteRecipe
# def PrevExecuteRecipe(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)
#    pass

# -------------------------------------------------------------------------------------------
# Technology post process operation group attributes
# def PostProcessOperationGroupAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator: CENPyOlpTech_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()
   attribName = changedAttrib.GetName()
   #logging.LogInfo('..................PostTechOnAttribChanged with Attribute =' + str(attribName))

   if(attribName == AW_SEAM_CALIBRATION_METHOD):
      seamCalibMethodIdx = attribGetter.GetEnumIndex(AW_SEAM_CALIBRATION_METHOD)
      if seamCalibMethodIdx > 0 and seamCalibMethodIdx < 4: # TS, SeamSearch, SeamFind
         attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE).SetVisibility(True)
      else:
         attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE).SetVisibility(False)

      if seamCalibMethodIdx == 1 or seamCalibMethodIdx == 2: # TS, SeamSearch
         attribGetter.GetAttributeBoolByName(AW_OPERATION_SORTED).SetVisibility(True)
      else:
         attribGetter.GetAttributeBoolByName(AW_OPERATION_SORTED).SetVisibility(False)

   if (attribName == 'TouchSensMotionTypeFirstTpe'):
      touchOpMotionType = attribGetter.GetEnumIndex('TouchSensMotionTypeFirstTpe')
      if touchOpMotionType == 1: # Linear 
         attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN).SetVisibility(True)
         attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP).SetVisibility(False)
      else: # PTP
         attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN).SetVisibility(False)
         attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP).SetVisibility(True)
      
   # Show/hide sensor tool related options
   tsTouchMethod = attribGetter.GetAttributeEnumByName(AW_TOUCH_METHOD)
   if(attribName == AW_SENSOR_TOOL_TYPE):
      tsTouchMethod.SetVisibility(True)
      sensorToolTypeAttrib = attribGetter.GetAttributeEnumByName(AW_SENSOR_TOOL_TYPE)
      sensorTypeLiteralIndex = sensorToolTypeAttrib.GetLiteralIndex()
      sensorIdTouch = attribGetter.GetAttributeIntegerByName(AW_SENSOR_ID_TOUCH)
      sensorIdPoint = attribGetter.GetAttributeIntegerByName(AW_SENSOR_ID_POINT)
      sensorIdLine = attribGetter.GetAttributeIntegerByName(AW_SENSOR_ID_LINE)
      seamFindId = attribGetter.GetAttributeIntegerByName(KUKA_SEAMFIND_ID)
      seamFindJointType = attribGetter.GetAttributeEnumByName(KUKA_SEAMFIND_JOINTTYPE)
      seamFindMountType = attribGetter.GetAttributeEnumByName(KUKA_SEAM_FINDING_MOUNT_TYPE)
      seamFindRecipe = attribGetter.GetAttributeEnumByName(KUKA_SEAM_FINDING_RECIPE)
      if(sensorTypeLiteralIndex == 0): # "Touch Sensor"
         sensorIdTouch.SetVisibility(True)
         sensorIdPoint.SetVisibility(False)
         sensorIdLine.SetVisibility(False)
         literalIndex = tsTouchMethod.GetLiteralIndex()
         seamFindId.SetVisibility(False)
         seamFindJointType.SetVisibility(False)
         seamFindMountType.SetVisibility(False) 
         seamFindRecipe.SetVisibility(False)
         attribSetter.SetBool(AW_SEAM_CALIB_CAD_MASTERED, True, 0) # Force CAD mastered for Touch Sensor
         if(literalIndex == 0): # "Detection with nozzle"
            attribSetter.SetDouble(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE, 8.0)
            return
         if(literalIndex == 1): # "Detection with wire"
            attribSetter.SetDouble(AW_TOUCH_DIFF_ANGLE, 45.0)
            return

      if(sensorTypeLiteralIndex == 1): # "Point Laser"
         sensorIdTouch.SetVisibility(False)
         sensorIdPoint.SetVisibility(True)
         sensorIdLine.SetVisibility(False)
         attribSetter.SetDouble(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE, 90.0)
         attribSetter.SetDouble(AW_TOUCH_DIFF_ANGLE, 90.0)
         tsTouchMethod.SetVisibility(False)
         seamFindId.SetVisibility(False)
         seamFindJointType.SetVisibility(False)
         seamFindMountType.SetVisibility(False) 
         seamFindRecipe.SetVisibility(False)
         attribSetter.SetBool(AW_SEAM_CALIB_CAD_MASTERED, True, 0) # Force CAD mastered for Touch Sensor
         return

      if(sensorTypeLiteralIndex == 2): # "Line Laser"
         wireMethod = attribSetter.SetEnumIndex(AW_TOUCH_METHOD,1,0) # Set to "Detection with wire"
         tsTouchMethod.SetVisibility(False)
         attribSetter.SetDouble(AW_TOUCH_DIFF_ANGLE, 45.0)
         attribGetter.GetAttributeDoubleByName(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE).SetVisibility(False)
         attribGetter.GetAttributeDoubleByName(AW_TOUCH_DIFF_ANGLE).SetVisibility(True)

         sensorIdTouch.SetVisibility(False)
         sensorIdPoint.SetVisibility(False)
         sensorIdLine.SetVisibility(True)
         tsTouchMethod.SetVisibility(False)
         seamFindId.SetVisibility(True)
         seamFindJointType.SetVisibility(True)
         seamFindMountType.SetVisibility(True) 
         seamFindRecipe.SetVisibility(True)
         attribSetter.SetBool(AW_SEAM_CALIB_CAD_MASTERED, False, 0) # Force CAD mastered for Touch Sensor
         return

   if(attribName == AW_TOUCH_METHOD):
      literalIndex = tsTouchMethod.GetLiteralIndex()

      if(literalIndex == 0): # "Detection with nozzle"
         attribSetter.SetDouble(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE, 8.0)
         return
      if(literalIndex == 1): # "Detection with wire"
         attribSetter.SetDouble(AW_TOUCH_DIFF_ANGLE, 45.0)
         return

   # Show/hide weaving options
   if (attribName == KUKA_WEAVE_PATTERN_DEFINE) or (attribName == KUKA_WEAVE_TYPE) or (attribName == KUKA_ARCSENSE_PATTERN_DEFINE):
      if (attribName == KUKA_WEAVE_PATTERN_DEFINE):
         weavePatternDefineAttrib = attribGetter.GetAttributeEnumByName(KUKA_WEAVE_PATTERN_DEFINE)
      elif (attribName == KUKA_ARCSENSE_PATTERN_DEFINE):
         weavePatternDefineAttrib = attribGetter.GetAttributeEnumByName(KUKA_ARCSENSE_PATTERN_DEFINE)

      if weavePatternDefineAttrib.IsValid():
         #logging.LogInfo('..................found Attribute KUKA_WEAVE_PATTERN_DEFINE=' + str(weavePatternDefineAttrib))
         weavePattern = weavePatternDefineAttrib.GetValue()
         #logging.LogInfo('...............................Value KUKA_WEAVE_PATTERN_DEFINE=' + str(weavePattern))
      
      weaveTypeAttrib = attribGetter.GetAttributeEnumByName(KUKA_WEAVE_TYPE)
      if weaveTypeAttrib.IsValid():
         #logging.LogInfo('..................found Attribute KUKA_WEAVE_TYPE=' + str(weaveTypeAttrib))
         weaveType = weaveTypeAttrib.GetValue()
         #logging.LogInfo('...............................Value KUKA_WEAVE_TYPE=' + str(weaveType))
      
      if weavePattern == "None":
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH_DEFINE)
         weave.SetVisibility(False)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY_DEFINE)
         weave.SetVisibility(False)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_DEFLECTION_DEFINE)
         weave.SetVisibility(False)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_ANGLE_DEFINE)
         weave.SetVisibility(False)
      else:  
         if weaveType == "Weave length":
            weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH_DEFINE)
            weave.SetVisibility(True)
            weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY_DEFINE)
            weave.SetVisibility(False)
         else:
            weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH_DEFINE)
            weave.SetVisibility(False)
            weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY_DEFINE)
            weave.SetVisibility(True)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_DEFLECTION_DEFINE)
         weave.SetVisibility(True)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_ANGLE_DEFINE)
         weave.SetVisibility(True)
      
   # Show/hide ArcTech Advanced options
   if (attribName == KUKA_ARCTECH_ADV):
      advancedOptions = attribGetter.GetBool(KUKA_ARCTECH_ADV)
      if advancedOptions:
         adv = attribGetter.GetAttributeByName(KUKA_PRE_FLOW_TIME_DEFINE)
         adv.SetVisibility(True)
         adv = attribGetter.GetAttributeByName(KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE)
         adv.SetVisibility(True)
         adv = attribGetter.GetAttributeByName(KUKA_END_CRATER_TIME_DEFINE)
         adv.SetVisibility(True)
         adv = attribGetter.GetAttributeByName(KUKA_POST_FLOW_TIME_DEFINE)
         adv.SetVisibility(True)
      else:
         adv = attribGetter.GetAttributeByName(KUKA_PRE_FLOW_TIME_DEFINE)
         adv.SetVisibility(False)
         adv = attribGetter.GetAttributeByName(KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE)
         adv.SetVisibility(False)
         adv = attribGetter.GetAttributeByName(KUKA_END_CRATER_TIME_DEFINE)
         adv.SetVisibility(False)
         adv = attribGetter.GetAttributeByName(KUKA_POST_FLOW_TIME_DEFINE)
         adv.SetVisibility(False)
   
   # Show/hide FlyBy distance
   if (attribName == KUKA_ON_THE_FLY_ACTIVE_DEFINE):
      flyByActive = attribGetter.GetBool(KUKA_ON_THE_FLY_ACTIVE_DEFINE)
      if flyByActive:
         flyBy = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE)
         flyBy.SetVisibility(True)
      else:
         flyBy = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE)
         flyBy.SetVisibility(False)
   
   pass

   if (attribName == KUKA_ARCSENSE_DEFINE):
      vBool = attribGetter.GetBool(KUKA_ARCSENSE_DEFINE)
      #ArcSense Definition
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_PATTERN_DEFINE)
      arcSense.SetVisibility(vBool)
      arcWeave = attribGetter.GetAttributeByName(KUKA_WEAVE_PATTERN_DEFINE)
      arcWeave.SetVisibility(not vBool)
      
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_LATCTRLGAIN_DEFINE)
      arcSense.SetVisibility(vBool)
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_HEIGHTCTRL_DEFINE)
      arcSense.SetVisibility(vBool)
      
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_LATBIAS_DEFINE)
      if vBool:
         arcSense.SetVisibility(attribGetter.GetBool(KUKA_ARCSENSE_FINDCENTER_DEFINE))
      else:
         arcSense.SetVisibility(False)
      
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_MAXCORR_DEFINE)
      arcSense.SetVisibility(vBool)
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_FINDCENTER_DEFINE)
      arcSense.SetVisibility(vBool)
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_ACTIVDELAY_DEFINE)
      arcSense.SetVisibility(vBool)

   if (attribName == KUKA_ARCSENSE_FINDCENTER_DEFINE):
      arcSense = attribGetter.GetAttributeByName(KUKA_ARCSENSE_LATBIAS_DEFINE)
      arcSense.SetVisibility(attribGetter.GetBool(KUKA_ARCSENSE_FINDCENTER_DEFINE))

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
   # 110 = R2025.1.3
   # 170 = R2025.1.4
   return 310

# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator : CENPyOlpTech_UpdateOperator):
   logging = Operator.GetLoggerOperator()
   logging.LogInfo('####################################################')
   logging.LogDebug("(Debug) Post tech update started.")
   lastVersion = Operator.GetLastSavedPythonTechnologyVersion()
   currentVersion = GetPythonTechnologyVersion()
   logging.LogInfo('Last script version: ' + str(lastVersion) + '. Current script version: ' + str(currentVersion))
   program = Operator.GetOlpProgram()
   attribGetter = Operator.GetAttribGetter(program)
   attribSetter = Operator.GetAttribSetter(program)
   attribCreator = Operator.GetAttribCreator(program)
      
   if (lastVersion < 8): 
      program = Operator.GetOlpProgram()      
      # attribGetter = Operator.GetAttribGetter(program)
      # RemoveAttribute(Operator,program,'ArcWeldingGlobalPortTouch')
      RemoveAttribute(Operator,program,KUKA_IGNITION_PARAM_SET_DEFINE)
      RemoveAttribute(Operator,program,KUKA_WELD_PARAM_SET_DEFINE)
      RemoveAttribute(Operator,program,KUKA_ARC_OFF_PARAM_SET_DEFINE)
      # RemoveAttribute(Operator,program,KUKA_IGNITION_PARAM_SET)
      # RemoveAttribute(Operator,program,KUKA_WELD_PARAM_SET)
      # RemoveAttribute(Operator,program,KUKA_ARC_OFF_PARAM_SET)

      attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 0, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
      #ArcTech Global settings
      attribInteger = attribCreator.AddInteger(KUKA_POWER_SOURCE_JOB_CANNEL,1,1,8,ATTRIBUTE_GLOBAL_LEVEL,KUKA_POWER_SOURCE_JOB_CANNEL)
      attribBool = attribCreator.AddBool(KUKA_SORT_DAT,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_SORT_DAT)
      attribIntENM = attribCreator.AddEnum(KUKA_POWER_SOURCE,KUKA_POWER_SOURCE_LIST,KUKA_POWER_SOURCE_LIST[1],ATTRIBUTE_GLOBAL_LEVEL,KUKA_POWER_SOURCE)
      attribBool = attribCreator.AddBool(KUKA_SINGLE_WDAT,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_SINGLE_WDAT)
      attribIntENM = attribCreator.AddEnum(KUKA_WEAVE_TYPE,KUKA_WEAVE_TYPE_LIST,KUKA_POWER_SOURCE_LIST[1],ATTRIBUTE_GLOBAL_LEVEL,KUKA_WEAVE_TYPE)
      attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribBool = attribCreator.AddBool(KUKA_ARCTECH_ADV,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_ARCTECH_ADV)
      attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribBool = attribCreator.AddBool(KUKA_TRACK_ARCSENSE,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_TRACK_ARCSENSE)
      # LaserScanner settings
      laserFovX = attribCreator.AddDouble(AW_LASER_FOV_X,-0.0065, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_X)
      laserFovX.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserFovY = attribCreator.AddDouble(AW_LASER_FOV_Y,-0.012, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Y)
      laserFovY.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserFovZ = attribCreator.AddDouble(AW_LASER_FOV_Z,0.005, -0.999, 0.999, 0.001, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_FOV_Z)
      laserFovZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserFovA = attribCreator.AddDouble(AW_LASER_FOV_RX,-15, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RX)
      laserFovA.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserFovB = attribCreator.AddDouble(AW_LASER_FOV_RY,0.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RY)
      laserFovB.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      laserFovC = attribCreator.AddDouble(AW_LASER_FOV_RZ,90.0, -90, 90, 5, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_FOV_RZ)
      laserFovC.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      #ArcOn definitions
      attribDouble = attribCreator.AddDouble(KUKA_PRE_FLOW_TIME_DEFINE,0.0,-100,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_PRE_FLOW_TIME)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attOnTheFly = attribCreator.AddBool(KUKA_ON_THE_FLY_ACTIVE_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ON_THE_FLY_ACTIVE)
      attOnTheFly.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_WAIT_TIME_AFTER_IGNITION)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribInteger = attribCreator.AddInteger(KUKA_IGNITION_PROGRAM_NUMBER_DEFINE,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_IGNITION_PROGRAM_NUMBER)
      attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribString = attribCreator.AddString(KUKA_IGNITION_PARAM_SET_DEFINE,'Set1',ATTRIBUTE_LEVEL,KUKA_IGNITION_PARAM_SET)
      attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribInteger = attribCreator.AddInteger(KUKA_WELD_JOB_NUMBER_DEFINE,1,0, MAX_INTEGER, ATTRIBUTE_LEVEL,KUKA_WELD_JOB_NUMBER)
      attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribString = attribCreator.AddString(KUKA_WELD_PARAM_SET_DEFINE,'Set1',ATTRIBUTE_LEVEL,KUKA_WELD_PARAM_SET)
      attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ROBOT_VELOCITY_1_DEFINE,0.5,0,99,0.1,ATTRIBUTE_LEVEL,ATTRIB_STANDARD,KUKA_ROBOT_VELOCITY_1)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribIntENM = attribCreator.AddEnum(KUKA_WEAVE_PATTERN_DEFINE,KUKA_WEAVE_PATTERN_LIST,KUKA_WEAVE_PATTERN_LIST[0],ATTRIBUTE_LEVEL,KUKA_WEAVE_PATTERN)
      attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_WEAVE_LENGTH_DEFINE,0.003,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH, KUKA_WEAVE_LENGTH)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble.SetVisibility(False)
      attribDouble = attribCreator.AddDouble(KUKA_WEAVE_FREQUENCY_DEFINE,1.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_FREQUENCY, KUKA_WEAVE_FREQUENCY)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble.SetVisibility(False)
      attribDouble = attribCreator.AddDouble(KUKA_WEAVE_DEFLECTION_DEFINE,0.0025,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH, KUKA_WEAVE_DEFLECTION)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble.SetVisibility(False)
      attribDouble = attribCreator.AddDouble(KUKA_WEAVE_ANGLE_DEFINE,0.0,-90,90,1,ATTRIBUTE_LEVEL,ATTRIB_ANGLE, KUKA_WEAVE_ANGLE)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble.SetVisibility(False)
      #ArcOff definitions
      attribInteger = attribCreator.AddInteger(KUKA_ARC_OFF_JOB_NUMBER_DEFINE,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_ARC_OFF_JOB_NUMBER)
      attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribString = attribCreator.AddString(KUKA_ARC_OFF_PARAM_SET_DEFINE,'Set2',ATTRIBUTE_LEVEL,KUKA_ARC_OFF_PARAM_SET)
      attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_END_CRATER_TIME_DEFINE,0.0,0,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_END_CRATER_TIME)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribBool = attribCreator.AddBool(KUKA_SPTP_SLIN,False,ATTRIBUTE_LEVEL,KUKA_SPTP_SLIN)
      attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      #SeamFinding Definition
      attribInteger = attribCreator.AddInteger(KUKA_SEAMFIND_ID,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,KUKA_SEAMFIND_ID)
      attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribIntENM = attribCreator.AddEnum(KUKA_SEAMFIND_JOINTTYPE,KUKA_SEAMFIND_JOINTTYPE_LIST,KUKA_SEAMFIND_JOINTTYPE_LIST[0],ATTRIBUTE_LEVEL,KUKA_SEAMFIND_JOINTTYPE)
      attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      # WorkMethod Attributes
      #RemoveAttribute(Operator,program,'SSSensingLength')
   if (lastVersion < 9): 
      attribDouble = attribCreator.AddDouble(KUKA_POST_FLOW_TIME_DEFINE,0.0,-100,100,1,ATTRIBUTE_LEVEL,ATTRIB_TIME,KUKA_POST_FLOW_TIME)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   if (lastVersion < 100): #R2024.2.2
      attribBool = attribCreator.AddBool(KUKA_ADD_WDAT_INDEX,True,ATTRIBUTE_GLOBAL_LEVEL,KUKA_ADD_WDAT_INDEX)
      attribGetter.GetAttributeIntegerByName(KUKA_POWER_SOURCE_JOB_CANNEL).SetOlpProperty(ATTRIBUTE_GLOBAL_LEVEL)
      attribGetter.GetAttributeEnumByName(KUKA_WEAVE_PATTERN).SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   if (lastVersion < 110): #R2025.1.3
      #ArcSense Definition
      attribBool = attribCreator.AddBool(KUKA_ARCSENSE_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ARCSENSE)
      attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribIntENM = attribCreator.AddEnum(KUKA_ARCSENSE_PATTERN_DEFINE,KUKA_ARCSENSE_PATTERN_LIST,KUKA_ARCSENSE_PATTERN_LIST[0],ATTRIBUTE_LEVEL,KUKA_ARCSENSE_PATTERN)
      attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATCTRLGAIN_DEFINE,50.0,0.0,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_LATCTRLGAIN)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_HEIGHTCTRL_DEFINE,50.0,0.0,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_HEIGHTCTRL)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATBIAS_DEFINE,50.0,-100,100.0,1,ATTRIBUTE_LEVEL, ATTRIB_PERCENT, KUKA_ARCSENSE_LATBIAS)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_MAXCORR_DEFINE,0.025,0.001,0.3,0.001,ATTRIBUTE_LEVEL, ATTRIB_LENGTH, KUKA_ARCSENSE_MAXCORR)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribBool = attribCreator.AddBool(KUKA_ARCSENSE_FINDCENTER_DEFINE,False,ATTRIBUTE_LEVEL,KUKA_ARCSENSE_FINDCENTER)
      attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_ACTIVDELAY_DEFINE,0.0,0.0,10.0,1,ATTRIBUTE_LEVEL, ATTRIB_TIME, KUKA_ARCSENSE_ACTIVDELAY)
      attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   if (lastVersion < 140): #R2025.1.3 Intecro
      attribGetter.GetAttributeBoolByName(AW_SEAM_CALIB_CAD_MASTERED).SetVisibility(False)
      attribGetter.GetAttributeDoubleByName(AW_LASER_FOV_RX).SetVisibility(True)
      attribGetter.GetAttributeDoubleByName(AW_LASER_FOV_RY).SetVisibility(True)
      attribGetter.GetAttributeDoubleByName(AW_LASER_FOV_RZ).SetVisibility(True)
      attribGetter.GetAttributeDoubleByName('SeamFindingSensingSpeed').SetOlpProperty(ATTRIBUTE_GLOBAL_LEVEL)
      attribGetter.GetAttributeEnumByName('SeamFindingSensingSpeed').SetOlpProperty(ATTRIBUTE_GLOBAL_LEVEL)
      attribGetter.GetAttributeEnumByName('TSConnectionType').SetOlpProperty(ATTRIBUTE_GLOBAL_LEVEL)

   if (lastVersion < 150): #R2025.1.3 Intecro
      #Seam tracking
      attribSeamTrackSearchStart = attribCreator.AddBool(KUKA_SEAMTRACK_SEARCH_START, True, ATTRIBUTE_LEVEL, KUKA_SEAMTRACK_SEARCH_START)
      attribSeamTrackSearchStart.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      #SeamFinding related attribs
      attribENM = attribCreator.AddEnum(KUKA_SEAM_FINDING_MOUNT_TYPE,KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS,KUKA_SEAM_FINDING_MOUNT_TYPE_LITERALS[1],ATTRIBUTE_GLOBAL_LEVEL,KUKA_SEAM_FINDING_MOUNT_TYPE)
      attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribENM = attribCreator.AddEnum(KUKA_SEAM_FINDING_RECIPE,KUKA_SEAM_FINDING_RECIPE_LITERALS,KUKA_SEAM_FINDING_RECIPE_LITERALS[1],ATTRIBUTE_GROUP_LEVEL,KUKA_SEAM_FINDING_RECIPE)
      attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)


   if (lastVersion < 210): #R2025.1.4 Intecro
      attribGetter.GetAttributeDoubleByName('KukaTrackingOnDistance').SetVisibility(True)
      attribGetter.GetAttributeDoubleByName('KukaTrackingOffDistance').SetVisibility(True)

   if (lastVersion < 230): #R2025.1.4 Intecro SeamTracking
      attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN,0.5,0.0,1,0.1,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED, AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
      attribSeamTrackSearchSpeed = attribCreator.AddDouble(KUKA_SEAMTRACK_SEARCH_SPEED,0.01,0.0,1,0.01,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED, KUKA_SEAMTRACK_SEARCH_SPEED)

   if (lastVersion < 250): #R2025.1.4 Intecro SeamTracking
      attribGetter.GetAttributeBoolByName(KUKA_SEAMTRACK_SEARCH_START).SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attribGetter.GetAttributeDoubleByName(KUKA_SEAMTRACK_SEARCH_SPEED).SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   if (lastVersion < 260): #R2025.1.4 Intecro TouchSensing 6D
      attribBool = attribCreator.AddBool(AW_TOUCHSENSE_LINKED_TOUCH,False,USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_TOUCHSENSE_LINKED_TOUCH)

   if (lastVersion < 280): #R2025.2.1 TouchSensing 6D
      attribGetter.GetAttributeBoolByName(AW_SEAM_CALIB_CAD_MASTERED).SetVisibility(True)
      attribGetter.GetAttributeBoolByName(AW_SEAM_CALIB_CAD_MASTERED).SetReadOnly(False)
      attribGetter.GetAttributeEnumByName('TouchSensMotionTypeFirstTpe').SetOlpProperty(ATTRIBUTE_LEVEL)

   if (lastVersion < 290): #R2025.2.2
      attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN).SetVisibility(False)
      attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP,50,0.0,100,5,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_PERCENT,AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP)

   if (lastVersion < 310): #R2025.2.2
      attribGetter.GetAttributeBoolByName(AW_TOUCHSENSE_LINKED_TOUCH).SetOlpProperty(ATTRIBUTE_LEVEL)

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
