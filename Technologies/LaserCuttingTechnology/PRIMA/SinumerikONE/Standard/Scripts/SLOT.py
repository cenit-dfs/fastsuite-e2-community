from centypes import *
from cenpylib import *
import sys, os, inspect
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "SLOT.py: "

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   attribCreator = Operator.GetAttribCreator()
   att1 = attribCreator.AddDouble('RegshapeRotOffsetRz', 0, -180, 180, 1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE, ATTRIB_ANGLE, 'Sys_Att_RotationRz')
   att1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att2 = attribCreator.AddDouble('RegshapeRotOffsetRy', 0, -180, 180, 1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE, ATTRIB_ANGLE, 'Sys_Att_RotationRy')
   att2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att3 = attribCreator.AddDouble('RegshapeRotOffsetRx', 0, -180, 180, 1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | OPERATION_ATTRIBUTE, ATTRIB_ANGLE, 'Sys_Att_RotationRx')
   att3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
# -------------------------------------------------------------------------------------------
def PostProcessAttributes(Operator:CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   attribGetter = Operator.GetAttribGetter()
   offsetRz = attribGetter.GetDouble('RegshapeRotOffsetRz')
   offsetRy = attribGetter.GetDouble('RegshapeRotOffsetRy')
   offsetRx = attribGetter.GetDouble('RegshapeRotOffsetRx')

# -------------------------------------------------------------------------------------------
# post event compute 
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()

# EventName must be the same as the event you wanna overright
# Recommendation: Use EventName also as file name
def GetEventName():
   return "SLOT"

def GetEventUuId():
   return "B751B56D-DAEF-45C6-A614-7183DFB445DB"
   
def GetIconName():
   return "Slot"

# Create unexploded regshape; exploding is possible
def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEALLOWED

# -------------------------------------------------------------------------------------------
# Definitions for regshapes (Dont modify)
def GetMultipleCreationIsPossible():
   return 1

def GetEventType():
   return OLPEVENT_PROCESS

# Auto translate of whole cycle
def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

# Manual translate of whole cycle
def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

# Auto rotation of cycle
def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTPATHTOOL

# Manual rotation around tool
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTPATHTOOL

# Set cycle as teachable
def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_TEACHABLE
   
def IsMachiningCycle():
   return 1

def GetGroupName():
   return "RegShapeEvent"
