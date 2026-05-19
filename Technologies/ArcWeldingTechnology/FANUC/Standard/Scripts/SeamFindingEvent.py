# -------------------------------------------------------------------------------------------
# Name: SeamFindingEvent
# Description: adding SeamFinding Points with respect to Standard basic.
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------
from centypes import *
import sys
sys.dont_write_bytecode = True
# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamFindingEvent.py: "

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

AW_SEAMFIND_DISTANCE = "SeamFindingDistance";
AW_SEAMFIND_OPTIONAL_DIR = "SeamFindingOptionalDirection";
AW_SEAMFIND_SENSING_SPEED = "SeamFindingSensingSpeed";
AW_SEAMFIND_LINKING_SPEED = "SeamFindingLinkingSpeed";
AW_SEAMFIND_END_LOCATION = "SeamFindingEndLocation";

# Events to indicate the different touch points for download only
AW_SEAM_FINDING_SCAN_EVENT_UUID = "bde08f6e-e836-4e64-9c27-0ddc0c02f323"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
    # get logger
    logging = Operator.GetLoggerOperator()

# -------------------------------------------------------------------------------------------
# post event compute
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get event operator
   eventOperator = Operator.GetEventOperator()
   # get reference toolpath element
   refTpElement= Operator.GetRefTpElement()
   # get SeamFinding operator
   sfOperator = Operator.GetSeamFindingOperator()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribGetter == None) or (eventOperator == None) or (refTpElement == None) or (sfOperator == None) or (controller == None):
      logging.LogError("TouchSensingEvent Python, zero pointer initialization PostCompute")

   # getting the SeamFinding Attributes
   try:
      atEndLocation = attribGetter.GetBool(AW_SEAMFIND_END_LOCATION)
      optionalDir = attribGetter.GetBool(AW_SEAMFIND_OPTIONAL_DIR)
      seamFindDistance = attribGetter.GetDouble(AW_SEAMFIND_DISTANCE)
      seamFindSensingSpeed = attribGetter.GetDouble(AW_SEAMFIND_SENSING_SPEED)
      seamFindLinkingSpeed = attribGetter.GetDouble(AW_SEAMFIND_LINKING_SPEED)
   except:
      logging.LogError('Cannot get the SeamFinding attributes!')
      
   # get the Point Matrixes from SeamFindingOperator
   sfStartPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   sfRefPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, 0.0)
   
   if (sfStartPointMatrix and sfRefPointMatrix):
      # got the Event Points
      # to the StartPoint
      tpElementStart = Operator.MoveLin(sfStartPointMatrix)
      eventOperator.AddEvent(AW_SEAM_FINDING_SCAN_EVENT_UUID, tpElementStart, TPINSERTPOS_INSERTAFTER)
      # to the RefPoint
      tpElementRef = Operator.MoveLin(sfRefPointMatrix)
   else:
      # Alternative Actions
      startM = Operator.GetReferenceTpElementInitialMatrix()
      startM.Translate(seamFindDistance, 0.0, 0.0, True)
      # to the StartPoint
      tpElementStart = Operator.MoveLin(startM)
      refM = Operator.GetReferenceTpElementInitialMatrix()
      # to the RefPoint
      tpElementRef = Operator.MoveLin(refM)
      
   # Set SeamFind Sensing Speed
   sensingSpeedEvent=eventOperator.AddSpeed(tpElementStart,TPINSERTPOS_INSERTAFTER)
   sensingSpeedEvent.SetSpeed(seamFindSensingSpeed)
   # Set SeamFind Linking Speed
   linkingSpeedEvent=eventOperator.AddSpeed(tpElementRef,TPINSERTPOS_INSERTAFTER)
   linkingSpeedEvent.SetSpeed(seamFindLinkingSpeed)

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

# -------------------------------------------------------------------------------------------

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY   
   
def GetEventType():
   return OLPEVENT_APPROACH
   
def IsMachiningCycle():
   return False

def GetGroupName():
   return "TpdbIgnore"