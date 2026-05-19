from centypes import *

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

# Laser Tracking on/off
AW_SEAMTRACKING_ONOFF = "SeamTrackingOnOff"
 
def PostWmInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribCreator = Operator.GetAttribCreator()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # your code 
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


   # Make seam tracking on/off Global, Process and User
   attSeamTrackingOnOff = attribCreator.AddBool(AW_SEAMTRACKING_ONOFF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_SEAMTRACKING_ONOFF)
   # attSeamTrackingOnOff = attribGetter.GetAttributeByName(AW_SEAMTRACKING_ONOFF)
   # attSeamTrackingOnOff.SetOlpProperty(PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE)
   attSeamTrackingOnOff.SetVisibility(True)
   pass 

def PostWmInitEvents(Operator):
   pass

def PostWmInitRules(Operator):
   pass

def PostWmOnAttribChanged(Operator):
   pass

def PostWmSyncPgAttributes(Operator):
   pass

def PostProcessOperationAttributes(Operator):
   pass
