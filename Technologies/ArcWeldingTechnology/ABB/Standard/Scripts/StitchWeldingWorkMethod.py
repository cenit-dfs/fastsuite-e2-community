# -------------------------------------------------------------------------------------------
# Name: StitchWeldingWorkMethod
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
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "StitchWeldingWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug) initialization of manufacturing geometry ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

ST_ABB_TRACKING_ON_DISTANCE = "ABBTrackingOnDistance"
ST_ABB_TRACKING_SETID = "ABBTrackingSetId"
ST_ABB_TRACKING_SEAM_PATTERN_NR = "ABBTrackingSeamPatternNr"
ST_ABB_TRACKING_SEARCH_LENGTH = "ABBTrackingSearchLength"
ST_ABB_TRACKING_CONT_AFTER_ERR = "ABBTrackingContAfterErr"
ST_ABB_TRACKING_CONT_AFTER_ERR_LIST = ["Without offset","With offset"]
ST_ABB_TRACKING_MAX_LIN_CORRECTION = "ABBTrackingMaxLinCorrection"
ST_ABB_TRACKING_CORR_ELIM_DISTANCE = "ABBTrackingCorrElimDistance"
ST_ABB_TRACKING_OFF_DISTANCE = "ABBTrackingOffDistance"
ST_ABB_TRACKING_OFF_KEEPDISTANCE = "ABBTrackingOffKeepDistance"
ST_SEAMTRACKING_DISTANCE = "SeamTrackingDistance"

ATTRIBUTE_GLOBAL_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE
ATTRIBUTE_LEVEL = USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE


# -------------------------------------------------------------------------------------------
# Work method post init attributes
def PostWmInitAttributes(Operator : CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get creator, getter & setter
   attribCreator = Operator.GetAttribCreator()
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   controller = Operator.GetController()
   # check none
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return

   try:
      # ABB-specific seam tracking attributes
      attribDouble = attribCreator.AddDouble(ST_ABB_TRACKING_ON_DISTANCE,0.0,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH,ST_ABB_TRACKING_ON_DISTANCE)
      attribDouble.SetVisibility(False)
      attribString = attribCreator.AddString(ST_ABB_TRACKING_SETID,'S1',ATTRIBUTE_LEVEL,ST_ABB_TRACKING_SETID)
      attribInteger = attribCreator.AddInteger(ST_ABB_TRACKING_SEAM_PATTERN_NR,2,1,255,ATTRIBUTE_LEVEL,ST_ABB_TRACKING_SEAM_PATTERN_NR)
      attribDouble = attribCreator.AddDouble(ST_ABB_TRACKING_SEARCH_LENGTH,0.150,0.005,0.150,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH,ST_ABB_TRACKING_SEARCH_LENGTH)
      attribIntENM = attribCreator.AddEnum(ST_ABB_TRACKING_CONT_AFTER_ERR,ST_ABB_TRACKING_CONT_AFTER_ERR_LIST,ST_ABB_TRACKING_CONT_AFTER_ERR_LIST[0],ATTRIBUTE_GLOBAL_LEVEL,ST_ABB_TRACKING_CONT_AFTER_ERR)
      attribDouble = attribCreator.AddDouble(ST_ABB_TRACKING_MAX_LIN_CORRECTION,0.050,0.0,0.05,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH,ST_ABB_TRACKING_MAX_LIN_CORRECTION)
      attribDouble = attribCreator.AddDouble(ST_ABB_TRACKING_CORR_ELIM_DISTANCE,0.200,0.005,0.2,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH,ST_ABB_TRACKING_CORR_ELIM_DISTANCE)
      attribDouble = attribCreator.AddDouble(ST_ABB_TRACKING_OFF_DISTANCE,0.0,-0.1,0.1,0.001,ATTRIBUTE_LEVEL,ATTRIB_LENGTH,ST_ABB_TRACKING_OFF_DISTANCE)
      attribDouble.SetVisibility(False)
      attribBool   = attribCreator.AddBool(ST_ABB_TRACKING_OFF_KEEPDISTANCE,True,ATTRIBUTE_LEVEL,ST_ABB_TRACKING_OFF_KEEPDISTANCE)
   except:
      logging.LogError("Cannot initialize vendor specific touch sensing work method attributes")

   seamTrackingDistance = attribGetter.GetAttributeByName(ST_SEAMTRACKING_DISTANCE)
   seamTrackingDistance.SetOlpProperty(GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

def PostWmInitEvents(WmEventInitOperator: CENPyOlpWM_EventInitOperator):
   WmEventInitOperator.RegisterPyTechnologyEvent('SeamTrackOnEvent.py')
   WmEventInitOperator.RegisterPyTechnologyEvent('SeamTrackOffEvent.py')
   WmEventInitOperator.RegisterPyTechnologyEvent('SeamTrackingSearchStart.py')
   WmEventInitOperator.RegisterPyTechnologyEvent('SeamTrackingLeadInEvent.py')

   # WmEventInitOperator.RegisterPyTechnologyEvent('ArcSpotEvent.py')
   # WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_TEACH_EVENT_FILE)
   # add Python Approach&Retract Event to WM
   # WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_SCAN_EVENT_FILE)
   # WmEventInitOperator.RegisterPyTechnologyEvent(PY_SEAMFIND_REF_EVENT_FILE)
   # WmEventInitOperator.RegisterPyTechnologyEvent(PY_LINELASERPOV_EVENT_FILE)
   pass

def PostWmInitRules(WmRuleInitOperator: CENPyOlpWM_RuleInitOperator):
   # get logger
   logging = WmRuleInitOperator.GetLoggerOperator()
   # Remove C++ APPROACH Event from Rule

# -------------------------------------------------------------------------------------------
# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator: CENPyOlpWM_SyncPgAttribOperator):
   # get logger
   # logging = Operator.GetLoggerOperator()
   # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_START)

   # attribGetter = Operator.GetAttribGetter()

   # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_END)
   pass

# -------------------------------------------------------------------------------------------
def PostWmOnAttribChanged(Operator: CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   
