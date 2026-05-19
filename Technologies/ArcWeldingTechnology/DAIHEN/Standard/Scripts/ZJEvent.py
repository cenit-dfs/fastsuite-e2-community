from operator import attrgetter
from centypes import *
from cenpylib import *
from centypes import *

# -------------------------------------------------------------------------------------------
# Measure event
# nothing special done here. There are just some parameters defined for the output
# -------------------------------------------------------------------------------------------

AW_LASER_ZJ_ON  = "LaserZjEvtOn"
AW_LASER_ZJ_SENSOR_NR  = "LaserZjEvtSensorNr"
AW_LASER_ZJ_MECHANISM_NR  = "LaserZjEvtMechanismNr"
AW_LASER_ZJ_GFF = "LaserZjEvtGFF"
AW_LASER_ZJ_GAP = "LaserZjEvtGAP"
AW_LASER_ZJ_DEV = "LaserZjEvtDEV"
AW_LASER_ZJ_STORE_NUMBER = "LaserZjEvtStoreNumber"
AW_LASER_ZJ_BASE_MEMORY = "LaserZjBasePointMemory"
AW_LASER_ZJ_BASE_POS_X = "LaserZjEvtBasePositionX"
AW_LASER_ZJ_BASE_POS_Y = "LaserZjEvtBasePositionY"
AW_LASER_ZJ_BASE_POS_Z = "LaserZjEvtBasePositionZ"
AW_LASER_ZJ_SEARCH_DELAY = "LaserZjEvtSearchWaitDelay"
AW_LASER_ZJ_STABLE_DELAY = "LaserZjEvtSearchStableDelay"
AW_LASER_ZJ_STORE_COORDINATES = "LaserZjEvtStoreCoordinates"
AW_LASER_ZJ_STORE_LIT = ["World", "Tool", "Work", "Machine"]
AW_LASER_ZJ_DEV_COMPOSITION = "LaserZjEvtDevComposition"
AW_LASER_ZJ_AUTO_MANUAL_MODIFY = "LaserZjEvtAutoManualModify"
AW_LASER_ZJ_DEVIATION_LENGTH = "LaserZjEvtDeviationLength"
AW_LASER_ZJ_MIN_DEPTH_VALUE = "LaserZjEvtMinDepthValue"
AW_LASER_ZJ_GAP_WATCH_RANGE_MAX = "LaserZjEvtGapWatchRangeMax"
AW_LASER_ZJ_GAP_WATCH_RANGE_MIN = "LaserZjEvtGapWatchRangeMin"
AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX = "LaserZjEvtAngleOneRangeMax"
AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN = "LaserZjEvtAngleOneRangeMin"
AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX = "LaserZjEvtAngleTwoRangeMax"
AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN = "LaserZjEvtAngleTwoRangeMin"

def GetEventName():
   return "ZJEvent"

def GetEventUuId():
   return "271CA110-5296-4B1F-B1C1-2C2450BD7108"

def GetIconName():
   return "ArcWeldCalibration_SeamFinding"

def GetEventType():
   return OLPEVENT_OLP

def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   attribCreator = Operator.GetAttribCreator()

   laserZjOn = attribCreator.AddBool(AW_LASER_ZJ_ON, True, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_ON)
   laserZjOn.SetVisibility(False)
   laserZjSensor = attribCreator.AddInteger(AW_LASER_ZJ_SENSOR_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_SENSOR_NR)   
   laserZjMechanism = attribCreator.AddInteger(AW_LASER_ZJ_MECHANISM_NR, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_MECHANISM_NR)   
   laserZjDEV = attribCreator.AddInteger(AW_LASER_ZJ_DEV, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_DEV)   
   laserZjGAP = attribCreator.AddInteger(AW_LASER_ZJ_GAP, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GAP)
   laserZjGFF = attribCreator.AddInteger(AW_LASER_ZJ_GFF, 1, 0, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_GFF)   
   laserZjStoreCoordinates = attribCreator.AddEnum(AW_LASER_ZJ_STORE_COORDINATES, AW_LASER_ZJ_STORE_LIT, AW_LASER_ZJ_STORE_LIT[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_COORDINATES)
   laserZjDevComposition = attribCreator.AddBool(AW_LASER_ZJ_DEV_COMPOSITION, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_DEV_COMPOSITION)
   laserZjAutoManualModify = attribCreator.AddBool(AW_LASER_ZJ_AUTO_MANUAL_MODIFY, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_AUTO_MANUAL_MODIFY)
   laserZjBasePointMemory = attribCreator.AddBool(AW_LASER_ZJ_BASE_MEMORY, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_BASE_MEMORY)   
   laserZjSearchWaitDelay = attribCreator.AddDouble(AW_LASER_ZJ_SEARCH_DELAY, 0.3, 0.0, 99.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_SEARCH_DELAY)
   laserZjSearchStableDelay = attribCreator.AddDouble(AW_LASER_ZJ_STABLE_DELAY, 0.5, 0.0, 99.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_ZJ_STABLE_DELAY)   
   laserZjStoreNumber = attribCreator.AddInteger(AW_LASER_ZJ_STORE_NUMBER, 0, 1, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_ZJ_STORE_NUMBER)   
   laserZjBasePositionX = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_X, 0.0, -0.10, 0.10, 0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_X)
   laserZjBasePositionY = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Y, 0.0, -0.10, 0.10, 0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Y)
   laserZjBasePositionZ = attribCreator.AddDouble(AW_LASER_ZJ_BASE_POS_Z, 0.049, -0.10, 0.10, 0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_BASE_POS_Z)
   laserZjDeviationLength = attribCreator.AddDouble(AW_LASER_ZJ_DEVIATION_LENGTH, 0.050, 0.0, 0.999, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_DEVIATION_LENGTH)   
   laserZjGapWatchRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MAX, 0.02, -0.999, 0.999, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MAX)
   laserZjGapWatchRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_GAP_WATCH_RANGE_MIN, -0.02, -0.999, 0.999, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_GAP_WATCH_RANGE_MIN)   
   laserZjMinDepthValue = attribCreator.AddDouble(AW_LASER_ZJ_MIN_DEPTH_VALUE, 0.005, 0.0, 0.099, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, AW_LASER_ZJ_MIN_DEPTH_VALUE)
   laserZjAngleOneRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX, 180.0, 0.0, 360.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MAX)
   laserZjAngleOneRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN, 0.0, -360.0, 360.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_ONE_RANGE_MIN)   
   laserZjAngleTwoRangeMax = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX, 90.0, 0.0, 360.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MAX)
   laserZjAngleTwoRangeMin = attribCreator.AddDouble(AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN, 0.0, -360.0, 360.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_ANGLE, AW_LASER_ZJ_ANGLE_TWO_RANGE_MIN)
   
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
