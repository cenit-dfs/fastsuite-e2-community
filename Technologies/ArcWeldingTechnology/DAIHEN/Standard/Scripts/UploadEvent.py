# -------------------------------------------------------------------------------------------
# Name: ArcOnEvent
# Description: Sets some Upload Attributes
# Debug info: E2@localhost:5254
# Author: Cenit AG 2025
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------
from centypes import *
from cenpylib import *
import importlib
import inspect, os
import sys
import csv

# -------------------------------------------------------------------------------------------
# general global definitions.
FILE_NAME = "UploadEvent.py: "

# DEBUG
DEBUG_INIT_ATTRIBS_START = "(Debug) initialization of attributes started."
DEBUG_INIT_ATTRIBS_END = "(Debug) initialization of attributes ended."

DEBUG_POST_PROCESS_ATTRIB_START = "(Debug) event post process attrib started."
DEBUG_POST_PROCESS_ATTRIB_END = "(Debug) event post process attrib ended."

DEBUG_POST_ON_ATTRIB_CHANGE_START = "(Debug) post on attribute change started."
DEBUG_POST_ON_ATTRIB_CHANGE_END = "(Debug) prev on attribute change ended."

DEBUG_POST_EVENT_COMPUTE_START = "(Debug) event post compute started."
DEBUG_POST_EVENT_COMPUTE_END = "(Debug) event post compute ended."

# ERROR
ERROR_CANNOT_CREATE_ATTRIB = "(Error) Could not create technology attributes."
ERROR_ATTRIB_SETTER_GETTER = "(Error) Could not get attribute setter or getter."
ERROR_GET_ATTRIB = "(Error) Could not get attribute."
ERROR_SET_ATTRIB = "(Error) Could not set attribute."

# Event Attributes
EVENT_EXECUTED = "EventExecuted"
PROGRAM_BASE_NAME = "ProgramBaseName"
ARC_ON_CODE = "ArcOnCode"
ARC_OFF_CODE = "ArcOffCode"
UNIT_MECHS = "UnitMechanism"

OTC_CELL_UNIT = "OTC_CELL_UNIT"
OTC_ARC_ON = "OTC_ARC_ON"
OTC_ARC_OFF = "OTC_ARC_OFF"
OTC_UNIT_NAME = "OTC_UNIT_NAME"
OTC_WIRE_FEED = "OTC_WIRE_FEED"
OTC_CURRENT = "OTC_CURRENT"
OTC_VOLTAGE = "OTC_VOLTAGE"
OTC_WELD_CHARACTER = "OTC_WELD_CHARACTER"
OTC_UNIT_MECHS = "OTC_UNIT_MECHS"

# Operation attribute definition

def GetEventName():
   return "UploadEvent"

def GetIconName():
   return "Upload"

def GetEventUuId():
   return "63D1FFAD-7364-49CC-A51F-77A3D29965F7"

def GetEventType():
   return OLPEVENT_OLP

def IsEnabled():
   return False
   
def GetCycleExplodeBehavior():
   # return CYCLE_EXPLODEFORBIDDEN
   return CYCLE_EXPLODEIMMEDIATELY

# -------------------------------------------------------------------------------------------
# Event post init attributes

def PostInitAttributes(Operator : CENPyOlpEvent_AttribInitOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_START)
   #logging.LogInfo("**********************************  UploadEvent  InitAttribute *******************************************")
   # get setter
   #attribSetter = Operator.GetAttribSetter()
   # get creator
   attribCreator = Operator.GetAttribCreator()
   # get getter
   attribGetter = Operator.GetAttribGetter()

   att2 = attribCreator.AddBool(EVENT_EXECUTED, False, USER_ATTRIBUTE | PROCESS_ATTRIBUTE , EVENT_EXECUTED)
   att2.SetVisibility(False)
   att2 = attribCreator.AddString(PROGRAM_BASE_NAME, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , PROGRAM_BASE_NAME)
   att2.SetVisibility(True)
   att3 = attribCreator.AddString(ARC_ON_CODE, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , ARC_ON_CODE)
   att3.SetVisibility(True)
   att4 = attribCreator.AddString(ARC_OFF_CODE, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , ARC_OFF_CODE)
   att4.SetVisibility(True)
   att5 = attribCreator.AddString(UNIT_MECHS, '', USER_ATTRIBUTE | PROCESS_ATTRIBUTE , UNIT_MECHS)
   att5.SetVisibility(True)

   logging.LogDebug(FILE_NAME + DEBUG_INIT_ATTRIBS_END)   

def PostOnAttribChanged(Operator : CENPyOlpEvent_AttribChangedOperator):
	# get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_ON_ATTRIB_CHANGE_END)

def PostProcessAttributes(Operator : CENPyOlpEvent_PEOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging
   logging.LogDebug(FILE_NAME + DEBUG_POST_PROCESS_ATTRIB_START)
   #logging.LogInfo("**********************************  UploadEvent  PostProcessAttributes *******************************************")
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()


# -------------------------------------------------------------------------------------------
# post event compute    
def PostCompute(Operator : CENPyOlpEvent_EventComputeOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug(FILE_NAME + DEBUG_POST_EVENT_COMPUTE_START)
   #logging.LogInfo("**********************************  UploadEvent  PostCompute *******************************************")
   # get getter
   attribGetter = Operator.GetAttribGetter()

   # Setting the related Cell defaults
   setCellDefaults(Operator)

   pass


# ----------------------------------------------------------------------------------------------
def setCellDefaults(Operator : CENPyOlpEvent_EventComputeOperator):
   """Read the DAIHEN Weld Power Source data"""
   # get logger
   logging = Operator.GetLoggerOperator()
   # get getter
   attribGetter = Operator.GetAttribGetter()
   # get setter
   attribSetter = Operator.GetAttribSetter()

   eventExecuted = attribGetter.GetBool(EVENT_EXECUTED)
   if eventExecuted:
      return
   
   #logging.LogInfo("----------------------------------  UploadEvent  execute Compute --------------------------------------")
   unitName = attribGetter.GetString(PROGRAM_BASE_NAME)
   arcOn = attribGetter.GetString(ARC_ON_CODE)
   arcOff = attribGetter.GetString(ARC_OFF_CODE)
   unitMechs = attribGetter.GetString(UNIT_MECHS)
   
   listCounter = 0
   dataSetFound = False
   dataSet = ""
   dataSetIndex = -1
   datasetByArcOnOff = -1
   path = str(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + '\\TechTabs\\')
   filename = 'CellDefaults.csv'
   # check it by PlugIn Manager
   csvPath = Operator.GetTechTabFolder("CellDefaults.csv")
   
   if os.path.exists(csvPath):
      cellDefaultsFile = csvPath
   else:
      cellDefaultsFile = path + filename

   _otc_CELL_UNIT = ""
   _otc_ARC_ON = ""
   _otc_ARC_OFF = ""
   _otc_UNIT_NAME = ""
   _otc_WIRE_FEED = ""
   _otc_CURRENT = ""
   _otc_VOLTAGE = ""
   _otc_WELD_CHARACTER = ""
   _otc_UNIT_MECHS = ""

   try:
      with open(cellDefaultsFile, 'r') as csvfile:
         csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
         # ignore the first line
         next(csv_reader)
         # reading line by line until the end of the file
         for row in csv_reader:
            
            # Unit Name and Mechs fitting
            if str(row[3]) == unitName and unitsFitting(row[8], unitMechs) == True:
               dataSetFound = True
               dataSet = row
               dataSetIndex = listCounter
            # found Unit Name, but Mechs don't fit
            if str(row[3]) == unitName and dataSetIndex < 0:
               dataSetFound = True
               dataSet = row
               dataSetIndex = listCounter
            # get first avail. Set, where ArcOn/Off fitting
            if str(row[1]) == arcOn and str(row[2]) == arcOff:
               if datasetByArcOnOff == -1:
                  datasetByArcOnOff = listCounter
            # upcount the Index
            listCounter += 1
   except:
      logging.LogWarn('Error Reading CellDefaults CSV File')

   if dataSetFound == True:
      # found a DataSet in the CellDefaults.csv
      row = dataSet
      logging.LogInfo('.....UploadEvent : Setting Defaults for Cell Unit : ' + str(unitName) + " / " + str(row[0]))
      _otc_CELL_UNIT = row[0]
      _otc_ARC_ON = row[1]
      _otc_ARC_OFF = row[2]
      _otc_UNIT_NAME = row[3]
      _otc_WIRE_FEED = row[4]
      _otc_CURRENT = row[5]
      _otc_VOLTAGE = row[6]
      _otc_WELD_CHARACTER = row[7]
      _otc_UNIT_MECHS = row[8]
      attribSetter.SetEnumIndex(OTC_CELL_UNIT, dataSetIndex)
      attribSetter.SetString(OTC_ARC_ON, _otc_ARC_ON)
      attribSetter.SetString(OTC_ARC_OFF, _otc_ARC_OFF)
      attribSetter.SetString(OTC_UNIT_NAME, _otc_UNIT_NAME)
      attribSetter.SetInteger(OTC_WELD_CHARACTER, int(_otc_WELD_CHARACTER))
      attribSetter.SetInteger(OTC_WIRE_FEED, int(_otc_WIRE_FEED))
      attribSetter.SetInteger(OTC_CURRENT, int(_otc_CURRENT))
      attribSetter.SetInteger(OTC_VOLTAGE, int(_otc_VOLTAGE))
      attribSetter.SetString(OTC_UNIT_MECHS, _otc_UNIT_MECHS)
      if unitsFitting(_otc_UNIT_MECHS, unitMechs) == False:
         logging.LogWarn('The Unit Mechanism of the Cell Default (' + str(_otc_UNIT_MECHS) + ') and the uploaded Program (' + str(unitMechs) + ') does NOT have the same Items.')
   else:
      # set some Stuff anyway
      if datasetByArcOnOff < 0:
         datasetByArcOnOff = 0
      attribSetter.SetEnumIndex(OTC_CELL_UNIT, datasetByArcOnOff)
      _otc_ARC_ON = attribGetter.GetString(ARC_ON_CODE)
      if _otc_ARC_ON:
         attribSetter.SetString(OTC_ARC_ON, _otc_ARC_ON)
      _otc_ARC_ON = attribGetter.GetString(ARC_OFF_CODE)
      if _otc_ARC_OFF:
         attribSetter.SetString(OTC_ARC_OFF, _otc_ARC_OFF)
   
   attribSetter.SetBool(EVENT_EXECUTED, True)

def unitsFitting(unitA: str, unitB: str):
   """comparing the Unit Mechanism Sets"""
   if unitA is not None and unitB is not None:
         unitA = set(map(int, unitA.split(',')))
         unitB = set(map(int, unitB.split(',')))
         if unitA == unitB:
            return True
   return False