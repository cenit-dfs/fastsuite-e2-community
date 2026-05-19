from centypes import *
import inspect, os
import csv
import ctypes
import sys

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "ArcWeldConditionEvent.py: "

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
# Definition atttributes (DEF)
AW_ARCWELDMODE_DEF = "SetArcWeldMode"
AW_ARCWELDMODE_DEFs = ["None","2","3"]

AW_WCMODE_DEF = "WeldConditionMode"
AW_WCMODE_DEFs = ["JobMode","ManualMode","None"] 
AW_WCNUMBER_DEF = "WeldConditionNumber"
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
AW_CRATERWELDCURRENT_DEF = "WC2WeldCurrent "
AW_CRATERARCLENGTHCORR_DEF = "WC2ArcLengthCorr"
AW_CRATERWELDVOLTAGE_DEF = "WC2WeldVoltage"
AW_CRATERPULSEDYNAMICCORR_DEF = "WC2PulseDynamicCorr"
AW_CRATERWIRERETRACTCORR_DEF = "WC2WireRetractCorr"

# Output atttributes (DL)
AW_ARCWELDMODE_DL = "DLSetArcWeldMode"
AW_ARCWELDMODE_DLs = ["None","2","3"]

AW_WCMODE = "WCMode"
AW_WCMODE_DLs = ["JobMode","ManualMode","None"] 
AW_WCMODE_DL = "DLWeldConditionMode"
AW_WCNUMBER_DL = "DLWeldConditionNumber"
AW_WCNAME_DL = "DLWeldConditionName"
AW_WCJOBNO_DL = "DLJobNumber"
AW_WELDSPEED_DL = "DLWC1WeldSpeed"
AW_WIREFEEDSPEED_DL = "DLWC1WireFeedSpeed"
AW_WELDCURRENT_DL = "DLWC1WeldCurrent"
AW_ARCLENGTHCORR_DL = "DLWC1ArcLengthCorr"
AW_WELDVOLTAGE_DL = "DLWC1WeldVoltage"
AW_PULSEDYNAMICCORR_DL = "DLWC1PulseDynamicCorr"
AW_WIRERETRACTCORR_DL = "DLWC1WireRetractCorr"

AW_CRATER_DL = "DLWC2Crater"
AW_CRATERNUMBER_DL = "DLCraterSpotConditionNumber"
AW_CRATERNAME_DL = "DLCraterSpotConditionName"
AW_CRATERJOBNO_DL = "DLCraterSpotJobNumber"

AW_TIME_DL = "DLWC2Time"
AW_CRATERWIREFEEDSPEED_DL = "DLWC2WireFeedSpeedmin)"
AW_CRATERWELDCURRENT_DL = "DLWC2WeldCurrent"
AW_CRATERARCLENGTHCORR_DL = "DLWC2ArcLengthCorr"
AW_CRATERWELDVOLTAGE_DL = "DLWC2WeldVoltage"
AW_CRATERPULSEDYNAMICCORR_DL = "DLWC2PulseDynamicCorr"
AW_CRATERWIRERETRACTCORR_DL = "DLWC2WireRetractCorr"

# AW_WEAVE_ONOFF = "WeaveOnOff"
# AW_WEAVE_WIDTH = "WeaveWidth"
# AW_WEAVE_FREQUENZ = "WeaveFrequenz"

AW_WEAVE_PATTERN = "DLWeavePattern"
AW_WEAVE_PATTERN_LITERALS = ["None","harmonic","harmonic with end stop","reciprocating triangular","circular clockwise","circular counterclockwise","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_WEAVE_PATTERN_NO = "DLWeavePatternNumber"
AW_WEAVEFREQUENZ = "DLWeaveFrequenz"
AW_WEAVEWIDTH = "DLWeaveWidth"

#SPS Event
AW_SPSPTN_DL = "DLPatternSPS"
AW_SPSPTN_LITERALS = ["None","Disabled","horizontal fillet","flat fillet","V groove","flat bevel groove","bevel groove","horizontal bevel groove","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_SPSPTN_NO = "DLPatternNum"
AW_SPSSD_DL = "DLStartDist"
AW_SPSTP_DL = "DLReliefDist"
AW_SPSSDG_DL = "DLDistInGroove"

#RTPM
AW_RTPM_DL = "DLRTPM"
AW_RTPM_LITERALS = ["None","Disabled","Enabled"]
AW_RTPM_NO = "DLWCRTPMNum"
AW_RTPM_WS_DL = "DLWCWireStick"
AW_RTPM_VG_DL = "DLWCVerticalGain"
AW_RTPM_HG_DL = "DLWCHorizontalGain"
AW_RTPM_VB_DL = "DLWCVerticalBIAS"
AW_RTPM_HB_DL = "DLWCHorizontalBIAS"
AW_RTPM_SG_DL = "DLWCStartGain"
AW_RTPM_II_DL = "DLWCDelayTime"
AW_RTPM_IT_DL = "DLWCInitialGainTime"
AW_RTPM_IVC_DL = "DLWCInitialVerticalCurrent"
AW_RTPM_IHC_DL = "DLWCInitialHorizontalCurrent"
AW_RTPM_ICC_DL = "DLWCInitialChangeCurrent"

#Software Slow Down 
AW_SSD_DL = "DLSSDown"
AW_SSD_LITERALS = ["None","Disabled","Enabled"]
AW_SSD_NO = "DLWCSSDNum"
AW_SSD_PHT_DL = "DLWCPreHeatTime"
AW_SSD_WP_DL = "DLWCWeavePattern"
AW_SSD_WP_LITERALS = ["no weaving","harmonic","harmonic with end stop","reciprocating triangular","circular clockwise","circular counterclockwise","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_SSD_WP_NO = "DLWCWeaveNum"
AW_SSD_WF_DL = "DLWCWeaveFreq"
AW_SSD_WW_DL = "DLWCWeaveWidth"

WC1Data = []
WC2Data = []

def GetEventName():
   return "ArcWeldConditionEvent"
   
def GetEventUuId():
   return "6026DCA2-0BCF-4C13-AA22-3BF568E26ED7"

def GetIconName():
   return "ProgramFlowChart"
   
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
   return CYCLEROTATION_ROTTOOL
   
def GetCycleRotationManualFlag():
   return CYCLEROTATION_ROTTOOL
   
def IsMachiningCycle():
   return 0

def GetGroupName():
   return "OlpEvent"

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
            craterTime = CsvDataColumn[2].replace(",",".")
            if float(craterTime) > 9.9:
               craterTime = "9.9"
            DataList.append(craterTime)                         # Crater Time
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
            craterTime = CsvDataColumn[3].replace(",",".")
            if float(craterTime) > 9.9:
               craterTime = "9.9"
            DataList.append(craterTime)                         # Crater Time
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
      # Set the Kawasaki Crater Condition Event attributes
      try:
         attribSetter.SetString(AW_CRATERNAME_DL, WCData[0])
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERNAME_DL!')

      try:
         attribSetter.SetInteger(AW_CRATERJOBNO_DL, int(WCData[1]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERJOBNO_DL!')         

      try:
         attribSetter.SetDouble(AW_TIME_DL, float(WCData[2]))
      except:
         logging.LogError('Cannot set the Attribute AW_TIME_DL!')

      try:
         attribSetter.SetDouble(AW_CRATERWIREFEEDSPEED_DL, float(WCData[3]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWIREFEEDSPEED_DL!')      
                     
      try:
         attribSetter.SetDouble(AW_CRATERWELDCURRENT_DL, float(WCData[4]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWELDCURRENT_DL!')

      try:
         attribSetter.SetDouble(AW_CRATERARCLENGTHCORR_DL, float(WCData[5]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERARCLENGTHCORR_DL!')      
            
      try:
         attribSetter.SetDouble(AW_CRATERWELDVOLTAGE_DL, float(WCData[6]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERWELDVOLTAGE_DL!')
            
      try:
         attribSetter.SetDouble(AW_CRATERPULSEDYNAMICCORR_DL, float(WCData[7]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERPULSEDYNAMICCORR_DL!')
      try:
         attribSetter.SetDouble(AW_CRATERWIRERETRACTCORR_DL, float(WCData[8]))
      except:
         logging.LogError('Cannot set the Attribute AW_CRATERPULSEDYNAMICCORR_DL!')

   else:
      # Set the Kawasaki Weld Condition Event attributes
      try:
         attribSetter.SetString(AW_WCNAME_DL, WCData[0])
      except:
         logging.LogError('Cannot set the Attribute AW_WCNAME_DL!')

      try:
         attribSetter.SetInteger(AW_WCJOBNO_DL, int(WCData[1]))
      except:
         logging.LogError('Cannot set the Attribute AW_WCJOBNO_DL!')         
         
      try:
         attribSetter.SetDouble(AW_WELDSPEED_DL, float(WCData[2]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDSPEED_DL!')

      try:
         attribSetter.SetDouble(AW_WIREFEEDSPEED_DL, float(WCData[3]))
      except:
         logging.LogError('Cannot set the Attribute AW_WIREFEEDSPEED_DL!')
         
      try:
         attribSetter.SetDouble(AW_WELDCURRENT_DL, float(WCData[4]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDCURRENT_DL!')

      try:
         attribSetter.SetDouble(AW_ARCLENGTHCORR_DL, float(WCData[5]))
      except:
         logging.LogError('Cannot set the Attribute AW_ARCLENGTHCORR_DL!')

      try:
         attribSetter.SetDouble(AW_WELDVOLTAGE_DL, float(WCData[6]))
      except:
         logging.LogError('Cannot set the Attribute AW_WELDVOLTAGE_DL!')

      try:
         attribSetter.SetDouble(AW_PULSEDYNAMICCORR_DL, float(WCData[7]))
      except:
         logging.LogError('Cannot set the Attribute AW_PULSEDYNAMICCORR_DL!')

      try:
         attribSetter.SetDouble(AW_WIRERETRACTCORR_DL, float(WCData[8]))
      except:
         logging.LogError('Cannot set the Attribute AW_WIRERETRACTCORR_DL!')
   
def SetWeaveAttributeVisu(attribGetter, logging, weavePatternIndex):
   if weavePatternIndex == 0:
      weaveOnOff = False
   else:
      weaveOnOff = True
   
   # Hide or Show the Weave attributes
   try:
      att = attribGetter.GetAttributeByName(AW_WEAVE_PATTERN_NO)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_PATTERN_NO!')

   try:
      att = attribGetter.GetAttributeByName(AW_WEAVEWIDTH)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVEWIDTH!')         
      
   try:
      att = attribGetter.GetAttributeByName(AW_WEAVEFREQUENZ)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_WEAVEFREQUENZ!')

def SetSpsAttributeVisu(attribGetter, logging, spsPatternIndex):
   if spsPatternIndex == 0:
      spsOnOff = False
   elif spsPatternIndex == 1:
      spsOnOff = False
   else:
      spsOnOff = True
   
   # Hide or Show the Start Point Sensing attributes
   try:
      att = attribGetter.GetAttributeByName(AW_SPSSD_DL)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SPSSD_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_SPSTP_DL)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SPSTP_DL!')
   try:
      att = attribGetter.GetAttributeByName(AW_SPSSDG_DL)
      att.SetVisibility(spsOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SPSSDG_DL!')
      
def SetRtpmAttributeVisu(attribGetter, logging, rtpmIndex):
   if rtpmIndex == 0:
      rtpmOnOff = False
   elif rtpmIndex == 1:
      rtpmOnOff = False
   else:
      rtpmOnOff = True
   # Hide or Show the Start Point Sensing attributes

   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_WS_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_RTPM_WS_DL!')

   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_VG_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_VG_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_HG_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_HG_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_VB_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_VB_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_HB_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_HB_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_SG_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_SG_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_II_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_II_DL!')
      
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IT_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_IT_DL!')
            
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IVC_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_IVC_DL!')
            
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_IHC_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_IHC_DL!')
            
   try:
      att = attribGetter.GetAttributeByName(AW_RTPM_ICC_DL)
      att.SetVisibility(rtpmOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_RTPM_ICC_DL!')

def SetSsdAttributeVisu(attribGetter, logging, ssdIndex):
   if ssdIndex == 0:
      ssdOnOff = False
   elif ssdIndex == 1:
      ssdOnOff = False
   else:
      ssdOnOff = True
   
   # Hide or Show the Start Point Sensing attributes
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_PHT_DL)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SSD_PHT_DL!')      
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WP_DL)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SSD_WP_DL!')    
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WF_DL)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SSD_WF_DL!')
   try:
      att = attribGetter.GetAttributeByName(AW_SSD_WW_DL)
      att.SetVisibility(ssdOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_SSD_WW_DL!')

def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get creator
   attribCreator = Operator.GetAttribCreator()

   # Read the Kawasaki WeldCondition file
   WCNumber = 1
   WC1Data = ReadCsv(WCNumber, 0, 1)

   # Read the Kawasaki Crater Condition file
   CCNumber = 1
   WC2Data = ReadCsv(CCNumber, 0, 2)

   # Kawasaki Weld Condition output attributes
   # Set Arc WeldMode (Enum)
   att = attribCreator.AddEnum(AW_ARCWELDMODE_DL, AW_ARCWELDMODE_DLs, AW_ARCWELDMODE_DLs[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_ARCWELDMODE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC Mode (Enum)
   att = attribCreator.AddEnum(AW_WCMODE, AW_WCMODE_DLs, AW_WCMODE_DLs[0], USER_ATTRIBUTE, AW_WCMODE)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)

   # WC Mode Number
   att = attribCreator.AddInt(AW_WCMODE_DL, 0, 0, 2, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCMODE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)
   att.SetVisibility(False)
   
   # WC Number
   att = attribCreator.AddInt(AW_WCNUMBER_DL, WCNumber, 1, 199, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCNUMBER_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)

   # WC Name
   att = attribCreator.AddString(AW_WCNAME_DL, WC1Data[0], USER_ATTRIBUTE, AW_WCNAME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC Job Number
   att = attribCreator.AddInt(AW_WCJOBNO_DL, int(WC1Data[1]), 1, 65535, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCJOBNO_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Weld Speed (cm/min)
   att = attribCreator.AddDouble(AW_WELDSPEED_DL, float(WC1Data[2]), 1.0, 999.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(False)

   # WC1 Wire Feed Speed
   att = attribCreator.AddDouble(AW_WIREFEEDSPEED_DL, float(WC1Data[3]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WIREFEEDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC1 Current
   att = attribCreator.AddDouble(AW_WELDCURRENT_DL, float(WC1Data[4]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDCURRENT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # WC1 Arc length corr.
   att = attribCreator.AddDouble(AW_ARCLENGTHCORR_DL, float(WC1Data[5]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_ARCLENGTHCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC1 Voltage
   att = attribCreator.AddDouble(AW_WELDVOLTAGE_DL, float(WC1Data[6]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDVOLTAGE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # WC1 PulseDynamic corr.
   att = attribCreator.AddDouble(AW_PULSEDYNAMICCORR_DL, float(WC1Data[7]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_PULSEDYNAMICCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC1 PulseDynamic corr.
   att = attribCreator.AddDouble(AW_WIRERETRACTCORR_DL, float(WC1Data[8]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WIRERETRACTCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)
   

   # Create Kawasaki WELD CONDITION 2 (Crater Condition) output attributes
   att = attribCreator.AddBool(AW_CRATER_DL, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATER_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)

   att = attribCreator.AddInt(AW_CRATERNUMBER_DL, CCNumber, 1, 299, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATERNUMBER_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   
   att = attribCreator.AddString(AW_CRATERNAME_DL, WC2Data[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATERNAME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   att = attribCreator.AddInt(AW_CRATERJOBNO_DL, int(WC2Data[1]), 1, 65535, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATERJOBNO_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Time
   att = attribCreator.AddDouble(AW_TIME_DL, float(WC2Data[2]), 0.0, 9.9, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_TIME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(False)

   # WC2 Wire Feed Speed
   att = attribCreator.AddDouble(AW_CRATERWIREFEEDSPEED_DL, float(WC2Data[3]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIREFEEDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC2 Crater Weld Current
   att = attribCreator.AddDouble(AW_CRATERWELDCURRENT_DL, float(WC2Data[4]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDCURRENT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # WC2 Arc length corr.
   att = attribCreator.AddDouble(AW_CRATERARCLENGTHCORR_DL, float(WC2Data[5]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERARCLENGTHCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC2 Crater Weld Voltage
   att = attribCreator.AddDouble(AW_CRATERWELDVOLTAGE_DL, float(WC2Data[6]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDVOLTAGE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # WC2 Crater Pulse Dynamic corr.
   att = attribCreator.AddDouble(AW_CRATERPULSEDYNAMICCORR_DL, float(WC2Data[7]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERPULSEDYNAMICCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC2 Crater Wire Retract corr.
   att = attribCreator.AddDouble(AW_CRATERWIRERETRACTCORR_DL, float(WC2Data[8]), -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIRERETRACTCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # Weave Attributes
   # AW_WEAVE_PATTERN (Enum)
   att = attribCreator.AddEnum(AW_WEAVE_PATTERN, AW_WEAVE_PATTERN_LITERALS, AW_WEAVE_PATTERN_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WEAVE_PATTERN)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)

   # AW_WEAVE_PATTERN_NO (0 - 10)
   att = attribCreator.AddInt(AW_WEAVE_PATTERN_NO, 0, 0, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WEAVE_PATTERN_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)
   att.SetVisibility(False)

   # AW_WEAVE_FREQUENZ
   att = attribCreator.AddDouble(AW_WEAVEFREQUENZ, 0.0, 0.0, 4.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WEAVEFREQUENZ)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # AW_WEAVE_WIDTH
   att = attribCreator.AddDouble(AW_WEAVEWIDTH, 0.0, 0.0, 0.04, 0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, AW_WEAVEWIDTH)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Start Point Sensing 
   
   # AW_SPSPTN_DL (Enum)
   att = attribCreator.AddEnum(AW_SPSPTN_DL, AW_SPSPTN_LITERALS, AW_SPSPTN_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SPSPTN_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   
   # AW_SPSPTN_NO
   att = attribCreator.AddInt(AW_SPSPTN_NO, 1, 1, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SPSPTN_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # AW_SPSSD_DL
   att = attribCreator.AddDouble(AW_SPSSD_DL, 0.0, 0.0, 99.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSSD_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # AW_SPSTP_DL
   att = attribCreator.AddDouble(AW_SPSTP_DL, 0.0, 0.0, 99.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSTP_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # AW_SPSSDG_DL
   att = attribCreator.AddDouble(AW_SPSSDG_DL, 0.0, 0.0, 99.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SPSSDG_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # RTPM 
   
   
    # RTPM ON/OFF
   att = attribCreator.AddEnum(AW_RTPM_DL, AW_RTPM_LITERALS, AW_RTPM_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   
   # AW_RTPM_NO
   att = attribCreator.AddInt(AW_RTPM_NO, 1, 1, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Wire Stick Out
   att = attribCreator.AddInt(AW_RTPM_WS_DL, 0, 0, 65535, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_WS_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Vertical Gain Current
   att = attribCreator.AddInt(AW_RTPM_VG_DL, 0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_VG_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Horizontal Gain Current
   att = attribCreator.AddInt(AW_RTPM_HG_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_HG_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Vertical BIAS
   att = attribCreator.AddInt(AW_RTPM_VB_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_VB_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Horizontal BIAS
   att = attribCreator.AddInt(AW_RTPM_HB_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_HB_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Delay Time for integral interval
   att = attribCreator.AddInt(AW_RTPM_II_DL, 0, 0, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_II_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)   
   
   # Start Gain ON/OFF
   att = attribCreator.AddBool(AW_RTPM_SG_DL, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_SG_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Initial gain time
   att = attribCreator.AddDouble(AW_RTPM_IT_DL, 0.1, 0.0, 9.9, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_RTPM_IT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # Initial vertical current
   att = attribCreator.AddInt(AW_RTPM_IVC_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_IVC_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Initial horizontal current
   att = attribCreator.AddInt(AW_RTPM_IHC_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_IHC_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Initial change current
   att = attribCreator.AddInt(AW_RTPM_ICC_DL,  0, -1000, 1000, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_ICC_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Software Slow Down

   #SSD ON/OFF 
   att = attribCreator.AddEnum(AW_SSD_DL, AW_SSD_LITERALS, AW_SSD_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   
   # AW_SSD_NO
   att = attribCreator.AddInt(AW_SSD_NO, 1, 1, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Preheat time
   att = attribCreator.AddDouble(AW_SSD_PHT_DL, 0.0, 0.0, 9.9, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_PHT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Weave Pattern
   att = attribCreator.AddEnum(AW_SSD_WP_DL, AW_SSD_WP_LITERALS , AW_SSD_WP_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_WP_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # AW_SSD_WP_NO
   att = attribCreator.AddInt(AW_SSD_WP_NO, 1, 1, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_WP_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)   
   att.SetReadOnly(True)
   
   # Weave Freq
   att = attribCreator.AddDouble(AW_SSD_WF_DL, 0.0, 0, 4.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WF_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Weave Freq
   att = attribCreator.AddDouble(AW_SSD_WW_DL, 0.0, 0, 40.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WW_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   # Get the WC Mode
   try:
      WCModeIndex = attribGetter.GetEnumIndex(AW_WCMODE)
   except:
      logging.LogError('Cannot get the attribute AW_WCMODE!')

   # Get the Crater Mode
   try:
      CraterMode = attribGetter.GetBool(AW_CRATER_DL)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATER_DL!')

   # Hide or Show Kawasaki WC Attributes
   SetWCAttributeVisu(attribGetter, logging, WCModeIndex, CraterMode)

   # Get the Weave Pattern Enum Index
   try:
      weavePatternIndex = attribGetter.GetEnumIndex(AW_WEAVE_PATTERN)
   except:
      logging.LogError('Cannot get the attribute AW_WEAVE_PATTERN!')

   # Get the SPS Pattern Enum Index
   try:
      spsPatternIndex = attribGetter.GetEnumIndex(AW_SPSPTN_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SPSPTN_DL!')

 # Get the RTPM Enum Index
   try:
      rtpmIndex = attribGetter.GetEnumIndex(AW_RTPM_DL)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_DL!')

   try:
      ssdIndex = attribGetter.GetEnumIndex(AW_SSD_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_DL!')
      
   try:
      ssdWeavpatt = attribGetter.GetEnumIndex(AW_SSD_WP_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_WP_DL!')

   # Get the Weld Condition Number
   try:
      WCNumber = attribGetter.GetInteger(AW_WCNUMBER_DL)
   except:
      logging.LogError('Cannot get the attribute AW_WCNUMBER_DL!')

   # Get the Crater Condition Number
   try:
      CCNumber = attribGetter.GetInteger(AW_CRATERNUMBER_DL)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNUMBER_DL!')

   # Set WC Mode Number
   try:
      attribSetter.SetInteger(AW_WCMODE_DL,WCModeIndex)
   except:
      logging.LogError('Cannot set the Attribute AW_WCMODE_DL!')

   # Read the Kawasaki WeldCondition file
   WC1Data = ReadCsv(WCNumber, WCModeIndex, 1)

   # Read the Kawasaki CraterCondition file
   WC2Data = ReadCsv(CCNumber, WCModeIndex, 2)

   # Set the Kawasaki WC1 Attributes
   SetWCAttribute(attribSetter, logging, WC1Data, 1)

   # Set the Kawasaki WC2 Attributes
   SetWCAttribute(attribSetter, logging, WC2Data, 2)

   # Set the Weave Pattern Number
   SetWeavePatternNumber(attribGetter, attribSetter, logging)
   
   # Set the SPS Pattern Number
   SetSpsPatternNumber(attribGetter, attribSetter, logging)
   
   # Set the RTPM Number
   SetRtpmNumber(attribGetter, attribSetter, logging)
   
   #Set the SSD Number
   SetSsdNumber(attribGetter, attribSetter, logging)
   
   #Set the SSD Weave number
   SetSsdWeaveNumber (attribGetter, attribSetter, logging)
   
   # Hide or Show Weave Attributes
   SetWeaveAttributeVisu(attribGetter, logging, weavePatternIndex)
      
   # Hide or Show Start Point Sensing Attributes
   SetSpsAttributeVisu(attribGetter, logging, spsPatternIndex)
   
   # Hide or Show RTPM Attributes
   SetRtpmAttributeVisu(attribGetter, logging, rtpmIndex)
   
   # Hide or Show Start Point Sensing Attributes
   SetSsdAttributeVisu(attribGetter, logging, ssdIndex)
 
def PostCompute(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)

   # get getter
   #attribGetter = Operator.GetAttribGetter()

   # debug logging
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)
   pass

def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get attribute setter
   #attribSetter = Operator.GetAttribSetter()
   # get attribute getter
   #attribGetter = Operator.GetAttribGetter()
   # get changed attribute name
   #changedAttribName = Operator.GetChangedAttributeName()

   # # Customizing Start 
   # if changedAttribName == AW_WCNUMBER_DL:
   #    # Get the WC Mode
   #    try:
   #       WCModeIndex = attribGetter.GetEnumIndex(AW_WCMODE)
   #    except:
   #       logging.LogError('Cannot get the attribute AW_WCMODE!')

   #    # Get the Weld Condition Number
   #    try:
   #       WCNumber = attribGetter.GetInteger(AW_WCNUMBER_DL)
   #    except:
   #       logging.LogError('Cannot get the attribute AW_WCNUMBER_DL!')

   #    # Read the Kawasaki WeldCondition file
   #    WC1Data = ReadCsv(WCNumber, WCModeIndex, 1)

   #    # Set the Kawasaki WC1 Attributes
   #    SetWCAttribute(attribSetter, logging, WC1Data, 1)
      
   # if changedAttribName == AW_CRATERNUMBER_DL:
   #    # Get the WC Mode
   #    try:
   #       WCModeIndex = attribGetter.GetEnumIndex(AW_WCMODE)
   #    except:
   #       logging.LogError('Cannot get the attribute AW_WCMODE!')

   #    # Get the Crater Condition Number
   #    try:
   #       CCNumber = attribGetter.GetInteger(AW_CRATERNUMBER_DL)
   #    except:
   #       logging.LogError('Cannot get the Attribute AW_CRATERNUMBER_DL!')

   #    # Read the Kawasaki CraterCondition file
   #    WC2Data = ReadCsv(CCNumber, WCModeIndex, 2)

   #    # Set the Kawasaki WC2 Attributes
   #    SetWCAttribute(attribSetter, logging, WC2Data, 2)

   pass

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
      att = attribGetter.GetAttributeByName(AW_WCNUMBER_DL)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCNUMBER_DL!')

   # Attribute Weld Condition Name         
   try:
      att = attribGetter.GetAttributeByName(AW_WCNAME_DL)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCNAME_DL!')

   # Attribute Job Number         
   try:
      att = attribGetter.GetAttributeByName(AW_WCJOBNO_DL)
      att.SetVisibility(jobModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WCJOBNO_DL!')

   # Attribute Weld Speed       
   try:
      att = attribGetter.GetAttributeByName(AW_WELDSPEED_DL)
      att.SetVisibility(jobmanModeVisu)
      # if WCModeIndex <= 1:
      #    att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_WELDSPEED_DL!')         
   
   # Attribute Wire Feed Speed         
   try:
      att = attribGetter.GetAttributeByName(AW_WIREFEEDSPEED_DL)
      att.SetVisibility(jobModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_WIREFEEDSPEED_DL!')

   # Attribute Weld Current     
   try:
      att = attribGetter.GetAttributeByName(AW_WELDCURRENT_DL)
      att.SetVisibility(manModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WELDCURRENT_DL!')

   # Attribute Arc Length corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_ARCLENGTHCORR_DL)
      att.SetVisibility(jobModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_ARCLENGTHCORR_DL!')            
      
   # Attribute Weld Voltage         
   try:
      att = attribGetter.GetAttributeByName(AW_WELDVOLTAGE_DL)
      att.SetVisibility(manModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_WELDVOLTAGE_DL!')

   # Attribute Pulse Dynamic corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_PULSEDYNAMICCORR_DL)
      att.SetVisibility(jobmanModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_PULSEDYNAMICCORR_DL!')

   # Attribute Wire Retract corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_WIRERETRACTCORR_DL)
      att.SetVisibility(jobmanModeVisu)
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_WIRERETRACTCORR_DL!')


   # Attribute WC2 Crater         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATER_DL)
      att.SetVisibility(jobmanModeVisu)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATER_DL!')

   # Attribute Crater Condition Number         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERNUMBER_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNAME_DL!')

   # Attribute Crater Condition Name         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERNAME_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERNAME_DL!')

   # Attribute Crater Job Number         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERJOBNO_DL)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERJOBNO_DL!')

   # Attribute WC2 Time (s)         
   try:
      att = attribGetter.GetAttributeByName(AW_TIME_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
      
      #if WCModeIndex <= 1:
      #   att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_TIME_DL!')

   # Attribute WC2 Wire Feed Speed (m/min)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIREFEEDSPEED_DL)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)
      
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWIREFEEDSPEED_DL!')

   # Attribute WC2 Weld Current (A)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWELDCURRENT_DL)
      if CraterMode == True:
         att.SetVisibility(manModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWELDCURRENT_DL!')

   # Attribute WC2 Arc Length corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERARCLENGTHCORR_DL)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)
      
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERARCLENGTHCORR_DL!')            

   # Attribute WC2 Weld Voltage (V)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWELDVOLTAGE_DL)
      if CraterMode == True:
         att.SetVisibility(manModeVisu)
      else:
         att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWELDVOLTAGE_DL!')

   # Attribute WC2 Pulse/Dynamic corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERPULSEDYNAMICCORR_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
      
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERPULSEDYNAMICCORR_DL!')

   # Attribute WC2 Wire Retract corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIRERETRACTCORR_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
      
      if WCModeIndex <= 1:
         att.SetReadOnly(jobModeReadOnly)
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERWIRERETRACTCORR_DL!')

def SetWeavePatternNumber(attribGetter, attribSetter, logging):
   # Get the Weave Pattern Enum Index
   try:
      weavePatternIndex = attribGetter.GetEnumIndex(AW_WEAVE_PATTERN)
   except:
      logging.LogError('Cannot get the attribute AW_WEAVE_PATTERN!')

   try:
      attribSetter.SetInteger(AW_WEAVE_PATTERN_NO,weavePatternIndex)
   except:
      logging.LogError('Cannot set the attribute AW_WEAVE_PATTERN_NO!')

def SetSpsPatternNumber(attribGetter, attribSetter, logging):
   # Get the SPS Pattern Enum Index
   try:
      spsPatternIndex = attribGetter.GetEnumIndex(AW_SPSPTN_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SPSPTN_DL!')

   try:
      attribSetter.SetInteger(AW_SPSPTN_NO,spsPatternIndex)
   except:
      logging.LogError('Cannot set the attribute AW_SPSPTN_NO!')

def SetRtpmNumber(attribGetter, attribSetter, logging):
   # Get the RTPM Enum Index
   try:
      rtpmIndex = attribGetter.GetEnumIndex(AW_RTPM_DL)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_DL!')

   try:
      attribSetter.SetInteger(AW_RTPM_NO,rtpmIndex)
   except:
      logging.LogError('Cannot set the attribute AW_RTPM_NO!')

def SetSsdNumber(attribGetter, attribSetter, logging):
   # Get the SSD  Enum Index
   try:
      ssdIndex = attribGetter.GetEnumIndex(AW_SSD_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_DL!')

   try:
      attribSetter.SetInteger(AW_SSD_NO,ssdIndex)
   except:
      logging.LogError('Cannot set the attribute AW_SSD_NO!')

def SetSsdWeaveNumber(attribGetter, attribSetter, logging):
   # Get the SSD Weave Enum Index
   try:
      ssdWeavpatt = attribGetter.GetEnumIndex(AW_SSD_WP_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_WP_DL!')

   try:
      attribSetter.SetInteger(AW_SSD_WP_NO,ssdWeavpatt)
   except:
      logging.LogError('Cannot set the attribute AW_SSD_WP_NO!')   