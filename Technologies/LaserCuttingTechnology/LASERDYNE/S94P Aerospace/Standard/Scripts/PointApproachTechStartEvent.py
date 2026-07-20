# -------------------------------------------------------------------------------------------
# Name: 
# Description: 
# Debugg info: E2@localhost:5254
# Author: 
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "PointApproachTechStartEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."
DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."
DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

APPROACH_SPEED = "LC_LD_PNT_APPROACH_FEEDRATE"
RETRACT_SPEED = "LC_LD_PNT_RETRACT_FEEDRATE"

# Operation attribute definition

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   ##logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # YOUR CODE
   ##logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   #logging.LogDebug(".................................PointApproachTechStartEvent :: PostCompute")
   # get event operator
   eventOperator = Operator.GetEventOperator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # debug logging
   refTpElement= Operator.GetRefTpElement()
   #-----------------------------------
   feedrate = attribGetter.GetDouble(APPROACH_SPEED)
   speedEventPTP=eventOperator.AddSpeed(refTpElement,TPINSERTPOS_INSERTBEFORE)
   speedEventPTP.SetPathType(EVENTPATHTYPE_POINTTOPOINT)
   speedEventPTP.SetUnit(ATTRIB_PERCENT)
   speedEventPTP.SetSpeed(50)
   speedEventLIN=eventOperator.AddSpeed(refTpElement,TPINSERTPOS_INSERTBEFORE)
   speedEventLIN.SetPathType(EVENTPATHTYPE_CONTOUR)
   speedEventLIN.SetUnit(ATTRIB_SPEED)
   speedEventLIN.SetSpeed(feedrate)
   #-----------------------------------
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

# -------------------------------------------------------------------------------------------
# 
def GetEventName():
   return "PointApproachTechStartEvent"
   
def GetEventUuId():
   return "DF63E3F2-174D-444E-A3FC-B21CEE745D31"

def GetIconName():
   return "Velocity"
   
def GetExplodeCycle():
   return 0
   
def GetMultipleCreationIsPossible():
   return 1

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEFORBIDDEN
   
def GetEventType():
   return OLPEVENT_PROCESS

def GetGroupName():
   return "OlpEvent"

def GetCycleRotationFlag():
   return CYCLEROTATION_ROTNO
def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTNO
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTNO

def GetCycleTranslationFlag():
   return CYCLETRANSLATION_TRANSNO
def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSNO
def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSNO

def IsMachiningCycle():
   return 0

def IsEnabled():
   # do not display in EventsDB
   return False
   
def GetGroupName():
   return ''