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

def GetUniqueId():
   return "2C843357-04F7-4738-838F-9014E59E9873"

def GetRuleProcessType():
   return EVENTPROCESS_INPROCESS

def GetInsertPosition():
   return TPINSERTPOS_INSERTAFTER

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

def PostExecute(Operator):
    tpes = Operator.FindTpElementsByType(EVENTPROCESS_INPROCESS)
    for x in tpes:
        Operator.AddTpe(x)