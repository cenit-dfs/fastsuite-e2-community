# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: this Python file adjust basic implementation for Yaskawa specific installation 
# Debug info: E2@localhost:5254
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Cenit AG
#        Date: July 2024
#     
# -------------------------------------------------------------------------------------------

import inspect, os, sys
sys.dont_write_bytecode = True
from centypes import *
from cenpylib import *
import inspect, os
import csv
import ctypes
import sys
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# Global definitions
FILE_NAME = "ArcWeldingTechnology.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug-Technology) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug-Technology) initialization of manufacturing geometry ended."

DEBUG_PREV_EXECUTE_RECIPE_START = "(Debug-Technology) prev execute recipe started."
DEBUG_PREV_EXECUTE_RECIPE_END = "(Debug-Technology) prev execute recipe ended."

DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START = "(Debug-Technology) post process operation group attributes started."
DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END = "(Debug-Technology) post process operation group attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) post on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

DEBUG_POST_TECH_UPDATE_START = "(Debug-Technology) post technology update started."
DEBUG_POST_TECH_UPDATE_END = "(Debug-Technology) post technology update ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."
ERROR_ON_ATTRIB_CHANGE = "(Error) Could not change attribute in OnAttribChange = "

SYS_ATT_PROCESSFLOWDIRECTION = "Sys_Att_ProcessFlowDirection"

# Attribute definition
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
MAX_INTEGER = 2147483647

AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"

#AW_ARC_ON_CMD = "ArcWeldingArcOnCmd"
AW_ARC_ON_MIG = 20
AW_ARC_ON_TIG = 5
AW_PROG_NUMBER2_DEFINE = "ProgNumber2Define"
AW_WEAVE_ON_CMD = "ArcWeldingWeaveOnCmd"
AW_ARC_OFF_CRATER_FILL = "ArcWeldingArcOffCraterFill"
AW_ARC_OFF_CRATER_FILL_DELAY = "ArcWeldingArcOffCraterFillDelay"

AW_PS_MANUFACTURER = "ArcWeldingPSManufacturer"
AW_PS_MANUFACTURER_LIST = ["Yaskawa","Fronius"]

AW_TORCH_TYPE = "ArcWeldingTorchType"
AW_TORCH_TYPE_LIST = ["MIG/MAG","TIG"]

AW_STATION_NR = "ArcWeldingStationNr"
AW_GROUP_MAPPING = "ArcWeldingGroupsMapping"

AW_SENSING_PORT = "ArcWeldingSensingPort"

AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
AW_TOUCHSENS_WIRE_DIAM = "TSWireDiam"

AW_WEAVE_METHOD = "ArcWeldingWeaveMethod" 
AW_WEAVE_METHODS = ["No Weaving", "WEV#()", "ComArc WEV#()", "ComArc AMP="]

COMARC_WEAVING_FILE_NUMBER = "ArcWeldingWeaveOnCmd" # use existing attribute for "ComArcWeavingFileNumber"
COMARC_AMPLITUDE = "ComArcAmplitude"
COMARC_FREQUENCY = "ComArcFrequency"
COMARC_USE_ANGLE = "ComArcUseAngle"
COMARC_ANGLE = "ComArcAngle"
# COMARC_USE_WEAVING_DIRECTION = "ComArcUseWeavingDirection"
COMARC_WEAVING_DIRECTION = "ComArcWeavingDirection"
COMARC_WEAVING_DIRECTIONS = ["Unused", "0" , "1"]
COMARC_CORRECTION_UP_DOWN = "ComArcCorrectionUpDown"
COMARC_CORRECTION_RIGHT_LEFT = "ComArcCorrectionRightLeft"
COMARC_USE_CONDITION_FILE = "ComArcUseConditionFile"
COMARC_CONDITION_FILE_NUMBER = "ComArcConditionFileNumber"

INT_MAX = 2**31 - 1
TC_DOUBLE_MAX = 1e15


def GetPythonTechnologyVersion():
   return 2
# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator : CENPyOlpTech_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   controller = Operator.GetController()
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return
      
   '''
   wireDiamAttr = attribCreator.AddDouble(AW_TOUCHSENS_WIRE_DIAM, 0.001, 0.0, TC_DOUBLE_MAX, 0.0001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_WIRE_DIAM) 
   if (wireDiamAttr):
      wireDiamAttr.SetVisibility(True) 
      wireDiamAttr.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   '''

   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
# -------------------------------------------------------------------------------------------

   att2 = attribCreator.AddInteger(AW_PROG_NUMBER2_DEFINE, 99, -1, 999, USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_PROG_NUMBER2_DEFINE)
   att2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att3 = attribCreator.AddInteger(AW_WEAVE_ON_CMD, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_ON_CMD)
   att3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att4 = attribCreator.AddEnum(AW_PS_MANUFACTURER, AW_PS_MANUFACTURER_LIST,AW_PS_MANUFACTURER_LIST[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_PS_MANUFACTURER)
   att4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att5 = attribCreator.AddEnum(AW_TORCH_TYPE, AW_TORCH_TYPE_LIST,AW_TORCH_TYPE_LIST[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TORCH_TYPE)
   att5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att6 = attribCreator.AddBool(AW_ARC_OFF_CRATER_FILL, False, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE, AW_ARC_OFF_CRATER_FILL)
   att6.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att7 = attribCreator.AddDouble(AW_ARC_OFF_CRATER_FILL_DELAY, 0.3, 0, 10, 0.1, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE, ATTRIB_STANDARD, AW_ARC_OFF_CRATER_FILL_DELAY)
   att7.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)   

   att10 = attribCreator.AddInteger(AW_SENSING_PORT, 4, 0, 6, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_SENSING_PORT)
   att10.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
  
   att12 = attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 20, 1, MAX_INTEGER, PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   att12.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   attConnectionType = attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE)
   attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
   attConnectionType.SetVisibility(False)
   # attConnectionType.AddLiteral("Frame3pConnect") # Not yet implemented for Yaskawa 

   attCA1 = attribCreator.AddEnum(AW_WEAVE_METHOD, AW_WEAVE_METHODS, AW_WEAVE_METHODS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_METHOD)
   attCA1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA2 = attribGetter.GetAttributeByName(COMARC_WEAVING_FILE_NUMBER)
   attCA2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA3 = attribCreator.AddDouble(COMARC_AMPLITUDE, 20, 0.1, 99.9, 5, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_AMPLITUDE)
   attCA3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA4 = attribCreator.AddDouble(COMARC_FREQUENCY, 2, 0.1, 5, 0.2, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_FREQUENCY)
   attCA4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA5 = attribCreator.AddBool(COMARC_USE_ANGLE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_USE_ANGLE)
   attCA5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA6 = attribCreator.AddDouble(COMARC_ANGLE, 45, 0, 180, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_ANGLE)
   attCA6.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA7 = attribCreator.AddEnum(COMARC_WEAVING_DIRECTION, COMARC_WEAVING_DIRECTIONS, COMARC_WEAVING_DIRECTIONS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_WEAVING_DIRECTION)
   attCA7.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA8 = attribCreator.AddInteger(COMARC_CORRECTION_UP_DOWN, 1, 1, 128, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_CORRECTION_UP_DOWN)
   attCA8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   attCA9 = attribCreator.AddDouble(COMARC_CORRECTION_RIGHT_LEFT, 0, -255, 255, 20, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_CORRECTION_RIGHT_LEFT)
   attCA9.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA10 = attribCreator.AddBool(COMARC_USE_CONDITION_FILE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_USE_CONDITION_FILE)
   attCA10.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attCA11 = attribCreator.AddInteger(COMARC_CONDITION_FILE_NUMBER, 0, 0, 128, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_CONDITION_FILE_NUMBER)
   attCA11.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # HideShowAttributes(attribGetter)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator : CENPyOlpTech_UpdateOperator):
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
   if (lastVersion < 1):      
      att2 = attribCreator.AddInteger(AW_PROG_NUMBER2_DEFINE, 99, -1, 999, USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_PROG_NUMBER2_DEFINE)
      att2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att3 = attribCreator.AddInteger(AW_WEAVE_ON_CMD, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_ON_CMD)
      att3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att4 = attribCreator.AddEnum(AW_PS_MANUFACTURER, AW_PS_MANUFACTURER_LIST,AW_PS_MANUFACTURER_LIST[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE , AW_PS_MANUFACTURER)
      att4.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att5 = attribCreator.AddEnum(AW_TORCH_TYPE, AW_TORCH_TYPE_LIST,AW_TORCH_TYPE_LIST[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TORCH_TYPE)
      att5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att6 = attribCreator.AddBool(AW_ARC_OFF_CRATER_FILL, False, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE, AW_ARC_OFF_CRATER_FILL)
      att6.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att7 = attribCreator.AddDouble(AW_ARC_OFF_CRATER_FILL_DELAY, 0.3, 0, 10, 0.1, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE, ATTRIB_STANDARD, AW_ARC_OFF_CRATER_FILL_DELAY)
      att7.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)      
      
   if (lastVersion < 2): 
      program = Operator.GetOlpProgram()      
      # attribGetter = Operator.GetAttribGetter(program)
      RemoveAttribute(Operator,program,'ArcWeldingGlobalPortTouch')
      RemoveAttribute(Operator,program,'ArcWeldingGlobalPortLaser')
      RemoveAttribute(Operator,program,'ArcWeldingStationNr')

      att10 = attribCreator.AddInteger(AW_SENSING_PORT, 4, 0, 6, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_SENSING_PORT)
      att10.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      attCA1 = attribCreator.AddEnum(AW_WEAVE_METHOD, AW_WEAVE_METHODS, AW_WEAVE_METHODS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_METHOD)
      attCA1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA2 = attribGetter.GetAttributeByName(COMARC_WEAVING_FILE_NUMBER)
      attCA2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA3 = attribCreator.AddDouble(COMARC_AMPLITUDE, 20, 0.1, 99.9, 5, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_AMPLITUDE)
      attCA3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA4 = attribCreator.AddDouble(COMARC_FREQUENCY, 2, 0.1, 5, 0.2, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_FREQUENCY)
      attCA4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA5 = attribCreator.AddBool(COMARC_USE_ANGLE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_USE_ANGLE)
      attCA5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA6 = attribCreator.AddDouble(COMARC_ANGLE, 45, 0, 180, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_ANGLE)
      attCA6.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA7 = attribCreator.AddEnum(COMARC_WEAVING_DIRECTION, COMARC_WEAVING_DIRECTIONS, COMARC_WEAVING_DIRECTIONS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_WEAVING_DIRECTION)
      attCA7.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA8 = attribCreator.AddInteger(COMARC_CORRECTION_UP_DOWN, 1, 1, 128, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_CORRECTION_UP_DOWN)
      attCA8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)      
      attCA9 = attribCreator.AddDouble(COMARC_CORRECTION_RIGHT_LEFT, 0, -255, 255, 20, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_STANDARD, COMARC_CORRECTION_RIGHT_LEFT)
      attCA9.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA10 = attribCreator.AddBool(COMARC_USE_CONDITION_FILE, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_USE_CONDITION_FILE)
      attCA10.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      attCA11 = attribCreator.AddInteger(COMARC_CONDITION_FILE_NUMBER, 0, 0, 128, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | GLOBAL_ATTRIBUTE, COMARC_CONDITION_FILE_NUMBER)
      attCA11.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      # WorkMethod Attributes
      RemoveAttribute(Operator,program,'SSSensingLength')
      RemoveAttribute(Operator,program,'SSOvertravelLength')
      RemoveAttribute(Operator,program,'SSAngleForSideTouch')
      RemoveAttribute(Operator,program,'SSOtherSideTouch')
      RemoveAttribute(Operator,program,'SSLocationAtEnd')
      RemoveAttribute(Operator,program,'SSContourTpeUUID')
      RemoveAttribute(Operator,program,'SSCycleExplode')
      RemoveAttribute(Operator,program,'SSCycleExplodeAvailability')
      RemoveAttribute(Operator,program,'UseWeaveDefine')
      
   completeRecomputeNeeded = True   

   return completeRecomputeNeeded


# -------------------------------------------------------------------------------------------
def PostTechOnAttribChanged(Operator : CENPyOlpTech_AttribChangedOperator):
# get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()
   attribName = changedAttrib.GetName()
   #logging.LogInfo('..................PostTechOnAttribChanged with Attribute =' + str(attribName))
   
   # Show/hide weaving options
   if (attribName == AW_ARC_OFF_CRATER_FILL):
      arcOffCraterFillAttrib = attribGetter.GetAttributeBoolByName(AW_ARC_OFF_CRATER_FILL)
      if arcOffCraterFillAttrib.IsValid():
         #logging.LogInfo('..................found Attribute AW_ARC_OFF_CRATER_FILL=' + str(arcOffCraterFillAttrib))
         craterMode = attribGetter.GetBool(AW_ARC_OFF_CRATER_FILL)
         #logging.LogInfo('...............................Value AW_ARC_OFF_CRATER_FILL=' + str(craterMode))
         craterFillDelay = attribGetter.GetAttributeByName(AW_ARC_OFF_CRATER_FILL_DELAY)
         if craterFillDelay.IsValid():
            #logging.LogInfo('...............................AW_ARC_OFF_CRATER_FILL_DELAY SetVisibility=' + str(craterMode))
            craterFillDelay.SetVisibility(craterMode)
   
   
   if (attribName == AW_WEAVE_METHOD) or (attribName == COMARC_USE_ANGLE) or (attribName == COMARC_USE_CONDITION_FILE):
      HideShowAttributes(attribGetter)    
   

# -------------------------------------------------------------------------------------------
# Technology post event initialization
def PostTechInitEvents(Operator : CENPyOlpTech_EventInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)
   return 1

# -------------------------------------------------------------------------------------------
# Technology post event rule initialization
def PostTechInitRules(Operator : CENPyOlpTech_RuleInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)
   return 1

# -------------------------------------------------------------------------------------------
# Technology post manufacturing geometry initialization
# def PostInitManufacturingGeometry(Operator : CENPyOlpTech_MfGeoInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_END)


# -------------------------------------------------------------------------------------------
# Technology PrevExecuteRecipe
# def PrevExecuteRecipe(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)

   
# -------------------------------------------------------------------------------------------
# Technology post process operation group attributes
# def PostProcessOperationGroupAttributes(Operator : CENPyOlpTech_POGAttribOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Technology post on frame change
# def PostTechOnFrameChanged(Operator : CENPyOlpFrameChangedOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
#    # attribGetter = Operator.GetAttribGetter()
#    # attribSetter = Operator.GetAttribSetter()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


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


def HideShowAttributes(attribGetter):
   WeaveMethodEnum = attribGetter.GetAttributeEnumByName(AW_WEAVE_METHOD)

   attribGetter.GetAttributeByName(COMARC_WEAVING_FILE_NUMBER).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_AMPLITUDE).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_FREQUENCY).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_USE_ANGLE).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_ANGLE).SetVisibility(False)
   # attribGetter.GetAttributeByName(COMARC_USE_WEAVING_DIRECTION).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_WEAVING_DIRECTION).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_CORRECTION_UP_DOWN).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_CORRECTION_RIGHT_LEFT).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_USE_CONDITION_FILE).SetVisibility(False)
   attribGetter.GetAttributeByName(COMARC_CONDITION_FILE_NUMBER).SetVisibility(False)

   WeaveMethod = WeaveMethodEnum.GetValue()

   if WeaveMethod == AW_WEAVE_METHODS[0]: # No Weaving
      pass

   if WeaveMethod == AW_WEAVE_METHODS[1]: # WEV#()                   
      attribGetter.GetAttributeByName(COMARC_WEAVING_FILE_NUMBER).SetVisibility(True)

   if WeaveMethod == AW_WEAVE_METHODS[2] or WeaveMethod == AW_WEAVE_METHODS[3]: # ComArc attributes
      
      # attribGetter.GetAttributeByName(COMARC_USE_WEAVING_DIRECTION).SetVisibility(True)
      attribGetter.GetAttributeByName(COMARC_USE_CONDITION_FILE).SetVisibility(True)
      attribGetter.GetAttributeByName(COMARC_CORRECTION_UP_DOWN).SetVisibility(True)
      attribGetter.GetAttributeByName(COMARC_CORRECTION_RIGHT_LEFT).SetVisibility(True)

      if attribGetter.GetBool(COMARC_USE_CONDITION_FILE) == True:               
         attribGetter.GetAttributeByName(COMARC_CONDITION_FILE_NUMBER).SetVisibility(True)
      # if attribGetter.GetBool(COMARC_USE_WEAVING_DIRECTION) == True:
      attribGetter.GetAttributeByName(COMARC_WEAVING_DIRECTION).SetVisibility(True)          

   if WeaveMethod == AW_WEAVE_METHODS[2]: # ComArc WEV#()
      attribGetter.GetAttributeByName(COMARC_WEAVING_FILE_NUMBER).SetVisibility(True)

   if WeaveMethod == AW_WEAVE_METHODS[3]: # ComArc AMP=
      attribGetter.GetAttributeByName(COMARC_AMPLITUDE).SetVisibility(True)
      attribGetter.GetAttributeByName(COMARC_FREQUENCY).SetVisibility(True)         
      attribGetter.GetAttributeByName(COMARC_USE_ANGLE).SetVisibility(True)
      if attribGetter.GetBool(COMARC_USE_ANGLE) == True:
         attribGetter.GetAttributeByName(COMARC_ANGLE).SetVisibility(True) 
