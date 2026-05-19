from operator import attrgetter
from centypes import *
from cenpylib import *
from centypes import *

# -------------------------------------------------------------------------------------------
# Measure event
# nothing special done here. There are just some parameters defined for the output
# -------------------------------------------------------------------------------------------

AW_LASER_SF8_STORING_DIRECTION_LIST =  ["Register->File", "File->Register"]
AW_LASER_SF8_STORING_DIRECTION =  "LaserSF8EvtStoringDirection"
AW_LASER_SF8_REGISTER_LIST =  ["Local", "Global"]
AW_LASER_SF8_REGISTER =  "LaserSF8EvtRegister"
AW_LASER_SF8_NO =  "LaserSF8EvtNo"
AW_LASER_SF8_CALL_NR =  "LaserSF8EvtCallNr"
AW_LASER_SF8_MECHANISM_NR =  "LaserSF8EvtMechanismNr"
AW_LASER_SF8_BASE_COORD_LIT =  ["Machine", "Tool", "World", "Work", "User"]
AW_LASER_SF8_BASE_COORD_SYSTEM =  "LaserSF8EvtBaseCoordSystem"
AW_LASER_SF8_POSTURE_DEVIATION =  "LaserSF8EvtPostureDeviation"
AW_LASER_SF8_POSITION_MAX =  "LaserSF8EvtPositionMax"
AW_LASER_SF8_POSITION_MIN =  "LaserSF8EvtPositionMin"
AW_LASER_SF8_POSTURE_MAX =  "LaserSF8EvtPostureMax"
AW_LASER_SF8_POSTURE_MIN =  "LaserSF8EvtPostureMin"

def GetEventName():
    return "SF8Event"

def GetEventUuId():
    return "00DECFD0-0C06-4F87-A209-18BD758DAD57"

def GetIconName():
    return ""

def GetEventType():
    return OLPEVENT_OLP


def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
    attribCreator = Operator.GetAttribCreator()  

    attribCreator.AddEnum(AW_LASER_SF8_STORING_DIRECTION, AW_LASER_SF8_STORING_DIRECTION_LIST, AW_LASER_SF8_STORING_DIRECTION_LIST[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_STORING_DIRECTION)
    
    attribCreator.AddEnum(AW_LASER_SF8_REGISTER, AW_LASER_SF8_REGISTER_LIST, AW_LASER_SF8_REGISTER_LIST[1], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_REGISTER)
    
    attribCreator.AddInteger(AW_LASER_SF8_NO, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_NO)  

    attribCreator.AddInteger(AW_LASER_SF8_CALL_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_CALL_NR)
    
    att2 = attribCreator.AddInteger(AW_LASER_SF8_MECHANISM_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_MECHANISM_NR) 
    att2.SetVisibility(True)
    
    att3 = attribCreator.AddEnum(AW_LASER_SF8_BASE_COORD_SYSTEM, AW_LASER_SF8_BASE_COORD_LIT, AW_LASER_SF8_BASE_COORD_LIT[2], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_BASE_COORD_SYSTEM)
    att3.SetVisibility(True)
    
    att4 = attribCreator.AddBool(AW_LASER_SF8_POSTURE_DEVIATION, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF8_POSTURE_DEVIATION) 
    att4.SetVisibility(True) 
    
    att5 = attribCreator.AddDouble(AW_LASER_SF8_POSITION_MAX, 0.02, -0.999, 0.999, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_SF8_POSITION_MAX)
    att5.SetVisibility(True)
    
    att6 = attribCreator.AddDouble(AW_LASER_SF8_POSITION_MIN, -0.02, 0.999, 0.999, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_SF8_POSITION_MIN)
    att6.SetVisibility(True)
        
    att7 = attribCreator.AddDouble(AW_LASER_SF8_POSTURE_MAX, 5, -90, 90, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_SF8_POSTURE_MAX)
    att7.SetVisibility(True)
    
    att8 = attribCreator.AddDouble(AW_LASER_SF8_POSTURE_MIN, -5, -90, 90, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_SF8_POSTURE_MIN)
    att8.SetVisibility(True)  

def PostOnAttribChanged(seriesAttribChangedOperator: CENPyOlpEvent_AttribChangedOperator):
   
   changedAttribName = seriesAttribChangedOperator.GetChangedAttributeName()
   attribGetter = seriesAttribChangedOperator.GetAttribGetter()
   if changedAttribName == AW_LASER_SF8_STORING_DIRECTION:
      value = attribGetter.GetAttributeEnumByName(AW_LASER_SF8_STORING_DIRECTION).GetValue()
      visiOne = False
      visiTwo = True
      if value == "File->Register":
         visiOne = True
         visiTwo = False      
  
      attribGetter.GetAttributeByName(AW_LASER_SF8_MECHANISM_NR).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_BASE_COORD_SYSTEM).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_POSTURE_DEVIATION).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_POSITION_MAX).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_POSITION_MIN).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_POSTURE_MAX).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF8_POSTURE_MIN).SetVisibility(visiTwo)
   pass

# -------------------------------------------------------------------------------------------
def GetExplodeCycle():
   return 0

def GetMultipleCreationIsPossible():
   return 1

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEFORBIDDEN

def IsMachiningCycle():
   return 0

def GetGroupName():
   return "Common"

def GetCycleReferenceBehavior():
   return CYCLEREFBEHAVIOR_NORMAL

def GetCycleRotationAutoFlag():
   return 0

def GetCycleTranslationAutoFlag():
   return 0

def GetCycleRotationManualFlag():
   return 0

def GetCycleTranslationManualFlag():
   return 0
