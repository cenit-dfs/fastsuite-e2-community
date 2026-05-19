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
import ctypes
from centypes import *
from cenpylib import *
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

AW_SEAMFIND_DISTANCE = "SeamFindingDistance"
AW_SEAMFIND_OPTIONAL_DIR = "SeamFindingOptionalDirection"
AW_SEAMFIND_SENSING_SPEED = "SeamFindingSensingSpeed"
AW_SEAMFIND_LINKING_SPEED = "SeamFindingLinkingSpeed"
AW_SEAMFIND_END_LOCATION = "SeamFindingEndLocation"

# Events to indicate the different touch points for download only
AW_SEAM_FINDING_SCAN_EVENT_UUID = "23d47a8b-11d4-4064-b558-d13fcef2583d"
AW_SEAM_FINDING_REF_EVENT_UUID = "0D196218-D99F-461F-8C41-06278F35CC6F"
AW_LASER_FOV_X = "LaserFovX"
AW_LASER_FOV_Y = "LaserFovY"
AW_LASER_FOV_Z = "LaserFovZ"
AW_LASER_FOV_A = "LaserFovA"
AW_LASER_FOV_B = "LaserFovB"
AW_LASER_FOV_C = "LaserFovC"
AW_LASER_ZJ_BASE_POS_Y = "LaserZjBasePositionY"
AW_LASER_ZJ_BASE_POS_Z = "LaserZjBasePositionZ"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()

# -------------------------------------------------------------------------------------------
# post event compute
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
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
   atEndLocation = False  # Default initialization to avoid unbound variable
   # Initialize variables with default values
   atEndLocation = False
   optionalDir = False
   seamFindDistance = 0.0
   seamFindLinkingSpeed = 0.0
   ZjFovX = 0.0
   ZjFovY = 0.0
   ZjFovZ = 0.0
   ZjFovA = 0.0
   ZjFovB = 0.0
   ZjFovC = 0.0

   try:
      atEndLocation = attribGetter.GetBool(AW_SEAMFIND_END_LOCATION)
      optionalDir = attribGetter.GetBool(AW_SEAMFIND_OPTIONAL_DIR)
      seamFindDistance = attribGetter.GetDouble(AW_SEAMFIND_DISTANCE)
      # seamFindSensingSpeed = attribGetter.GetDouble(AW_SEAMFIND_SENSING_SPEED)
      seamFindLinkingSpeed = attribGetter.GetDouble(AW_SEAMFIND_LINKING_SPEED)
      ZjFovX = attribGetter.GetDouble(AW_LASER_FOV_X)
      ZjFovY = attribGetter.GetDouble(AW_LASER_FOV_Y)
      ZjFovZ = attribGetter.GetDouble(AW_LASER_FOV_Z)
      ZjFovA = attribGetter.GetDouble(AW_LASER_FOV_A)
      ZjFovB = attribGetter.GetDouble(AW_LASER_FOV_B)
      ZjFovC = attribGetter.GetDouble(AW_LASER_FOV_C)
   except:
      logging.LogError('Cannot get the SeamFinding attributes!')
      
   # get the Point Matrixes from SeamFindingOperator
   if not atEndLocation:
      optionalDir = not optionalDir

   if (optionalDir):
      sfRefPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, False, seamFindDistance*(-1))
   else:
      sfRefPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   # sfRefPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   sfRefPointMatrix.GetRotation()
   tpElementRef = Operator.MoveLin(sfRefPointMatrix)
   tpElementRefInBF = tpElementRef.GetMatrixToActiveBaseFrame()
   refPointXYZ = str(tpElementRefInBF.GetPosition().GetXYZ())
   refPointOri = str(tpElementRefInBF.GetRotation(True))
   eventOperator.AddEvent(AW_SEAM_FINDING_REF_EVENT_UUID, tpElementRef, TPINSERTPOS_INSERTBEFORE)

   # sfStartPointMatrix = tpElementRef.GetGlobalTransformedMatrix()
   sfStartPointMatrix = sfRefPointMatrix
   sfStartPointMatrix.RotateX(-ZjFovA)
   sfStartPointMatrix.RotateY(-ZjFovB)
   sfStartPointMatrix.RotateZ(-ZjFovC)
   sfStartPointMatrix.Translate(-ZjFovX, -ZjFovY, -ZjFovZ, True)
   # got the Event Points
   # to the StartPoint
   tpElementStart = Operator.MoveLin(sfStartPointMatrix)
   tpElementStartInBF = tpElementStart.GetMatrixToActiveBaseFrame()
   startPointXYZ = str(tpElementStartInBF.GetPosition().GetXYZ())
   startPointOri = str(tpElementStartInBF.GetRotation(True))
   eventOperator.AddEvent(AW_SEAM_FINDING_SCAN_EVENT_UUID, tpElementStart, TPINSERTPOS_INSERTAFTER)
      # # to the RefPoint
      # tpElementRef = Operator.MoveLin(sfRefPointMatrix)
      
   # Set SeamFind Sensing Speed
   sensingSpeedEvent=eventOperator.AddSpeed(tpElementStart,TPINSERTPOS_INSERTBEFORE)
   sensingSpeedEvent.SetSpeed(seamFindLinkingSpeed)

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

# -------------------------------------------------------------------------------------------

def GetEventName():
   return "SeamFindingEvent"
   
def GetEventUuId():
   return "82CC2C05-C801-431B-A9BF-4B9210C6E4B4"
   
# -------------------------------------------------------------------------------------------
