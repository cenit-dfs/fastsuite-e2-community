from centypes import *

# -------------------------------------------------------------------------------------------
# Event Definition in C++
# This Python only override some Attributes or Callbacks
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "ArcOnEvent.py: "

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
AW_ARCSET_PROGNR_DEF = "ArcSetProgNumber"
AW_SPEED_WELDING = "Speed"

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

AW_USE_WEAVE_DEF = "UseWeaveDefine"
AW_WEAVE_FREQUENZ_DEF = "WeaveFrequenzDefine"
AW_WEAVE_WIDTH_DEF = "WeaveWidthDefine"

AW_WEAVE_PATTERN_NO_DEF = "WCWeavePatternNumber"
AW_WEAVEFREQUENZ_DEF = "WCWeaveFrequenz"
AW_WEAVEWIDTH_DEF = "WCWeaveWidth"

#SPS Event
AW_SPS_PATTERN_NO_DEF = "WCStartPointSensing"
AW_SPS_PATTERN_NO_DEFs = ["None","Disabled","horizontal fillet","flat fillet","V groove","flat bevel groove","bevel groove","horizontal bevel groove","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5","user pattern 6"]
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
# Output atttributes (DL)
AW_ARC_PRGNR = "ProgNumber"

AW_ARCWELDMODE_DL = "DLSetArcWeldMode"
AW_ARCWELDMODE_DLs = ["None","2","3"]

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
AW_CRATERWIREFEEDSPEED_DL = "DLWC2WireFeedSpeed"
AW_CRATERWELDCURRENT_DL = "DLWC2WeldCurrent"
AW_CRATERARCLENGTHCORR_DL = "DLWC2ArcLengthCorr"
AW_CRATERWELDVOLTAGE_DL = "DLWC2WeldVoltage"
AW_CRATERPULSEDYNAMICCORR_DL = "DLWC2PulseDynamicCorr"
AW_CRATERWIRERETRACTCORR_DL = "DLWC2WireRetractCorr"

AW_WEAVE_ONOFF = "WeaveOnOff"
AW_WEAVE_FREQUENZ = "WeaveFrequenz"
AW_WEAVE_WIDTH = "WeaveWidth"
AW_WEAVE_TIME1 = "WeaveTime1"
AW_WEAVE_TIME2 = "WeaveTime2"

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
AW_SSD_NO = "DLWCSSDown"
AW_SSD_PHT_DL = "DLWCPreHeatTime"
AW_SSD_WP_DL = "DLWCWeavePattern"
AW_SSD_WP_LITERALS = ["no weaving","harmonic","harmonic with end stop","reciprocating triangular","circular clockwise","circular counterclockwise","user pattern 1","user pattern 2","user pattern 3","user pattern 4","user pattern 5"]
AW_SSD_WP_NO = "DLWCWeaveNum"
AW_SSD_WF_DL = "DLWCWeaveFreq"
AW_SSD_WW_DL = "DLWCWeaveWidth"

def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Kawasaki Weld Condition output attributes
   # Set Arc WeldMode (Enum)
   att = attribCreator.AddEnum(AW_ARCWELDMODE_DL, AW_ARCWELDMODE_DLs, AW_ARCWELDMODE_DLs[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_ARCWELDMODE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # # WC Mode (Enum)
   # att = attribCreator.AddEnum(AW_WCMODE_DL, AW_WCMODE_DEFs, AW_WCMODE_DEFs[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCMODE_DL)
   # att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   
   # WC Mode Index
   att = attribCreator.AddInt(AW_WCMODE_DL, 0, 0, 2, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCMODE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   
   # WC Number
   att = attribCreator.AddInt(AW_WCNUMBER_DL, 11, 1, 199, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCNUMBER_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC Name
   att = attribCreator.AddString(AW_WCNAME_DL, "", USER_ATTRIBUTE, AW_WCNAME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC Job Number
   att = attribCreator.AddInt(AW_WCJOBNO_DL, 101, 1, 65535, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WCJOBNO_DL)  
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Weld Speed (cm/min)
   att = attribCreator.AddInt(AW_WELDSPEED_DL, 30, 1, 999, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WELDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Wire Feed Speed
   att = attribCreator.AddDouble(AW_WIREFEEDSPEED_DL, 1.1, 1.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WIREFEEDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Weld Current
   att = attribCreator.AddDouble(AW_WELDCURRENT_DL, 61.1, -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDCURRENT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Arc length corr.
   att = attribCreator.AddDouble(AW_ARCLENGTHCORR_DL, 1.1, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_ARCLENGTHCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Weld Voltage
   att = attribCreator.AddDouble(AW_WELDVOLTAGE_DL, 21.1, -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WELDVOLTAGE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Pulse Dynamic corr.
   att = attribCreator.AddDouble(AW_PULSEDYNAMICCORR_DL, 0.3, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_PULSEDYNAMICCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC1 Wire Retract  corr.
   att = attribCreator.AddDouble(AW_WIRERETRACTCORR_DL, 0.4, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WIRERETRACTCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   
   # WC2 Crater (Bool)
   att = attribCreator.AddBool(AW_CRATER_DL, True, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATER_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Crater Condition Number
   att = attribCreator.AddInt(AW_CRATERNUMBER_DL, 1, 1, 299, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATERNUMBER_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   att = attribCreator.AddString(AW_CRATERNAME_DL, "", USER_ATTRIBUTE, AW_CRATERNAME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetReadOnly(True)

   # WC2 Crater Job Number
   attribCreator.AddInt(AW_CRATERJOBNO_DL, 101, 1, 65535, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_CRATERJOBNO_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Time
   att = attribCreator.AddDouble(AW_TIME_DL, 0.0, 0.0, 9.9, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_TIME_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Wire Feed Speed
   att = attribCreator.AddDouble(AW_CRATERWIREFEEDSPEED_DL, 1.1, 1.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIREFEEDSPEED_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Crater Weld Current
   att = attribCreator.AddDouble(AW_CRATERWELDCURRENT_DL, 11.1, -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDCURRENT_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Arc length corr.
   att = attribCreator.AddDouble(AW_CRATERARCLENGTHCORR_DL, 2.2, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERARCLENGTHCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Crater Weld Voltage
   att = attribCreator.AddDouble(AW_CRATERWELDVOLTAGE_DL, 12.2, -999.9, 999.9, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWELDVOLTAGE_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Crater PulseDynamic corr.
   att = attribCreator.AddDouble(AW_CRATERPULSEDYNAMICCORR_DL, 0.3, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERPULSEDYNAMICCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

   # WC2 Crater PulseDynamic corr.
   att = attribCreator.AddDouble(AW_CRATERWIRERETRACTCORR_DL, 0.4, -100.0, 100.0, 1.0, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATERWIRERETRACTCORR_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)


   # AW_WEAVE_PATTERN (Enum)
   att = attribCreator.AddEnum(AW_WEAVE_PATTERN, AW_WEAVE_PATTERN_LITERALS, AW_WEAVE_PATTERN_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WEAVE_PATTERN)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   att.SetVisibility(True)

   # AW_WEAVE_PATTERN_NO (0 - 10)
   att = attribCreator.AddInt(AW_WEAVE_PATTERN_NO, 0, 0, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_WEAVE_PATTERN_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # AW_WEAVEFREQUENZ
   att = attribCreator.AddDouble(AW_WEAVEFREQUENZ, 0.0, 0.0, 4.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_WEAVEFREQUENZ)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # AW_WEAVEWIDTH
   att = attribCreator.AddDouble(AW_WEAVEWIDTH, 0.0, 0.0, 0.04, 0.001, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_LENGTH, AW_WEAVEWIDTH)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

# Start Point Sensing 
   
   # AW_SPSPTN_DL (Enum)
   att = attribCreator.AddEnum(AW_SPSPTN_DL, AW_SPSPTN_LITERALS, AW_SPSPTN_LITERALS[0], USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SPSPTN_DL)
   att.SetReComputeEnterState(ENTERSTATE_STARTWITHMANUALEVENTS)
   att.SetVisibility(True)
   
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
   att.SetVisibility(True)
   
   # RTPM Option 
   att = attribCreator.AddInt(AW_RTPM_NO, 0, 0, 3, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_NO)
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
   att = attribCreator.AddBool(AW_RTPM_SG_DL, True, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_RTPM_SG_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Initial gain time
   att = attribCreator.AddDouble(AW_RTPM_IT_DL, 0.1, 0.1, 9.9, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_RTPM_IT_DL)
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
   att.SetVisibility(True)
   
   # So Option 
   att = attribCreator.AddInt(AW_SSD_NO, 1, 1, 3, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_NO)
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
   
   # Weave Pattern Number 
   att = attribCreator.AddInt(AW_SSD_WP_NO, 0, 0, 10, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_SSD_WP_NO)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Weave Freq
   att = attribCreator.AddDouble(AW_SSD_WF_DL, 0.0, 0, 4.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WF_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)
   
   # Weave Width
   att = attribCreator.AddDouble(AW_SSD_WW_DL, 0.0, 0, 40.0, 0.1, USER_ATTRIBUTE | PROCESS_ATTRIBUTE, ATTRIB_STANDARD, AW_SSD_WW_DL)
   att.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   att.SetVisibility(False)

   # Change the Visibility (Hide) for ArcOnEvent Weave attributes
   try:
      useWeaveAtt = attribGetter.GetAttributeByName(AW_WEAVE_ONOFF)
      useWeaveAtt.SetOlpProperty(USER_ATTRIBUTE)
      useWeaveAtt.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_ONOFF!')

   try:
      weaveFrequenzAtt = attribGetter.GetAttributeByName(AW_WEAVE_FREQUENZ)
      weaveFrequenzAtt.SetOlpProperty(USER_ATTRIBUTE)
      weaveFrequenzAtt.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_FREQUENZ!')

   try:
      weaveWidthAtt = attribGetter.GetAttributeByName(AW_WEAVE_WIDTH)
      weaveWidthAtt.SetOlpProperty(USER_ATTRIBUTE)
      weaveWidthAtt.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_WIDTH!')
   
   try:
      weaveTime1Att = attribGetter.GetAttributeByName(AW_WEAVE_TIME1)
      weaveTime1Att.SetOlpProperty(USER_ATTRIBUTE)
      weaveTime1Att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_TIME1!')

   try:
      weaveTime2Att = attribGetter.GetAttributeByName(AW_WEAVE_TIME2)
      weaveTime2Att.SetOlpProperty(USER_ATTRIBUTE)
      weaveTime2Att.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVE_TIME2!')


   # Hide ProgNumber Attribute
   try:
      progNumberAtt = attribGetter.GetAttributeByName(AW_ARC_PRGNR)
      progNumberAtt.SetOlpProperty(USER_ATTRIBUTE)
      progNumberAtt.SetVisibility(False)
   except:
      logging.LogError('Cannot get the Attribute AW_ARC_PRGNR!')

def PostProcessAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   # Set Arc WeldMode
   try:
      SetArcWeldMode = attribGetter.GetEnumIndex(AW_ARCWELDMODE_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_ARCWELDMODE_DEF!')

   # WC Mode
   try:
      WCMode = attribGetter.GetEnumIndex(AW_WCMODE_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WCMODE_DEF!')

   # WC2 Crater
   try:
      WC2_Crater = attribGetter.GetBool(AW_CRATER_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATER_DEF!')

   # Set Event Attribute Visu
   SetWCAttributeVisu(attribGetter, logging, WCMode, WC2_Crater)

   # WC Number
   try:
      WCNumber = attribGetter.GetInteger(AW_WCNUMBER_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WCNUMBER_DEF!')

   # WC Name
   try:
      WCName = attribGetter.GetString(AW_WCNAME_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WCNAME_DEF!')

   # WC JobNo
   try:
      WCJobNo = attribGetter.GetInteger(AW_WCJOBNO_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WCJOBNO_DEF!')

   # WC1 Weld Speed
   try:
      WC1_WeldSpeed = int(attribGetter.GetDouble(AW_WELDSPEED_DEF))
   except:
      logging.LogError('Cannot get the attribute AW_WELDSPEED_DEF!')      

   # WC1 Wire Feed Speed
   try:
      WC1_WireFeedSpeed = attribGetter.GetDouble(AW_WIREFEEDSPEED_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WIREFEEDSPEED_DEF!')

   # WC1 Weld Current
   try:
      WC1_WeldCurrent = attribGetter.GetDouble(AW_WELDCURRENT_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WELDCURRENT_DEF!')

   # WC1 Arc length corr.
   try:
      WC1_ArclengthCorr = attribGetter.GetDouble(AW_ARCLENGTHCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_ARCLENGTHCORR_DEF!')      
   
   # WC1 Weld Voltage
   try:
      WC1_WeldVoltage = attribGetter.GetDouble(AW_WELDVOLTAGE_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WELDVOLTAGE_DEF!')

   # WC1 Pulse Dynamic Corr.
   try:
      WC1_PulseDynamicCorr = attribGetter.GetDouble(AW_PULSEDYNAMICCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_PULSEDYNAMICCORR_DEF!')

   # WC1 Wire Retract Corr.
   try:
      WC1_WireRetractCorr = attribGetter.GetDouble(AW_WIRERETRACTCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WIRERETRACTCORR_DEF!')


   # WC2 Crater Number
   try:
      CCNumber = attribGetter.GetInteger(AW_CRATERNUMBER_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERNUMBER_DEF!')

   # WC2 Crater Name
   try:
      CCName = attribGetter.GetString(AW_CRATERNAME_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERNAME_DEF!')

   # WC2 Crater JobNo
   try:
      CCJobNo = attribGetter.GetInteger(AW_CRATERJOBNO_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERJOBNO_DEF!')

   # WC2 Time
   try:
      WC2_Time = attribGetter.GetDouble(AW_TIME_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_TIME_DEF!')

   # WC2 Crater Wire Feed Speed
   try:
      WC2_CraterWireFeedSpeed = attribGetter.GetDouble(AW_CRATERWIREFEEDSPEED_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERWIREFEEDSPEED_DEF!')      

   # WC2 Crater Weld Current
   try:
      WC2_CraterWeldCurrent = attribGetter.GetDouble(AW_CRATERWELDCURRENT_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERWELDCURRENT_DEF!')

   # WC2 Crater Arc length corr.
   try:
      WC2_CraterArclengthCorr = attribGetter.GetDouble(AW_CRATERARCLENGTHCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERARCLENGTHCORR_DEF!')      

   # WC2 Crater Weld Voltage
   try:
      WC2_CraterWeldVoltage = attribGetter.GetDouble(AW_CRATERWELDVOLTAGE_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERWELDCURRENT_DEF!')

   # WC2 Crater Pulse Dynamic Corr.
   try:
      WC2_CraterPulseDynamicCorr = attribGetter.GetDouble(AW_CRATERPULSEDYNAMICCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERWELDCURRENT_DEF!')

   # WC2 Crater Wire Retract Corr.
   try:
      WC2_CraterWireRetractCorr = attribGetter.GetDouble(AW_CRATERWIRERETRACTCORR_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_CRATERWIRERETRACTCORR_DEF!')


   # AW_PATTERN (EnumIndex)
   try:
      weavePatternIndex = attribGetter.GetEnumIndex(AW_WEAVE_PATTERN_NO_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WEAVE_PATTERN_NO_DEF!')

   # AW_WEAVE_FREQUENZ
   try:
      weaveFrequenz = attribGetter.GetDouble(AW_WEAVEFREQUENZ_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WEAVEFREQUENZ_DEF!')

   # AW_WEAVE_WIDTH
   try:
      weaveWidth = attribGetter.GetDouble(AW_WEAVEWIDTH_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_WEAVEWIDTH_DEF!')
   
   # AW_StartPointSensing (EnumIndex)
   try:
      spsPatternIndex = attribGetter.GetEnumIndex(AW_SPS_PATTERN_NO_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SPS_PATTERN_NO_DEF!')
      
   # AW_StartPointSensing Sensing Dinstance
   try:
      spsSesnsdist = attribGetter.GetDouble(AW_SPSSD_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SPSSD_DEF!')
   
   # AW_StartPointSensing Relief Dinstance
   try:
      spsReldist = attribGetter.GetDouble(AW_SPSTPRD_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SPSTPRD_DEF!')
   
   # AW_StartPointSensing Distance in Groove 
   try:
      spsDistgr = attribGetter.GetDouble(AW_SPSSDG_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SPSSDG_DEF!')
    
    # AW_DEF RTPM (EnumIndex)
   try:
      rtpmPatternIndex = attribGetter.GetEnumIndex(AW_RTPM_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_DEF!')
      
   # AW_RTPM_WS_DEF WireStick
   try:
      rtpmWireStick = attribGetter.GetInteger(AW_RTPM_WS_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SPSSD_DEF!')
   
   # AW_RTPM_VG_DEF VerticalGain
   try:
      rtpmVerGain = attribGetter.GetInteger(AW_RTPM_VG_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_VG_DEF!')
   
   # AW_RTPM_HG_DEF Horizontal Gain 
   try:
      rtpmHorGain = attribGetter.GetInteger(AW_RTPM_HG_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_HG_DEF!')  
  
   # AW_RTPM_VB_DEF Vertical BIAS 
   try:
      rtpmVerBias = attribGetter.GetInteger(AW_RTPM_VB_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_VB_DEF!')  
      
   # AW_RTPM_HB_DEF Horizontal BIAS 
   try:
      rtpmHorBias = attribGetter.GetInteger(AW_RTPM_HB_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_HB_DEF!') 
   
   # AW_RTPM_SG_DEF Start Gain
   try:
      rtpmStartGain = attribGetter.GetBool(AW_RTPM_SG_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_SG_DEF!') 
           
   # AW_RTPM_II_DEF Delay Time for II
   try:
      rtpmTime = attribGetter.GetInteger(AW_RTPM_II_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_II!') 
                 
   # AW_RTPM_IT_DEF Initial gain time
   try:
      rtpmIniGain = attribGetter.GetDouble(AW_RTPM_IT_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_IT_DEF!')
  
   # AW_RTPM_IGT_DEF Horizontal gain
   try:
      rtpmIniVerGain = attribGetter.GetInteger(AW_RTPM_IVC_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_IVC_DEF!')
      
   # AW_RTPM_IHC_DEF Vertical Gain 
   try:
      rtpmIniHorGain = attribGetter.GetInteger(AW_RTPM_IHC_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_IHC_DEF!')
      
   # AW_RTPM_ICC_DEF Initial change gain
   try:
      rtpmIniChanGain = attribGetter.GetInteger(AW_RTPM_ICC_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_ICC_DEF!')    

   # AW_SSD_DEF EnumIndex
   try:
      ssdIndex = attribGetter.GetEnumIndex(AW_SSD_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_DEF!')        
      
   # AW_SSD_PHT_DEF Preheat time
   try:
      ssdPreheat = attribGetter.GetDouble(AW_SSD_PHT_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_PHT_DEF!')   
   
   # AW_SSD_WP_DEF Weave Pattern
   try:
      ssdWeavpatt = attribGetter.GetEnumIndex(AW_SSD_WP_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_WP_DEF!')       
   # AW_SSD_WF_DEF Weave Frequrency
   try:
      ssdWeavfreq = attribGetter.GetDouble(AW_SSD_WF_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_WF_DEF!')   
   
   # AW_SSD_WW_DEF Weave Frequrency
   try:
      ssdWeavwid = attribGetter.GetDouble(AW_SSD_WW_DEF)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_WW_DEF!')   
      
   attribSetter.SetInteger(AW_ARC_PRGNR, WCJobNo)

   attribSetter.SetEnumIndex(AW_ARCWELDMODE_DL, SetArcWeldMode)
   attribSetter.SetInteger(AW_WCMODE_DL, WCMode)
   attribSetter.SetInteger(AW_WCNUMBER_DL, WCNumber)
   attribSetter.SetString(AW_WCNAME_DL, WCName)
   attribSetter.SetInteger(AW_WCJOBNO_DL, WCJobNo)
   attribSetter.SetInteger(AW_WELDSPEED_DL, WC1_WeldSpeed)

   attribSetter.SetDouble(AW_WIREFEEDSPEED_DL, WC1_WireFeedSpeed)
   attribSetter.SetDouble(AW_WELDCURRENT_DL, WC1_WeldCurrent)
   attribSetter.SetDouble(AW_ARCLENGTHCORR_DL, WC1_ArclengthCorr)
   attribSetter.SetDouble(AW_WELDVOLTAGE_DL, WC1_WeldVoltage)
   attribSetter.SetDouble(AW_PULSEDYNAMICCORR_DL, WC1_PulseDynamicCorr)
   attribSetter.SetDouble(AW_WIRERETRACTCORR_DL, WC1_WireRetractCorr)

   attribSetter.SetBool(AW_CRATER_DL, WC2_Crater)
   attribSetter.SetInteger(AW_CRATERNUMBER_DL, CCNumber)
   attribSetter.SetString(AW_CRATERNAME_DL, CCName)
   attribSetter.SetInteger(AW_CRATERJOBNO_DL, CCJobNo)

   attribSetter.SetDouble(AW_TIME_DL, WC2_Time)
   attribSetter.SetDouble(AW_CRATERWIREFEEDSPEED_DL, WC2_CraterWireFeedSpeed)
   attribSetter.SetDouble(AW_CRATERWELDCURRENT_DL, WC2_CraterWeldCurrent)
   attribSetter.SetDouble(AW_CRATERARCLENGTHCORR_DL, WC2_CraterArclengthCorr)
   attribSetter.SetDouble(AW_CRATERWELDVOLTAGE_DL, WC2_CraterWeldVoltage)
   attribSetter.SetDouble(AW_CRATERPULSEDYNAMICCORR_DL, WC2_CraterPulseDynamicCorr)
   attribSetter.SetDouble(AW_CRATERWIRERETRACTCORR_DL, WC2_CraterWireRetractCorr)

   attribSetter.SetEnumIndex(AW_WEAVE_PATTERN, weavePatternIndex)
   attribSetter.SetInteger(AW_WEAVE_PATTERN_NO, weavePatternIndex)
   attribSetter.SetDouble(AW_WEAVEFREQUENZ, weaveFrequenz)
   attribSetter.SetDouble(AW_WEAVEWIDTH, weaveWidth)
  
   attribSetter.SetEnumIndex(AW_SPSPTN_DL, spsPatternIndex)
   attribSetter.SetInteger(AW_SPSPTN_NO, spsPatternIndex)
   attribSetter.SetDouble(AW_SPSSD_DL, spsSesnsdist)
   attribSetter.SetDouble(AW_SPSTP_DL, spsReldist)
   attribSetter.SetDouble(AW_SPSSDG_DL, spsDistgr)
   
   attribSetter.SetEnumIndex(AW_RTPM_DL, rtpmPatternIndex)
   attribSetter.SetInteger(AW_RTPM_NO, rtpmPatternIndex)
   attribSetter.SetInteger(AW_RTPM_WS_DL, rtpmWireStick)
   attribSetter.SetInteger(AW_RTPM_VG_DL, rtpmVerGain)
   attribSetter.SetInteger(AW_RTPM_HG_DL, rtpmHorGain)
   attribSetter.SetInteger(AW_RTPM_VB_DL, rtpmVerBias)
   attribSetter.SetInteger(AW_RTPM_HB_DL, rtpmHorBias)
   attribSetter.SetBool(AW_RTPM_SG_DL, rtpmStartGain)
   attribSetter.SetInteger(AW_RTPM_II_DL, rtpmTime)
   attribSetter.SetDouble(AW_RTPM_IT_DL, rtpmIniGain)
   attribSetter.SetInteger(AW_RTPM_IVC_DL, rtpmIniVerGain)
   attribSetter.SetInteger(AW_RTPM_IHC_DL, rtpmIniHorGain)
   attribSetter.SetInteger(AW_RTPM_ICC_DL, rtpmIniChanGain)
   
   attribSetter.SetEnumIndex(AW_SSD_DL, ssdIndex)
   attribSetter.SetDouble(AW_SSD_PHT_DL, ssdPreheat)
   attribSetter.SetEnumIndex(AW_SSD_WP_DL, ssdWeavpatt)
   attribSetter.SetInteger(AW_SSD_WP_NO, ssdWeavpatt)
   attribSetter.SetDouble(AW_SSD_WF_DL, ssdWeavfreq)
   attribSetter.SetDouble(AW_SSD_WW_DL, ssdWeavwid)
   # Set the active Welding Speed
   arcSpeedValue = WC1_WeldSpeed / 6000
   try:
      attribSetter.SetDouble(AW_SPEED_WELDING, arcSpeedValue)
   except:
      logging.LogError('Cannot set the Attribute AW_SPEED_WELDING!')

   # Set the ProgNumber
   try:
      attribSetter.SetInteger(AW_ARCSET_PROGNR_DEF, WCJobNo)
   except:
      logging.LogError('Cannot get the attribute AW_ARCSET_PROGNR_DEF!')

   # Set the Weave Pattern Number
   SetWeavePatternNumber(attribGetter, attribSetter, logging)

   # Hide or Show Weave Attributes
   SetWeaveAttributeVisu(attribGetter, logging, weavePatternIndex)
   
   # Set the StartPointSensing Number
   SetSpsPatternNumber(attribGetter, attribSetter, logging)

   # Hide or StartPointSensing Attributes
   SetSpsAttributeVisu(attribGetter, logging, spsPatternIndex)
   
   # Set the RTPM Number
   SetRtpmPatternNumber(attribGetter, attribSetter, logging)

   # Hide or RTPM Attributes
   SetRtpmAttributeVisu(attribGetter, logging, rtpmPatternIndex)
   
   # Set the RTPM Number
   SetSsdPatternNumber(attribGetter, attribSetter, logging)

   # Hide or RTPM Attributes
   SetSsdAttributeVisu(attribGetter, logging, ssdIndex)
   
def PostCompute(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   pass
   
def PostOnAttribChanged(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   pass

def SetWCAttributeVisu(attribGetter, logging, WCModeIndex, CraterMode):
   if WCModeIndex == 0:
      jobModeVisu = True
      manModeVisu = False
      jobmanModeVisu = True
   elif WCModeIndex == 1:
      jobModeVisu = False
      manModeVisu = True
      jobmanModeVisu = True
   else:
      jobModeVisu = False
      manModeVisu= False
      jobmanModeVisu = False

   # # Attribute Set Arc WeldMode        
   # try:
   #    att = attribGetter.GetAttributeByName(AW_ARCWELDMODE_DL)
   #    att.SetVisibility(jobmanModeVisu)
   # except:
   #    logging.LogError('Cannot get the Attribute AW_ARCWELDMODE_DL!')
   
   # # Attribute Weld Condition Mode        
   # try:
   #    att = attribGetter.GetAttributeByName(AW_WCMODE_DL)
   #    att.SetVisibility(jobmanModeVisu)
   # except:
   #    logging.LogError('Cannot get the Attribute AW_WCMODE_DL!')

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
   except:
      logging.LogError('Cannot get the Attribute AW_WELDSPEED_DL!')

   # Attribute Wire Feed Speed         
   try:
      att = attribGetter.GetAttributeByName(AW_WIREFEEDSPEED_DL)
      att.SetVisibility(jobModeVisu)
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
   except:
      logging.LogError('Cannot get the Attribute AW_PULSEDYNAMICCORR_DL!')

   # Attribute Wire Retract corr.         
   try:
      att = attribGetter.GetAttributeByName(AW_WIRERETRACTCORR_DL)
      att.SetVisibility(jobmanModeVisu)
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
   except:
      logging.LogError('Cannot get the Attribute AW_TIME_DL!')

   # Attribute WC2 Wire Feed Speed (m/min)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIREFEEDSPEED_DL)
      if CraterMode == True:
         att.SetVisibility(jobModeVisu)
      else:
         att.SetVisibility(False)
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
   except:
      logging.LogError('Cannot get the Attribute AW_CRATERPULSEDYNAMICCORR_DL!')

   # Attribute WC2 Wire Retract corr. (%)         
   try:
      att = attribGetter.GetAttributeByName(AW_CRATERWIRERETRACTCORR_DL)
      if CraterMode == True:
         att.SetVisibility(jobmanModeVisu)
      else:
         att.SetVisibility(False)
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
      att = attribGetter.GetAttributeByName(AW_WEAVEFREQUENZ)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot get the Attribute AW_WEAVEFREQUENZ!')         
      
   try:
      att = attribGetter.GetAttributeByName(AW_WEAVEWIDTH)
      att.SetVisibility(weaveOnOff)
   except:
      logging.LogError('Cannot set the Attribute AW_WEAVEWIDTH!')
def SetSpsPatternNumber(attribGetter, attribSetter, logging):
   # Get the StartPointSensing Pattern Enum Index
   try:
      spsPatternIndex = attribGetter.GetEnumIndex(AW_SPSPTN_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SPSPTN_DL!')

   try:
      attribSetter.SetInteger(AW_SPSPTN_NO,spsPatternIndex)
   except:
      logging.LogError('Cannot set the attribute AW_SPSPTN_NO!')

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
      
def SetRtpmPatternNumber(attribGetter, attribSetter, logging):
   # Get the RTPM Enum Index
   try:
      rtpmPatternIndex = attribGetter.GetEnumIndex(AW_RTPM_DL)
   except:
      logging.LogError('Cannot get the attribute AW_RTPM_DL!')

   try:
      attribSetter.SetInteger(AW_RTPM_NO,rtpmPatternIndex)
   except:
      logging.LogError('Cannot set the attribute AW_RTPM_NO!')

def SetRtpmAttributeVisu(attribGetter, logging, rtpmPatternIndex):
   if rtpmPatternIndex == 0:
      rtpmOnOff = False
   elif rtpmPatternIndex == 1:
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

def SetSsdPatternNumber(attribGetter, attribSetter, logging):
   # Get the RTPM Enum Index
   try:
      ssdIndex = attribGetter.GetEnumIndex(AW_SSD_DL)
   except:
      logging.LogError('Cannot get the attribute AW_SSD_DL!')

   try:
      attribSetter.SetInteger(AW_SSD_NO,ssdIndex)
   except:
      logging.LogError('Cannot set the attribute AW_SSD_DL!')
      
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