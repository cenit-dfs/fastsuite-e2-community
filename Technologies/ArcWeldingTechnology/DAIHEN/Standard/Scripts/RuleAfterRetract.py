# Import libraries
from centypes import *

# -------------------------------------------------------------------------------------------
# Event Definition in C++
# This Python only override some Attributes or Callbacks
# General global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "RetractArcWeldingStitch.py: "

# DEBUG
DEBUG_POST_EVENT_RULE_COMPUTE_START = "(Debug) rule post compute started."
DEBUG_POST_EVENT_RULE_COMPUTE_END = "(Debug) rule post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMTRACKING_ONOFF = "SeamTrackingOnOff"
AW_SEAMFINDING = "SeamFinding"   
AW_SEAMTRACKING = "SeamTracking"

def GetUniqueId():
   return "d6949f48-c13e-45a3-bb4f-ad06570e359a"
   
def GetRuleProcessType():
   return EVENTPROCESS_TECHEVENT

def GetInsertPosition():
   return TPINSERTPOS_INSERTAFTER

def GetActiveEvent():
   return 0

def GetVisibility():
   return True

def NeedSelection():
   return True

def GetSelectability():
   return True

def HasDefault():
   return True

def PostExecute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_RULE_COMPUTE_START)

   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()

   # Add seam tracker off event after retract end
   try:
      calibrationMethod=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
   except:
      logging.LogError(ERROR_GET_ATTRIB +' '+ AW_SEAM_CALIBRATION_METHOD)
   try:
      seamTrackingOnOff=attribGetter.GetBool(AW_SEAMTRACKING_ONOFF)
   except:
      logging.LogError(ERROR_GET_ATTRIB +' '+ AW_SEAMTRACKING_ONOFF)

   if ((calibrationMethod == AW_SEAMFINDING) or (calibrationMethod == AW_SEAMTRACKING)) and seamTrackingOnOff:
      tpes = Operator.FindTpeByTechRequestId(TPETECHREQUESTID_RETRACTEND)
      for x in tpes:
         Operator.AddTpe(x)
