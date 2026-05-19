# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customization for ABB IRC5
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

#ABB Welding Paramter
ABB_AW_SEAMDATANUMBER = "Seamdata Number"
ABB_AW_WELDDATANUMBER = "Welddata Number"
ABB_AW_WEAVEDATANUMBER = "Weavedata Number"
ABB_AW_TRACKDATANUMBER = "Trackdata Number"

TECH_TABS_PATH = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
ABB_TECH_DEFAULTS_FILE = os.path.join(TECH_TABS_PATH, 'ABB_IRC5_TECH.json')

def _load_defaults(path):
   try:
      with open(path, 'r', encoding='utf-8') as f:
         data = json.load(f)
      if isinstance(data, dict) and isinstance(data.get('defaults'), dict):
         return data.get('defaults')
   except Exception:
      pass
   return {}

# Load JSON data
def load_json(file_path):
   try:
      with open(file_path, "r", encoding="utf-8") as f:
         return json.load(f)
   except Exception:
      pass
   return {}

# Populate SeamFinding constants
def SeamFindingPopulateConstants():
    global ABB_SEAM_FINDING_MOUNT_TYPE_LITERALS, ABB_SEAM_FINDING_RECIPE_LITERALS

    # Load data from JSON files
    recipes = load_json(SEAMFIND_RECIPES_PATH)
    profiles = load_json(SEAMFIND_PROFILES_PATH)["profiles"]

    # Extract names for literals
    ABB_SEAM_FINDING_MOUNT_TYPE_LITERALS = [profile["name"] for profile in profiles]
    ABB_SEAM_FINDING_RECIPE_LITERALS = [recipe["name"] for recipe in recipes]

# Populate station configuration from downloader JSON
def PopulateStationConstants():
    global ABB_STATION_LIST, ABB_STATION_DEFAULT
    
    try:
        # Path to JSON in TechTabs folder
        json_path = os.path.join(TECH_TABS_PATH, 'ABB_IRC5_DL.json')
        json_path = os.path.normpath(json_path)
        
        # Load configuration JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        stations_config = config.get('stations', {})
        if stations_config.get('enabled', False):
            station_list = stations_config.get('list', [])
            default_index = stations_config.get('default', 1)
            
            # Extract setup_proc names as station identifiers
            ABB_STATION_LIST = []
            for station in station_list:
                setup_proc = station.get('setup_proc', f"Station{station.get('index', 0)}")
                ABB_STATION_LIST.append(setup_proc)
            
            # Set default based on default index
            if ABB_STATION_LIST:
                # Find station with matching index
                default_station = None
                for station in station_list:
                    if station.get('index') == default_index:
                        default_station = station.get('setup_proc', ABB_STATION_LIST[0])
                        break
                
                ABB_STATION_DEFAULT = default_station if default_station else ABB_STATION_LIST[0]
            else:
                ABB_STATION_DEFAULT = ""
        else:
            # Stations disabled, provide empty list
            ABB_STATION_LIST = []
            ABB_STATION_DEFAULT = ""
    
    except Exception as e:
        # Fallback to empty if JSON not found or invalid
        ABB_STATION_LIST = []
        ABB_STATION_DEFAULT = ""

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
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"

AW_ABB_TECH_TAB_FOLDER = "ABBTechTabFolder"

ATTRIBUTE_GLOBAL_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_GROUP_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE

#ArcTech Global settings
ABB_STATION = "ABBStation"
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
ABB_SEAM_FINDING_MOUNT_TYPE = "ABBSeamFindingMountType"
ABB_SEAM_FINDING_RECIPE = "ABBSeamFindingRecipe"
SeamFindingPopulateConstants()
#SeamFinding Definition
ABB_SEAMFIND_ID = "SeamFindingId"
# ToDo: move to method and script for auto Literal addition from Backup/Onsite-IP "..KRC\R1\TP\SeamTechFinding\Sensor\bfs_interface.dat"
ABB_SEAMFIND_JOINTTYPE = "SeamFindingJointType"
# ABB_SEAMFIND_JOINTTYPE_LIST=["255-Calibration-D3","2-KEHL_ST_WIG-4","5-ECK_ALU_2mm-4","9-STUMPF_VA_1mm_ohne_Spalt-3","10-STUMPF_ST_1mm_ohne_Spalt-3","11-ECK_VA_WIG-4","21-ECK_ST_MAG-4","31-KEHL_ST_MAG-4","41-ECK_ST_WIG-4"]
ABB_SEAMFIND_JOINTTYPE_LIST=["1-Corner joint-4","2-Fillet joint-4","3-Butt joint-3","4-Lap joint-3","5-V Groove joint-3","6-Half V Groove joint-3","7-J Groove joint-3","8-TWB join-3","9-Melt run-2","10-Dot-1","42-CENIT Corner-4"]

ABB_SEAMTRACK_SEARCH_START = "SeamTrackSearchStart"
ABB_SEAMTRACK_SEARCH_SPEED = "SeamTrackSearchSpeed"

# Machining tech type selection
ABB_MACHINING_TECH_TYPE = "MACHINING_TECH_TYPE"
ABB_MACHINING_TECH_TYPE_LITERALS = ["ArcWelding", "Machining"]
ABB_MACHINING_TECH_TYPE_DEFAULT = "ArcWelding"

# Machining data attributes
ABB_MACH_PROCESS_NAME = "MACH_PROCESS_NAME"
ABB_MACH_PROCESS_INDEX = "MACH_PROCESS_INDEX"
ABB_MACH_POSE_NAME = "MACH_POSE_NAME"
ABB_MACH_POSE_INDEX = "MACH_POSE_INDEX"
ABB_MACH_APPROACH_TYPE = "MACH_APPROACH_TYPE"
ABB_MACH_APPROACH_TYPE_LITERALS = ["MachJ", "MoveJ"]
ABB_MACH_APPROACH_TYPE_DEFAULT = "MoveJ"

# -------------------------------------------------------------------------------------------
# Initialize data management default values from JSON instances
def InitializeDataManagementDefaults(Operator, attribSetter, logging):
   """Load default values from JSON instances and set in attributes."""
   try:
      # Import data_utils if available
      import data_utils as dm_utils
      
      # Get controller name
      controllerName = dm_utils.get_controller_name(Operator)
      
      # Process each data type
      for dataType in ['seamdata', 'welddata', 'weavedata', 'trackdata', 'machineprocess', 'machiningpose']:
         try:
            # Load instances
            instances = dm_utils.load_instances(controllerName, dataType)
            if not instances:
               continue
            
            # Get default instance
            default = dm_utils.get_default_instance(instances)
            if not default:
               continue
            
            # Set name and index attributes
            if dataType == 'machineprocess':
               prefix = 'MACH_PROCESS'
            elif dataType == 'machiningpose':
               prefix = 'MACH_POSE'
            else:
               prefix = dataType.replace('data', '').upper()
            nameAttr = f"{prefix}_NAME" if dataType in ('machineprocess', 'machiningpose') else f"{prefix}_DATA_NAME"
            indexAttr = f"{prefix}_INDEX" if dataType in ('machineprocess', 'machiningpose') else f"{prefix}_DATA_INDEX"
            
            attribSetter.SetString(nameAttr, default.get('name', ''))
            attribSetter.SetInteger(indexAttr, default.get('id', -1))
            
            logging.LogInfo(f"Initialized {dataType} default: {default.get('name', '')} (ID {default.get('id', -1)})")
         
         except Exception as e:
            logging.LogInfo(f"Could not initialize {dataType} defaults: {str(e)}")
   
   except ImportError:
      # data_utils not available - skip initialization
      pass
   except Exception as e:
      logging.LogInfo(f"Error in InitializeDataManagementDefaults: {str(e)}")

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

   startPtpFeed = attribGetter.GetAttributeDoubleByName("StartPtpFeedRate")
   if startPtpFeed.IsValid():
      startPtpFeed.SetMaximum(1000.0)
   startPtpFeedEvt = attribGetter.GetAttributeDoubleByName("EventStartPtpFeedRate")
   if startPtpFeedEvt.IsValid():
      startPtpFeedEvt.SetMaximum(1000.0)

   defaults = _load_defaults(ABB_TECH_DEFAULTS_FILE)
   weld_default = int(defaults.get(ABB_AW_WELDDATANUMBER, 1))
   seam_default = int(defaults.get(ABB_AW_SEAMDATANUMBER, 1))
   weave_default = int(defaults.get(ABB_AW_WEAVEDATANUMBER, 1))
   track_default = int(defaults.get(ABB_AW_TRACKDATANUMBER, 1))

   # Legacy attributes - keep for downloader fallback but hide from UI
   att1=attribCreator.AddInteger(ABB_AW_WELDDATANUMBER, weld_default, 1, 99, GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE|PROCESS_ATTRIBUTE|USER_ATTRIBUTE, ABB_AW_WELDDATANUMBER)
   att1.SetVisibility(False)
   att2=attribCreator.AddInteger(ABB_AW_SEAMDATANUMBER, seam_default, 1, 99, GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE|PROCESS_ATTRIBUTE|USER_ATTRIBUTE, ABB_AW_SEAMDATANUMBER)
   att2.SetVisibility(False)
   att3=attribCreator.AddInteger(ABB_AW_WEAVEDATANUMBER, weave_default, 1, 99, GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE|PROCESS_ATTRIBUTE|USER_ATTRIBUTE, ABB_AW_WEAVEDATANUMBER)
   att3.SetVisibility(False)
   att4=attribCreator.AddInteger(ABB_AW_TRACKDATANUMBER, track_default, 1, 99, GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE|PROCESS_ATTRIBUTE|USER_ATTRIBUTE, ABB_AW_TRACKDATANUMBER)
   att4.SetVisibility(False)

   # Machining tech type selector
   machTechType = attribCreator.AddEnum(ABB_MACHINING_TECH_TYPE, ABB_MACHINING_TECH_TYPE_LITERALS, ABB_MACHINING_TECH_TYPE_DEFAULT, ATTRIBUTE_LEVEL, ABB_MACHINING_TECH_TYPE)
   machTechType.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Data Management System - global output control
   attribCreator.AddBool("GLOBAL_DATA", False, ATTRIBUTE_GLOBAL_LEVEL, "GLOBAL_DATA")
   attribCreator.AddBool("OUTPUT_DATA_MODULE", False, ATTRIBUTE_GLOBAL_LEVEL, "OUTPUT_DATA_MODULE")
   attribCreator.AddString("DATA_MODULE_NAME", "ABB_Data", ATTRIBUTE_GLOBAL_LEVEL, "DATA_MODULE_NAME")

   # Data Management System - seamdata
   seam_name_attr = attribCreator.AddString("SEAM_DATA_NAME", "", ATTRIBUTE_LEVEL, "SEAM_DATA_NAME")
   seam_name_attr.SetVisibility(True)
   seam_name_attr.SetReadOnly(True)
   seam_index_attr = attribCreator.AddInteger("SEAM_DATA_INDEX", -1, -1, 9999, ATTRIBUTE_LEVEL, "SEAM_DATA_INDEX")
   seam_index_attr.SetVisibility(False)
   seam_index_attr.SetReadOnly(True)
   attribCreator.AddBool("SELECT_SEAMDATA", False, ATTRIBUTE_LEVEL, "SELECT_SEAMDATA")
   attribCreator.AddBool("EDIT_SEAMDATA", False, ATTRIBUTE_LEVEL, "EDIT_SEAMDATA")
   
   # Data Management System - welddata
   weld_name_attr = attribCreator.AddString("WELD_DATA_NAME", "", ATTRIBUTE_LEVEL, "WELD_DATA_NAME")
   weld_name_attr.SetVisibility(True)
   weld_name_attr.SetReadOnly(True)
   weld_index_attr = attribCreator.AddInteger("WELD_DATA_INDEX", -1, -1, 9999, ATTRIBUTE_LEVEL, "WELD_DATA_INDEX")
   weld_index_attr.SetVisibility(False)
   weld_index_attr.SetReadOnly(True)
   attribCreator.AddBool("SELECT_WELDDATA", False, ATTRIBUTE_LEVEL, "SELECT_WELDDATA")
   attribCreator.AddBool("EDIT_WELDDATA", False, ATTRIBUTE_LEVEL, "EDIT_WELDDATA")
   
   # Data Management System - weavedata
   weave_name_attr = attribCreator.AddString("WEAVE_DATA_NAME", "", ATTRIBUTE_LEVEL, "WEAVE_DATA_NAME")
   weave_name_attr.SetVisibility(True)
   weave_name_attr.SetReadOnly(True)
   weave_index_attr = attribCreator.AddInteger("WEAVE_DATA_INDEX", -1, -1, 9999, ATTRIBUTE_LEVEL, "WEAVE_DATA_INDEX")
   weave_index_attr.SetVisibility(False)
   weave_index_attr.SetReadOnly(True)
   attribCreator.AddBool("SELECT_WEAVEDATA", False, ATTRIBUTE_LEVEL, "SELECT_WEAVEDATA")
   attribCreator.AddBool("EDIT_WEAVEDATA", False, ATTRIBUTE_LEVEL, "EDIT_WEAVEDATA")
   use_weaving_attr = attribCreator.AddBool("USE_WEAVING", False, ATTRIBUTE_LEVEL, "USE_WEAVING")
   use_weaving_attr.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # Data Management System - trackdata
   track_name_attr = attribCreator.AddString("TRACK_DATA_NAME", "", ATTRIBUTE_LEVEL, "TRACK_DATA_NAME")
   track_name_attr.SetVisibility(True)
   track_name_attr.SetReadOnly(True)
   track_index_attr = attribCreator.AddInteger("TRACK_DATA_INDEX", -1, -1, 9999, ATTRIBUTE_LEVEL, "TRACK_DATA_INDEX")
   track_index_attr.SetVisibility(False)
   track_index_attr.SetReadOnly(True)
   attribCreator.AddBool("SELECT_TRACKDATA", False, ATTRIBUTE_LEVEL, "SELECT_TRACKDATA")
   attribCreator.AddBool("EDIT_TRACKDATA", False, ATTRIBUTE_LEVEL, "EDIT_TRACKDATA")
   use_tracking_attr = attribCreator.AddBool("USE_TRACKING", False, ATTRIBUTE_LEVEL, "USE_TRACKING")
   use_tracking_attr.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Data Management System - machineprocess
   mach_proc_name = attribCreator.AddString(ABB_MACH_PROCESS_NAME, "", ATTRIBUTE_LEVEL, ABB_MACH_PROCESS_NAME)
   mach_proc_name.SetVisibility(True)
   mach_proc_name.SetReadOnly(True)
   mach_proc_idx = attribCreator.AddInteger(ABB_MACH_PROCESS_INDEX, -1, -1, 9999, ATTRIBUTE_LEVEL, ABB_MACH_PROCESS_INDEX)
   mach_proc_idx.SetVisibility(False)
   mach_proc_idx.SetReadOnly(True)
   attribCreator.AddBool("SELECT_MACHPROCESS", False, ATTRIBUTE_LEVEL, "SELECT_MACHPROCESS")
   attribCreator.AddBool("EDIT_MACHPROCESS", False, ATTRIBUTE_LEVEL, "EDIT_MACHPROCESS")

   # Data Management System - machiningpose
   mach_pose_name = attribCreator.AddString(ABB_MACH_POSE_NAME, "", ATTRIBUTE_LEVEL, ABB_MACH_POSE_NAME)
   mach_pose_name.SetVisibility(True)
   mach_pose_name.SetReadOnly(True)
   mach_pose_idx = attribCreator.AddInteger(ABB_MACH_POSE_INDEX, -1, -1, 9999, ATTRIBUTE_LEVEL, ABB_MACH_POSE_INDEX)
   mach_pose_idx.SetVisibility(False)
   mach_pose_idx.SetReadOnly(True)
   attribCreator.AddBool("SELECT_MACHPOSE", False, ATTRIBUTE_LEVEL, "SELECT_MACHPOSE")
   attribCreator.AddBool("EDIT_MACHPOSE", False, ATTRIBUTE_LEVEL, "EDIT_MACHPOSE")

   # Machining approach type (MachJ vs MoveJ for non-process moves)
   mach_approach = attribCreator.AddEnum(ABB_MACH_APPROACH_TYPE, ABB_MACH_APPROACH_TYPE_LITERALS, ABB_MACH_APPROACH_TYPE_DEFAULT, ATTRIBUTE_LEVEL, ABB_MACH_APPROACH_TYPE)
   mach_approach.SetVisibility(False)
   
   # Load station configuration from downloader JSON
   PopulateStationConstants()
   if ABB_STATION_LIST:
      attribIntENM = attribCreator.AddEnum(ABB_STATION,ABB_STATION_LIST,ABB_STATION_DEFAULT,ATTRIBUTE_GLOBAL_LEVEL,ABB_STATION)

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

   #SeamFinding Definition
   attribInteger = attribCreator.AddInteger(ABB_SEAMFIND_ID,1,0,MAX_INTEGER,ATTRIBUTE_LEVEL,ABB_SEAMFIND_ID)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(ABB_SEAMFIND_JOINTTYPE,ABB_SEAMFIND_JOINTTYPE_LIST,ABB_SEAMFIND_JOINTTYPE_LIST[0],ATTRIBUTE_LEVEL,ABB_SEAMFIND_JOINTTYPE)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribENM = attribCreator.AddEnum(ABB_SEAM_FINDING_MOUNT_TYPE,ABB_SEAM_FINDING_MOUNT_TYPE_LITERALS,ABB_SEAM_FINDING_MOUNT_TYPE_LITERALS[1],ATTRIBUTE_LEVEL,ABB_SEAM_FINDING_MOUNT_TYPE)
   attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribENM = attribCreator.AddEnum(ABB_SEAM_FINDING_RECIPE,ABB_SEAM_FINDING_RECIPE_LITERALS,ABB_SEAM_FINDING_RECIPE_LITERALS[1],ATTRIBUTE_LEVEL,ABB_SEAM_FINDING_RECIPE)
   attribENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   #Connection Types
   attConnectionType = attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE)
   attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
   attConnectionType.AddLiteral("Frame3pConnect")

   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN,10,0.0,1000,5,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED,AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
   attribDouble.SetVisibility(False)
   attribDouble = attribCreator.AddDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP,1000,0.0,1000,5,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_PERCENT,AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP)

   sensorType_index = attribCreator.AddEnum(AW_SENSOR_TOOL_TYPE, AW_SENSOR_TOOL_TYPE_LITERALS, "Touch Sensor", USER_ATTRIBUTE|PROCESS_ATTRIBUTE|GLOBAL_ATTRIBUTE|OPERATION_GROUP_ATTRIBUTE|OPERATION_ATTRIBUTE, AW_SENSOR_TOOL_TYPE)
   sensorType_index.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_TOUCH,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_TOUCH)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_POINT,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_POINT)
   attribInteger = attribCreator.AddInteger(AW_SENSOR_ID_LINE,1,1,254,ATTRIBUTE_LEVEL,AW_SENSOR_ID_LINE)

   #Seam tracking
   attribSeamTrackSearchStart = attribCreator.AddBool(ABB_SEAMTRACK_SEARCH_START, True, ATTRIBUTE_LEVEL, ABB_SEAMTRACK_SEARCH_START)
   attribSeamTrackSearchStart.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribSeamTrackSearchSpeed = attribCreator.AddDouble(ABB_SEAMTRACK_SEARCH_SPEED,0.01,0.0,1,0.01,ATTRIBUTE_GLOBAL_LEVEL,ATTRIB_SPEED,ABB_SEAMTRACK_SEARCH_SPEED)
   attribSeamTrackSearchStart.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   
   # Initialize data management default values
   try:
      InitializeDataManagementDefaults(Operator, attribSetter, logging)
   except Exception as e:
      logging.LogInfo(f"Could not initialize data management defaults: {str(e)}")


# -------------------------------------------------------------------------------------------
# Technology post event initialization
# def PostTechInitEvents(Operator: CENPyOlpTech_EventInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

#    # YOUR CODE
#    # Operator.RegisterPyTechnologyEvent("ArcSwitchEvent.py")

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)
#    pass

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

   # Handle MACHINING_TECH_TYPE visibility toggle
   if attribName == ABB_MACHINING_TECH_TYPE:
      techTypeIdx = attribGetter.GetEnumIndex(ABB_MACHINING_TECH_TYPE)
      is_machining = (techTypeIdx == 1)  # 0=ArcWelding, 1=Machining
      is_arcwelding = not is_machining

      # --- ArcWelding group: name, index, select/edit buttons ---
      try:
         for aw_attr in ["SEAM_DATA_NAME", "WELD_DATA_NAME",
                          "SELECT_SEAMDATA", "EDIT_SEAMDATA",
                          "SELECT_WELDDATA", "EDIT_WELDDATA"]:
            attribGetter.GetAttributeByName(aw_attr).SetVisibility(is_arcwelding)
         for aw_idx in ["SEAM_DATA_INDEX", "WELD_DATA_INDEX"]:
            attribGetter.GetAttributeByName(aw_idx).SetVisibility(False)  # always hidden (internal)
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – ArcWelding attrs: {e}")

      # --- Weave / Track group: hide when machining ---
      try:
         for wt_attr in ["USE_WEAVING", "USE_TRACKING"]:
            attribGetter.GetAttributeByName(wt_attr).SetVisibility(is_arcwelding)
         if is_machining:
            for wt_hide in ["WEAVE_DATA_NAME", "WEAVE_DATA_INDEX",
                             "SELECT_WEAVEDATA", "EDIT_WEAVEDATA",
                             "TRACK_DATA_NAME", "TRACK_DATA_INDEX",
                             "SELECT_TRACKDATA", "EDIT_TRACKDATA"]:
               attribGetter.GetAttributeByName(wt_hide).SetVisibility(False)
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – Weave/Track attrs: {e}")

      # --- Machining group: name, index (hidden), select/edit buttons, approach type ---
      try:
         for mp_attr in [ABB_MACH_PROCESS_NAME,
                          "SELECT_MACHPROCESS", "EDIT_MACHPROCESS"]:
            attribGetter.GetAttributeByName(mp_attr).SetVisibility(is_machining)
         attribGetter.GetAttributeByName(ABB_MACH_PROCESS_INDEX).SetVisibility(False)  # always hidden
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – MachProcess attrs: {e}")
      try:
         for mpose_attr in [ABB_MACH_POSE_NAME,
                             "SELECT_MACHPOSE", "EDIT_MACHPOSE"]:
            attribGetter.GetAttributeByName(mpose_attr).SetVisibility(is_machining)
         attribGetter.GetAttributeByName(ABB_MACH_POSE_INDEX).SetVisibility(False)  # always hidden
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – MachPose attrs: {e}")
      try:
         attribGetter.GetAttributeByName(ABB_MACH_APPROACH_TYPE).SetVisibility(is_machining)
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – MachApproach attr: {e}")

      # Apply per-tech-type orientation defaults (LocalOffsetRx/Ry/Rz) from config
      try:
         dl_config = load_json(os.path.join(TECH_TABS_PATH, 'ABB_IRC5_DL.json'))
         tech_type_key = "Machining" if is_machining else "ArcWelding"
         orient = dl_config.get('orientation_defaults', {}).get(tech_type_key, {})
         if orient:
            attribSetter.SetDouble("LocalOffsetRx", orient.get("rx", 45.0))
            attribSetter.SetDouble("LocalOffsetRy", orient.get("ry", 0.0))
            attribSetter.SetDouble("LocalOffsetRz", orient.get("rz", 90.0))
      except Exception as e:
         logging.LogInfo(f"MACHINING_TECH_TYPE toggle – orientation defaults: {e}")

      return True

   # Handle USE_WEAVING visibility control
   if attribName == "USE_WEAVING":
      try:
         use_weaving = attribGetter.GetBool("USE_WEAVING")
         for wv_attr in ["WEAVE_DATA_NAME", "SELECT_WEAVEDATA", "EDIT_WEAVEDATA"]:
            attribGetter.GetAttributeByName(wv_attr).SetVisibility(use_weaving)
         attribGetter.GetAttributeByName("WEAVE_DATA_INDEX").SetVisibility(False)
      except Exception as e:
         logging.LogInfo(f"Error setting weavedata visibility: {str(e)}")
      return True
   
   # Handle USE_TRACKING visibility control
   if attribName == "USE_TRACKING":
      try:
         use_tracking = attribGetter.GetBool("USE_TRACKING")
         for tk_attr in ["TRACK_DATA_NAME", "SELECT_TRACKDATA", "EDIT_TRACKDATA"]:
            attribGetter.GetAttributeByName(tk_attr).SetVisibility(use_tracking)
         attribGetter.GetAttributeByName("TRACK_DATA_INDEX").SetVisibility(False)
      except Exception as e:
         logging.LogInfo(f"Error setting trackdata visibility: {str(e)}")
      return True
   
   # Data Management System - Boolean triggers for data picker/editor apps
   # Track open windows to prevent multiple instances
   if not hasattr(PostTechOnAttribChanged, '_open_windows'):
      PostTechOnAttribChanged._open_windows = {}
   
   if attribName in ["SELECT_SEAMDATA", "SELECT_WELDDATA", "SELECT_WEAVEDATA", "SELECT_TRACKDATA",
                     "EDIT_SEAMDATA", "EDIT_WELDDATA", "EDIT_WEAVEDATA", "EDIT_TRACKDATA",
                     "SELECT_MACHPROCESS", "EDIT_MACHPROCESS", "SELECT_MACHPOSE", "EDIT_MACHPOSE"]:
      try:
         if attribGetter.GetBool(attribName):
            # Check if another window is already open for this attribute
            if attribName in PostTechOnAttribChanged._open_windows:
               try:
                  # Try to bring existing window to front
                  existing_window = PostTechOnAttribChanged._open_windows[attribName]
                  if existing_window and existing_window.winfo_exists():
                     existing_window.lift()
                     existing_window.focus_force()
                     attribSetter.SetBool(attribName, False)
                     return True
                  else:
                     # Window no longer exists, remove from tracking
                     del PostTechOnAttribChanged._open_windows[attribName]
               except:
                  # Window reference is invalid, remove from tracking
                  del PostTechOnAttribChanged._open_windows[attribName]
            
            # Find script directory by searching sys.path for technology folder
            script_dir = None
            
            # Search sys.path for a directory containing this file
            for path in sys.path:
               if os.path.isdir(path):
                  # Look for technology structure markers
                  test_path = os.path.join(path, 'ArcWeldingTechnology.py')
                  if os.path.exists(test_path):
                     script_dir = path
                     break
                  # Check if this is inside Technologies folder structure
                  if 'Technologies' in path and 'Scripts' in path:
                     script_dir = path
                     break
            
            # Fallback: search from current working directory
            if not script_dir:
               cwd = os.getcwd()
               # Look for Technologies folder
               for root, dirs, files in os.walk(cwd):
                  if 'ArcWeldingTechnology.py' in files and 'data_picker.py' in files:
                     script_dir = root
                     break
                  # Limit search depth
                  if root.count(os.sep) - cwd.count(os.sep) > 5:
                     break
            
            if not script_dir:
               logging.LogInfo(f"Could not find Scripts directory. sys.path: {sys.path[:3]}")
               attribSetter.SetBool(attribName, False)
               return
            
            # Import data management modules
            data_picker_path = os.path.join(script_dir, 'data_picker.py')
            data_editor_path = os.path.join(script_dir, 'data_editor.py')
            
            # Add script directory to sys.path for imports
            if script_dir not in sys.path:
               sys.path.insert(0, script_dir)
            
            # Determine data type
            rawType = attribName.replace("SELECT_", "").replace("EDIT_", "").lower()
            # Map trigger names to JSON data types
            _trigger_to_dtype = {
               'machprocess': 'machineprocess',
               'machpose': 'machiningpose',
            }
            dataType = _trigger_to_dtype.get(rawType, rawType)
            
            # Launch appropriate app with module reload to prevent caching
            if "SELECT_" in attribName:
               if os.path.exists(data_picker_path):
                  import data_picker
                  import data_utils
                  import data_validator
                  # Reload modules to get latest changes
                  import importlib
                  importlib.reload(data_utils)
                  importlib.reload(data_validator)
                  importlib.reload(data_picker)
                  window = data_picker.launch_data_picker(Operator, dataType, attribName)
                  if window:
                     PostTechOnAttribChanged._open_windows[attribName] = window
               else:
                  logging.LogInfo(f"Data picker not found: {data_picker_path}")
            elif "EDIT_" in attribName:
               if os.path.exists(data_editor_path):
                  import data_editor
                  import data_utils
                  import data_validator
                  # Reload modules to get latest changes
                  import importlib
                  importlib.reload(data_utils)
                  importlib.reload(data_validator)
                  importlib.reload(data_editor)
                  window = data_editor.launch_data_editor(Operator, dataType, attribName)
                  if window:
                     PostTechOnAttribChanged._open_windows[attribName] = window
               else:
                  logging.LogInfo(f"Data editor not found: {data_editor_path}")
            
            # Reset boolean
            attribSetter.SetBool(attribName, False)
      except Exception as e:
         logging.LogError(f"Error launching data management app: {str(e)}")
         attribSetter.SetBool(attribName, False)
      return True

   if(attribName == AW_SEAM_CALIBRATION_METHOD):
      seamCalibMethodIdx = attribGetter.GetEnumIndex(AW_SEAM_CALIBRATION_METHOD)
      if seamCalibMethodIdx > 0 and seamCalibMethodIdx < 4: # TS, SeamSearch, SeamFind
         attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE).SetVisibility(True)
      else:
         attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE).SetVisibility(False)

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
      seamFindId = attribGetter.GetAttributeIntegerByName(ABB_SEAMFIND_ID)
      seamFindJointType = attribGetter.GetAttributeEnumByName(ABB_SEAMFIND_JOINTTYPE)
      seamFindMountType = attribGetter.GetAttributeEnumByName(ABB_SEAM_FINDING_MOUNT_TYPE)
      seamFindRecipe = attribGetter.GetAttributeEnumByName(ABB_SEAM_FINDING_RECIPE)
      if(sensorTypeLiteralIndex == 0): # "Touch Sensor"
         sensorIdTouch.SetVisibility(True)
         sensorIdPoint.SetVisibility(False)
         sensorIdLine.SetVisibility(False)
         literalIndex = tsTouchMethod.GetLiteralIndex()
         seamFindId.SetVisibility(False)
         seamFindJointType.SetVisibility(False)
         seamFindMountType.SetVisibility(False) 
         seamFindRecipe.SetVisibility(False)
         if(literalIndex == 0): # "Detection with nozzle"
            attribSetter.SetDouble(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE, 10.0)
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
         return

   if(attribName == AW_TOUCH_METHOD):
      literalIndex = tsTouchMethod.GetLiteralIndex()

      if(literalIndex == 0): # "Detection with nozzle"
         attribSetter.SetDouble(AW_TOUCH_TOUCH_DIFF_ANGLE_NOZZLE, 10.0)
         return
      if(literalIndex == 1): # "Detection with wire"
         attribSetter.SetDouble(AW_TOUCH_DIFF_ANGLE, 45.0)
         return


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
   # 100 = R2025.2.3
   return 110

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

   if (lastVersion < 100):
      # program = Operator.GetOlpProgram()      
      # RemoveAttribute(Operator,program,ABB_IGNITION_PARAM_SET_DEFINE)
      # RemoveAttribute(Operator,program,ABB_WELD_PARAM_SET_DEFINE)
      # RemoveAttribute(Operator,program,ABB_ARC_OFF_PARAM_SET_DEFINE)

      PtpFeed = attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP)
      if PtpFeed.IsValid():
         PtpFeed.SetMaximum(1000.0)
      LinFeed = attribGetter.GetAttributeDoubleByName(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
      if LinFeed.IsValid():
         LinFeed.SetMaximum(1.0)

      completeRecomputeNeeded = True

      return completeRecomputeNeeded

   if (lastVersion < 110):
   # Machining tech type selector
      machTechType = attribCreator.AddEnum(ABB_MACHINING_TECH_TYPE, ABB_MACHINING_TECH_TYPE_LITERALS, ABB_MACHINING_TECH_TYPE_DEFAULT, ATTRIBUTE_LEVEL, ABB_MACHINING_TECH_TYPE)
      machTechType.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      mach_approach = attribCreator.AddEnum(ABB_MACH_APPROACH_TYPE, ABB_MACH_APPROACH_TYPE_LITERALS, ABB_MACH_APPROACH_TYPE_DEFAULT, ATTRIBUTE_LEVEL, ABB_MACH_APPROACH_TYPE)
      mach_approach.SetVisibility(False)
      # Data Management System - machineprocess
      mach_proc_name = attribCreator.AddString(ABB_MACH_PROCESS_NAME, "", ATTRIBUTE_LEVEL, ABB_MACH_PROCESS_NAME)
      mach_proc_name.SetVisibility(False)
      mach_proc_name.SetReadOnly(True)
      mach_proc_idx = attribCreator.AddInteger(ABB_MACH_PROCESS_INDEX, -1, -1, 9999, ATTRIBUTE_LEVEL, ABB_MACH_PROCESS_INDEX)
      mach_proc_idx.SetVisibility(False)
      mach_proc_idx.SetReadOnly(True)
      mach_sel = attribCreator.AddBool("SELECT_MACHPROCESS", False, ATTRIBUTE_LEVEL, "SELECT_MACHPROCESS")
      mach_sel.SetVisibility(False)
      mach_edit = attribCreator.AddBool("EDIT_MACHPROCESS", False, ATTRIBUTE_LEVEL, "EDIT_MACHPROCESS")
      mach_edit.SetVisibility(False)
      # Data Management System - machiningpose
      mach_pose_name = attribCreator.AddString(ABB_MACH_POSE_NAME, "", ATTRIBUTE_LEVEL, ABB_MACH_POSE_NAME)
      mach_pose_name.SetVisibility(False)
      mach_pose_name.SetReadOnly(True)
      mach_pose_idx = attribCreator.AddInteger(ABB_MACH_POSE_INDEX, -1, -1, 9999, ATTRIBUTE_LEVEL, ABB_MACH_POSE_INDEX)
      mach_pose_idx.SetVisibility(False)
      mach_pose_idx.SetReadOnly(True)
      mach_pose_sel = attribCreator.AddBool("SELECT_MACHPOSE", False, ATTRIBUTE_LEVEL, "SELECT_MACHPOSE")
      mach_pose_sel.SetVisibility(False)
      mach_pose_edit = attribCreator.AddBool("EDIT_MACHPOSE", False, ATTRIBUTE_LEVEL, "EDIT_MACHPOSE")
      mach_pose_edit.SetVisibility(False)

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
