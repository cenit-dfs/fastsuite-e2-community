from centypes import *

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
# LaserTrackingEvent (Online)
FILE_NAME = "LT_Event.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."


# Operation attribute definition
LS_APPROACH_MTYPE = "Motion"
LS_APPROACH_SPEED = "Speed"

LTS_DEF = "LTS"
LTS_DEFs = ["None","On","Point","Off"]
LTSCNT_DEF = "LTSCount"
LTE_DEF = "LTE"
LTE_DEFs = ["None","On","Off"]
LTECNT_DEF = "LTECount"

# Event attribute definition
LTS_DL = "DLLTS"
LTS_DLs = ["None","On","Point","Off"]
LTSINDEX_DL = "DLLTSIndex"
LTSINDEX_DLs = ["0","1","2","3"]
LTSCNT_DL = "DLLTSCount"
LTE_DL = "DLLTE"
LTE_DLs = ["None","On","Off"]
LTEINDEX_DL = "DLLTEIndex"
LTEINDEX_DLs = ["0","1","2"]
LTECNT_DL = "DLLTECount"


def GetEventName():
   return "LT_Event"
   
def GetEventUuId():
   return "0A24F1DA-B513-4E53-A6BC-6DED9F508B17"
   
def GetIconName():
   return "COM_TableRecord"
   
def GetExplodeCycle():
   return 0
   
def GetMultipleCreationIsPossible():
   return 1

def GetEventType():
   return OLPEVENT_OLP
   
def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY

def GetCycleTranslationAutoFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleTranslationManualFlag():
   return CYCLETRANSLATION_TRANSYES

def GetCycleRotationAutoFlag():
   return CYCLEROTATION_ROTPATHTOOL
   
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTPATHTOOL
   
def IsMachiningCycle():
   return 0

def GetGroupName():
   return "OlpEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes
def PostInitAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   attribCreator = Operator.GetAttribCreator()
   
   # Laser Tracking Attributes
   # LTS
   att1 = attribCreator.AddEnum(LTS_DL, LTS_DLs, LTS_DLs[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTS_DL)
   att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att2 = attribCreator.AddEnum(LTSINDEX_DL, LTSINDEX_DLs, LTSINDEX_DLs[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTSINDEX_DL)
   att2.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att2.SetReadOnly(True)
   att2.SetVisibility(False)

   att3 = attribCreator.AddInt(LTSCNT_DL, 0, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTSCNT_DL)
   att3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # LTE
   att4 = attribCreator.AddEnum(LTE_DL, LTE_DLs, LTE_DLs[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTE_DL)
   att4.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att5 = attribCreator.AddEnum(LTEINDEX_DL, LTEINDEX_DLs, LTEINDEX_DLs[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTEINDEX_DL)
   att5.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att5.SetReadOnly(True)
   att5.SetVisibility(False)

   att6 = attribCreator.AddInt(LTECNT_DL, 0, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, LTECNT_DL)
   att6.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)   
   
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

  
def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   pass   

# -------------------------------------------------------------------------------------------
# Event post compute
def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Set LTS Attribute Visu
   SetLTSAttributeVisu(attribGetter,logging)

   # Set LTE Attribute Visu
   SetLTEAttributeVisu(attribGetter,logging)
   #pass
   
def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   pass

def SetLTSAttributeVisu(attribGetter,logging):
   try:
      ltsIndex = attribGetter.GetEnumIndex(LTS_DL)
   except:
      logging.LogError('Cannot get the attribute LTS_DL!')

   if ltsIndex == 1:
      visu = True
   else:
      visu = False

   try:
      ltsCountAtt = attribGetter.GetAttributeByName(LTSCNT_DL)
      ltsCountAtt.SetVisibility(visu)
   except:
      logging.LogError('Cannot get the attribute LTSCNT_DL!')

   try:
      att = attribGetter.GetAttributeEnumByName(LTSINDEX_DL)
      att.SetValue(str(ltsIndex))
   except:
      logging.LogError('Cannot get the attribute LTSINDEX_DL!')
   
def SetLTEAttributeVisu(attribGetter,logging):
   try:
      lteIndex = attribGetter.GetEnumIndex(LTE_DL)
   except:
      logging.LogError('Cannot get the attribute LTE_DL!')

   if lteIndex == 1:
      visu = True
   else:
      visu = False

   try:
      lteCountAtt = attribGetter.GetAttributeByName(LTECNT_DL)
      lteCountAtt.SetVisibility(visu)
   except:
      logging.LogError('Cannot get the attribute LTECNT_DL!')

   try:
      att = attribGetter.GetAttributeEnumByName(LTEINDEX_DL)
      att.SetValue(str(lteIndex))
   except:
      logging.LogError('Cannot get the attribute LTEINDEX_DL!')
