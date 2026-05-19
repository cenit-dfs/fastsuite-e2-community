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
   return "ToolpathReport"
   
def GetCommandUuId():
   return "738306BC-17D0-49E4-9619-40221E2CFDCC"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator: CENPyOlpProgramModifyOperator):
   
   # ======== create a PDF Report =============
   pdf = ReportUtility()
   ret = pdf.createAuxCommandsPDFReport(Operator, "")
   
   # == check Return and give User Feedback ===
   nls = NLSUtility()
   nls.defineNLS(language=nls.getETwoNLS(Operator), project="common")
   if ret > 0:
      nlsMes = "message" + str(ret).zfill(4) # message0001
      warnMes = nls.getNLS("feedbackWarning") + " : " + nls.getNLS(nlsMes)
      return [FeedbackWarning, warnMes]
   else:
      return [FeedbackOK,nls.getNLS("feedbackOK")]
   
# ============================================
