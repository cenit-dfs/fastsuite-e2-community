from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "LT_Param_Event.py: "

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
LTJ_DEF = "JobNumberLaser"
LTBIAS_X_DEF = "LTBiasX"
LTBIAS_Y_DEF = "LTBiasY"
LTBIAS_Z_DEF = "LTBiasZ"

# Event attribute definition
LTJ_DL = "DLJobNumberLaser"
LTBIAS_X_DL = "DLLTBiasX"
LTBIAS_Y_DL = "DLLTBiasY"
LTBIAS_Z_DL = "DLLTBiasZ"
LTOFF_DL = "DLLTOff"

def GetEventName():
   return "LT_Param_Event"
   
def GetEventUuId():
   return "F21BBF39-ED1F-446A-8B0C-ED7860AAE2B1"
   
def GetIconName():
   return "LaserCladding"
   
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

def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   
   # Laser Tracking Attributes
   # LJT
   att1 = attribCreator.AddInt(LTJ_DL, 1, 0, 255, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTJ_DL)
   att1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   
   # LTBIAS X, Y, Z
   att2 = attribCreator.AddDouble(LTBIAS_X_DL, 0.0,-0.015,0.015,0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_X_DL)
   att2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att3 = attribCreator.AddDouble(LTBIAS_Y_DL, 0.0,-0.015,0.015,0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_Y_DL)
   att3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att4 = attribCreator.AddDouble(LTBIAS_Z_DL, 0.0,-0.015,0.015,0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_Z_DL)
   att4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # LTOFF
   att5 = attribCreator.AddBool(LTOFF_DL, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTOFF_DL)
   att5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
  
def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   pass   

def PostCompute(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   pass
   
def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   pass
