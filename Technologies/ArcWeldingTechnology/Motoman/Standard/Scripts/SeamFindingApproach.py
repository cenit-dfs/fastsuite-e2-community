# -------------------------------------------------------------------------------------------
# Name: Generic Approach & Retract
# Description: this Python file adjust basic implementation for Yaskawa specific installation 
# Debug info: E2@localhost:5254
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Cenit AG
#        Date: July 2024
#     
# -------------------------------------------------------------------------------------------

import sys
sys.dont_write_bytecode = True
from centypes import *
from cenpylib import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "ApproachOnePoint.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."


# Operation attribute definition
APPROACH_MOTION_TYPE = "SFApproachMotionType"
APPROACH_MOTION_TYPE_LITERAL = ["PTP", "LIN"]

APP_DISTANCE_X="ApproachOnePointDistanceX"
APP_DISTANCE_Y="ApproachOnePointDistanceY"
APP_DISTANCE_Z="ApproachOnePointDistanceZ"

   
# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator : CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   attribCreator = Operator.GetAttribCreator()
   
   # set Motion Type to Approach Point
   motionType = attribCreator.AddEnum(APPROACH_MOTION_TYPE, APPROACH_MOTION_TYPE_LITERAL, APPROACH_MOTION_TYPE_LITERAL[0], USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE, APPROACH_MOTION_TYPE)
   motionType.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Default values for second point (X1,Y1,Z1)
   apprZ=attribCreator.AddDouble(APP_DISTANCE_Z,0.100,-1.0,1.0, 0.005, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, APP_DISTANCE_Z)
   apprZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass

   
def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   pass

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # !!! get SeamFinding operator !!!
   sfOperator = Operator.GetSeamFindingOperator()
   # get event operator
   eventOperator = Operator.GetEventOperator()
   # debug logging: post compute
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   
   # get motion type
   motionType = attribGetter.GetEnumIndex(APPROACH_MOTION_TYPE)
   
   # get SeamFinding Attributes to place Approach on Startpoint
   atEndLocation = attribGetter.GetBool(AW_SEAMFIND_END_LOCATION)
   optionalDir = attribGetter.GetBool(AW_SEAMFIND_OPTIONAL_DIR)
   seamFindDistance = attribGetter.GetDouble(AW_SEAMFIND_DISTANCE)
   
   # get the Point Matrixes from SeamFindingOperator
   sfStartPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   # get offsets
   LX1 = 0.0
   LY1 = 0.0
   LZ1 = attribGetter.GetDouble(APP_DISTANCE_Z)

   # place the AR Point RotX:RotPathTool / RotY&Z:RotTool
   sfARMatrix = sfOperator.SeamFindingApproachRetractPoint(sfStartPointMatrix, LX1, LY1, LZ1)
   
   if (sfStartPointMatrix):
      # got the Event Point -> AR-Point
      if motionType == 1:
         tpElementStart = Operator.MoveLin(sfARMatrix)
      else:
         tpElementStart = Operator.MovePTP(sfARMatrix)
   else:
      # Alternative Actions
      startM = Operator.GetRefTpElement().GetInitialPathMatrix()
      startM.Translate(0.0, 0.0, LZ1, True)
      # to the StartPoint
      if motionType == 1:
         tpElementStart = Operator.MoveLin(startM)
      else:
         tpElementStart = Operator.MovePTP(startM)
      
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
   pass

def GetEventName():
   return "SeamFindingApproach"
   
def GetEventUuId():
   return "924C497B-D012-45A4-97A7-A76086850E58"
   
def GetIconName():
   return "ToolpathApproach"
   
def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY   
   
def GetMultipleCreationIsPossible():
   return 1
   
def GetEventType():
   return OLPEVENT_APPROACH

def GetCycleTranslationFlag():
   return CYCLETRANSLATION_TRANSNO

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSNO

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSNO

def GetCycleRotationFlag():
   return CYCLEROTATION_ROTTOOL

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTTOOL

def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTTOOL
   
def IsMachiningCycle():
   return False

def GetGroupName():
   return "TpdbIgnore"
   
def IsEnabled():
   return False