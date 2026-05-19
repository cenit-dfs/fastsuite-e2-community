from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
# LaserTrackingEvent (Online)
FILE_NAME = "SeamTrackerOffEvent.py: "

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
   return "SeamTrackerOffEvent"
   
def GetEventUuId():
   return "cea2e6fe-e5e8-4818-9f27-c21f27cd4b86"
   
def GetIconName():
   return "ArcWeldCalibration_SeamTracking"
   
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
