# -------------------------------------------------------------------------------------------
# Name: TouchSensingEvent
# Description: adding touch points with respect to Standard basic.
# Debug info: E2@localhost:5254
# Author: Hohmann
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
import math
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
AW_SENSOR_TOOL_TYPE = "SensorToolType"
AW_MOTION_TYPE = "OperationGroupMotionType"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_TOUCHSENS_TOUCH_DIRECTION = "TSTouchDirection" # AlongFaceToNormal = 0, AlongBaseFrame = 1
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TOUCHSENS_SENSING_SPEED="SensingSpeed"
AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN ="TSSpeedFromCycleLin"
AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP='TSSpeedFromCyclePtp'

#Laser Scanner attribs
AW_LASER_FOV_X = "LaserFovX"
AW_LASER_FOV_Y = "LaserFovY"
AW_LASER_FOV_Z = "LaserFovZ"
AW_LASER_FOV_RX = "LaserFovA"
AW_LASER_FOV_RY = "LaserFovB"
AW_LASER_FOV_RZ = "LaserFovC"

# Events to indicate the different touch points for download only
TOUCH_POINT_START_APP_EVENT_UUID = "99b470ac-d51c-11ec-9d64-0242ac120002"
TOUCH_POINT_COLLISION_EVENT_UUID = "8ab88d40-d51c-11ec-9d64-0242ac120002"
TOUCH_POINT_END_EVENT_UUID = "9273cf0e-d51c-11ec-9d64-0242ac120002"
TOUCH_POINT_START_RET_EVENT_UUID = "a7f1340c-d51c-11ec-9d64-0242ac120002"

SEAM_FIND_TEACH_EVENT_UUID       = "FB052ADC-BA26-4BC6-A952-BDF108ABC84F"

SEAM_FINDING_SCAN_EVENT_UUID = "23d47a8b-11d4-4064-b558-d13f45df34aa"
SEAM_FINDING_REF_EVENT_UUID  = "89B68E1A-654A-428A-BD9C-375FCDDDD334"
SEAM_FINDING_EVENT_UUID      = "FB052ADC-BA26-4BC6-A952-BDF10884484F"
LINELASERPOV_EVENT_UUID      = "0D196218-D99F-461F-8C41-06278F654123"

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
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging: create attributes
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

#    # YOUR CODE

#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 

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
      logging.LogError("TouchSensingEvent Python, zero pointer initialization PostCompute")


   # SEARCH MOTION TYPE INDEX (0 = PTP; 1 = LIN)
   searchMoTypeIndex = 0
   try:
      # sensorToolType literals: 0 = 'Touch Sensor', 1 = 'Point Laser', 2 = 'Line Laser'
      sensorToolType = attribGetter.GetAttributeEnumByName(AW_SENSOR_TOOL_TYPE).GetValue()
      sensorToolTypeIndex = attribGetter.GetEnumIndex(AW_SENSOR_TOOL_TYPE)
      searchMoTypeFirstTpeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE_FIRST_TPE)
      searchMoTypeIndex = attribGetter.GetEnumIndex(AW_MOTION_TYPE)
      searchDirection = attribGetter.GetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION)
      touchStartDistance = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_LENGTH)
      touchEndDistance = attribGetter.GetDouble(AW_TOUCHSENS_OVERTRAVEL_LENGTH)
      touchSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_SPEED)
      linearSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
      ptpSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_PTP)
      afterCycleSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
      afterCycleSpeed = attribGetter.GetDouble(AW_TOUCHSENS_SPEED_FROM_CYCLE_LIN)
      
      LX1 = attribGetter.GetDouble(AW_LASER_FOV_X)
      LY1 = -attribGetter.GetDouble(AW_LASER_FOV_Y)
      LZ1 = attribGetter.GetDouble(AW_LASER_FOV_Z)
      LRX1 = attribGetter.GetDouble(AW_LASER_FOV_RX)
      LRY1 = -attribGetter.GetDouble(AW_LASER_FOV_RY)
      LRZ1 = attribGetter.GetDouble(AW_LASER_FOV_RZ)
   except:
      logging.LogError('Cannot get the attribute AW_MOTION_TYPE!')
   
   # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   if sensorToolTypeIndex == 2:
      return
   # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

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

   if (tsRefPointMatrix or tsStartPointMatrix or tsEndPointMatrix or tsCollisionPointMatrix):
      # -------------------------------------------------------------------
      # to StartPoint
      usedMatrix = tsStartPointMatrix
      if usedMatrix:
         # tpElementStartApp = Operator.MovePTP(tsStartPointMatrix)
         if searchMoTypeFirstTpeIndex == LIN:
            tpElementStartApp = Operator.MoveLin(usedMatrix)
         else:
            tpElementStartApp = Operator.MovePTP(usedMatrix)
      # -------------------------------------------------------------------
      # use RefPoint for Line Laser instead of CollisionPoint
      usedMatrix = tsCollisionPointMatrix

      logging.LogInfo('-----------------------------------------------------------')
      logging.LogInfo('------------TOUCH_SENSING_EVENT::PostCompute()---------------')
      pos = usedMatrix.GetPosition().GetXYZ()
      rot = usedMatrix.GetRotation()
      xyz, deg = convert_xyz_rot(pos, rot)
      logging.LogInfo('------  RefPointMatrix : XYZ=' + str(xyz) + '  ROT=' + str(deg))
      logging.LogInfo('-----------------------------------------------------------')

      if usedMatrix:
         if searchMoTypeIndex == LIN:
            tpElementCollision = Operator.MoveLin(usedMatrix)
         else:
            tpElementCollision = Operator.MovePTP(usedMatrix)
      # -------------------------------------------------------------------
      # to EndPoint
      usedMatrix = tsStartPointMatrix
      if usedMatrix:
         if searchMoTypeIndex == LIN:
            tpElementStartRet = Operator.MoveLin(usedMatrix)
         else: 
            tpElementStartRet = Operator.MovePTP(usedMatrix)
      # -------------------------------------------------------------------

      # Set further Events
      eventOperator.AddEvent(TOUCH_POINT_START_APP_EVENT_UUID, tpElementStartApp, TPINSERTPOS_INSERTBEFORE)
      eventOperator.AddEvent(TOUCH_POINT_COLLISION_EVENT_UUID, tpElementCollision, TPINSERTPOS_INSERTBEFORE)
      eventOperator.AddEvent(TOUCH_POINT_START_RET_EVENT_UUID, tpElementStartRet, TPINSERTPOS_INSERTBEFORE)

      eventOperator.AddAccuracyEvent(tpElementCollision,TPINSERTPOS_INSERTBEFORE).SetCriteria(0)
      SfSpeedEvent=eventOperator.AddSpeed(tpElementCollision,TPINSERTPOS_INSERTBEFORE)
      if SfSpeedEvent:
         if searchMoTypeFirstTpeIndex == LIN:
            SfSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
            SfSpeedEvent.SetSpeed(linearSpeed)
         else:
            SfSpeedEvent.SetPathType(EVENTPATHTYPE_POINTTOPOINT)
            SfSpeedEvent.SetUnit(ATTRIB_PERCENT)
            SfSpeedEvent.SetSpeed(ptpSpeed)

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

# -------------------------------------------------------------------------------------------
def SetFOVMatrix(inMatrix,LX,LY,LZ,LRX,LRY,LRZ ):
   inMatrix.Translate(LX,LY,LZ,True)
   inMatrix.RotateX(LRX)
   inMatrix.RotateY(LRY)
   inMatrix.RotateZ(LRZ)
   return inMatrix

def convert_xyz_rot(xyz, rot):
    # Convert meters to millimeters and round to 4 digits
    xyz_mm = [round(value * 1000, 4) for value in xyz]
    # Convert radians to degrees and round to 4 digits
    rot_deg = [round(math.degrees(value), 4) for value in rot]
    # Combine both lists
    return xyz_mm, rot_deg
# -------------------------------------------------------------------------------------------
