# -------------------------------------------------------------------------------------------
# Name: LaserCutting technology
# Description: Customisation for PRIMA LASERNEXT and EVEREST with SINUMERIK ONE Controller
# Debugg info: E2@localhost:5254
# Author: Berauer
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 2024-12-04
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
import importlib
import inspect, os, sys
import csv
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import UploadUtils
importlib.reload(UploadUtils)
from UploadUtils import *

# -------------------------------------------------------------------------------------------
# global definitions.
FILE_NAME = "LaserCuttingTechnology.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug) initialization of manufacturing geometry ended."

DEBUG_PREV_EXECUTE_RECIPE_START = "(Debug) prev execute recipe started."
DEBUG_PREV_EXECUTE_RECIPE_END = "(Debug) prev execute recipe ended."

DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START = "(Debug) post process operation group attributes started."
DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END = "(Debug) post process operation group attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug) prev on attribute change ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

REQUEST_RECOMPUTE = 'RequestRecompute'
# Tech group attributes
FORMAT_REGSHAPE = 'FormatRegshape'
FIXTURE_CODE = 'FixtureCode'
AREA_USED = 'AreaUsed'
EDIT_UPLOAD_HEADER = 'EditUploadHeader'
EDIT_UPLOAD_FOOTER = 'EditUploadFooter'
UPLOAD_HEADER = 'UploadHeader'
UPLOAD_FOOTER = 'UploadFooter'
MULTI_LINE_SEPARATOR = "MultiLineSeparator"
MULTI_LINE_SEPARATOR_CHAR = "|"

# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator : CENPyOlpTech_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()

   # PRIMA Everest Upload and Auto Validation attributes
   # attribCreator.AddInteger(FORMAT_REGSHAPE, 4, 0, 6, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , FORMAT_REGSHAPE)
   attribCreator.AddString(FIXTURE_CODE, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , FIXTURE_CODE)
   attribCreator.AddString(AREA_USED, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , AREA_USED)

   att0 = attribCreator.AddBool(EDIT_UPLOAD_HEADER, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, EDIT_UPLOAD_HEADER)
   att1 = attribCreator.AddBool(EDIT_UPLOAD_FOOTER, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, EDIT_UPLOAD_FOOTER)
   att2 = attribCreator.AddString(UPLOAD_HEADER, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , UPLOAD_HEADER)
   # att2.SetVisibility(False)
   att3 = attribCreator.AddString(UPLOAD_FOOTER, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , UPLOAD_FOOTER)
   # att3.SetVisibility(False)
   att4 = attribCreator.AddString(MULTI_LINE_SEPARATOR, MULTI_LINE_SEPARATOR_CHAR, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, MULTI_LINE_SEPARATOR)
   att4.SetVisibility(False)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# Technology post event initialization
def PostTechInitEvents(Operator : CENPyOlpTech_EventInitOperator):
   # # get logger
   logging = Operator.GetLoggerOperator()
   # # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   Operator.RegisterPyTechnologyEvent('TextEvent.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  TextEvent ')
   Operator.RegisterPyTechnologyEvent('UploadFlags.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  UploadFlags ')
   
   # # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)
   pass
# -------------------------------------------------------------------------------------------
# Technology post event rule initialization
def PostTechInitRules(Operator : CENPyOlpTech_RuleInitOperator):
   # # get logger
   # logging = Operator.GetLoggerOperator()
   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

   # # YOUR CODE
   # # pyLaserEvent= Operator.AddPyEvent('RuleGohome','SC_FM_GOHOME')
   # # Operator.SetActivePyEvent('RuleGohome','SC_FM_GOHOME')     

   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)
   pass


# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator : CENPyOlpTech_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()

   changed_attrib_name = Operator.GetChangedAttributeName()

   if changed_attrib_name == EDIT_UPLOAD_HEADER:
      handle_edit_attribute(
         EDIT_UPLOAD_HEADER, 
         UPLOAD_HEADER, 
         attribGetter, 
         attribSetter,
         logging
      )

   elif changed_attrib_name == EDIT_UPLOAD_FOOTER:
      handle_edit_attribute(
         EDIT_UPLOAD_FOOTER, 
         UPLOAD_FOOTER, 
         attribGetter, 
         attribSetter,
         logging
      )
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

# -------------------------------------------------------------------------------------------
# Technology post manufacturing geometry initialization
def PostInitManufacturingGeometry(Operator : CENPyOlpTech_MfGeoInitOperator):
   # # get logger
   # logging = Operator.GetLoggerOperator()
   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_START)

   # # YOUR CODE

   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_END)
   pass

# -------------------------------------------------------------------------------------------
# Technology PrevExecuteRecipe
def PrevExecuteRecipe(Operator : CENPyOlpTech_RecipeOperator):
   # # get logger
   # logging = Operator.GetLoggerOperator()
   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

   # # YOUR CODE

   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)
   pass

# -------------------------------------------------------------------------------------------
# Technology PostProcessOperationGroupAttributes
def PostProcessOperationGroupAttributes(Operator : CENPyOlpTech_POGAttribOperator):
   # # get logger
   # logging = Operator.GetLoggerOperator()
   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

   # # YOUR CODE

   # # debug logging
   # logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)
   pass

# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   return 5

# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator: CENPyOlpTech_UpdateOperator):
   logging = Operator.GetLoggerOperator()
   logging.LogInfo('####################################################')
   logging.LogDebug("(Debug) Post tech update started.")
   lastVersion = Operator.GetLastSavedPythonTechnologyVersion()
   currentVersion = GetPythonTechnologyVersion()
   logging.LogInfo('Last script version: ' + str(lastVersion) + '. Current script version: ' + str(currentVersion))
   program = Operator.GetOlpProgram()
   attribGetter = Operator.GetAttribGetter(program)
   attribSetter = Operator.GetAttribSetter(program)
   attribCreator = Operator.GetAttribCreator(program)
      
   if (lastVersion < 5):
      requestRecompute = attribCreator.AddInteger(REQUEST_RECOMPUTE,  0, 0, 99, GLOBAL_ATTRIBUTE | OPERATION_ATTRIBUTE, REQUEST_RECOMPUTE)
      # attribCreator.AddInteger(FORMAT_REGSHAPE, 4, 0, 6, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , FORMAT_REGSHAPE)
      attribCreator.AddString(FIXTURE_CODE, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , FIXTURE_CODE)
      attribCreator.AddString(AREA_USED, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , AREA_USED)
      attribCreator.AddBool(EDIT_UPLOAD_HEADER, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, EDIT_UPLOAD_HEADER)
      attribCreator.AddBool(EDIT_UPLOAD_FOOTER, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, EDIT_UPLOAD_FOOTER)
      attribCreator.AddString(UPLOAD_HEADER, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , UPLOAD_HEADER)
      attribCreator.AddString(UPLOAD_FOOTER, '', GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE , UPLOAD_FOOTER)
      attribCreator.AddString(MULTI_LINE_SEPARATOR, MULTI_LINE_SEPARATOR_CHAR, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, MULTI_LINE_SEPARATOR)

      
      # componentsList = program.GetChildComponents()
      # for component in componentsList:
      #    componentType = component.GetType()       
      #    if componentType < OLPPROGRAMCOMPONENTTYPE_EVENT:
      #       attribGetter = Operator.GetAttribGetter(component)
      #       sequence = attribCreator.AddInteger(AW_WELD_SEQUENCE_DEFINE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WELD_SEQUENCE)
      #       sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      #       # att = None
      #       # att = attribGetter.GetAttributeByName(AW_GLOBAL_PORT_LASER)
      #       # if (att):
      #       #    try:
      #       #       Operator.RemoveAttribute(component,AW_GLOBAL_PORT_LASER)
      #       #    except:
      #       #       pass                 
      #       # att = None
      #       # att = attribGetter.GetAttributeByName(AW_GLOBAL_PORT_TOUCH)
      #       # if (att):
      #       #    try:
      #       #       Operator.RemoveAttribute(component,AW_GLOBAL_PORT_TOUCH)
      #       #    except:
      #       #       pass
      #    elif componentType == OLPPROGRAMCOMPONENTTYPE_EVENT:
      #       attribGetter = Operator.GetAttribGetter(component)
      #       sequence = attribCreator.AddInteger(AW_WELD_SEQUENCE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_WELD_SEQUENCE)
      #       sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   completeRecomputeNeeded = ENTERSTATE_STARTWITHRULEEVENTS   

   return completeRecomputeNeeded

def RemoveAttribute(Operator, component, Name):
   if component.GetType() < 4:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttribute(Operator, childComponent, Name)


def RemoveAttributeFromWM(Operator, component, Name, CreatorName):
   if component.GetType() < 4 and component.GetCreatorName()==CreatorName:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttributeFromWM(Operator, childComponent, Name, CreatorName)
