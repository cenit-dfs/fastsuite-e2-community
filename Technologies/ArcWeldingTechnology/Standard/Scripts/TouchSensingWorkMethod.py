# -------------------------------------------------------------------------------------------
# Name: TouchSensingWorkMethod
# Description: this Python file adjust basic implementation for vendor specific installation 
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

# Operation attribute definition
WM_MOTION_TYPE = "OperationGroupMotionType"
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TOUCHSENS_LENGTH = "TouchSensingLength"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY = "Tooltip" + AW_MOTION_TYPE_FIRST_TPE
AW_MOTION_TYPE_FIRST_TPE_LITERALS = ["PTP", "LIN"]

# -------------------------------------------------------------------------------------------
# Work method post init attributes
def PostWmInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return

   try:
      # set motion type default PTP = 0; LIN = 1
      attribSetter.SetEnumIndex(WM_MOTION_TYPE, 1)
      searchMoTypeIndex = attribGetter.GetEnumIndex(WM_MOTION_TYPE)
      attrib = attribCreator.AddEnum(AW_MOTION_TYPE_FIRST_TPE, AW_MOTION_TYPE_FIRST_TPE_LITERALS, AW_MOTION_TYPE_FIRST_TPE_LITERALS[searchMoTypeIndex], OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_MOTION_TYPE_FIRST_TPE)
      attrib.SetTooltipKey(AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY)
      attrib.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   except:
      logging.LogError("Cannot initialize vendor specific touch sensing work method attributes")

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# Work method post init events
def PostWmInitEvents(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   Operator.RegisterPyTechnologyEvent('TouchPointStartAppEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointCollisionEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointEndEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointStartRetEvent.py')

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)


# -------------------------------------------------------------------------------------------
# Work method post init event rules
# def PostWmInitRules(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)


# -------------------------------------------------------------------------------------------
# Work method post sync process geometry attributes
# def PostWmSyncPgAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Work method post process operation attributes
# def PostProcessOperationAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Work method on attribute change 
def PostWmOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # changedAttrib = Operator.GetChangedAttribute()  
   # attribName = changedAttrib.GetName()

   # YOUR CODE

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)


# -------------------------------------------------------------------------------------------
# Work method on frame change 
# def PostWmOnFrameChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
