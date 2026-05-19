from centypes import *
from cenpylib import *
import math
import inspect, os
import csv
import ctypes
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))


# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamFindTeachTSWMEvent.py: "

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

# Operation attribute definition
AW_SEAMFIND_SENSING_SPEED = "SeamFindingSensingSpeed"
AW_SEAMFIND_LINKING_SPEED = "SeamFindingLinkingSpeed"

#Laser Scanner attribs
AW_LASER_FOV_X = "LaserFovX"
AW_LASER_FOV_Y = "LaserFovY"
AW_LASER_FOV_Z = "LaserFovZ"
AW_LASER_FOV_RX = "LaserFovA"
AW_LASER_FOV_RY = "LaserFovB"
AW_LASER_FOV_RZ = "LaserFovC"

# Events to indicate the different touch points for download only
AW_SEAM_FINDING_REF_EVENT_UUID  = "89B68E1A-654A-428A-BD9C-375FCDDDD334"
AW_SEAM_FINDING_SCAN_EVENT_UUID = "23d47a8b-11d4-4064-b558-d13f45df34aa"
AW_LINELASERPOV_EVENT_UUID      = "0D196218-D99F-461F-8C41-06278F654123"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   
   
def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
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
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Approach Length
   try:
      LX1 = attribGetter.GetDouble(AW_LASER_FOV_X)
      LY1 = -attribGetter.GetDouble(AW_LASER_FOV_Y)
      LZ1 = attribGetter.GetDouble(AW_LASER_FOV_Z)
   except:
      logging.LogError('Cannot get the Escape Frame Attributes!')

   refTpElement = Operator.GetRefTpElement()
   eventOperator = Operator.GetEventOperator()

   eventOperator.AddEvent(AW_SEAM_FINDING_REF_EVENT_UUID, refTpElement, TPINSERTPOS_INSERTBEFORE)
   
   # Get the Initial Path Matrix (Start Point)
   # M1 = Operator.GetRefTpElement().GetInitialPathMatrix ()
   M1 = Operator.GetRefTpElement().GetGlobalTransformedMatrixUnaligned ()
   M1P = M1.GetPosition().GetXYZ()
   M1R = M1.GetRotation()
   # M1 = Operator.GetRefTpElement().GetInitialPathMatrixTranslatedInBaseFrame ()
   # M2 = Operator.GetRefTpElement().GetMatrix ()
   # M2 = M1.Inverse()
   # M2P = M2.GetPosition().GetXYZ()
   # M2R = M2.GetRotation()
   # M1.SetRotation(M2.GetXDirection(), M2.GetYDirection(), M2.GetZDirection())
   # Move Matrix
   M1.Translate(LX1,LY1,LZ1,True)
   
   # First point
   first = Operator.MoveLin(M1)
   #Add IsEscapeFrameEvent
   eventOperator.AddEvent(AW_SEAM_FINDING_SCAN_EVENT_UUID, first, TPINSERTPOS_INSERTAFTER)
   laserMove = eventOperator.AddEvent(AW_LINELASERPOV_EVENT_UUID, first, TPINSERTPOS_INSERTAFTER)
   eventOperator.ExecuteEvent(laserMove)
   
def GetEventName():
   return "SeamFindTeachTSWMEvent"

def GetEventUuId():
   return "FB052ADC-BA26-4BC6-A789-BDF108ABC84F"

def GetIconName():
   return "ArcWeldCalibration_SeamFinding"
   
def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
   # return CYCLE_EXPLODEIMMEDIATELY
   return CYCLE_EXPLODEIMMEDIATELY
   
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
   
def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_TEACHABLE

def GetCycleDownloadBehavior():
   return CYCLEDOWNLOAD_NORMALREFPOINTANDPROCESSPOINTS

def IsMachiningCycle():
   return 1

def GetGroupName():
   return ""
   
def IsEnabled():
   return False
