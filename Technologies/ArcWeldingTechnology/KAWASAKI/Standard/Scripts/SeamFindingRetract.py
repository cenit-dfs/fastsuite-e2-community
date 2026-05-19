# -------------------------------------------------------------------------------------------
# Name: Generic Approach & Retract
# Description: 
# Debug info: E2@localhost:5254
# Author:  Cenit DFS
# Changelog:
#     Version: 1.0
#        Changed by:
#        Date: 
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "RetractOnePoint.py: "

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

# Operation attribute definition
RET_DISTANCE_X="RetractOnePointDistanceX"
RET_DISTANCE_Y="RetractOnePointDistanceY"
RET_DISTANCE_Z="RetractOnePointDistanceZ"

AW_SEAMFIND_END_LOCATION = "SeamFindingEndLocation"
AW_SEAMFIND_OPTIONAL_DIR = "SeamFindingOptionalDirection"
AW_SEAMFIND_DISTANCE = "SeamFindingDistance"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   attribCreator = Operator.GetAttribCreator()

   # Default values for second point (X1,Y1,Z1)   
   retrX=attribCreator.AddDouble(RET_DISTANCE_X,-0.020,-1.0,1.0, 0.005, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, RET_DISTANCE_X)
   retrX.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   retrZ=attribCreator.AddDouble(RET_DISTANCE_Z,0.05,-1.0,1.0, 0.005, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, RET_DISTANCE_Z)
   retrZ.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass

   
def PostProcessAttributes(CENPyOlpEvent_PEOperator):
   pass

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator):
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

   # get SeamFinding Attributes to place Approach on Startpoint
   atEndLocation = attribGetter.GetBool(AW_SEAMFIND_END_LOCATION)
   optionalDir = attribGetter.GetBool(AW_SEAMFIND_OPTIONAL_DIR)
   # seamFindDistance = attribGetter.GetDouble(AW_SEAMFIND_DISTANCE)
   seamFindDistance = 0.0   # Retract stated at Reference Point (can be minus for overtravel)
   
   # get the Point Matrixes from SeamFindingOperator
   sfStartPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   
   # get offsets : at EndPos retract in Z(tool), at StartPos retract in X(tangent)
   LY1 = 0.0
   if atEndLocation == True:
      LX1 = 0.0
      LZ1 = attribGetter.GetDouble(RET_DISTANCE_Z)
   else:
      LX1 = attribGetter.GetDouble(RET_DISTANCE_X)
      LZ1 = 0.0
   
   # place the AR Point RotX:RotPathTool / RotY&Z:RotTool
   sfARMatrix = sfOperator.SeamFindingApproachRetractPoint(sfStartPointMatrix, LX1, LY1, LZ1)
   
   if (sfARMatrix):
      # got the Event Point -> AR-Point
      tpElementStart = Operator.MoveLin(sfARMatrix)
   else:
      # Alternative Actions
      startM = Operator.GetRefTpElement().GetInitialPathMatrix()
      startM.Translate(LX1, LY1, LZ1, True)
      # to the StartPoint
      tpElementStart = Operator.MoveLin(startM)
   
   # set global Welding Speed here, bec. followed Welding Operation has no ApproachEvent to set.
   if atEndLocation == False:
      weldingSpeed = attribGetter.GetDouble("Speed")
      weldingSpeedEvent=eventOperator.AddSpeed(tpElementStart,TPINSERTPOS_INSERTAFTER)
      weldingSpeedEvent.SetSpeed(weldingSpeed)
   
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
   pass

def GetEventName():
   return "SeamFindingRetract"
   
def GetEventUuId():
   return "4AE6B187-515D-4DFE-8CF6-F26DF816F685"
   
def GetIconName():
   return "ToolpathRetract"
   
def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY   
   
def GetMultipleCreationIsPossible():
   return 1
   
def GetEventType():
   return OLPEVENT_RETRACT

def GetCycleTranslationFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

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