# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Adds ArcOn program number to standard event
# Debugg info: E2@localhost:5254
# Author:
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import inspect, os
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "LaserOn.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

# Event Attributes

# Operation attribute definition

def GetEventName():
   return "LaserOn"

# -------------------------------------------------------------------------------------------
# Event post init attributes

def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # att1 = attribCreator.AddInteger(ATT_EVT_WEAVE_ON_CMD, 99, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_ON_CMD)
   # att1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   # att1.SetVisibility(False)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostOnAttribChanged(Operator):
	# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()

   #UseWeave = attribGetter.GetBool(ATT_EVT_WEAVE_ONOFF) 
   #attribGetter.GetAttributeByName(ATT_EVT_WEAVE_ON_CMD).SetVisibility(UseWeave)
   #attribGetter.GetAttributeByName(ATT_EVT_WEAVE_FREQ).SetVisibility(False)
   #attribGetter.GetAttributeByName(ATT_EVT_WEAVE_WIDTH).SetVisibility(False)
   #attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME1).SetVisibility(False)
   #attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME2).SetVisibility(False)
   
   
def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   #if (Operator.IsEventCreatedAutomatically()):
   #   UseWeave = attribGetter.GetBool(ATT_AW_USE_WEAVE_DEFINE)
   #   attribSetter.SetBool(ATT_EVT_WEAVE_ONOFF,UseWeave)
      
   #   WeaveOnPrgNumber = attribGetter.GetInteger(ATT_AW_WEAVE_ON_CMD)
   #   attribSetter.SetInteger(ATT_EVT_WEAVE_ON_CMD,WeaveOnPrgNumber)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()