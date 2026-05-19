from operator import attrgetter
from centypes import *
from cenpylib import *
from centypes import *

# -------------------------------------------------------------------------------------------
# Measure event
# nothing special done here. There are just some parameters defined for the output
# -------------------------------------------------------------------------------------------

AW_LASER_SF4_VERSION_NR = "LaserSF4EvtVersionNr"
AW_LASER_SF4_DEV_FILE_ONE = "LaserSF4EvtDevFileOne"
AW_LASER_SF4_RATE_ONE = "LaserSF4EvtRateOne"
AW_LASER_SF4_DEV_FILE_TWO = "LaserSF4EvtDevFileTwo"
AW_LASER_SF4_RATE_TWO = "LaserSF4EvtRateTwo"
AW_LASER_SF4_DEV_FILE_THREE = "LaserSF4EvtDevFileThree"
AW_LASER_SF4_RATE_THREE = "LaserSF4EvtRateThree"
AW_LASER_SF4_DEV_STORE_NR = "LaserSF4EvtDevStoreNr"

def GetEventName():
   return "SF4Event"

def GetEventUuId():
   return "4F9256D1-1A55-480C-A7AB-F6EDC7ACA19E"

def GetIconName():
   return "ArcWeldCalibration_TouchSensing"

def GetEventType():
   return OLPEVENT_OLP

def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   attribCreator = Operator.GetAttribCreator()

   attribCreator.AddInteger(AW_LASER_SF4_VERSION_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_VERSION_NR)
   attribCreator.AddInteger(AW_LASER_SF4_DEV_FILE_ONE, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_DEV_FILE_ONE)
   attribCreator.AddInteger(AW_LASER_SF4_RATE_ONE, 100, 0, 100, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_RATE_ONE)
   attribCreator.AddInteger(AW_LASER_SF4_DEV_FILE_TWO, 0, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_DEV_FILE_TWO)
   attribCreator.AddInteger(AW_LASER_SF4_RATE_TWO, 100, 0, 100, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_RATE_TWO)
   attribCreator.AddInteger(AW_LASER_SF4_DEV_FILE_THREE, 0, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_DEV_FILE_THREE)
   attribCreator.AddInteger(AW_LASER_SF4_RATE_THREE, 100, 0, 100, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_RATE_THREE)
   attribCreator.AddInteger(AW_LASER_SF4_DEV_STORE_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_SF4_DEV_STORE_NR)

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
