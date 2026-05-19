from centypes import *
import math

# -------------------------------------------------------------------------------------------
# general global definitions. Enter here the technology name, followed by ": "
FILE_NAME = "LT2PTApproach.py: "

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

# Operation Attribute Definition
LS_APPROACH_MTYPE_LIST = ["PTP", "LIN"]
LS_APPROACH_MTYPE = "Motion"
LS_APPROACH_SPEED = "Speed"

LTJ_DEF = "JobNumberForLaser"
LTBIAS_X_DEF = "LTBiasX"
LTBIAS_Y_DEF = "LTBiasY"
LTBIAS_Z_DEF = "LTBiasZ"
LTS_DEF = "LTS"
LTS_DEFs = ["None","On","Point","Off"]
LTSCNT_DEF = "LTSCount"
LTE_DEF = "LTE"
LTE_DEFs = ["None","On","Off"]
LTECNT_DEF = "LTECount"

LT_ACTIV_DEF = "LTActiv"

LENGTH_X1="OffsetP1X"
LENGTH_Y1="OffsetP1Y"
LENGTH_Z1="OffsetP1Z"

LENGTH_X2="OffsetP2X"
LENGTH_Y2="OffsetP2Y"
LENGTH_Z2="OffsetP2Z"

# Event Attributes (for Download)
LTJ_DL = "DLJobNumberLaser"
LTBIAS_X_DL = "DLLTBiasX"
LTBIAS_Y_DL = "DLLTBiasY"
LTBIAS_Z_DL = "DLLTBiasZ"

LTS_DL = "DLLTS"
LTS_DLs = ["None","On","Point","Off"]
LTSINDEX_DL = "DLLTSIndex"
LTSCNT_DL = "DLLTSCount"
LTE_DL = "DLLTE"
LTE_DLs = ["None","On","Off"]
LTEINDEX_DL = "DLLTEIndex"
LTECNT_DL = "DLLTECount"

# Operation Attribut Names
AW_WELDSPEED_DEF = "WC1WeldSpeed"
AW_SPEED_WELDING = "Speed"
AW_FLYBY_WELDING = "FlybyWelding"

AW_WORK_ANGLE = "LocalOffsetRx"
AW_TRAVEL_ANGLE = "LocalOffsetRy"

LASER_SENSOR_EVENT_UUID = "F7A0979F-AA52-4974-9286-6A26CD45977C"
LT_Param_Event_UUID = "F21BBF39-ED1F-446A-8B0C-ED7860AAE2B1"
LT_EVENT_UUID = "0A24F1DA-B513-4E53-A6BC-6DED9F508B17"
LTON_EVENT_UUID = "C78BA38F-EC44-4ABB-A76E-511FD7F13204"
AW_ARC_ON_EVENT_UUID = "120173a6-d528-11e7-9296-cec278b6b50a"


def GetEventName():
   return "LT2PTApproach"
   
def GetEventUuId():
   return "D74014E3-420C-438C-9E69-CBC01D7D5212"
   
def GetIconName():
   return "ToolpathApproach"
   
def GetExplodeCycle():
   return 0

def GetCycleExplodeBehavior():
   return CYCLE_EXPLODEIMMEDIATELY
   
def GetMultipleCreationIsPossible():
   return 1
   
def GetEventType():
   return OLPEVENT_APPROACH

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
   
def IsEnabled():
   return False

def PostInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   # get setter
   attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   
   # Approach Motion Type and Speed
   att1 = attribCreator.AddEnum(LS_APPROACH_MTYPE, LS_APPROACH_MTYPE_LIST,LS_APPROACH_MTYPE_LIST[0], USER_ATTRIBUTE, LS_APPROACH_MTYPE)
   att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   # att1.SetVisibility(False)
   # att1.SetReadOnly(True)
   att2 = attribCreator.AddDouble(LS_APPROACH_SPEED, 0.2,0.01,1.0,0.01, USER_ATTRIBUTE, ATTRIB_SPEED, LS_APPROACH_SPEED)
   att2.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   # Laser Tracking Attributes
   # LJT
   att3 = attribCreator.AddInt(LTJ_DEF, 1, 1, 99, USER_ATTRIBUTE, LTJ_DEF)
   att3.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # LTBIAS X, Y, Z
   att4 = attribCreator.AddDouble(LTBIAS_X_DEF, 0.0,-0.1,0.1,0.001, USER_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_X_DEF)
   att4.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att5 = attribCreator.AddDouble(LTBIAS_Y_DEF, 0.0,-0.1,0.1,0.001, USER_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_Y_DEF)
   att5.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)
   att6 = attribCreator.AddDouble(LTBIAS_Z_DEF, 0.0,-0.1,0.1,0.001, USER_ATTRIBUTE, ATTRIB_LENGTH, LTBIAS_Z_DEF)
   att6.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # LTS
   att7 = attribCreator.AddEnum(LTS_DEF, LTS_DEFs,LTS_DEFs[1], USER_ATTRIBUTE, LTS_DEF)
   att7.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att8 = attribCreator.AddInt(LTSCNT_DEF, 0, 0, 999, USER_ATTRIBUTE, LTSCNT_DEF)
   att8.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # LTE
   att9 = attribCreator.AddEnum(LTE_DEF, LTE_DEFs,LTE_DEFs[1], USER_ATTRIBUTE, LTE_DEF)
   att9.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att10 = attribCreator.AddInt(LTECNT_DEF, 0, 0, 999, USER_ATTRIBUTE, LTECNT_DEF)
   att10.SetReComputeEnterState(ENTERSTATE_STARTWITHRULEEVENTS)

   # LT_ACTIV_DEF
   # att11 = attribCreator.AddBool(LT_ACTIV_DEF, False, USER_ATTRIBUTE, LT_ACTIV_DEF)
   # att11.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)
   # att11.SetVisibility(False)

   att=attribCreator.AddDouble(LENGTH_X1,-0.05,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_X1)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   att=attribCreator.AddDouble(LENGTH_Y1,0.00,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_Y1)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   att=attribCreator.AddDouble(LENGTH_Z1,0.00,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_Z1)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   
   att=attribCreator.AddDouble(LENGTH_X2,-0.05,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_X2)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   att=attribCreator.AddDouble(LENGTH_Y2,0.00,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_Y2)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   att=attribCreator.AddDouble(LENGTH_Z2,0.08,-1.0,1.0, 0.005, USER_ATTRIBUTE, ATTRIB_LENGTH, LENGTH_Z2)
   att.SetReComputeEnterState(ENTERSTATE_COMPLETE)   
   
   # Lasertracking - Tool (normal rotation) must be 0.0 deg (Laser before TCP)
   # 2020-11-12 set the attribute here means you change the 'programming defaults'
   # ToDo: Check to set the attribute only if 'LSensor2PTApproach' is activ!
   #attribSetter.SetDouble("LocalOffsetRz",0.0)
   
   #logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   
   #pass
   
def PostProcessAttributes(Operator):
   # get logger
   #logging = Operator.GetLoggerOperator()
   # get getter
   #attribGetter = Operator.GetAttribGetter()
   # get setter
   #attribSetter = Operator.GetAttribSetter()

   # # Workaround Set Dummy Operation Attribut LT_ACTIV_DEF to True
   # try:
   #    attribSetter.SetBool(LT_ACTIV_DEF,True)
   # except:
   #    logging.LogError('Cannot set the attribute LT_ACTIV_DEF!')
   pass

def PostCompute(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # LS_APPROACH_MTYPE
   try:
      LsApproachMtype = attribGetter.GetEnumIndex(LS_APPROACH_MTYPE)
   except:
      logging.LogError('Cannot get the attribute LS_APPROACH_MTYPE!')

   # LS_APPROACH_SPEED
   try:
      LsApproachSpeed = attribGetter.GetDouble(LS_APPROACH_SPEED)
   except:
      logging.LogError('Cannot get the attribute LS_APPROACH_SPEED!')

   # LTJ_DEF
   try:
      Ltj = attribGetter.GetInteger(LTJ_DEF)
   except:
      logging.LogError('Cannot get the attribute LTJ_DEF!')
   
   # LTBIAS_X_DEF
   try:
      LtBiasX = attribGetter.GetDouble(LTBIAS_X_DEF)
   except:
      logging.LogError('Cannot get the attribute LTBIAS_X_DEF!')
      
   # LTBIAS_Y_DEF
   try:
      LtBiasY = attribGetter.GetDouble(LTBIAS_Y_DEF)
   except:
      logging.LogError('Cannot get the attribute LTBIAS_Y_DEF!')
      
   # LTBIAS_Z_DEF
   try:
      LtBiasZ = attribGetter.GetDouble(LTBIAS_Z_DEF)
   except:
      logging.LogError('Cannot get the attribute LTBIAS_Z_DEF!')

   # LTS_DEF
   try:
      Lts = attribGetter.GetEnumIndex(LTS_DEF)
   except:
      logging.LogError('Cannot get the attribute LTS_DEF!')

   # LTSCNT_DEF
   try:
      LtsCount = attribGetter.GetInteger(LTSCNT_DEF)
   except:
      logging.LogError('Cannot get the attribute LTSCNT_DEF!')
      
   # LTE_DEF
   try:
      Lte = attribGetter.GetEnumIndex(LTE_DEF)
   except:
      logging.LogError('Cannot get the attribute LTE_DEF!')

   # LTECNT_DEF
   try:
      LteCount = attribGetter.GetInteger(LTECNT_DEF)
   except:
      logging.LogError('Cannot get the attribute LTECNT_DEF!')
   
   try:
      LX1 = attribGetter.GetDouble(LENGTH_X1)   
      LY1 = attribGetter.GetDouble(LENGTH_Y1)   
      LZ1 = attribGetter.GetDouble(LENGTH_Z1)
      
      LX2 = attribGetter.GetDouble(LENGTH_X2)   
      LY2 = attribGetter.GetDouble(LENGTH_Y2)   
      LZ2 = attribGetter.GetDouble(LENGTH_Z2)
   except:
      logging.LogError('Cannot get the Approach Length Attributes!')

   # Consideration of the Work Angle
   # AW_WORK_ANGLE
   WorkAngle = 0
   try:
      WorkAngle = attribGetter.GetDouble(AW_WORK_ANGLE)
   except:
      logging.LogError('Cannot get the attribute AW_WORK_ANGLE!')
   
   # Calculate the Triangle (YZ Plane) Hypotenuse = LZ2
   if (WorkAngle!=0):
      LY1 = LY1 + LZ1 * math.sin(math.radians(WorkAngle))
      LZ1 = LZ1 * math.cos(math.radians(WorkAngle))

      LY2 = LY2 + LZ2 * math.sin(math.radians(WorkAngle))
      LZ2 = LZ2 * math.cos(math.radians(WorkAngle))

   # Consideration of the Travel Angle
   # AW_TRAVEL_ANGLE
   TravelAngle = 0
   try:
      TravelAngle = attribGetter.GetDouble(AW_TRAVEL_ANGLE)
   except:
      logging.LogError('Cannot get the attribute AW_TRAVEL_ANGLE!')
   
   # Calculate the Triangle (XZ Plane) Hypotenuse = LZ2
   if (TravelAngle!=0):
       LX2 = LX2 + LZ2 * math.sin(math.radians(TravelAngle))
       LZ2 = LZ2 * math.cos(math.radians(TravelAngle)) 


   # P1 and P2 are relative to the RefPoint (Start Point)
   LX2 += LX1
   LY2 += LY1
   LZ2 += LZ1
   
   # Get the Initial Path Matrix (Start Point)
   M1 = Operator.GetRefTpElement().GetInitialPathMatrix ()
   M2 = Operator.GetRefTpElement().GetInitialPathMatrix ()
   startPoint = Operator.GetRefTpElement()
   
   # Approach direction +/- 1  
   appFactor = int(attribGetter.GetBool("Sys_Att_ApproachDirection"))
   if (appFactor==0):
     appFactor=-1.0
   
   # Process direction +/- 1
   procFactor = int(attribGetter.GetBool("Sys_Att_ProcessFlowDirection"))
   if (procFactor==0):
     procFactor=-1.0

   LY1 = LY1 * (appFactor * procFactor)
   LY2 = LY2 * (appFactor * procFactor)
   
   # Move Matrix
   M1.Translate(LX1,LY1,LZ1,True)
   M2.Translate(LX2,LY2,LZ2,True)
   
   # First point in Approach (Second Point from RefPoint)
   if (LsApproachMtype==1):
      first = Operator.MoveLin(M2)
   else:
      first = Operator.MovePTP(M2)
   
   # set RequestID on Startpoint to sign that an Approach was used (in Case of no Approach, ArcON has to be set)
   Operator.SetTechnologyRequestId(first, TPETECHREQUESTID_APPROACHSTART)
   
   # Add and Set Accuracy On Event (before)
   weldingAccuracy = attribGetter.GetDouble(AW_FLYBY_WELDING)
   approachAccuracy = weldingAccuracy
   AccuracyEvent = Operator.GetEventOperator().AddAccuracyEvent(first,TPINSERTPOS_INSERTAFTER)
   AccuracyEvent.SetAccuracy(approachAccuracy)
   
   # Add and Set Speed Event (after)
   SpeedEvent = Operator.GetEventOperator().AddSpeed(first, TPINSERTPOS_INSERTAFTER)
   SpeedEvent.SetSpeed(LsApproachSpeed)
   
   # Second point in Approach (First Point from RefPoint)
   second = Operator.MoveLin(M1)

   # Add and Set LT_Param_Event (before)
   LT_Param_Event = Operator.GetEventOperator().AddEvent(LT_Param_Event_UUID, second, TPINSERTPOS_INSERTBEFORE)
   LT_Param_Event.SetInteger(LTJ_DL,Ltj)
   LT_Param_Event.SetDouble(LTBIAS_X_DL,LtBiasX)
   LT_Param_Event.SetDouble(LTBIAS_Y_DL,LtBiasY)
   LT_Param_Event.SetDouble(LTBIAS_Z_DL,LtBiasZ)

   # Add Accuracy Off Event (before)
   acc = Operator.GetEventOperator().AddAccuracyEvent(second,TPINSERTPOS_INSERTBEFORE)
   acc.SetCriteria(ACCURACY_OFF)

   # Add and Set LT_Event (before)
   LT_Event = Operator.GetEventOperator().AddEvent(LT_EVENT_UUID, second, TPINSERTPOS_INSERTBEFORE)
   LT_Event.SetEnumIndex(LTS_DL,Lts)
   LT_Event.SetEnumIndex(LTSINDEX_DL, Lts)
   LT_Event.SetInteger(LTSCNT_DL, LtsCount)
   LT_Event.SetEnumIndex(LTE_DL,Lte)
   LT_Event.SetEnumIndex(LTEINDEX_DL, Lte)
   LT_Event.SetInteger(LTECNT_DL, LteCount)

   # Add LTOnEvent (before)
   LT_Event = Operator.GetEventOperator().AddEvent(LTON_EVENT_UUID, second, TPINSERTPOS_INSERTBEFORE)

   # Add ArcOnEvent after Start Point
   ArcOnEvent = Operator.GetEventOperator().AddEvent(AW_ARC_ON_EVENT_UUID, startPoint, TPINSERTPOS_INSERTAFTER)
   
   # Welding Speed  and Accuracy
   # AW_WELDSPEED_DEF (value in cm/min -> conversion to m/s)
   try:
      weldingSpeed = attribGetter.GetDouble(AW_WELDSPEED_DEF) / 6000
   except:
      weldingSpeed = 0.03
      logging.LogError('Cannot get the attribute AW_SPEED_WELDING!')
      
   #weldingSpeed = attribGetter.GetDouble(AW_SPEED_WELDING)
   SpeedEvent = Operator.GetEventOperator().AddSpeed(startPoint, TPINSERTPOS_INSERTAFTER)
   SpeedEvent.SetSpeed(weldingSpeed)
   
   # AW_FLYBY_WELDING
   weldingAccuracy = attribGetter.GetDouble(AW_FLYBY_WELDING)
   AccuracyEvent = Operator.GetEventOperator().AddAccuracyEvent(startPoint,TPINSERTPOS_INSERTAFTER)
   AccuracyEvent.SetAccuracy(weldingAccuracy)
   
   #logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_END)

def PostOnAttribChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Set LTS Attribute Visu
   SetLTSAttributeVisu(attribGetter,logging)

   # Set LTE Attribute Visu
   SetLTEAttributeVisu(attribGetter,logging)
   #pass

def SetLTSAttributeVisu(attribGetter,logging):
   try:
      ltsIndex = attribGetter.GetEnumIndex(LTS_DEF)
   except:
      logging.LogError('Cannot get the attribute LTS_DEF!')

   if ltsIndex == 1:
      visu = True
   else:
      visu = False

   try:
      ltsCountAtt = attribGetter.GetAttributeByName(LTSCNT_DEF)
      ltsCountAtt.SetVisibility(visu)
   except:
      logging.LogError('Cannot get the attribute LTSCNT_DEF!')

def SetLTEAttributeVisu(attribGetter,logging):
   try:
      lteIndex = attribGetter.GetEnumIndex(LTE_DEF)
   except:
      logging.LogError('Cannot get the attribute LTE_DEF!')

   if lteIndex == 1:
      visu = True
   else:
      visu = False

   try:
      lteCountAtt = attribGetter.GetAttributeByName(LTECNT_DEF)
      lteCountAtt.SetVisibility(visu)
   except:
      logging.LogError('Cannot get the attribute LTECNT_DEF!')
