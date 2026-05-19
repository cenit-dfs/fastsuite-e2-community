from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SPSEvent.py: "

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
SPSPTN_DEF = "PatternNumber"
SPSSD_DEF = "StartDistance"
SPSTPRD_DEF = "TouchPointReliefDistance"
SPSSDG_DEF = "SensingDistanceInTheGroove"

# Event attribute definition
SPSPTN_DL = "DLPatternNum"
SPSSD_DL = "DLStartDist"
SPSTPRD_DL = "DLReliefDist"
SPSSDG_DL = "DLDistInGroove"

def GetEventName():
   return "SPSEvent"
   
def GetEventUuId():
   return "906A4490-207B-4733-AC79-006C5DE77358"
   
def GetIconName():
   return "ControllerLogic"
   
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
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   attribCreator = Operator.GetAttribCreator()
   
   # Laser Tracking Attributes
   # LJT
   att1 = attribCreator.AddInt(SPSPTN_DL, 1, 1, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SPSPTN_DL)
   att1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   
   # LTBIAS X, Y, Z
   att2 = attribCreator.AddInt(SPSSD_DL, 1, 1, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SPSSD_DL)
   att2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att3 = attribCreator.AddInt(SPSTPRD_DL, 1, 1, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SPSTPRD_DL)
   att3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att4 = attribCreator.AddInt(SPSSDG_DL, 1, 1, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SPSSDG_DL)
   att4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

  
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
