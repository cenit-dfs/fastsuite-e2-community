# Name: RegshapeCycleTimeDelayCalculation
# Description: Adds cycle time delay on specific events
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Cenit AG
#        Date: december 2024
#     
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
# -------------------------------------------------------------------------------------------

FILE_NAME = "CycleTimeDelayCalculation.py: "
DEBUG_INIT_CYCLE_TIME_CALCULATION_START = "(Debug) initialization of CycleTimeDelayCalculation started."
DEBUG_INIT_CYCLE_TIME_CALCULATION_END = "(Debug) initialization of CycleTimeDelayCalculation ended."
# Cycle time delay attributes
# general global definitions.
ATTR_EVT_ACCURACY_OFF_CYCLE_TIME_DELAY = "Sequence_Cycle_Time_Delay_AccuracyOff"
# Event Attributes
ATTR_OLP_EVT_CYCLE_TIME_DELAY = "CycleTimeDelay"
# Event Attributes Regshape
ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY = "RegshapeCycleTimeDelay"
# -------------------------------------------------------------------------------------------

# Event Regshape Names
RECTANGLE = "RECTANGLE"
CIRCLE = "CIRCLE"
HEXAGON = "HEXAGON"
SLOT = "SLOT"
KEYHOLE = "KEYHOLE"

# Event Attributes Regshape Names
LENGTH = "Length"
WIDTH = "Width"
RADIUS = "Radius"
SMOOTH = "SMOOTH"
   
# OLP Events Names
ATTR_EVT_LASER_ON_NAME = "LaserOn"
ATTR_EVT_LASER_OFF_NAME = "LaserOff"

# Operation attributes
ATTR_OPERATION_MATERIAL = "Material"
ATTR_OPERATION_MATERIAL_INDEX = "MaterialIndex"
ATTR_OPERATION_THICKNESS = "Thickness"
# -------------------------------------------------------------------------------------------


def ModifyActiveProgram(Operator):
   activeProgram = Operator.GetActiveProgram()
   eventHandler  = Operator.GetEventHandler()
   operations = activeProgram.GetOperations()  
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: start of calculation
   logging.LogDebug(FILE_NAME + DEBUG_INIT_CYCLE_TIME_CALCULATION_START)

   for operation in operations:
      # handle the OLPEvents attributes 
      #handleOlpEventsAttributes(operation, eventHandler, logging)
      # handle the Operation Global attributes 
      handleOperationGlobalAttributes(operation, logging)   
      additionalAttributes = getAdditionalAttributes(operation)           
      activeEventRules = operation.GetActiveEventRules()
      for eventRule in activeEventRules:
         handleRegularShapeAttributes(eventRule,additionalAttributes, logging)
      
   # debug logging: end of calculation
   logging.LogDebug(FILE_NAME + DEBUG_INIT_CYCLE_TIME_CALCULATION_END)
                  
         
# method to handle the OLPEvents delay attributes
def handleOperationGlobalAttributes(operation, logging):  
   attribGetter = operation.GetAttribGetter()
   if attribGetter:
      accuracyOffAttribute = attribGetter.GetAttributeByName(ATTR_EVT_ACCURACY_OFF_CYCLE_TIME_DELAY)
      if accuracyOffAttribute.IsValid():
         # get setter
         attribSetter = operation.GetAttribSetter()
         attribSetter.SetDouble(ATTR_EVT_ACCURACY_OFF_CYCLE_TIME_DELAY, 1.0)         
         
# method to handle the OLPEvents delay attributes
def handleOlpEventsAttributes(operation, eventHandler, logging):     
   #laserOn
   tpElementsWithEvent = operation.GetTpElementsWithEvent(ATTR_EVT_LASER_ON_NAME)
   for tpElement in tpElementsWithEvent:
      events = eventHandler.GetEventsByName(tpElement, ATTR_EVT_LASER_ON_NAME)
      for event in events:           
         isAttributeValid = event.IsAttributeValid(ATTR_OLP_EVT_CYCLE_TIME_DELAY)
         if isAttributeValid:
            event.SetDouble(ATTR_OLP_EVT_CYCLE_TIME_DELAY, 0.0)
         else:            
            logging.LogError(ATTR_OLP_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + ATTR_EVT_LASER_ON_NAME + ", please create in technology script")   
   #laserOff
   tpElementsWithEvent = operation.GetTpElementsWithEvent(ATTR_EVT_LASER_OFF_NAME)
   for tpElement in tpElementsWithEvent:
      events = eventHandler.GetEventsByName(tpElement, ATTR_EVT_LASER_OFF_NAME)
      for event in events:
         isAttributeValid = event.IsAttributeValid(ATTR_OLP_EVT_CYCLE_TIME_DELAY)
         if isAttributeValid:
            event.SetDouble(ATTR_OLP_EVT_CYCLE_TIME_DELAY, 0.0)
         else:            
            logging.LogError(ATTR_OLP_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + ATTR_EVT_LASER_OFF_NAME + ", please create in technology script") 

# method to gather additional attributes needed for cycle time delay
def getAdditionalAttributes(operation):
   additionalAttributes = {}
   attribGetter = operation.GetAttribGetter()
   if attribGetter:
      materialIndexAttribute = attribGetter.GetAttributeByName(ATTR_OPERATION_MATERIAL_INDEX)
      if materialIndexAttribute.IsValid():
         additionalAttributes[ATTR_OPERATION_MATERIAL_INDEX] = attribGetter.GetDouble(ATTR_OPERATION_MATERIAL_INDEX)
      materialAttribute = attribGetter.GetAttributeByName(ATTR_OPERATION_MATERIAL)
      if materialAttribute.IsValid():
         additionalAttributes[ATTR_OPERATION_MATERIAL] = attribGetter.GetString(ATTR_OPERATION_MATERIAL)
      thicknessAttribute = attribGetter.GetAttributeByName(ATTR_OPERATION_THICKNESS)
      if thicknessAttribute.IsValid():
         additionalAttributes[ATTR_OPERATION_THICKNESS] = attribGetter.GetDouble(ATTR_OPERATION_THICKNESS)
   return additionalAttributes

# method to handle the regshape active event delay attributes
def handleRegularShapeAttributes(eventRule, additionalAttributes, logging):
   eventName = eventRule.GetOlpEventName()
   if eventName == RECTANGLE:
      rectangleRegShape(eventRule,additionalAttributes, logging)
   if eventName == CIRCLE:
      circleRegShape(eventRule,additionalAttributes, logging)
   if eventName == HEXAGON:
      hexagonRegShape(eventRule,additionalAttributes, logging)
   if eventName == SLOT:
      slotRegShape(eventRule,additionalAttributes, logging)
   if eventName == KEYHOLE:
      keyHoleRegShape(eventRule,additionalAttributes, logging)
   
# method to handle rectangle event
def rectangleRegShape(eventRule,additionalAttributes, logging):
   length = eventRule.GetDouble(LENGTH)
   width = eventRule.GetDouble(WIDTH)
   radius = eventRule.GetDouble(RADIUS)
   material = additionalAttributes[ATTR_OPERATION_MATERIAL]
   thickness = additionalAttributes[ATTR_OPERATION_THICKNESS]
   #if(material == "ANREISSEN"):
      #if(thickness == 0.001):
         #eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 1)   
   isAttributeValid = eventRule.IsAttributeValid(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
   if isAttributeValid:
      cycleTime = eventRule.GetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
      eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 0.0)
   else:            
      logging.LogError(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + RECTANGLE + ", please create in technology script") 

# method to handle circle event
def circleRegShape(eventRule, additionalAttributes, logging):
   smooth = eventRule.GetDouble(SMOOTH)
   radius = eventRule.GetDouble(RADIUS)
   isAttributeValid = eventRule.IsAttributeValid(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
   if isAttributeValid:
      cycleTime = eventRule.GetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
      eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 0.0)
   else:            
      logging.LogError(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + CIRCLE + ", please create in technology script") 
   
 
# method to handle hexagon event  
def hexagonRegShape(eventRule,additionalAttributes, logging):
   width = eventRule.GetDouble(WIDTH)
   radius = eventRule.GetDouble(RADIUS)   
   isAttributeValid = eventRule.IsAttributeValid(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
   if isAttributeValid:
      cycleTime = eventRule.GetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
      eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 0.0)
   else:            
      logging.LogError(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + HEXAGON + ", please create in technology script") 

# method to handle slot event   
def slotRegShape(eventRule,additionalAttributes, logging):
   length = eventRule.GetDouble(LENGTH)
   radius = eventRule.GetDouble(RADIUS)
   isAttributeValid = eventRule.IsAttributeValid(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
   if isAttributeValid:
      cycleTime = eventRule.GetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
      eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 0.0)
   else:            
      logging.LogError(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + SLOT + ", please create in technology script") 
   
# method to handle keyHole event
def keyHoleRegShape(eventRule,additionalAttributes, logging):
   length = eventRule.GetDouble(LENGTH)
   width = eventRule.GetDouble(WIDTH)
   radius = eventRule.GetDouble(RADIUS)
   isAttributeValid = eventRule.IsAttributeValid(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
   if isAttributeValid:
      cycleTime = eventRule.GetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY)
      eventRule.SetDouble(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY, 0.0)
   else:            
      logging.LogError(ATTR_REGSHAPE_EVT_CYCLE_TIME_DELAY + " attribute does not exist in event " + KEYHOLE + ", please create in technology script")

def GetCommandName():
   return "RegularShapeCycleTimeDelayCalculation"

def GetCommandUuId():
   return "9A5148CD-ED5F-4F40-B4E4-1AADA79E9ED3"

def GetIconName():
   return "Dummy"