# Import libraries
from centypes import *

# -------------------------------------------------------------------------------------------
# Event Definition in C++
# This Python only override some Attributes or Callbacks
# General global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "RetractArcWeldingStitch.py: "

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
LT_ACTIV_DEF = "LTActiv"
LTOFF_EVENT_UUID = "7A518E8D-EADA-4A14-A5BE-942411C894E7"

# Download attribute definition

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get attribute creator
   #attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()

   # YOUR CODE
   # attribSetter.SetDouble('RetractLengthX',0.00)
   # attribSetter.SetDouble('RetractLengthY',0.00)
   # attribSetter.SetDouble('RetractLengthZ',0.06)
   # attribSetter.SetDouble('SpeedViaRetract',0.20)
   # attribSetter.SetDouble('FlybyRetract',0.01)
   
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
   pass

# -------------------------------------------------------------------------------------------
# post process attribute
def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)

   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()

   # YOUR CODE


   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_END)
   pass
    
 
def PostCompute(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()

   # YOUR CODE
   # try:
   #    ltActiv = attribGetter.GetBool(LT_ACTIV_DEF)
   # except:
   #    logging.LogError('Cannot get the attribute LT_ACTIV_DEF!')

   # if ltActiv == True:
   #    endPoint = Operator.GetRefTpElement()
   #    Operator.GetEventOperator().AddEvent(LTOFF_EVENT_UUID, endPoint, TPINSERTPOS_INSERTBEFORE)
   pass

def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # YOUR CODE
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
   pass
