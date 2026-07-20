# -------------------------------------------------------------------------------------------
# Name: create a PDF report about the toolpath quality
# Description: 
# Author: Cenit AG
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

from os.path import exists
from cenpylib import *
from centypes import *
import sys, os, inspect

from fpdf import FPDF

sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

def GetCommandName():
   return "ArcWeldReport"
   
def GetCommandUuId():
   return "D54B9E29-7E6C-4035-86BB-17E0B4A47621"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator: CENPyOlpProgramModifyOperator):
   
   # ======== create an ArcWelding PDF Report =============
   arc = ArcReportUtility()
   ret = arc.createAuxCommandArcWeldReport(Operator, "")
   
   # -------- final Message as Feedback Bubble ------------
   nls = NLSUtility()
   if ret > 0:
      nls.defineNLS(language=nls.getETwoNLS(Operator), project="common")
      nlsMes = "message" + str(ret).zfill(4) # message0001
      warnMes = nls.getNLS("feedbackWarning") + " : " + nls.getNLS(nlsMes)
      return [FeedbackWarning, warnMes]
   else:
      nls.defineNLS(language=nls.getETwoNLS(Operator), project="arcreport")
      text = nls.getNLS("pdfsuccess") + " : " + Operator.GetController().GetOutputDirectory()
      return [FeedbackOK,text]
   
   
# ============================================

#class ArcReportUtility(ArcReportUtility):
#   '''
#   Class "ArcReportUtility" for PDF Reports
#   '''

      
      
      
      
      
      
      
      
      
      