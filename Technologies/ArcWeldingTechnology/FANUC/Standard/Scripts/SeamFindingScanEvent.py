# -------------------------------------------------------------------------------------------
# Name: SeamFindingScanEvent
# Description: with this event a position is marked to output the required scanner syntax in the downloader
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
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamFindingScanEvent.py: "

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
# def PostCompute(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)


# -------------------------------------------------------------------------------------------
# event post on attribute change 
# def PostOnAttribChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

#    # changedAttrib = Operator.GetChangedAttribute()  
#    # attribName = changedAttrib.GetName()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)


# -------------------------------------------------------------------------------------------
# 
def GetEventName():
   return "SeamFindingScanEvent"
   
def GetEventUuId():
   return "bde08f6e-e836-4e64-9c27-0ddc0c02f323"
   
def GetIconName():
   return "ArcWeldCalibration_SeamFinding"
   
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
   return CYCLEROTATION_ROTNO
   
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTNO
   
def GetGroupName():
   return "OlpEvent"

def IsEnabled():
   return False