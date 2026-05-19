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

#Chain flag
CW_CHAIN_BEGIN = "ChainBegin"
CW_CHAIN_END = "ChainEnd"

# Laser Tracking on/off
AW_SEAMTRACKING_ONOFF = "SeamTrackingOnOff"

def PostWmInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   attribCreator = Operator.GetAttribCreator()
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # your code 
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

   #Chain Welding attribs
   
   att4=attribCreator.AddBool(CW_CHAIN_BEGIN, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, CW_CHAIN_BEGIN)
   att4.SetReadOnly(True)
   att4.SetVisibility(False)

   att5=attribCreator.AddBool(CW_CHAIN_END, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, CW_CHAIN_END)
   att5.SetReadOnly(True)
   att5.SetVisibility(False)

   # Make seam tracking on/off Global, Process and User
   attSeamTrackingOnOff = attribCreator.AddBool(AW_SEAMTRACKING_ONOFF, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_SEAMTRACKING_ONOFF)
   attSeamTrackingOnOff.SetVisibility(True)

   pass 

def PostWmInitEvents(Operator):
      
   #Laser Tracking     
   Operator.RegisterPyTechnologyEvent('LT_Param_Event.py')
   Operator.RegisterPyTechnologyEvent('LT_Event.py')
   Operator.RegisterPyTechnologyEvent('LTOnEvent.py')
   Operator.RegisterPyTechnologyEvent('LTOffEvent.py')
   Operator.RegisterPyTechnologyEvent('LT2PTApproach.py')
   
   #Touch Sensing - regular
   # Operator.RegisterPyTechnologyEvent('TSCalcApproach.py')
   # Operator.RegisterPyTechnologyEvent('TSCorrectEvent.py')
   # Operator.RegisterPyTechnologyEvent('TSCorrectOnEvent.py')

   #Chain welding w/ Touch Sensing
   # Operator.RegisterPyTechnologyEvent('CWChainApproach.py')
   # Operator.RegisterPyTechnologyEvent('CWChainRetract.py')
   # Operator.RegisterPyTechnologyEvent('CWLocalEndEvent.py')
   #pass

def PostWmInitRules(Operator):
   #Approach Events
   Operator.AddPyEvent('ApproachRule', 'LT2PTApproach')
   # Operator.AddPyEvent('ApproachRule', 'TSCalcApproach')
   # Operator.AddPyEvent('ApproachRule', 'CWChainApproach')
   
   #Set a default
   Operator.SetActivePyEvent('ApproachRule','OnePointApproach')

   #Retract Events
   # Operator.AddPyEvent('RetractRule','CWChainRetract')
   #default - one point approach
   

   #Operator.SetActivePyEvent('ApproachRule', 'YourEventNname')
   #Operator.RemoveEventFromRule('Approach', 'OnePointApproach')
   
def PostWmOnAttribChanged(Operator):
   pass
   
def PostWmSyncPgAttributes(Operator):
   pass
   
def PostProcessOperationAttributes(Operator):
   pass
      
