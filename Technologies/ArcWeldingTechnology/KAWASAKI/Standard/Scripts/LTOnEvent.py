from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
# LaserTrackingEvent (Online)
FILE_NAME = "LTOnEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."


# Operation attribute definition

# Event attribute definition


def GetEventName():
   return "LTOnEvent"
   
def GetEventUuId():
   return "C78BA38F-EC44-4ABB-A76E-511FD7F13204"
   
def GetIconName():
   return "Events_UltrasonicOn"
   
def GetExplodeCycle():
   return 0
   
def GetMultipleCreationIsPossible():
   return 1

def GetEventType():
   return OLPEVENT_OLP
   
def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTTOOL
   
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTTOOL
   
def IsMachiningCycle():
   return 0

def GetGroupName():
   return "OlpEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   #attribCreator = Operator.GetAttribCreator()
   
   # This Event has no Attributes
   
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass

  
def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)
   pass   

# -------------------------------------------------------------------------------------------
# Event post compute
def PostCompute(Operator):
   pass
   
def PostOnAttribChanged(Operator):
   pass
