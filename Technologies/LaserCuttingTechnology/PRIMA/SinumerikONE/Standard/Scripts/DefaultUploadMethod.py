from centypes import *
from cenpylib import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "DefaultUploadMethod.py: "

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

def PostWmInitAttributes(Operator : CENPyOlpWM_AttribInitOperator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribCreator = Operator.GetAttribCreator()
   attribGetter = Operator.GetAttribGetter()
   #attribSetter = Operator.GetAttribSetter()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # set all linear flyby attribs maximum to 100mm AKA %
   flyByLinMax = 0.1 # m=100mm=100%
   fb2 = attribGetter.GetAttributeDoubleByName("LinkFlybySW")
   #fb2.SetMinimum(0)
   #fb2.SetMaximum(flyByLinMax)
   #fb2.SetValue(0.055)
   fb3 = attribGetter.GetAttributeDoubleByName("FlybyRetract")
   #fb3.SetMinimum(0)
   #fb3.SetMaximum(flyByLinMax)
   #fb3.SetValue(0.033)

   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

   pass 

def PostWmInitEvents(Operator : CENPyOlpWM_EventInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   # Add circle regshape event (Your python file)
   Operator.RegisterPyTechnologyEvent('CIRCLE.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  CIRCLE ')
   Operator.RegisterPyTechnologyEvent('HEXAGON.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  HEXAGON ')
   Operator.RegisterPyTechnologyEvent('KEYHOLE.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  KEYHOLE ')
   Operator.RegisterPyTechnologyEvent('RECTANGLE.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  RECTANGLE ')
   Operator.RegisterPyTechnologyEvent('SLOT.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  SLOT ')
   Operator.RegisterPyTechnologyEvent('UniApproachLinLin.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  UniApproachLinLin ')
   Operator.RegisterPyTechnologyEvent('UploadFlags.py')
   logging.LogDebug(FILE_NAME + '............................................................RegisterPyTechnologyEvent  :  UploadFlags ')

   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)

def PostWmInitRules(Operator : CENPyOlpWM_RuleInitOperator):
   # Remove default E2 regshape circle event
   # Operator.RemoveEventFromRule('RegshapeRule', 'CIRCLE')
   # Operator.RemoveEventFromRule('RegshapeRule', 'SLOT')
   # Operator.RemoveEventFromRule('RegshapeRule', 'RECTANGLE')

   # Add your regshape event by UUID (See in your event definition)
   # Operator.AddPyEventByUUID('RegshapeRule', 'C2520F42-9369-449B-A4BC-645D02BA23E6')
   pass

def PostWmOnAttribChanged(Operator : CENPyOlpWM_AttribChangedOperator):
   pass
   
def PostWmSyncPgAttributes(Operator : CENPyOlpWM_SyncPgAttribOperator):
   pass
   
def PostProcessOperationAttributes(Operator : CENPyOlpWM_POAttribOperator):
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   pass
      
