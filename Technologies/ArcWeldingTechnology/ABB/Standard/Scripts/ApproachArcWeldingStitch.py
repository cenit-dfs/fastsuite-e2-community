# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Extend standard ArcOnEvent for KUKA KRC4/5
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
import inspect, os, json
import sys
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# Global definitions
# -------------------------------------------------------------------------------------------
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
# -------------------------------------------------------------------------------------------

EVENT_FILE_NAME = "ApproachArcWeldingStitch.py"
EVENT_NAME = "ApproachArcWeldingStitch"
EVENT_ICON = "ArcOn"
EVENT_ATTRIBUTE_TYPE = USER_ATTRIBUTE | PROCESS_ATTRIBUTE

def GetEventName():
   return EVENT_NAME

def GetIconName():
   return EVENT_ICON

def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   attribDouble = attribCreator.AddDouble('SpeedViaApproach',0.0,0,100,0.1,PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE ,ATTRIB_STANDARD,'SpeedViaApproach')


# post process attribute
def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   pass

# post event compute    
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # try:
   #    # get attribute creator
   #    attribGetter = Operator.GetAttribGetter()
   #    # get controller
   #    controller = Operator.GetController()
   #    # get reference toolpath element operator
   #    refTpe = Operator.GetRefTpElement()
   #    # get event operator
   #    eventOperator = Operator.GetEventOperator()
   # except:
   #    # log error
   #    logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)
   #    return

   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
# -------------------------------------------------------------------------------------------
