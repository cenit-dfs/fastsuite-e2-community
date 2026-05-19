# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Sets some Upload Attributes
# Debug info: E2@localhost:5254
# Author: Cenit AG 2025
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------
from centypes import *
from cenpylib import *
import importlib
import inspect, os
import sys
import csv

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "UploadTSMotionEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug) prev on attribute change ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

# Event Attributes
IS_TS_MOTION = "IsTouchSensingMotion"
PRE_PARAMS = "PreParameters"
POST_PARAMS = "PostParameters"

# Operation attribute definition

def GetEventName():
   return "UploadTSMotionEvent"

def GetIconName():
   return "Upload"

def GetEventUuId():
   return "6AA8DD46-8DFC-4403-8291-7F6D683973C1"

def GetEventType():
   return OLPEVENT_OLP

def IsEnabled():
   return False
   
def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY

# -------------------------------------------------------------------------------------------
# Event post init attributes

def PostInitAttributes(Operator : CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   #logging.LogInfo("**********************************  UploadEvent  InitAttribute *******************************************")
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   att2 = attribCreator.AddBool(IS_TS_MOTION, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE , IS_TS_MOTION)
   att2.SetVisibility(False)
   att3 = attribCreator.AddString(PRE_PARAMS, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , PRE_PARAMS)
   att3.SetVisibility(True)
   att4 = attribCreator.AddString(POST_PARAMS, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , POST_PARAMS)
   att4.SetVisibility(True)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
	# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)

def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()


# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   #logging.LogInfo("**********************************  UploadEvent  PostCompute *******************************************")
   # get getter
   attribGetter = Operator.GetAttribGetter()
   pass
