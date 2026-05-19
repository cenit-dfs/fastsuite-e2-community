# -------------------------------------------------------------------------------------------
# Name: SPTP_SLIN
# Description: New SPTP_SLIN event to flag spline output for KUKA KRC4/5
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
import inspect, os
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

EVENT_FILE_NAME = "SPTP_SLIN.py"
EVENT_NAME = "SPTP_SLIN"
EVENT_ICON = "OLP_Param_StartposMove"

EVENT_UUID = "3cefea2f-db3e-43a7-a8e7-dd8ddc98eab2"
EVENT_ATTRIBUTE_TYPE = USER_ATTRIBUTE | PROCESS_ATTRIBUTE

#Spline Definition
KUKA_SPTP_SLIN = "SPtpSLin"

def GetEventName():
   return EVENT_NAME

def GetEventUuId():
   return EVENT_UUID

def GetIconName():
   return EVENT_ICON

def GetEventType():
   return OLPEVENT_OLP

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

   attribBool = attribCreator.AddBool(KUKA_SPTP_SLIN,False,EVENT_ATTRIBUTE_TYPE,KUKA_SPTP_SLIN)

# -------------------------------------------------------------------------------------------
def GetExplodeCycle():
   return 0

def GetMultipleCreationIsPossible():
   return 1

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEFORBIDDEN

def IsMachiningCycle():
   return 0

def GetGroupName():
   return "Kuka Arc Weld"

def GetCycleReferenceBehavior():
	return CYCLEREFBEHAVIOR_NORMAL

def GetCycleRotationAutoFlag():
   return 0

def GetCycleTranslationAutoFlag():
   return 0

def GetCycleRotationManualFlag():
   return 0

def GetCycleTranslationManualFlag():
   return 0