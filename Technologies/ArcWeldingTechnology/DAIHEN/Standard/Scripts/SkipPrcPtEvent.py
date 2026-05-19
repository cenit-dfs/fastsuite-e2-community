from centypes import *
import math
import inspect, os
import csv
import ctypes
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# Event skip process point
# this event does not define any parameters but it declares this point as a machining cyle which means, this tpe will
# neither be simulated or written in the output.
# You have to be carefully, because all events or tpe relative to this tpe will also be suppressed (Approach, retract or teach inserts)
# -------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SkipPrcPtEvent.py: "

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

def GetEventName():
   return "SkipPrcPtEvent"

def GetEventUuId():
   return "30abbd0a-30ca-4ebe-8358-6089f9542492"

def GetIconName():
   return "ToolpathApproach"

def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEFORBIDDEN

def GetMultipleCreationIsPossible():
   return 1

def GetEventType():
   return OLPEVENT_PROCESS

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTTOOL

def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTTOOL

def IsMachiningCycle():
   return 1

def GetGroupName():
   return "OlpEvent"

def IsEnabled():
   return False

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   #attribCreator = Operator.GetAttribCreator()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()

# -------------------------------------------------------------------------------------------
# post event compute
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()


