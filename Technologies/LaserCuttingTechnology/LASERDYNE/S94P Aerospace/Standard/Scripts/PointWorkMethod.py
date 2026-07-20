from centypes import *
import math
import inspect, os
import csv

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "PointWorkMethod.py: "

APPROACH_SPEED = "LC_LD_PNT_APPROACH_FEEDRATE"
RETRACT_SPEED = "LC_LD_PNT_RETRACT_FEEDRATE"

def PostWmInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # Attribute
   apprSpeed = attribCreator.AddDouble(APPROACH_SPEED, 0.444,0.001,99.0,0.001, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_SPEED, APPROACH_SPEED)
   apprSpeed.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   # Attribute
   retrSpeed = attribCreator.AddDouble(RETRACT_SPEED, 0.666,0.001,99.0,0.001, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_SPEED, RETRACT_SPEED)
   retrSpeed.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   
def PostWmInitEvents(Operator): 
   logging = Operator.GetLoggerOperator()
   #logging.LogDebug(".................................PointWorkMethod :: PostWmInitEvents")
   Operator.RegisterPyTechnologyEvent('PointApproachTechStartEvent.py')  
   Operator.RegisterPyTechnologyEvent('PointRetractTechEndEvent.py')  
   #logging.LogDebug(".................................PointWorkMethod :: PostWmInitEvents")

def PostWmInitRules(Operator):
   logging = Operator.GetLoggerOperator()
   #logging.LogDebug(".................................PointWorkMethod :: PostWmInitRules")
   #Operator.RemoveEventFromRule('PointRule', 'PointEvent')
   Operator.AddPyEvent('PointApproachTechStartRule', 'PointApproachTechStartEvent')
   Operator.SetActivePyEvent('PointApproachTechStartRule', 'PointApproachTechStartEvent')
   Operator.AddPyEvent('PointRetractTechEndRule', 'PointRetractTechEndEvent')
   Operator.SetActivePyEvent('PointRetractTechEndRule', 'PointRetractTechEndEvent')
   #logging.LogDebug(".................................PointWorkMethod :: PostWmInitRules")
   
def PostWmSyncPgAttributes(Operator):
   pass
   
def PostProcessOperationAttributes(Operator):
   pass
      