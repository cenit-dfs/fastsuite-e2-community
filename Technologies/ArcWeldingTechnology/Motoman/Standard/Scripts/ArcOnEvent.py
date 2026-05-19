# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Adds ArcOn program number to standard event
# Debug info: E2@localhost:5254
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Cenit AG
#        Date: July 2024
#     
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import inspect, os
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "ArcOnEvent.py: "

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

# Event Attributes
ATT_EVT_WEAVE_ON_CMD = "WeaveOnCmd"

ATT_EVT_WEAVE_ONOFF = "WeaveOnOff"
ATT_EVT_WEAVE_FREQ = "WeaveFrequenz"
ATT_EVT_WEAVE_WIDTH = "WeaveWidth"
ATT_EVT_WEAVE_TIME1 = "WeaveTime1"
ATT_EVT_WEAVE_TIME2 = "WeaveTime2"

# Operation attribute definition
ATT_AW_USE_WEAVE_DEFINE = "UseWeaveDefine"
ATT_AW_WEAVE_ON_CMD = "ArcWeldingWeaveOnCmd"

def GetEventName():
   return "ArcOnEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes

AW_WEAVE_METHOD = "ArcWeldingWeaveMethod" 
AW_WEAVE_METHODS = ["No Weaving", "WEV#()", "ComArc WEV#()", "ComArc AMP="]

COMARC_WEAVING_FILE_NUMBER = "ArcWeldingWeaveOnCmd" # use existing attribute for "ComArcWeavingFileNumber"
COMARC_AMPLITUDE = "ComArcAmplitude" # "ComArcAmplitude"
COMARC_FREQUENCY = "ComArcFrequency" # "ComArcFrequency"
COMARC_USE_ANGLE = "ComArcUseAngle"
COMARC_ANGLE = "ComArcAngle"
COMARC_USE_WEAVING_DIRECTION = "ComArcUseWeavingDirection"
COMARC_WEAVING_DIRECTION = "ComArcWeavingDirection"
COMARC_WEAVING_DIRECTIONS = ["Unused", "0" , "1"]
COMARC_CORRECTION_UP_DOWN = "ComArcCorrectionUpDown"
COMARC_CORRECTION_RIGHT_LEFT = "ComArcCorrectionRightLeft"
COMARC_USE_CONDITION_FILE = "ComArcUseConditionFile"
COMARC_CONDITION_FILE_NUMBER = "ComArcConditionFileNumber"


ATT_EVT_WEAVE_METHOD = "WeaveMethod" # Replacing "WeaveOnOff"
ATT_EVT_WEAVE_METHODS = ["No Weaving", "WEV#()", "ComArc WEV#()", "ComArc AMP="] 
ATT_EVT_WEAVING_FILE_NUMBER = "WeaveOnCmd"
ATT_EVT_AMPLITUDE = "ComArcEvtAmplitude"    # "ComArcWidth"
ATT_EVT_FREQUENCY = "ComArcEvtFrequency" # "ComArcFrequency"
ATT_EVT_USE_ANGLE = "UseAngle"
ATT_EVT_ANGLE = "Angle"
ATT_EVT_USE_WEAVING_DIRECTION = "UseWeavingDirection"
ATT_EVT_WEAVING_DIRECTION = "WeavingDirection"
ATT_EVT_WEAVING_DIRECTIONS = ["Unused", "0" , "1"]
ATT_EVT_CORRECTION_UP_DOWN = "CorrectionUpDown"
ATT_EVT_CORRECTION_RIGHT_LEFT = "CorrectionRightLeft"
ATT_EVT_USE_CONDITION_FILE = "UseConditionFile"
ATT_EVT_CONDITION_FILE_NUMBER = "ConditionFileNumber"

def PostInitAttributes(Operator : CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   attribGetter.GetAttributeByName(ATT_EVT_WEAVE_ONOFF).SetVisibility(False)

   attCA1 = attribCreator.AddEnum(ATT_EVT_WEAVE_METHOD, ATT_EVT_WEAVE_METHODS, ATT_EVT_WEAVE_METHODS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_METHOD)
   attCA1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA2 = attribCreator.AddInteger(ATT_EVT_WEAVE_ON_CMD, 99, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_ON_CMD)
   attCA2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   # att1.SetVisibility(False)

   attCA3 = attribCreator.AddDouble(ATT_EVT_AMPLITUDE, 20, 0.1, 99.9, 5, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, ATT_EVT_AMPLITUDE)
   attCA3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA4 = attribCreator.AddDouble(ATT_EVT_FREQUENCY, 2, 0.1, 5, 0.2, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, ATT_EVT_FREQUENCY)
   attCA4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA5 = attribCreator.AddBool(ATT_EVT_USE_ANGLE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE,ATT_EVT_USE_ANGLE)
   attCA5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA6 = attribCreator.AddDouble(ATT_EVT_ANGLE, 45, 0, 180, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, ATT_EVT_ANGLE)
   attCA6.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA5 = attribCreator.AddBool(ATT_EVT_USE_WEAVING_DIRECTION, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_USE_WEAVING_DIRECTION)
   attCA5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA7 = attribCreator.AddEnum(ATT_EVT_WEAVING_DIRECTION, ATT_EVT_WEAVING_DIRECTIONS, ATT_EVT_WEAVING_DIRECTIONS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVING_DIRECTION)
   attCA7.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA8 = attribCreator.AddDouble(ATT_EVT_CORRECTION_UP_DOWN, 10, 1, 199, 20, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, ATT_EVT_CORRECTION_UP_DOWN)
   attCA8.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   
   attCA9 = attribCreator.AddDouble(ATT_EVT_CORRECTION_RIGHT_LEFT, 0, -255, 255, 20, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, ATT_EVT_CORRECTION_RIGHT_LEFT)
   attCA9.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA10 = attribCreator.AddBool(ATT_EVT_USE_CONDITION_FILE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_USE_CONDITION_FILE)
   attCA10.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attCA11 = attribCreator.AddInteger(ATT_EVT_CONDITION_FILE_NUMBER, 0, 0, 128, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_CONDITION_FILE_NUMBER)
   attCA11.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   HideShowAttributes(attribGetter)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()

   attribGetter.GetAttributeByName(ATT_EVT_WEAVE_ONOFF).SetVisibility(False)
   # attribGetter.GetAttributeByName(ATT_EVT_WEAVE_FREQ).SetVisibility(False)
   # attribGetter.GetAttributeByName(ATT_EVT_WEAVE_WIDTH).SetVisibility(False)
   # attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME1).SetVisibility(False)
   # attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME2).SetVisibility(False)
   
   attribName = Operator.GetChangedAttributeName()
   try:
      if attribName in [ATT_EVT_WEAVE_METHOD, ATT_EVT_USE_ANGLE, ATT_EVT_USE_WEAVING_DIRECTION, ATT_EVT_USE_CONDITION_FILE]:
         HideShowAttributes(attribGetter)
   except:
      logging.LogError('Cannot get the ComArc attributes')
      pass

def HideShowAttributes(attribGetter):
         WeaveMethodEnum = attribGetter.GetAttributeEnumByName(ATT_EVT_WEAVE_METHOD)

         attribGetter.GetAttributeByName(ATT_EVT_WEAVING_FILE_NUMBER).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_AMPLITUDE).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_FREQUENCY).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_USE_ANGLE).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_ANGLE).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_USE_WEAVING_DIRECTION).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_WEAVING_DIRECTION).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_CORRECTION_UP_DOWN).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_CORRECTION_RIGHT_LEFT).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_USE_CONDITION_FILE).SetVisibility(False)
         attribGetter.GetAttributeByName(ATT_EVT_CONDITION_FILE_NUMBER).SetVisibility(False)

         WeaveMethod = WeaveMethodEnum.GetValue()

         if WeaveMethod == ATT_EVT_WEAVE_METHODS[0]: # No Weaving
            pass

         if WeaveMethod == ATT_EVT_WEAVE_METHODS[1]: # WEV#()                   
            attribGetter.GetAttributeByName(ATT_EVT_WEAVING_FILE_NUMBER).SetVisibility(True)

         if WeaveMethod == ATT_EVT_WEAVE_METHODS[2] or WeaveMethod == ATT_EVT_WEAVE_METHODS[3]: # ComArc attributes
            
            attribGetter.GetAttributeByName(ATT_EVT_USE_WEAVING_DIRECTION).SetVisibility(True)
            attribGetter.GetAttributeByName(ATT_EVT_USE_CONDITION_FILE).SetVisibility(True)
            attribGetter.GetAttributeByName(ATT_EVT_CORRECTION_UP_DOWN).SetVisibility(True)
            attribGetter.GetAttributeByName(ATT_EVT_CORRECTION_RIGHT_LEFT).SetVisibility(True)

            if attribGetter.GetBool(ATT_EVT_USE_CONDITION_FILE) == True:               
               attribGetter.GetAttributeByName(ATT_EVT_CONDITION_FILE_NUMBER).SetVisibility(True)
            if attribGetter.GetBool(ATT_EVT_USE_WEAVING_DIRECTION) == True:
               attribGetter.GetAttributeByName(ATT_EVT_WEAVING_DIRECTION).SetVisibility(True)          
         
         if WeaveMethod == ATT_EVT_WEAVE_METHODS[2]: # ComArc WEV#()
            attribGetter.GetAttributeByName(ATT_EVT_WEAVING_FILE_NUMBER).SetVisibility(True)

         if WeaveMethod == ATT_EVT_WEAVE_METHODS[3]: # ComArc AMP=
            attribGetter.GetAttributeByName(ATT_EVT_AMPLITUDE).SetVisibility(True)
            print(attribGetter.GetDouble(ATT_EVT_AMPLITUDE))
            attribGetter.GetAttributeByName(ATT_EVT_FREQUENCY).SetVisibility(True)         
            attribGetter.GetAttributeByName(ATT_EVT_USE_ANGLE).SetVisibility(True)
            if attribGetter.GetBool(ATT_EVT_USE_ANGLE) == True:
               attribGetter.GetAttributeByName(ATT_EVT_ANGLE).SetVisibility(True)

def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   if (Operator.IsEventCreatedAutomatically()):

      attribSetter.SetEnumIndex(ATT_EVT_WEAVE_METHOD, attribGetter.GetEnumIndex(AW_WEAVE_METHOD),ATTRIBOVERRIDEMODE_DEFAULT)
      attribSetter.SetInteger(ATT_EVT_WEAVING_FILE_NUMBER, attribGetter.GetInteger(COMARC_WEAVING_FILE_NUMBER))
      attribSetter.SetDouble(ATT_EVT_AMPLITUDE, attribGetter.GetDouble(COMARC_AMPLITUDE))
      attribSetter.SetDouble(ATT_EVT_FREQUENCY, attribGetter.GetDouble(COMARC_FREQUENCY))
      attribSetter.SetBool(ATT_EVT_USE_ANGLE, attribGetter.GetBool(COMARC_USE_ANGLE))
      attribSetter.SetDouble(ATT_EVT_ANGLE, attribGetter.GetDouble(COMARC_ANGLE))
      attribSetter.SetDouble(ATT_EVT_CORRECTION_UP_DOWN, attribGetter.GetInteger(COMARC_CORRECTION_UP_DOWN))
      attribSetter.SetDouble(ATT_EVT_CORRECTION_RIGHT_LEFT, attribGetter.GetDouble(COMARC_CORRECTION_RIGHT_LEFT))
      attribSetter.SetEnumIndex(ATT_EVT_WEAVING_DIRECTION, attribGetter.GetEnumIndex(COMARC_WEAVING_DIRECTION))
      attribSetter.SetBool(ATT_EVT_USE_CONDITION_FILE, attribGetter.GetBool(COMARC_USE_CONDITION_FILE))
      attribSetter.SetInteger(ATT_EVT_CONDITION_FILE_NUMBER, attribGetter.GetInteger(COMARC_CONDITION_FILE_NUMBER))


# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()
