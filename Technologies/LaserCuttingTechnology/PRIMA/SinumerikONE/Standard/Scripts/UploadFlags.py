# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Adds ArcOn program number to standard event
# Debugg info: E2@localhost:5254
# Author:
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
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import UploadUtils
importlib.reload(UploadUtils)
from UploadUtils import *

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "UploadFlags.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug) prev on attribute change ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

UPLOAD_FLAG = 'UploadFlag'
UPLOAD_FLAG_LIST = ['APPROACH', 'RETRACT', 'HEADER', 'FOOTER']

EDIT_TEXT = 'EditText'
TEXT = 'Text'
MULTI_LINE_SEPARATOR = "MultiLineSeparator"
MULTI_LINE_SEPARATOR_CHAR = "|"

# Event Attributes

# Operation attribute definition

def GetEventName():
   return "UploadFlags"

def GetIconName():
   return "Upload"

def GetEventUuId():
   return "75f08226-eca4-4a46-aa5e-a33a40e7dcba"

def GetEventType():
   return OLPEVENT_OLP

def IsEnabled():
   return True


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

   attribIntENM = attribCreator.AddEnum(UPLOAD_FLAG,UPLOAD_FLAG_LIST,UPLOAD_FLAG_LIST[0],PROCESS_ATTRIBUTE|USER_ATTRIBUTE,UPLOAD_FLAG)

   att0 = attribCreator.AddBool(EDIT_TEXT, False, USER_ATTRIBUTE, EDIT_TEXT)
   att2 = attribCreator.AddString(TEXT, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , TEXT)
   att2.SetVisibility(False)
   att4 = attribCreator.AddString(MULTI_LINE_SEPARATOR, MULTI_LINE_SEPARATOR_CHAR, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, MULTI_LINE_SEPARATOR)
   att4.SetVisibility(False)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
	# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   changed_attrib_name = Operator.GetChangedAttributeName()

   if changed_attrib_name == EDIT_TEXT:
      editText = attribGetter.GetAttributeByName(EDIT_TEXT)
      handle_edit_attribute(
         EDIT_TEXT, 
         TEXT, 
         attribGetter, 
         attribSetter,
         logging
      )

   elif changed_attrib_name == UPLOAD_FLAG:
      flag = attribGetter.GetEnumIndex(UPLOAD_FLAG)
      editText = attribGetter.GetAttributeByName(EDIT_TEXT)
      if flag == 0 or flag == 1:
         editText.SetVisibility(False)
      else:
         editText.SetVisibility(True)      

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)

def handle_edit_attribute(edit_flag, text_attrib, attrib_getter, attrib_setter, logging):
   """
   Generic function to handle editing of attributes.
   """
   if attrib_getter.GetBool(edit_flag):
      input_str = attrib_getter.GetString(text_attrib)
      multi_line_separator = attrib_getter.GetString(MULTI_LINE_SEPARATOR)
      
      # Open MultiLineEditor window
      edited_str = edit_text_lines(input_str, multi_line_separator)
      
      # Adapt attribute values and properties
      if edited_str is not None:
         attrib_setter.SetString(text_attrib, edited_str, ATTRIBOVERRIDEMODE_DEFAULT)
         logging.LogInfo(f"Edited text: {edited_str}")
      else:
         logging.LogInfo("Editing was cancelled.")
      
      # Reset Editor flag
      attrib_setter.SetBool(edit_flag, False, ATTRIBOVERRIDEMODE_DEFAULT)
   
   
def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   # attribSetter = Operator.GetAttribSetter()

   #if (Operator.IsEventCreatedAutomatically()):
   #   UseWeave = attribGetter.GetBool(ATT_AW_USE_WEAVE_DEFINE)
   #   attribSetter.SetBool(ATT_EVT_WEAVE_ONOFF,UseWeave)

   flag = attribGetter.GetEnumIndex(UPLOAD_FLAG)
   editText = attribGetter.GetAttributeByName(EDIT_TEXT)
   if flag == 0 or flag == 1:
      editText.SetVisibility(False)
   else:
      editText.SetVisibility(True)      

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   # attribGetter = Operator.GetAttribGetter()
