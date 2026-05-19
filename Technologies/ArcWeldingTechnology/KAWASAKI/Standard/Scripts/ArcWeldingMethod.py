from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "ArcWeldingMethod.py: "

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
 
def PostWmInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()

   # your code
   pass 

def PostWmInitEvents(Operator):        
   #get logger
   logging = Operator.GetLoggerOperator()

   Operator.RegisterPyTechnologyEvent('LT_Param_Event.py')
   Operator.RegisterPyTechnologyEvent('LT_Event.py')
   Operator.RegisterPyTechnologyEvent('LTOnEvent.py')
   Operator.RegisterPyTechnologyEvent('LTOffEvent.py')
   Operator.RegisterPyTechnologyEvent('LT2PTApproach.py')
   Operator.RegisterPyTechnologyEvent('SPSEvent.py')
   #Operator.RegisterPyTechnologyEvent('TSCorrectEvent.py')
   #Operator.RegisterPyTechnologyEvent('TSCalcApproach.py')
   #pass

def PostWmInitRules(Operator):
   # 2PT Approach
   Operator.AddPyEvent('ApproachRule', 'LT2PTApproach')
   #Operator.AddPyEvent('ApproachRule', 'TSCalcApproach')

   #Set a default
   Operator.SetActivePyEvent('ApproachRule','OnePointApproach')

   #Operator.SetActivePyEvent('ApproachRule', 'YourEventNname')
   #Operator.RemoveEventFromRule('Approach', 'OnePointApproach')
   
def PostWmOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   #changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   #attribName = changedAttrib.GetName()
   pass
   
def PostWmSyncPgAttributes(Operator):
   pass
   
def PostProcessOperationAttributes(Operator):
   pass
      
