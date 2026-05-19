# -------------------------------------------------------------------------------------------
# Name: create a report about the Design Change of Process Geometries
# Description: 
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: Apostol
#        Date: 28.07.2025
# -------------------------------------------------------------------------------------------
from os.path import exists
from cenpylib import *
from centypes import *
import sys, os, inspect

from fpdf import FPDF

def GetCommandName():
   return "DesignChangeProcessGeometriesReportScript"
   
def GetCommandUuId():
   return "3D01001F-F178-44E8-B734-A66609D9BA40"
   
def GetIconName():
   return "COM_ScriptsRun"

    
# -------------------------------------------------------------------------------------------
def DesignChangeProcessGeometriesReportScript(Operator: CENPyOlpDesignChangeProcessGeometryReportOperator):    
        
    #full report getter    
    # list for each PG and the report for each PG -> list<tuple<PgName, ReportOnPg>>    
    fullModificationReport = Operator.GetDesignChangeProcessGeometryFullReport()  # Returns list<tuple<string, string>>
    
    #program components report
    programComponentsModificationReport = Operator.GetDesignChangeProcessGeometryProgramComponentsReport()  # Returns string
        
    return[FeedbackOK, "FeedbackOK"]
        
# ============================================
