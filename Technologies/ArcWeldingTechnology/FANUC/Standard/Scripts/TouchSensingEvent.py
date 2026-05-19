from centypes import *
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "TouchSensingEvent.py: "

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
AlongFaceToNormal = 0
AlongBaseFrame = 1


AW_MOTION_TYPE = "OperationGroupMotionType"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_TOUCHSENS_TOUCH_DIRECTION = "TSTouchDirection" # AlongFaceToNormal = 0, AlongBaseFrame = 1
AW_TOUCH_BASE_DIRECTION = "TouchBaseDirection"
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TS_BASEFRAME_TOUCH_AXIS = "TSBaseFrameTouchAxis"
AW_TOUCHSENS_SENSING_SPEED="SensingSpeed"
AW_TOUCHSENS_APPR_RETR_SPEED="TouchApprRetrSpeed"
AW_TOUCHSENS_APPR_RETR_FLYBY="TouchApprFlyBy"

# Events to indicate the different touch points for download only
TOUCH_POINT_START_APP_EVENT_UUID = "5b4dcd32-d29b-11ec-9d64-0242ac120002"
TOUCH_POINT_START_RET_EVENT_UUID = "61c660a2-d29b-11ec-9d64-0242ac120002"
TOUCH_POINT_COLLISION_EVENT_UUID = "4f259b16-d29b-11ec-9d64-0242ac120002"
TOUCH_POINT_END_EVENT_UUID = "53d9f698-d29b-11ec-9d64-0242ac120002"

# -------------------------------------------------------------------------------------------
# Event post init attributes
# def PostInitAttributes(Operator):
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
   # # get logger
   # logging = Operator.GetLoggerOperator()
   # # debug logging: create attributes
   # logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

   # logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 


# -------------------------------------------------------------------------------------------
# post event compute 
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
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
      return


   # SEARCH MOTION TYPE INDEX (0 = PTP; 1 = LIN)
   searchMoTypeIndex = 0
   try:
      searchMoTypeFirstTpeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE_FIRST_TPE)
      searchMoTypeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE)
      searchDirection = attribGetter.GetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION)
      touchStartDistance = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_LENGTH)
      touchEndDistance = attribGetter.GetDouble(AW_TOUCHSENS_OVERTRAVEL_LENGTH)
      touchSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_SPEED)
      apprRetrSpeed = attribGetter.GetDouble(AW_TOUCHSENS_APPR_RETR_SPEED)
      retrFlyBy = attribGetter.GetDouble(AW_TOUCHSENS_APPR_RETR_FLYBY)
   except:
      logging.LogError('Cannot get the attribute AW_MOTION_TYPE!')
      

   # set distance between collision point and start point
   tsOperator.SetTouchStartDistance(touchStartDistance)

   # set distance between collision point and end point
   tsOperator.SetTouchEndDistance(touchEndDistance)

   # GetStartPoint()  tsOperator->GetEndPoint()  tsOperator->GetCollisionPoint()  tsOperator->GetReferencePoint()
   tsRefPointMatrix = tsOperator.GetReferencePoint()
   tsStartPointMatrix = tsOperator.GetStartPoint(searchDirection)
   tsEndPointMatrix = tsOperator.GetEndPoint(searchDirection)
   tsCollisionPointMatrix = tsOperator.GetCollisionPoint(searchDirection)

   # SIMULATION
   # start point - collision point - start point
   # DOWNLOAD
   # start point: one time, not twice
   # collision point: 
   # touch sensing operators
   if (tsRefPointMatrix or tsStartPointMatrix or tsEndPointMatrix or tsCollisionPointMatrix):
      if (tsStartPointMatrix):
         if searchMoTypeFirstTpeIndex == LIN:
            tpElementStartApp = Operator.MoveLin(tsStartPointMatrix)
         else:
            tpElementStartApp = Operator.MovePTP(tsStartPointMatrix)
      if (tsCollisionPointMatrix):
         if searchMoTypeIndex == LIN:
            tpElementCollision = Operator.MoveLin(tsCollisionPointMatrix)
         else:
            tpElementCollision = Operator.MovePTP(tsCollisionPointMatrix)
      # else:
      #    if (tsEndPointMatrix):
      #       if searchMoTypeIndex == LIN:
      #          tpElementEnd = Operator.MoveLin(tsEndPointMatrix)
      #       else:
      #          tpElementEnd = Operator.MovePTP(tsEndPointMatrix)
      if (tsStartPointMatrix):
         if searchMoTypeIndex == LIN:
            tpElementStartRet = Operator.MoveLin(tsStartPointMatrix)
         else: 
            tpElementStartRet = Operator.MovePTP(tsStartPointMatrix)
   else:
      # Alternative Actions
      downUnder = Operator.GetReferenceTpElementInitialMatrix()
      if searchMoTypeIndex == LIN:
         Operator.MoveLin(downUnder)
      else:
         Operator.MovePTP(downUnder)
   
   # LastTouchDir: Undefined=0, X+=1, X-=2, Y+=3, etc...
   searchBaseAxis = 0
   if (searchDirection == AlongBaseFrame):
      searchBaseAxis = tsOperator.GetLastTouchDir()
   
   touchPointStartAppEvent = eventOperator.AddEvent(TOUCH_POINT_START_APP_EVENT_UUID, tpElementStartApp, TPINSERTPOS_INSERTBEFORE)
   touchPointStartAppEvent.SetInteger(AW_TOUCH_BASE_DIRECTION, searchBaseAxis)
   
   eventOperator.AddEvent(TOUCH_POINT_COLLISION_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
   eventOperator.AddEvent(TOUCH_POINT_START_RET_EVENT_UUID,tpElementStartRet,TPINSERTPOS_INSERTBEFORE)
   
   # Set Accuracy On Approach Event
   apprAccuracyEvent = eventOperator.AddAccuracyEvent(tpElementStartApp,TPINSERTPOS_INSERTBEFORE)
   apprAccuracyEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   apprAccuracyEvent.SetAccuracy(retrFlyBy)

   # Set Approach Sensing Speed
   apprSpeedEvent=eventOperator.AddSpeed(tpElementStartApp,TPINSERTPOS_INSERTBEFORE)
   apprSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   apprSpeedEvent.SetSpeed(apprRetrSpeed)

   # Set Touch Sensing Speed
   touchSpeedEvent=eventOperator.AddSpeed(tpElementCollision,TPINSERTPOS_INSERTBEFORE)
   touchSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   touchSpeedEvent.SetSpeed(touchSpeed)

   # Set Retract Sensing Speed
   apprSpeedEvent=eventOperator.AddSpeed(tpElementStartRet,TPINSERTPOS_INSERTBEFORE)
   apprSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   apprSpeedEvent.SetSpeed(apprRetrSpeed)

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