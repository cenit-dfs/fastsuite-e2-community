# -------------------------------------------------------------------------------------------
# Name: ArcOffEvent
# Description: Adds ArcOff program number to standard event
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
import inspect, os
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "ArcOffEvent.py: "

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
ATT_EVT_PROG_NUMBER = "ProgNumber"

# Operation attribute definition
ATT_AW_ARC_OFF_CMD = "ProgNumber2Define"

def GetEventName():
   return "ArcOffEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes

def PostInitAttributes(Operator : CENPyOlpEvent_AttribInitOperator):
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

   att1 = attribCreator.AddInteger(ATT_EVT_PROG_NUMBER, 99, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_PROG_NUMBER)
   att1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   
   
def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   if (Operator.IsEventCreatedAutomatically):
      ArcOffPrgNumber = attribGetter.GetInteger(ATT_AW_ARC_OFF_CMD)
      attribSetter.SetInteger(ATT_EVT_PROG_NUMBER,ArcOffPrgNumber)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()