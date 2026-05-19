"""
COPYRIGHT Cenit AG Q2/2024
   Production ready PANASONIC downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off            YES
      touch sensing in base frame direction:       NO
      touch sensing in surface direction:          NO
      touch sensing with wire:                     NO
      wire check for touch with wire:              NO
      touch sensing with nozzle:                   NO
      seam search in surface direction:            NO (should work equal to touch sensing, but not evaluated)
      seam finding:                                NO
      seam tracking:                               NO
      robot team/synchronized multi robot motions: YES (controlled by Mechanism selection including Slave Robot 'A', Slave program downloaded auto)
      Multi Panasonic Mechanisms:                  YES
      Multi Panasonic Welding Condition Sets:      YES
      Panasonic AJ Output  :                       YES (default , Output Style can be influenced by E2 Robot Attribute 'CENOlpTargetOutputType')
      Panasonic AU Output  :                       YES
      

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities

"""

import sys, inspect, os, importlib
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
sys.argv  = ['']
sys.dont_write_bytecode = True

from datetime import datetime
from math import *
from cenpylib import FileUtility
from cenpydownload import Downloader
from cenpydownload import *
from cenpyolpcore.stubs import *
from cenpydownload.stubs import *
from cenpydownload.stubs.DULPythonDownloadOperator import *

def ensure_module_is_updated(module_name):
      if module_name in sys.modules:
         importlib.reload(sys.modules[module_name])
      else:
         importlib.import_module(module_name)

# import base class and define class name of the current download
ensure_module_is_updated('Panasonic') #  <---- Perform module force-reload in order to apply hot changes



#################### CONSTANTS ####################
# name of the download class
DOWNLOAD_CLASS_NAME = "Panasonic"
# Motion target
MOTION_TARGET_TYPE_CARTESIAN = 0
MOTION_TARGET_TYPE_JOINT = 1
# kinematic type
JOINT_TYPE_LINEAR = 0
JOINT_TYPE_ROTATION = 1
# kinematic 
DRIVEN_JOINT = 0
SYNCHRONOUS_JOINT = 1
# joint object array
JOINT_DATA_TYPE = 0
JOINT_VALUE = 1

# Item Types
UNSET = 0
PRODUCTION = 1
PERIPHERAL = 4
HUMAN = 8
MISCELLEANOS = 16

#Item SubTypes
Unset = 0 
MachineRobot = 1
RailGantry = 2
WorkpiecePositioner = 3
EndEffector = 4
Tool = 5
Fixture = 6
Jig = 7
DressUp = 8
ToolMagazine = 9
Human1 = 10
Protection = 11
BuildingPart = 12
Furniture = 13
Chassis = 14
FloorPlan = 15
SweptVolume = 16



class Panasonic(Downloader):
   '''Panasonic downloader
   Base robot vendor downloader
   Derived from: Base downloader

   # Baseframe output not supported yet

   # Section [Work]:
   # This Section is only needed when User Defined Attribute "CENOlpTargetOutputType" == WU or WV
   # Example: E2 BaseFrame is "B0" (RobRoot)
   # Position, 0, 0, 0, 0, 0, 0, 0 (Position, Index{1-7 -- 0 is default RobRoot}, X, Y, Z, Rx, Ry, Rz)

   # Section [Pose]:
   # Panasonic can export a binary ".rpg" file in 6 different types:
   # - Angle                    == AJ (Name, Type, RT, UA, FA, RW, BW, TW - in Deg)
   # - Position + Vector == AV (Name, Type, X, Y, Z, X1, X2, X3, Z1, Z2, Z3)
   # - Position + UVW   == AU (Name, Type, X, Y, Z, U, V, W)
   # - Pulse                    == AP (Name, Type, RT, UA, FA, RW, BW, TW - in Pulse Hexadecimal)
   # - Work + Vector     == WV (Name, Type, RT, UA, FA, RW, BW, TW, X, Y, Z, Xx, Xy, Xz, Zx, Zy, Zz, G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14, G15, G16, G17, G18, G19, G20, G21)
   # - Work + UVW       == WU (Name, Type, RT, UA, FA, RW, BW, TW, X, Y, Z, Rx, Ry, Rz, --, --, --, G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14, G15, G16, G17, G18, G19, G20, G21)

   # Default is "AJ" - for the other supported Pose output you have to set the User Defined Attribute "CENOlpTargetOutputType"   

   # Section [Command]:
   # MOVE COMMAND
   # „PTP"           == MOVEP, Position, Speed, Speed unit, Air-Weld, Smooth Level
   # „LINEAR"     == MOVEL, Position, Speed, Speed unit, CL No., Air-Weld, Smooth Level
   # „CIRCULAR" == MOVEC, Position, Speed, Speed unit, CL No., Air-Weld, Smooth Level

   # Speed unit:   PTP == %; LIN CIRC == m/min
   # Cl No.:       List{0,3,4} ? - not implemented - hard coded == 0
   # Air-Weld:     Air == N; Weld == W
   # Smooth Level: List{Default,0,1,2,...,10} Default == -1 - today hard coded == -1
   #  ;
   # Default values (hard coded) for "Cl No.", Air-Weld" and "Smooth Level" see ID: CENOLP_FMT_INIT

   # Base robot vendor downloader
   # Derived from: Base downloader
   '''
   # Motion target
   MOTION_TARGET_TYPE_CARTESIAN = 0
   MOTION_TARGET_TYPE_JOINT = 1
   # kinematic type
   JOINT_TYPE_LINEAR = 0
   JOINT_TYPE_ROTATION = 1
   # kinematic 
   DRIVEN_JOINT = 0
   SYNCHRONOUS_JOINT = 1
   # joint object array
   JOINT_DATA_TYPE = 0
   JOINT_VALUE = 1

   NEW_LINE_NUMBER_PREFIX = True
   NO_NEW_LINE_NUMBER_PREFIX = False

   FILE_EXTENSION = '.csr'

   def __init__(self) -> None:
      '''Class initialization
      '''
      super().__init__()
      self.DEBUG=False
      #
      self.FileUtil = FileUtility()
      # output file path
      self.OutputFilePath = ""
      # store the program name
      self.ProgramName = ""
      # array to store header content
      self.Header = []
      self.Header.append('[Description]')
      
      # array to store application command
      # e.g. arc welding equipment
      self.SourceHeader = []
      self.SourceHeader.append('')
      self.SourceHeader.append('[Command]')
      
      # array to store motion commands
      self.Source = []
            
      # array to store motion commands
      self.DataHeader = []
      self.DataHeader.append('')
      self.DataHeader.append('[Pose]')
      # array to store point coordinates and joints
      self.Data = []

      # array to store slave motion commands
      self.SlaveDataHeader = []
      self.SlaveDataHeader.append('')
      self.SlaveDataHeader.append('[Pose R2]')
      # array to store point coordinates and joints
      self.SlaveData = []

      # program footer text
      self.Footer = []      

      # skips the next source output
      self.SkipSourceMotion = False
      # skips the next data output
      self.SkipDataMotion = False

      # store the currently used base frame index
      # min = 0; max = 9
      self.CurrentBaseFrameIndex = -1
      self.BaseFrameMinIndex = 0
      self.BaseFrameMaxIndex = 9
      # store the currently used tool frame index
      # min = 0; max = 10
      self.CurrentToolFrameIndex = -1
      self.ToolFrameMinIndex = 0
      self.ToolFrameMaxIndex = 10
      self.LastToolFrameIndex = -9999999
      
      # store the currently used feedrate; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpFeedrate = 50
      # store the currently used feedrate; expected unit = [mm/sec]
      self.CurrentLinFeedrate = .1
      # store the currently used accuracy; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpAccuracy = 0
      # storage for comparison of previous Lin Accuracy 
      self.LastPtpAccuracy =-1
      # store the currently used accuracy; expected unit = [%]
      # min = 0; max = 100
      self.CurrentLinAccuracy = 0
      # storage for comparison of previous Lin Accuracy 
      self.LastLinAccuracy =-1
      # store current status for Accuracy
      self.CurrentAccuracyActive=False
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 150
      self.CurrentPtpAcceleration = 100
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 150
      self.CurrentLinAcceleration = 100
      # Panasonic Smooth levels (PL=0,PL=1,PL=2...PL=8)
      self.PanasonicAccuracyMapping = [0,13,25,38,50,63,75,88,100]
      # point counter
      self.PointCounter = int(0)
      # line counter for motion instruction
      self.SourceLineCounter = 0

      # string for program header to define used motion groups
      self.UsedGroups = ""

      # Robot Name
      self.RobotName = ''

      # PanasonicOutputStyles 
      self.SupportedPanasonicOutputStyles = ['AJ','AU']
      # Panasonic Putout Style 
      self.PanasonicOutputStyle = 'AJ'

      # Panasonic Mechanism
      self.Mechanism = ''
      self.GetMechanismAxes =[]

      # Panasonic Process Command,can be overwritten by ArcWeldingExtension ('W')
      self.PanasonicProcessCommand = 'N'
      self.ArcOffEventAfterCurrentMotion = False
      self.ArcOnEventAfterCurrentMotion = False

      self.IsSlaveProgram = False
      self.IsMasterProgram = False
      # Panasonic SlaveProgram for common program generation with Team Controller
      self.SlaveProgram = ''
      # Panasonic SlaveRobotName
      self.SlaveRobotName = ''
      # ArcWelding 
      self.IsTouchPointCollision = False
      self.IsTouchPointStartApp = False
      self.IsTouchPointRetApp = False
      self.CurrentTSCounter = 0
      self.CurrentTSCount = -1
      self.CurrentTouchID = -1
      self.PreviousTouchID = -1
      self.ArcWeldingActive = False
      self.CorrectionActive = False
      self.CurrentSensingPort = 0
      self.CraterFill = False
      self.CraterFillDelay = 0
      # arcWelding Parameters
      self.CurrentArcSetAmp = 0
      self.CurrentArcSetVolt = 0
      self.CurrentArcSetSpeed = 0
      self.CurrentCraterAmp = 0
      self.CurrentCraterVolt = 0
      self.CurrentCraterTime = 0

      self.UseHarmonic = 0
      self.IsFirstMotion = True

      # Initialize at download begin
   
   def GetPanasonicMechanismHex(self, Mech):
      '''Panasonic Mechanism bit sum (integer)
         G4 -> 8, G5 -> 16,...., A (Slave Robot)
      '''
      strHex=''
      iMech = 0    
      # expected format STATION;MECHANISMNAME;EANUMBER,EANUMBER,EANUMBER,...
      # i.e. Robot1;Mechanism1;G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,A (DEFAULT)
      # i.e A;Mechanism1;G4,G5,G6          
      arrEAxes = Mech.split(',')
      for ax in arrEAxes[1:len(arrEAxes)]:
         if ax != '':
            if ax == 'A':
               #iMech += 2048
               iMech += 0
            elif ax =='B':
               iMech += 4096
            elif ax == 'C':
               iMech += 8192
            elif ax == 'SL':
               self.IsSlaveProgram = True
            else:
               iMech += int(pow(2,int(ax[1:])-1))
      return iMech      
         
   def GetPanasonicPositionLevelFromAccuracyValue(self, AccuracyValue):
      pl=0
      while (self.PanasonicAccuracyMapping[pl]<=AccuracyValue and pl<8):
         pl+=1
      return pl 
   
   def Initialize(self, Operator):     
      logger = Operator.GetLogOperator()
      controller=Operator.GetController()
      if self.DEBUG:
         for att in controller.GetAttributes():
            if str('Array') in type(att).__name__:
               self.Source.append('REM, #CA# ' + att.GetName()[0:12] + ', ' + str(att.GetValues())[0:12])
            else:
               self.Source.append('REM, #CA# ' +att.GetName()[0:12] + ', ' + str(att.GetValue())[0:12])
      program=controller.GetActiveProgram()
      resources=controller.GetResources()
      for resource in resources:
         resource.GetName()
         resource.GetItemType()
         if self.DEBUG:
            for att in resource.GetAttributes():
               if str('Array') in type(att).__name__:
                  self.Source.append('REM, #RA# ' + att.GetName()[0:12] + ', ' + str(att.GetValues())[0:12])
               else:
                  self.Source.append('REM, #RA# ' +att.GetName()[0:12] + ', ' + str(att.GetValue())[0:12])
      resource=resources[0]
      robotAttributes=resource.GetAttributes()
      # In case of Cooperate Robots Programming by Team Controller and Usage of 2nd Robot by Current Mechanism, start Download of involved robots programs
      x=0
      for att in robotAttributes:
         # Get Panasonic Output Style om robot attribute
         if att.GetName() == 'CENOlpTargetOutputType':
            self.PanasonicOutputStyle = str(att.GetValue())
      # Check if this is a supported Panasonic output style
      if not self.SupportedPanasonicOutputStyles.__contains__(self.PanasonicOutputStyle):
         # TBD: Throw Exception to cancel download with Error Message
        logger.LogError('### Unsupported Panasonic output style '+ self.PanasonicOutputStyle)       
     
   def ProgramStart(self, Operator, program):
      logger = Operator.GetLogOperator()
      logger.LogDebug("SimplePython ProgramStart called")
      for att in program.GetAttributes():
         if self.DEBUG:
            if str('Array') in type(att).__name__:
               self.Source.append('REM, #PA# ' + att.GetName()[0:12] + ', ' + str(att.GetValues())[0:12])
            else:
               self.Source.append('REM, ##PA# ' +att.GetName()[0:12] + ', ' + str(att.GetValue())[0:12])
         if att.GetName() == 'Mechanism':
            # expected format STATION;MECHANISMNAME;EANUMBER,EANUMBER,EANUMBER,...
            # i.e. 'Robot1;Mechanism1;G1,G2,G3,G4,G5,G6,G7,G8,G9,G10' (DEFAULT)
            # i.e  'A;Mechanism1;G4,G5,G6'  
            self.Mechanism = att.GetValue()
            self.MechanismHex = hex(self.GetPanasonicMechanismHex(self.Mechanism))
            self.GetMechanismAxes = self.Mechanism.split(':')[2].split(',')
         if att.GetName() == 'SlaveProgram':
            self.SlaveProgram = att.GetValue()
            if self.SlaveProgram != '':
               self.IsMasterProgram = True
         if att.GetName() == 'SlaveRobotName':
            self.SlaveRobotName = str(att.GetValue())
      # Prepare Headers for Position output (to be extended for new Output styles)
      if self.PanasonicOutputStyle == 'AU':
         # /Name, Type, X, Y, Z, U, V, W, G4, G5, G6 ....
         PanasonicDataHeaderString = '/Name, Type, X, Y, Z, U, V, W'
         for ax in self.GetMechanismAxes[1:len(self.GetMechanismAxes)]:
            PanasonicDataHeaderString += ', '+ ax
         self.Data.append(PanasonicDataHeaderString)
      elif self.PanasonicOutputStyle == 'AJ':
         PanasonicDataHeaderString = '/Name, Type, RT, UA, FA, RW, BW, TW'
         for ax in self.GetMechanismAxes[1:len(self.GetMechanismAxes)]:
            if ax != 'SL' and ax != 'A' and ax != 'B' and ax != 'C' :
               PanasonicDataHeaderString += ', '+ ax
         self.Data.append(PanasonicDataHeaderString)
      if self.Mechanism == '':
         self.Mechanism = 'Mechanism4;G4,G5,G6'
         self.MechanismHex = hex(self.GetPanasonicMechanismHex(self.Mechanism))
         self.GetMechanismAxes = self.Mechanism.split(':')[1].split(',')
      # Setting HARMONIUS option for Panasonic depending on current Mechanism (from Mechansims.csv)
      if self.Mechanism.__contains__(",A"):
         self.UseHarmonic = True      
      logger.LogDebug(program.GetName())

   def OperationStart(self,operator,operation):
      '''Operation start   
      Args:
         operator: download operator
         operation: access to the operation
      '''
      logger = operator.GetLogOperator()
      # Add operation name
      operationName = "REM Operation " + operation.GetName()
      if operationName != "":
         self.AddLineToSource(operationName)
         pass

   def HandleMotion(self, operator, motion):
      '''Evaluation of toolpath elements and events

      Args:
         operator: download operator
         motion: current motion
      '''
      # get log operator
      logger = operator.GetLogOperator()

      # handle events, inserted before. Do not handle events which to change toolpath element output
      eventsBefore = motion.GetEventsBefore()
      # iterate through events
      for event in eventsBefore:
         name = event.GetName()
         self.HandleEvent(operator, motion, event)
      
      # Check if motion has ARC OFF or ARC ON Event after (which influences Motion output)
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         if event.GetName() == 'ArcOffEvent':
            self.ArcOffEventAfterCurrentMotion = True
            #self.PanasonicProcessCommand = 'N'
         elif event.GetName() == 'ArcOnEvent':
            self.ArcOnEventAfterCurrentMotion = True
            #self.PanasonicProcessCommand = 'W'

      # handle source section of the motion
      self.HandleSourceSection(operator, motion)
      # handle data section of the motion
      self.HandleDataSection(operator, motion)

      # handle events, inserted after. Do not handle events which to change toolpath element output
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         self.HandleEvent(operator, motion, event)

   def HandleEvent(self, operator, currentMotion, event):
      '''Handle event
      
      Args:
         operator: download operator
         event: access to the event object
      '''
      if self.DEBUG:
         self.Source.append("REM, # EV: " + str(event. GetInsertPosition())[0:12] +  "," + event.GetName()[0:12])  
      # handle build in events like speed, accuracy
      self.HandleBuildInEvents(operator, event)
      # output Event
      self.OutputEvent(operator, event)
     # get motions of the event
      motions = event.GetMotions()
      # handle each motion of the event
      for motion in motions:
         self.HandleMotion(operator, motion)

   def SubprogramStart(self, operator: DULPythonDownloadOperator, subProgram : DULPythonSubprogram):
      """called when a sup program is called

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         subprogram (DULPythonSubprogram): sub program operator gives access to the complete sub program
      """
      # get sub program name
      subProgramName = subProgram.GetName()
      # add call in program
      self.AddLineToSource('CALL, %s.rpg' % subProgramName)

   def OutputEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Output event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes      """
      
      
      if event.GetName() == 'TouchPointStartAppEvent':
         self.IsTouchPointStartApp = True
         self.skipSourceMotion = True          
      if event.GetName() == 'TouchPointCollisionEvent':
         self.IsTouchPointCollision = True
         self.skipSourceMotion = True
         self.suppressBCECOutput = True
         self.AddLineToSource('OUT O1#(8:O1#008)=ON')         
         self.AddLineToSource('TCHSNS, 0.9')
      if event.GetName() == 'TouchPointStartRetEvent':
         self.IsTouchPointRetApp = True
         self.skipSourceMotion = True  
         self.AddLineToSource('SNSSFTLD, GD#(1:GD001)')
         self.AddLineToSource('OUT O1#(8:O1#008)=OFF')  
      if event.GetName() == 'ConnectTouchProcessPointEvent':
         #self.SetConnectionID(operator,event)
         self.CurrentTouchID = int(event.GetAttributes()[0].GetValue())
         #self.AddLineToSource('REM TOUCHID'+str(self.CurrentTouchID))
      if event.GetName() == 'ArcOnEvent':
         self.OutputArcOnEvent(event)
      if event.GetName() == 'ArcOffEvent':
         self.OutputArcOffEvent(event)
      attributes = event.GetAttributes()
      if self.DEBUG == True:
         for attribute in attributes:
            if str('Array') in type(attribute).__name__:
               self.Source.append('REM, #EA# ' + attribute.GetName()[0:12] + ', ' + str(attribute.GetValues())[0:12])
            else:
               self.Source.append('REM, #EA# ' +attribute.GetName()[0:12] + ', ' + str(attribute.GetValue())[0:12])
         pass

   def OutputArcOnEvent(self, event: DULPythonEvent):
      """Arc on command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      
      for att in event.GetAttributes():
         if att.GetName() == 'ProgNumber':
            self.CurrentProgNumber = att.GetValue()
         if att.GetName() == 'DL ArcSet Amp (A)':
            self.CurrentArcSetAmp = att.GetValue()
         if att.GetName() == 'DL ArcSet Volt (V)':
            self.CurrentArcSetVolt = att.GetValue()
         if att.GetName() == 'DL ArcSet Speed (m/min)':
            self.CurrentArcSetSpeed = att.GetValue()
         if att.GetName() == 'WeaveOnOff':
            self.CurrentWeaveOnOff = att.GetValue()
         if att.GetName() == 'WeaveFrequenz':
            self.CurrentWeaveFrequenz = att.GetValue()
         if att.GetName() == 'WeaveWidth':
            self.CurrentWeaveWidth = att.GetValue()
         if att.GetName() == 'WeaveTime1':
            self.CurrentWeaveTime1  = att.GetValue()
         if att.GetName() == 'WeaveTime2':
            self.CurrentWeaveTime2 = att.GetValue()
   
      self.ArcWeldingActive == True
      # Flexible values from Technology
      self.Source.append("ARC-SET, %d, %.2f, %.2f" % (self.CurrentArcSetAmp, self.CurrentArcSetVolt, self.CurrentArcSetSpeed))
      self.Source.append("ARC-ON, ArcStart1.rpg, 1")
      

   def OutputArcOffEvent(self, event: DULPythonEvent):
      """Arc off command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      for att in event.GetAttributes():
         if att.GetName() == 'ProgNumber':
            self.CurrentProgNumber = att.GetValue()
         if att.GetName() == 'DL Crater Amp (A)':
            self.CurrentCraterAmp = att.GetValue()
         if att.GetName() == 'DL Crater Volt (V)':
            self.CurrentCraterVolt = att.GetValue()
         if att.GetName() == 'DL Crater Time (s)':
            self.CurrentCraterTime = att.GetValue()

      self.ArcWeldingActive = False
      # Flexible values from Technology            
      self.Source.append("CRATER, %d, %.2f, %.2f" % (self.CurrentCraterAmp, self.CurrentCraterVolt, self.CurrentCraterTime))
      self.Source.append("ARC-OFF, ArcEnd1.rpg, 1")
      if self.CraterFill:
         self.Source.append('TIMER T=%.7f' % (self.CraterFillDelay))     
      

   def HandleBuildInEvents(self,operator, event):
      '''Handle build in events like speed, accuracy, ...

      Args:
         operator: download operator
         event: access to the event object
      '''
      # check if speed event
      if event.GetName() == 'Speed':
         self.setSpeed(event)
      # check if accuracy event 
      elif event.GetName() == 'Accuracy':
          self.SetAccuracy(operator, event)
      # # check if acceleration event
      # elif event.GetName() == 'Acceleration':
      #    self.SetAcceleration(operator, event)
      # # text event
      # elif event.GetName() == 'Text':
      #    self.OutputTextEvent(operator, event)
      # # dwell event
      # elif event.GetName() == 'Dwell':
      #    self.OutputDwellEvent(operator, event)
      # set signal event
      elif event.GetName() == 'LogicPort':
         self.setLogicPort(event)
      elif event.GetName() == 'SyncRobots':
         self.SetSyncRobotsEvent(event)
      # # wait for signal event
      # elif event.GetName() == 'WaitForSignalBool':
      #    self.OutputWaitForSignalBoolEvent(operator, event)
      pass

   def HandleSourceSection(self, operator, motion):
      '''
      '''
      # contains the string of one source line.
      sourcePosition = ''
      # check if motion pre processing necessary and if the normal/general motion output must be skipped
      isRef = motion.IsReferenceMotion()

      # check if the motion is a reference motion or if the motion was already processed
      if not isRef and not self.SkipSourceMotion:
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # create LIN source string
            sourcePosition = self.OutputSourceLin(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string
            sourcePosition = self.OutputSourceCirc(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

         # check if the motion is of type point to point
         else:
            # create PTP source string
            sourcePosition = self.OutputSourcePtp(operator, motion)
            # add string to source array
            self.AddLineToSource(sourcePosition)

         # reset skip source creation
         self.SkipSourceMotion = False
         # reset Look ahead Arc ON/Off
         self.ArcOnEventAfterCurrentMotion = False
         self.ArcOffEventAfterCurrentMotion = False

   def HandleDataSection(self, operator, motion, dataOutputOnly = False):
      '''
      '''
      # contains data section of multiple motion groups
      dataPositions = []
      # complete data section of one motion group
      dataPosition = []

      # check if motion pre processing necessary and if the normal/general motion output must be skipped
      isRef = motion.IsReferenceMotion()

      # check if the motion is a reference motion or if the motion was already processed
      if not isRef and not self.SkipDataMotion:
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # create LIN source string
            dataPosition = self.OutputDataLin(operator, motion, dataOutputOnly)
            for line in dataPosition:
               # add string to data array
               self.AddLineToData(line)

         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string
            dataPositions = self.OutputDataCirc(operator, motion, dataOutputOnly)
            for line in dataPositions:
               # add string to data array
               self.AddLineToData(line)

         # check if the motion is of type point to point
         else:
            # create PTP source string
            dataPosition = self.OutputDataPtp(operator, motion, dataOutputOnly)
            for line in dataPosition:
                  # add string to data array
                  self.AddLineToData(line)

         # reset skip data creation
         self.SkipDataMotion = False

   def OutputSourcePtp(self, operator, motion):
      '''Output point to point motion
      J P[1] 50% FINE ACC80;

      Args:
         operator: download operator
         motion: current motion
      '''
      retstr = ''
      # increment point counter
      self.PointCounter += int(1)
      # Panasonic MOVEP Instruction
      if self.ArcOnEventAfterCurrentMotion == True:
         self.PanasonicProcessCommand = 'W'
      if self.ArcOffEventAfterCurrentMotion == True:
         self.PanasonicProcessCommand = 'N'      
      retstr = 'MOVEP, P%03d, %.2f, m/min, %s, -1' % (self.PointCounter, self.CurrentLinFeedrate*60, self.PanasonicProcessCommand)
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program
      if self.IsMasterProgram:
         retstr += ', MOVEP'
      return(retstr)

   def OutputSourceLin(self, operator, motion):
      '''Output linear motion
      L P[1] 50% FINE ACC80;

      Args:
         operator: download operator
         motion: current motion
      '''
      retstr = ''
      # increment point counter
      self.PointCounter += 1
      # Set Accuracy
      if self.CurrentAccuracyActive:
         acc = '%s'  % self.GetPanasonicPositionLevelFromAccuracyValue(self.CurrentLinAccuracy)
         self.LastLinAccuracy=self.CurrentLinAccuracy
      else:
         acc = '-1 '
      # Panasonic MOVEL Instruction
      if self.ArcOnEventAfterCurrentMotion == True:
         self.PanasonicProcessCommand = 'W'
      if self.ArcOffEventAfterCurrentMotion == True:
         self.PanasonicProcessCommand = 'N'     
      if self.UseHarmonic == True:
         moveCommand = "MOVEL+"
      else:
         moveCommand = "MOVEL"
      retstr = moveCommand+' , P%03d, %.2f, m/min, 0, %s, %s' % (self.PointCounter, self.CurrentLinFeedrate*60, self.PanasonicProcessCommand, acc)
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program
      if self.IsMasterProgram:
         retstr += ', '+moveCommand+', 0'
      return(retstr)

   def OutputSourceCirc(self, operator, motion):
         '''Output linear motion
         L P[1] 50% FINE ACC80;

         Args:
            operator: download operator
            motion: current motion
         '''
         retstr = ''
         # Redefine Last Motion  to be first MOVC command (Yaskawa CIRC consists of 3 instead of 2 Instructions...)
         # Due to that, an extra LIN position was inserted before
         LastSourceArrayString=self.Source[len(self.Source)-1]
         if LastSourceArrayString.startswith('MOVEP'):
            # Speed also has to be changed (removed and replaced bi LIN feedrate) because output was VJ
            NewLine=LastSourceArrayString.replace('MOVEP','MOVEC')           
            self.Source[len(self.Source)-1] =NewLine
         if LastSourceArrayString.startswith('MOVEL'):
            NewLine=LastSourceArrayString.replace('MOVEL','MOVEC')
            self.Source[len(self.Source)-1] =NewLine
         # output Array
         CircAndVia=''
         # increment point counter
         self.PointCounter += 1
         # Set Accuracy
         if self.CurrentAccuracyActive:
            acc = '%s'  % self.GetPanasonicPositionLevelFromAccuracyValue(self.CurrentLinAccuracy)
            self.LastLinAccuracy=self.CurrentLinAccuracy
         else:
            acc = '-1'
         # Panasonic MOVEC Instruction (VIACIRC and CIRC)
         if self.ArcOnEventAfterCurrentMotion == True:
            self.PanasonicProcessCommand = 'W'
         if self.ArcOffEventAfterCurrentMotion == True:
            self.PanasonicProcessCommand = 'W'     
         if self.UseHarmonic == True:
            moveCommand = "MOVEC+"
         else:
            moveCommand = "MOVEC"
         CircAndVia = moveCommand+', P%03d, %.2f, m/min, 0, %s, %s' % (self.PointCounter, self.CurrentLinFeedrate*60, self.PanasonicProcessCommand, acc)
         # Case Master/Slave -> Read Pose Data from auto generated Slave Program
         if self.IsMasterProgram:
            CircAndVia += ', '+moveCommand+', 0'
         CircAndVia += '\n'
         self.PointCounter += 1    
         if self.ArcOnEventAfterCurrentMotion == True:
            self.PanasonicProcessCommand = 'W'
         if self.ArcOffEventAfterCurrentMotion == True:
            self.PanasonicProcessCommand = 'N'          
         CircAndVia += moveCommand+', P%03d, %.2f, m/min, 0, %s, %s' % (self.PointCounter, self.CurrentLinFeedrate*60, self.PanasonicProcessCommand, acc)
          # Case Master/Slave -> Read Pose Data from auto generated Slave Program
         if self.IsMasterProgram:
            CircAndVia += ', '+moveCommand+', 0'

         return(CircAndVia)

   def MasterSlaveModifications(self,data, pointCounter, logger):
      slaveFile = open(self.SlaveProgram+'.csr', 'r+')
      if slaveFile:
         for line in slaveFile.readlines():
            if line.startswith('/Name') and len(self.SlaveData)==0:
               headerarray = line.split(',')
               lenHeader = len(headerarray)                         
               tempHEADER = ',' + str(headerarray[lenHeader-1]) 
               tempHeaderString = line.strip(tempHEADER)
               self.SlaveData.append(tempHeaderString)
               # Modify Master Data Header
               masterheaderarray = self.Data[0].split(',')
               lenMasterHeader = len(masterheaderarray)
               # special for Technik in Form ?
               tempMAsterHeader = ',' + str(masterheaderarray[lenMasterHeader-1])               
               #self.Data[0].strip(tempMAsterHeader)
               #self.Data[0] += ''
            elif line.startswith('P%03d' % (pointCounter)):
               # Get rid of the external Axes in Slave and append Master
               # find 2nd last komma
               pointarr = line.split(',')
               lenAxes =len(pointarr)
               # special for Technik in Form ?
               
               #tempStr = line.strip(tempAE)               
               tempAE = ',' + str(pointarr[lenAxes-1]) 
               #tempStr = line.strip(tempAE)  
               tempStr = line.split(tempAE)[0]             
               self.SlaveData.append(tempStr)
               # extend Master Data
               data[len(data)-1].strip('\n')
               data[len(data)-1] += tempAE.strip('\n')
               slaveFile.close()#
               
               break
            else:
               logger.LogError('### Position not existing in Slave Program! ###')
      else:
         log.LogError('### Slave Program File %s not present!' % slaveFile)

   def OutputDataPtp(self,operator, motion, dataOutputOnly = False):
      '''Output point to point position in data section
      
      Args:
         operator: download operator
         motion: current motion object
         dataOutputOnly:   False: the point is also output in source section
                              and point counter is already increased
                           True:  the point is NOT output is source section
                              and point counter needs to be increased
         
      Return:
         returns the string of the data section for the point to point motion'''
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      logger = operator.GetLogOperator()
      if dataOutputOnly:
         # increment point counter
         self.PointCounter += int(1)

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      data = []
      # Panasonic Ptp points always generated as with joint output
      data.append(self.OutputPanasonicData(operator, motionGroups[0], motion.GetName(), self.PointCounter))
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program, Modify and write to Masterprogram
      if self.IsMasterProgram:
         self.MasterSlaveModifications(data,self.PointCounter, logger)         
      return data

   def OutputDataLin(self, operator, motion, dataOutputOnly = False):
      '''Output linear position in data section
      
      Args:
         operator: download operator
         motion: current motion object
         dataOutputOnly:   False: the point is also output in source section
                              and point counter is already increased
                           True:  the point is NOT output is source section
                              and point counter needs to be increased
         
      Return:
         returns the string of the data section for the point to point motion'''
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      logger = operator.GetLogOperator()
      if dataOutputOnly:
         # increment point counter
         self.PointCounter += int(1)
      
      # get position of motion
      position = motion.GetPosition()
      # get motion target type 
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      data = []
      # check if motion target type is of type cartesian or joint      
      # 
      data.append(self.OutputPanasonicData(operator, motionGroups[0], motion.GetName(), self.PointCounter))   
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program, Modify and write to Masterprogram
      if self.IsMasterProgram:
         self.MasterSlaveModifications(data,self.PointCounter,logger)       
      return data

   def OutputDataCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      '''Output linear position in data section
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
         
      Return:
         returns the string of the data section for the point to point motion'''
      # point counter is incremented in source section. If source output wasn't
      # called, the point counter needs to be incremented independently
      logger = operator.GetLogOperator()
      if dataOutputOnly:
         # increment point counter for via point and end point
         self.PointCounter += 2

      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroupsViaPoint = self.CreateMotionGroupStructure(operator, motion.GetViaPosition())
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      data = []      
      data.append(self.OutputPanasonicData(operator, motionGroupsViaPoint[0], motion.GetViaPosition().GetName(), self.PointCounter - 1 ))
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program, Modify and write to Masterprogram
      if self.IsMasterProgram:
         self.MasterSlaveModifications(data,self.PointCounter-1,logger)       
      # output position
      data.append(self.OutputPanasonicData(operator, motionGroups[0], motion.GetPosition().GetName(), self.PointCounter))
      # Case Master/Slave -> Read Pose Data from auto generated Slave Program, Modify and write to Masterprogram
      if self.IsMasterProgram:
         self.MasterSlaveModifications(data,self.PointCounter,logger)       
      return data  
      
   
   def GetRobotJoints(self,joints):
      robotjoints=[]
      for joint in joints:
         if int(joint.JointRole) == 0:
            robotjoints.append(joint)
      return robotjoints
   
   def GetRailJoints(self,joints):
      railjoints=[]
      for joint in joints:
         if int(joint.JointRole) == 1:
            railjoints.append(joint)
      return railjoints
   
   def GetWPPositionerJoints(self,joints):
      wppositionerjoints=[]
      for joint in joints:
         if int(joint.JointRole) == 2:
            wppositionerjoints.append(joint)
      return wppositionerjoints
  

   def OutputPanasonicData(self, operator : DULPythonDownloadOperator, motionGroup, pointName, pointCounter):
      #stringArray = []
      tempstr= ''
      log= operator.GetLogOperator()
      tempstr = 'P%03d, %s' % (pointCounter, self.PanasonicOutputStyle)
      if self.PanasonicOutputStyle == 'AJ':
         # Write all joints
         joints = motionGroup.GetAllJoints()
         # separate different joint types
         RobotJoints=self.GetRobotJoints(joints)
         RailJoints=self.GetRailJoints(joints)
         WPPositionerJoints=self.GetWPPositionerJoints(joints)

         for joint in RobotJoints:            
               tempstr += ', %.3f' % (joint.Value)
            

         for joint in RailJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  tempstr += ', %.3f' % (joint.Value)
            else:
                  log.LogInfo('Error: %s not matching Panasonic Mechanism Signature of %s' % (joint.JointName, self.Mechanism))
         
         for joint in WPPositionerJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  tempstr += ', %.3f' % (joint.Value)
            else:
                  log.LogInfo('Error: %s not matching Panasonic Mechanism Signature of %s' % (joint.JointName, self.Mechanism))
         
               
            #stringArray.append(tempstr) 
      elif self.PanasonicOutputStyle == 'AU':
         # Write cartesian value 
         tempstr += ', %.3f, %.3f, %.3f, %.3f, %.3f, %.3f' % (motionGroup.X, motionGroup.Y, motionGroup.Z, motionGroup.R, motionGroup.P, motionGroup.W) 
         # Write all external axis joints
         joints = motionGroup.GetAllSynchronousJoints()
         if len(joints):
            # group every three joint together to a list
            # from joints [1,2,3,4,5,6,7,8] --> [[1,2,3], [4,5,6], [7,8]]
            slicedJointList = [joints[i:i+3] for i in range(0, len(joints), 3)]
            for jointList in slicedJointList:            
               for lineCounter, joint in enumerate(jointList):
                  if joint.KinematicType == self.JOINT_TYPE_LINEAR:
                     jointMovementType = 'mm'
                  else: 
                     jointMovementType = 'deg'
                  if self.GetMechanismAxes.__contains__(joint.JointName):
                     tempstr += ', %.3f' % (joint.Value)
                  else:
                     log.LogInfo('Error: %s not matching Panasonic Mechanism Signature of %s' % (joint.JointName, self.Mechanism))
            #stringArray.append(tempstr)       
      return tempstr
         
   def CreateOutputFile(self, operator):
      '''Create output file
      
      Args:
         operator: download operator
      '''
      # get controller
      controller = operator.GetController()
      # get controller
      program = controller.GetActiveProgram()
      # get output directory
      outputDir = controller.GetOutputDirectory()
      # define output path
      self.OutputFilePath = outputDir + "\\" + program.GetName() + self.FILE_EXTENSION
      # Get RobotName 
      # Get Resource Attributes
      resources=controller.GetResources()
      for resource in resources:
         if resource.GetItemType() == 1 and resource.GetItemSubType() ==1:
            self.RobotName = resource.GetName()         
      # create Header
      self.CreateHeader(operator)

   def OperationStart(self, operator, operation):
      '''Operation start   
      Args:
         operator: download operator
         operation: access to the operation
      '''
      logger = operator.GetLogOperator()      
      # Add operation name
      operationName = "REM Operation " + operation.GetName()
      if operationName != "":
         #self.AddLineToSource(operationName)
         pass
      # only for debugging:
      if self.DEBUG:
         opatts=operation.GetAttributes()
         for att in opatts:
            self.AddLineToSource(att.GetName()+":"+str(att.GetValue()))     
         

   
   def CreateHeader(self, operator):
      '''Create program header.
      Separated function, because some information doesn't exist at the beginning

      Args:
         operator: download operator
      '''
      self.AddLineToHeader('Robot, %s' % (self.RobotName))
      if self.SlaveProgram != '':
          self.AddLineToHeader('Robot2, %s' % (self.SlaveRobotName))
      self.AddLineToHeader('Comment,')
      self.AddLineToHeader('SubComment1,') 
      self.AddLineToHeader('SubComment2,')
      n=self.Mechanism
      self.AddLineToHeader('Mechanism, %d(%s)' % (int(n.split('Mechanism')[1].split(':')[0]),str(self.MechanismHex)[2:]))
      self.AddLineToHeader('Creator, Cenit Fastsuite')
      self.AddLineToHeader('Welder, 1:TAWERS')
      self.AddLineToHeader('User coordinate, None')         
      created = datetime.today().strftime('%Y, %m, %d, %H, %M, %S')
      modified = datetime.today().strftime('%Y, %m, %d, %H, %M, %S')
      # prevent Date/Time Differences during Test Run
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      #self.AddLineToHeader('REM "GetWindowsEnvironmentVariable(CPOST_TESTLAUF_CENIT)=%s"' % (ktaTest))
      if ktaTest == "TRUE":
         created = "2024, 11, 14, 15, 38, 35"
         modified = "2024, 11, 14, 15, 38, 35"
      self.AddLineToHeader('Create, %s' % (created))
      self.AddLineToHeader('Update, %s' % (modified))
      self.AddLineToHeader('Original,')
      self.AddLineToHeader('Edit, 0')
   
   def CheckAndUpdateBaseFrame(self, logger, index):
      '''Checks if base frame index is within range and generate a output line
      '''
      if self.CurrentBaseFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.BaseFrameMinIndex, self.BaseFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentBaseFrameIndex = index
         else:
            logger.LogError('Base frame index out of range')
   
   def CheckAndUpdateToolFrame(self, logger, index):
      '''Checks if tool frame index is within range and generate a output line
      '''
      if self.CurrentToolFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.ToolFrameMinIndex, self.ToolFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentToolFrameIndex = index
         else:
            logger.LogError('Tool frame index out of range')

   def RangeCheck(self, value, min, max):
      '''Check if the value is in range

      Return:
         Returns True if the value is in range
         Returns False is the value is not in range
      '''
      try:
         # if frame index is smaller then minimum frame index value, return ERROR
         if value < min:
            return False
         # if frame index is higher then maximum frame index value, return ERROR
         elif max < value:
            return False
         # frame index is within range
         else:
            return True
      except: 
         pass
   
   def AddLineToHeader(self, newline):
      '''Add a line to the program header
      '''
      self.Header.append(newline)
   
   def AddLineToSource(self, newline):
      '''Add a new line to the source section and add optional the line number

      Args:
         newline: string to 
      '''
      # e.g add a technology command in a new line. No new line number necessary
      self.Source.append("%s"  % (newline))

   def AddLineToData(self, newline):
      '''Add a new line to the data section
      '''
      self.Data.append(newline)
   
   def WriteOutputFile(self, operator):
      '''Write output file
      
      Args:
         operator: download operator
      '''
      # create file and output the program
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Data)
      if self.SlaveProgram != '':
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SlaveDataHeader)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SlaveData)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)      
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Footer)
      operator.AddOutputFilePath(self.OutputFilePath)
      pass

   def CreateMotionGroupStructure(self, operator, positionObject):
      '''Create the motion group structure depending on axes mapping in layout builder

      Args:
         operator: download operator
         positionObject:

      Return:
         returns the motion groups for the position object
      '''
      # read configuration
      configuration = positionObject.GetConfig()
      # read turn value
      turn = positionObject.GetTurn()
      # read coordinates
      cartesian = positionObject.GetXYZ()
      # read orientation 
      orientation = positionObject.GetOrientation()
      # read motion target type
      motionTargetType = positionObject.GetTargetType()

      positionName = positionObject.GetName()
      # get all joints
      joints = positionObject.GetAllJointValues()
      motionGroups = []
      currentGroupIndex = -1
      for joint in joints:
         # get motion group index
         groupIndex = joint[self.JOINT_DATA_TYPE].GetJointGroupIndex()
         motionGroup = self.GetMotionGroupByIndex(motionGroups, groupIndex)
         # check if motion group exist
         if motionGroup is None:
            # create a new motion group
            motionGroup = self.MotionGroup(motionTargetType, groupIndex, configuration, turn, 0, 0, cartesian, orientation)
            motionGroups.append(motionGroup)

         # get the joint index
         jointIndex = joint[self.JOINT_DATA_TYPE].GetJointIndex()
         # get the kinematic type, linear or rotation
         jointKinematicType = joint[self.JOINT_DATA_TYPE].GetJointType()
         # check if driven joint (robot) or external joint (synchronous)
         isExternalJoint = joint[self.JOINT_DATA_TYPE].IsExternal()
         # to which type of resource belongs the joint
         jointRole = joint[self.JOINT_DATA_TYPE].GetJointRole()
         # joint name
         jointName = joint[self.JOINT_DATA_TYPE].GetName()
         if isExternalJoint:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.SYNCHRONOUS_JOINT, jointRole, joint[self.JOINT_VALUE], jointName)
         else:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.DRIVEN_JOINT, jointRole, joint[self.JOINT_VALUE], jointName)
      
      # return the motion groups
      return motionGroups

   def GetMotionGroupByIndex(self, motionGroups, index):
      '''Get the motion group by index
      
      Args:
         motionGroups: 
         index: Index of the searched motion group

      Return:
         if motion group exist, return the motion group
         if motion group doesn't exist, return None
         '''
      # iterate through motion groups
      for motionGroup in motionGroups:
         if motionGroup.MotionGroupIndex == index:
            return motionGroup
      return None
   
   # Set Current Feedrate from Speed Event 
   def setSpeed(self, event):
      pathtype = ''
      speed = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            speed=attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype=attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinFeedrate = speed
      else:
         self.CurrentPtpFeedrate = speed        

   def SetAccuracy(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      '''Set current accuracy from accuracy event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      '''
      # get log operator
      logger = operator.GetLogOperator()
      # variable initialization
      pathtype= ''
      accuracy = -1
      criteria = ''
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get accuracy value
         if attribute.GetName() == 'Value':
            accuracy = attribute.GetValue()
         # get path type
         if attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
         # get criteria On/Off/Distance/JointDistance/
         if attribute.GetName() == 'Criteria':
            criteria = attribute.GetValue()
      # check if criteria is On
      if criteria =='On':
         self.CurrentAccuracyActive = True
         if accuracy > 0.0:
            # distinguish between contour and point to point
            if pathtype == 'Contour':
               self.CurrentLinAccuracy = int(accuracy * 1000)
               if self.CurrentLinAccuracy > 100:
                  logger.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
                  self.CurrentLinAccuracy = 100
            else:
               self.CurrentPtpAccuracy = int(accuracy)
      # check if criteria is OFF
      elif criteria == 'Off':
         self.CurrentAccuracyActive = False
      # check if criteria is distance
      elif criteria == 'Distance':
         self.CurrentLinAccuracy = int(accuracy * 1000)
         if self.CurrentLinAccuracy > 100:
            logger.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
            self.CurrentLinAccuracy = 100
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      # check if criteria is joint distance
      elif criteria == 'JointDistance':
         self.CurrentPtpAccuracy = int(accuracy)
         if accuracy > 0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
   
   
   # Set Logic Port Event
   def setLogicPort(self, event):
      atts = event.GetAttributes()
      for att in atts:
         self.Source.append(att.GetName() + ',' + str(att.GetValue()))
   
   # Sync Robot Event Panasonic (Handshake)
   def SetSyncRobotsEvent(self,event):
      atts = event.GetAttributes()
      bHandshake=False
      for att in atts:
         if att.GetName() == 'SyncMode':
            bHandshake=True
         if att.GetName() == 'SyncText':
           if bHandshake == True:
              self.Source.append('SEMNUM, 1, ' +str(att.GetValue()))
              bHandshake=False
   
   class MotionGroup():
      '''Class that emulates the Fanuc Data section and thus simplifies output/customizing.
      A motion group contains one or more joints.
      '''

      # Motion target
      MOTION_TARGET_TYPE_CARTESIAN = 0
      MOTION_TARGET_TYPE_JOINT = 1
      # kinematic type
      JOINT_TYPE_LINEAR = 0
      JOINT_TYPE_ROTATION = 1
      # kinematic 
      DRIVEN_JOINT = 0
      SYNCHRONOUS_JOINT = 1
      # joint object array
      JOINT_DATA_TYPE = 0
      JOINT_VALUE = 1

      def __init__(self, motionTargetType, motionGroupIndex, configuration="", turn="", toolIndex=0, baseIndex=0, cartesian = [0.0, 0.0, 0.0], orientation = [0.0, 0.0, 0.0]):
         '''Class initialization
         '''
         # if configuration and turn are empty,
         # motion group doesn't contain a robot and
         # configuration and turn must not be outputted.
         self.MotionGroupIndex = int(motionGroupIndex)
         # motion target type
         self.MotionTargetType = motionTargetType
         # point configuration
         self.Configuration = str(configuration)
         # turn
         self.Turn = str(turn)
         # tool frame index
         self.ToolIndex = int(toolIndex)
         # base frame index
         self.BaseIndex =int(baseIndex)
         # coordinates
         self.X = cartesian[0] * 1000 # X
         self.Y = cartesian[1] * 1000 # Y
         self.Z = cartesian[2] * 1000 # Z
         # orientation
         self.W = orientation[0] # W (Rx)
         self.P = orientation[1] # P (Ry)
         self.R = orientation[2] # R (Rz)
         # list with joints
         self.Joints = []

      def AddJointToMotionGroup(self, index, kinematicType, resourceJointType, jointRole, value, name):
         '''Add a joint to the motion group

         Args:
            index: joint index from port mapping in layout builder
            kinematicType: linear or rotation
            resourceJointType: driven or synchronous joint
            jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
            value: joint value

         Return:
            return the new created joint object
         '''
         joint = self.Joint(index, kinematicType, resourceJointType, jointRole, value,name)
         self.Joints.append(joint)
         return joint
      
      def GetAllJoints(self):
         '''get all joints of the motion group

         Return:
            Returns a list of all joint of the motion group
         '''
         return self.Joints
      
      def GetAllSynchronousJoints(self):
         '''Get all synchronous joints from motion group

         Return:
            Returns a list of all synchronous joints of the motion group
         '''
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == self.SYNCHRONOUS_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def GetAllDrivenJoints(self):
         '''Get all synchronous joints from motion group

         Return:
            Returns a list of all synchronous joints of the motion group
         '''
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == self.DRIVEN_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def HasDrivenJoints(self):
         '''Check if a robot/machine is part of the motion group

         Return:
            returns True if the motion group has driven joints
            returns False if the motion groups has no driven joints
         '''
         # get all driven joints
         drivenJoints = self.GetAllDrivenJoints()
         # check the length of the list
         if len(drivenJoints) > 0:
            # motion group has driven joints (robot)
            return True
         else:
            # motion group has NO driven joints (robot)
            return False
         
      
      class Joint():
         '''Joint class to store important joint information in a separated object
         '''
         # kinematic type
         JOINT_TYPE_LINEAR = 0
         JOINT_TYPE_ROTATION = 1

         def __init__(self, index, kinematicType, resourceJointType, jointRole, value, name):
            '''Class initialization

            Args:
               index: joint index from port mapping in layout builder
               kinematicType: linear or rotation
               resourceJointType: driven or synchronous joint
               jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
               value: joint value
            '''
            self.Index = index
            # movement type is linear or rotation
            self.KinematicType = kinematicType
            # resource joint type can be driven or synchronous
            self.ResourceJointType = resourceJointType
            # to which type of resource does the joint belong (robot, workpiece positioner, rail, ...)
            self.JointRole = jointRole
            # check if joint is of type rotation
            if int(kinematicType) == self.JOINT_TYPE_ROTATION:
               self.Value = value
            else:
               # if linear joint, multiply by 1000 to get mm
               self.Value = value * 1000
            # joint name
            self.JointName = name