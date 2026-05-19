# -------------------------------------------------------------------------------------------
# Name: ArcWeldingTechnology
# Description: Customisation for PANASONIC
# Debug info: E2@localhost:5254
# Author: Pfeifer
# Changelog:
#     Version: 1.0
#        Changed by: Pfeifer
#        Date: 2024-03-25
#
# -------------------------------------------------------------------------------------------

# Import libraries

import inspect, os, sys
sys.dont_write_bytecode = True
from centypes import *
import inspect, os
import csv

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

SYS_ATT_PROCESSFLOWDIRECTION = "Sys_Att_ProcessFlowDirection"

# Attribute definition
AW_ARC_PRGNR_DEF = "ProgNumberDefine"
AW_SPEED_WELDING = "Speed"
AW_ARCDATANAME_DEF = "Arc Data Set"
AW_ARCSET_PROGNR_DEF = "ArcSet ProgNumber"
AW_ARCSET_AMP_DEF = "ArcSet Amp (A)"
AW_ARCSET_VOLT_DEF = "ArcSet Volt (V)"
AW_ARCSET_SPEED_DEF = "ArcSet Speed (m/min)"
AW_CRATER_AMP_DEF = "Crater Amp (A)"
AW_CRATER_VOLT_DEF = "Crater Volt (V)"
AW_CRATER_TIME_DEF = "Crater Time (s)"

AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
MAX_INTEGER = 2147483647
AW_MACHANISM_NUMBER=0
AW_MECHANISMNAME="Mechanism"
AW_SLAVEPROGRAM='SlaveProgram'
AW_SLAVEROBOTNAME='SlaveRobotName'
AW_ISSLAVEPROGRAM = 'IsSlaveProgram'


# -------------------------------------------------------------------------------------------
# Technology post attribute initialization
def PostTechInitAttributes(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # get attribute creator
   attribCreator = Operator.GetAttribCreator()
   # get attribute getter
   attribGetter = Operator.GetAttribGetter()
   # get attribute setter
   attribSetter = Operator.GetAttribSetter()

   # Read the Panasonic ARCSET.csv file
   try:
      ArcSetData = []
      AW_ARCDATANAME_DEFs = []
      numArcSetData = 0
      # read content from the file
      filename = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\ARCDATASET.csv')
      with open(filename, 'r') as csvfile:
         csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
         # ignore the first line
         next(csv_reader)
         # reading line by line until the end of the file
         # the content is added to the end of the list, until everyting in read
         for row in csv_reader:
            ArcSetData.append(row)
            AW_ARCDATANAME_DEFs.append(row[0])
         
   except:
      logging.LogError('Cannot read the ARCDATASET.csv file!')
      
   logging.LogDebug(FILE_NAME + str(len(ArcSetData)))

   # Get the corresponding ArcSetData Column by index
   try:
      ArcSetDataIndex = 0
      ArcSetDataColumn = ArcSetData[ArcSetDataIndex]
      logging.LogDebug(FILE_NAME + 'ArcSetDataIndex: ' + str(ArcSetDataIndex))
      
   except:
      logging.LogError('Cannot read the ArcSetDataColumn!')

   # Get defined values from the ArcSetData Column
   arcSetPrognrValue = int(ArcSetDataColumn[0])
   arcDataName = ArcSetDataColumn[1]
   arcSetAmpValue = int(ArcSetDataColumn[2])
   arcSetVoltValue = float(ArcSetDataColumn[3].replace(",","."))
   arcSetSpeedValue = float(ArcSetDataColumn[4].replace(",","."))
   craterAmpValue = int(ArcSetDataColumn[5])
   craterVoltValue = float(ArcSetDataColumn[6].replace(",","."))
   craterTimeValue = float(ArcSetDataColumn[7].replace(",","."))
   
   logging.LogDebug(FILE_NAME + str(arcSetPrognrValue) + ',' + str(arcSetAmpValue) + ',' + str(arcSetVoltValue) + ',' + str(arcSetSpeedValue))

   # Create Panasonic ARC-SET attributes
   #att1 = attribCreator.AddEnum(AW_ARCDATANAME_DEF, AW_ARCDATANAME_DEFs, AW_ARCDATANAME_DEFs[0], GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE, AW_ARCDATANAME_DEF)
   #att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   att1 = attribCreator.AddString(AW_ARCDATANAME_DEF, arcDataName, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, AW_ARCDATANAME_DEF)
   att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att2 = attribCreator.AddInt(AW_ARCSET_AMP_DEF, arcSetAmpValue, 10, 600, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, AW_ARCSET_AMP_DEF)
   att2.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att3 = attribCreator.AddDouble(AW_ARCSET_VOLT_DEF, arcSetVoltValue, 0.1, 100.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, ATTRIB_STANDARD, AW_ARCSET_VOLT_DEF)
   att3.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att4 = attribCreator.AddDouble(AW_ARCSET_SPEED_DEF, arcSetSpeedValue, 0.1, 10.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, ATTRIB_STANDARD, AW_ARCSET_SPEED_DEF)
   att4.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att5 = attribCreator.AddInt(AW_CRATER_AMP_DEF, craterAmpValue, 10, 600, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, AW_CRATER_AMP_DEF)
   att5.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att6 = attribCreator.AddDouble(AW_CRATER_VOLT_DEF, craterVoltValue, 0.1, 100.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATER_VOLT_DEF)
   att6.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att7 = attribCreator.AddDouble(AW_CRATER_TIME_DEF, craterTimeValue, 0.1, 10.0, 0.1, GLOBAL_ATTRIBUTE | OPERATION_GROUP_ATTRIBUTE | OPERATION_ATTRIBUTE | USER_ATTRIBUTE | READONLY_ATTRIBUTE, ATTRIB_STANDARD, AW_CRATER_TIME_DEF)
   att7.SetReComputeEnterState(ENTERSTATE_COMPLETE)

   att8 = attribGetter.GetAttributeByName(AW_ARC_PRGNR_DEF)
   att9 = attribGetter.GetAttributeByName(AW_SPEED_WELDING)


   groupPanasonic_ARC_SET = attribCreator.AddAttribGroup("Panasonic_ARC_SET")
   groupPanasonic_ARC_SET.AddAttribute(att1)
   groupPanasonic_ARC_SET.AddAttribute(att2)
   groupPanasonic_ARC_SET.AddAttribute(att3)
   groupPanasonic_ARC_SET.AddAttribute(att4)
   groupPanasonic_ARC_SET.AddAttribute(att5)
   groupPanasonic_ARC_SET.AddAttribute(att6)
   groupPanasonic_ARC_SET.AddAttribute(att7)
   groupPanasonic_ARC_SET.AddAttribute(att8)
   groupPanasonic_ARC_SET.AddAttribute(att9)
  
   # Read Mechanisms
   # expected format STATION;MECHANISMNAME;EANUMBER,EANUMBER,EANUMBER,...
   # i.e. Robot1;Mechanism1;G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,A (DEFAULT)
   # i.e A;Mechanism1;G4,G5,G6  
   filename = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) +  '\\TechTabs\\Mechanisms.csv')
   numOfMechanisms=0
   Mechanisms = []
   with open(filename, 'r') as csvfile:
      csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
      next(csv_reader)
      for row in csv_reader:
         # Collect Data for Naming
         mechName=str(row[0]+':'+row[1]+ ':Robot')
         #mechName=str(row[0])
         try:
            for iEA in row[2].split(','):
               mechName += ','+str(iEA)
         except:
            logging.LogInfo('### No external axes in Mechanism detected!"')
         if Operator.GetController().GetResources(0,0)[0].GetName() == 'R002-ROBOT':
            mechName += '_ROBOT2'
         Mechanisms.append(mechName)
         numOfMechanisms+=1

   attribCreator.AddInteger(AW_GLOBAL_TOUCH_COUNTER, 0, 1, MAX_INTEGER, GLOBAL_ATTRIBUTE, AW_GLOBAL_TOUCH_COUNTER)
   att1=attribCreator.AddEnum(AW_MECHANISMNAME, Mechanisms, 'Mechanism1', USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_MECHANISMNAME)
   att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)
   attribCreator.AddString(AW_SLAVEPROGRAM,'',GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE  ,AW_SLAVEPROGRAM)
   attribCreator.AddString(AW_SLAVEROBOTNAME,'',GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE  ,AW_SLAVEROBOTNAME)
   attribCreator.AddBool(AW_ISSLAVEPROGRAM,False ,GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE ,AW_ISSLAVEPROGRAM)
   
   # Template to set Attribute to enable SeamTracking-Off-EventRule
   #attr = attribGetter.GetAttributeByName("SeamTrackingOffEventActive")
   #if (attr):
   #   attribSetter.SetBool("SeamTrackingOffEventActive", True)
   
   # add TouchConnectId-Event from last OpGroup with Touches to Welding-Op (default) or no TouchConnect-Event on single Welding Ops
   # True = no Connect-Events on single Welding-OPs, False(default) = add Connect-Event on single Welding-OPs, ID from last Touch-OP
   lastTouchId = attribCreator.AddBool(AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP, True, USER_ATTRIBUTE | GLOBAL_ATTRIBUTE, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   lastTouchId.SetVisibility(False)
   
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Technology post event initialization
# def PostTechInitEvents(Operator):
#    # get logger
#    logging = Operator.GetLoggerOperator()
#    # debug logging
#    logging.LogDebug(FILE_NAME + DEBUG_INIT_EVENTS_START)

#    # YOUR CODE

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
   attribName = changedAttrib.GetName()
   logging.LogDebug('OnAttribChanged - Attribute Name: ' + str(attribName))

   numberOfRows = 0

   # Customizing Start
   if attribName == AW_ARC_PRGNR_DEF:
      # Read the Panasonic ARCSET.csv file
      try:
         ArcSetData = []
         # read content from the file
         filename = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\ARCDATASET.csv')
         with open(filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
            # ignore the first line
            next(csv_reader)
            # reading line by line until the end of the file
            # the content is added to the end of the list, until everyting in read
            for row in csv_reader:
               numberOfRows += 1
               ArcSetData.append(row)
            
      except:
         logging.LogError('Cannot read the ARCDATASET.csv file!')

      logging.LogDebug('OnAttribChanged: ' + str(len(ArcSetData)))

      # Get the active Welding Program Number
      try:
         #ArcSetDataIndex = attribGetter.GetEnumIndex(AW_ARCDATANAME_DEF)
         arcPrognrValue = attribGetter.GetInteger(AW_ARC_PRGNR_DEF)
         ArcSetDataIndex = arcPrognrValue - 1
         
         logging.LogDebug('OnAttribChanged: ' + str(arcPrognrValue))
         
      except:
         logging.LogError('Cannot get the Attribute AW_ARC_PRGNR_DEF!')

      if arcPrognrValue > 0 & arcPrognrValue <= numberOfRows:
         # Get the corresponding ArcSetData Column by index
         try:
            ArcSetDataColumn = ArcSetData[ArcSetDataIndex]
            
         except:
            logging.LogError('Cannot read the ArcSetDataColumn!')

         # Get defined values from the ArcSetData Column
         arcSetPrognrValue = int(ArcSetDataColumn[0])
         arcDataName = ArcSetDataColumn[1]
         arcSetAmpValue = int(ArcSetDataColumn[2])
         arcSetVoltValue = float(ArcSetDataColumn[3].replace(",","."))
         arcSetSpeedValue = float(ArcSetDataColumn[4].replace(",","."))
         craterAmpValue = int(ArcSetDataColumn[5])
         craterVoltValue = float(ArcSetDataColumn[6].replace(",","."))
         craterTimeValue = float(ArcSetDataColumn[7].replace(",","."))
         
         logging.LogDebug('OnAttribChanged: ' + str(arcSetPrognrValue) + ',' + str(arcSetAmpValue) + ',' + str(arcSetVoltValue) + ',' + str(arcSetSpeedValue))
      else:
         # Set undefined values
         arcDataName = "nicht belegt"
         arcSetAmpValue = 100
         arcSetVoltValue = 0.0
         arcSetSpeedValue = 1.8
         craterAmpValue = 100
         craterVoltValue = 0.0
         craterTimeValue = 0.0        
      

      # set the active Welding Speed
      arcSpeedValue = arcSetSpeedValue / 60
      try:
         attribSetter.SetDouble(AW_SPEED_WELDING,arcSpeedValue)
                     
      except:
         logging.LogError('Cannot set the Attribute AW_SPEED_WELDING!')         

      # Set the Panasonic ARC-SET attributes
      attribSetter.SetString(AW_ARCDATANAME_DEF, arcDataName)
      attribSetter.SetInteger(AW_ARCSET_AMP_DEF, arcSetAmpValue)
      attribSetter.SetDouble(AW_ARCSET_VOLT_DEF, arcSetVoltValue)
      attribSetter.SetDouble(AW_ARCSET_SPEED_DEF, arcSetSpeedValue)
      attribSetter.SetInteger(AW_CRATER_AMP_DEF, craterAmpValue)
      attribSetter.SetDouble(AW_CRATER_VOLT_DEF, craterVoltValue)
      attribSetter.SetDouble(AW_CRATER_TIME_DEF, craterTimeValue)


# -------------------------------------------------------------------------------------------
# Technology post on frame change
def PostTechOnFrameChanged(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_FRAME_CHANGE_START)
   
   # attribGetter = Operator.GetAttribGetter()
   # attribSetter = Operator.GetAttribSetter()

   # YOUR CODE

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)


# -------------------------------------------------------------------------------------------
# Technology get technology Python version
def GetPythonTechnologyVersion():
   return 4


# -------------------------------------------------------------------------------------------
# Technology post update technology
def PostTechUpdate(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_TECH_UPDATE_START)
   
   # attribGetter = Operator.GetAttribGetter()
   # attribSetter = Operator.GetAttribSetter()
   
   # YOUR CODE
   
   program = Operator.GetOlpProgram()
   attribCreator = Operator.GetAttribCreator(program)
   myString= attribCreator.AddString(AW_SLAVEPROGRAM,'',GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE ,AW_SLAVEPROGRAM)
   myString2= attribCreator.AddString(AW_SLAVEROBOTNAME,'',GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE ,AW_SLAVEROBOTNAME)
   myBool= attribCreator.AddBool(AW_ISSLAVEPROGRAM,False ,GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE | USER_ATTRIBUTE ,AW_ISSLAVEPROGRAM)
   attribGetter=Operator.GetAttribGetter(program)
   
   # Read Mechanisms
   # expected format STATION;MECHANISMNAME;EANUMBER,EANUMBER,EANUMBER,...
   # i.e. Robot1;Mechanism1;G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,A (DEFAULT)
   # i.e A;Mechanism1;G4,G5,G6  
   filename = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) +  '\\TechTabs\\Mechanisms.csv')
   numOfMechanisms=0
   Mechanisms = []
   with open(filename, 'r') as csvfile:
      csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
      next(csv_reader)
      for row in csv_reader:
         # Collect Data for Naming
         mechName=str(row[0]+':'+row[1]+ ':Robot')
         for iEA in row[2].split(','):
            try: 
               int(iEA)
            except ValueError:
               mechName += ','+str(iEA)
            else:
               mechName += ',G'+str(iEA)   
         Mechanisms.append(mechName)
         numOfMechanisms+=1
   Operator.RemoveAttribute(program,AW_MECHANISMNAME)   
   att1=attribCreator.AddEnum(AW_MECHANISMNAME, Mechanisms, 'Mechanism1', USER_ATTRIBUTE | GLOBAL_ATTRIBUTE | PROCESS_ATTRIBUTE, AW_MECHANISMNAME)
   att1.SetReComputeEnterState(ENTERSTATE_COMPLETE)

        
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_TECH_UPDATE_END)
