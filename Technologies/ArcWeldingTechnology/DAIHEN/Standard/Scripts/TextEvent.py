# -------------------------------------------------------------------------------------------
# Name: TextEvent
# Description: Adds MultiLine support to regular TextEvent
# Debug info: E2@localhost:5254
# Author: Cenit AG 2025
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import importlib
import inspect, os
import sys
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import UploadUtils
importlib.reload(UploadUtils)
from UploadUtils import *

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "TextEvent.py: "

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

TEXT_EVT_IS_MULTI_LINE = "IsMultiLine"
TEXT_EVT_IS_MULTI_LINE_FLAG = False
TEXT_EVT_MULTI_LINE_EDITOR = "OpenMultiLineEditor"
TEXT_EVT_MULTI_LINE_EDITOR_FLAG = False
TEXT_EVT_MULTI_LINE_SEPARATOR = "MultiLineSeparator"
TEXT_EVT_MULTI_LINE_SEPARATOR_CHAR = "|"

# Event Attributes

# Operation attribute definition

def GetEventName():
   return "TextEvent"
def GetEventUuId():
   return "1F8F31A9-68DD-4323-B051-6E6ED44BD4CD"
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

   att0 = attribCreator.AddBool(TEXT_EVT_IS_MULTI_LINE, TEXT_EVT_IS_MULTI_LINE_FLAG, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, TEXT_EVT_IS_MULTI_LINE)
   att0.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att1 = attribCreator.AddBool(TEXT_EVT_MULTI_LINE_EDITOR, TEXT_EVT_MULTI_LINE_EDITOR_FLAG, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, TEXT_EVT_MULTI_LINE_EDITOR)
   att1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att2 = attribCreator.AddString(TEXT_EVT_MULTI_LINE_SEPARATOR, TEXT_EVT_MULTI_LINE_SEPARATOR_CHAR, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, TEXT_EVT_MULTI_LINE_SEPARATOR)
   att2.SetVisibility(False)
   #att3 = attribGetter.GetAttributeByName("IsComment")
   #if att3 is not None:
   #   att3.SetVisibility(False)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   text = attribGetter.GetAttributeByName("Text")
   input_str = attribGetter.GetString("Text")
   isMultiLine = attribGetter.GetAttributeByName(TEXT_EVT_IS_MULTI_LINE)
   if TEXT_EVT_MULTI_LINE_SEPARATOR_CHAR in input_str:
      text.SetVisibility(False)
      isMultiLine.SetReadOnly(True)
      # isMultiLine.SetVisibility(True)
      attribSetter.SetBool(TEXT_EVT_IS_MULTI_LINE,True,ATTRIBOVERRIDEMODE_DEFAULT)
   else:
      text.SetVisibility(True)
      isMultiLine.SetReadOnly(True)
      # isMultiLine.SetVisibility(False)
      attribSetter.SetBool(TEXT_EVT_IS_MULTI_LINE,False,ATTRIBOVERRIDEMODE_DEFAULT)

   #if (Operator.IsEventCreatedAutomatically()):
   #   UseWeave = attribGetter.GetBool(ATT_AW_USE_WEAVE_DEFINE)
   #   attribSetter.SetBool(ATT_EVT_WEAVE_ONOFF,UseWeave)

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
	# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   changedAttribName = Operator.GetChangedAttributeName()
   if changedAttribName == TEXT_EVT_MULTI_LINE_EDITOR:
      if attribGetter.GetBool(TEXT_EVT_MULTI_LINE_EDITOR):
         text = attribGetter.GetAttributeByName("Text")
         input_str = attribGetter.GetString("Text")
         isMultiLine = attribGetter.GetAttributeByName(TEXT_EVT_IS_MULTI_LINE)
         multiLineSeparator = attribGetter.GetString(TEXT_EVT_MULTI_LINE_SEPARATOR)
         # Open MultiLineEditor window
         edited_str = edit_text_lines(input_str, multiLineSeparator)
         # Adapt attribute values and properties
         if edited_str is not None:
            if TEXT_EVT_MULTI_LINE_SEPARATOR_CHAR in edited_str:
               text.SetVisibility(False)
               isMultiLine.SetReadOnly(True)
               # isMultiLine.SetVisibility(True)
               attribSetter.SetBool(TEXT_EVT_IS_MULTI_LINE,True,ATTRIBOVERRIDEMODE_DEFAULT)
            else:
               text.SetVisibility(True)
               isMultiLine.SetReadOnly(True)
               # isMultiLine.SetVisibility(False)
               attribSetter.SetBool(TEXT_EVT_IS_MULTI_LINE,False,ATTRIBOVERRIDEMODE_DEFAULT)

            attribSetter.SetString("Text",edited_str,ATTRIBOVERRIDEMODE_DEFAULT)
            logging.LogInfo("Edited text: " + edited_str)
         else:
            logging.LogInfo("Editing was cancelled.")
      # Reset Editor flag
      attribSetter.SetBool(TEXT_EVT_MULTI_LINE_EDITOR,False,ATTRIBOVERRIDEMODE_DEFAULT)
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   #att3 = attribGetter.GetAttributeByName("IsComment")
   #if att3 is not None:
   #   att3.SetVisibility(False)
