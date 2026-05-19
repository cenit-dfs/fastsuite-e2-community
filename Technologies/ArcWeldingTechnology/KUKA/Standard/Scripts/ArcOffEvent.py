# -------------------------------------------------------------------------------------------
# Name: ArcOffEvent
# Description: Extend standard ArcOffEvent for KUKA KRC4/5
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

EVENT_FILE_NAME = "ArcOffEvent.py"
EVENT_NAME = "ArcOffEvent"
EVENT_ICON = "ArcOff"
EVENT_ATTRIBUTE_TYPE = USER_ATTRIBUTE | PROCESS_ATTRIBUTE

#ArcTech Globals
KUKA_ARCTECH_ADV = "KukaArcTechAdv"
#ArcOff Event Definition
KUKA_ARC_OFF_JOB_NUMBER = "KukaArcOffJobNumber"
KUKA_ARC_OFF_PARAM_SET = "KukaArcOffParmSet"
KUKA_END_CRATER_TIME = "KukaEndCraterTime"
KUKA_POST_FLOW_TIME = "KukaPostFlowTime"
#ArcOff Technology Definition
KUKA_ARC_OFF_JOB_NUMBER_DEFINE = "KukaArcOffJobNumberDefine"
KUKA_ARC_OFF_PARAM_SET_DEFINE = "KukaArcOffParmSetDefine"
KUKA_END_CRATER_TIME_DEFINE = "KukaEndCraterTimeDefine"
KUKA_POST_FLOW_TIME_DEFINE = "KukaPostFlowTimeDefine"
KUKA_ARCOFF_JSON = "KukaArcOffJson"

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
   # Create KUKA attributes
   attribDouble = attribCreator.AddInteger(KUKA_ARC_OFF_JOB_NUMBER,0,0,MAX_INTEGER,EVENT_ATTRIBUTE_TYPE,KUKA_ARC_OFF_JOB_NUMBER)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribString = attribCreator.AddString(KUKA_ARC_OFF_PARAM_SET,'Set2', EVENT_ATTRIBUTE_TYPE,KUKA_ARC_OFF_PARAM_SET)
   attribString.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_END_CRATER_TIME,1.0,-100,100,0.1,EVENT_ATTRIBUTE_TYPE,ATTRIB_TIME,KUKA_END_CRATER_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attribDouble = attribCreator.AddDouble(KUKA_POST_FLOW_TIME,0.0,-100,100,0.1,EVENT_ATTRIBUTE_TYPE,ATTRIB_TIME,KUKA_POST_FLOW_TIME)
   attribDouble.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcOffJson = attribCreator.AddString(KUKA_ARCOFF_JSON,'', EVENT_ATTRIBUTE_TYPE, KUKA_ARCOFF_JSON)
   arcOffJson.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   arcOffJson.SetVisibility(False)

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

   # YOUR CODE
   if (Operator.IsEventCreatedAutomatically() == True):
      ruleEvent = True
      attribSetter.SetInteger(KUKA_ARC_OFF_JOB_NUMBER, attribGetter.GetInteger(KUKA_ARC_OFF_JOB_NUMBER_DEFINE))
      attribSetter.SetString(KUKA_ARC_OFF_PARAM_SET, attribGetter.GetString(KUKA_ARC_OFF_PARAM_SET_DEFINE))
      attribSetter.SetDouble(KUKA_END_CRATER_TIME, attribGetter.GetDouble(KUKA_END_CRATER_TIME_DEFINE))
      attribSetter.SetDouble(KUKA_POST_FLOW_TIME, attribGetter.GetDouble(KUKA_POST_FLOW_TIME_DEFINE))
   else:
      ruleEvent = False

   # put all ArcOn attribs in a dictionary and store it in a JSON string attrib for easy download
   arcOffInfo = {
      KUKA_ARC_OFF_JOB_NUMBER: attribGetter.GetInteger(KUKA_ARC_OFF_JOB_NUMBER),
      KUKA_ARC_OFF_PARAM_SET: attribGetter.GetString(KUKA_ARC_OFF_PARAM_SET),
      KUKA_END_CRATER_TIME: attribGetter.GetDouble(KUKA_END_CRATER_TIME),
      KUKA_POST_FLOW_TIME: attribGetter.GetDouble(KUKA_POST_FLOW_TIME),
      "KukaRuleEvent": ruleEvent
   }
   attribSetter.SetString(KUKA_ARCOFF_JSON, json.dumps(arcOffInfo))
   pass

def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   # get changed attribute
   # changedAttribName = Operator.GetChangedAttributeName()
   # changedAttrib=attribGetter.GetAttributeByName(changedAttribName)

   ArcOffVisualize(Operator)

   pass

def ArcOffVisualize(Operator):   # Hide unused default event attributes
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()
   advancedOptions = attribGetter.GetBool(KUKA_ARCTECH_ADV)
   # Show/hide ArcTech Advanced options
   if advancedOptions:
      adv = attribGetter.GetAttributeByName(KUKA_END_CRATER_TIME)
      adv.SetVisibility(True)
   else:
      adv = attribGetter.GetAttributeByName(KUKA_END_CRATER_TIME)
      adv.SetVisibility(False)
   pass


# post event compute    
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(EVENT_FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   ArcOffVisualize(Operator)

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
