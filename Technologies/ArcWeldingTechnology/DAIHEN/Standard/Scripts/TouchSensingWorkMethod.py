# -------------------------------------------------------------------------------------------
# Name: TouchSensingWorkMethod
# Description: this Python file adjust basic implementation for vendor specific installation 
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import sys, os, inspect
sys.dont_write_bytecode = True
import csv

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "TouchSensingWorkMethod.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) WM initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) WM initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) WM initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) WM initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) WM initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) WM initialization of event rules ended."

DEBUG_SYNC_PG_ATTRIB_START = "(Debug-Technology) WM synchronization of process geometry started."
DEBUG_SYNC_PG_ATTRIB_END = "(Debug-Technology) WM synchronization of process geometry ended."

DEBUG_POST_PROCESS_OPERATION_ATTRIB_START = "(Debug-Technology) WM post process operation attributes stared."
DEBUG_POST_PROCESS_OPERATION_ATTRIB_END = "(Debug-Technology) WM post process operation attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) prev on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) WM Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) WM Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) WM Could not get attribute."
ERROR_SET_ATTRIB = "(Error) WM Could not set attribute."

# Operation attribute definition
SF1_TOUCH_PARAMS="SF1_TOUCH_PARAMS"
SF1_P01_MECHNO = "SF1_P01_MECHNO"
SF1_P02_STORENR = "SF1_P02_STORENR"
SF1_P03_IDX_STORE_COORD = "SF1_P03_IDX_STORE_COORD"
SF1_P04_DUMMY = "SF1_P04_DUMMY"
SF1_P05_STORE_POS_START = "SF1_P05_STORE_POS_START"
SF1_P06_DEV_COMP = "SF1_P06_DEV_COMP"
SF1_P07_TOUCH_LOGIC = "SF1_P07_TOUCH_LOGIC"
SF1_P08_SEARCH_SPEED = "SF1_P08_SEARCH_SPEED"
SF1_P09_S_RANGE_MAX = "SF1_P09_S_RANGE_MAX"
SF1_P10_S_RANGE_MIN = "SF1_P10_S_RANGE_MIN"
SF1_P11_OVER_DEV_RANGE = "SF1_P11_OVER_DEV_RANGE"
SF1_P12_IDX_STORE_COORD = "SF1_P12_IDX_STORE_COORD"
SF1_P13_DUMMY = "SF1_P13_DUMMY"

SF3_P03_CALL_POS = "SF3_P03_CALL_POS"
SF3_P04_SF3_SECTION = "SF3_P04_SF3_SECTION"
SF3_P04_OPTIONS = ["End","Start","All End"]
SF3_P05_POSTURE_CALL_0 = "SF3_P05_POSTURE_CALL_0"
SF3_P06_OFFSET_X = "SF3_P06_OFFSET_X"
SF3_P07_OFFSET_Y = "SF3_P07_OFFSET_Y"
SF3_P08_OFFSET_Z = "SF3_P08_OFFSET_Z"

SF4_OUTPUT = "SF4_OUTPUT"
SF4_P2_DEVPOS_1 = "SF4_P2_DEVPOS_1"
SF4_P3_RATIO_1 = "SF4_P3_RATIO_1"
SF4_P4_DEVPOS_2 = "SF4_P4_DEVPOS_2"
SF4_P5_RATIO_2 = "SF4_P5_RATIO_2"
SF4_P6_DEVPOS_3 = "SF4_P6_DEVPOS_3"
SF4_P7_RATIO_3 = "SF4_P7_RATIO_3"
SF4_P8_DEVPOS_COMB = "SF4_P8_DEVPOS_COMB"

WM_MOTION_TYPE = "OperationGroupMotionType"
AW_TOUCHSENS_SENSING_LENGTH = "SensingLength"
AW_TOUCHSENS_OVERTRAVEL_LENGTH = "OvertravelLength"
AW_TOUCHSENS_LENGTH = "TouchSensingLength"
# number of the position register where touch sensing starts
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"

# Custom Attributes
AW_TOUCHSENS_APPR_RETR_SPEED="TouchApprRetrSpeed"
AW_TOUCHSENS_APPR_RETR_FLYBY="TouchApprFlyBy"
TS_AUTO_SIDE_OFFSET = "TS_AUTO_SIDE_OFFSET"
TS_AUTO_TANG_OFFSET = "TS_AUTO_TANG_OFFSET"
AW_MOTION_TYPE_FIRST_TPE = "TouchSensMotionTypeFirstTpe"
AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY = "Tooltip" + AW_MOTION_TYPE_FIRST_TPE
AW_MOTION_TYPE_FIRST_TPE_LITERALS = ["PTP", "LIN"]

# -------------------------------------------------------------------------------------------
# Work method post init attributes
def PostWmInitAttributes(Operator: CENPyOlpWM_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return

   try:
      # set motion type default PTP = 0; LIN = 1
      attribSetter.SetEnumIndex(WM_MOTION_TYPE, 1)
      # attrbiute to calculate total touch sensing length = SensingLength + OvertravelLength; for download only
      attribCreator.AddDouble(AW_TOUCHSENS_LENGTH, 0,-5,5,0.001, OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_LENGTH)
   except:
      logging.LogError("Cannot set attribute OperationGroupMotionType!")

   attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_SPEED, 0.200,0,1,0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_SPEED)
   attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_FLYBY, 0.0025,0,0.1,0.005, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_FLYBY)
   attribCreator.AddDouble(TS_AUTO_TANG_OFFSET, 0.015,-1,1,0.001, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, TS_AUTO_TANG_OFFSET)
   attribCreator.AddDouble(TS_AUTO_SIDE_OFFSET, 0.02,-1,1,0.001, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, TS_AUTO_SIDE_OFFSET)
   
   searchMoTypeIndex = attribGetter.GetEnumIndex(WM_MOTION_TYPE)
   attrib = attribCreator.AddEnum(AW_MOTION_TYPE_FIRST_TPE, AW_MOTION_TYPE_FIRST_TPE_LITERALS, AW_MOTION_TYPE_FIRST_TPE_LITERALS[searchMoTypeIndex], OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_MOTION_TYPE_FIRST_TPE)
   attrib.SetTooltipKey(AW_MOTION_TYPE_FIRST_TPE_TOOLTIP_KEY)
   attrib.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   # Touch Attribs DAIHEN
   # GetTechnologyTable implementation missing
   path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
   filename =  path + 'DaihenTouchSchedule.csv'
   # filename = Operator.GetTechnologyTable("DaihenTouchSchedule.csv")
   
   # retrieve the number of schedule
   numOfSchedules = 0
   touchScheduleLiterals = []

   with open(filename, 'r') as csvfile:
      csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
      next(csv_reader)
      for row in csv_reader:
         numOfSchedules += 1
         touchScheduleLiterals.append(row[0])

   # There are no schedule in ths CSV
   if numOfSchedules <= 0:
      pass
   
   # schedule Strings
   recipeEnum = attribCreator.AddEnum(SF1_TOUCH_PARAMS, touchScheduleLiterals, touchScheduleLiterals[0], OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE,SF1_TOUCH_PARAMS)
   recipeEnum.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   # Mechanism number
   attribCreator.AddInt(SF1_P01_MECHNO, 1,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P01_MECHNO)
   # Storage No for all registers SF1_P01_MECHNO
   attribCreator.AddInt(SF1_P02_STORENR, 1,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P02_STORENR)
   # Index of coordinate system used
   attribCreator.AddInt(SF1_P03_IDX_STORE_COORD, 1,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P03_IDX_STORE_COORD)
   # Unknown - Dummy
   attribCreator.AddInt(SF1_P04_DUMMY, 2,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P04_DUMMY)
   # Store # for 1st touch offset; will be incremented by 1 for each search event until Daihen TouchEnd event is found
   attribCreator.AddInt(SF1_P05_STORE_POS_START, 0,0,498, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P05_STORE_POS_START)
   # Deviation composition; to be off according to Sumig
   attribCreator.AddBool(SF1_P06_DEV_COMP, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P06_DEV_COMP)
   # Touch Logic 
   attribCreator.AddBool(SF1_P07_TOUCH_LOGIC, False, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P07_TOUCH_LOGIC)
   # Search Speed 
   attribCreator.AddInt(SF1_P08_SEARCH_SPEED, 90,0,360, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P08_SEARCH_SPEED)
   # Search ra nge max
   attribCreator.AddDouble(SF1_P09_S_RANGE_MAX, 0.1,0.0,0.9999,0.010, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF1_P09_S_RANGE_MAX)
   # Search range min
   attribCreator.AddDouble(SF1_P10_S_RANGE_MIN, 0.0,0.0,0.9999,0.010, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF1_P10_S_RANGE_MIN)
   # Search over deviation range
   attribCreator.AddDouble(SF1_P11_OVER_DEV_RANGE, 0.015,0,0.9999,0.005, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF1_P11_OVER_DEV_RANGE)
   # Index of coordinate system used - same as 
   attribCreator.AddInt(SF1_P12_IDX_STORE_COORD, 1,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P12_IDX_STORE_COORD)
   # Storeage No for all registers
   attribCreator.AddInt(SF1_P13_DUMMY, -1,1,10, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF1_P13_DUMMY)

   # Dummy Param
   attribCreator.AddInt(SF3_P03_CALL_POS, 500,0,999,OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF3_P03_CALL_POS)
   # schedule Strings
   attribCreator.AddEnum(SF3_P04_SF3_SECTION,SF3_P04_OPTIONS,SF3_P04_OPTIONS[1], OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE,SF3_P04_SF3_SECTION)
   # Dummy Param
   attribCreator.AddInt(SF3_P05_POSTURE_CALL_0, 0,0,999, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF3_P05_POSTURE_CALL_0)
   # Ratio of Position 1
   attribCreator.AddDouble(SF3_P06_OFFSET_X, 0.0,0.0,0.9999,0.010, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF3_P06_OFFSET_X)
   # Ratio of Position 1
   attribCreator.AddDouble(SF3_P07_OFFSET_Y, 0.0,0.0,0.9999,0.010, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF3_P07_OFFSET_Y)
   # Ratio of Position 1
   attribCreator.AddDouble(SF3_P08_OFFSET_Z, 0.0,0.0,0.9999,0.010, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, SF3_P08_OFFSET_Z)

   # Store # of Position 1
   attribCreator.AddInt(SF4_P2_DEVPOS_1, 0,0,999, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF4_P2_DEVPOS_1)
   # Ratio of Position 1
   attribCreator.AddDouble(SF4_P3_RATIO_1, 1,-1,1,0.5, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_PERCENT, SF4_P3_RATIO_1)
   # Store # of Position 1
   attribCreator.AddInt(SF4_P4_DEVPOS_2, 0,0,999, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF4_P4_DEVPOS_2)
   # Ratio of Position 1
   attribCreator.AddDouble(SF4_P5_RATIO_2, 1,-1,1,0.5, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_PERCENT, SF4_P5_RATIO_2)
   # Store # of Position 1
   attribCreator.AddInt(SF4_P6_DEVPOS_3, 0,0,999, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF4_P6_DEVPOS_3)
   # Ratio of Position 1
   attribCreator.AddDouble(SF4_P7_RATIO_3, 1,-1,1,0.5, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_PERCENT, SF4_P7_RATIO_3)
   # Store # of compiled deviation
   attribCreator.AddInt(SF4_P8_DEVPOS_COMB, 500,1,999, OPERATION_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, SF4_P8_DEVPOS_COMB)

   UpdateAutoDefault(Operator)

# -------------------------------------------------------------------------------------------
# Work method post init events
def PostWmInitEvents(Operator: CENPyOlpWM_EventInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   Operator.RegisterPyTechnologyEvent('TouchPointStartAppEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointCollisionEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointEndEvent.py')
   Operator.RegisterPyTechnologyEvent('TouchPointStartRetEvent.py')

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)


# -------------------------------------------------------------------------------------------
# Work method post init event rules
# def PostWmInitRules(Operator: CENPyOlpWM_RuleInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)


# -------------------------------------------------------------------------------------------
# Work method post sync process geometry attributes
# def PostWmSyncPgAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_SYNC_PG_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Work method post process operation attributes
def PostProcessOperationAttributes(Operator: CENPyOlpWM_POAttribOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_ATTRIB_START)

   # retrieve the select recipe id
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()

   try:
      # get sensing length; value from collision point to start point
      sensingLength = attribGetter.GetDouble(AW_TOUCHSENS_SENSING_LENGTH)
      # get overtravel length; value from collision point to end point
      overTravelLength = attribGetter.GetDouble(AW_TOUCHSENS_OVERTRAVEL_LENGTH)
      # sum sensing and overtravel length to have the total touch sensing motion length
      attribSetter.SetDouble(AW_TOUCHSENS_LENGTH, sensingLength + overTravelLength)
   except:
      logging.LogError("Could not calculate total touch sensing length")

   readSf1Schedule(Operator)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_ATTRIB_END)

def readSf1Schedule(Operator):   
   # retrieve the select recipe id
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()
   # TouchSchedule ID 
   sched = attribGetter.GetEnumIndex(SF1_TOUCH_PARAMS)
   
   # no valid schedule ID
   if sched <= 0:
      pass

   # This is currently the only way to read the CSV which is in the same location like this script
   path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
   filename =  path + 'DaihenTouchSchedule.csv'
   # filename = Operator.GetTechnologyTable("DaihenTouchSchedule.csv")

   # read all schedule data
   schedule = []
   with open(filename, 'r') as csvfile:
      csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
      next(csv_reader)
      for row in csv_reader:
         schedule.append(row)

   # schedule id is out of range
   if sched > len(schedule):
      pass

   # parameter set of selected schedule
   parameters = schedule[sched]

   # Mechanism number
   attribSetter.SetInteger(SF1_P01_MECHNO, int(parameters[1]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P01_MECHNO)
   attrVisu.SetVisibility(False)
   # Storeage No for all registers SF1_P01_MECHNO
   attribSetter.SetInteger(SF1_P02_STORENR, int(parameters[2]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P02_STORENR)
   attrVisu.SetVisibility(False)
   # Index of coordinate system used
   attribSetter.SetInteger(SF1_P03_IDX_STORE_COORD, int(parameters[3]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P03_IDX_STORE_COORD)
   attrVisu.SetVisibility(False)
   # Unknown - Dummy
   attribSetter.SetInteger(SF1_P04_DUMMY, int(parameters[4]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P04_DUMMY)
   attrVisu.SetVisibility(False)
   # Store # for 1st touch offset; will be incremented by 1 for each search event until Daihen TouchEnd event is found
   attribSetter.SetInteger(SF1_P05_STORE_POS_START, int(parameters[5]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P05_STORE_POS_START)
   attrVisu.SetVisibility(True)
   # Deviation composition; to be off according to Sumig
   attribSetter.SetInteger(SF1_P06_DEV_COMP, bool(parameters[6]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P06_DEV_COMP)
   attrVisu.SetVisibility(True)
   # Touch Logic 
   attribSetter.SetInteger(SF1_P07_TOUCH_LOGIC, bool(parameters[7]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P07_TOUCH_LOGIC)
   attrVisu.SetVisibility(False)
   # Search Speed 
   attribSetter.SetInteger(SF1_P08_SEARCH_SPEED, int(parameters[8]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P08_SEARCH_SPEED)
   attrVisu.SetVisibility(False)
   # Search ra nge max
   attribSetter.SetDouble(SF1_P09_S_RANGE_MAX, float(parameters[9])/1000)
   attrVisu = attribGetter.GetAttributeByName(SF1_P09_S_RANGE_MAX)
   attrVisu.SetVisibility(True)
   # Search range min
   attribSetter.SetDouble(SF1_P10_S_RANGE_MIN, float(parameters[10])/1000)
   attrVisu = attribGetter.GetAttributeByName(SF1_P10_S_RANGE_MIN)
   attrVisu.SetVisibility(True)
   # Search over deviation range
   attribSetter.SetDouble(SF1_P11_OVER_DEV_RANGE, float(parameters[11])/1000)
   attrVisu = attribGetter.GetAttributeByName(SF1_P11_OVER_DEV_RANGE)
   attrVisu.SetVisibility(True)
   # Index of coordinate system used - same as 
   attribSetter.SetInteger(SF1_P12_IDX_STORE_COORD, int(parameters[12]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P12_IDX_STORE_COORD)
   attrVisu.SetVisibility(False)
   # Storeage No for all registers
   attribSetter.SetInteger(SF1_P13_DUMMY, int(parameters[13]))
   attrVisu = attribGetter.GetAttributeByName(SF1_P13_DUMMY)
   attrVisu.SetVisibility(False)

# -------------------------------------------------------------------------------------------
# Work method on attribute change 
def PostWmOnAttribChanged(Operator: CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   changedAttrib = Operator.GetChangedAttribute()  
   attribName = changedAttrib.GetName()
      
   if (attribName == TS_AUTO_TANG_OFFSET) or (attribName == TS_AUTO_SIDE_OFFSET):
      UpdateAutoDefault(Operator)

   if (attribName == SF1_TOUCH_PARAMS):
      readSf1Schedule(Operator)

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)

# -------------------------------------------------------------------------------------------
# Work method on frame change 
# def PostWmOnFrameChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)

# -------------------------------------------------------------------------------------------
# sub method UpdateAutoDefault
def UpdateAutoDefault(Operator: CENPyOlpWM_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)

   # changedAttrib = Operator.GetChangedAttribute()  
   # attribName = changedAttrib.GetName()

   # YOUR CODE

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)

   # retrieve the select recipe id
   attribGetter = Operator.GetAttribGetter()
   attribSetter = Operator.GetAttribSetter()

   # Set default offsets for automatic TS mode
   try:
      # get sensing length; value from collision point to start point
      TsTangOffset=attribGetter.GetDouble(TS_AUTO_TANG_OFFSET)
      TsSideOffset=attribGetter.GetDouble(TS_AUTO_SIDE_OFFSET)
      attribSetter.SetDouble("TouchSensStartToolDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensStartToolDirDist",TsTangOffset)
      attribSetter.SetDouble("TouchSensStartWorkDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensStartWorkDirDist",TsTangOffset)
      attribSetter.SetDouble("TouchSensStartTravelDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensStartTravelDirDist",TsTangOffset)

      attribSetter.SetDouble("TouchSensEndToolDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensEndToolDirDist",TsTangOffset)
      attribSetter.SetDouble("TouchSensEndWorkDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensEndWorkDirDist",TsTangOffset)
      attribSetter.SetDouble("TouchSensEndTravelDirTangDist",TsSideOffset)
      attribSetter.SetDouble("TouchSensEndTravelDirDist",TsTangOffset)
   except:
      logging.LogError("Could not set default TS offsets")
