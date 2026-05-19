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
FILE_NAME = "SeamFindTeachEvent.py: "

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
AW_TOUCHSENS_LINEAR_SPEED='TSSpeedFromCycleLin'
AW_TOUCHSENS_PTP_SPEED='TSSpeedFromCyclePtp'
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
      linearSpeed = attribGetter.GetDouble(AW_TOUCHSENS_LINEAR_SPEED)
      ptpSpeed = attribGetter.GetDouble(AW_TOUCHSENS_PTP_SPEED)
      
      LX1 = attribGetter.GetDouble(AW_LASER_FOV_X)
      LY1 = -attribGetter.GetDouble(AW_LASER_FOV_Y)
      LZ1 = attribGetter.GetDouble(AW_LASER_FOV_Z)
      LRX1 = attribGetter.GetDouble(AW_LASER_FOV_RX)
      LRY1 = -attribGetter.GetDouble(AW_LASER_FOV_RY)
      LRZ1 = attribGetter.GetDouble(AW_LASER_FOV_RZ)
   except:
      logging.LogError('Cannot get the attribute AW_MOTION_TYPE!')
   
   # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   if sensorToolTypeIndex != 2:
      return
   # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

   tsRefPointMatrix = Operator.GetRefTpElement().GetGlobalTransformedMatrixUnaligned()

   if tsRefPointMatrix:
      # -------------------------------------------------------------------
      # to StartPoint
      # usedMatrix = SetFOVMatrix(tsStartPointMatrix,LX1,LY1,LZ1,LRX1,LRY1,LRZ1)
      usedMatrix = SetFOVMatrix(tsRefPointMatrix,LX1,LY1,LZ1,LRX1,LRY1,LRZ1)

      if usedMatrix:
         if searchMoTypeFirstTpeIndex == LIN:
            tpElementSF = Operator.MoveLin(usedMatrix)
         else:
            tpElementSF = Operator.MovePTP(usedMatrix)

      # Set further Events
      # case LINE LASER
      eventOperator.AddEvent(SEAM_FINDING_SCAN_EVENT_UUID, tpElementSF, TPINSERTPOS_INSERTBEFORE)

      SfAccuracyEvent = eventOperator.AddAccuracyEvent(tpElementSF,TPINSERTPOS_INSERTBEFORE)
      SfSpeedEvent=eventOperator.AddSpeed(tpElementSF,TPINSERTPOS_INSERTBEFORE)
      SfDwellEvent=eventOperator.AddDwellEvent(tpElementSF,TPINSERTPOS_INSERTAFTER)
      SfDwellEvent.SetDwellTime(0.5)
      if SfSpeedEvent:
         if searchMoTypeFirstTpeIndex == LIN:
            SfSpeedEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
            SfSpeedEvent.SetSpeed(linearSpeed)
            SfAccuracyEvent.SetPathType(EVENTPATHTYPE_CONTOUR)
            SfAccuracyEvent.SetCriteria(ACCURACY_OFF)
         else:
            SfSpeedEvent.SetPathType(EVENTPATHTYPE_POINTTOPOINT)
            SfSpeedEvent.SetUnit(ATTRIB_PERCENT)
            SfSpeedEvent.SetSpeed(ptpSpeed)
            SfAccuracyEvent.SetPathType(EVENTPATHTYPE_POINTTOPOINT)
            SfAccuracyEvent.SetCriteria(ACCURACY_OFF)

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

# -------------------------------------------------------------------------------------------
def SetFOVMatrix(inMatrix,LX,LY,LZ,LRX,LRY,LRZ ):
   inMatrix.Translate(LX,LY,LZ,True)
   inMatrix.RotateZ(LRZ)
   inMatrix.RotateY(LRY)
   inMatrix.RotateX(LRX)
   return inMatrix
# -------------------------------------------------------------------------------------------

def GetEventName():
   return "SeamFindTeachEvent"

def GetEventUuId():
   return "FB052ADC-BA26-4BC6-A952-BDF108ABC84F"

def GetIconName():
   return "ArcWeldCalibration_SeamFinding"
   
def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
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
   return CYCLEROTATION_ROTPATHTOOL
   
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTPATHTOOL
   
def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_TEACHABLE

def GetCycleDownloadBehavior():
   return CYCLEDOWNLOAD_NORMALREFPOINTANDPROCESSPOINTS

def IsMachiningCycle():
   return 1

def GetGroupName():
   return ""
   
def IsEnabled():
   return True
