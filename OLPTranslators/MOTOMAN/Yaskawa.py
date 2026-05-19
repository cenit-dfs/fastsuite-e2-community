import importlib
import sys, os
sys.argv  = ['']
sys.dont_write_bytecode = True

from cenpylib import *

#from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *

from tkinter import *
#import re
from datetime import datetime


#################### CONSTANTS ####################
# name of the download class
DOWNLOAD_CLASS_NAME = "Yaskawa"
from cenpydownload import Downloader

class Yaskawa(Downloader):
   """Yaskawa downloader
   Base robot vendor downloader
   Derived from: Base downloader
   """
   
   FILE_EXTENSION = ".JBI"

   POS_TYPE_PULSE = 'PULSE'
   POS_TYPE_RECTAN = 'Relative'

   DRIVEN_JOINT = 0
   SYNCHRONOUS_JOINT = 1
   # kinematic 
   DRIVEN_JOINT = 0
   SYNCHRONOUS_JOINT = 1

   # joint roles
   MAIN = 0
   RAIL = 1
   WORKPIECE_POSITIONER = 2
   END_EFFECTOR = 3
   PERIPHERAL = 4
   SYNCHRONOUS_ON_ROBOT = 5

#################### BASE FUNCTIONS ####################

   def __init__(self) -> None:
      super().__init__()
      self.DEBUG = False
      self.OnDev=False
      self.OutputFilePath = ""
      self.FileUtil = FileUtility()
      self._correctedProgramName = ""
      self._groups=[['']]
      # Default group names Group 0 not used by Yaskawa, so ti begins with number 1 (i.e. RB1)
      self.bReplaceBasicGroupNamesInOutput=False
      self.OutputSubGroupNames=['RB1','ST1','']
      self.JointArray=[]
      
      self._jointPulses=[]
      self._baseGroups=[]
      self._stationGroups=[]
      self._posCounter=0
      self.PosCounterC = 0
      self.PosCounterBC = 0
      self.PosCounterEC = 0
      self.PosCounterP = 0
      # Job Header   
      self.JobHeader=[]
      self.DataHeader=[]
      # Definitions
      # ROBOT Section
      self.DataC=[]
      self.DataCHeader = []
      # BASE Section
      self.DataBC=[]
      self.DataBCHeader = []
      # STATION Section
      self.DataEC=[]
      self.DataECHeader =[]
      # Source Header
      self.SourceHeader=[]
      # Source (Move Instructions)
      self.Source=[]
      # Job Footer
      self.JobFooter=[]
      # Skip Source Output Flag
      self.skipSourceMotion = False
      # Skip Data Output Flag
      self.skipDataMotion = False
      # Default Postype Relative/PULSE
      self.PosType='PULSE'
      # Current Baseframe
      self.CurrentBaseFrameIndex=''
      # Current Toolframe   
      self.CurrentToolFrameIndex=''
      # last Baseframe=''
      self.LastBaseframeIndex =''
      # last Toolframe
      self.LastToolframeIndex=''
      # store the currently used feedrate; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpFeedrate = 50
      # store the currently used feedrate; expected unit = [m/sec]
      self.CurrentLinFeedrate = 0.099
      # last LinFeedrate
      self.LastLinFeedrate = -1
      # lst PtpFeedrate
      self.LastPtpFeedrate = -1
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
      # min = 0; max = 105      
      self.CurrentPtpAcceleration = 100
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 105
      self.CurrentLinAcceleration = 100
      # store current state for Welding Active/Inactive
      self.ArcWeldingActive = False
      # Yaskawa Mapping Array (PL=0,PL=1,PL=2...PL=8)
      self.YaskawaAccuracyMapping = [0,13,25,38,50,63,75,88,100]
      # Pulse Values
      self.CENOlpPulseValues = ''
      # Pulse offsets
      self.CENOlpZeroValues = ''
      #
      self.CENOlpYaskawaGroupsMapping = []
      #
      self.CENOlpDataOutputStyle = ''
      self.RobotInformation = None   
      #
      self.LastConfig = ''
      self.LastTurn = ''   
      #
      self.lastMotionType = ''
      self.lastPositionObject = ''
      self.currentOperationWorkMethod = ''
      self.suppressBCECOutput = False
      self.Logging = None

   def DevLogging(self, info):
      if self.OnDev == True and self.Logging != None:
         self.Logging.LogInfo(info)

   def Initialize(self, operator: DULPythonDownloadOperator):
      """Translator initialization.
      Called only once per download, even when downloading sub programs

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      logger = operator.GetLogOperator()
      self.Logging = operator.GetLogOperator()
      controller = operator.GetController()
      program = controller.GetActiveProgram()
      # Yaskawa Program Name Check and Modification
      r = self.CheckYaskawaProgramName(program.GetName())
      if r > 0:
         mb = MessageBox()
         if r == 1:            
            self._correctedProgramName = str(program.GetName())[0:31]
            mb.Show("Yaskawa Translator Info","Program name not allowed, shortened to 32 characters! : " + self._correctedProgramName, 1,  0)
      else:
         self._correctedProgramName = program.GetName()
      # # Yaskawa analyze Joints and handle Group Information
      # self.CreateMotionGroupStructure(logger, controller)
      # self.CreateYaskawaGroupOutputInformation(logger)
      # Get Resource Attributes
      resources=controller.GetResources()
      for resource in resources:
         resource.GetName()
         resource.GetItemType()
      resource=resources[0]
      robotAttributes=resource.GetAttributes()
      for att in robotAttributes:
         aaa = att.GetName()
         # Yaskawa Pulse value set from robot attribute
         if att.GetName() == 'CENOlpJointStepFactorValues':
            self.CENOlpPulseValues = str(att.GetValue()).split(';')
         # Yaskawa Zero value set from robot attribute
         if att.GetName() == 'CENOlpJointZeroOffsetValues':
            self.CENOlpZeroValues = str(att.GetValue()).split(';')
         # Yaskawa group mapping (only for name of subgroup)
         if att.GetName() == 'CENOlpYaskawaGroupsMapping':
            self.CENOlpYaskawaGroupsMapping = str(att.GetValue()).split(';')
         # When CENOlpDataOutputStyle value is set in E2 it overwrites self.PosType
         if att.GetName() == 'CENOlpDataOutputStyle':
            if len(att.GetValue()) > 0:
               self.CENOlpDataOutputStyle = str(att.GetValue())
               if self.CENOlpDataOutputStyle == 'RECTAN':
                  self.PosType = 'Relative'
      # Create Source Header Information 
      if len(self.CENOlpYaskawaGroupsMapping) < 3:
         self.Logging.LogWarn('Robot Attribute "CENOlpYaskawaGroupsMapping" is not set correctly. Default "RB1:1:1;;" will be used.')
         self.CENOlpYaskawaGroupsMapping = ["RB1:1:1","",""]
      
      # Yaskawa analyze Joints and handle Group Information
      self.CreateMotionGroupStructure(logger, controller)
      self.CreateYaskawaGroupOutputInformation(logger)
      
      self.CreateSourceHeader(program, operator)

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
      """
      #/JOB
      #//NAME PRG001
      # Maximum 32 characters (letters or numbers)
      # Allowed Characters:-_!%&'()
      # Question: Do we check or even modify program names here? (or breack with message?)
      for att in program.GetAttributes():
         if self.DEBUG:
            self.Source.append('\' Program Attribute: ' + str(att. GetName())+  ',' + str(att.GetValue())) 
      if len(self.CENOlpPulseValues) < 1:
         self.Logging.LogWarn('Robot Attribute "CENOlpJointStepFactorValues" is not set. Default "1;1;1;1;..." will be used.')
         self.CENOlpPulseValues = [1,1,1,1,1,1,1,1,1,1,1,1]
      if len(self.CENOlpZeroValues) < 1:
         self.Logging.LogWarn('Robot Attribute "CENOlpJointZeroOffsetValues" is not set. Default "0;0;0;0;..." will be used.')
         self.CENOlpZeroValues = [0,0,0,0,0,0,0,0,0,0,0,0]
      

      self.GetFirstToolFrame(program)

   def OperationGroupStart(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      """Operation start

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operationGroup (DULPythonOperationGroup): operation group operator gives access to the current operation group
      """
      for att in operationGroup.GetAttributes():
         if self.DEBUG:
            self.Source.append('\' OperationGroup Attribute: ' + str(att. GetName())+  ',' + str(att.GetValue())) 

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Operation start

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator gives access to the current operation
      """
      self.CurrentBaseFrameIndex=operation.GetUsedBaseProfile().GetIndex()

      if operation.GetUsedToolProfile().IsVisionFrame() == False:
         self.CurrentToolFrameIndex=operation.GetUsedToolProfile().GetIndex()

      for att in operation.GetAttributes():
         if self.DEBUG:
            self.Source.append('\' Operation Attribute: ' + str(att. GetName())+  ',' + str(att.GetValue())) 
         if att.GetName() == 'ArcWeldingOperationWorkMethodName':
            self.currentOperationWorkMethod = att.GetValue()

   def HandleMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Evaluation of toolpath elements and events

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
      """
      eventsBefore = motion.GetEventsBefore()
      for event in eventsBefore:
         self.HandleEvent(operator, event)   
      # Yaskawa special handling fro CIRC in LIN combination
      if motion.IsCircularMotion():    
         # In case, last Motion was LIN, an additional LIN Position will be inserted before this CIRC
         # this one has to be a position with own definition
         if self.lastMotionType == 'LIN' or self.lastMotionType == 'PTP':
            additionalLinStartPointName='C{num:0{width}}'.format(num=self.PosCounterC,width=5)
            self.PosCounterC += 1
            self.PosCounterBC += 1
            self.PosCounterEC += 1
         vianame='C{num:0{width}}'.format(num=self.PosCounterC,width=5)
         self.PosCounterC += 1
         self.PosCounterBC += 1
         self.PosCounterEC += 1
      
      posname= 'C{num:0{width}}'.format(num=self.PosCounterC,width=5)
      self.PosCounterC += 1
      self.PosCounterBC += 1
      self.PosCounterEC += 1
                  
      positionObject = motion.GetPosition()
      isRef = motion.IsReferenceMotion()
      if motion.IsLinearMotion():
         #elf.OutputYaskawaMotion(posname, positionObject,motion)
         sourcePosition = self.OutputYaskawaLin(operator, posname, positionObject)
         if self.skipSourceMotion == False:
            self.Source.append(sourcePosition)
         self.lastMotionType = 'LIN'
         # This positionObject is saved because it may be used for Follow up CIRC
         self.lastPositionObject = positionObject
      elif motion.IsCircularMotion():
         # In case, last Motion was LIN, an additional LIN Position will be inserted before this CIRC
         # this one has to be a position with own definition
         if self.lastMotionType == 'LIN':
               sourcePosition = self.OutputYaskawaLin(operator, additionalLinStartPointName, self.lastPositionObject)
               if self.skipSourceMotion == False:
                  self.Source.append(sourcePosition)
         if self.lastMotionType == 'PTP':
               sourcePosition = self.OutputYaskawaPtp(operator, additionalLinStartPointName, self.lastPositionObject)
               if self.skipSourceMotion == False:  
                  self.Source.append(sourcePosition)
         sourcePosition = self.OutputYaskawaCirc(operator, vianame, posname, motion.GetViaPosition(), positionObject)
         if self.skipSourceMotion == False:
            self.Source.append(sourcePosition)
         self.lastMotionType = 'CIRC'
      else:
         sourcePosition = self.OutputYaskawaPtp(operator, posname, positionObject)
         if self.skipSourceMotion == False:
            self.Source.append(sourcePosition)
         self.lastMotionType = 'PTP'
         # This positionObject is saved because it may be used for Follow up CIRC
         self.lastPositionObject = positionObject 
      # Reset Skipping Source
      self.skipSourceMotion = False           

      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         self.HandleEvent(operator, event)

   def ProgramEnd(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called at the end of each the program 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      self.JobFooter.append('END')

   def CloseOutputFile(self, operator: DULPythonDownloadOperator):
      """Close the output file if still opened

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      operator.AddOutputFilePath(self.OutputFilePath)

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Create output file
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # get controller
      controller = operator.GetController()
      # get active program
      program = controller.GetActiveProgram()
      # get output directory
      outputDir = controller.GetOutputDirectory()
      self.OutputFilePath = outputDir + "\\" + self._correctedProgramName +  self.FILE_EXTENSION
      self.CreateJobHeader(program)

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Write output file
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      # create file and output the program
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.JobHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataC)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataBC)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataEC)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.JobFooter)


#################### PROGRAM SECTION ####################

   def CreateMotionGroupStructure(self, logger: OlpCorePythonLogOperator, controller: DULPythonController):
      """Create motion group structure

      Args:
         logger (DULPythonLogOperator): log operator for user feedback
         controller (DULPythonController): controller object gives access to all controller information

      Returns:
         bool: _description_
      """
      connectedJoints = controller.GetConnectedJoints()
      currentGroupIndex = -1
      self.RobotInformation = self.RobotSystemInformation()
      for connectedJoint in connectedJoints:
         groupIndex = connectedJoint.GetJointGroupIndex()
         if groupIndex != currentGroupIndex:
            motionGroup = self.RobotInformation.AddMotionGroupToSystem(groupIndex)
            currentGroupIndex = groupIndex
         if motionGroup == None:
            logger.LogError("No motion group available")
            return False
         jointIndex = connectedJoint.GetJointIndex()
         jointKinematicType = connectedJoint.GetJointType()
         isExternalJoint = connectedJoint.IsExternal()
         jointRole = connectedJoint.GetJointRole().value
         value = 5 # TODO
         if isExternalJoint:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.SYNCHRONOUS_JOINT, jointRole, value)
         else:
            motionGroup.AddJointToMotionGroup(jointIndex, jointKinematicType, self.DRIVEN_JOINT, jointRole, value)
      return True
   
   def ConvertGroupNamesToType(self, name):
      '''extract the Group Names to a Type'''
      if name == 'RB':
          self.RobotInformation.containsRobot=True
          return 'R'
      if name == 'BS':
         self.RobotInformation.containsBase=True
         return 'BC'
      if name == 'ST':
         self.RobotInformation.containsStation=True
         return 'EC'
      if name == 'AA':
         return 'BB'
      return 'XX'
   
   def CheckForGroupsFromAttributesAndJoints(self, tempArray):
      '''Check Resource Group between Attribute and Joints 
      ['GROUP1', ['R','BC']]  <-->  ['GROUP1', ['R']]
      '''
      inChkName = tempArray[0]
      inGrpArray = tempArray[1]
      for curRes in inGrpArray:
         for gottenGrp in self.RobotInformation.YaskawaOutputStyle:
            for res in gottenGrp[1]:
               if curRes == res:
                  return True
      return False
   
   def CreateYaskawaGroupOutputInformation(self, logger: OlpCorePythonLogOperator):
      """Analyse MotionGroupInformation to identify Yaskawa Output Style

      Args:
         logger (OlpCorePythonLogOperator): log operator for user feedback
      """
      currentJointRole = ''
      constGroupHeaderName = 'GROUP'
      anyGroupNumber = 0
      currentGroupNumber = 0
      tempArray = []
      chkArray = []
      intermArray = []
      bYaskawaGroupsMapping = True
      #self.CENOlpYaskawaGroupsMapping.append("AA1:2:1")
      if len(self.CENOlpYaskawaGroupsMapping) and bYaskawaGroupsMapping:
         # RB1:1:1   BS1:1:1   ST1:2:2
         for grp in self.CENOlpYaskawaGroupsMapping:
            grpList = str(grp).split(':')
            if len(grpList) == 0:
               continue
            if len(grpList) > 1:
               group = int(grpList[1])
               if not group in chkArray:
                  chkArray.append(group)
                  intermArray = []
                  tempArray = []
                  for grp in self.CENOlpYaskawaGroupsMapping:
                     grpList = str(grp).split(':')
                     if len(grpList) == 0:
                        continue
                     if len(grpList) > 1:
                        tmpgroup = int(grpList[1])
                        if tmpgroup == group:
                           name = str(grpList[0][0:2])
                           intermArray.append(self.ConvertGroupNamesToType(name))
                  itemName = constGroupHeaderName+str(group)  # 'GROUP1'
                  anyGroupNumber += 1
                  tempArray.append(itemName)  # 'GROUP1'
                  tempArray.append(intermArray) # ['R', 'BC']
                  self.RobotInformation.YaskawaOutputStyle.append(tempArray)
      
      tempArray = []
      for group in self.RobotInformation.MotionGroups:
         currentGroupNumber += 1
         tempArray.append(constGroupHeaderName+str(currentGroupNumber))
         tempArray2 = []
         for joint in group.Joints:
            if joint.JointRole == self.MAIN and not currentJointRole == joint.JointRole:
               tempArray2.append('R')
               self.RobotInformation.containsRobot=True
            if joint.JointRole == self.RAIL and not currentJointRole == joint.JointRole:
               tempArray2.append('BC')
               self.RobotInformation.containsBase=True
            if joint.JointRole == self.WORKPIECE_POSITIONER and not currentJointRole == joint.JointRole:
               tempArray2.append('EC')
               self.RobotInformation.containsStation=True
            currentJointRole = joint.JointRole
         tempArray.append(tempArray2)
         # ......!!!....self.RobotInformation.YaskawaOutputStyle.append(tempArray)
         if not self.CheckForGroupsFromAttributesAndJoints(tempArray):
            self.Logging.LogWarn('Could not find ' + str(tempArray[1]) + ' from CENOlpYaskawaGroupsMapping. Add as ' + str(tempArray[0]))
            self.RobotInformation.YaskawaOutputStyle.append(tempArray)
         else:
            iDummy = 0
            #self.Logging.LogWarn('FOUND ' + str(tempArray[1]) + ' in CENOlpYaskawaGroupsMapping. NOT ' + str(tempArray[0]))
         tempArray=[]
         tempArray2=[]
      tempArray = []

   def OutputYaskawaPtp(self, operator: DULPythonDownloadOperator, posname: str, position: DULPythonPosition):
      """_summary_

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         posname (str): name of the position
         position (DULPythonPosition): Position operator gives access to the position object. The position object is equal to an tool path element.

      Returns:
         _type_: _description_
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputYaskawaPtp called")
      # Data
      if self.PosType == self.POS_TYPE_RECTAN:
         self.OutputYaskawaCoordinates(posname, position.GetXYZ(), position.GetOrientation(), position.GetName(), position.GetConfig(), position.GetTurn(),position.GetAllJointValues())       
      else:
         self.OutputYaskawaPulses(posname, position.GetXYZ(), position.GetOrientation(), position.GetName(), position.GetConfig(), position.GetTurn(),position.GetAllJointValues())  
      # Source
      iGroupCounter=0
      iSubGroupCounter=0
      moveCommand=''
      # Add Motion Output depending on MotionGroups
      for GroupOutputInfo in self.RobotInformation.YaskawaOutputStyle: 
         iGroupCounter += 1
         # Add Additional Sub Group Output 
         if iGroupCounter > 1:
            moveCommand += ' +MOVJ'
         for subGroup in GroupOutputInfo[1]:
               iSubGroupCounter += 1
               if subGroup == 'R':
                  # Add Robot Motion and Speed
                  moveCommand ='MOVJ '+posname 
               # Add Additional Sub Group Output EC
               if subGroup == 'EC':
                  moveCommand += ' ' +posname.replace('C','EC')
               # Add Additional Sub Group Output BC
               if subGroup == 'BC':
                  moveCommand += ' ' +posname.replace('C','BC')
               if iGroupCounter==1 and len(GroupOutputInfo[1]) == iSubGroupCounter:
                  # Add Speed an Accuracy (position level)
                  #if self.LastLinFeedrate != self.CurrentLinFeedrate:
                  moveCommand += ' VJ='+str(f"{self.CurrentPtpFeedrate:.2f}")
                  self.LastPtpFeedrate = self.CurrentPtpFeedrate
                  # Add Accuracy
                  if self.CurrentAccuracyActive:
                     moveCommand += ' PL=' + str(self.GetYaskawaPositionLevelFromAccuracyValue(self.CurrentPtpAccuracy))
                     self.LastPtpAccuracy=self.CurrentPtpAccuracy
                  else:
                     if self.LastLinAccuracy > 0.000001:
                        self.LastLinAccuracy = 0.0
                        moveCommand += ' PL=0'
      return moveCommand

   def OutputYaskawaLin(self, operator: DULPythonDownloadOperator, posname: str, position: DULPythonPosition):
      """_summary_

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         posname (str): name of the position
         position (DULPythonPosition): Position operator gives access to the position object. The position object is equal to an tool path element.

      Returns:
         _type_: _description_
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputLin called")
      # Data 
      if self.PosType == self.POS_TYPE_RECTAN:
         self.OutputYaskawaCoordinates(posname, position.GetXYZ(), position.GetOrientation(), position.GetName(), position.GetConfig(), position.GetTurn(),position.GetAllJointValues())       
      else:
         self.OutputYaskawaPulses(posname, position.GetXYZ(), position.GetOrientation(), position.GetName(), position.GetConfig(), position.GetTurn(),position.GetAllJointValues()) 
      # Source      
      iGroupCounter=0
      iSubGroupCounter=0
      moveCommand=''
      # Add Motion Output depending on MotionGroups      
      for GroupOutputInfo in self.RobotInformation.YaskawaOutputStyle: 
         iGroupCounter += 1               
         # Add Additional Sub Group Output 
         if iGroupCounter > 1:
            moveCommand += ' +MOVJ'
         for subGroup in GroupOutputInfo[1]:
               iSubGroupCounter += 1
               if subGroup == 'R':
                  # Add Robot Motion 
                  moveCommand ='MOVL '+posname                  
               # Add Additional Sub Group Output EC
               if subGroup == 'EC':
                  moveCommand += ' ' +posname.replace('C','EC')
               # Add Additional Sub Group Output BC
               if subGroup == 'BC':
                  moveCommand += ' ' +posname.replace('C','BC')
               #if subGroup == 'R':
               if iGroupCounter==1 and len(GroupOutputInfo[1]) == iSubGroupCounter:
                  # Add Speed an Accuracy (position level)
                  #if self.LastLinFeedrate != self.CurrentLinFeedrate:
                  moveCommand += ' V=%.1f' % (self.CurrentLinFeedrate*1000)
                  self.LastLinFeedrate = self.CurrentLinFeedrate
                  # Add Accuracy
                  if self.CurrentAccuracyActive:
                     moveCommand += ' PL=' + str(self.GetYaskawaPositionLevelFromAccuracyValue(self.CurrentLinAccuracy))
                     self.LastLinAccuracy=self.CurrentLinAccuracy 
                  else:
                     if self.LastLinAccuracy > 0.000001:
                        self.LastLinAccuracy = 0.0
                        moveCommand += ' PL=0'
      return moveCommand

   def OutputYaskawaCirc(self, operator: DULPythonDownloadOperator, vianame: str, posname: str, viaPoint: DULPythonPosition, endPoint: DULPythonPosition):
      """_summary_

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         vianame (str): via point name
         posname (str): position point name
         viaPoint (DULPythonPosition): via point of the motion
         endPoint (DULPythonPosition): end point of the motion

      Returns:
         _type_: 
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("SimplePython OutputCirc called")
      if self.PosType == self.POS_TYPE_RECTAN:
         self.OutputYaskawaCoordinates(vianame, viaPoint.GetXYZ(), viaPoint.GetOrientation(), viaPoint.GetName(), viaPoint.GetConfig(), viaPoint.GetTurn(),viaPoint.GetAllJointValues())       
      else:
         self.OutputYaskawaPulses(vianame, viaPoint.GetXYZ(), viaPoint.GetOrientation(), viaPoint.GetName(), viaPoint.GetConfig(), viaPoint.GetTurn(),viaPoint.GetAllJointValues()) 
      # Source      
      iGroupCounter=0
      iSubGroupCounter=0
      moveCommand=''
      # Redefine Last Motion  to be first MOVC command (Yaskawa CIRC consists of 3 instead of 2 Instructions...)
      # Due to that, an extra LIN position was inserted before
      LastSourceArrayString=self.Source[len(self.Source)-1]
      if LastSourceArrayString.startswith('MOVJ'):
         # Speed also has to be changed (removed and replaced bi LIN feedrate) because output was VJ
         NewLine=LastSourceArrayString.replace('MOVJ','MOVC').split(' V')[0]
         NewLine += ' V=%.1f' % (self.CurrentLinFeedrate*1000) 
         NewLine += ' PL=' + str(self.GetYaskawaPositionLevelFromAccuracyValue(self.CurrentLinAccuracy))
         self.Source[len(self.Source)-1] =NewLine
      if LastSourceArrayString.startswith('MOVL'):
         NewLine=LastSourceArrayString.replace('MOVL','MOVC')
         self.Source[len(self.Source)-1] =NewLine
      #self.Source(len(self.Source))
      
      # Add ViaMotion Output depending on MotionGroups      
      for GroupOutputInfo in self.RobotInformation.YaskawaOutputStyle: 
         iGroupCounter += 1               
         # Add Additional Sub Group Output 
         if iGroupCounter > 1:
            moveCommand += ' +MOVJ'
         for subGroup in GroupOutputInfo[1]:
               iSubGroupCounter += 1
               if subGroup == 'R':
                  # Add Robot Motion and Speed
                  moveCommand +='MOVC '+vianame 
               # Add Additional Sub Group Output EC
               if subGroup == 'EC':
                  #moveCommand += ' ' + 'EC{num:0{width}}'.format(num=self.PosCounterC-2,width=5)
                  moveCommand += ' ' +vianame.replace('C','EC')
               # Add Additional Sub Group Output BC
               if subGroup == 'BC':
                  #moveCommand += ' ' + 'BC{num:0{width}}'.format(num=self.PosCounterC-2,width=5)
                  moveCommand += ' ' +vianame.replace('C','BC')
               if iGroupCounter==1 and len(GroupOutputInfo[1]) == iSubGroupCounter:
                  # Add Speed an Accuracy (position level)
                  #if self.LastLinFeedrate != self.CurrentLinFeedrate:
                  moveCommand += ' V=%.1f' % (self.CurrentLinFeedrate*1000)
                  self.LastLinFeedrate = self.CurrentLinFeedrate
                  # Add Accuracy
                  if self.CurrentAccuracyActive:
                     moveCommand += ' PL=' + str(self.GetYaskawaPositionLevelFromAccuracyValue(self.CurrentLinAccuracy))
                     self.LastLinAccuracy=self.CurrentLinAccuracy 
                  else:
                     if self.LastLinAccuracy > 0.000001:
                        self.LastLinAccuracy = 0.0
                        moveCommand += ' PL=0'
      

      # Newline for 2nd Circ point
      moveCommand += '\n'
      iGroupCounter=0
      iSubGroupCounter=0
      
      # Add Motion Output depending on MotionGroups      
      for GroupOutputInfo in self.RobotInformation.YaskawaOutputStyle: 
         iGroupCounter += 1               
         # Add Additional Sub Group Output 
         if iGroupCounter > 1:
            moveCommand += ' +MOVJ'
         for subGroup in GroupOutputInfo[1]:
               iSubGroupCounter += 1
               if subGroup == 'R':
                  # Add Robot Motion and Speed
                  moveCommand +='MOVC '+posname 
               # Add Additional Sub Group Output EC
               if subGroup == 'EC':
                  #moveCommand += ' ' + 'EC{num:0{width}}'.format(num=self.PosCounterC-1,width=5)
                  moveCommand += ' ' +posname.replace('C','EC')
               # Add Additional Sub Group Output BC
               if subGroup == 'BC':
                  #moveCommand += ' ' + 'BC{num:0{width}}'.format(num=self.PosCounterC-1,width=5)
                  moveCommand += ' ' +posname.replace('C','BC')
               if iGroupCounter==1 and len(GroupOutputInfo[1]) == iSubGroupCounter:
                  # Add Speed an Accuracy (position level)
                  #if self.LastLinFeedrate != self.CurrentLinFeedrate:
                  moveCommand += ' V=%.1f' % (self.CurrentLinFeedrate*1000)
                  self.LastLinFeedrate = self.CurrentLinFeedrate
                  # Add Accuracy
                  if self.CurrentAccuracyActive:
                     moveCommand += ' PL=' + str(self.GetYaskawaPositionLevelFromAccuracyValue(self.CurrentLinAccuracy))
                     self.LastLinAccuracy=self.CurrentLinAccuracy 
                  else:
                     if self.LastLinAccuracy > 0.000001:
                        self.LastLinAccuracy = 0.0
                        moveCommand += ' PL=0'
      
      #self.OutputYaskawaCoordinates(posname, endPoint.GetXYZ(), endPoint.GetOrientation(), endPoint.GetName(),endPoint.GetConfig(), endPoint.GetTurn(),endPoint.GetAllJointValues())
      if self.PosType == self.POS_TYPE_RECTAN:
         self.OutputYaskawaCoordinates(posname, endPoint.GetXYZ(), endPoint.GetOrientation(), endPoint.GetName(), endPoint.GetConfig(), endPoint.GetTurn(),endPoint.GetAllJointValues())       
      else:
         self.OutputYaskawaPulses(posname, endPoint.GetXYZ(), endPoint.GetOrientation(), endPoint.GetName(), endPoint.GetConfig(), endPoint.GetTurn(),endPoint.GetAllJointValues()) 
      #self.Source.append('MOVC '+posname) 
      return moveCommand

   def OutputYaskawaCoordinates(self, posname, xyz, angles, initialName, config, turn, joints):
      """_summary_

      Args:
         posname (_type_): position name
         xyz (_type_): _description_
         angles (_type_): _description_
         initialName (_type_): _description_
         config (_type_): _description_
         turn (_type_): _description_
         joints (_type_): _description_
      """
      # Generate cartesian position output data c
      if len(self.DataC) == 0:
         if self.CurrentBaseFrameIndex == 0:
            self.DataC.append("///POSTYPE ROBOT")  
         else:
            self.DataC.append("///POSTYPE USER")
            if self.LastBaseframeIndex != self.CurrentBaseFrameIndex:
               if self.CurrentBaseFrameIndex > -1 and self.CurrentBaseFrameIndex < 9999:
                  self.DataC.append("///USER %d" % (int(self.CurrentBaseFrameIndex)))
         self.DataC.append("///RECTAN")     
      if self.LastToolframeIndex != self.CurrentToolFrameIndex:
         if self.CurrentToolFrameIndex > -1 and self.CurrentToolFrameIndex < 9999:
            self.DataC.append("///TOOL %d" % (int(self.CurrentToolFrameIndex)))
      if self.LastConfig != config or self.LastTurn != turn:
         self.DataC.append("///RCONF "+str(config)+','+str(turn))

      # Joint Values for BC and EC
      robotjoints=[]
      for joint in joints:
         if joint[0].GetJointRole().value == self.MAIN:
               robotjoints.append(joint[1])
      robotjointsPulses=self.GetPulseValuesFromDegrees(joints)

      tempstr = posname + '=%.3f,%.3f,%.3f,%.3f,%.3f,%.3f' % (xyz[0]*1000, xyz[1]*1000,xyz[2]*1000,angles[0],angles[1],angles[2]) # + " '" + initial name + " '" + config + " '" + turn
      self.LastBaseframeIndex=self.CurrentBaseFrameIndex
      self.LastToolframeIndex=self.CurrentToolFrameIndex
      self.LastConfig=config
      self.LastTurn=turn   
      if self.RobotInformation.containsRobot:
         self.DataC.append(tempstr)        
      
      # Output BC Part
      if self.RobotInformation.containsBase and not self.suppressBCECOutput:         
         if len(self.DataBC) == 0:            
            self.DataBC.append('///TOOL 0')
            self.DataBC.append('///RCONF 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
         RCOutputData= posname.replace('C','BC')+'='
         iCounter = 0
         for joint in joints:
            if joint[0].GetJointRole().value == self.RAIL:
               # ....was : RCOutputData += '%.3f,' % (joint[1]*1000)
               RCOutputData += '%d,' % (robotjointsPulses[iCounter])
            iCounter += 1
         self.DataBC.append(RCOutputData[0:len(RCOutputData)-1])   
         self.PosCounterBC += 1
      # Output EC Part    
      if self.RobotInformation.containsStation and not self.suppressBCECOutput:
         # if len(self.DataEC) == 0:            
         #    self.DataEC.append('///POSTYPE PULSE')
         #    self.DataEC.append('///PULSE')
         ECOutputData= posname.replace('C','EC')+'='          
         iCounter = 0
         for joint in joints:
            if joint[0].GetJointRole().value == self.WORKPIECE_POSITIONER:
               if joint[0].GetUnit() == 'deg':
                  # ....was : ECOutputData += '%d,' % (robotjointsPulses[joint[0].GetJointIndex()-1])
                  ECOutputData += '%d,' % (robotjointsPulses[iCounter])
               else:      
                  ECOutputData += '%.3f,' % (joint[1])
            iCounter += 1
         self.DataEC.append(ECOutputData[0:len(ECOutputData)-1])
         self.PosCounterEC +=1
      self.suppressBCECOutput = False

   def OutputYaskawaPulses(self, posname, xyz, angles, initialName, config, turn, joints):
      """_summary_

      Args:
         posname (_type_): _description_
         xyz (_type_): _description_
         angles (_type_): _description_
         initialName (_type_): _description_
         config (_type_): _description_
         turn (_type_): _description_
         joints (_type_): _description_
      """
      # Output Position 
      # Generate cartesian position output data c
      if len(self.DataC) == 0:
         self.DataC.append('///POSTYPE PULSE')
         self.DataC.append('///PULSE')      
      if self.LastBaseframeIndex != self.CurrentBaseFrameIndex:
         if self.CurrentBaseFrameIndex > -1 and self.CurrentBaseFrameIndex < 9999:
            self.DataC.append("///USER %d" % (int(self.CurrentBaseFrameIndex)))
      if self.LastToolframeIndex != self.CurrentToolFrameIndex:
         if self.CurrentToolFrameIndex > -1 and self.CurrentToolFrameIndex < 9999:
            self.DataC.append("///TOOL %d" % (int(self.CurrentToolFrameIndex)))
      
      # Joint Values for BC and EC
      robotjoints=[]
      for joint in joints:
         if joint[0].GetJointRole().value == self.MAIN:             
               robotjoints.append(joint[1])
      robotjointsPulses=self.GetPulseValuesFromDegrees(joints)


      if self.PosType == self.POS_TYPE_PULSE:         
         tempstr= posname + '=%d,%d,%d,%d,%d,%.d' % (robotjointsPulses[0], robotjointsPulses[1], robotjointsPulses[2], robotjointsPulses[3], robotjointsPulses[4], robotjointsPulses[5])#+ " 'E2 Position " + initial name
      else:
         tempstr= posname + '=%.3f,%.3f,%.3f,%.3f,%.3f,%.3f' % (robotjoints[0], robotjoints[1], robotjoints[2], robotjoints[3], robotjoints[4], robotjoints[5])#+ " 'E2 Position " + initial name
      self.LastBaseframeIndex = self.CurrentBaseFrameIndex
      self.LastToolframeIndex = self.CurrentToolFrameIndex
      self.LastConfig = config
      self.LastTurn = turn
      if self.RobotInformation.containsRobot:
         self.DataC.append(tempstr)
         #self.PosCounterC += 1

      # Output BC Part
      if self.RobotInformation.containsBase and not self.suppressBCECOutput:
         RCOutputData= posname.replace('C','BC')+'=' 
         #RCOutputData = str('BC%05d=' % (self.PosCounterC-1))
         iCounter = 0
         for joint in joints:
            if joint[0].GetJointRole().value == self.RAIL:
               # ....was : RCOutputData += '%d,' % (robotjointsPulses[joint[0].GetJointIndex()-1])
               RCOutputData += '%d,' % (robotjointsPulses[iCounter])
            iCounter += 1
         self.DataBC.append(RCOutputData[0:len(RCOutputData)-1]) 
         self.PosCounterBC += 1

      # Output EC Part       
      if self.RobotInformation.containsStation and not self.suppressBCECOutput:
         # if len(self.DataEC) == 0:
         #    #self.DataEC.append(' EC Data Section')
         #    self.DataEC.append('///POSTYPE PULSE')
         #    self.DataEC.append('///PULSE')
         BCOutputData= posname.replace('C','EC')+'=' 
         #BCOutputData = str('EC%05d=' % (self.PosCounterC-1))
         iCounter =0
         for joint in joints:
            if joint[0].GetJointRole().value == self.WORKPIECE_POSITIONER:   
               if joint[0].GetUnit() == 'deg':
                  # .....was : BCOutputData += '%d,' % (robotjointsPulses[joint[0].GetJointIndex()-1])
                  BCOutputData += '%d,' % (robotjointsPulses[iCounter])
               else:      
                  BCOutputData += '%.3f,' % (joint[1]) 
            iCounter += 1
         self.DataEC.append(BCOutputData[0:len(BCOutputData)-1])
         self.PosCounterEC += 1
      self.suppressBCECOutput = False


#################### EVENTS ####################

   def HandleEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handle event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      self.OutputEvent(operator, event)
      motions = event.GetMotions()
      for motion in motions:
         self.HandleMotion(operator, motion)

   def OutputEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Output event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # Only for debugging, output all event to see what is in or not
      if self.DEBUG:
         self.Source.append("' Event: " + str(event. GetInsertPosition()) +  "," + event.GetName())
      if event.GetName()=='Speed':
         self.SetSpeed(event)
      elif event.GetName()=='Acceleration':
         self.SetAcceleration(event)
      elif event.GetName()=='Accuracy':
         self.SetAccuracy(event)
      elif event.GetName() == 'LogicPort':
         self.LogicPortEvent(operator, event)

   def SetSpeed(self, event: DULPythonEvent):
      """Set the current speed from speed event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
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

   def SetAccuracy(self, event: DULPythonEvent):
      """Set current accuracy from accuracy event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      pathtype= ''
      accuracy = -1
      criteria = ''
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            accuracy=attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype=attribute.GetValue()
         if attribute.GetName() == 'Criteria':
            criteria=attribute.GetValue()
      if criteria =='On':
         self.CurrentAccuracyActive = True
         if accuracy>0.0:
            if pathtype == 'Distance':
               self.CurrentLinAccuracy = accuracy
            if pathtype == 'PointToPoint':
               self.CurrentPtpAccuracy = accuracy 
      if criteria == 'Off':
         self.CurrentAccuracyActive = False
      if criteria == 'Distance':
         self.CurrentLinAccuracy = accuracy
         if accuracy>0.0:
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      if criteria == 'JointDistance':
         self.CurrentPtpAccuracy = accuracy
         if accuracy>0.0:      
            self.CurrentAccuracyActive = True
         else:
            self.CurrentAccuracyActive = False
      if self.DEBUG:
            self.Source.append("' DEBUG " + criteria + ' ' + pathtype + ' ' + str(accuracy))

   def SetAcceleration(self, event: DULPythonEvent):
      """Set the current acceleration from acceleration event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      pathtype = ''
      acceleration = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            acceleration = attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype=attribute.GetValue()
      if pathtype =='Contour':
         self.CurrentLinAcceleration = acceleration
      else:
         self.CurrentPtpAcceleration = acceleration

   def LogicPortEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      '''Set signal bool event

      Args:
         operator: download operator
         event: event object
      '''
      # get logging operator
      logger = operator.GetLogOperator()
      # init variables
      eventType = ''
      signalName = ''
      signalAddress = ''
      signalNumber = 0
      # get list opf attributes
      attributes = event.GetAttributes()
      # iterate through attribute list
      for attribute in attributes:
         # get event type, could be following values:
         # - CENE2SetSignal
         # - CENE2SetSignalInt <- not supported in default
         # - CENE2SetSignalFloat <- not supported in default
         # - CENE2SetSignalByte <- not supported in default
         # - CENE2SetSignalShortInt <- not supported in default
         # - CENE2WaitForSignal
         # - CENE2WaitForSignalInt <- not supported in default
         # - CENE2WaitForSignalFloat <- not supported in default
         # - CENE2WaitForSignalByte <- not supported in default
         # - CENE2WaitForSignalShortInt <- not supported in default
         if attribute.GetName() == 'EventType':
            eventType = attribute.GetValue()
         # get the signal name
         elif attribute.GetName() == 'SignalName':
            signalName = attribute.GetValue()
         # address is the automatically generated string of the signal address (e.g. DO3)
         elif attribute.GetName() == 'SignalAddress':
            signalAddress = attribute.GetValue()
            try:
               # cut DI or DO and convert the number to an integer
               signalNumber = int(signalAddress[2:])
            except:
               logger.LogError("DOWNLOADER EXCEPTION: couldn't convert signal address to signal number. Check download")               
         # get the signal value. Can be bool, int, float, ...
         elif attribute.GetName() == 'SignalValue':
            signalValue = attribute.GetValue() 
         try:
            # check if value is of type bool
            if isinstance(signalValue, bool):
               # SET BOOL
               if eventType == 'CENE2SetSignal':
                  # output set bool signal event
                  self.OutputSetSignalBoolEvent(operator, signalName, signalNumber, signalValue,signalAddress)
               # WAITFOR BOOL
               elif eventType == 'CENE2WaitForSignal':
                  # output wait for bol signal event
                  self.OutputWaitForSignalBoolEvent(operator, signalName, signalNumber, signalValue, signalAddress)
               else:
                  logger.LogInfo('DOWNLOADER F: Used event type not supported. Check download.')
                  self.Source.append('EVENT TYPE NOT SUPPORTED')
               # add empty line as separator
               self.Source.append('')
         except:
            logger.LogError('DOWNLOADER EXCEPTION: Set or wait for signal event.')

   def OutputSetSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool, signalAddress: str):
      """Output set signal command in Yaskawa robot program.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         signalName (str): Signal name, used for comment
         signalNumber (int): Signal number
         signalValue (bool): Signal value (True/False)
         signalAddress (str): Address of the signal
      """
      # check if signal is true/false
      if signalValue == True:
         self.Source.append('\' ### Setting %s' % signalAddress)
         self.Source.append('DOUT OT#(%d) ON' % signalNumber)
         #self.Source.append('DO[%d] = True' % (signalNumber))
      else:
         self.Source.append('\' ### Reset %s' % signalAddress)
         self.Source.append('DOUT OT#(%d) OFF' % signalNumber)
         #self.Source.append('DO[%d] = False;' % (signalNumber))

   def OutputWaitForSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool, signalAddress: str):
      """Output wait for signal command in Yaskawa robot program.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         signalName (str): Signal name, used for comment
         signalNumber (int): Signal number
         signalValue (bool): Signal value (True/False)
         signalAddress (str): Address of the signal
      """
      # check if signal is true/false
      if signalValue == True:
         self.Source.append('\' ### Wait for %s' % signalAddress)
         self.Source.append('WAIT IN#(%d)=ON' % signalNumber)
         #self.Source.append('DI[%d] = True' % (signalNumber))
      else:
         self.Source.append('\' ### Wait for %s' % signalAddress)
         self.Source.append('WAIT IN#(%d)=OFF' % signalNumber)
         #self.Source.append('DI[%d] = True' % (signalNumber))

#################### HELPER ####################

   def CheckYaskawaProgramName(self, progname: str):
      """Check program name. Max 32 character

      Args:
         progname (str): name of the program

      Returns:
         _type_: error code (0 = program name ok, 1 = program length to high)
      """
      if len(progname)>32:
         return 1
      #if re.match(progname,'[^0-9a-zA-Z\-\_\!\%\&\(\)\'\\]'):
      #   return 2
      return 0

   def CreateJobHeader(self, program: DULPythonProgram):
      """create the job header information

      Args:
         program (DULPythonProgram): access to the program object
      """
      self.JobHeader.append('/JOB')
      self.JobHeader.append('//NAME '+self._correctedProgramName)
      self.JobHeader.append('//POS')
      # Yaskawa controller needs to know highest number of definitions for Robot,
      # Base and Station (not count, but highest number)
      posNumberR = 0
      posNumberRC = 0
      posNumberEC = 0
      # Usually highest number of Robot is also highest number of Base and Station,
      #but only outputted in case Bse or Station is in use
      if self.RobotInformation.containsRobot:
         posNumberR = self.PosCounterC
      if self.RobotInformation.containsBase:
         posNumberRC = self.PosCounterC
      if self.RobotInformation.containsStation:
         posNumberEC = self.PosCounterC
      # Pos Var Counter is always in output
      self.JobHeader.append('///NPOS ' + str(posNumberR) + ',' + str(posNumberRC) + ',' + str(posNumberEC) + ',' + str(self.PosCounterP) + ',0,0')

   def CreateSourceHeader(self, program: DULPythonProgram, operator: DULPythonDownloadOperator):
      """create the source header information

      Args:
         program (DULPythonProgram): access to the program object
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      #//INST
      #///DATE 2023/09/18 13:48
      #///ATTR SC,RW,RJ
      #///GROUP1 RB2,BS2
      #///GROUP2 ST2 
      #NOP
      self.SourceHeader.append('//INST')

      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      if ktaTest == "TRUE":
         self.SourceHeader.append('///DATE  2025/01/01 08:00')
      else:
         self.SourceHeader.append('///DATE ' + datetime.today().strftime('%Y/%m/%d %H:%M'))
      if self.PosType == self.POS_TYPE_RECTAN:
         self.SourceHeader.append('///ATTR SC,RW,RJ')
      else:
         self.SourceHeader.append('///ATTR SC,RW')
      # Set Group Header Information ///Groupx
      iCounter=0
      for GroupOutputInfo in self.RobotInformation.YaskawaOutputStyle:
         tempstr = '///' + GroupOutputInfo[0] + ' '
         
         for SubGroup in GroupOutputInfo[1]:            
            # use custom names instead of basic names (i.e 'RB1,'ST1' instead of 'R','EC')
            if len(self.CENOlpYaskawaGroupsMapping)>0:
               if self.bReplaceBasicGroupNamesInOutput:
                  # use free defined sub group names
                  tempstr += self.OutputSubGroupNames[iCounter] +','
               else:
                  # use sub group names from E2 resource attribute 'CENOlpYaskawaGroupsMapping'
                  # get ///GROUPx RB1/BS1/ST1 from 
                  # e.g. ['GROUP1',['R','BC']] ['GROUP2',['EC']]
                  # and ['RB1:1:1', 'BS1:1:1', 'ST1:2:2']
                  tempstr += self.GetGroupResourceName(SubGroup) + ','
            else:
               tempstr += SubGroup + ','
            iCounter += 1               
         self.SourceHeader.append(tempstr[0:len(tempstr)-1])
      self.SourceHeader.append('NOP')

   def GetGroupResourceName(self, subGroup):
      '''getting ///GROUPx RB1/BS1/ST1 from R/BC/EC'''
      for YGM in self.CENOlpYaskawaGroupsMapping:
         if subGroup =='R' and YGM[0:2] == 'RB':
            return YGM.split(':')[0]
         if subGroup =='BC' and YGM[0:2] == 'BS':
            return YGM.split(':')[0]
         if subGroup =='EC' and YGM[0:2] == 'ST':
            return YGM.split(':')[0]
      return ''
   
   def GetYaskawaPositionLevelFromAccuracyValue(self, AccuracyValue):
      """Yaskawa method for mapping accuracy value to position level

      Args:
         AccuracyValue (_type_): Accuracy value

      Returns:
         _type_: returns the PL value depending on the 
      """
      # Off[off;Speed;0];PL=1[Speed;13];PL=2[Speed;25];PL=3[Speed;38];PL=4[Speed;50];PL=5[Speed;63];PL=6[Speed;75];PL=7[Speed;88];PL=8[Speed;100]"
      pl = 0
      while (self.YaskawaAccuracyMapping[pl] <= AccuracyValue * 1000 and pl < 8):
         pl += 1
      return pl

   def GetPulseValuesFromDegrees(self, allJointTuple):
      """Returns Joint Array with pulses (for rotational) and mm (for translational)

      Args:
         AllJointTuple (_type_): list with joint values in degree or mm

      Returns:
         list: list with calculated pulse values
      """
      # variable initialization
      iCounter=0
      Degrees=[]
      # iterate through joint list
      for joint in allJointTuple:
         if joint[0].GetUnit() == 'deg':
            # in case of 'deg' calculate pules value of joint 
            Degrees.append(round(int(self.CENOlpZeroValues[iCounter])+joint[1]*float(self.CENOlpPulseValues[iCounter])/360))
         else:
            # in case of Unit 'mm', keep value
            Degrees.append(round(int(self.CENOlpZeroValues[iCounter])+joint[1]*float(self.CENOlpPulseValues[iCounter])))
            # ...was : Degrees.append(joint[1])
         iCounter += 1
      return Degrees


   def GetFirstToolFrame(self, program):
      for groups in program.GetOperationGroups():
         for operation in groups.GetOperations():
               if operation.GetUsedToolProfile().IsVisionFrame() == False:
                  self.CurrentToolFrameIndex = operation.GetUsedToolProfile().GetIndex()
                  return
               
#################### HELPER CLASS (MOTION GROUP & JOINT) ####################

   class RobotSystemInformation():
      """class toi handle to grouping of the motions with respect to robot, base and station
      """

      def __init__(self):
         """Class initialization
         """
         self.MotionGroups = []   
         self.YaskawaOutputStyle = []
         self.containsRobot = False
         self.containsBase = False
         self.containsStation = False
         self.containsPVars = False  

      def AddMotionGroupToSystem(self, groupIndex: int):
         """Create a new motion group and add it to the system

         Args:
            GroupIndex (int): index of the new motion group

         Returns:
            MotionGroup: return the new created motion group
         """
         motionGroup = self.MotionGroup(groupIndex)
         self.MotionGroups.append(motionGroup)
         return motionGroup
      
      # TODO: Wird das noch gebraucht???
      def GetAllMotionGroups(self):
         """Get a list with all motion groups
         """
         return self.MotionGroups
      
      class MotionGroup():
         def __init__(self,  motionGroupIndex):
            """Class initialization
            """
            # if configuration and turn are empty,
            # motion group doesn't contain a robot and
            # configuration and turn must not be outputted.
            self.MotionGroupIndex = int(motionGroupIndex)
            self.Joints = []

         def AddJointToMotionGroup(self, index, kinematicType, resourceJointType, jointRole, value):
            """Add a joint to the motion group

            Args:
               index: joint index from port mapping in layout builder
               kinematicType: linear or rotation
               resourceJointType: driven or synchronous joint
               jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
               value: joint value

            Return:
               return the new created joint object
            """
            joint = self.Joint(index, kinematicType, resourceJointType, jointRole, value)
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
               if joint.resourceJointType == self.SYNCHRONOUS_JOINT:
                  synchronousJoints.append(joint)
            return synchronousJoints
         
         def GetAllDrivenJoints(self):
            '''Get all synchronous joints from motion group

            Return:
               Returns a list of all synchronous joints of the motion group
            '''
            synchronousJoints = []
            for joint in self.joints:
               if joint.ResourceJointType == self.DRIVEN_JOINT:
                  synchronousJoints.append(joint)
            return synchronousJoints
         
         class Joint():
            """Joint class to store important joint information in a separated object
            """

            def __init__(self, index, movementType, resourceJointType, jointRole, value):
               """Class initialization

               Args:
                  index: joint index from port mapping in layout builder
                  kinematicType: linear or rotation
                  resourceJointType: driven or synchronous joint
                  jointRole: to which resource type the joint belong (robot, rail, workpiece positioner, ...)
                  value: joint value
               """
               self.Index = index
               # movement type is linear or rotation
               self.KinematicType = movementType
               # resource joint type can be driven or synchronous
               self.ResourceJointType = resourceJointType
               self.JointRole = jointRole
               self.Value = value