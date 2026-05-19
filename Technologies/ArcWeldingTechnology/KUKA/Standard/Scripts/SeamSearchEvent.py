# -------------------------------------------------------------------------------------------
# Name: SeamSearchEvent
# Description: adding touch points with respect to Standard basic.
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import sys
sys.dont_write_bytecode = True

# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamSearchEvent.py: "

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

PTP = 0
LIN = 1
TouchLocationTypeAtStart = 1
TouchLocationTypeAtEnd = 2
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
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

#    try:
#       # get attribute creator
#       attribCreator = Operator.GetAttribCreator()
#       # get attribute setter
#       attribSetter = Operator.GetAttribSetter()
#       # get attribute getter
#       attribGetter = Operator.GetAttribGetter()
#    except:
#       logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   return 1

# -------------------------------------------------------------------------------------------
# post process attribute
# def PostProcessAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# post process upload attribute
# def PostProcessAttributesUpload(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 


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
   # get touch sensing operator
   tsOperator = Operator.GetTouchSensingOperator()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribGetter == None) or (eventOperator == None) or (refTpElement == None) or (tsOperator == None) or (controller == None):
      logging.LogError("SeamSearchEvent Python, zero pointer initialization PostCompute")

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
   M1 = Operator.GetRefTpElement().GetInitialPathMatrix ()
   
   # Move Matrix
   M1.Translate(LX1,LY1,LZ1,True)
   
   # First point
   first = Operator.MoveLin(M1)
   #Add IsEscapeFrameEvent
   eventOperator.AddEvent(AW_SEAM_FINDING_SCAN_EVENT_UUID, first, TPINSERTPOS_INSERTAFTER)
   laserMove = eventOperator.AddEvent(AW_LINELASERPOV_EVENT_UUID, first, TPINSERTPOS_INSERTAFTER)
   eventOperator.ExecuteEvent(laserMove)

   # apprAccuracyEvent = eventOperator.AddAccuracyEvent(first,TPINSERTPOS_INSERTBEFORE)
   # apprAccuracyEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   # apprAccuracyEvent.SetAccuracy(retrFlyBy)
   apprSpeedEvent=eventOperator.AddSpeed(first,TPINSERTPOS_INSERTBEFORE)
   apprSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   apprSpeedEvent.SetSpeed(20.0)

   # # SEARCH MOTION TYPE INDEX (0 = PTP; 1 = LIN)
   # searchMoTypeIndex = 0
   # try:
   #    searchMoTypeFirstTpeIndex = attribGetter.GetEnumIndex(AW_SEAMSEARCH_MOTION_TYPE_FIRST_TPE)
   #    searchMoTypeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE)
   #    searchDirection = attribGetter.GetEnumIndex(AW_SEAMSEARCH_TOUCH_DIRECTION)
   #    touchStartDistance = attribGetter.GetDouble(AW_SEAMSEARCH_SENSING_LENGTH)
   #    touchEndDistance = attribGetter.GetDouble(AW_SEAMSEARCH_OVERTRAVEL_LENGTH)
   #    touchSpeed = attribGetter.GetDouble(AW_SEAMSEARCH_SENSING_SPEED)
   #    apprRetrSpeed = attribGetter.GetDouble(AW_SEAMSEARCH_APPR_RETR_SPEED)
   #    retrFlyBy = attribGetter.GetDouble(AW_SEAMSEARCH_APPR_RETR_FLYBY)
   # except:
   #    logging.LogError('Cannot get the attribute AW_MOTION_TYPE!')
      

   # # set distance between collision point and start point
   # tsOperator.SetTouchStartDistance(touchStartDistance)

   # # set distance between collision point and end point
   # tsOperator.SetTouchEndDistance(touchEndDistance)

   # # GetStartPoint()  tsOperator->GetEndPoint()  tsOperator->GetCollisionPoint()  tsOperator->GetReferencePoint()
   # tsRefPointMatrix = tsOperator.GetReferencePoint()
   # tsStartPointMatrix = tsOperator.GetStartPoint(searchDirection)
   # tsEndPointMatrix = tsOperator.GetEndPoint(searchDirection)
   # tsCollisionPointMatrix = tsOperator.GetCollisionPoint(searchDirection)

   # # SIMULATION
   # # start point - collision point - start point
   # # DOWNLOAD
   # # start point: one time, not twice
   # # collision point: 

   # if (tsRefPointMatrix or tsStartPointMatrix or tsEndPointMatrix or tsCollisionPointMatrix):
   #    if (tsStartPointMatrix):
   #       if searchMoTypeFirstTpeIndex == LIN:
   #          tpElementStartApp = Operator.MoveLin(tsStartPointMatrix)
   #       else:
   #          tpElementStartApp = Operator.MovePTP(tsStartPointMatrix)
   #       #if (tsRefPointMtrx) Operator.MovePTP(tsRefPointMtrx)
   #    if (tsCollisionPointMatrix):
   #       if searchMoTypeIndex == LIN:
   #          tpElementCollision = Operator.MoveLin(tsCollisionPointMatrix)
   #       else:
   #          tpElementCollision = Operator.MovePTP(tsCollisionPointMatrix)
   #    # else:
   #    #    if (tsEndPointMatrix):
   #    #       if searchMoTypeIndex == LIN:
   #    #          tpElementEnd = Operator.MoveLin(tsEndPointMatrix)
   #    #       else:
   #    #          tpElementEnd = Operator.MovePTP(tsEndPointMatrix)
   #    if (tsStartPointMatrix):
   #       if searchMoTypeIndex == LIN:
   #          tpElementStartRet = Operator.MoveLin(tsStartPointMatrix)
   #       else: 
   #          tpElementStartRet = Operator.MovePTP(tsStartPointMatrix)

   # else:
   #    # Alternative Actions
   #    downUnder = Operator.GetReferenceTpElementInitialMatrix()
   #    #downUnder.Translate(0.0, 0.0, 0.0)
   #    if searchMoTypeIndex == LIN:
   #       Operator.MoveLin(downUnder)
   #    else:
   #       Operator.MovePTP(downUnder)

   # eventOperator.AddEvent(TOUCH_POINT_START_APP_EVENT_UUID, tpElementStartApp, TPINSERTPOS_INSERTBEFORE)
   # eventOperator.AddEvent(TOUCH_POINT_COLLISION_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
   # eventOperator.AddEvent(TOUCH_POINT_START_RET_EVENT_UUID, tpElementStartRet, TPINSERTPOS_INSERTBEFORE)

   # apprAccuracyEvent = eventOperator.AddAccuracyEvent(tpElementStartApp,TPINSERTPOS_INSERTBEFORE)
   # apprAccuracyEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   # apprAccuracyEvent.SetAccuracy(retrFlyBy)
   # apprSpeedEvent=eventOperator.AddSpeed(tpElementStartApp,TPINSERTPOS_INSERTBEFORE)
   # apprSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   # apprSpeedEvent.SetSpeed(apprRetrSpeed)
   # # Set Touch Sensing Speed
   # touchSpeedEvent=eventOperator.AddSpeed(tpElementCollision,TPINSERTPOS_INSERTBEFORE)
   # touchSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   # touchSpeedEvent.SetSpeed(touchSpeed)

   # apprSpeedEvent=eventOperator.AddSpeed(tpElementStartRet,TPINSERTPOS_INSERTBEFORE)
   # apprSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   # apprSpeedEvent.SetSpeed(apprRetrSpeed)
   
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)


# -------------------------------------------------------------------------------------------
# event post on attribute change 
# def PostOnAttribChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

#    # changedAttrib = Operator.GetChangedAttribute()  
#    # attribName = changedAttrib.GetName()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)
