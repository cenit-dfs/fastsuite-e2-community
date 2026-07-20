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
import sys
sys.dont_write_bytecode = True
# -------------------------------------------------------------------------------------------
FILE_NAME = "SeamFindingWorkMethod.py: "
# general global definitions. Enter here the technology name, followed by ": "
AW_SEAMFIND_APPROACH_EVENT_NAME = "SeamFindingOnePointApproach"
PY_SEAMFIND_APPROACH_EVENT_NAME = "SeamFindingApproach"
PY_SEAMFIND_APPROACH_EVENT_FILE = "SeamFindingApproach.py"

AW_SEAMFIND_RETRACT_EVENT_NAME = "SeamFindingOnePointRetract"
PY_SEAMFIND_RETRACT_EVENT_NAME = "SeamFindingRetract"
PY_SEAMFIND_RETRACT_EVENT_FILE = "SeamFindingRetract.py"

def PostWmInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   pass

def PostWmInitEvents(WmEventInitOperator):
   # add Python Approach&Retract Event to WM
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_APPROACH_EVENT_FILE)
   WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_RETRACT_EVENT_FILE)

def PostWmInitRules(WmRuleInitOperator):
   # Remove C++ APPROACH Event from Rule and add Python Event
   WmRuleInitOperator.RemoveEventFromRule('ApproachRule', AW_SEAMFIND_APPROACH_EVENT_NAME)
   WmRuleInitOperator.AddPyEvent('ApproachRule', PY_SEAMFIND_APPROACH_EVENT_NAME)
   WmRuleInitOperator.SetActivePyEvent('ApproachRule', PY_SEAMFIND_APPROACH_EVENT_NAME)
   # Remove C++ RETRACT Event from Rule and add Python Event
   WmRuleInitOperator.RemoveEventFromRule('RetractRule', AW_SEAMFIND_RETRACT_EVENT_NAME)
   WmRuleInitOperator.AddPyEvent('RetractRule', PY_SEAMFIND_RETRACT_EVENT_NAME)
   WmRuleInitOperator.SetActivePyEvent('RetractRule', PY_SEAMFIND_RETRACT_EVENT_NAME)

# -------------------------------------------------------------------------------------------
def PostWmOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   
# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   # attribGetter = Operator.GetAttribGetter()
