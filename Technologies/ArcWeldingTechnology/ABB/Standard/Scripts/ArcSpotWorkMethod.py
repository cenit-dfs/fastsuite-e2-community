from centypes import *
import math
import inspect, os
import csv

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "PointWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug) initialization of manufacturing geometry ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

# Operation attribute definition
# KREIS
MEASURE_DIAMETER = "ABBArcSpotDiameter"
# KREUZBOGEN
MEASURE_TOTALANGLE = "ABBArcAngleRange"
MEASURE_ANGLE1 = "ABBArcAngle1"
# GENERAL
MEASURE_ANGLE = "ABBArcSpotWeldAngle"
MEASURE_SPEED = "ABBArcSpotWeldSpeed"
FLIP_UPDOWN = "ABBArcSpotUpDown"
FLIP_180 = "ABBArcSpotSide"
FLIP_INOUT = "ABBArcSpotInOut"
MARKO_VARIANT = "ABBArcSpotVariant"
MARKO_VARIANT_LIST = ["ABBArcSpotKREIS","ABBArcSpotKREUZBOGEN"]
RESOLUTION = "ABBArcSpotNrPoints"


def PostWmInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   attribCreator = Operator.GetAttribCreator()    
   # Attribute
   att22 = attribCreator.AddDouble(MEASURE_DIAMETER, 0.020, 0.0, 360.0, 1.0, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, MEASURE_DIAMETER)
   att22.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   # Attribute
   att24 = attribCreator.AddDouble(MEASURE_SPEED, 0.100,0.001,99.0,0.001, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_SPEED, MEASURE_SPEED)
   att24.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Attribute
   att26 = attribCreator.AddDouble(MEASURE_ANGLE, 10.0,-180.0,90.0,5.0, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_ANGLE, MEASURE_ANGLE)
   att26.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Attribute
   att28 = attribCreator.AddBool(FLIP_UPDOWN, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, FLIP_UPDOWN)
   att28.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Attribute
   att30 = attribCreator.AddBool(FLIP_180, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, FLIP_180)
   att30.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Attribute
   att32 = attribCreator.AddBool(FLIP_INOUT, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, FLIP_INOUT)
   att32.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # Attribute
   att33 = attribCreator.AddEnum(MARKO_VARIANT, MARKO_VARIANT_LIST,MARKO_VARIANT_LIST[0], OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, MARKO_VARIANT)
   att33.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   # MEASURE_TOTALANGLE
   att34 = attribCreator.AddDouble(MEASURE_TOTALANGLE, 150.0,-180.0,180.0,5.0, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_ANGLE, MEASURE_TOTALANGLE)
   att34.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # MEASURE_ANGLE1
   att36 = attribCreator.AddDouble(MEASURE_ANGLE1, -30.0,-180.0,180.0,5.0, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_ANGLE, MEASURE_ANGLE1)
   att36.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # RESOLUTION
   att38 = attribCreator.AddInteger(RESOLUTION, 7,1,100, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, RESOLUTION)
   att38.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)


def PostWmInitEvents(Operator): 
   Operator.RegisterPyTechnologyEvent('FlexMacro.py')  

def PostWmInitRules(Operator):
   Operator.RemoveEventFromRule('ProcessPointRule', 'ProcessPointEvent')
   Operator.AddPyEvent('ProcessPointRule', 'FlexMacro')
   Operator.SetActivePyEvent('ProcessPointRule', 'FlexMacro')
   #Operator.SetActivePyEvent('RetractRule', 'NoRetract')


   
   
 
def PostWmOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()
   # get controller
   #controller = Operator.GetController()   


def PostWmSyncPgAttributes(Operator):
   pass
   
def PostProcessOperationAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # retrieve the selectd recipe id
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   
   pass
      