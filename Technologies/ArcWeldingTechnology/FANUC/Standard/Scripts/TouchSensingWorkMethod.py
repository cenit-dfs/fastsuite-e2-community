# -------------------------------------------------------------------------------------------
# Name: TouchSensingWorkMethod
# Description: Vendor specific Fanuc arc welding technology
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 2.0
#        Changed by: Hohmann
#        Date: 02/06/24
#        Added touch sensing in surface direction (E2 search)
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import sys
sys.dont_write_bytecode = True

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "TouchSensingWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) WM initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) WM initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) WM initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) WM initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) WM initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) WM initialization of event rules ended."

DEBUG_SYNC_PG_ATTRIB_START = "(Debug-Technology) WM synchronization of process geometry started."
DEBUG_SYNC_PG_ATTRIB_END = "(Debug-Technology) WM synchronization of process geometry ended."

DEBUG_POST_PROCESS_OPERATION_ATTRIB_START = "(Debug-Technology) WM post process operation attributes stared."
DEBUG_POST_PROCESS_OPERATION_ATTRIB_END = "(Debug-Technology) WM post process operation attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) prev on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) WM Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) WM Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) WM Could not get attribute."
ERROR_SET_ATTRIB = "(Error) WM Could not set attribute."


AW_MOTION_TYPE = "OperationGroupMotionType"
AW_TOUCHSENS_TOUCH_DIRECTION = "TSTouchDirection" # AlongFaceToNormal = 0, AlongBaseFrame = 1
AW_TOUCHSENS_TOUCH_METHOD = "TSTouchMethod" # Nozzle = 0, Wire = 1
AW_TOUCHSENS_WIRE_CHECK = "TSWireCheck"
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TOUCHSENS_CONNECTION_TYPE = "TSConnectionType"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"
AW_TOUCHSENS_FANUC_TOUCHREGISTER="TSTouchOffsetRegister"

WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"

# work method Attributes
AW_TOUCHSENS_FANUC_SEARCHSCHEDULE="TSTouchSchedule"
AW_TOUCHSENS_FANUC_TEMPREGISTER="TSTouchOffsetTempRegister"
AW_TOUCHSENS_CYCLE_TYPE = "TSCycleType"
AW_TOUCHSENS_CYCLE_LITERALS = ["Base frame direction", "Normal to surface"]
AW_TOUCHSENS_SENSING_SPEED = "SensingSpeed"
AW_TOUCHSENS_APPR_RETR_SPEED="TouchApprRetrSpeed"
AW_TOUCHSENS_APPR_RETR_FLYBY="TouchApprFlyBy"
# number of the position register where touch sensing starts
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
# touch sensing digital output
AW_TOUCHSENS_DIGITAL_INPUT = "TSDigitalInput"
# touch sensing sensor output 
AW_TOUCHSENS_DIGITAL_OUTPUT = "TSDigitalOutput"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY = "Tooltip" + AW_MOTION_TYPE_FIRST_TPE
AW_MOTION_TYPE_FIRST_TPE_LITERALS = ["PTP", "LIN"]


# -------------------------------------------------------------------------------------------
# Work method post init attributes
def PostWmInitAttributes(Operator: CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
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

   try:
      # set motion type default PTP = 0; LIN = 1
      attribSetter.SetEnumIndex(AW_MOTION_TYPE, 1)
      attrib = attribCreator.AddEnum(AW_MOTION_TYPE_FIRST_TPE, AW_MOTION_TYPE_FIRST_TPE_LITERALS, AW_MOTION_TYPE_FIRST_TPE_LITERALS[0], OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_MOTION_TYPE_FIRST_TPE)
      attrib.SetTooltipKey(AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY)
      attrib.SetReComputeEnterState(ENTERSTATE_COMPLETE)
      # use wire only and make the attribute none user user attribute
      attribSetter.SetEnumIndex(AW_TOUCHSENS_TOUCH_METHOD, 1)
      touchMethod = attribGetter.GetAttributeByName(AW_TOUCHSENS_TOUCH_METHOD)
      touchMethod.SetOlpProperty(OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE)
      # enable visibly for wire check
      wireCheck = attribGetter.GetAttributeByName(AW_TOUCHSENS_WIRE_CHECK)
      wireCheck.SetVisibility(True)
      # set touch direction to base frame
      attribSetter.SetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION, 1)
      attribTouchDirection = attribGetter.GetAttributeByName(AW_TOUCHSENS_TOUCH_DIRECTION)
      attribTouchDirection.SetOlpProperty(USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE)
      attribTouchDirection.SetVisibility(True)
      # disable over travel length because end point is not used for Fanuc
      attribTouchEndDistance = attribGetter.GetAttributeByName(AW_TOUCHSENS_OVERTRAVEL_LENGTH)
      # attribTouchEndDistance.SetOlpProperty(OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE)
      # add workmethod name to operation
      attribCreator.AddString(WORKMETHOD_NAME, "TouchSensingWorkMethod", PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE, WORKMETHOD_NAME)
      # add Attribute for FANUC Search Schedule, temporary Register and Touch Register
      attribCreator.AddInteger(AW_TOUCHSENS_FANUC_SEARCHSCHEDULE, 8,1,99, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_FANUC_SEARCHSCHEDULE)
      attribCreator.AddInteger(AW_TOUCHSENS_FANUC_TEMPREGISTER, 99,1,99, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_FANUC_TEMPREGISTER)

      # Choose between surface-normal E2 cycle or standard Fanuc search method
      attribCreator.AddEnum(AW_TOUCHSENS_CYCLE_TYPE, AW_TOUCHSENS_CYCLE_LITERALS, AW_TOUCHSENS_CYCLE_LITERALS[1], PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_TOUCHSENS_CYCLE_TYPE)
      # new attributes for touch sensing using dedicated macro. To enable visibility, set 
      att = attribCreator.AddInteger(AW_TOUCHSENS_DIGITAL_INPUT, 10, 1, 9999, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_DIGITAL_INPUT)
      att.SetVisibility(False)
      att = attribCreator.AddInteger(AW_TOUCHSENS_DIGITAL_OUTPUT, 13, 1, 9999, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_DIGITAL_OUTPUT)
      att.SetVisibility(False)
      attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_SPEED, 0.200,0,1,0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_SPEED)
      attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_FLYBY, 0.025,0,0.1,0.005, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_FLYBY)
   except:
      logging.LogError("Cannot set FANUC vendor specific attribute on touch sensing work method InitAttributes()!")

   CycleTypeInit(Operator)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Work method post init events
def PostWmInitEvents(Operator: CENPyOlpWM_EventInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   # add 
   Operator.RegisterPyTechnologyEvent('TouchPointStartAppEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointCollisionEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointEndEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointStartRetEvent.py')

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)


# -------------------------------------------------------------------------------------------
# Work method post sync process geometry attributes
def PostWmSyncPgAttributes(Operator: CENPyOlpWM_SyncPgAttribOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_START)

   attribGetter = Operator.GetAttribGetter()

   posRegStartRegister = attribGetter.GetAttributeByName(AW_GLOBAL_TOUCH_COUNTER)
   if posRegStartRegister != None:
      posRegStartRegister.SetVisibility(False)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Work method post on attribute change 
def PostWmOnAttribChanged(Operator: CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   attribName = changedAttrib.GetName()

   # show/hide ConnectionType Attribute due to CalibrationMethod
   if (attribName == AW_SEAM_CALIBRATION_METHOD):
      calibrationMethod = attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
      attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECTION_TYPE)
      attTSCycleType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CYCLE_TYPE)

      if (calibrationMethod == AW_SEAMSEARCHING) or (calibrationMethod == AW_TOUCHSENSE_BY_POINT) or (calibrationMethod == AW_TOUCHSENSE_AUTOMATIC):
         attConnectionType.SetVisibility(True)
         attTSCycleType.SetVisibility(True)
      else:
         attConnectionType.SetVisibility(False)
         attTSCycleType.SetVisibility(False)

   elif (attribName == AW_TOUCHSENS_CYCLE_TYPE):
      CycleTypeInit(Operator)


def CycleTypeInit(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   cycleTypeIndex = attribGetter.GetEnumIndex(AW_TOUCHSENS_CYCLE_TYPE)

   E2TouchDigitalInput = attribGetter.GetAttributeByName(AW_TOUCHSENS_DIGITAL_INPUT)
   E2TouchDigitalOutput = attribGetter.GetAttributeByName(AW_TOUCHSENS_DIGITAL_OUTPUT)
   E2TouchPosRegStartNumber = attribGetter.GetAttributeByName(AW_GLOBAL_TOUCH_COUNTER)
   FanucTouchSearchSchedule = attribGetter.GetAttributeByName(AW_TOUCHSENS_FANUC_SEARCHSCHEDULE)
   FanucTouchTempRegister = attribGetter.GetAttributeByName(AW_TOUCHSENS_FANUC_TEMPREGISTER)
   FanucTouchRegister = attribGetter.GetAttributeByName(AW_TOUCHSENS_FANUC_TOUCHREGISTER)
   # enable connection type 
   attConnectionType = attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECTION_TYPE)
   attTouchSensingSpeed = attribGetter.GetAttributeByName(AW_TOUCHSENS_SENSING_SPEED)
   
   # Touch sensing in base frame direction
   if cycleTypeIndex == 0:
      E2TouchDigitalInput.SetVisibility(False)
      E2TouchDigitalOutput.SetVisibility(False)
      E2TouchPosRegStartNumber.SetVisibility(False)
      FanucTouchSearchSchedule.SetVisibility(True)
      FanucTouchTempRegister.SetVisibility(True)
      FanucTouchRegister.SetVisibility(True)
      attribSetter.SetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION, 1)
      attConnectionType.SetValue("OperationConnect")
      attConnectionType.SetVisibility(False)
      attTouchSensingSpeed.SetOlpProperty(USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE)
   # Touch sensing normal to surface
   else:
      E2TouchDigitalInput.SetVisibility(True)
      E2TouchDigitalOutput.SetVisibility(True)
      E2TouchPosRegStartNumber.SetVisibility(True)
      FanucTouchSearchSchedule.SetVisibility(False)
      FanucTouchTempRegister.SetVisibility(False)
      FanucTouchRegister.SetVisibility(False)
      attribSetter.SetEnumIndex(AW_TOUCHSENS_TOUCH_DIRECTION, 0)
      attConnectionType.SetVisibility(True)
      attTouchSensingSpeed.SetOlpProperty(USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE)


   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)