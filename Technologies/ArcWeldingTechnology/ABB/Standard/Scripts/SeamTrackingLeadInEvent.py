# -------------------------------------------------------------------------------------------
# Name: Laser SeamTrackingLeadInEvent
# Description: 
# Debug info: E2@localhost:5254
# Author:  Cenit DFS
# Changelog:
#     Version: 1.0
#        Changed by: Berauer
#        Date: 2024-05-17
# -------------------------------------------------------------------------------------------
# Import libraries
import ctypes
from centypes import *
from cenpylib import *
import sys
import math
sys.dont_write_bytecode = True
# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SeamTrackingLeadInEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."


# Operation attribute definition
LEADIN_DISTANCE_X="SeamTrackingDistancePD"
LASER_BASE_OFFSET_Y="0"
LASER_BASE_OFFSET_Y="0"

AW_SEAMFIND_END_LOCATION = "SeamFindingEndLocation"
AW_SEAMFIND_OPTIONAL_DIR = "SeamFindingOptionalDirection"
AW_SEAMFIND_DISTANCE = "SeamFindingDistance"

SEAM_TRACKING_ZJ_EVENT_UUID = '75f08226-eca4-4a46-aa5e-a33a40e7cfb8'
AW_SKIP_PRC_POINT_EVENT_UUID = "30abbd0a-30ca-4ebe-8358-6089f9542492"

AW_LASER_ZJ_ON  = "LaserZjOn"
AW_LASER_ZJ_BASE_POS_Y = "LaserZjBasePositionY"
AW_LASER_ZJ_BASE_POS_Z = "LaserZjBasePositionZ"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   attribCreator = Operator.GetAttribCreator()
   
   # # Default values for second point (X1,Y1,Z1)
   # leadinX=attribCreator.AddDouble(LEADIN_DISTANCE_X,0.100,-1.0,1.0, 0.005, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, LEADIN_DISTANCE_X)
   # leadinX.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass

   
def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   xDir = Operator.GetRefToolpathElementPosition().GetXDirection()
   pass

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
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
   # atEndLocation = attribGetter.GetBool(AW_SEAMFIND_END_LOCATION)
   # optionalDir = attribGetter.GetBool(AW_SEAMFIND_OPTIONAL_DIR)
   # seamFindDistance = attribGetter.GetDouble(AW_SEAMFIND_DISTANCE)
   
   # get the Point Matrixes from SeamFindingOperator
   # sfStartPointMatrix = sfOperator.GetSeamFindingPoint(atEndLocation, optionalDir, seamFindDistance)
   
   startOffset = attribGetter.GetDouble('Sys_Att_StartPoint_ForUI')
   
   # get offsets
   startM = Operator.GetRefTpElement().GetInitialPathMatrix()
   startM.Translate(-startOffset, 0, 0, True)
   # to the StartPoint
   tpElement = Operator.MoveLin(startM)
   if attribGetter.GetBool('SeamTrackSearchStart'):
      eventOperator.AddEvent('bd8ff82e-7043-4390-971e-7a7498ecb145', tpElement, TPINSERTPOS_INSERTBEFORE)

   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
   pass

def GetEventUuId():
   return "3B09592C-0719-48CD-A9AF-0DD3E74A55B9"
   
def GetEventName():
   return "SeamTrackingLeadInEvent"

def IsEnabled():
   return False
