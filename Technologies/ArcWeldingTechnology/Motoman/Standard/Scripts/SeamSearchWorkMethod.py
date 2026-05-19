# -------------------------------------------------------------------------------------------
# Name: SeamSearchWorkMethod
# Description: this Python file adjust basic implementation for Yaskawa specific installation 
# Debug info: E2@localhost:5254
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Cenit AG
#        Date: July 2024
#     
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
FILE_NAME = "SeamSearchWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) WM initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) WM initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) WM initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) WM initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) WM initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) WM initialization of event rules ended."

DEBUG_SYNC_PG_ATTRIB_START = "(Debug-Technology) WM synchronization of process geometry started."
DEBUG_SYNC_PG_ATTRIB_END = "(Debug-Technology) WM synchronization of process geometry ended."

DEBUG_POST_PROCESS_OPERATION_ATTRIB_START = "(Debug-Technology) WM post process operation attributes stared."
DEBUG_POST_PROCESS_OPERATION_ATTRIB_END = "(Debug-Technology) WM post process operation attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) prev on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

# general global definitions. Enter here the technology name, followed by ": "
AW_SEAMFIND_APPROACH_EVENT_NAME = "SeamFindingOnePointApproach"
PY_SEAMFIND_APPROACH_EVENT_NAME = "TouchPointStartAppEvent"
PY_SEAMFIND_APPROACH_EVENT_FILE = "TouchPointStartAppEvent"

AW_SEAMFIND_RETRACT_EVENT_NAME = "SeamFindingOnePointRetract"
PY_SEAMFIND_RETRACT_EVENT_NAME = "TouchPointStartRetEvent"
PY_SEAMFIND_RETRACT_EVENT_FILE = "TouchPointStartRetEvent"

WM_MOTION_TYPE = "OperationGroupMotionType"
#AW_SEAMSEARCH_FRAME_PT="FramePt"
AW_SEAMSEARCH_APPR_RETR_SPEED="SeamSearchApprRetrSpeed"
AW_SEAMSEARCH_APPR_RETR_FLYBY="SeamSearchApprFlyBy"
AW_MOTION_TYPE_FIRST_TPE = "SeamSearchMotionTypeFirstTpe"
AW_MOTION_TYPE_FIRST_TPE_LITERALS = ["PTP", "LIN"]

AW_SPEED_WELDING_MINIMUM = 0.001
AW_SPEED_WELDING_MAXIMUM = 0.2
AW_SPEED_WELDING_STEP = 0.005

AW_SPEED_VIA_MINIMUM = 0.01
AW_SPEED_VIA_MAXIMUM = 2.0
AW_SPEED_VIA_STEP = 0.1

AW_FLYBY_MINIMUM = 0.001
AW_FLYBY_MAXIMUM = 0.2
AW_FLYBY_STEP = 0.005

#AW_TOUCHSENS_TOUCH_ID = "SSTouchID"
#AW_TOUCHSENS_WIRE_DIAM = "TSWireDiam"

AW_SEAMSEARCH_TOUCH_DIRECTION = "SeamSearchTouchDirection"
AW_SEAMSEARCH_TOUCH_DIRECTION_LITERALS = ["AlongFaceNormal", "AlongBaseFrame"]
AW_SEAMSEARCH_TOUCH_DIRECTION_NR = 2
#static const CENCHAR AW_TOUCHSENS_CONNECTION_TYPE[] = "TSConnectionType" 
#static const CENCHAR* AW_TOUCHSENS_CONNECTION_TYPE_LITERALS[] = { "OperationConnect", "StartEndConnect", "ShortestDistanceConnect" } 
#const int AW_TOUCHSENS_CONNECTION_TYPE_NR = 3 

TC_LOCAL_OFFSET_R_MINIMUM = -360.0
TC_LOCAL_OFFSET_R_MAXIMUM = +360.0
TC_LOCAL_OFFSET_R_STEP = +1.0

AW_SEAMSEARCH_WIRE_CHECK_OPERATION = "TSWireCheckOperation"

AW_WELDING_GROUP_TOUCH_ID = "TouchId"
AW_WELDING_GROUP_TOUCH_COUNTER = "Touch_Cntr"


INT_MAX = 2**31 - 1
TC_DOUBLE_MAX = 1e15

AW_TOUCHSENS_LAST_COMPUTED_OPERATION = "TSLastComputedOperation"


def PostWmInitAttributes(Operator : CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return

   try:
      # set motion type default PTP = 0  LIN = 1
      attribSetter.SetEnumIndex(WM_MOTION_TYPE, 1)
   except:
      logging.LogError("Cannot initialize vendor specific touch sensing work method attributes")
     
   #attribCreator.AddInt(AW_TOUCHSENS_FRAME_PT, 0,0,3, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_TOUCHSENS_FRAME_PT)
   
   att3 = attribCreator.AddDouble(AW_SEAMSEARCH_APPR_RETR_SPEED, 0.200,0,1,0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_SEAMSEARCH_APPR_RETR_SPEED)
   att4 = attribCreator.AddDouble(AW_SEAMSEARCH_APPR_RETR_FLYBY, 0.005,0,0.1,0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_SEAMSEARCH_APPR_RETR_FLYBY)
   
   searchMoTypeIndex = attribGetter.GetEnumIndex(WM_MOTION_TYPE)
   att5 = attribCreator.AddEnum(AW_MOTION_TYPE_FIRST_TPE, AW_MOTION_TYPE_FIRST_TPE_LITERALS, AW_MOTION_TYPE_FIRST_TPE_LITERALS[searchMoTypeIndex], OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_MOTION_TYPE_FIRST_TPE)
   att5.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   ResState = ENTERSTATE_COMPLETE
   
   att6 = attribCreator.AddEnum(AW_SEAMSEARCH_TOUCH_DIRECTION, AW_SEAMSEARCH_TOUCH_DIRECTION_LITERALS, AW_SEAMSEARCH_TOUCH_DIRECTION_LITERALS[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_SEAMSEARCH_TOUCH_DIRECTION)
   if (att6):
      att6.SetReComputeEnterState(ResState) 
      att6.SetVisibility(False) 
   att11 = attribCreator.AddBool(AW_TOUCHSENS_LAST_COMPUTED_OPERATION, True, OPERATION_ATTRIBUTE, AW_TOUCHSENS_LAST_COMPUTED_OPERATION)

   if (att11):
      att11.SetVisibility(False)
   ## Touch ID, this attribute will be used in touch operations
   att15 = attribCreator.AddInt(AW_WELDING_GROUP_TOUCH_ID, 0, 0, INT_MAX, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, "TouchId") 
   if (att15):
      ## Todo: Recompute?
      att15.SetVisibility(True) 
   ## Touch counter, this attribute will be used in touch operations
   att16 = attribCreator.AddInt(AW_WELDING_GROUP_TOUCH_COUNTER, 0, 0, INT_MAX,OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WELDING_GROUP_TOUCH_COUNTER) 
   if (att16):
      att16.SetVisibility(False) 
  
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

def PostWmInitEvents(Operator : CENPyOlpWM_EventInitOperator):
# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)
   
   # add Python Approach&Retract Event to WM
   ##Operator.RegisterPyTechnologyEvent(PY_SEAMFIND_APPROACH_EVENT_FILE)
   ##Operator.RegisterPyTechnologyEvent(PY_SEAMFIND_RETRACT_EVENT_FILE)
   
   Operator.RegisterPyTechnologyEvent('TouchPointStartAppEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointCollisionEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointEndEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointStartRetEvent.py')

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)

def PostWmInitRules(Operator : CENPyOlpWM_RuleInitOperator):
   # Remove C++ APPROACH Event from Rule and add Python Event
   Operator.RemoveEventFromRule('ApproachRule', AW_SEAMFIND_APPROACH_EVENT_NAME)
   Operator.AddPyEvent('ApproachRule', PY_SEAMFIND_APPROACH_EVENT_NAME)
   #WmRuleInitOperator.SetActivePyEvent('ApproachRule', PY_SEAMFIND_APPROACH_EVENT_NAME)
   # Remove C++ RETRACT Event from Rule and add Python Event
   Operator.RemoveEventFromRule('RetractRule', AW_SEAMFIND_RETRACT_EVENT_NAME)
   Operator.AddPyEvent('RetractRule', PY_SEAMFIND_RETRACT_EVENT_NAME)
   #WmRuleInitOperator.SetActivePyEvent('RetractRule', PY_SEAMFIND_RETRACT_EVENT_NAME)
   pass
# -------------------------------------------------------------------------------------------
def PostWmOnAttribChanged(Operator : CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
    # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()   
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   # attribName = changedAttrib.GetName()
  

# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator : CENPyOlpWM_SyncPgAttribOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()

   #auto attribPGOperator = olpOperator->GetCurrentProcessGeometryOperator();
   #auto attribGetter = olpOperator->GetAttribGetter();
   #auto attribSetter = olpOperator->GetAttribSetter();
  
   attribSetter.SetBool(AW_SEAMSEARCH_WIRE_CHECK_OPERATION, False, ATTRIBOVERRIDEMODE_OPERATIONLEVEL)
   