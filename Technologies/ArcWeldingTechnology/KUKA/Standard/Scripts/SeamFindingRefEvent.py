# -------------------------------------------------------------------------------------------
# Name: SeamFindingRefEvent
# Description: with this event a special point within the touch operation is marked
# Debug info: E2@localhost:5254
# Author: Berauer
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
from centypes import *
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamFindingRefEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology-Technology) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug-Technology) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug-Technology) event post process attrib ended."

DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START = "(Debug-Technology) event post process upload attrib started."
DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END = "(Debug-Technology) event post process upload attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug-Technology) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug-Technology) event post compute ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) prev on attribute change ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

# Operation attribute definition


# Download attribute definition


# -------------------------------------------------------------------------------------------
# Event post init attributes
# def PostInitAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

#    try:
#       # get attribute creator
#       attribCreator = Operator.GetAttribCreator()
#       # get attribute setter
#       attribSetter = Operator.GetAttribSetter()
#       # get attribute getter
#       attribGetter = Operator.GetAttribGetter()
#    except:
#       logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# post process attribute
# def PostProcessAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# post process upload attribute
# def PostProcessAttributesUpload(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 


# -------------------------------------------------------------------------------------------
# post event compute    
# def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

#    # YOUR CODE
#    logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)


# -------------------------------------------------------------------------------------------
# event post on attribute change 
def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   changedAttrib = Operator.GetChangedAttributeName()  
   # attribName = changedAttrib.GetName()

   # YOUR CODE
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)


# -------------------------------------------------------------------------------------------
# 
def GetEventName():
   return "SeamFindingRefEvent"
   
# Set UUID mandatory
def GetEventUuId():
   return "89B68E1A-654A-428A-BD9C-375FCDDDD334"
   
def GetIconName():
   return "Circle"

def GetExplodeCycle():
   return 0

def IsMachiningCycle():
   return 0

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEFORBIDDEN

def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_HIDDEN

def GetMultipleCreationIsPossible():
   return 1

def GetEventType():
   return OLPEVENT_OLP

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSNO

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSNO

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTPATHTOOL

def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTPATHTOOL

# Set cycle as teachable
def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_NORMAL

def GetCycleDownloadBehaviour():
   return CYCLEDOWNLOAD_NORMALREFPOINTANDPROCESSPOINTS


# def GetProcessType():
#    return 7

# def GetGroupName():
#    return "Test"

def IsEnabled():
   return False