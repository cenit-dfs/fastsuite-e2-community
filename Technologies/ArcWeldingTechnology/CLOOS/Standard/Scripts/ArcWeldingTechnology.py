# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customisation for OTC-DAIHEN
# Debugg info: E2@localhost:5254
# Author: Fasel
# Changelog:
#     Version: 1.0
#        Changed by: Berauer
#        Date: 2022-05-17
#
# -------------------------------------------------------------------------------------------

# Import libraries

import inspect, os, sys
sys.dont_write_bytecode = True
from centypes import *

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
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
MAX_INTEGER = 2147483647
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"


# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 1, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   
   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute() 
   
# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   return 1
