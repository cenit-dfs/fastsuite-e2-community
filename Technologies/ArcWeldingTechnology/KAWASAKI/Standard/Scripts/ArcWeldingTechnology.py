# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customisation for Kawasaki
# Debugg info: E2@localhost:5254
# Author: Fasel
# Changelog:
#     Version: 1.0
#        Changed by: Feye
#        Date: 2021-04-08
#
#     Version: 1.1
#        Changed by: MGL
#        Date: 2021-12-15
#
# - Removed unused content
# - QoL and code cleanup
# - Added Batch attrib setter
# - Added Chain Welding Special Mode
# -------------------------------------------------------------------------------------------

# Import libraries

import inspect, os, sys
sys.dont_write_bytecode = True
from centypes import *
import inspect, os
import csv
import ctypes
import sys
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
AW_ARC_PRGNR_DEF = "ProgNumberDefine"
AW_SPEED_WELDING = "Speed"

AW_GROUPNUMBER_DEF = "GroupNumber"

AW_ARCWELDMODE_DEF = "SetArcWeldMode"
AW_ARCWELDMODE_DEFs = ["None","2","3"]
AW_WCMODE_DEF = "WeldConditionMode"
AW_WCMODE_DEFs = ["JobMode","ManualMode","None"] 
AW_WCNUMBER_DEF = "WeldConditionNumber"
AW_WCNAME_DEF = "WeldConditionName"
AW_WCJOBNO_DEF = "JobNumber"

AW_WELDSPEED_DEF = "WC1WeldSpeed"
AW_WELDCURRENT_DEF = "WC1WeldCurrent"
AW_WIREFEEDSPEED_DEF = "WC1WireFeedSpeed"
AW_WELDVOLTAGE_DEF = "WC1WeldVoltage"
AW_ARCLENGTHCORR_DEF = "WC1ArcLengthCorr"
AW_PULSEDYNAMICCORR_DEF = "WC1PulseDynamicCorr"
AW_WIRERETRACTCORR_DEF = "WC1WireRetractCorr"


AW_CRATER_DEF = "WC2Crater"
AW_CRATERNUMBER_DEF = "CraterSpotConditionNumber"
AW_CRATERNAME_DEF = "CraterSpotConditionName"
AW_CRATERJOBNO_DEF = "CraterSpotJobNumber"

AW_TIME_DEF = "WC2Time"
AW_CRATERWIREFEEDSPEED_DEF = "WC2WireFeedSpeed"
AW_CRATERWELDCURRENT_DEF = "WC2WeldCurrent"
AW_CRATERARCLENGTHCORR_DEF = "WC2ArcLengthCorr"
AW_CRATERWELDVOLTAGE_DEF = "WC2WeldVoltage"
AW_CRATERPULSEDYNAMICCORR_DEF = "WC2PulseDynamicCorr"
AW_CRATERWIRERETRACTCORR_DEF = "WC2WireRetractCorr"

AW_WEAVE_PATTERN_NO_DEF = "WCWeavePatternNumber"
AW_WEAVE_PATTERN_NO_DEFs = ["no weaving","harmonic","harmonic with end stop","reciprocating triangular","circular clockwise","circular counterclockwise","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_WEAVEFREQUENZ_DEF = "WCWeaveFrequenz"
AW_WEAVEWIDTH_DEF = "WCWeaveWidth"

#SPS Event
AW_SPS_PATTERN_NO_DEF = "WCStartPointSensing"
AW_SPS_PATTERN_NO_DEFs = ["None","Disabled","horizontal fillet","flat fillet","V groove","flat bevel groove","bevel groove","horizontal bevel groove","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_SPSSD_DEF = "WCStartDist"
AW_SPSTPRD_DEF = "WCReliefDist"
AW_SPSSDG_DEF = "WCDistInGroove"

#RTPM
AW_RTPM_DEF = "WCRTPM"
AW_RTPM_DEFs = ["None","Disabled","Enabled"]
AW_RTPM_WS_DEF = "WCWireStick"
AW_RTPM_VG_DEF = "WCVerticalGain"
AW_RTPM_HG_DEF = "WCHorizontalGain"
AW_RTPM_VB_DEF = "WCVerticalBIAS"
AW_RTPM_HB_DEF = "WCHorizontalBIAS"
AW_RTPM_SG_DEF = "WCStartGain"
AW_RTPM_II_DEF = "WCDelayTime"
AW_RTPM_IT_DEF = "WCInitialGainTime"
AW_RTPM_IVC_DEF = "WCInitialVerticalCurrent"
AW_RTPM_IHC_DEF = "WCInitialHorizontalCurrent"
AW_RTPM_ICC_DEF = "WCInitialChangeCurrent"

#Software Slow Down 
AW_SSD_DEF = "WCSSDown"
AW_SSD_DEFs = ["None","Disabled","Enabled"]
AW_SSD_PHT_DEF = "WCPreHeatTime"
AW_SSD_WP_DEF = "WCWeavePattern"
AW_SSD_WP_DEFs = ["no weaving","harmonic","harmonic with end stop","reciprocating triangular","circular clockwise","circular counterclockwise","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_SSD_WF_DEF = "WCWeaveFreq"
AW_SSD_WW_DEF = "WCWeaveWidth1"

LT_ACTIV_DEF = "LTActiv"

AW_ARCWELDMODE_DL = "DLSetArcWeldMode"

WC1Data = []
WC2Data = []

#Chain Mode
CW_CHAIN_MODE = "CWChainMode"
CW_CHAIN_BEGIN = "ChainBegin"
CW_CHAIN_END = "ChainEnd"

#Ref mode
RF_REF_MODE = "RefMode"

#Touch Sense
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
MAX_INTEGER = 2147483647
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENSE_BY_POINT    = "TouchSensByPoint"
AW_TOUCHSENSE_AUTOMATIC   = "TouchSensAutomatic"
AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
AW_SEAMSEARCHING = "SeamSearching"

# -------------------------------------------------------------------------------------------

def ReadCsv(index, mode,wcTypeNumber):
   # Read the Kawasaki WeldCondition data
   path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
   
   if mode == 1:
      if wcTypeNumber == 2:
         filename = 'CraterCondition_ManMode.csv'
      else:
         filename = 'WeldCondition_ManMode.csv'
   else:
      if wcTypeNumber == 2:
         filename = 'CraterCondition_JobMode.csv'
      else:
         filename = 'WeldCondition_JobMode.csv'

   try:
      CsvData = []
      
      # read content from the file

      with open(path + filename, 'r') as csvfile:
         csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
         # ignore the first line
         next(csv_reader)
         # reading line by line until the end of the file
         # the content is added to the end of the list, until everyting in read
         for row in csv_reader:
            CsvData.append(row)

   except:
      print('Error')

   DataList = []
   DataList.clear

   if index <= len(CsvData):
      CsvDataColumn = CsvData[index - 1]
      
      if mode == 1:
         # Manual Mode Data
         DataList.append(CsvDataColumn[1])                   # Weld Condition Name
         DataList.append(99)                                 # JobNo
         if wcTypeNumber == 2:
            # Manual Mode Data Crater Condition
            DataList.append(CsvDataColumn[2].replace(",","."))  # Crater Time
            DataList.append(0.0)                                # Crater Wire Feed Speed
            DataList.append(CsvDataColumn[3].replace(",","."))  # Crater Weld Current
            DataList.append(0.0)                                # Crater Arc Length corr.
            DataList.append(CsvDataColumn[4].replace(",","."))  # Crater Weld Voltage
            DataList.append(CsvDataColumn[5].replace(",","."))  # Crater Pulse Dynamic corr.
            DataList.append(CsvDataColumn[6].replace(",","."))  # Crater Wire Retract corr.
         else:
            # Manual Mode Data Weld Condition
            DataList.append(CsvDataColumn[2].replace(",","."))  # Weld Speed
            DataList.append(0.0)                                # Wire Feed Speed
            DataList.append(CsvDataColumn[3].replace(",","."))  # Weld Current
            DataList.append(0.0)                                # Arc Length corr.
            DataList.append(CsvDataColumn[4].replace(",","."))  # Weld Voltage
            DataList.append(CsvDataColumn[5].replace(",","."))  # Pulse Dynamic corr.
            DataList.append(CsvDataColumn[6].replace(",","."))  # Wire Retract corr.
      else:
         # Job Mode Data
         DataList.append(CsvDataColumn[1])                   # Weld Condition Name
         DataList.append(CsvDataColumn[2].replace(",","."))  # JobNo
         if wcTypeNumber == 2:
            # Manual Mode Data Crater Condition
            DataList.append(CsvDataColumn[3].replace(",","."))  # Crater Time
            DataList.append(CsvDataColumn[4].replace(",","."))  # Crater Wire Feed Speed
            DataList.append(0.0)                                # Crater Weld Current
            DataList.append(CsvDataColumn[5].replace(",","."))  # Crater Arc Length corr.
            DataList.append(0.0)                                # Crater Weld Voltage
            DataList.append(CsvDataColumn[6].replace(",","."))  # Crater Pulse Dynamic corr.
            DataList.append(CsvDataColumn[7].replace(",","."))  # Crater Wire Retract corr.
         else:
            DataList.append(CsvDataColumn[3].replace(",","."))  # Weld Speed
            DataList.append(CsvDataColumn[4].replace(",","."))  # Wire Feed Speed
            DataList.append(0.0)                                # Weld Current
            DataList.append(CsvDataColumn[5].replace(",","."))  # Arc Length corr.
            DataList.append(0.0)                                # Weld Voltage
            DataList.append(CsvDataColumn[6].replace(",","."))  # Pulse Dynamic corr.
            DataList.append(CsvDataColumn[7].replace(",","."))  # Wire Retract corr.
   else:
      if wcTypeNumber == 2:
         DataList.append('not defined')
         DataList.append(0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
      else:
         DataList.append('not defined')
         DataList.append(0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)
         DataList.append(0.0)

   return DataList

def SetWCAttribute(attribSetter, logging, WCData, wcTypeNumber):
   if wcTypeNumber == 2:
      try:
         attribSetter.SetString(AW_CRATERNAME_DEF, WCData[0])
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERNAME_DEF!')

      try:
         attribSetter.SetInteger(AW_CRATERJOBNO_DEF, int(WCData[1]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERJOBNO_DEF!')         

      try:
         attribSetter.SetDouble(AW_TIME_DEF, float(WCData[2]))
      except:
         logging.LogError('Cannot set the Attribute AW_TIME_DEF!')

      try:
         attribSetter.SetDouble(AW_CRATERWIREFEEDSPEED_DEF, float(WCData[3]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWIREFEEDSPEED_DEF!')      
                     
      try:
         attribSetter.SetDouble(AW_CRATERWELDCURRENT_DEF, float(WCData[4]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWELDCURRENT_DEF!')

      try:
         attribSetter.SetDouble(AW_CRATERARCLENGTHCORR_DEF, float(WCData[5]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERARCLENGTHCORR_DEF!')      
            
      try:
         attribSetter.SetDouble(AW_CRATERWELDVOLTAGE_DEF, float(WCData[6]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWELDVOLTAGE_DEF!')
            
      try:
         attribSetter.SetDouble(AW_CRATERPULSEDYNAMICCORR_DEF, float(WCData[7]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERPULSEDYNAMICCORR_DEF!')
      try:
         attribSetter.SetDouble(AW_CRATERWIRERETRACTCORR_DEF, float(WCData[8]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERPULSEDYNAMICCORR_DEF!')

   else:
      # set the active Welding Speed
      arcSpeedValue = float(WCData[2]) / 6000
      try:
         attribSetter.SetDouble(AW_SPEED_WELDING, arcSpeedValue)
      except:
         logging.LogError('Cannot set the Attribute AW_SPEED_WELDING!')         

      # Set the Kawasaki Weld Condition attributes
      try:
         attribSetter.SetString(AW_WCNAME_DEF, WCData[0])
      except:
         logging.LogError('Cannot set the Attribute AW_WCNAME_DEF!')

      try:
         attribSetter.SetInteger(AW_WCJOBNO_DEF, int(WCData[1]))
      except:
         logging.LogError('Cannot set the Attribute AW_WCJOBNO_DEF!')         
         
      try:
         attribSetter.SetInteger(AW_ARC_PRGNR_DEF, int(WCData[1]))
      except:
         logging.LogError('Cannot set the Attribute AW_ARC_PRGNR_DEF!')      
         
      try:
         attribSetter.SetDouble(AW_WELDSPEED_DEF, float(WCData[2]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDSPEED_DEF!')

      try:
         attribSetter.SetDouble(AW_WIREFEEDSPEED_DEF, float(WCData[3]))
      except:
         logging.LogError('Cannot set the Attribute AW_WIREFEEDSPEED_DEF!')
         
      try:
         attribSetter.SetDouble(AW_WELDCURRENT_DEF, float(WCData[4]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDCURRENT_DEF!')

      try:
         attribSetter.SetDouble(AW_ARCLENGTHCORR_DEF, float(WCData[5]))
      except:
         logging.LogError('Cannot set the Attribute AW_ARCLENGTHCORR_DEF!')

      try:
         attribSetter.SetDouble(AW_WELDVOLTAGE_DEF, float(WCData[6]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDVOLTAGE_DEF!')

      try:
         attribSetter.SetDouble(AW_PULSEDYNAMICCORR_DEF, float(WCData[7]))
      except:
         logging.LogError('Cannot set the Attribute AW_PULSEDYNAMICCORR_DEF!')

      try:
         attribSetter.SetDouble(AW_WIRERETRACTCORR_DEF, float(WCData[8]))
      except:
         logging.LogError('Cannot set the Attribute AW_WIRERETRACTCORR_DEF!')

def PostTechInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   calibMethod = attribGetter.GetAttributeByName(AW_SEAM_CALIBRATION_METHOD)
   #calibMethod.SetOlpProperty(GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
   calibMethod.SetVisibility(True)

   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 1, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)

   # Read the Kawasaki Weld Condition file
   WCNumber = 1
   WC1Data = ReadCsv(WCNumber, 0, 1)

   # Read the Kawasaki Crater Condition file
   CCNumber = 1
   WC2Data = ReadCsv(CCNumber, 0, 2)

   # GROUP Number
   attGPN = attribCreator.AddInt(AW_GROUPNUMBER_DEF, 0, -1, 6, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_GROUPNUMBER_DEF)
   attGPN.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # Create Kawasaki WELD Mode attribute
   attWM1 = attribCreator.AddEnum(AW_ARCWELDMODE_DEF, AW_ARCWELDMODE_DEFs, AW_ARCWELDMODE_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_ARCWELDMODE_DEF)
   attWM1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Create Kawasaki WELD CONDITION 1 (Basic Condition) attributes
   attWC1_1 = attribCreator.AddEnum(AW_WCMODE_DEF, AW_WCMODE_DEFs, AW_WCMODE_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_WCMODE_DEF)
   attWC1_1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attWC1_2 = attribCreator.AddInt(AW_WCNUMBER_DEF, WCNumber, 1, 199, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_WCNUMBER_DEF)
   attWC1_2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   attWC1_3 = attribCreator.AddString(AW_WCNAME_DEF, WC1Data[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_WCNAME_DEF)
   attWC1_3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   attWC1_3.SetReadOnly(True)

   attWC1_4 = attribCreator.AddInt(AW_WCJOBNO_DEF, int(WC1Data[1]), 1, 65535, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_WCJOBNO_DEF)
   attWC1_4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_4.SetReadOnly(False)

   attWC1_5 = attribCreator.AddDouble(AW_WELDSPEED_DEF, float(WC1Data[2]), 1.0, 999.0, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDSPEED_DEF)
   attWC1_5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_5.SetReadOnly(False)

   attWC1_6_JM_S1 = attribCreator.AddDouble(AW_WIREFEEDSPEED_DEF, float(WC1Data[3]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WIREFEEDSPEED_DEF)
   attWC1_6_JM_S1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_6_JM_S1.SetReadOnly(True)

   attWC1_7_MM_S1 = attribCreator.AddDouble(AW_WELDCURRENT_DEF, float(WC1Data[4]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDCURRENT_DEF)
   attWC1_7_MM_S1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_7_MM_S1.SetVisibility(False)

   attWC1_8_JM_S2 = attribCreator.AddDouble(AW_ARCLENGTHCORR_DEF, float(WC1Data[5]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_ARCLENGTHCORR_DEF)
   attWC1_8_JM_S2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_8_JM_S2.SetReadOnly(True)
   
   attWC1_9_MM_S2 = attribCreator.AddDouble(AW_WELDVOLTAGE_DEF, float(WC1Data[6]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDVOLTAGE_DEF)
   attWC1_9_MM_S2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_9_MM_S2.SetVisibility(False)

   attWC1_10_S3 = attribCreator.AddDouble(AW_PULSEDYNAMICCORR_DEF, float(WC1Data[7]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_PULSEDYNAMICCORR_DEF)
   attWC1_10_S3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_10_S3.SetReadOnly(True)

   attWC1_11_S4 = attribCreator.AddDouble(AW_WIRERETRACTCORR_DEF, float(WC1Data[8]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WIRERETRACTCORR_DEF)
   attWC1_11_S4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC1_11_S4.SetReadOnly(True)

   # Create Kawasaki WELD CONDITION 2 (Crater Condition) attributes
   attWC2_1 = attribCreator.AddBool(AW_CRATER_DEF, True, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_CRATER_DEF)
   attWC2_1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   attWC2_2 = attribCreator.AddInt(AW_CRATERNUMBER_DEF, CCNumber, 1, 299, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_CRATERNUMBER_DEF)
   attWC2_2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   attWC2_3 = attribCreator.AddString(AW_CRATERNAME_DEF, WC2Data[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_CRATERNAME_DEF)
   attWC2_3.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   attWC2_3.SetReadOnly(True)

   attWC2_4 = attribCreator.AddInt(AW_CRATERJOBNO_DEF, int(WC2Data[1]), 1, 65535, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_CRATERJOBNO_DEF)
   attWC2_4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   attWC2_5 = attribCreator.AddDouble(AW_TIME_DEF, float(WC2Data[2]), 0.0, 9.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_TIME_DEF)
   attWC2_5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_5.SetReadOnly(False)

   attWC2_6_JM_S1 = attribCreator.AddDouble(AW_CRATERWIREFEEDSPEED_DEF, float(WC2Data[3]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIREFEEDSPEED_DEF)
   attWC2_6_JM_S1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_6_JM_S1.SetReadOnly(True)

   attWC2_7_MM_S1 = attribCreator.AddDouble(AW_CRATERWELDCURRENT_DEF, float(WC2Data[4]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDCURRENT_DEF)
   attWC2_7_MM_S1.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_7_MM_S1.SetVisibility(False)

   attWC2_8_JM_S2 = attribCreator.AddDouble(AW_CRATERARCLENGTHCORR_DEF, float(WC2Data[5]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERARCLENGTHCORR_DEF)
   attWC2_8_JM_S2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_8_JM_S2.SetReadOnly(True)

   attWC2_9_MM_S2 = attribCreator.AddDouble(AW_CRATERWELDVOLTAGE_DEF, float(WC2Data[6]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDVOLTAGE_DEF)
   attWC2_9_MM_S2.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_9_MM_S2.SetVisibility(False)

   attWC2_10_S3 = attribCreator.AddDouble(AW_CRATERPULSEDYNAMICCORR_DEF, float(WC2Data[7]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERPULSEDYNAMICCORR_DEF)
   attWC2_10_S3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_10_S3.SetReadOnly(True)

   attWC2_11_S4 = attribCreator.AddDouble(AW_CRATERWIRERETRACTCORR_DEF, float(WC2Data[8]), -999.9, 999.9, 1.0, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIRERETRACTCORR_DEF)
   attWC2_11_S4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   attWC2_11_S4.SetReadOnly(True)
  
   att16 = attribGetter.GetAttributeByName(AW_ARC_PRGNR_DEF)
   att17 = attribGetter.GetAttributeByName(AW_SPEED_WELDING)

   # Set the active Welding Speed
   arcSpeedValue = float(WC1Data[2]) / 6000
   try:
      attribSetter.SetDouble(AW_SPEED_WELDING, arcSpeedValue)
   except:
      logging.LogError('Cannot set the Attribute AW_SPEED_WELDING!')

   # Group Kawasaki Weld Condition Attributes
   groupKawasaki_WC = attribCreator.AddAttribGroup("Kawasaki_WC")
   groupKawasaki_WC.AddAttribute(attWC1_1)
   groupKawasaki_WC.AddAttribute(attWC1_2)
   groupKawasaki_WC.AddAttribute(attWC1_3)
   groupKawasaki_WC.AddAttribute(attWC1_4)
   groupKawasaki_WC.AddAttribute(attWC1_5)
   groupKawasaki_WC.AddAttribute(attWC1_6_JM_S1)
   groupKawasaki_WC.AddAttribute(attWC1_7_MM_S1)
   groupKawasaki_WC.AddAttribute(attWC1_8_JM_S2)
   groupKawasaki_WC.AddAttribute(attWC1_9_MM_S2)
   groupKawasaki_WC.AddAttribute(attWC1_10_S3)
   groupKawasaki_WC.AddAttribute(attWC1_11_S4)
   groupKawasaki_WC.AddAttribute(att16)
   groupKawasaki_WC.AddAttribute(att17)
   groupKawasaki_WC.AddAttribute(attWC2_1)
   groupKawasaki_WC.AddAttribute(attWC2_2)
   groupKawasaki_WC.AddAttribute(attWC2_3)
   groupKawasaki_WC.AddAttribute(attWC2_4)
   groupKawasaki_WC.AddAttribute(attWC2_5)
   groupKawasaki_WC.AddAttribute(attWC2_6_JM_S1)
   groupKawasaki_WC.AddAttribute(attWC2_7_MM_S1)
   groupKawasaki_WC.AddAttribute(attWC2_8_JM_S2)
   groupKawasaki_WC.AddAttribute(attWC2_9_MM_S2)
   groupKawasaki_WC.AddAttribute(attWC2_10_S3)
   groupKawasaki_WC.AddAttribute(attWC2_11_S4)

   # Set the ProgNumber
   try:
      attribSetter.SetInteger(AW_ARC_PRGNR_DEF, int(WC1Data[1]))
   except:
      logging.LogError('Cannot set the Attribute AW_ARC_PRGNR_DEF!')

   # Add Weave Pattern Number
   weavePNAtt = attribCreator.AddEnum(AW_WEAVE_PATTERN_NO_DEF, AW_WEAVE_PATTERN_NO_DEFs, AW_WEAVE_PATTERN_NO_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_WEAVE_PATTERN_NO_DEF)
   weavePNAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Add Weave Frequenz
   weaveFAtt = attribCreator.AddDouble(AW_WEAVEFREQUENZ_DEF, 0.0, 0.0, 4.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_WEAVEFREQUENZ_DEF)
   weaveFAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveFAtt.SetVisibility(False)

   # Add Weave Width
   weaveWAtt = attribCreator.AddDouble(AW_WEAVEWIDTH_DEF, 0.0, 0.0, 0.04, 0.001, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_LENGTH, AW_WEAVEWIDTH_DEF)
   weaveWAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   weaveWAtt.SetVisibility(False)

   # Group Kawasaki Weave Attributes
   groupKawasaki_Weave = attribCreator.AddAttribGroup("Kawasaki_Weave")
   groupKawasaki_Weave.AddAttribute(weavePNAtt)
   groupKawasaki_Weave.AddAttribute(weaveFAtt)
   groupKawasaki_Weave.AddAttribute(weaveWAtt)
   
  # Add SPS Pattern Number
   spsPNAtt = attribCreator.AddEnum(AW_SPS_PATTERN_NO_DEF, AW_SPS_PATTERN_NO_DEFs, AW_SPS_PATTERN_NO_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_SPS_PATTERN_NO_DEF)
   spsPNAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # Add SPS start distance
   spsSDAtt = attribCreator.AddDouble(AW_SPSSD_DEF, 0.0, 0.0, 99.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSSD_DEF)
   spsSDAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   spsSDAtt.SetVisibility(False)

   # Add SPS relief distance
   spsTPRDAtt = attribCreator.AddDouble(AW_SPSTPRD_DEF, 0.0, 0.0, 99.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSTPRD_DEF)
   spsTPRDAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   spsTPRDAtt.SetVisibility(False)

   # Add SPS distance in groove
   spsSDGAtt = attribCreator.AddDouble(AW_SPSSDG_DEF, 0.0, 0.0, 99.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSSDG_DEF)
   spsSDGAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   spsSDGAtt.SetVisibility(False)

   # Group Kawasaki SPS Attributes
   groupKawasaki_Sps = attribCreator.AddAttribGroup("Kawasaki_SPS")
   groupKawasaki_Sps.AddAttribute(spsPNAtt)
   groupKawasaki_Sps.AddAttribute(spsSDAtt)
   groupKawasaki_Sps.AddAttribute(spsTPRDAtt)
   groupKawasaki_Sps.AddAttribute(spsSDGAtt)   
   
   # Add RTPM ON/OFF 
   rtpmAtt = attribCreator.AddEnum(AW_RTPM_DEF, AW_RTPM_DEFs, AW_RTPM_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_DEF)
   rtpmAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   #Add RTPM Wire Stick Out
   rtpmWSAtt = attribCreator.AddInt(AW_RTPM_WS_DEF, 0, 0, 65535, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_WS_DEF)
   rtpmWSAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmWSAtt.SetVisibility(False)
   
   # Add RTPM Vertical Gain
   rtpmVgAtt = attribCreator.AddInt(AW_RTPM_VG_DEF, 0, -1000, 1000, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_VG_DEF)
   rtpmVgAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmVgAtt.SetVisibility(False)

   # Add RTPM Horizontal Gain 
   rtpmHgAtt = attribCreator.AddInt(AW_RTPM_HG_DEF, 0, -1000, 1000, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_HG_DEF)
   rtpmHgAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmHgAtt.SetVisibility(False)
   
   # Add RTPM Vertical BIAS
   rtpmVbAtt = attribCreator.AddInt(AW_RTPM_VB_DEF, 0, -1000, 1000, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_VB_DEF)
   rtpmVbAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmVbAtt.SetVisibility(False)
    
   # Add RTPM Horizontal BIAS
   rtpmHbAtt = attribCreator.AddInt(AW_RTPM_HB_DEF,  0, -1000, 1000, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_HB_DEF)
   rtpmHbAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmHbAtt.SetVisibility(False)

   # Add RTPM Delay Time for integral interval
   rtpmIiAtt = attribCreator.AddInt(AW_RTPM_II_DEF, 0, 0, 10, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_II_DEF)
   rtpmIiAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmIiAtt.SetVisibility(False)
   
   # Add RTPM Start Gain
   rtpmSgAtt = attribCreator.AddBool(AW_RTPM_SG_DEF, True, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_SG_DEF)
   rtpmSgAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmSgAtt.SetVisibility(False)

   # Add RTPM WC Initial gain time
   rtpmItAtt = attribCreator.AddDouble(AW_RTPM_IT_DEF, 0.1, 0.1, 9.9, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_RTPM_IT_DEF)
   rtpmItAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmItAtt.SetVisibility(False)
  
  # Add RTPM WC up-down gain
   rtpmIvcAtt = attribCreator.AddInt(AW_RTPM_IVC_DEF, 0, -1000, 1000, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_IVC_DEF)
   rtpmIvcAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmIvcAtt.SetVisibility(False)
   
   # Add RTPM WC lateral BIAS
   rtpmIhcAtt = attribCreator.AddInt(AW_RTPM_IHC_DEF,  0, -1000, 1000,GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_IHC_DEF)
   rtpmIhcAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmIhcAtt.SetVisibility(False)  

   # Add RTPM WC additional value after time elapse
   rtpmIccAtt = attribCreator.AddInt(AW_RTPM_ICC_DEF,  0, -1000, 1000,GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_RTPM_ICC_DEF)
   rtpmIccAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   rtpmIccAtt.SetVisibility(False)  
   
   # Group Kawasaki RTPM Attributes
   groupKawasaki_Rtpm = attribCreator.AddAttribGroup("Kawasaki_RTPM")
   groupKawasaki_Rtpm.AddAttribute(rtpmAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmWSAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmVgAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmHgAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmVbAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmHbAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmIiAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmSgAtt)   
   groupKawasaki_Rtpm.AddAttribute(rtpmItAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmIvcAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmIhcAtt)
   groupKawasaki_Rtpm.AddAttribute(rtpmIccAtt)  
   
   # Add Software Slow Down
   ssdAtt = attribCreator.AddEnum(AW_SSD_DEF, AW_SSD_DEFs, AW_SSD_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_SSD_DEF)
   ssdAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   
   #Add Software Slow Down Preheat Time
   ssdPhtAtt = attribCreator.AddDouble(AW_SSD_PHT_DEF, 0.0, 0, 9.9, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_PHT_DEF)
   ssdPhtAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   ssdPhtAtt.SetVisibility(False)
   
   #Add Software Slow Down Weave Pattern
   ssdWpAtt = attribCreator.AddEnum(AW_SSD_WP_DEF, AW_SSD_WP_DEFs, AW_SSD_WP_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_SSD_WP_DEF)
   ssdWpAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   ssdWpAtt.SetVisibility(False)
   
   #Add Software Slow Down Weave Frequrency
   ssdWftAtt = attribCreator.AddDouble(AW_SSD_WF_DEF, 0.0, 0, 4.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WF_DEF)
   ssdWftAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   ssdWftAtt.SetVisibility(False)
   
   #Add Software Slow Down Weave Width
   ssdWwtAtt = attribCreator.AddDouble(AW_SSD_WW_DEF, 0.0, 0, 40.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WW_DEF)
   ssdWwtAtt.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   ssdWwtAtt.SetVisibility(False)
   
   # Group Kawasaki SoftwareSlowDown Attributes
   groupKawasaki_Ssd = attribCreator.AddAttribGroup("Kawasaki_SSD")
   groupKawasaki_Ssd.AddAttribute(ssdAtt)
   groupKawasaki_Ssd.AddAttribute(ssdPhtAtt)
   groupKawasaki_Ssd.AddAttribute(ssdWpAtt)
   groupKawasaki_Ssd.AddAttribute(ssdWftAtt)
   groupKawasaki_Ssd.AddAttribute(ssdWwtAtt)
   
   # Chain Mode - special option 
   cMode = attribCreator.AddBool(CW_CHAIN_MODE, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, CW_CHAIN_MODE)
   rMode = attribCreator.AddBool(RF_REF_MODE, False, GLOBAL_ATTRIBUTE | USER_ATTRIBUTE, RF_REF_MODE)
   
   # Touch Sense
   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 0, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   attConnectionType = attribGetter.GetAttributeEnumByName(AW_TOUCHSENS_CONNECT_TYPE)
   attConnectionType.SetOlpProperty(GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE)
   attConnectionType.SetVisibility(False)
   attConnectionType.AddLiteral("Frame3pConnect")
   
   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)
# -------------------------------------------------------------------------------------------

# Technology post event initialization
def PostTechInitEvents(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

   try:
      # Register additional olp events here
      Operator.RegisterPyTechnologyEvent('ArcWeldConditionEvent.py')
   except:
      logging.LogError('Cannot register python Event "ArcWeldConditionEvent.py"')

   try:
      # Register additional olp events here
      Operator.RegisterPyTechnologyEvent('SPSEvent.py')
   except:
      logging.LogError('Cannot register python Event "SPSEvent.py"')

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_END)


# -------------------------------------------------------------------------------------------
# Technology post event rule initialization
# def PostTechInitRules(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENT_RULES_END)


# -------------------------------------------------------------------------------------------
# Technology post manufacturing geometry initialization
# def PostInitManufacturingGeometry(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_MFGEO_END)


# -------------------------------------------------------------------------------------------
# Technology PrevExecuteRecipe
# def PrevExecuteRecipe(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_PREV_EXECUTE_RECIPE_END)

   
# -------------------------------------------------------------------------------------------
# Technology post process operation group attributes
# def PostProcessOperationGroupAttributes(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_START)

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_OPERATION_GROUP_ATTRIB_END)


# -------------------------------------------------------------------------------------------
# Technology post on attribute change
def PostTechOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get changed attribute
   changedAttrib = Operator.GetChangedAttribute()

   # Customizing Start   
   attribName = changedAttrib.GetName()

   # logging.LogInfo('---------------------------------------------------- ArcWeldingtech AttribChange!')       

   # Get the Weld Condition Mode - Job Mode (Index 0) or Manual Mode (Index 1) or None (Index 2)
   try:
      WCModeIndex = attribGetter.GetEnumIndex(AW_WCMODE_DEF)
   except:
      logging.LogError('Cannot get the Attribute AW_WCMODE_DEF!')

   # Get the Crater Mode
   try:
      CraterMode = attribGetter.GetBool(AW_CRATER_DEF)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATER_DEF!')

   # Get the Weld Condition Number
   try:
      WCNumber = attribGetter.GetInteger(AW_WCNUMBER_DEF)
   except:
      logging.LogError('Cannot get the Attribute AW_WCNUMBER_DEF!')

   # Get the Crater Condition Number
   try:
      CCNumber = attribGetter.GetInteger(AW_CRATERNUMBER_DEF)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNUMBER_DEF!')
  
   if attribName == AW_WCMODE_DEF:
      WCModeIndex = attribGetter.GetEnumIndex(AW_WCMODE_DEF)

      # Set OP Attribute Visu
      SetWCAttributeVisu(attribGetter, logging, WCModeIndex, CraterMode)

      # Read the Kawasaki WeldCondition file
      WC1Data = ReadCsv(WCNumber, WCModeIndex, 1)

      # Read the Kawasaki CraterCondition file
      WC2Data = ReadCsv(CCNumber, WCModeIndex, 2)

      # Set the Kawasaki WC1 Attributes
      SetWCAttribute(attribSetter, logging, WC1Data, 1)

      # Set the Kawasaki WC2 Attributes
      SetWCAttribute(attribSetter, logging, WC2Data, 2)

   if attribName == AW_WCNUMBER_DEF:
      # Read the Kawasaki WeldCondition file
      WCNumber = attribGetter.GetInteger(AW_WCNUMBER_DEF)
      WC1Data = ReadCsv(WCNumber, WCModeIndex, 1)

      # Set the Kawasaki WC1 Attributes
      SetWCAttribute(attribSetter, logging, WC1Data, 1)
      
      # Set the active Welding Speed
      arcSpeedValue = float(WC1Data[2]) / 6000
      try:
         attribSetter.SetDouble(AW_SPEED_WELDING, arcSpeedValue)
      except:
         logging.LogError('Cannot set the Attribute AW_SPEED_WELDING!')

   if attribName == AW_CRATERNUMBER_DEF:
      # Read the Kawasaki CraterCondition file
      CCNumber = attribGetter.GetInteger(AW_CRATERNUMBER_DEF)
      WC2Data = ReadCsv(CCNumber, WCModeIndex, 2)
      
      # Set the Kawasaki WC2 Attributes
      SetWCAttribute(attribSetter, logging, WC2Data, 2)

   if attribName == AW_CRATER_DEF:
      # Set OP Attribute Visu
      SetWCAttributeVisu(attribGetter, logging, WCModeIndex, CraterMode)

   if attribName == AW_WEAVE_PATTERN_NO_DEF:
         try:
            weavePatternIndex = attribGetter.GetEnumIndex(AW_WEAVE_PATTERN_NO_DEF)
         except:
            logging.LogError('Cannot get the Attribute AW_WEAVE_PATTERN_NO_DEF!')

         SetWeaveAttributeVisu(attribGetter, logging, weavePatternIndex)       

   if attribName == AW_SPS_PATTERN_NO_DEF:
         try:
            spsPatternIndex = attribGetter.GetEnumIndex(AW_SPS_PATTERN_NO_DEF)
         except:
            logging.LogError('Cannot get the Attribute AW_SPS_PATTERN_NO_DEF!')

         SetSpsAttributeVisu(attribGetter, logging, spsPatternIndex)            

   # Set RTPM
   if attribName == AW_RTPM_DEF:
         try:
            rtpmIndex = attribGetter.GetEnumIndex(AW_RTPM_DEF)
         except:
            logging.LogError('Cannot get the Attribute AW_RTPM_DEF!')

         SetRtpmAttributeVisu(attribGetter, logging, rtpmIndex)            
   
   # Set SoftwareSlowDown
   if attribName == AW_SSD_DEF:
         try:
            ssdIndex = attribGetter.GetEnumIndex(AW_SSD_DEF)
         except:
            logging.LogError('Cannot get the Attribute AW_SSD_DEF!')

         SetSsdAttributeVisu(attribGetter, logging, ssdIndex)      

   # show/hide ConnectionType Attribute due to CalibrationMethod
   if (attribName == AW_SEAM_CALIBRATION_METHOD):
      calibrationMethod=attribGetter.GetAttributeEnumByName(AW_SEAM_CALIBRATION_METHOD).GetValue()
      # logging.LogInfo('..................found Calibration Method AW_SEAM_CALIBRATION_METHOD=' + calibrationMethod)
      attConnectionType = attribGetter.GetAttributeByName(AW_TOUCHSENS_CONNECT_TYPE)
      if (calibrationMethod == AW_SEAMSEARCHING) or (calibrationMethod == AW_TOUCHSENSE_BY_POINT) or (calibrationMethod == AW_TOUCHSENSE_AUTOMATIC):
         attConnectionType.SetVisibility(True)
      else:
         attConnectionType.SetVisibility(False)

# -------------------------------------------------------------------------------------------
   
def SetWCAttributeVisu(attribGetter, logging, WCModeIndex, CraterMode):
   if WCModeIndex == 0:
      jobModeVisu = True
      manModeVisu = False
      jobmanModeVisu = True
      jobModeReadOnly = True
   elif WCModeIndex == 1:
      jobModeVisu = False
      manModeVisu = True
      jobmanModeVisu = True
      jobModeReadOnly = False
   else:
      jobModeVisu = False
      manModeVisu= False
      jobmanModeVisu = False

   # Attribute Weld Condition Number         
   try:
      att = attribGetter.GetAttributeByName(AW_WCNUMBER_DEF)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCNUMBER_DEF!')

   # Attribute Weld Condition Name         
   try:
      att = attribGetter.GetAttributeByName(AW_WCNAME_DEF)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCNAME_DEF!')

   # Attribute Job Number         
   try:
      att = attribGetter.GetAttributeByName(AW_WCJOBNO_DEF)
      att.SetVisibility(jobModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCJOBNO_DEF!')

   # Attribute Wire Feed Speed         
   try:
      att = attribGetter.GetAttributeByName(AW_WIREFEEDSPEED_DEF)
      att.SetVisibility(jobModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_WIREFEEDSPEED_DEF!')

   # Attribute Weld Current     
   try:
      att = attribGetter.GetAttributeByName(AW_WELDCURRENT_DEF)
      att.SetVisibility(manModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WELDCURRENT_DEF!')

   # Attribute Arc Length corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_ARCLENGTHCORR_DEF)
      att.SetVisibility(jobModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_ARCLENGTHCORR_DEF!')            
      
   # Attribute Weld Voltage         
   try:
      att = attribGetter.GetAttributeByName(AW_WELDVOLTAGE_DEF)
      att.SetVisibility(manModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WELDVOLTAGE_DEF!')

   # Attribute Pulse Dynamic corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_PULSEDYNAMICCORR_DEF)
      att.SetVisibility(jobmanModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_PULSEDYNAMICCORR_DEF!')

   # Attribute Wire Retract corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_WIRERETRACTCORR_DEF)
      att.SetVisibility(jobmanModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_WIRERETRACTCORR_DEF!')


   # Attribute WC2 Crater         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATER_DEF)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATER_DEF!')

   # Attribute Crater Condition Number         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERNUMBER_DEF)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNAME_DEF!')

   # Attribute Crater Condition Name         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERNAME_DEF)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNAME_DEF!')

   # Attribute Crater Job Number         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERJOBNO_DEF)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERJOBNO_DEF!')

   # Attribute WC2 Time (s)         
   try:
      att = attribGetter.GetAttributeByName(AW_TIME_DEF)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)

      #if WCModeIndex <= 1:
      #   att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_TIME_DEF!')

   # Attribute WC2 Wire Feed Speed (m/min)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIREFEEDSPEED_DEF)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)

      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWIREFEEDSPEED_DEF!')

   # Attribute WC2 Weld Current (A)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWELDCURRENT_DEF)
      if CraterMode == True:
         att.SetVisibility(manModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWELDCURRENT_DEF!')

   # Attribute WC2 Arc Length corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERARCLENGTHCORR_DEF)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)

      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERARCLENGTHCORR_DEF!')            

   # Attribute WC2 Weld Voltage (V)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWELDVOLTAGE_DEF)
      if CraterMode == True:
         att.SetVisibility(manModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWELDVOLTAGE_DEF!')

   # Attribute WC2 Pulse/Dynamic corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERPULSEDYNAMICCORR_DEF)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)

      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERPULSEDYNAMICCORR_DEF!')

   # Attribute WC2 Wire Retract corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIRERETRACTCORR_DEF)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)

      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWIRERETRACTCORR_DEF!')

def SetWeaveAttributeVisu(attribGetter, logging, weavePatternIndex):
   if weavePatternIndex == 0:
      weaveOnOff = False
   else:
      weaveOnOff = True
   
   # Hide or Show the Weave attributes
   try:
      att = attribGetter.GetAttributeByName(AW_WEAVEFREQUENZ_DEF)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_WEAVEFREQUENZ_DEF!')
   
   try:
      att = attribGetter.GetAttributeByName(AW_WEAVEWIDTH_DEF)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVEWIDTH_DEF!')         
      
def SetSpsAttributeVisu(attribGetter, logging, spsPatternIndex):
   if spsPatternIndex == 0:
      spsOnOff = False
   elif spsPatternIndex == 1:
      spsOnOff = False
   else:
      spsOnOff = True
   
   # Hide or Show the SPS attributes
   try:
      att = attribGetter.GetAttributeByName(AW_SPSSD_DEF)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SPSSD_DEF!')
   
   try:
      att = attribGetter.GetAttributeByName(AW_SPSTPRD_DEF)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SPSTPRD_DEF!')         
      
   try:
      att = attribGetter.GetAttributeByName(AW_SPSSDG_DEF)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SPSSDG_DEF!')    

#Set Visibility of RTPM parameters
def SetRtpmAttributeVisu(attribGetter, logging, rtpmIndex):
   if rtpmIndex == 0:
      rtpmOnOff = False
   elif rtpmIndex == 1:
      rtpmOnOff = False
   else:
      rtpmOnOff = True
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_WS_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_WS_DEF!')
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_VG_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_VG_DEF!')         
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_HG_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_HG_DEF!')   
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_VB_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_VB_DEF!')   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_HB_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_HB_DEF!')   
  
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_II_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_II!')   
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_SG_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_SG_DEF!') 
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IT_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_IT_DEF!')   
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IVC_DEF )
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_IVC_DEF!')   
   
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IHC_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_IHC_DEF!')   
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_ICC_DEF)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_ICC_DEF!')   

#Set Visibility of SoftwareSlowDown parameters
def SetSsdAttributeVisu(attribGetter, logging, ssdIndex):
   if ssdIndex == 0:
      ssdOnOff = False
   elif ssdIndex == 1:
      ssdOnOff = False
   else:
      ssdOnOff = True
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_PHT_DEF)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SSD_PHT_DEF!')
   
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WP_DEF)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SSD_WP_DEF!')         
      
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WP_DEF)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SSD_WP_DEF!')   
   
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WF_DEF)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SSD_WF_DEF!')   
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WW_DEF)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_SSD_WW_DEF!')   

# -------------------------------------------------------------------------------------------
# Technology post on frame change
# def PostTechOnFrameChanged(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
#    # attribGetter = Operator.GetAttribGetter()
#    # attribSetter = Operator.GetAttribSetter()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   return 1


# -------------------------------------------------------------------------------------------
# Technology post update technology
# def PostTechUpdate(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_TECH_UPDATE_START)
   
#    # attribGetter = Operator.GetAttribGetter()
#    # attribSetter = Operator.GetAttribSetter()

#    # YOUR CODE

#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_POST_TECH_UPDATE_END)
