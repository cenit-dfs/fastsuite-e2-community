# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Extend standard ArcOnEvent for KUKA KRC4/5
# Debug info: E2@localhost:5254
# Author: CENIT
# Changelog:
#     Version: 1.0
#        Changed by: Berauer
#        Date: 2024-07-25
#
# -------------------------------------------------------------------------------------------

# Import libraries

from centypes import *
from cenpylib import *
import inspect, os, json
import sys
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# Global definitions
# -------------------------------------------------------------------------------------------
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
# -------------------------------------------------------------------------------------------

EVENT_FILE_NAME = "ArcOnEvent.py"
EVENT_NAME = "ArcOnEvent"
EVENT_ICON = "ArcOn"
EVENT_ATTRIBUTE_TYPE = USER_ATTRIBUTE | PROCESS_ATTRIBUTE

#ArcTech Globals
KUKA_ARCTECH_ADV = "KukaArcTechAdv"
KUKA_WEAVE_TYPE = "KukaWeaveType"
#ArcOn Event Definition
KUKA_ARC_SWITCH = "KukaArcSwitch"
KUKA_IGNITION_PROGRAM_NUMBER = "KukaIgnitionProgNumber"
KUKA_IGNITION_PARAM_SET = "KukaIgnitionParmSet"
KUKA_PRE_FLOW_TIME = "KukaPreflowTime"
KUKA_ON_THE_FLY_ACTIVE = "KukaOnTheFlyActive"
KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME = "KukaOnTheFlyGasPreflowTime"
KUKA_WAIT_TIME_AFTER_IGNITION = "KukaWaitTimeAfterIgnition"
KUKA_WELD_JOB_NUMBER = "KukaProgNumber"
KUKA_WELD_PARAM_SET = "KukaWeldParmSet"
KUKA_ROBOT_VELOCITY_1 = "KukaRobotVelocity1"
KUKA_WEAVE_PATTERN = "KukaWeavePattern"
# KUKA_WEAVE_PATTERN_LIST = ["None","Spiral","Trapecoid","Triangle","UnsymetricTrapecoid","OnSeam"]
KUKA_WEAVE_PATTERN_LIST = ["None","Spiral","Trapecoid","Triangle","UnsymetricTrapecoid","Spiral", "Double8", "OnSeam", "EdgeBottom", "EdgeTop", "UserDefined1", "UserDefined2"]
KUKA_WEAVE_LENGTH = "KukaWeaveLength"
KUKA_WEAVE_FREQUENCY = "KukaWeaveFrequency"
KUKA_WEAVE_DEFLECTION = "KukaWeaveDeflection"
KUKA_WEAVE_ANGLE = "KukaWeaveAngle"
#ArcSense Definition
KUKA_ARCSENSE = "KukaArcSense"
KUKA_ARCSENSE_PATTERN = "KukaArcSensePattern"
KUKA_ARCSENSE_PATTERN_LIST = ["None","Trapecoid","Triangle"]
KUKA_ARCSENSE_LATCTRLGAIN = "KukaArcSenseLatCtrlGain"
KUKA_ARCSENSE_HEIGHTCTRL = "KukaArcSenseHeightCtrl"
KUKA_ARCSENSE_LATBIAS = "KukaArcSenseLatBias"
KUKA_ARCSENSE_MAXCORR = "KukaArcSenseMaxCorr"
KUKA_ARCSENSE_FINDCENTER = "KukaArcSenseFindCenter"
KUKA_ARCSENSE_ACTIVDELAY = "KukaArcSenseActivDelay"
#ArcOn Technology Definition
KUKA_IGNITION_PROGRAM_NUMBER_DEFINE = "KukaIgnitionProgNumberDefine"
KUKA_IGNITION_PARAM_SET_DEFINE = "KukaIgnitionParmSetDefine"
KUKA_PRE_FLOW_TIME_DEFINE = "KukaPreflowTimeDefine"
KUKA_ON_THE_FLY_ACTIVE_DEFINE = "KukaOnTheFlyActiveDefine"
KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE = "KukaOnTheFlyGasPreflowTimeDefine"
KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE = "KukaWaitTimeAfterIgnitionDefine"
KUKA_WELD_JOB_NUMBER_DEFINE = "KukaProgNumberDefine"
KUKA_WELD_PARAM_SET_DEFINE = "KukaWeldParmSetDefine"
KUKA_ROBOT_VELOCITY_1_DEFINE = "KukaRobotVelocity1Define"
KUKA_WEAVE_PATTERN_DEFINE = "KukaWeavePatternDefine"
KUKA_WEAVE_LENGTH_DEFINE = "KukaWeaveLengthDefine"
KUKA_WEAVE_FREQUENCY_DEFINE = "KukaWeaveFrequencyDefine"
KUKA_WEAVE_DEFLECTION_DEFINE = "KukaWeaveDeflectionDefine"
KUKA_WEAVE_ANGLE_DEFINE = "KukaWeaveAngleDefine"
#ArcSense Definition
KUKA_ARCSENSE_DEFINE = "KukaArcSenseDefine"
KUKA_ARCSENSE_PATTERN_DEFINE = "KukaArcSensePatternDefine"
KUKA_ARCSENSE_LATCTRLGAIN_DEFINE = "KukaArcSenseLatCtrlGainDefine"
KUKA_ARCSENSE_HEIGHTCTRL_DEFINE = "KukaArcSenseHeightCtrlDefine"
KUKA_ARCSENSE_LATBIAS_DEFINE = "KukaArcSenseLatBiasDefine"
KUKA_ARCSENSE_MAXCORR_DEFINE = "KukaArcSenseMaxCorrDefine"
KUKA_ARCSENSE_FINDCENTER_DEFINE = "KukaArcSenseFindCenterDefine"
KUKA_ARCSENSE_ACTIVDELAY_DEFINE = "KukaArcSenseActivDelayDefine"
# ArcOn JSON attributes
KUKA_ARCIGNITION_JSON = "KukaArcIgnitionJson"
KUKA_ARCON_JSON = "KukaArcOnJson"
KUKA_ARCSENSE_JSON = "KukaArcSenseJson"

MAX_INTEGER = 2147483647

def GetEventName():
   return EVENT_NAME

def GetIconName():
   return EVENT_ICON

def GetGroupName():
   return "Kuka Arc Weld"

def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Hide unused default event attributes ProgNumber
   w0 = attribGetter.GetAttributeByName("ProgNumber").SetVisibility(False)
   w1 = attribGetter.GetAttributeByName("WeaveFrequenz").SetVisibility(False)
   w2 = attribGetter.GetAttributeByName("WeaveWidth").SetVisibility(False)
   w3 = attribGetter.GetAttributeByName("WeaveTime1").SetVisibility(False)
   w4 = attribGetter.GetAttributeByName("WeaveTime2").SetVisibility(False)
   w5 = attribGetter.GetAttributeByName("WeaveOnOff").SetVisibility(False)
   # Create KUKA attributes
   attribBool = attribCreator.AddBool(KUKA_ARC_SWITCH,True,EVENT_ATTRIBUTE_TYPE,KUKA_ARC_SWITCH)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(KUKA_IGNITION_PROGRAM_NUMBER,1,0,MAX_INTEGER,EVENT_ATTRIBUTE_TYPE,KUKA_IGNITION_PROGRAM_NUMBER)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_IGNITION_PARAM_SET,'Set1', EVENT_ATTRIBUTE_TYPE,KUKA_IGNITION_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_ON_THE_FLY_ACTIVE,False,EVENT_ATTRIBUTE_TYPE,KUKA_ON_THE_FLY_ACTIVE)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME,0.0,0,100,1,EVENT_ATTRIBUTE_TYPE,ATTRIB_TIME,KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_PRE_FLOW_TIME,0.0,0,100,1,EVENT_ATTRIBUTE_TYPE,ATTRIB_TIME,KUKA_PRE_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WAIT_TIME_AFTER_IGNITION,0.0,0,100,0.1,EVENT_ATTRIBUTE_TYPE,ATTRIB_TIME,KUKA_WAIT_TIME_AFTER_IGNITION)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribInteger = attribCreator.AddInteger(KUKA_WELD_JOB_NUMBER,1,0, MAX_INTEGER, EVENT_ATTRIBUTE_TYPE,KUKA_WELD_JOB_NUMBER)
   attribInteger.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_WELD_PARAM_SET,'Set1', EVENT_ATTRIBUTE_TYPE,KUKA_WELD_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ROBOT_VELOCITY_1,0.02,0,100,0.1,EVENT_ATTRIBUTE_TYPE,ATTRIB_SPEED,KUKA_ROBOT_VELOCITY_1)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(KUKA_WEAVE_PATTERN,KUKA_WEAVE_PATTERN_LIST,KUKA_WEAVE_PATTERN_LIST[0],EVENT_ATTRIBUTE_TYPE,KUKA_WEAVE_PATTERN)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribIntENM = attribCreator.AddEnum(KUKA_ARCSENSE_PATTERN,KUKA_ARCSENSE_PATTERN_LIST,KUKA_ARCSENSE_PATTERN_LIST[0],EVENT_ATTRIBUTE_TYPE,KUKA_ARCSENSE_PATTERN)
   attribIntENM.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_LENGTH,0.003,-0.1,0.1,0.001,EVENT_ATTRIBUTE_TYPE,ATTRIB_LENGTH, KUKA_WEAVE_LENGTH)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_FREQUENCY,1.0,0,100,0.1,EVENT_ATTRIBUTE_TYPE,ATTRIB_FREQUENCY, KUKA_WEAVE_FREQUENCY)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_DEFLECTION,0.0025,0,0.1,0.001,EVENT_ATTRIBUTE_TYPE,ATTRIB_LENGTH, KUKA_WEAVE_DEFLECTION)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_WEAVE_ANGLE,0.0,-90,90,1,EVENT_ATTRIBUTE_TYPE,ATTRIB_ANGLE, KUKA_WEAVE_ANGLE)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   #ArcSense Definition
   attribBool = attribCreator.AddBool(KUKA_ARCSENSE,False,EVENT_ATTRIBUTE_TYPE,KUKA_ARCSENSE)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATCTRLGAIN,50.0,0.0,100.0,1,EVENT_ATTRIBUTE_TYPE, ATTRIB_PERCENT, KUKA_ARCSENSE_LATCTRLGAIN)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_HEIGHTCTRL,50.0,0.0,100.0,1,EVENT_ATTRIBUTE_TYPE, ATTRIB_PERCENT, KUKA_ARCSENSE_HEIGHTCTRL)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_LATBIAS,50.0,-100,100.0,1,EVENT_ATTRIBUTE_TYPE, ATTRIB_PERCENT, KUKA_ARCSENSE_LATBIAS)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_MAXCORR,0.025,0.001,0.3,0.001,EVENT_ATTRIBUTE_TYPE, ATTRIB_LENGTH, KUKA_ARCSENSE_MAXCORR)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribBool = attribCreator.AddBool(KUKA_ARCSENSE_FINDCENTER,False,EVENT_ATTRIBUTE_TYPE,KUKA_ARCSENSE_FINDCENTER)
   attribBool.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_ARCSENSE_ACTIVDELAY,0.0,0.0,10.0,1,EVENT_ATTRIBUTE_TYPE, ATTRIB_TIME, KUKA_ARCSENSE_ACTIVDELAY)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   arcIgnJson = attribCreator.AddString(KUKA_ARCIGNITION_JSON,'', EVENT_ATTRIBUTE_TYPE, KUKA_ARCIGNITION_JSON)
   arcIgnJson.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcIgnJson.SetVisibility(False)
   arcOnJson = attribCreator.AddString(KUKA_ARCON_JSON,'', EVENT_ATTRIBUTE_TYPE, KUKA_ARCON_JSON)
   arcOnJson.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcOnJson.SetVisibility(False)
   arcSense = attribCreator.AddString(KUKA_ARCSENSE_JSON,'', EVENT_ATTRIBUTE_TYPE, KUKA_ARCSENSE_JSON)
   arcSense.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcSense.SetVisibility(False)

# post process attribute
def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   try:
      # get attribute setter
      attribSetter = Operator.GetAttribSetter()
      # get attribute getter
      attribGetter = Operator.GetAttribGetter()
   except:
      logging.LogError(EVENT_FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

   # ArcOnVisualize(Operator)
   # YOUR CODE
   if (Operator.IsEventCreatedAutomatically() == True):
      ruleEvent = True
      attribSetter.SetBool(KUKA_ARC_SWITCH, False)
      attribSetter.SetInteger(KUKA_IGNITION_PROGRAM_NUMBER, attribGetter.GetInteger(KUKA_IGNITION_PROGRAM_NUMBER_DEFINE))
      attribSetter.SetString(KUKA_IGNITION_PARAM_SET, attribGetter.GetString(KUKA_IGNITION_PARAM_SET_DEFINE))
      attribSetter.SetString(KUKA_WELD_PARAM_SET, attribGetter.GetString(KUKA_WELD_PARAM_SET_DEFINE))
      attribSetter.SetDouble(KUKA_PRE_FLOW_TIME, attribGetter.GetDouble(KUKA_PRE_FLOW_TIME_DEFINE))
      attribSetter.SetBool(KUKA_ON_THE_FLY_ACTIVE, attribGetter.GetBool(KUKA_ON_THE_FLY_ACTIVE_DEFINE))
      attribSetter.SetDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME, attribGetter.GetDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME_DEFINE))
      attribSetter.SetDouble(KUKA_WAIT_TIME_AFTER_IGNITION, attribGetter.GetDouble(KUKA_WAIT_TIME_AFTER_IGNITION_DEFINE))
      attribSetter.SetInteger(KUKA_WELD_JOB_NUMBER, attribGetter.GetInteger(KUKA_WELD_JOB_NUMBER_DEFINE))
      attribSetter.SetDouble(KUKA_ROBOT_VELOCITY_1, attribGetter.GetDouble(KUKA_ROBOT_VELOCITY_1_DEFINE))
      attribSetter.SetEnumIndex(KUKA_WEAVE_PATTERN, attribGetter.GetEnumIndex(KUKA_WEAVE_PATTERN_DEFINE))
      attribSetter.SetDouble(KUKA_WEAVE_LENGTH, attribGetter.GetDouble(KUKA_WEAVE_LENGTH_DEFINE))
      attribSetter.SetDouble(KUKA_WEAVE_FREQUENCY, attribGetter.GetDouble(KUKA_WEAVE_FREQUENCY_DEFINE))
      attribSetter.SetDouble(KUKA_WEAVE_DEFLECTION, attribGetter.GetDouble(KUKA_WEAVE_DEFLECTION_DEFINE))
      attribSetter.SetDouble(KUKA_WEAVE_ANGLE, attribGetter.GetDouble(KUKA_WEAVE_ANGLE_DEFINE))

      attribSetter.SetBool(KUKA_ARCSENSE, attribGetter.GetBool(KUKA_ARCSENSE_DEFINE))
      attribSetter.SetEnumIndex(KUKA_ARCSENSE_PATTERN, attribGetter.GetEnumIndex(KUKA_ARCSENSE_PATTERN_DEFINE))
      attribSetter.SetDouble(KUKA_ARCSENSE_LATCTRLGAIN, attribGetter.GetDouble(KUKA_ARCSENSE_LATCTRLGAIN_DEFINE))
      attribSetter.SetDouble(KUKA_ARCSENSE_HEIGHTCTRL, attribGetter.GetDouble(KUKA_ARCSENSE_HEIGHTCTRL_DEFINE))
      attribSetter.SetDouble(KUKA_ARCSENSE_LATBIAS, attribGetter.GetDouble(KUKA_ARCSENSE_LATBIAS_DEFINE))
      attribSetter.SetDouble(KUKA_ARCSENSE_MAXCORR, attribGetter.GetDouble(KUKA_ARCSENSE_MAXCORR_DEFINE))
      attribSetter.SetBool(KUKA_ARCSENSE_FINDCENTER, attribGetter.GetBool(KUKA_ARCSENSE_FINDCENTER_DEFINE))
      attribSetter.SetDouble(KUKA_ARCSENSE_ACTIVDELAY, attribGetter.GetDouble(KUKA_ARCSENSE_ACTIVDELAY_DEFINE))
   else:
      ruleEvent = False

   # put all ArcOn attribs in a dictionary and store it in a JSON string attrib for easy download
   arcIgnInfo = {
      KUKA_ARC_SWITCH: attribGetter.GetBool(KUKA_ARC_SWITCH),
      KUKA_IGNITION_PROGRAM_NUMBER: attribGetter.GetInteger(KUKA_IGNITION_PROGRAM_NUMBER),
      KUKA_IGNITION_PARAM_SET: attribGetter.GetString(KUKA_IGNITION_PARAM_SET),
      KUKA_PRE_FLOW_TIME: attribGetter.GetDouble(KUKA_PRE_FLOW_TIME),
      KUKA_ON_THE_FLY_ACTIVE: attribGetter.GetBool(KUKA_ON_THE_FLY_ACTIVE),
      KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME: attribGetter.GetDouble(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME),
      KUKA_WAIT_TIME_AFTER_IGNITION: attribGetter.GetDouble(KUKA_WAIT_TIME_AFTER_IGNITION),
      "KukaRuleEvent": ruleEvent
   }
   attribSetter.SetString(KUKA_ARCIGNITION_JSON, json.dumps(arcIgnInfo))
   arcOnInfo = {
      KUKA_WELD_JOB_NUMBER: attribGetter.GetInteger(KUKA_WELD_JOB_NUMBER),
      KUKA_WELD_PARAM_SET: attribGetter.GetString(KUKA_WELD_PARAM_SET),
      KUKA_ROBOT_VELOCITY_1: attribGetter.GetDouble(KUKA_ROBOT_VELOCITY_1),
      KUKA_WEAVE_PATTERN: attribGetter.GetAttributeEnumByName(KUKA_WEAVE_PATTERN).GetValue(),
      KUKA_WEAVE_PATTERN+"Index": attribGetter.GetEnumIndex(KUKA_WEAVE_PATTERN),
      KUKA_WEAVE_PATTERN+"List": KUKA_WEAVE_PATTERN_LIST,
      KUKA_WEAVE_LENGTH: attribGetter.GetDouble(KUKA_WEAVE_LENGTH)*1000,
      KUKA_WEAVE_FREQUENCY: attribGetter.GetDouble(KUKA_WEAVE_FREQUENCY),
      KUKA_WEAVE_DEFLECTION: attribGetter.GetDouble(KUKA_WEAVE_DEFLECTION)*1000,
      KUKA_WEAVE_ANGLE: attribGetter.GetDouble(KUKA_WEAVE_ANGLE)
   }
   attribSetter.SetString(KUKA_ARCON_JSON, json.dumps(arcOnInfo))

   arcSense = {
      KUKA_ARCSENSE: attribGetter.GetBool(KUKA_ARCSENSE),
      KUKA_ARCSENSE_PATTERN: attribGetter.GetAttributeEnumByName(KUKA_ARCSENSE_PATTERN).GetValue(),
      KUKA_ARCSENSE_PATTERN+"Index": attribGetter.GetEnumIndex(KUKA_ARCSENSE_PATTERN),
      KUKA_ARCSENSE_PATTERN+"List": KUKA_ARCSENSE_PATTERN_LIST,
      KUKA_ARCSENSE_LATCTRLGAIN: attribGetter.GetDouble(KUKA_ARCSENSE_LATCTRLGAIN),
      KUKA_ARCSENSE_HEIGHTCTRL: attribGetter.GetDouble(KUKA_ARCSENSE_HEIGHTCTRL),
      KUKA_ARCSENSE_LATBIAS: attribGetter.GetDouble(KUKA_ARCSENSE_LATBIAS),
      KUKA_ARCSENSE_MAXCORR: attribGetter.GetDouble(KUKA_ARCSENSE_MAXCORR)*1000,
      KUKA_ARCSENSE_FINDCENTER: attribGetter.GetBool(KUKA_ARCSENSE_FINDCENTER),
      KUKA_ARCSENSE_ACTIVDELAY: attribGetter.GetDouble(KUKA_ARCSENSE_ACTIVDELAY)
   }

   attribSetter.SetString(KUKA_ARCSENSE_JSON, json.dumps(arcSense))
   pass

def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   ArcOnVisualize(Operator)
   pass

def ArcOnVisualize(Operator: CENPyOlpEvent_AttribChangedOperator):   # Hide unused default event attributes
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()
   attribGetter.GetAttributeByName("WeaveFrequenz").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveWidth").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveTime1").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveTime2").SetVisibility(False)

   enumAttrib = attribGetter.GetAttributeEnumByName(KUKA_WEAVE_PATTERN)
   weavePattern = enumAttrib.GetValue()
   enumAttrib = attribGetter.GetAttributeEnumByName(KUKA_WEAVE_TYPE)
   weaveType = enumAttrib.GetValue()
   advancedOptions = attribGetter.GetBool(KUKA_ARCTECH_ADV)
   flyByActive = attribGetter.GetBool(KUKA_ON_THE_FLY_ACTIVE)
   arcSwitch = attribGetter.GetBool(KUKA_ARC_SWITCH)
   # Show/hide weaving options
   if weavePattern == "None":
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH)
      weave.SetVisibility(False)
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY)
      weave.SetVisibility(False)
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_DEFLECTION)
      weave.SetVisibility(False)
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_ANGLE)
      weave.SetVisibility(False)
   else:  
      if weaveType == "Weave length":
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH)
         weave.SetVisibility(True)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY)
         weave.SetVisibility(False)
      else:
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_LENGTH)
         weave.SetVisibility(False)
         weave = attribGetter.GetAttributeByName(KUKA_WEAVE_FREQUENCY)
         weave.SetVisibility(True)
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_DEFLECTION)
      weave.SetVisibility(True)
      weave = attribGetter.GetAttributeByName(KUKA_WEAVE_ANGLE)
      weave.SetVisibility(True)
   if not arcSwitch:
      flyByActiveAttr = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_ACTIVE)
      flyByActiveAttr.SetVisibility(True)
      jobIgn = attribGetter.GetAttributeByName(KUKA_IGNITION_PROGRAM_NUMBER)
      jobIgn.SetVisibility(True)
      # Show/hide ArcTech Advanced options
      if advancedOptions:
         adv = attribGetter.GetAttributeByName(KUKA_PRE_FLOW_TIME)
         adv.SetVisibility(True)
         adv = attribGetter.GetAttributeByName(KUKA_WAIT_TIME_AFTER_IGNITION)
         adv.SetVisibility(True)
      else:
         adv = attribGetter.GetAttributeByName(KUKA_PRE_FLOW_TIME)
         adv.SetVisibility(False)
         adv = attribGetter.GetAttributeByName(KUKA_WAIT_TIME_AFTER_IGNITION)
         adv.SetVisibility(False)
      # Show/hide FlyBy distance
      if flyByActive:
         flyByEvt = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
         flyByEvt.SetVisibility(True)
      else:
         flyByEvt = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
         flyByEvt.SetVisibility(False)
   else:
      jobIgn = attribGetter.GetAttributeByName(KUKA_IGNITION_PROGRAM_NUMBER)
      jobIgn.SetVisibility(False)
      adv = attribGetter.GetAttributeByName(KUKA_PRE_FLOW_TIME)
      adv.SetVisibility(False)
      adv = attribGetter.GetAttributeByName(KUKA_WAIT_TIME_AFTER_IGNITION)
      adv.SetVisibility(False)
      flyByActiveAttr = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_ACTIVE)
      flyByActiveAttr.SetVisibility(False)
      flyByEvt = attribGetter.GetAttributeByName(KUKA_ON_THE_FLY_GAS_PRE_FLOW_TIME)
      flyByEvt.SetVisibility(False)
   pass


# post event compute    
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   ArcOnVisualize(Operator)

   # try:
   #    # get attribute creator
   #    attribGetter = Operator.GetAttribGetter()
   #    # get controller
   #    controller = Operator.GetController()
   #    # get reference toolpath element operator
   #    refTpe = Operator.GetRefTpElement()
   #    # get event operator
   #    eventOperator = Operator.GetEventOperator()
   # except:
   #    # log error
   #    logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)
   #    return

   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
# -------------------------------------------------------------------------------------------
