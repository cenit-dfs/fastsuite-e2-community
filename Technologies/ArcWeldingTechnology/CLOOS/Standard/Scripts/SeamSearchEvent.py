# -------------------------------------------------------------------------------------------
# Name: TouchSensingEvent
# Description: adding touch points with respect to vendor basic.
# Debug info: E2@localhost:5254
# Author: Hohmann
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
AW_MOTION_TYPE = "OperationGroupMotionType"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_TOUCHSENS_TOUCH_DIRECTION = "TSTouchDirection" # AlongFaceToNormal = 0, AlongBaseFrame = 1
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TOUCHSENS_SENSING_SPEED="SensingSpeed"

# Events to indicate the different touch points for download only
TOUCH_POINT_START_APP_EVENT_UUID = "a1433ae6-d513-11ec-9d64-0242ac120002"
TOUCH_POINT_COLLISION_EVENT_UUID = "a7c23bb0-d513-11ec-9d64-0242ac120002"
TOUCH_POINT_END_EVENT_UUID = "b672844e-d513-11ec-9d64-0242ac120002"
TOUCH_POINT_START_RET_EVENT_UUID = "b1b220f4-d513-11ec-9d64-0242ac120002"


# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   try:
      # get attribute creator
      attribCreator = Operator.GetAttribCreator()
      # get attribute setter
      attribSetter = Operator.GetAttribSetter()
      # get attribute getter
      attribGetter = Operator.GetAttribGetter()
   except:
      logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# post process attribute
def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# post process upload attribute
def PostProcessAttributesUpload(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 


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
   # get touch sensing operator
   tsOperator = Operator.GetTouchSensingOperator()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribGetter == None) or (eventOperator == None) or (refTpElement == None) or (tsOperator == None) or (controller == None):
      logging.LogError("TouchSensingEvent Python, zero pointer initialization PostCompute")


   # SEARCH MOTION TYPE INDEX (0 = PTP; 1 = LIN)
   searchMoTypeIndex = 0
   try:
      searchMoTypeFirstTpeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE_FIRST_TPE)
      searchMoTypeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE)
      searchDirection = attribGetter.GetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION)
      touchStartDistance = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_LENGTH)
      touchEndDistance = attribGetter.GetDouble(AW_TOUCHSENS_OVERTRAVEL_LENGTH)
      touchSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_SPEED)
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
   # approach - start point - collision point - end point - start point
   # DOWNLOAD
   # start point: one time, not twice
   # collision point: 
   if (tsRefPointMatrix or tsStartPointMatrix or tsEndPointMatrix or tsCollisionPointMatrix):
      #if (tsStartPointMatrix):
      #   if searchMoTypeFirstTpeIndex == LIN:
      #      tpElementStartApp = Operator.MoveLin(tsStartPointMatrix)
      #   else:
      #      tpElementStartApp = Operator.MovePTP(tsStartPointMatrix)
      #else:
      #   logging.LogError("could not calculate start point matrix for touch point event")
      if (tsCollisionPointMatrix):
         # special CLOOS handling: Colli point always LIN
         tpElementCollision = Operator.MoveLin(tsCollisionPointMatrix)
         
      else:
         logging.LogError("could not calculate collision point matrix for touch point event")
      #if (tsEndPointMatrix):
      #   # special CLOOS handling: End point always LIN
      #   tpElementEnd = Operator.MoveLin(tsEndPointMatrix)         
      #else:
      #   logging.LogError("could not calculate end point matrix for touch point event")
      ## 
      #if (tsStartPointMatrix):
      #   if searchMoTypeIndex == LIN:
      #      tpElementStartRet = Operator.MoveLin(tsStartPointMatrix)
      #   else: 
      #      tpElementStartRet = Operator.MovePTP(tsStartPointMatrix)
      #else:
      #   logging.LogError("could not calculate start point matrix for touch point event")

   else:
      # Alternative Actions
      downUnder = Operator.GetReferenceTpElementInitialMatrix()
      if searchMoTypeIndex == LIN:
         Operator.MoveLin(downUnder)
      else:
         Operator.MovePTP(downUnder)

   eventOperator.AddEvent(TOUCH_POINT_START_APP_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
   eventOperator.AddEvent(TOUCH_POINT_COLLISION_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
   eventOperator.AddEvent(TOUCH_POINT_END_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
   eventOperator.AddEvent(TOUCH_POINT_START_RET_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)

   # Set Touch Sensing Speed
   touchSpeedEvent=eventOperator.AddSpeed(tpElementCollision,TPINSERTPOS_INSERTBEFORE)
   touchSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
   touchSpeedEvent.SetSpeed(touchSpeed)


   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)


# -------------------------------------------------------------------------------------------
# event post on attribute change 
def PostOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # changedAttrib = Operator.GetChangedAttribute()  
   # attribName = changedAttrib.GetName()

   # YOUR CODE

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)