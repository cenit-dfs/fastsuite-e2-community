'''
COPYRIGHT Cenit AG Q1/2024
   Production ready YASKAWA/MOTOMAN arc welding downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off            YES
      touch sensing in surface direction:          YES
      touch sensing with wire:                     
      wire check for touch with wire:              
      touch sensing with nozzle:                   
      seam search:                                 YES
      seam finding:                                NO
      seam tracking:                               NO
      robot team/synchronized multi robot motions: NO

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
'''

import sys, inspect, os
import importlib

sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
sys.argv  = ['']
sys.dont_write_bytecode = True

from cenpydownload import *
from cenpyolpcore import *

def ensure_module_is_updated(module_name):
      if module_name in sys.modules:
         importlib.reload(sys.modules[module_name])
      else:
         importlib.import_module(module_name)

# import base class and define class name of the current download
ensure_module_is_updated('Yaskawa')#  <---- Perform module force-reload in order to apply hot changes
from Yaskawa import Yaskawa
DOWNLOAD_CLASS_NAME = "Yaskawa_Arc_Welding"

WEAVE_METHODS = ["No Weaving", "WEV#()", "ComArc WEV#()", "ComArc AMP="] 
WEAVING_DIRECTIONS = ["Unused", "0" , "1"]

class Yaskawa_Arc_Welding(Yaskawa):
   '''Yaskawa arc welding downloader
   Base robot vendor downloader
   Derived from: Base downloader
   '''

#################### BASE FUNCTIONS ####################

   def __init__(self):
      super().__init__()
      self.DEBUG = False
      self.CurrentProgNumber = -1
      self.CurrentWeaveOnOff = False
      self.CurrentWeaveFrequenz = -1
      self.CurrentWeaveWidth = -1
      self.CurrentWeaveTime1  = -1
      self.CurrentWeaveTime2 = -1
      self.DataPV =[]
      self.IsTouchPointCollision = False
      self.IsTouchPointStartApp = False
      self.IsTouchPointRetApp = False
      self.CurrentTSCounter = 0
      self.CurrentTSCount = -1
      self.CurrentTouchID = -1
      self.PreviousTouchID = -1
      self.ArcWeldingActive = False
      self.CorrectionActive = False
      self.CurrentSensingSpeed = 150
      self.CurrentOvertravelLength = 10
      self.SensingPort = 3
      self.TouchsenseSensingSpeed = 150
      self.SeamSearchSensingSpeed = 150
      self.TouchsenseOvertravelLength = 30
      self.SeamSearchOvertravelLength = 30
      self.PowerSource = ""
      self.CraterFill = False 
      self.CraterFillDelay = 0
      self.ArcWeldingTorchType = ""
      self.WeaveOnCmd = ""
      self.IsWeavingActive = False
   
   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
      """
      # call method from parent class
      super().ProgramStart(operator, program)  
      # for att in program.GetAttributes():
      #   pass
      self.GlobalGetAttributes(operator, program)
      
      self.AppendOnNonExistence('P%05d=0,0,0,0,0,0' % (1),self.DataPV)
      self.AppendOnNonExistence('P%05d=0,0,0,0,0,0' % (2),self.DataPV)
      self.AppendOnNonExistence('P%05d=0,0,0,0,0,0' % (3),self.DataPV)
      self.PosCounterP = 3

   def OperationGroupStart(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      """Called at the start of each operation group.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operationGroup (DULPythonOperationGroup):operation group operator gives access to the current operation group
      """
      # call method from parent class
      super().OperationGroupStart(operator,operationGroup)  
      for att in operationGroup.GetAttributes():
         if att.GetName() == 'Touch_Cntr':
            self.CurrentTSCount = att.GetValue()
         elif att.GetName() == 'TouchId':
            self.CurrentTouchID = int(att.GetValue())   
      self.GlobalGetAttributes(operator,operationGroup)

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Called at the start of each operation.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator gives access to the current operation
      """
      # call method from parent class
      super().OperationStart(operator,operation)  
      for att in operation.GetAttributes():
         if att.GetName() == 'Touch_Cntr':
            self.CurrentTSCount = att.GetValue()
         elif att.GetName() == 'TouchId':
            self.CurrentTouchID = int(att.GetValue())   

      self.GlobalGetAttributes(operator,operation)      

      if self.currentOperationWorkMethod in ('TouchSensingWorkMethod', 'SeamSearchWorkMethod'):      
         if (self.CurrentTouchID != self.PreviousTouchID and self.PreviousTouchID >-1):
            self.CurrentTSCounter = 1
         else:
            self.CurrentTSCounter +=1
         #self.Source.append('\' TouchSense Operation ' + str(self.CurrentTSCounter) +'/' + str(self.CurrentTSCount) +' TouchID: ' + str(self.CurrentTouchID))

   def HandleMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Called for each motion. A motion can have two positions (like circular motions).
      Furthermore, a motion can have events before or after. This means that the events are also managed here.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      # call method from parent class
      super().HandleMotion(operator,motion)
      if self.IsTouchPointStartApp:
         if self.DEBUG:
            self.Source.append('\'SEARCHMACRO ' + 'P{num:0{width}}'.format(num=self.CurrentTSCounter,width=5))

         SenseSpeedCmMin = self.CurrentSensingSpeed*100*60
         self.Source.append('MACRO1 MJ#(28) ARGF0 ARGFC%05d ARGFBC%05d ARGFC%05d ARGFBC%05d ARGFC%05d ARGFBC%05d ARGF1 ARGF%i ARGF%i ARGF25 ARGF%d ARGF25 ARGF2 ARGF99 ARGF%d' % (self.PosCounterC-1, self.PosCounterC-1, self.PosCounterC, self.PosCounterC, self.PosCounterC+1, self.PosCounterC+1,SenseSpeedCmMin, self.CurrentOvertravelLength, self.CurrentTSCounter, self.SensingPort))
         self.IsTouchPointStartApp = False
         # Append position variable         
         if self.AppendOnNonExistence('P%05d=0,0,0,0,0,0' % (self.CurrentTSCounter),self.DataPV) == 0:
            self.PosCounterP += 1
      if self.IsTouchPointCollision:
         if self.DEBUG:
            self.Source.append('\' CORRRECTIONHANDLING ' +'P{num:0{width}}'.format(num=self.CurrentTSCounter,width=5))
         #for i in range(self.CurrentTSCounter,1,-1):
         if self.CurrentTSCounter >1:
            self.Source.append('ADD P%05d P%05d' % (self.CurrentTSCounter-1,self.CurrentTSCounter))
         self.Source.append('SFTON P%05d' % (self.CurrentTSCounter))
         if self.CurrentTSCounter == self.CurrentTSCount:
            if self.AppendOnNonExistence('P%05d=0,0,0,0,0,0' % (self.CurrentTouchID),self.DataPV) == 0:
               self.PosCounterP += 1
            
            self.Source.append('SET P%05d P%05d' % (self.CurrentTouchID, self.CurrentTSCounter))
            self.Source.append('SUB P00001 P00001')
            self.Source.append('SUB P00002 P00002')
            self.Source.append('SUB P00003 P00003')
            pass
         self.IsTouchPointCollision = False
      if self.IsTouchPointRetApp:
         self.IsTouchPointRetApp = False

   def OperationEnd(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Called at the end of each operation.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator gives access to the current operation
      """
      # call method from parent class
      super().OperationEnd(operator,operation)
      # Reset in case Touch_Cntr == Self.currentTSCount or  different TouchId
      if (self.CurrentTSCounter == self.CurrentTSCount):
         self.CurrentTSCounter = 0
      self.PreviousTouchID = self.CurrentTouchID
      # Handle Correction
      if self.CorrectionActive:
         self.Source.append('SFTOF')
         self.CorrectionActive = False

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Write output file; Overwrite output block order (Pos vars should come after External Axes)
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.JobHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataC)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataBC)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataEC)
      #Pos variables
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataPV)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.JobFooter)

      operator.AddOutputFilePath(self.OutputFilePath)


#################### EVENTS ####################

   def OutputEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Output event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      super().OutputEvent(operator,event)
      if event.GetName() == 'TouchPointCollisionEvent':
         self.IsTouchPointCollision = True
         self.skipSourceMotion = True
         self.suppressBCOutput = False
         self.suppressECOutput = True
      elif event.GetName() == 'TouchPointStartAppEvent':
         self.IsTouchPointStartApp = True
         self.skipSourceMotion = True  
         self.suppressBCOutput = False
         self.suppressECOutput = True
      elif event.GetName() == 'TouchPointStartRetEvent':
         self.IsTouchPointRetApp = True
         self.skipSourceMotion = True  
         self.suppressBCOutput = False
         self.suppressECOutput = True
      elif event.GetName() == 'ConnectTouchProcessPointEvent':
         self.SetConnectionID(operator,event)
      elif event.GetName() == 'ArcOnEvent':
         self.OutputArcOnEvent(event)
      elif event.GetName() == 'ArcOffEvent':
         self.OutputArcOffEvent(event)
      attributes = event.GetAttributes()
      for attribute in attributes:
         #self.OutputAttribute(operator, attribute)
         pass

   def OutputArcOnEvent(self, event: DULPythonEvent):
      """Arc on command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      
      for att in event.GetAttributes():
         attName = att.GetName()
         if attName == 'ProgNumber':
            self.CurrentProgNumber = att.GetValue()
         elif attName == 'WeaveOnOff':
            self.CurrentWeaveOnOff = att.GetValue()
         elif attName == 'WeaveOnCmd':
            self.WeaveOnCmd = att.GetValue()
         elif attName == 'WeaveFrequenz':
            self.CurrentWeaveFreuquenz = att.GetValue()
         elif attName == 'WeaveWidth':
            self.CurrentWeaveWidth = att.GetValue()
         elif attName == 'WeaveTime1':
            self.CurrentWeaveTime1  = att.GetValue()
         elif attName == 'WeaveTime2':
            self.CurrentWeaveTime2 = att.GetValue()
         elif attName == 'WeaveMethod':
            self.WeaveMethod = att.GetValue()
         elif attName == 'UseAngle':
            self.UseAngle = att.GetValue()
         elif attName == 'Angle':
            self.Angle = att.GetValue()        
         elif attName == 'WeavingDirection':
            self.WeavingDirection = att.GetValue()
         elif attName == 'CorrectionUpDown':
            self.CorrectionUpDown = att.GetValue()
         elif attName == 'CorrectionRightLeft':
            self.CorrectionRightLeft = att.GetValue()
         elif attName == 'UseConditionFile':
            self.UseConditionFile = att.GetValue()
         elif attName == 'ConditionFileNumber':
            self.ConditionFileNumber = att.GetValue()

      if self.ArcWeldingActive == True:
         # Welding is active - an ARCSET is called
         ArcCmd = "ARCSET"
      else:
         # Welding is not active - an ARCON is called
         ArcCmd = "ARCON"
         self.ArcWeldingActive = True
      
      if (self.PowerSource == "Yaskawa"):
         self.Source.append('%s ASF#(%d)' % (ArcCmd, self.CurrentProgNumber))

      elif (self.PowerSource == "Fronius"):

         if (self.ArcWeldingTorchType == "MIG/MAG"): 
            self.Source.append('MACRO1 MJ#(0) ARGF%d' % (self.CurrentProgNumber))
            self.Source.append('%s' % (ArcCmd))

         elif (self.ArcWeldingTorchType == "TIG"): 
            self.Source.append('MACRO1 MJ#(1) ARGF%d ARGF0' % (self.CurrentProgNumber))
            self.Source.append('%s WELD2' % (ArcCmd))
         
      else:
         self.Source.append('!!!! UNKNOWN POWER SOURCE !!!!')

      # Check weaving activity         
      # if self.CurrentWeaveOnOff == True:
      #    self.Source.append('WVON WEV#(%i)' % (self.WeaveOnCmd))


      if self.WeaveMethod == WEAVE_METHODS[0]:
         # No weaving - nothing to do
         pass
      else:

         if self.WeaveMethod == WEAVE_METHODS[1]:
            WeaveCommand = 'WVON WEV#(%i)' % (self.WeaveOnCmd)
            # self.Source.append('WVON WEV#(%i)' % (self.WeaveOnCmd))

         if self.WeaveMethod == WEAVE_METHODS[2] or self.WeaveMethod == WEAVE_METHODS[3]:
            oWEV = ' WEV#(%s)' % (self.WeaveOnCmd)
            oAMP = ' AMP=%s' % (self.CurrentWeaveWidth)
            oFreq = ' FREQ=%s' % (self.CurrentWeaveFreuquenz)
            
            oUPDown = ' U/D=%s' % int(self.CorrectionUpDown)
            oRightLeft = ' L/R=%s' % (self.CorrectionRightLeft)            

            if self.UseAngle == True:
               oAngle = ' ANGL=%s' % (self.ConditionFileNumber)
            else: oAngle = ""

            if self.WeavingDirection != WEAVING_DIRECTIONS[0]:
               oDir = ' Dir=%s' % (self.WeavingDirection)
            else: oDir = ""

            if self.UseConditionFile == True:
               oCondFile = ' CAF#(%s)' % (self.ConditionFileNumber)
            else: oCondFile = ""

            if self.IsWeavingActive == False:
               oCmd = "COMARCON"
            else:
               oCmd = "COMARCSET"
               
            try:
               if self.WeaveMethod == WEAVE_METHODS[2]:
                  WeaveCommand = "%s%s%s%s%s%s" % (oCmd, oWEV, oDir, oUPDown, oRightLeft, oCondFile)

               elif self.WeaveMethod == WEAVE_METHODS[3]:
                  WeaveCommand = "%s%s%s%s%s%s%s%s" % (oCmd, oAMP, oFreq, oAngle, oDir, oUPDown, oRightLeft, oCondFile)
       
            except:
               WeaveCommand = ""

         self.Source.append('%s' % (WeaveCommand))
         self.IsWeavingActive = True


   def OutputArcOffEvent(self, event: DULPythonEvent):
      """Arc off command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      #if self.ArcWeldingActive == True:
      for att in event.GetAttributes():
         if att.GetName() == 'ProgNumber':
            self.CurrentProgNumber = att.GetValue()

      self.ArcWeldingActive = False
      
      if self.CraterFill:
         self.Source.append('TIMER T=%.7f' % (self.CraterFillDelay))
      
      if (self.PowerSource == "Yaskawa"):
         self.Source.append('ARCOF AEF#(%d)' % (self.CurrentProgNumber))

      elif (self.PowerSource == "Fronius"):

         if (self.ArcWeldingTorchType == "MIG/MAG"): 
            self.Source.append('ARCOF')

         elif (self.ArcWeldingTorchType == "TIG"): 
            self.Source.append('ARCOF WELD2')
         
      else:
         self.Source.append('!!!! UNKNOWN POWER SOURCE !!!!')
        
      if self.IsWeavingActive == True:
         if self.WeaveMethod == WEAVE_METHODS[1]:
            WeaveCommand = 'WVOF'
         elif self.WeaveMethod == WEAVE_METHODS[2] or self.WeaveMethod == WEAVE_METHODS[3]:
            WeaveCommand = 'COMARCOF'

         self.Source.append('%s' % (WeaveCommand))
         self.IsWeavingActive = False


#################### HELPER ####################

   def AppendOnNonExistence(self, lineToAppend, list):
      """_summary_

      Args:
         lineToAppend (_type_): _description_
         list (_type_): _description_

      Returns:
         _type_: _description_
      """
      iCounter=1
      for line in list:
         if line == lineToAppend:
            return iCounter
         iCounter +=1
      list.append(lineToAppend)
      return 0

   def SetConnectionID(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """_summary_

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      for att in event.GetAttributes():
         if att.GetName() == 'TouchId':
               self.CurrentTouchID = int(att.GetValue())
      self.CorrectionActive = True
      self.Source.append('SFTON P%05i' % (self.CurrentTouchID))

   def GlobalGetAttributes(self, operator: DULPythonDownloadOperator, element):
      """_summary_

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         element (_type_): _description_
      """

      
      for att in element.GetAttributes():
         attName = att.GetName()
         if attName == 'ArcWeldingPSManufacturer':
            self.PowerSource = att.GetValue()
         elif attName == 'ArcWeldingArcOffCraterFill':
            self.CraterFill = att.GetValue()
         elif attName == 'ArcWeldingArcOffCraterFillDelay':
            self.CraterFillDelay = att.GetValue()
         elif attName == 'ArcWeldingTorchType':
            self.ArcWeldingTorchType = att.GetValue()
         elif (attName == "SensingSpeed"):
            self.TouchsenseSensingSpeed = att.GetValue()
         elif (attName == "SeamSearchSensingSpeed"):
            self.SeamSearchSensingSpeed = att.GetValue()            
         elif (attName == "OvertravelLength"):
            self.TouchsenseOvertravelLength = att.GetValue()*1000
         elif (attName == "SeamSearchOvertravelLength"):
            self.SeamSearchOvertravelLength = att.GetValue()*1000
         elif (attName == "ArcWeldingSensingPort"):
            self.SensingPort = att.GetValue()            

      if self.currentOperationWorkMethod == 'TouchSensingWorkMethod':
         self.CurrentSensingSpeed = self.TouchsenseSensingSpeed
         self.CurrentOvertravelLength = self.TouchsenseOvertravelLength
        
      elif self.currentOperationWorkMethod == 'SeamSearchWorkMethod':
         self.CurrentSensingSpeed = self.SeamSearchSensingSpeed
         self.CurrentOvertravelLength = self.SeamSearchOvertravelLength
