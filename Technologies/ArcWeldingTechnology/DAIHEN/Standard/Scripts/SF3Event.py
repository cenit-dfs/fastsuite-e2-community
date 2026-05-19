from operator import attrgetter
from centypes import *
from cenpylib import *
from centypes import *

# -------------------------------------------------------------------------------------------
# Measure event
# nothing special done here. There are just some parameters defined for the output
# -------------------------------------------------------------------------------------------

AW_LASER_SF3_MECHANISM_NR =  "LaserSF3EvtMechanismNr"
AW_LASER_SF3_VERSION_NR =  "LaserSF3EvtVersionNr"
AW_LASER_SF3_SECTION_LIT =  ["Start", "End", "All End"]
AW_LASER_SF3_SECTION =  "LaserSF3EvtSection"
AW_LASER_SF3_SHIFT_LIT =  ["DEV.file", "Num.Input", "Man.Operation"]
AW_LASER_SF3_SHIFT_METHOD =  "LaserSF3EvtShiftMethod"
AW_LASER_SF3_CALL_NR =  "LaserSF3EvtCallNr"
AW_LASER_SF3_POSTURE_CALLING =  "LaserSF3EvtPostureCalling"
AW_LASER_SF3_BASE_COORD_LIT =  ["Machine", "Tool", "World", "Work", "User"]
AW_LASER_SF3_BASE_COORD_SYSTEM =  "LaserSF3EvtBaseCoordSystem"
AW_LASER_SF3_BCS_USER =  "LaserSF3EvtBCSUser"
AW_LASER_SF3_FILE_OFFSET_X =  "LaserSF3EvtDEVFileOffsetX"
AW_LASER_SF3_FILE_OFFSET_Y =  "LaserSF3EvtDEVFileOffsetY"
AW_LASER_SF3_FILE_OFFSET_Z =  "LaserSF3EvtDEVFileOffsetZ"
AW_LASER_SF3_SHIFT_DIST_X =  "LaserSF3EvtNumericalShiftDistanceX"
AW_LASER_SF3_SHIFT_DIST_Y =  "LaserSF3EvtNumericalShiftDistanceY"
AW_LASER_SF3_SHIFT_DIST_Z =  "LaserSF3EvtNumericalShiftDistanceZ"
AW_LASER_SF3_MAIN_DEV_NR =  "LaserSF3EvtMainDEVNr"
AW_LASER_SF3_AUX_DEV_NR1 =  "LaserSF3EvtAuxiliaryDEVNr1"
AW_LASER_SF3_AUX_DEV_NR2 =  "LaserSF3EvtAuxiliaryDEVNr2"
AW_LASER_SF3_AUX_DEV_NR3 =  "LaserSF3EvtAuxiliaryDEVNr3"

def GetEventName():
    return "SF3Event"

def GetEventUuId():
    return "FADECFD0-0C06-4F87-A209-18BD7A0DAD57"

def GetIconName():
    return "ArcWeldCalibration_SeamSearch"

def GetEventType():
    return OLPEVENT_OLP


def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
    attribCreator = Operator.GetAttribCreator()
    
    attribCreator.AddInteger(AW_LASER_SF3_MECHANISM_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_MECHANISM_NR)    
    
    attribCreator.AddInteger(AW_LASER_SF3_VERSION_NR, 2, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_VERSION_NR)
    
    attribCreator.AddEnum(AW_LASER_SF3_SECTION, AW_LASER_SF3_SECTION_LIT, AW_LASER_SF3_SECTION_LIT[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_SECTION)
    
    att2 = attribCreator.AddEnum(AW_LASER_SF3_SHIFT_METHOD, AW_LASER_SF3_SHIFT_LIT, AW_LASER_SF3_SHIFT_LIT[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_SHIFT_METHOD)    
    att2.SetVisibility(True)
    
    att3 = attribCreator.AddInteger(AW_LASER_SF3_CALL_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_CALL_NR)
    att3.SetVisibility(True)
    
    att4 = attribCreator.AddBool(AW_LASER_SF3_POSTURE_CALLING, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_POSTURE_CALLING) 
    att4.SetVisibility(True)
    
    att5 = attribCreator.AddEnum(AW_LASER_SF3_BASE_COORD_SYSTEM, AW_LASER_SF3_BASE_COORD_LIT, AW_LASER_SF3_BASE_COORD_LIT[2], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_BASE_COORD_SYSTEM)
    att5.SetVisibility(False)
    
    att6 = attribCreator.AddInteger(AW_LASER_SF3_BCS_USER, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_BCS_USER)
    att6.SetVisibility(False)
    
    att7 = attribCreator.AddDouble(AW_LASER_SF3_FILE_OFFSET_X, 0, 0, 10000, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_SF3_FILE_OFFSET_X)
    att7.SetVisibility(True)
    
    att8 = attribCreator.AddDouble(AW_LASER_SF3_FILE_OFFSET_Y, 0, 0, 10000, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_SF3_FILE_OFFSET_Y)
    att8.SetVisibility(True)
        
    att9 = attribCreator.AddDouble(AW_LASER_SF3_FILE_OFFSET_Z, 0, 0, 10000, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_SF3_FILE_OFFSET_Z)
    att9.SetVisibility(True)
    
    att10 = attribCreator.AddDouble(AW_LASER_SF3_SHIFT_DIST_X, 0, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_SF3_SHIFT_DIST_X)
    att10.SetVisibility(False)
    
    att11 = attribCreator.AddDouble(AW_LASER_SF3_SHIFT_DIST_Y, 0, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_SF3_SHIFT_DIST_Y)
    att11.SetVisibility(False)
    
    att12 = attribCreator.AddDouble(AW_LASER_SF3_SHIFT_DIST_Z, 0, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_SF3_SHIFT_DIST_Z)
    att12.SetVisibility(False)
    
    att13 = attribCreator.AddString(AW_LASER_SF3_MAIN_DEV_NR, "0", USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_MAIN_DEV_NR)
    att13.SetVisibility(False)
    
    att14 = attribCreator.AddString(AW_LASER_SF3_AUX_DEV_NR1, "0", USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_AUX_DEV_NR1)
    att14.SetVisibility(False)   

    att15 = attribCreator.AddString(AW_LASER_SF3_AUX_DEV_NR2, "1", USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_AUX_DEV_NR2)
    att15.SetVisibility(False)    
     
    att16 = attribCreator.AddString(AW_LASER_SF3_AUX_DEV_NR3, "1", USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF3_AUX_DEV_NR3)
    att16.SetVisibility(False)
    
def PostOnAttribChanged(seriesAttribChangedOperator: CENPyOlpEvent_AttribChangedOperator):
   
   changedAttribName = seriesAttribChangedOperator.GetChangedAttributeName()
   attribGetter = seriesAttribChangedOperator.GetAttribGetter()
   if changedAttribName == AW_LASER_SF3_SECTION:
      value = attribGetter.GetAttributeEnumByName(AW_LASER_SF3_SECTION).GetValue()
      visiOne = False
      visiTwo = True
      if value == "End" or value == "All End":
         visiOne = True
         visiTwo = False
      
      # attribGetter.GetAttributeByName(AW_LASER_SF3_BASE_COORD_SYSTEM).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_BCS_USER).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_MAIN_DEV_NR).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_SHIFT_DIST_X).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_SHIFT_DIST_Y).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_SHIFT_DIST_Z).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_AUX_DEV_NR1).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_AUX_DEV_NR1).SetVisibility(visiOne)
      # attribGetter.GetAttributeByName(AW_LASER_SF3_AUX_DEV_NR1).SetVisibility(visiOne)
   
      attribGetter.GetAttributeByName(AW_LASER_SF3_SHIFT_METHOD).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF3_CALL_NR).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF3_POSTURE_CALLING).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF3_FILE_OFFSET_X).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF3_FILE_OFFSET_Y).SetVisibility(visiTwo)
      attribGetter.GetAttributeByName(AW_LASER_SF3_FILE_OFFSET_Z).SetVisibility(visiTwo)
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
