# -------------------------------------------------------------------------------------------
# Name: 
# Description: 
# Debugg info: E2@localhost:5254
# Author: 
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
#     
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *

# RequestIDs for Approach&Retract
# APPROACH_START = 1st ApproachPoint
# APPROACH_MID = 2nd AP, only on 2Point-Approach
# APPROACH_END = 1st Process/ContourPoint
# Retract vice-versa
TPE_REQUEST_ID_APPROACH_START = 5
TPE_REQUEST_ID_APPROACH_MID = 6
TPE_REQUEST_ID_APPROACH_END = 7
TPE_REQUEST_ID_RETRACT_START = 8
TPE_REQUEST_ID_RETRACT_MID = 9
TPE_REQUEST_ID_RETRACT_END = 10

def PostExecute(Operator):
   # put Event on the desired RequestID
   logging = Operator.GetLoggerOperator()
   #logging.LogDebug(".................................PointApproachTechStartRule :: PostExecute")
   tpes = Operator.FindTpeByTechRequestId(TPE_REQUEST_ID_APPROACH_START)
   for x in tpes:
      Operator.AddTpe(x)

def GetUniqueId():
   return "45300B0C-2C54-48DC-BDB3-2ACA76C869F1"

def GetRuleProcessType():
   return EVENTPROCESS_TECHEVENT

def GetInsertPosition():
   return TPINSERTPOS_INSERTBEFORE

def GetActiveEvent():
   return 0

def GetVisibility():
   return 1

def NeedSelection():
   return 1

def GetSelectability():
   return 1

def HasDefault():
   return 1
