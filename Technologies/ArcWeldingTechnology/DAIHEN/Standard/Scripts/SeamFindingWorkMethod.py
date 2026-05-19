# -------------------------------------------------------------------------------------------
# Name: SeamFindingWorkMethod
# Description: this Python file adjust basic implementation for vendor specific installation 
# Debug info: E2@localhost:5254
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------
from centypes import *
from cenpylib import *
import sys
sys.dont_write_bytecode = True
# -------------------------------------------------------------------------------------------
FILE_NAME = "SeamFindingWorkMethod.py: "
# general global definitions. Enter here the technology name, followed by ": "
DEBUG_SYNC_PG_ATTRIB_START = "(Debug-Technology) WM synchronization of process geometry started."
DEBUG_SYNC_PG_ATTRIB_END = "(Debug-Technology) WM synchronization of process geometry ended."

AW_SEAMFIND_APPROACH_EVENT_NAME = "SeamFindingOnePointApproach"
AW_SEAMFIND_RETRACT_EVENT_NAME  = "SeamFindingOnePointRetract"
AW_GLOBAL_TOUCH_COUNTER         = "AWGlobalTouchCounter"

PY_SEAMFIND_SCAN_EVENT_FILE     = "SeamFindingScanEvent.py"
PY_SEAMFIND_REF_EVENT_FILE      = "SeamFindingRefEvent.py"
PY_SEAMFIND_EVENT_FILE          = "SeamFindingEvent.py"

def PostWmInitAttributes(Operator: CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()

   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribCreator = Operator.GetAttribCreator()
   attribGetter = Operator.GetAttribGetter()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # your code 
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

   # Make SeamFindingEndLocation available in downloader
   attSeamFindingEndLocation = attribGetter.GetAttributeByName('SeamFindingEndLocation')
   attSeamFindingEndLocation.SetOlpProperty(PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE)

def PostWmInitEvents(WmEventInitOperator: CENPyOlpWM_EventInitOperator):
   # add Python Approach&Retract Event to WM
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_SCAN_EVENT_FILE)
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_EVENT_FILE)
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_REF_EVENT_FILE)

def PostWmInitRules(WmRuleInitOperator: CENPyOlpWM_RuleInitOperator):
   # Remove C++ APPROACH Event from Rule and add Python Event
   WmRuleInitOperator.RemoveEventFromRule('ApproachRule', AW_SEAMFIND_APPROACH_EVENT_NAME)
   # Remove C++ RETRACT Event from Rule and add Python Event
   WmRuleInitOperator.RemoveEventFromRule('RetractRule', AW_SEAMFIND_RETRACT_EVENT_NAME)

# -------------------------------------------------------------------------------------------
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

# -------------------------------------------------------------------------------------------
def PostWmOnAttribChanged(Operator: CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   
# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator: CENPyOlpWM_SyncPgAttribOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   # attribGetter = Operator.GetAttribGetter()
