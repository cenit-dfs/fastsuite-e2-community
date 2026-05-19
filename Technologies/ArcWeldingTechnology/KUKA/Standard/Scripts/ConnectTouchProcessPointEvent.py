# -------------------------------------------------------------------------------------------
# Name: TouchSensingEvent
# Description: adding touch points with respect to vendor basic.
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

from cenpylib import *
from centypes import *
import sys
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

# ATTRIBUTES
AW_TOUCH_COUNTER = "Touch_Cntr"
AW_TOUCH_ID_VIACIR = "TouchID_ViaCir"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
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

   attribCreator.AddInteger(AW_TOUCH_COUNTER, 0,0,99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE, AW_TOUCH_COUNTER)
   attribString = attribCreator.AddString('ApprDirX', '',PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE, 'ApprDirX')
   attribString.SetVisibility(False)
   attribString = attribCreator.AddString('ApprDirZ', '',PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE, 'ApprDirZ')
   attribString.SetVisibility(False)

   id = attribGetter.GetAttributeIntegerByName('TouchID')
   id.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attribCreator.AddBool(AW_TOUCH_ID_VIACIR, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE, AW_TOUCH_ID_VIACIR)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# post process attribute
def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   # YOUR CODE
   xDir=Operator.GetRefToolpathElementPosition().GetXDirection().GetXYZ()
   zDir=Operator.GetRefToolpathElementPosition().GetZDirection().GetXYZ()

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# post process upload attribute
def PostProcessAttributesUpload(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_START)

   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_UPLOAD_ATTRIB_END) 


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


   # YOUR CODE

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)


# -------------------------------------------------------------------------------------------
# event post on attribute change 
def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # changedAttrib = Operator.GetChangedAttribute()  
   # attribName = changedAttrib.GetName()

   # YOUR CODE
   # YOUR CODE

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)