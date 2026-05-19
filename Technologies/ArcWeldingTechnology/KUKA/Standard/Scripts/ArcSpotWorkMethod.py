from centypes import *
from cenpylib import *
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "ArcSpotWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug) initialization of manufacturing geometry ended."

# general global definitions. Enter here the technology name, followed by ": "
DEBUG_SYNC_PG_ATTRIB_START = "(Debug-Technology) WM synchronization of process geometry started."
DEBUG_SYNC_PG_ATTRIB_END = "(Debug-Technology) WM synchronization of process geometry ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

AW_SEAMFIND_APPROACH_EVENT_NAME = "SeamFindingOnePointApproach"
AW_SEAMFIND_RETRACT_EVENT_NAME  = "SeamFindingOnePointRetract"
AW_SEAMFIND_TEACH_EVENT_NAME    = "SeamFindTeach"

PY_SEAMFIND_SCAN_EVENT_FILE     = "SeamFindingScanEvent.py"
PY_SEAMFIND_REF_EVENT_FILE      = "SeamFindingRefEvent.py"
PY_SEAMFIND_TEACH_EVENT_FILE    = "SeamFindTeach.py"
PY_LINELASERPOV_EVENT_FILE      = "LaserFovEvent.py"

AW_SEAM_FIND_USE                = "SeamFindUse"

AW_GLOBAL_TOUCH_COUNTER         = "AWGlobalTouchCounter"
AW_TOUCHSENS_TOUCH_ID           = "TouchIdArcSpot"
AW_TOUCHSENS_FRAME_PT           = "FramePt"

ATTRIBUTE_GLOBAL_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE

def PostWmInitAttributes(Operator: CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribCreator = Operator.GetAttribCreator()
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # your code 

   sf01 = attribCreator.AddBool(AW_SEAM_FIND_USE,True,ATTRIBUTE_LEVEL,AW_SEAM_FIND_USE)
   sf01.SetVisibility(True)
   sf02 = attribCreator.AddInteger(AW_TOUCHSENS_TOUCH_ID, 0,0,999, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, "TouchId")
   sf02.SetVisibility(True)
   sf03 = attribCreator.AddInteger(AW_TOUCHSENS_FRAME_PT, 0,0,3, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_TOUCHSENS_FRAME_PT)
   sf03.SetVisibility(True)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass 

def PostWmInitEvents(WmEventInitOperator: CENPyOlpWM_EventInitOperator):

   # ArcSpot Technology
   # WmEventInitOperator.RegisterPyTechnologyEvent('ArcSpotEvent.py')
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_TEACH_EVENT_FILE)
   # add Python Approach&Retract Event to WM
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_SCAN_EVENT_FILE)
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_REF_EVENT_FILE)
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_LINELASERPOV_EVENT_FILE)

def PostWmInitRules(Operator: CENPyOlpWM_RuleInitOperator):

   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes

   # Remove C++ APPROACH Event from Rule
   Operator.RemoveEventFromRule('ApproachRule', AW_SEAMFIND_APPROACH_EVENT_NAME)
   # Remove C++ RETRACT Event from Rule
   Operator.RemoveEventFromRule('RetractRule', AW_SEAMFIND_RETRACT_EVENT_NAME)
   # Remove C++ RETRACT Event from Rule and add Python Event
   Operator.RemoveEventFromRule('ProcessPointRule', 'ProcessPointEvent')
   # Add SeamFindTeach event
   Operator.AddPyEvent('ProcessPointRule', AW_SEAMFIND_TEACH_EVENT_NAME)     
   Operator.SetActivePyEvent('ProcessPointRule', AW_SEAMFIND_TEACH_EVENT_NAME)

   pass

def PostWmOnAttribChanged(Operator: CENPyOlpWM_AttribChangedOperator):
   pass
   
# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator: CENPyOlpWM_SyncPgAttribOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_START)

   attribGetter = Operator.GetAttribGetter()

   posRegStartRegister = attribGetter.GetAttributeByName(AW_GLOBAL_TOUCH_COUNTER)
   if posRegStartRegister != None:
      posRegStartRegister.SetVisibility(False)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_END)

def PostProcessOperationAttributes(Operator: CENPyOlpWM_POAttribOperator):
   pass
      
