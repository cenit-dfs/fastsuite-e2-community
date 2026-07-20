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

class ArcReportUtility(ArcReportUtility):
   '''
   Class "ArcReportUtility" for PDF Reports
   '''
   def cenheader(self, Operator, portrLands):
      '''
      Defines the customized Header of the PDF Report, underneath common Header
      
      Args:
         Operator : the CENPyOlpProgramModifyOperator
         portrLands : if Report is created in Portrait or Landscape Mode
      '''
      self.__currentSpeed = 0.0
      self.__seamTable = 1
      self.set_font(self.__fontType, size=int(int(self.__fontSize)*1.5))
      self.set_font(self.__fontType, style=self.__fontStyle)
      self.cell(80, 10, self.__NLS.getNLS("title","Arc Welding Report*"), border=0, align="L")
      # Performing a line break:
      self.ln(2)
      self.header_table(Operator)
      
      # ======= added Code due to different Attribute Usage of  OTC_WELD_PRGNR_DEF <==> ProgNumberDefine ======
      # ======= ProgNumberDefine is used in Std.Python Class
      # get active program
      program = Operator.GetActiveProgram()
      # get all operations
      operations = program.GetOperations()
      # ----------- get all Operations in Program ------
      opList = []
      for op in operations:
         attribGetter = op.GetAttribGetter()
         attribSetter = op.GetAttribSetter()
         
         # ONLY STITCHWELDING OPERATIONS !
         wmAttrib = attribGetter.GetAttributeByName(self.AW_OPERATION_WORKMETHOD_NAME)
         wmName = ""
         if wmAttrib.IsValid():
            wmName = attribGetter.GetString(self.AW_OPERATION_WORKMETHOD_NAME)
         if wmName != self.AW_STITCHWELDING_WORKMETHOD:
            continue
         # put OTC_WELD_PRGNR_DEF Value to ProgNumberDefine
         opAttrib = attribGetter.GetAttributeByName("OTC_WELD_PRGNR_DEF")
         if opAttrib.IsValid():
            pgmnr = attribGetter.GetInteger("OTC_WELD_PRGNR_DEF")
            opAttrib = attribGetter.GetAttributeByName("ProgNumberDefine")
            if opAttrib.IsValid():
               attribSetter.SetInteger("ProgNumberDefine", pgmnr, ATTRIBOVERRIDEMODE_OPERATIONLEVEL)
      
      
      
      
      
      
      
      
      
      