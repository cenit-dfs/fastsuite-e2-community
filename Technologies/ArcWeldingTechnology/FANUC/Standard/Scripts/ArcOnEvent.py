# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Adds ArcOn program number to standard event
# Debugg info: E2@localhost:5254
# Author: Schoppenhauer
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
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
# ATT_EVT_WEAVE_ON_CMD = "WeaveOnCmd"

ATT_EVT_WEAVE_ONOFF = "WeaveOnOff"
ATT_EVT_WEAVE_FREQ = "WeaveFrequenz"
ATT_EVT_WEAVE_WIDTH = "WeaveWidth"
ATT_EVT_WEAVE_TIME1 = "WeaveTime1"
ATT_EVT_WEAVE_TIME2 = "WeaveTime2"
ATT_EVT_WEAVE_PATTERN = "WeavePattern"
ATT_EVT_WEAVE_PATTERN_LITERALS = ["Sine", "Sine 2", "Figure 8", "Circle", "L"]
ATT_EVT_WEAVE_USE_SCHEDULE = "WeaveUseSchedule"
ATT_EVT_WEAVE_SCHEDULE = "WeaveSchedule"
# ArcWelding
ATT_EVT_WELD_SEQUENCE = "WeldSequence"
ATT_AW_WELD_SEQUENCE_DEFINE = "WeldSequenceDefine"
# Operation attribute definition
ATT_AW_USE_WEAVE_DEFINE = "UseWeaveDefine"
ATT_AW_WEAVE_PATTERN_DEFINE = "WeavePatternDefine"
ATT_AW_WEAVE_USE_SCHEDULE_DEFINE = "WeaveUseScheduleDefine"
ATT_AW_WEAVE_SCHEDULE_DEFINE = "WeaveScheduleDefine"

def GetEventName():
   return "ArcOnEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes

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

   # att1 = attribCreator.AddInteger(ATT_EVT_WEAVE_ON_CMD, 99, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_ON_CMD)
   # att1.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   # att1.SetVisibility(False)

   sequence = attribCreator.AddInteger(ATT_EVT_WELD_SEQUENCE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WELD_SEQUENCE)
   sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   # Weaving
   weavePattern = attribCreator.AddEnum(ATT_EVT_WEAVE_PATTERN, ATT_EVT_WEAVE_PATTERN_LITERALS, ATT_EVT_WEAVE_PATTERN_LITERALS[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_PATTERN)
   weavePattern.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveUseSchedule = attribCreator.AddBool(ATT_EVT_WEAVE_USE_SCHEDULE, True, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_USE_SCHEDULE)
   weaveUseSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveSchedule = attribCreator.AddInteger(ATT_EVT_WEAVE_SCHEDULE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATT_EVT_WEAVE_SCHEDULE)
   weaveSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   try:
      # get attribute setter
      attribSetter = Operator.GetAttribSetter()
      # get attribute getter
      attribGetter = Operator.GetAttribGetter()
   except:
      logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

   if (Operator.IsEventCreatedAutomatically() == True):
      ruleEvent = True
      attribSetter.SetInteger(ATT_EVT_WELD_SEQUENCE, attribGetter.GetInteger(ATT_AW_WELD_SEQUENCE_DEFINE))
      attribSetter.SetBool(ATT_EVT_WEAVE_ONOFF, attribGetter.GetBool(ATT_AW_USE_WEAVE_DEFINE))
      attribSetter.SetEnumIndex(ATT_EVT_WEAVE_PATTERN, attribGetter.GetEnumIndex(ATT_AW_WEAVE_PATTERN_DEFINE))
      attribSetter.SetBool(ATT_EVT_WEAVE_USE_SCHEDULE, attribGetter.GetBool(ATT_AW_WEAVE_USE_SCHEDULE_DEFINE))
      attribSetter.SetInteger(ATT_EVT_WEAVE_SCHEDULE, attribGetter.GetInteger(ATT_AW_WEAVE_SCHEDULE_DEFINE))

      # WeavePattern = attribGetter.GetEnumIndex(ATT_EVT_WEAVE_PATTERN)
      # if (WeavePattern > -1):
      #    attribSetter.SetEnumIndex(ATT_EVT_WEAVE_PATTERN,WeavePattern)
      #    UseWeaveSchedule = attribGetter.GetBool(ATT_AW_WEAVE_USE_SCHEDULE_DEFINE)
      #    attribSetter.SetBool(ATT_EVT_WEAVE_USE_SCHEDULE,UseWeaveSchedule)
      #    WeaveSchedule = attribGetter.GetInteger(ATT_AW_WEAVE_SCHEDULE_DEFINE)
      #    attribSetter.SetInteger(ATT_EVT_WEAVE_SCHEDULE,WeaveSchedule)
   else:
      ruleEvent = False

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   # attribGetter = Operator.GetAttribGetter()
   # get setter
   # attribSetter = Operator.GetAttribSetter()

   ArcOnVisualize(Operator)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   #attribGetter = Operator.GetAttribGetter()

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

# -------------------------------------------------------------------------------------------

def ArcOnVisualize(Operator: CENPyOlpEvent_AttribChangedOperator):   # Hide unused default event attributes
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   # attribSetter = Operator.GetAttribSetter()

   useWeave = attribGetter.GetBool(ATT_EVT_WEAVE_ONOFF) 
   # attribGetter.GetAttributeByName(ATT_EVT_WEAVE_ON_CMD).SetVisibility(UseWeave)
   
   # Weaving and Thru the arc sensing attributes
   sequence = attribGetter.GetAttributeByName(ATT_EVT_WELD_SEQUENCE)
   weaveFreq = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_FREQ)
   weaveWidth = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_WIDTH)
   weaveTime1 = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME1)
   weaveTime2 = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_TIME2)
   weavePattern = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_PATTERN)
   weaveUseSchedule = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_USE_SCHEDULE)
   weaveUseScheduleValue = attribGetter.GetBool(ATT_EVT_WEAVE_USE_SCHEDULE)
   weaveSchedule = attribGetter.GetAttributeByName(ATT_EVT_WEAVE_SCHEDULE)
   # if useWeaving:
   if useWeave:
      # Weaving
      weavePattern.SetVisibility(True)
      weaveUseSchedule.SetVisibility(True)
      if weaveUseScheduleValue:
         weaveFreq.SetVisibility(False)
         weaveWidth.SetVisibility(False)
         weaveTime1.SetVisibility(False)
         weaveTime2.SetVisibility(False)
         weaveSchedule.SetVisibility(True)
      else:
         weaveFreq.SetVisibility(True)
         weaveWidth.SetVisibility(True)
         weaveTime1.SetVisibility(True)
         weaveTime2.SetVisibility(True)
         weaveSchedule.SetVisibility(False)
   else:
      weavePattern.SetVisibility(False)
      weaveUseSchedule.SetVisibility(False)
      weaveFreq.SetVisibility(False)
      weaveWidth.SetVisibility(False)
      weaveTime1.SetVisibility(False)
      weaveTime2.SetVisibility(False)
      weaveSchedule.SetVisibility(False)
