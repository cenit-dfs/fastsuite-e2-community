from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "StitchWeldingWorkMethod.py: "

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

# Laser Tracking on/off
AW_SEAMTRACKING_ONOFF = "SeamTrackingOnOff"
AW_SEAMTRACKING_DISTANCE = "SeamTrackingDistance"
AW_SEAMTRACKING_OFF_EVENT_ACTIVE = "SeamTrackingOffEventActive"

def PostWmInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   attribCreator = Operator.GetAttribCreator()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # set all linear flyby attribs maximum to 100mm AKA %
   flyByLinMax = 0.1 # m=100mm=100%
   fb1 = attribGetter.GetAttributeDoubleByName("FlybyWelding")
   if fb1.IsValid():
      fb1.SetMinimum(0.0)
      fb1.SetMaximum(flyByLinMax)
      fb1.SetValue(0.002)
   #fb3 = attribGetter.GetAttributeDoubleByName("FlybyRetract")
   #if fb3.IsValid():
   #   fb3.SetMinimum(0.0)
   #   fb3.SetMaximum(flyByLinMax)
   #   fb3.SetValue(0.002)


   # Make seam tracking on/off Global, Process and User
   attSeamTrackingOnOff = attribCreator.AddBool(AW_SEAMTRACKING_ONOFF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_SEAMTRACKING_ONOFF)
   # attSeamTrackingOnOff = attribGetter.GetAttributeByName(AW_SEAMTRACKING_ONOFF)
   # attSeamTrackingOnOff.SetOlpProperty(PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE)
   attSeamTrackingOnOff.SetVisibility(True)

   seamTrackingDistance = attribGetter.GetAttributeByName(AW_SEAMTRACKING_DISTANCE)
   seamTrackingDistance.SetOlpProperty(GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE)

   seamTrackingOffEventActive = attribGetter.GetAttributeByName(AW_SEAMTRACKING_OFF_EVENT_ACTIVE)
   seamTrackingOffEventActive.SetVisibility(False)
   seamTrackingOffEventActive.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   seamTrackingOffEventActive.SetOlpProperty(GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE)

   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

   pass 

def PostWmInitEvents(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   # Add circle regshape event (Your python file)
   Operator.RegisterPyTechnologyEvent('SkipPrcPtEvent.py')
   Operator.RegisterPyTechnologyEvent('SeamTrackingLeadInEvent.py')
   Operator.RegisterPyTechnologyEvent('SeamTrackingZJEvent.py')
   Operator.RegisterPyTechnologyEvent('SeamTrackerOffEvent.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  SkipPrcPtEvent ')
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)

def PostWmInitRules(Operator):
     Operator.AddPyEvent('RuleAfterRetract', 'SeamTrackerOffEvent')
     Operator.SetActivePyEvent('RuleAfterRetract', 'SeamTrackerOffEvent')
   # pass

def PostWmOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   pass
   
def PostWmSyncPgAttributes(Operator):
   pass
   
def PostProcessOperationAttributes(Operator):
   pass
      
