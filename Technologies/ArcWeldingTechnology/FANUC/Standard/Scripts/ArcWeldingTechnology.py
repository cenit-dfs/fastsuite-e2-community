# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Vendor specific Fanuc arc welding technology
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 2.0
#        Changed by: Hohmann
#        Date: 02/06/24
#        Added touch sensing in surface direction (E2 search)
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
# -------------------------------------------------------------------------------------------
# Global definitions
FILE_NAME = "ArcWeldingTechnology.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug-Technology) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug-Technology) initialization of attributes ended."

DEBUG_INIT_EVENTS_START = "(Debug-Technology) initialization of events started."
DEBUG_INIT_EVENTS_END = "(Debug-Technology) initialization of events ended."

DEBUG_INIT_EVENT_RULES_START = "(Debug-Technology) initialization of event rules started."
DEBUG_INIT_EVENT_RULES_END = "(Debug-Technology) initialization of event rules ended."

DEBUG_INIT_MFGEO_START = "(Debug-Technology) initialization of manufacturing geometry started."
DEBUG_INIT_MFGEO_END = "(Debug-Technology) initialization of manufacturing geometry ended."

DEBUG_PREV_EXECUTE_RECIPE_START = "(Debug-Technology) prev execute recipe started."
DEBUG_PREV_EXECUTE_RECIPE_END = "(Debug-Technology) prev execute recipe ended."

DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START = "(Debug-Technology) post process operation group attributes started."
DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END = "(Debug-Technology) post process operation group attributes ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug-Technology) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug-Technology) post on attribute change ended."

DEBUG_POST_ON_FRAME_CHANGE_START = "(Debug-Technology) post on frame change started."
DEBUG_POST_ON_FRAME_CHANGE_END = "(Debug-Technology) post on frame change ended."

DEBUG_POST_TECH_UPDATE_START = "(Debug-Technology) post technology update started."
DEBUG_POST_TECH_UPDATE_END = "(Debug-Technology) post technology update ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."
ERROR_ON_ATTRIB_CHANGE = "(Error) Could not change attribute in OnAttribChange = "

# Attribute definition
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
AW_TOUCHSENS_FANUC_TOUCHREGISTER="TSTouchOffsetRegister"
MAX_INTEGER = 2147483647
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_TOUCHSENS_APPR_RETR_SPEED = "TouchApprRetrSpeed"
AW_TOUCHSENS_APPR_RETR_FLYBY = "TouchApprFlyBy"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"
AW_SEAMFINDING = "SeamFinding"   
AW_SEAMTRACKING = "SeamTracking"
# Weaving
AW_WEAVE_PATTERN_DEFINE = "WeavePatternDefine"
AW_WEAVE_PATTERN_LITERALS = ["Sine", "Sine 2", "Figure 8", "Circle", "L"]
AW_WEAVE_USE_SCHEDULE_DEFINE = "WeaveUseScheduleDefine"
AW_WEAVE_SCHEDULE_DEFINE = "WeaveScheduleDefine"
AW_WEAVE_PATTERN = "WeavePattern"
AW_WEAVE_USE_SCHEDULE = "WeaveUseSchedule"
AW_WEAVE_SCHEDULE = "WeaveSchedule"
# ArcWelding
AW_WELD_SPEED_TYPE = "WeldSpeedType"
AW_WELD_SPEED_TYPE_LITERALS = ["Value", "WELD_SPEED"]
AW_WELD_SEQUENCE_DEFINE = "WeldSequenceDefine"
AW_WELD_SEQUENCE = "WeldSequence"
# Thru Arc Seam Tracking (ArcSensor)
AW_ARCSENSE = "ArcSense"
AW_ARCSENSE_SCHEDULE = "ArcSenseSchedule"
AW_ARCSENSE_CARRY_ON = "ArcSenseCarryOn"
AW_ARCSENSE_CARRY_ON_SCHEDULE = "ArcSenseCarryOnSchedule"
# Laser Tracking
AW_LASER_TRACKER_ID = "LaserTrackerId"
AW_LASER_TRACKER_SCHEDULE = "LaserTrackerSchedule"
AW_LASER_TRACKER_POS_REGISTER = "LaserTrackerPosRegister"
AW_LASER_TRACKER_DELAY = "LaserTrackerDelay"
# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator: CENPyOlpTech_AttribInitOperator):
   # Get Logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)

   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get controller
   controller = Operator.GetController()
   # check none
   if (attribCreator == None) or (attribGetter == None) or (attribSetter == None) or (controller == None):
      return

   calibMethod = attribGetter.GetAttributeByName(AW_SEAM_CALIBRATION_METHOD)
   #calibMethod.SetOlpProperty(OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)

   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 20, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   attribCreator.AddInteger(AW_TOUCHSENS_FANUC_TOUCHREGISTER, 61,1,99 , PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_FANUC_TOUCHREGISTER)

   speedType = attribCreator.AddEnum(AW_WELD_SPEED_TYPE, AW_WELD_SPEED_TYPE_LITERALS, AW_WELD_SPEED_TYPE_LITERALS[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WELD_SPEED_TYPE)
   speedType.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   # Weld Sequence
   sequence = attribCreator.AddInteger(AW_WELD_SEQUENCE_DEFINE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WELD_SEQUENCE)
   sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   # Weaving
   weavePattern = attribCreator.AddEnum(AW_WEAVE_PATTERN_DEFINE, AW_WEAVE_PATTERN_LITERALS, AW_WEAVE_PATTERN_LITERALS[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_PATTERN)
   weavePattern.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveUseSchedule = attribCreator.AddBool(AW_WEAVE_USE_SCHEDULE_DEFINE, True, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_USE_SCHEDULE)
   weaveUseSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveSchedule = attribCreator.AddInteger(AW_WEAVE_SCHEDULE_DEFINE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_SCHEDULE)
   weaveSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Arc Sensing (TAST) attributes
   arcSense = attribCreator.AddBool(AW_ARCSENSE, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE)
   arcSenseSchedule = attribCreator.AddInteger(AW_ARCSENSE_SCHEDULE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_SCHEDULE)
   carryOn = attribCreator.AddBool(AW_ARCSENSE_CARRY_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_CARRY_ON)
   carrsyOnSchedule = attribCreator.AddInteger(AW_ARCSENSE_CARRY_ON_SCHEDULE, 5, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_CARRY_ON_SCHEDULE)

   # Arc Tracker attributes
   laserTrackerId = attribCreator.AddInteger(AW_LASER_TRACKER_ID, 1, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_ID)
   laserTrackerSchedule = attribCreator.AddInteger(AW_LASER_TRACKER_SCHEDULE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_SCHEDULE)
   laserTrackerPosRegister = attribCreator.AddInteger(AW_LASER_TRACKER_POS_REGISTER, 20, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_POS_REGISTER)
   laserTrackerDelay = attribCreator.AddDouble(AW_LASER_TRACKER_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_TRACKER_DELAY)

   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# # -------------------------------------------------------------------------------------------
# # Technology post event initialization
# def PostTechInitEvents(Operator: CENPyOlpTech_EventInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)

# # -------------------------------------------------------------------------------------------
# # Technology post event rule initialization
# def PostTechInitRules(Operator: CENPyOlpTech_RuleInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)

# # -------------------------------------------------------------------------------------------
# # Technology post manufacturing geometry initialization
# def PostInitManufacturingGeometry(Operator: CENPyOlpTech_MfGeoInitOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_END)

# # -------------------------------------------------------------------------------------------
# # Technology prev execute recipe
# def PrevExecuteRecipe(Operator: CENPyOlpTech_RecipeOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)

# # -------------------------------------------------------------------------------------------
# # Technology post process operation group attributes
# def PostProcessOperationGroupAttributes(Operator: CENPyOlpTech_POGAttribOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator: CENPyOlpTech_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_START)
   
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   attribName = changedAttrib.GetName()

   # show/hide ConnectionType Attribute due to CalibrationMethod
   if (attribName == AW_SEAM_CALIBRATION_METHOD):
      calibrationMethod=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
      # logging.LogInfo('..................found Calibration Method AW_SEAM_CALIBRATION_METHOD=' + calibrationMethod)
      attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
      if (calibrationMethod == AW_SEAMSEARCHING) or (calibrationMethod == AW_TOUCHSENSE_BY_POINT) or (calibrationMethod == AW_TOUCHSENSE_AUTOMATIC):
         attConnectionType.SetVisibility(True)
      else:
         attConnectionType.SetVisibility(False)

      laserTrackerId = attribGetter.GetAttributeByName(AW_LASER_TRACKER_ID)
      laserTrackerSchedule = attribGetter.GetAttributeByName(AW_LASER_TRACKER_SCHEDULE)
      laserTrackerPosRegister = attribGetter.GetAttributeByName(AW_LASER_TRACKER_POS_REGISTER)
      laserTrackerDelay = attribGetter.GetAttributeByName(AW_LASER_TRACKER_DELAY)
      laserTrackerId.SetVisibility(True)
      if (calibrationMethod == AW_SEAMTRACKING) or (calibrationMethod == AW_SEAMFINDING):
         # laserTrackerId.SetVisibility(True)
         laserTrackerSchedule.SetVisibility(True)
         laserTrackerPosRegister.SetVisibility(True)
         laserTrackerDelay.SetVisibility(True)
      else:
         # laserTrackerId.SetVisibility(False)
         laserTrackerSchedule.SetVisibility(False)
         laserTrackerPosRegister.SetVisibility(False)
         laserTrackerDelay.SetVisibility(False)

   # Weaving and Thru the arc sensing attributes
   elif (attribName == "UseWeaveDefine") or (attribName == AW_ARCSENSE) or (attribName == AW_ARCSENSE_CARRY_ON) or (attribName == AW_WEAVE_USE_SCHEDULE_DEFINE) or (attribName == AW_WEAVE_PATTERN_DEFINE):
      useWeaving = attribGetter.GetBool("UseWeaveDefine")
      weaveFreq = attribGetter.GetAttributeByName("WeaveFrequenzDefine")
      weaveWidth = attribGetter.GetAttributeByName("WeaveWidthDefine")
      weaveTime1 = attribGetter.GetAttributeByName("WeaveTime1Define")
      weaveTime2 = attribGetter.GetAttributeByName("WeaveTime2Define")
      weavePattern = attribGetter.GetAttributeByName(AW_WEAVE_PATTERN_DEFINE)
      weavePatternIndex = attribGetter.GetEnumIndex(AW_WEAVE_PATTERN_DEFINE)
      weaveUseSchedule = attribGetter.GetAttributeByName(AW_WEAVE_USE_SCHEDULE_DEFINE)
      weaveUseScheduleValue = attribGetter.GetBool(AW_WEAVE_USE_SCHEDULE_DEFINE)
      weaveSchedule = attribGetter.GetAttributeByName(AW_WEAVE_SCHEDULE_DEFINE)
      arcSense = attribGetter.GetAttributeByName(AW_ARCSENSE)
      useArcSense = attribGetter.GetBool(AW_ARCSENSE)
      arcSenseSchedule = attribGetter.GetAttributeByName(AW_ARCSENSE_SCHEDULE)
      carryOn = attribGetter.GetAttributeByName(AW_ARCSENSE_CARRY_ON)
      useCarryOn = attribGetter.GetBool(AW_ARCSENSE_CARRY_ON)
      carrsyOnSchedule = attribGetter.GetAttributeByName(AW_ARCSENSE_CARRY_ON_SCHEDULE)
      if useWeaving:
         # Weaving
         weavePattern.SetVisibility(True)
         weaveUseSchedule.SetVisibility(True)
         if weaveUseScheduleValue:
            weaveFreq.SetVisibility(False)
            weaveWidth.SetVisibility(False)
            weaveTime1.SetVisibility(False)
            weaveTime2.SetVisibility(False)
            weaveSchedule.SetVisibility(True)
         else:
            weaveFreq.SetVisibility(True)
            weaveWidth.SetVisibility(True)
            weaveTime1.SetVisibility(True)
            weaveTime2.SetVisibility(True)
            weaveSchedule.SetVisibility(False)
         arcSense.SetVisibility(True)
         if weavePatternIndex == 0:
            arcSense.SetReadOnly(False)
         else:
            useArcSense = False
            arcSense.SetReadOnly(True)
         if useArcSense:
            arcSenseSchedule.SetVisibility(True)
            carryOn.SetVisibility(True)
            if useCarryOn:
               carrsyOnSchedule.SetVisibility(True)
            else:
               carrsyOnSchedule.SetVisibility(False)
         else:
            arcSenseSchedule.SetVisibility(False)
            carryOn.SetVisibility(False)
            carrsyOnSchedule.SetVisibility(False)
      else:
         weavePattern.SetVisibility(False)
         weaveUseSchedule.SetVisibility(False)
         weaveFreq.SetVisibility(False)
         weaveWidth.SetVisibility(False)
         weaveTime1.SetVisibility(False)
         weaveTime2.SetVisibility(False)
         weaveSchedule.SetVisibility(False)

         # arcSense.SetVisibility(False)
         arcSense.SetVisibility(False)
         arcSenseSchedule.SetVisibility(False)
         carryOn.SetVisibility(False)
         carrsyOnSchedule.SetVisibility(False)
   elif (attribName == AW_WELD_SPEED_TYPE):
      speedType = attribGetter.GetEnumIndex(AW_WELD_SPEED_TYPE)
      if speedType == 0:
         attribGetter.GetAttributeByName('Speed').SetVisibility(True)
      else:
         attribGetter.GetAttributeByName('Speed').SetVisibility(False)
               

# # -------------------------------------------------------------------------------------------
# # Technology post on frame changed
# def PostTechOnFrameChanged(Operator: CENPyOlpFrameChangedOperator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGED_START)
   
#    # YOUR CODE
   
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGED_END) 
   
#    # Set to True when a recompute is required
#    requestStartWithRuleEventsRecompute = True
#    return requestStartWithRuleEventsRecompute


# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   return 4


# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator: CENPyOlpTech_UpdateOperator):
   logging = Operator.GetLoggerOperator()
   #logging.LogInfo('------------------ ArcWeldingTechnology PostTechUpdate -------------------')
   logging.LogDebug("(Debug) Post tech update started.")
   lastVersion = Operator.GetLastSavedPythonTechnologyVersion()
   # currentVersion = GetPythonTechnologyVersion()
   # logging.LogInfo('Last script version: ' + str(lastVersion) + '. Current script version: ' + str(currentVersion))
   program = Operator.GetOlpProgram()
   attribGetter = Operator.GetAttribGetter(program)
   attribSetter = Operator.GetAttribSetter(program)
   attribCreator = Operator.GetAttribCreator(program)
      
   if (lastVersion < 2):
      #logging.LogInfo('----- PostTechUpdate SavedPythonVersion < 2')
      program = Operator.GetOlpProgram()           
      attribGetter = Operator.GetAttribGetter(program)
      attribSetter = Operator.GetAttribSetter(program)
      attribCreator = Operator.GetAttribCreator(program)

      #calibMethod = attribGetter.GetAttributeByName(AW_SEAM_CALIBRATION_METHOD)
      #calibMethod.SetOlpProperty(OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)

      attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 20, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
      attribCreator.AddInteger(AW_TOUCHSENS_FANUC_TOUCHREGISTER, 61,1,99 , PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_TOUCHSENS_FANUC_TOUCHREGISTER)

      # Arc Weld
      speedType = attribCreator.AddEnum(AW_WELD_SPEED_TYPE, AW_WELD_SPEED_TYPE_LITERALS, AW_WELD_SPEED_TYPE_LITERALS[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WELD_SPEED_TYPE)
      speedType.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      # Weaving
      weavePattern = attribCreator.AddEnum(AW_WEAVE_PATTERN_DEFINE, AW_WEAVE_PATTERN_LITERALS, AW_WEAVE_PATTERN_LITERALS[0], PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_PATTERN_DEFINE)
      weavePattern.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      weaveUseSchedule = attribCreator.AddBool(AW_WEAVE_USE_SCHEDULE_DEFINE, True, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_USE_SCHEDULE_DEFINE)
      weaveUseSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
      weaveSchedule = attribCreator.AddInteger(AW_WEAVE_SCHEDULE_DEFINE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WEAVE_SCHEDULE_DEFINE)
      weaveSchedule.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      # Arc Sensing (TAST) attributes
      arcSense = attribCreator.AddBool(AW_ARCSENSE, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE)
      arcSenseSchedule = attribCreator.AddInteger(AW_ARCSENSE_SCHEDULE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_SCHEDULE)
      carryOn = attribCreator.AddBool(AW_ARCSENSE_CARRY_ON, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_CARRY_ON)
      carrsyOnSchedule = attribCreator.AddInteger(AW_ARCSENSE_CARRY_ON_SCHEDULE, 5, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_CARRY_ON_SCHEDULE)

      # Arc Tracker attributes
      laserTrackerId = attribCreator.AddInteger(AW_LASER_TRACKER_ID, 1, 0, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_ID)
      laserTrackerSchedule = attribCreator.AddInteger(AW_LASER_TRACKER_SCHEDULE, 1, 1, 10, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_SCHEDULE)
      laserTrackerPosRegister = attribCreator.AddInteger(AW_LASER_TRACKER_POS_REGISTER, 20, 1, 99, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_LASER_TRACKER_POS_REGISTER)
      laserTrackerDelay = attribCreator.AddDouble(AW_LASER_TRACKER_DELAY, 0.0, 0.0, 10.0, 0.1, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, AW_LASER_TRACKER_DELAY)

   if (lastVersion < 3):
      #logging.LogInfo('----- PostTechUpdate SavedPythonVersion < 3')
      att01    = attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_SPEED, 0.200,0,1,0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_SPEED)
      att01.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      att02    = attribCreator.AddDouble(AW_TOUCHSENS_APPR_RETR_FLYBY, 0.025,0,0.1,0.005, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_TOUCHSENS_APPR_RETR_FLYBY)
      att02.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
      
      sequenceAttrib = attribGetter.GetAttributeByName(AW_SEAM_CALIBRATION_METHOD)
      if not sequenceAttrib.IsValid():
         logging.LogInfo('PostTechUpdate : AW_WELD_SEQUENCE_DEFINE does NOT exist, will be created !')
         sequence = attribCreator.AddInteger(AW_WELD_SEQUENCE_DEFINE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_WELD_SEQUENCE)
         sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

      componentsList = program.GetChildComponents()
      for component in componentsList:
         compName = component.GetCreatorName()
         #logging.LogInfo('.................................... Component GetCreatorName(component)=' + str(compName))
         componentType = component.GetType()
         if componentType == OLPPROGRAMCOMPONENTTYPE_EVENT:
            attribGetter = Operator.GetAttribGetter(component)
            eventName = component.GetCreatorName()
            #logging.LogInfo('.................................... Event GetCreatorName(component)=' + str(eventName))
            if eventName == "ArcOnEvent":
               #logging.LogInfo('- - - - - - - - - - - - - - - - - -  Event GetCreatorName(component)=' + str(eventName) + ' - - - - - - - - - - - - - - - - - -')
               attribGetter = Operator.GetAttribGetter(component)
               #logging.LogInfo('......................... try getting Attribute AW_WELD_SEQUENCE')
               attribWeldSeq = attribGetter.GetAttributeByName(AW_WELD_SEQUENCE)
               if attribWeldSeq.IsValid():
                  logging.LogInfo('...found AW_WELD_SEQUENCE, n.t.d.')
               else:
                  logging.LogInfo('PostTechUpdate : AW_WELD_SEQUENCE does NOT exist, will be created !')
                  evtAttribCreator = Operator.GetAttribCreator(component)
                  sequence = evtAttribCreator.AddInteger(AW_WELD_SEQUENCE, 1, 0, 100, PROCESS_ATTRIBUTE | USER_ATTRIBUTE, AW_WELD_SEQUENCE)
                  sequence.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
            
   
   completeRecomputeNeeded = ENTERSTATE_STARTWITHRULEEVENTS   

   return completeRecomputeNeeded

def RemoveAttribute(Operator, component, Name):
   if component.GetType() < 4:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttribute(Operator, childComponent, Name)


def RemoveAttributeFromWM(Operator, component, Name, CreatorName):
   if component.GetType() < 4 and component.GetCreatorName()==CreatorName:
      attribGetter = Operator.GetAttribGetter(component)

      att = attribGetter.GetAttributeByName(Name)
      if (att):
         if Operator.RemoveAttribute(component,Name) == False:
            print("Error removing attribute     " + Name)         

   for childComponent in component.GetChildComponents():      
      RemoveAttributeFromWM(Operator, childComponent, Name, CreatorName)
