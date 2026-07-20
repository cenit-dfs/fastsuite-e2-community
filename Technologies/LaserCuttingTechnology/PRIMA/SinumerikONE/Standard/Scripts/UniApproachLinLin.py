from centypes import *

# -------------------------------------------------------------------------------------------
# Event Definition in C++
# This Python only override some Attributes or Callbacks
# General global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "UniApproachLinLin.py: "

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

# Download attribute definition

def GetEventName():
   return "UniApproachLinLin"

def GetEventUuId():
   return "4B8BACD9-7128-4CAD-A2D7-E0819F558E89"

def GetIconName():
   return "ToolpathApproach"

def GetEventType():
   return OLPEVENT_APPROACH

def IsEnabled():
   return True

def PostInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute creator
   #attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()
   pass

def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()

   # # Workaround Set Dummy Operation Attribut LT_ACTIV_DEF to False
   # try:
   #    attribSetter.SetBool(LT_ACTIV_DEF,False)
   # except:
   #    logging.LogError('Cannot set the attribute LT_ACTIV_DEF!')
   pass
    
def PostCompute(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   pass

def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   pass
