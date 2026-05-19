# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Adds ArcOn program number to standard event
# Debugg info: E2@localhost:5254
# Author: Schoppenhauer
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

from centypes import *
from cenpylib import *
import inspect, os, json
import sys
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "ArcOnEvent.py: "

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

# Rule event attributes in tech
OTC_WELD_CHARACTER_DEF   = "OTC_WELD_CHARACTER_DEF"
OTC_CURRENT_DEF  = "OTC_CURRENT_DEF"
OTC_VOLTAGE_DEF  = "OTC_VOLTAGE_DEF"
OTC_WIRE_FEED_DEF  = "OTC_WIRE_FEED_DEF"
OTC_WELD_PRGNR_DEF = "OTC_WELD_PRGNR_DEF"
OTC_WELD_OFF_PRGNR_DEF = "OTC_WELD_OFF_PRGNR_DEF"
OTC_USE_WEAVE_DEF = "OTC_USE_WEAVE_DEF"
OTC_WEAVE_COND_NR_DEF  = "OTC_WEAVE_COND_NR_DEF"
#Stitch-Pulse ASS
OTC_STITCH_PULSE_AS_COND_DEF = "OTC_STITCH_PULSE_AS_COND_DEF"
OTC_STITCH_PULSE_AE_COND_DEF = "OTC_STITCH_PULSE_AE_COND_DEF"
OTC_STITCH_PULSE_ENABLED_DEF = "OTC_STITCH_PULSE_ENABLED_DEF"
OTC_STITCH_PULSE_WELDING_TIME_DEF = "OTC_STITCH_PULSE_WELDING_TIME_DEF"
OTC_STITCH_PULSE_COOLING_TIME_DEF = "OTC_STITCH_PULSE_COOLING_TIME_DEF"
OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF = "OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF"
OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF = "OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF"
# event attributes
OTC_WELD_CHARACTER   = "OTC_WELD_CHARACTER"
OTC_CURRENT  = "OTC_CURRENT"
OTC_VOLTAGE  = "OTC_VOLTAGE"
OTC_WIRE_FEED  = "OTC_WIRE_FEED"
OTC_WELD_PRGNR = "OTC_WELD_PRGNR"
OTC_WELD_OFF_PRGNR = "OTC_WELD_OFF_PRGNR"
OTC_USE_WEAVE = "OTC_USE_WEAVE"
OTC_WEAVE_COND_NR  = "OTC_WEAVE_COND_NR"
#Stitch-Pulse ASS
OTC_STITCH_PULSE_AS_COND = "OTC_STITCH_PULSE_AS_COND"
OTC_STITCH_PULSE_AE_COND = "OTC_STITCH_PULSE_AE_COND"
OTC_STITCH_PULSE_ENABLED = "OTC_STITCH_PULSE_ENABLED"
OTC_STITCH_PULSE_WELDING_TIME = "OTC_STITCH_PULSE_WELDING_TIME"
OTC_STITCH_PULSE_COOLING_TIME = "OTC_STITCH_PULSE_COOLING_TIME"
OTC_STITCH_PULSE_MOVEMENT_PITCH = "OTC_STITCH_PULSE_MOVEMENT_PITCH"
OTC_STITCH_PULSE_MOVE_COND_NUMBER = "OTC_STITCH_PULSE_MOVE_COND_NUMBER"
AW_SEAMTRACKING = "SeamTracking"
# Thru Arc Seam Tracking (ArcSensor) Define
AW_ARCSENSE_DEF = "ArcSenseStDef"
AW_ARCSENSE_ST_COND_FILE_DEF = "ArcSenseStCondFileDef"
AW_ARCSENSE_ST_SAMPLE_DATA_DEF = "ArcSenseStSampleDataDef"
AW_ARCSENSE_ET_COND_FILE_DEF = "ArcSenseEtCondFileDef"
# Thru Arc Seam Tracking (ArcSensor)
AW_ARCSENSE = "ArcSenseSt"
AW_ARCSENSE_ST_COND_FILE = "ArcSenseStCondFile"
AW_ARCSENSE_ST_SAMPLE_DATA = "ArcSenseStSampleData"
AW_ARCSENSE_ET_COND_FILE = "ArcSenseEtCondFile"

AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"
AW_SEAMFINDING = "SeamFinding"   
AW_SEAMTRACKING = "SeamTracking"

OTC_ARCON_JSON = "OTC_ARCON_JSON"

def GetEventName():
   return "ArcOnEvent"

# -------------------------------------------------------------------------------------------
# Event post init attributes

def PostInitAttributes(Operator: CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Hide unused default event attributes ProgNumber
   w0 = attribGetter.GetAttributeByName("ProgNumber").SetVisibility(False)
   w1 = attribGetter.GetAttributeByName("WeaveFrequenz").SetVisibility(False)
   w2 = attribGetter.GetAttributeByName("WeaveWidth").SetVisibility(False)
   w3 = attribGetter.GetAttributeByName("WeaveTime1").SetVisibility(False)
   w4 = attribGetter.GetAttributeByName("WeaveTime2").SetVisibility(False)
   w5 = attribGetter.GetAttributeByName("WeaveOnOff").SetVisibility(False)

   weldOnProg = attribCreator.AddInteger(OTC_WELD_PRGNR, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_PRGNR)
   weldOffProg = attribCreator.AddInteger(OTC_WELD_OFF_PRGNR, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_OFF_PRGNR)
   weldChar = attribCreator.AddInteger(OTC_WELD_CHARACTER, 4, 1, 10, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WELD_CHARACTER)
   wireFeed = attribCreator.AddInteger(OTC_WIRE_FEED, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WIRE_FEED)
   current = attribCreator.AddInteger(OTC_CURRENT, 0, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_CURRENT)
   voltage = attribCreator.AddInteger(OTC_VOLTAGE, 0, 0, 9999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_VOLTAGE)
   stitchPulseEnabled = attribCreator.AddBool(OTC_STITCH_PULSE_ENABLED, False, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_ENABLED)
   stitchPulseAsCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AS_COND, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AS_COND)
   stitchPulseAeCond = attribCreator.AddInteger(OTC_STITCH_PULSE_AE_COND, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_STITCH_PULSE_AE_COND)
   stitchPulseWeldingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_WELDING_TIME,0.7, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_WELDING_TIME)
   stitchPulseCoolingTime = attribCreator.AddDouble(OTC_STITCH_PULSE_COOLING_TIME,0.2, 0.0, 100, 1.0, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_TIME, OTC_STITCH_PULSE_COOLING_TIME)
   stitchPulseMovementTime = attribCreator.AddDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH,0.004, 0.0, 0.1, 0.001, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, ATTRIB_LENGTH, OTC_STITCH_PULSE_MOVEMENT_PITCH)
   stitchPulseMoveCondNumber = attribCreator.AddInteger(OTC_STITCH_PULSE_MOVE_COND_NUMBER, 0, 0, 999, PROCESS_ATTRIBUTE | USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_STITCH_PULSE_MOVE_COND_NUMBER)

   # Weave condition
   useWeave = attribCreator.AddBool(OTC_USE_WEAVE, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, OTC_USE_WEAVE)
   weaveCondNr = attribCreator.AddInteger(OTC_WEAVE_COND_NR, 1, 0, 999, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE, OTC_WEAVE_COND_NR)

   # Arc Sensing (FD-AR) attributes
   arcSense = attribCreator.AddBool(AW_ARCSENSE, False, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE)
   arcSenseStCondFile = attribCreator.AddInteger(AW_ARCSENSE_ST_COND_FILE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_COND_FILE)
   arcSenseStSampleData = attribCreator.AddInteger(AW_ARCSENSE_ST_SAMPLE_DATA, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ST_SAMPLE_DATA)
   ArcSenseEtCondFile = attribCreator.AddInteger(AW_ARCSENSE_ET_COND_FILE, 1, 1, 999, PROCESS_ATTRIBUTE |USER_ATTRIBUTE | OPERATION_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_ARCSENSE_ET_COND_FILE)

   arcOnJson = attribCreator.AddString(OTC_ARCON_JSON,'', USER_ATTRIBUTE | PROCESS_ATTRIBUTE, OTC_ARCON_JSON)
   arcOnJson.SetVisibility(False)
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostProcessAttributes(Operator: CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   try:
      # get attribute setter
      attribSetter = Operator.GetAttribSetter()
      # get attribute getter
      attribGetter = Operator.GetAttribGetter()
   except:
      logging.LogError(FILE_NAME + ERROR_ATTRIB_SETTER_GETTER)

   # YOUR CODE
   if (Operator.IsEventCreatedAutomatically() == True):
      ruleEvent = True

      attribSetter.SetInteger(OTC_WELD_PRGNR, attribGetter.GetInteger(OTC_WELD_PRGNR_DEF))
      attribSetter.SetInteger(OTC_WELD_OFF_PRGNR, attribGetter.GetInteger(OTC_WELD_OFF_PRGNR_DEF))
      attribSetter.SetInteger(OTC_WELD_CHARACTER, attribGetter.GetInteger(OTC_WELD_CHARACTER_DEF))
      attribSetter.SetInteger(OTC_WIRE_FEED, attribGetter.GetInteger(OTC_WIRE_FEED_DEF))
      attribSetter.SetInteger(OTC_CURRENT, attribGetter.GetInteger(OTC_CURRENT_DEF))
      attribSetter.SetInteger(OTC_VOLTAGE, attribGetter.GetInteger(OTC_VOLTAGE_DEF))
      
      attribSetter.SetBool(OTC_USE_WEAVE, attribGetter.GetBool(OTC_USE_WEAVE_DEF))
      attribSetter.SetInteger(OTC_WEAVE_COND_NR, attribGetter.GetInteger(OTC_WEAVE_COND_NR_DEF))

      attribSetter.SetBool(AW_ARCSENSE, attribGetter.GetBool(AW_ARCSENSE_DEF))
      attribSetter.SetInteger(AW_ARCSENSE_ST_COND_FILE, attribGetter.GetInteger(AW_ARCSENSE_ST_COND_FILE_DEF))
      attribSetter.SetInteger(AW_ARCSENSE_ST_SAMPLE_DATA, attribGetter.GetInteger(AW_ARCSENSE_ST_SAMPLE_DATA_DEF))
      attribSetter.SetInteger(AW_ARCSENSE_ET_COND_FILE, attribGetter.GetInteger(AW_ARCSENSE_ET_COND_FILE_DEF))

      attribSetter.SetBool(OTC_STITCH_PULSE_ENABLED, attribGetter.GetBool(OTC_STITCH_PULSE_ENABLED_DEF))
      attribSetter.SetInteger(OTC_STITCH_PULSE_AS_COND, attribGetter.GetInteger(OTC_STITCH_PULSE_AS_COND_DEF))
      attribSetter.SetInteger(OTC_STITCH_PULSE_AE_COND, attribGetter.GetInteger(OTC_STITCH_PULSE_AE_COND_DEF))
      attribSetter.SetDouble(OTC_STITCH_PULSE_WELDING_TIME, attribGetter.GetDouble(OTC_STITCH_PULSE_WELDING_TIME_DEF))
      attribSetter.SetDouble(OTC_STITCH_PULSE_COOLING_TIME, attribGetter.GetDouble(OTC_STITCH_PULSE_COOLING_TIME_DEF))
      attribSetter.SetDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH, attribGetter.GetDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH_DEF))
      attribSetter.SetInteger(OTC_STITCH_PULSE_MOVE_COND_NUMBER, attribGetter.GetInteger(OTC_STITCH_PULSE_MOVE_COND_NUMBER_DEF))

   else:
      ruleEvent = False

   # put all ArcOn attribs in a dictionary and store it in a JSON string attrib for easy download
   arcOnInfo = {
      OTC_WELD_PRGNR: str(attribGetter.GetInteger(OTC_WELD_PRGNR)),
      OTC_WELD_OFF_PRGNR: str(attribGetter.GetInteger(OTC_WELD_OFF_PRGNR)),
      OTC_WELD_CHARACTER: str(attribGetter.GetInteger(OTC_WELD_CHARACTER)),
      OTC_WIRE_FEED: str(attribGetter.GetInteger(OTC_WIRE_FEED)),
      OTC_CURRENT: str(attribGetter.GetInteger(OTC_CURRENT)),
      OTC_VOLTAGE: str(attribGetter.GetInteger(OTC_VOLTAGE)),
      OTC_USE_WEAVE: attribGetter.GetBool(OTC_USE_WEAVE),
      OTC_WEAVE_COND_NR: str(attribGetter.GetInteger(OTC_WEAVE_COND_NR)),
      AW_ARCSENSE: attribGetter.GetBool(AW_ARCSENSE),
      AW_ARCSENSE_ST_COND_FILE: str(attribGetter.GetInteger(AW_ARCSENSE_ST_COND_FILE)),
      AW_ARCSENSE_ST_SAMPLE_DATA: str(attribGetter.GetInteger(AW_ARCSENSE_ST_SAMPLE_DATA)),
      AW_ARCSENSE_ET_COND_FILE: str(attribGetter.GetInteger(AW_ARCSENSE_ET_COND_FILE)),
      OTC_STITCH_PULSE_ENABLED: attribGetter.GetBool(OTC_STITCH_PULSE_ENABLED),
      OTC_STITCH_PULSE_AS_COND: str(attribGetter.GetInteger(OTC_STITCH_PULSE_AS_COND)),
      OTC_STITCH_PULSE_AE_COND: str(attribGetter.GetInteger(OTC_STITCH_PULSE_AE_COND)),
      OTC_STITCH_PULSE_WELDING_TIME: str(attribGetter.GetDouble(OTC_STITCH_PULSE_WELDING_TIME)),
      OTC_STITCH_PULSE_COOLING_TIME: str(attribGetter.GetDouble(OTC_STITCH_PULSE_COOLING_TIME)),
      OTC_STITCH_PULSE_MOVEMENT_PITCH: str(attribGetter.GetDouble(OTC_STITCH_PULSE_MOVEMENT_PITCH)*1000),
      OTC_STITCH_PULSE_MOVE_COND_NUMBER: str(attribGetter.GetDouble(OTC_STITCH_PULSE_MOVE_COND_NUMBER)),
      "ruleEvent": str(ruleEvent)
   }
   attribSetter.SetString(OTC_ARCON_JSON, json.dumps(arcOnInfo))
   logging.LogDebug(FILE_NAME + attribGetter.GetString(OTC_ARCON_JSON))   
   pass

def PostOnAttribChanged(Operator: CENPyOlpEvent_AttribChangedOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttributeName()

   calibrationMethod=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
   useWeaving = attribGetter.GetBool(OTC_USE_WEAVE)
   useArcSense = attribGetter.GetBool(AW_ARCSENSE)
   arcSense = attribGetter.GetAttributeByName(AW_ARCSENSE)
   if useWeaving:
      # Weaving
      attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR).SetVisibility(True)
      arcSense.SetVisibility(True)
      if (calibrationMethod == AW_SEAMTRACKING):
         useArcSense = attribSetter.SetBool(AW_ARCSENSE, False)
         arcSense.SetReadOnly(True)
      else:
         arcSense.SetReadOnly(False)
   else:
      attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR).SetVisibility(False)
      # arcSense.SetVisibility(False)
      useArcSense = attribSetter.SetBool(AW_ARCSENSE, False)

   ArcOnVisualize(Operator, changedAttrib)
   pass

#def ArcOnVisualize(Operator: CENPyOlpEvent_AttribChangedOperator, changedAttrib: str):   # Hide unused default event attributes
def ArcOnVisualize(Operator: CENPyOlpEvent_AttribChangedOperator, changedAttrib: str):   # Hide unused default event attributes
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   # changedAttrib = Operator.GetChangedAttributeName()

   # Hide unused default attributes
   attribGetter.GetAttributeByName("WeaveFrequenz").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveWidth").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveTime1").SetVisibility(False)
   attribGetter.GetAttributeByName("WeaveTime2").SetVisibility(False)

   # if useArcSense:
   useArcSense = attribGetter.GetBool(AW_ARCSENSE)
   sense1 = attribGetter.GetAttributeByName(AW_ARCSENSE_ST_COND_FILE)
   sense1.SetVisibility(useArcSense)
   sense2 = attribGetter.GetAttributeByName(AW_ARCSENSE_ST_SAMPLE_DATA)
   sense2.SetVisibility(useArcSense)
   sense3 = attribGetter.GetAttributeByName(AW_ARCSENSE_ET_COND_FILE)
   sense3.SetVisibility(useArcSense)

   # Stitch-Pulse
   useStitchPulse = attribGetter.GetBool(OTC_STITCH_PULSE_ENABLED)
   if (changedAttrib == OTC_STITCH_PULSE_ENABLED) or (changedAttrib == ""):
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_AS_COND).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_AE_COND).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_WELDING_TIME).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_COOLING_TIME).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_MOVEMENT_PITCH).SetVisibility(useStitchPulse)
      attribGetter.GetAttributeByName(OTC_STITCH_PULSE_MOVE_COND_NUMBER).SetVisibility(useStitchPulse)

   # Weld Program or Manual Entries
   if (changedAttrib == OTC_WELD_PRGNR) or (changedAttrib == ""):
      OtcWeldPrgnr = attribGetter.GetInteger(OTC_WELD_PRGNR)
      OtcWeldCharacter = attribGetter.GetAttributeByName(OTC_WELD_CHARACTER)
      OtcWireFeed = attribGetter.GetAttributeByName(OTC_WIRE_FEED)
      OtcCurrent = attribGetter.GetAttributeByName(OTC_CURRENT)
      OtcVoltage = attribGetter.GetAttributeByName(OTC_VOLTAGE)
      if (OtcWeldPrgnr < 1):
         OtcWeldCharacter.SetVisibility(True)
         OtcWireFeed.SetVisibility(True)
         OtcCurrent.SetVisibility(True)
         OtcVoltage.SetVisibility(True)
      else:
         OtcWeldCharacter.SetVisibility(False)
         OtcWireFeed.SetVisibility(False)
         OtcCurrent.SetVisibility(False)
         OtcVoltage.SetVisibility(False)

# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator: CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   
   calibrationMethod=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
   useWeaving = attribGetter.GetBool(OTC_USE_WEAVE)
   useArcSense = attribGetter.GetBool(AW_ARCSENSE)
   arcSense = attribGetter.GetAttributeByName(AW_ARCSENSE)
   if useWeaving:
      # Weaving
      attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR).SetVisibility(True)
      arcSense.SetVisibility(True)
      if (calibrationMethod == AW_SEAMTRACKING):
         arcSense.SetReadOnly(True)
      else:
         arcSense.SetReadOnly(False)
   else:
      attribGetter.GetAttributeByName(OTC_WEAVE_COND_NR).SetVisibility(False)
      # arcSense.SetVisibility(False)

   ArcOnVisualize(Operator, "")
   pass
