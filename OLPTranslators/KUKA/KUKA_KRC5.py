"""
COPYRIGHT Cenit AG Q1/2024
   KUKA KRC5 downloader

   This downloader* SUPPORTs:
      Motion commands PTP/LIN/CIR                  YES
      Motion commands SPTP/SLIN                    YES
      tool & base frame mapping                    YES
      motion events                                YES
      controller ports (bool only)                 YES
      resource ports:                              NO
      robot team/PROGSYNC multi robot handshake    YES
      robot team/synchronized multi robot motions  NO

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
"""

import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from enum import Enum
from datetime import datetime
from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *
from centypes import *
from dataclasses import dataclass

#################### CONSTANTS ####################
@dataclass
class Tech():
   # Global Technology placeholder attribs
   # Placeholder for Motion/Tech Fold data
   ParamFoldIlfProviderEntry: str = ''
   ParamFoldEndTech: str = ''
   # Placeholder for Tech OptionPack syntax inside of the motion fold
   SourceFirstMotionFold: str = ''
   SourceBeforeMotion = []
   SourceAfterMotion = []
   # Sort DAT file entries by E6POS, LDAT, FDAT and Technology DAT
   SortDat:bool = False
   # Default velocity units. To be overwritten be controller string attributes by the same name
   VelocityUnitLinear:str = 'm/s'
   VelocityUnitTechnology:str = 'm/s' #customize to 'm/min', 'cm/min'  or 'm/s'
   OptionPacks = []
   # Default KSS version. To be overwritten be controller string attribute by the same name
   KssVersion:str = '8.7'
   KssVersionList = []
   # Names of events to read ahead
   ReadAheadEvents = []
   # Flag to be set ArcWelding or other technology downloader
   SplinesWhenNotProcessing = False
   # Flag to be set/reset in tool_on/off events
   Processing = False

# name of the download class
DOWNLOAD_CLASS_NAME = "KUKA_KRC5"
class KUKA_KRC5(Downloader):
   """KUKA_KRC5 downloader
   Base robot vendor downloader
   Derived from: SimplePython downloader
   """
   PARAM_FOLD_ILF_PROVIDER_DEFAULT = 'kukaroboter.basistech.inlineforms.movement.old'
   SOURCEFILE_EXTENSION = '.src'
   DATAFILE_EXTENSION = '.dat'
   DOWNLOADER_VERSION = '1.1'
   
#################### BASE FUNCTIONS CALLED BY DOWNLOAD STARTER ####################

   def __init__(self) -> None:
      """Class initialization
      """
      super().__init__()

      self.Tech = Tech()  # Initialize the Tech class and assign it to an instance variable

      self.FileUtil = FileUtility()
      # controller Manufacturer entry
      self.controllerManufacturer = ''
      # controller Series entry
      self.controllerSeries = ''
      # controller Model entry
      self.controllerModel = ''
      # controller output path entry
      self.controllerOutputDir = ''
      # output source file path
      self.OutputSourceFilePath = ''
      # output data file path
      self.OutputDataFilePath = ''
      # array to store common data/source header content
      self.Header = []
      # array to store source initialization commands
      self.SourceHeader = []
      # array to store motion commands
      self.Source = []
      # array to store suppressed motion commands
      self.SourceSuppressed = []
      # program footer text
      self.SourceFooter = []
      # array to store data initialization commands
      self.DataHeader = []
      # array to store point coordinates/joints, motion and frame profiles
      self.Data = []
      self.Data.append('; Declarations')
      self.DataE6POS = []
      self.DataE6AXIS = []
      self.DataPDAT = []
      self.DataFDAT = []
      self.DataLDAT = []
      self.DataTechDAT1 = []
      self.DataTechDAT2 = []
      self.DataTechDAT3 = []
      # data footer text
      self.DataFooter = []
      
      # max. Base Frame Index
      self.maxBaseIndex = 128
      # max. Tool Frame Index
      self.maxToolIndex = 128
      # current Base Frame Index
      self.CurrentBaseIndex = ''
      # current Tool Frame Index
      self.CurrentToolIndex = ''
      # current Base Frame Name
      self.CurrentBaseName = ''
      # current Tool Frame Name
      self.CurrentToolName = ''
      # current Base Frame
      self.CurrentBase: DULPythonBaseProfile
      # current Tool Frame
      self.CurrentTool: DULPythonToolProfile
      

      # current Operation Group
      self.CurrentOperationGroup: DULPythonOperationGroup
      # current Operation
      self.CurrentOperation: DULPythonOperation

      # current set point to point acceleration; expected unit = [%]
      self.CurrentPtpAcceleration = 100.0
      # current set linear acceleration; expected unit = [%]
      self.CurrentLinAcceleration = 100.0
      # current set velocity for point to point; expected unit = [%]
      self.CurrentPtpVelocity = 20.0
      # current set linear velocity; expected unit = [mm/sec]
      self.CurrentLinVelocity = 500
      self.CurrentLinVelocityTechnology = 500
      # current set accuracy for point to point; expected unit = [%]
      self.CurrentPtpAccuracy = 50.0
      # current set linear accuracy; expected unit = [%]
      self.CurrentLinAccuracy = 50.0
      self.CurrentAccuracyActive = False
      # PDAT/LDAT Motion Profile Counter
      self.MotionProfileCounterLIN = 0 
      self.MotionProfileCounterPTP = 0
      # VelocityParamSet can be overwritten by derived downloader
      self.VelocityParamSet = ''
      # store latest position
      self.CurrentE6POS: str = ''
      self.CurrentE6AXIS: str = ''
      self.CurrentFDAT: str = ''
      self.CurrentLDAT: str = ''
      self.CurrentPDAT: str = ''

      self.SuppressNextMotion: bool = False
      self.SuppressNextSource: bool = False
      self.NoNextSource: bool = False
      self.DownloadReferenceMotion: bool = False
      self.SpecialPosName: str = ''

      # used language in user interface
      self.DownloaderName = ""
      self.Language = ""

   def Initialize(self, operator : DULPythonDownloadOperator):
      """Translator initialization.
      Called first and only once per download, even when downloading sub programs

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """

      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader Initialize called")
      
      # get set language
      # self.DownloaderName = DOWNLOAD_CLASS_NAME
      self.Language = operator.GetCurrentLanguage()
      pass

   def OutputHeader(self, operator: DULPythonDownloadOperator, controller : DULPythonController):
      """Create and store program header. Internally called from download starter. (Main file Header if Subprograms are included) 
      Separated function, because some information doesn't exist at the beginning

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         controller (DULPythonController): controller instance gives access to controller, its attributes, its children and connected resources  
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputHeader called")
      
      velocityUnitLinear = ''
      velocityUnitTechnology = ''
      #Get downloader flags from controller attributes
      try:
         # Get KssVersion string from controller attributes if available and reduce to major.minor
         kssVersion = controller.GetString('KssVersion',False)
         self.Tech.KssVersionList = kssVersion.split('.')
         self.Tech.KssVersion = self.Tech.KssVersionList[0] + '.' + self.Tech.KssVersionList[1]
      except:
         self.Tech.KssVersionList = self.Tech.KssVersion.split('.')
         self.Tech.KssVersion = self.Tech.KssVersionList[0] + '.' + self.Tech.KssVersionList[1]
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " 'KssVersion' ")
         logger.LogWarn("Downloader Warning: Default KSS version: " + self.Tech.KssVersion)
      try:
         # Get velocity unit for regular linear/circular motion from controller attributes if available
         velocityUnitLinear = controller.GetString('VelocityUnitLinear',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " 'VelocityUnitLinear' from ['m/min','cm/min','m/s']")
      if velocityUnitLinear in ['m/min','cm/min','m/s']:
         self.Tech.VelocityUnitLinear = velocityUnitLinear
      try:
         # Get velocity unit for regular linear/circular motion from controller attributes if available
         velocityUnitTechnology = controller.GetString('VelocityUnitTechnology',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " 'VelocityUnitTechnology' from ['m/min','cm/min','m/s']")
      if velocityUnitTechnology in ['m/min','cm/min','m/s']:
         self.Tech.VelocityUnitTechnology = velocityUnitTechnology

      # get program instance
      program = controller.GetActiveProgram()
      # get and store output directory
      self.controllerOutputDir = controller.GetOutputDirectory()
      # get and store header information
      self.controllerName = controller.GetName()
      self.controllerManufacturer = controller.GetManufacturer()
      self.controllerSeries = controller.GetSeries()
      self.controllerModel = controller.GetModel()
      self.programName = program.GetName()
      date = self.GetDate()
      time = self.GetTime()
      user = self.FileUtil.GetWindowsUserName()
      
      # prevent Date/Time Differences during Test Run
      ktaTest = operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      #self.AddLineToHeader('REM "GetWindowsEnvironmentVariable(CPOST_TESTLAUF_CENIT)=%s"' % (ktaTest))
      if ktaTest == "TRUE":
         date = "KTA"
         time = "TEST"
         user = "KTATEST"
         
      # define common source and data file header
      self.AddLineToHeader('&ACCESS RVP')
      self.AddLineToHeader('&REL 10')
      self.AddLineToHeader('&PARAM EDITMASK = *')
      
      # define data file header
      self.AddLineToDataHeader('DEFDAT %s' % (self.programName))
      self.AddLineToDataHeader('; %s' % (self.controllerName))
      
      # define source file header
      self.AddLineToSourceHeader('DEF %s( )' % (self.programName))
      self.AddLineToSourceHeader('; %s' % (self.controllerName))
      self.AddLineToSourceHeader(';FOLD BASISTECH INI')
      self.AddLineToSourceHeader('  GLOBAL INTERRUPT DECL 3 WHEN $STOPMESS==TRUE DO IR_STOPM ( )')
      self.AddLineToSourceHeader('  INTERRUPT ON 3 ')
      self.AddLineToSourceHeader('  BAS (#INITMOV,0 )')
      self.AddLineToSourceHeader(';ENDFOLD (BASISTECH INI)')

      self.AddLineToSourceHeader('\n;***************************************************')

      self.AddLineToSourceHeader('; PROGRAM         = %s%s' % (self.programName, self.SOURCEFILE_EXTENSION))
      self.AddLineToSourceHeader('; MANUFACTURER    = %s' % (self.controllerManufacturer))
      # the model attribute is being used as series since KRC5 is not available in the drop down list
      # self.AddLineToSourceHeader('; SERIES          = %s' % (self.controllerSeries))
      self.AddLineToSourceHeader('; SERIES          = %s' % (self.controllerModel))
      #                             CREATE          = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToSourceHeader('; CREATE          = DATE %s TIME %s' % (date, time))
      #                             MODIFIED        = DATE 23-12-12 TIME 17:03:19;
      self.AddLineToSourceHeader('; MODIFIED        = DATE %s TIME %s' % (date, time))
      self.AddLineToSourceHeader('; VERSION         = ' + self.DOWNLOADER_VERSION)
      if self.DownloaderName == '':
         self.AddLineToSourceHeader('; Downloader      = %s.py' % (DOWNLOAD_CLASS_NAME))
      else:
         self.AddLineToSourceHeader('; Downloader      = %s.py' % (self.DownloaderName))
      self.AddLineToSourceHeader('; User            = %s' % (user))
      self.AddLineToSourceHeader(';***************************************************')
      self.AddLineToSourceHeader('; KSS Version     = %s' % (self.Tech.KssVersion))
      self.AddLineToSourceHeader(';***************************************************')

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
      """

      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader ProgramStart called")
      logger.LogDebug(program.GetName())

   def ProgramEnd(self, operator : DULPythonDownloadOperator, program : DULPythonProgram):
      """Called at the end of each the program 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): Program operator with access to the program content.
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader ProgramEnd called")
      logger.LogDebug(program.GetName())
      
      self.AddLineToSourceFooter("END")
      self.AddLineToDataFooter("ENDDAT")

   def OperationGroupStart(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      """Called at start of each Operation Group 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operationGroup (DULPythonOperationGroup): operationGroup operator with access to the operation groups content.
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationGroupStart called")
      logger.LogDebug(operationGroup.GetName())
      self.CurrentOperationGroup = operationGroup
      self.AddLineToSource( "\n" + "; Operation group: "+ " " + operationGroup.GetName())

   def OperationGroupEnd(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationGroupEnd called")
      logger.LogDebug(operationGroup.GetName())

   def OperationStart(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      """Called at start of each Operation Group 

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         operation (DULPythonOperation): operation operator with access to the operations content.
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationStart called")
      logger.LogDebug(operation.GetName())
      self.CurrentOperation = operation
      
      self.AddLineToSource( "\n" + "; Operation: " + operation.GetName())
      
      # get operations used tool and base frame profiles 
      usedBaseProfile = operation.GetUsedBaseProfile()
      self.CurrentBase = usedBaseProfile
      usedToolProfile = operation.GetUsedToolProfile()
      self.CurrentTool = usedToolProfile
      
      # check and store current Base Frame Index
      if (usedBaseProfile.GetIndex() > self.maxBaseIndex):
         self.CurrentBaseIndex = -1
         logger.LogError("KukaPythonDownloader OperationStart: Not mapped Frame use detected in " + operation.GetName())
      else:
         self.CurrentBaseIndex = usedBaseProfile.GetIndex()
      # check and store current Tool Frame Index
      if (usedToolProfile.GetIndex() > self.maxToolIndex):
         self.CurrentToolIndex = -1
         logger.LogError("KukaPythonDownloader OperationStart: Not mapped Frame use detected in " + operation.GetName())
      else:
         self.CurrentToolIndex = usedToolProfile.GetIndex()
      
      # store current Base and Tool Frame Name
      self.CurrentBaseName = usedBaseProfile.GetName()
      self.CurrentToolName = usedToolProfile.GetName()

   def OperationEnd(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationEnd called")
      logger.LogDebug(operation.GetName())

   def HandleMotion(self, operator : DULPythonDownloadOperator, motion : DULPythonMotion):
      """motion handler called for TPE motion entries and event based motions 
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion object gives access to the complete motion information, positions and events
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader HandleMotion called")
      logger.LogDebug(motion.GetName())

      event: DULPythonEvent
      eventsBefore = motion.GetEventsBefore()
      if len(eventsBefore) > 0:
         for event in eventsBefore:
            self.HandleEvent(operator, event, motion)

      # read ahead to non-motion tech events like ArcOn/Off which need to be processed before the motion for KUKA syntax but simulated after the move
      eventsAfter = motion.GetEventsAfter()
      if len(eventsAfter) > 0:
         for event in eventsAfter:
            try:
               if event.GetName() in self.Tech.ReadAheadEvents:
                  self.HandleReadAheadEvent(operator, event, motion)
            except:
               pass
      
      positionObject = motion.GetPosition()
      
      if not self.SpecialPosName:
         posName = positionObject.GetName()
      else:
         posName = self.SpecialPosName

      # generate and output position info, Frame set, MotionProfile
      if (not motion.IsReferenceMotion() or self.DownloadReferenceMotion) and not self.SuppressNextMotion:
         usedMotionFrameDeclName = "F"+ posName
         usedMotionFrameDeclaration = "DECL FDAT " + usedMotionFrameDeclName + "={TOOL_NO " + str(self.CurrentToolIndex) + ",BASE_NO " + str(self.CurrentBaseIndex) + ',IPO_FRAME #BASE,POINT2[] " "}'
         
         if motion.IsLinearMotion():
            self.MotionProfileCounterLIN +=1
            usedMotionProfileDeclName = "CPDAT" + str(self.MotionProfileCounterLIN)
            usedMotionProfileDeclName = "CPDAT" + posName
            self.OutputPositionData(operator, positionObject)

            if self.Tech.SortDat:
               self.AddLineToDataFDAT(usedMotionFrameDeclaration)
            else:
               self.AddLineToData(usedMotionFrameDeclaration)
            tempData = "DECL LDAT L" + usedMotionProfileDeclName \
                                    +"={VEL " + str(self.CurrentLinVelocity) \
                                    +",ACC "+ str(self.CurrentLinAcceleration) \
                                    +",APO_DIST "+ str(self.CurrentLinAccuracy) \
                                    +",APO_FAC 50.0,AXIS_VEL 100.0,AXIS_ACC 100.0,ORI_TYP #VAR,CIRC_TYP #BASE,JERK_FAC 50.0000,GEAR_JERK 100.000,EXAX_IGN 0}"
            if self.Tech.SortDat:
               self.AddLineToDataLDAT(tempData)
            else:
               self.AddLineToData(tempData)
            # generate and output motion FOLD entry CIRC
            self.OutputMotionData( operator, motion, "LIN", usedMotionFrameDeclName, usedMotionProfileDeclName, posName)
         elif motion.IsCircularMotion():
            self.MotionProfileCounterLIN +=1
            usedMotionProfileDeclName = "CPDAT" + str(self.MotionProfileCounterLIN)
            usedMotionProfileDeclName = "CPDAT" + posName
            viaPositionObject = motion.GetViaPosition()
            self.OutputPositionData(operator, viaPositionObject)
            self.OutputPositionData(operator, positionObject)
            tempData = "DECL FDAT " + usedMotionFrameDeclName + "={TOOL_NO " + str(self.CurrentToolIndex) + ",BASE_NO " + str(self.CurrentBaseIndex) + ',IPO_FRAME #BASE,POINT2[] "' + viaPositionObject.GetName() + '"}'
            if self.Tech.SortDat:
               self.AddLineToDataFDAT(tempData)
            else:
               self.AddLineToData(tempData)
            tempData = "DECL LDAT L" + usedMotionProfileDeclName \
                                    +"={VEL " + str(self.CurrentLinVelocity) \
                                    +",ACC "+ str(self.CurrentLinAcceleration) \
                                    +",APO_DIST "+ str(self.CurrentLinAccuracy) \
                                    +",APO_FAC 50.0,AXIS_VEL 100.0,AXIS_ACC 100.0,ORI_TYP #VAR,CIRC_TYP #BASE,JERK_FAC 50.0000,GEAR_JERK 100.000,EXAX_IGN 0}"
            if self.Tech.SortDat:
               self.AddLineToDataLDAT(tempData)
            else:
               self.AddLineToData(tempData)
            # generate and output motion FOLD entry CIRC
            self.OutputMotionData( operator, motion, "CIRC", usedMotionFrameDeclName, usedMotionProfileDeclName, positionObject.GetName(),viaPositionObject.GetName())
         else:
            self.MotionProfileCounterPTP +=1
            usedMotionProfileDeclName = "PDAT" + str(self.MotionProfileCounterPTP)
            usedMotionProfileDeclName = "PDAT" + posName
            self.OutputPositionData(operator, positionObject)
            if self.Tech.SortDat:
               self.AddLineToDataFDAT(usedMotionFrameDeclaration)
            else:
               self.AddLineToData(usedMotionFrameDeclaration)
            tempData = "DECL PDAT P" + usedMotionProfileDeclName \
                                    + "={VEL " + str(self.CurrentPtpVelocity) \
                                    + ",ACC "+ str(self.CurrentPtpAcceleration) \
                                    + ",APO_DIST "+ str(self.CurrentPtpAccuracy) \
                                    + ",APO_MODE #CDIS,GEAR_JERK 100.000,EXAX_IGN 0}"
            if self.Tech.SortDat:
               self.AddLineToDataPDAT(tempData)
            else:
               self.AddLineToData(tempData)
            # generate and output motion FOLD entry PTP
            self.OutputMotionData( operator, motion, "PTP", usedMotionFrameDeclName, usedMotionProfileDeclName, posName)
      else:
         # Reset suppress motion flag
         self.SuppressNextMotion = False
      # Reset Download reference motion flag
      self.DownloadReferenceMotion = False
      
      eventsAfter = motion.GetEventsAfter()
      if len(eventsAfter) > 0:
         for event in eventsAfter:
            self.HandleEvent(operator, event, motion)

   def SubprogramStart(self, operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader SubprogramStart called")
      logger.LogDebug(subprogram.GetName())

   def SubProgramEnd(self, operator : DULPythonDownloadOperator, subprogram : DULPythonSubprogram):
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationEnd called")
      logger.LogDebug(subprogram.GetName())

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Create output file, internally called
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader CreateOutputFile called")
      # define output path
      self.OutputSourceFilePath = self.controllerOutputDir + "\\" + self.programName + self.SOURCEFILE_EXTENSION
      self.OutputDataFilePath = self.controllerOutputDir + "\\" + self.programName + self.DATAFILE_EXTENSION
      # print debug Information
      logger.LogDebug(self.OutputSourceFilePath)
      logger.LogDebug(self.OutputDataFilePath)

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Write output file, internally called. 
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader WriteOutputFile called")
      # create files and output the program
      self.FileUtil.AppendTextArrayToFile(self.OutputSourceFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputSourceFilePath, self.SourceHeader)
      self.FileUtil.AppendTextArrayToFile(self.OutputSourceFilePath, self.Source)
      if self.SourceSuppressed:
         self.SourceSuppressed.append("ENDIF")
      self.FileUtil.AppendTextArrayToFile(self.OutputSourceFilePath, self.SourceSuppressed)
      self.FileUtil.AppendTextArrayToFile(self.OutputSourceFilePath, self.SourceFooter)
      
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataHeader)
      if not self.Tech.SortDat:
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.Data)
      else:
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataE6POS)
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataE6AXIS)
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataPDAT)
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataLDAT)
         self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataFDAT)
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataTechDAT1)
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataTechDAT2)
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataTechDAT3)
      self.FileUtil.AppendTextArrayToFile(self.OutputDataFilePath, self.DataFooter)
      
      self.Header.clear()
      self.SourceHeader.clear()
      self.Source.clear()
      self.SourceSuppressed.clear()
      self.SourceFooter.clear()
      self.DataHeader.clear()
      self.Data.clear()
      self.DataE6POS.clear()
      self.DataE6AXIS.clear()
      self.DataPDAT.clear()
      self.DataLDAT.clear()
      self.DataFDAT.clear()
      self.DataTechDAT1.clear()
      self.DataTechDAT2.clear()
      self.DataTechDAT3.clear()
      self.DataFooter.clear()

   def CloseOutputFile(self, operator: DULPythonDownloadOperator):
      """register finalized output files, internally called. 
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      """
      operator.AddOutputFilePath(self.OutputSourceFilePath)
      operator.AddOutputFilePath(self.OutputDataFilePath)

#################### INTERNAL HANDLE FUNCTIONS ####################

   def FillTechPlaceholders(self, operator : DULPythonDownloadOperator, motion : DULPythonMotion, motionType : str, motionFrames : str, motionProfile : str, positionName : str, viaPositionName : str = ""):
      """Fill global technological placeholder attributes in derived DL method to be used in base DL output methods
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motionType (string): type of motion [LIN,PTP,CIRC]
         motionFrames (string): motions frame definition name [FDAT1, F{positionName}]
         motionProfile (string): motions velocity, acceleration and accuracy setting variable name [PPDAT1, LCPDAT1]
         positionName (string): motions position name / point name
         viaPositionName (string): motions via position name, optional for circular motion 
      """
      pass

   def OutputMotionData(self, operator : DULPythonDownloadOperator, motion : DULPythonMotion, motionType : str, motionFrames : str, motionProfile : str, positionName : str, viaPositionName : str = ""):
      """Generate motion command output
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motionType (string): type of motion [LIN,PTP,CIRC]
         motionFrames (string): motions frame definition name [FDAT1, F{positionName}]
         motionProfile (string): motions velocity, acceleration and accuracy setting variable name [PPDAT1, LCPDAT1]
         positionName (string): motions position name / point name
         viaPositionName (string): motions via position name, optional for circular motion 
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputMotionData called")
      
      # Empty line
      self.Source.append('')

      if not self.NoNextSource:
         # Output the source statements as usual or 'hidden' at the and of the SRC file
         # Hidden positions are sometime required for things like measurement positions or similar
         if self.SuppressNextSource:
            addLineToSource = self.AddLineToSourceSuppressed
            if not self.SourceSuppressed:
               self.AddLineToSourceSuppressed('')
               self.AddLineToSourceSuppressed(';========== SeamFind & TouchSense Positions --> NOT MOVED TO =========')
               self.AddLineToSourceSuppressed(';FOLD SeamFind Clear ;%{PE}')
               self.AddLineToSourceSuppressed(';FOLD Parameters Parameters ;%{h}')
               self.AddLineToSourceSuppressed(';Params IlfProvider=SeamFind.SensorClear')
               self.AddLineToSourceSuppressed(';ENDFOLD')
               self.AddLineToSourceSuppressed('BF_ClearSensor()')
               self.AddLineToSourceSuppressed(';ENDFOLD')
               self.AddLineToSourceSuppressed('')
               self.AddLineToSourceSuppressed('IF FALSE THEN')
         else:
            addLineToSource = self.AddLineToSource
         
         # Decide if spline output applies to next LIN or PTP motion
         if self.Tech.SplinesWhenNotProcessing == True and self.Tech.Processing == False:
            splineOutput = True
            splineIdentifier = 'S'
            splineFieldEnabledSyntax = '; Kuka.VelocityFieldEnabled=True; Kuka.ColDetectFieldEnabled=True'
         else:
            splineOutput = False
            splineIdentifier = ''
            splineFieldEnabledSyntax = ''

         # motion Fold addition/change according tech event activity [GunOn/Off,GlueOn/Off,ArcOn/Off] and spline output
         eventFoldEntry = ""
         if self.Tech.ParamFoldIlfProviderEntry == '':
            if splineOutput == True:
               self.Tech.ParamFoldIlfProviderEntry = 'kukaroboter.basistech.inlineforms.movement.spline'
            else:
               self.Tech.ParamFoldIlfProviderEntry = self.PARAM_FOLD_ILF_PROVIDER_DEFAULT

         self.CurrentLinVelocityTechnology = self.CurrentLinVelocity

         self.VelocityParamSet = ''
         self.FillTechPlaceholders(operator, motion, motionType, motionFrames, motionProfile, positionName, viaPositionName)
         
         # set entries for current accuracy mode [Flyby: On/Off]
         if self.CurrentAccuracyActive == True and splineOutput == False:
            continuosMotionFlag = "CONT "
            continuosMotionMode = "C_DIS "
         else:
            continuosMotionFlag = ""
            continuosMotionMode = ""

         # set different Fold entries for PTP or LIN/CIRC 
         if motionType == "PTP":
            motionProfileActSet = "PDAT_ACT = P" + motionProfile
            splineMotionProfile =  "P" + motionProfile
            if not self.VelocityParamSet:
               self.VelocityParamSet = "#PTP_PARAMS," + str(self.CurrentPtpVelocity)
            velocityFoldEntry = str(int(self.CurrentPtpVelocity)) + " % "
            paramsFoldEntry = "Kuka.PointName=" + positionName + "; Kuka.BlendingEnabled=True; "\
               "Kuka.MoveDataPtpName=" + motionProfile + "; Kuka.VelocityPtp=" + str(int(self.CurrentPtpVelocity)) + splineFieldEnabledSyntax + "; Kuka.CurrentCDSetIndex=0; "\
                  "Kuka.MovementParameterFieldEnabled=True; IlfCommand=" + splineIdentifier + motionType
         else:
            motionProfileActSet = "LDAT_ACT = L" + motionProfile
            splineMotionProfile =  "L" + motionProfile
            if not self.VelocityParamSet:
               self.VelocityParamSet = "#CP_PARAMS," + str(self.CurrentLinVelocity)
            velocityFoldEntry = str(self.CurrentLinVelocity) + " m/s "
            paramsFoldEntry = "Kuka.PointName=" + positionName + "; Kuka.BlendingEnabled=True; "\
               "Kuka.MoveDataName=" + motionProfile + "; Kuka.VelocityPath=" + f'{self.CurrentLinVelocityTechnology:.3f}' + splineFieldEnabledSyntax + "; Kuka.CurrentCDSetIndex=0; "\
                  "Kuka.MovementParameterFieldEnabled=True; " + self.Tech.ParamFoldEndTech
            if self.Tech.ParamFoldEndTech == '':
               paramsFoldEntry = paramsFoldEntry + "IlfCommand=" + splineIdentifier + motionType

         # set different Fold entries and structure for LIN or CIRC
         if motionType == "CIRC":
            paramsFoldEntry = "Kuka.PointName=" + positionName + "; Kuka.HelpPointName=" + viaPositionName + "; Kuka.BlendingEnabled=True; "\
               "Kuka.MoveDataName=" + motionProfile + "; Kuka.VelocityPath=" + f'{self.CurrentLinVelocityTechnology:.3f}' + "; Kuka.CurrentCDSetIndex=0; "\
                  "Kuka.MovementParameterFieldEnabled=True; " + self.Tech.ParamFoldEndTech
            if self.Tech.ParamFoldEndTech == '':
               paramsFoldEntry = paramsFoldEntry + "IlfCommand=" + motionType
            motionCMD = motionType + " X" + viaPositionName + ", X" + positionName + " " + continuosMotionMode
            # output first Motion Fold Line output for CIRC to source
            addLineToSource( ";FOLD " + self.Tech.SourceFirstMotionFold + motionType + " " + viaPositionName + " " + positionName + " " + continuosMotionFlag + 
                                    "Vel=" + velocityFoldEntry + motionProfile + eventFoldEntry + 
                                    " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName + 
                                    " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         else:         
            motionCMD = splineIdentifier + motionType + " X" + positionName + " " + continuosMotionMode
            if splineOutput:
               if motionType == "PTP":
                  #            SPTP XME1_1 WITH $VEL_AXIS[1] = SVEL_JOINT(100.0),                                     $TOOL = STOOL2(FME1_1),                $BASE = SBASE(FME1_1.BASE_NO),                $IPO_MODE = SIPO_MODE(FME1_1.IPO_FRAME),                $LOAD = SLOAD(FME1_1.TOOL_NO),                $ACC_AXIS[1] = SACC_JOINT(PPDAT_ME),                    $APO = SAPO_PTP(PPDAT_ME),                    $GEAR_JERK[1] = SGEAR_JERK(PPDAT_ME),                    $COLLMON_TOL_PRO[1] = USE_CM_PRO_VALUES(0)
                  motionCMD = motionCMD + "WITH $VEL_AXIS[1] = SVEL_JOINT(" + str(int(self.CurrentPtpVelocity)) + "), $TOOL = STOOL2(F" + positionName + "), $BASE = SBASE(F" + positionName + ".BASE_NO), $IPO_MODE = SIPO_MODE(F" + positionName + ".IPO_FRAME), $LOAD = SLOAD(F" + positionName + ".TOOL_NO), $ACC_AXIS[1] = SACC_JOINT(" + splineMotionProfile + "), $APO = SAPO_PTP(" + splineMotionProfile + "), $GEAR_JERK[1] = SGEAR_JERK(" + splineMotionProfile + "), $COLLMON_TOL_PRO[1] = USE_CM_PRO_VALUES(0)"
               else:
                  #               SLIN XP8 WITH $VEL = SVEL_CP(2.0                                , ,                    LCPDAT24), $TOOL = STOOL2(FP8),                   $BASE = SBASE(FP8.BASE_NO),                   $IPO_MODE = SIPO_MODE(FP8.IPO_FRAME),                   $LOAD = SLOAD(FP8.TOOL_NO),                   $ACC = SACC_CP(LCPDAT24),                    $ORI_TYPE = SORI_TYP(LCPDAT24),                    $APO = SAPO(LCPDAT24),                    $JERK = SJERK(LCPDAT24),                    $COLLMON_TOL_PRO[1] = USE_CM_PRO_VALUES(0)
                  motionCMD = motionCMD + "WITH $VEL = SVEL_CP(" + str(self.CurrentLinVelocity) +", , " + splineMotionProfile + "), $TOOL = STOOL2(F" + positionName + "), $BASE = SBASE(F" + positionName + ".BASE_NO), $IPO_MODE = SIPO_MODE(F" + positionName + ".IPO_FRAME), $LOAD = SLOAD(F" + positionName + ".TOOL_NO), $ACC = SACC_CP(" + splineMotionProfile + "), $ORI_TYPE = SORI_TYP(" + splineMotionProfile + "), $APO = SAPO(" + splineMotionProfile + "), $JERK = SJERK(" + splineMotionProfile + "), $COLLMON_TOL_PRO[1] = USE_CM_PRO_VALUES(0)"
            # output first Motion Fold Line output for PTP/LIN to source
            addLineToSource( ";FOLD " + self.Tech.SourceFirstMotionFold + splineIdentifier + motionType + " " + positionName + " " + continuosMotionFlag + 
                                    "Vel=" + velocityFoldEntry + motionProfile + eventFoldEntry + 
                                    " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName + 
                                    " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         
         # output next Motion Fold Lines output to source
         addLineToSource( "  ;FOLD Parameters ;%{h}")
         addLineToSource( "    ;Params IlfProvider=" + self.Tech.ParamFoldIlfProviderEntry + "; Kuka.IsGlobalPoint=False; " + paramsFoldEntry)
         addLineToSource( "  ;ENDFOLD")
         # Splines don't require the next few lines
         if not splineOutput:
            addLineToSource( "  $BWDSTART = FALSE")
            addLineToSource( "  " + motionProfileActSet)
            addLineToSource( "  FDAT_ACT = " + motionFrames)
            addLineToSource( "  BAS(" + self.VelocityParamSet + ")")
            addLineToSource( "  SET_CD_PARAMS (0)")
         # output Tech Pack info for derive technology specific downloader via global placeholders
         for line in self.Tech.SourceBeforeMotion:
            addLineToSource(line)
         # actual motion command
         addLineToSource( "  " + motionCMD)
         # output Tech Pack info for derive technology specific downloader via global placeholders
         for line in self.Tech.SourceAfterMotion:
            addLineToSource(line)
         addLineToSource( ";ENDFOLD")
      # clear Tech Pack info
      self.Tech.SourceFirstMotionFold = ''
      self.Tech.SourceBeforeMotion.clear()
      self.Tech.SourceAfterMotion.clear()
      self.Tech.ParamFoldIlfProviderEntry = ''
      self.Tech.ParamFoldEndTech = ''
      # Reset suppress flag
      self.SuppressNextSource = False
      self.NoNextSource = False

   def OutputPositionData(self, operator : DULPythonDownloadOperator, position : DULPythonPosition):
      """Generate position data 
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         position (DULPythonPosition): motions position object gives access to the target position data and attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputPositionData called")
      logger.LogDebug(str(position.GetTargetType().name))
      logger.LogDebug(str(position.GetName()))
      
      xyz = position.GetXYZ()
      angles = position.GetOrientation()
      joints = position.GetMainJointValues()
      externals = position.GetExternalJointValues()
      externals.sort(key=lambda external: external[0].GetJointIndex()) # type: ignore
      dataPrefix = ""
      mainAxisPos = ""
      externalAxisPos = ""
      axisCounter = 0
      if not self.SpecialPosName:
         posName = position.GetName()
      else:
         posName = self.SpecialPosName
      dataCartesianPrefix = "DECL E6POS X" + posName + "={" 
      dataJointPrefix = "DECL E6AXIS X" + posName + "={" 
      motionTargetType:TargetType = position.GetTargetType()
      
      # gather available external axis information
      for ext in externals:
         jointObject:DULPythonJoint = ext[0] # type: ignore
         kinematicType:JointKinematicType = jointObject.GetJointType()
         axisCounter += 1
         # differ between rotation/translational axis (m->mm) 
         if kinematicType == JointKinematicType.Prismatic:
            externalAxisPos += ",E" + str(axisCounter) + " {:.6f}".format(ext[1]*1000) # type: ignore
         else:
            externalAxisPos += ",E" + str(axisCounter) + " {:.6f}".format(ext[1]) # type: ignore
      # fill up to KUKA default, 
      # result: ",E1 0.0,E2 0.0,E3 0.0,E4 0.0,E5 0.0,E6 0.0}"
      while axisCounter < 6: 
         axisCounter += 1
         externalAxisPos += ",E" + str(axisCounter) + " 0.0"
      externalAxisPos += "}"
      
      # differ target output between joint axis or cartesian coordinates
      if motionTargetType == TargetType.Joint:
         axisCounter = 0
         # set prefix for joint axis output
         dataPrefix = dataJointPrefix
         for joint in joints:
            jointObject:DULPythonJoint = joint[0] # type: ignore
            #mainAxisPos += "," + jointObject.GetName() + " {:.6f}".format(joint[1])
            axisCounter += 1
            mainAxisPos += "A" + str(axisCounter) + " {:.6f}".format(joint[1]) + "," # type: ignore
         # finalize joint axis output trim last character (,) 
         # result: "A1 0.000046,A2 -101.839806,A3 120.979851,A4 -0.000058,A5 30.859955,A6 0.000085"
         mainAxisPos = mainAxisPos[0:-1]
      else:
         # set prefix for cartesian coordinate output
         dataPrefix = dataCartesianPrefix 
         # line up cartesian coordinates, config and turn 
         # result: "X 205.300236,Y -163.326010,Z -29.551006,A 90.120000,B 0.046161,C 134.923097,S2,T34" 
         config = position.GetConfig()
         turn = position.GetTurn()
         mainAxisPos = "X {:.6f}".format(xyz[0]*1000) + ",Y {:.6f}".format(xyz[1]*1000) + ",Z {:.6f}".format(xyz[2]*1000) + ",A {:.6f}".format(angles[2]) + ",B {:.6f}".format(angles[1]) + ",C {:.6f}".format(angles[0]) + "," + config[0] + " " + config[1:] + "," + turn[0] + " " + turn[1:]
      
      # add position data to data file buffer 
      tempData = dataPrefix + mainAxisPos + externalAxisPos
      # Global attrib to allow to easily add custom positions for derived downloaders
      if dataPrefix == dataCartesianPrefix:
         self.CurrentE6POS = tempData
      elif dataPrefix == dataJointPrefix:
         self.CurrentE6AXIS = tempData
      if not self.Tech.SortDat:
         self.AddLineToData(tempData)
      else:
         if dataPrefix == dataCartesianPrefix:
            self.AddLineToDataE6POS(tempData)
         elif dataPrefix == dataJointPrefix:
            self.AddLineToDataE6AXIS(tempData)
      # Reset special naming
      self.SpecialPosName = ''

   def HandleReadAheadEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      """Handle Read Ahead event (After Events to be processed Before motion) e.g. GunOn/Off,GlueOn/Off,ArcOn/Off
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader HandleReadAheadEvent called")
      logger.LogDebug(event.GetName())

   def HandleEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      """Handle event
      
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader HandleEvent called")
      logger.LogDebug(event.GetName())
      
      # handle build in events like speed, accuracy
      self.HandleBuildInEvents(operator, event)
      
      eventMotions = event.GetMotions()
      for eventMotion in eventMotions:
         self.HandleMotion(operator, eventMotion)

   def HandleBuildInEvents(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handle build in events like speed, accuracy, ...

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # check if speed event
      if event.GetName() == 'Speed':
         self.SetSpeed(operator, event)
      # check if accuracy event
      elif event.GetName() == 'Accuracy':
         self.SetAccuracy(operator, event)
      # check if acceleration event
      elif event.GetName() == 'Acceleration':
         self.SetAcceleration(operator, event)
      # text event
      elif event.GetName() == 'TextEvent':
         self.TextEvent(operator, event)
      # dwell event
      elif event.GetName() == 'Dwell':
         self.DwellEvent(operator, event)
      # logic port event
      elif event.GetName() == 'LogicPort':
         self.LogicPortEvent(operator, event)
      # 
      elif event.GetName() == 'SetResourcePort':
         self.LogicPortEvent(operator, event)
      # 
      elif event.GetName() == 'WaitForResourcePort':
         self.LogicPortEvent(operator, event)
      elif event.GetName() == 'SyncRobots':
         self.OutputTeamSyncEvent(event)

   def OutputTeamSyncEvent(self, event: DULPythonEvent):
      """CENE2TeamSync command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      for attribute in event.GetAttributes():
         if attribute.GetName() == 'SyncMode':
            self.SyncMode = attribute.GetValue()
         elif attribute.GetName() == 'SyncText':
            self.SyncText = attribute.GetValue()
      if self.SyncMode == "Handshake":
         # Empty line
         self.Source.append('')
         self.Source.append(';FOLD PROGSYNC '+self.SyncText+' -> 1_2 WAIT ;%{PE}')
         self.Source.append(';FOLD Parameters ;%{h}')
         self.Source.append(';Params IlfProvider=kukaroboter.basistech.inlineforms.roboteam.progsync; SyncLabel='+self.SyncText+'; CoopRobots=R1_R2; Wait=True')
         self.Source.append(';ENDFOLD')
         self.Source.append('SYNCCMD(#ProgSync, "'+self.SyncText+'", 3)')
         self.Source.append(';ENDFOLD')

   def SetSpeed(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set the current speed from speed event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # variable initialization
      pathtype = ''
      speed = 0.0
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get speed value
         if attribute.GetName() == 'Value':
            speed = attribute.GetValue()
         # get path type
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      # check if path type is contour
      if pathtype == 'Contour':
         self.CurrentLinVelocity = float(speed)
      # else path type is point to point
      else:
         self.CurrentPtpVelocity = float(speed)

   def SetAccuracy(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set current accuracy from accuracy event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
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
            else:
               self.CurrentPtpAccuracy = int(accuracy)
      # check if criteria is OFF
      elif criteria == 'Off':
         self.CurrentAccuracyActive = False
      # check if criteria is distance
      elif criteria == 'Distance':
         self.CurrentLinAccuracy = int(accuracy * 1000)
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

   def SetAcceleration(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Set the current acceleration from acceleration event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader SetAcceleration called")
      # variable initialization
      pathtype = ''
      acceleration = 0.0
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for attribute in attributes:
         # get acceleration value
         if attribute.GetName() == 'Value':
            acceleration = attribute.GetValue()
         # get path type
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinAcceleration = int(acceleration * 1000)
      else:
         self.CurrentPtpAcceleration = int(acceleration)

   def TextEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """text event implementation

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader TextEvent called")
      # get all attributes
      attributes = event.GetAttributes()
      # initialize variables
      text = ''
      isComment = True
      # iterate through attributes
      for attribute in attributes:
         # get text
         if attribute.GetName() == 'Text':
            text = attribute.GetValue()
         # get flag is text is a comment (True) or command (False)
         elif attribute.GetName() == 'IsComment':
            isComment = attribute.GetValue()
      # check if comment
      if isComment:
         # create string and add it to source string array
         self.OutputFOLDComment(operator, text)
      else:
         self.AddLineToSource(text)

   def OutputFOLDComment(self, operator: DULPythonDownloadOperator, comment: str, shortCommentFoldStyle = True ):
      """Output a comment in source section of Kuka robot program

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         comment (str): string containing the comment
      """
      # get logger operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputFOLDComment called")
      logger.LogDebug(comment)
      # add comment to source section
      if shortCommentFoldStyle:
         self.AddLineToSource(";FOLD ; " + comment + f";%{{PE}}%R 8.2.24,%MKUKATPBASIS,%CCOMMENT,%VNORMAL,%P 2:" + comment)
         self.AddLineToSource(";ENDFOLD")
      else:
         self.AddLineToSource(";FOLD ; " + comment + f";%{{PE}}")
         self.AddLineToSource("  ;FOLD Parameters ;%{{h}}")
         self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.comments.comment; Kuka.Content=" + comment)
         self.AddLineToSource("  ;ENDFOLD")
         self.AddLineToSource(";ENDFOLD")

   def DwellEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """dwell event implementation

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader DwellEvent called")
      # get all attributes
      attributes = event.GetAttributes()
      # initialize variables
      time = 0.0
      # iterate through attributes
      for attribute in attributes:
         # get dwell time value
         if attribute.GetName() == 'Value':
            time = attribute.GetValue()
      self.AddLineToSource(";FOLD WAIT Time= " + str(time) + " sec ;%{PE}")
      self.AddLineToSource("  ;FOLD Parameters ;%{h}")
      self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.logics.wait; Time=" + str(time))
      self.AddLineToSource("  ;ENDFOLD")
      self.AddLineToSource("  WAIT SEC " + str(time))
      self.AddLineToSource(";ENDFOLD")

   def LogicPortEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """LogicPortEvent event implementation.
      Handles three EventType categories:
        - SetResourcePort / WaitForResourcePort: multi-signal containers
          (attributes repeat in groups: SignalName, SignalAddress, SignalNumber, SignalValue)
        - LogicPort: single signal with subtype dispatch (CENE2SetSignal, etc.)

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader LogicPortEvent called")
      # dispatch on high-level EventType enum
      eventType = event.GetEventType()
      if eventType == EventType.SetResourcePort or eventType == EventType.WaitForResourcePort:
         # ResourcePort events are MULTI-SIGNAL containers:
         # attributes repeat in groups of (SignalName, SignalAddress, SignalNumber, SignalValue)
         signals = []
         currentSignal = {}
         for attribute in event.GetAttributes():
            name = attribute.GetName()
            if name == 'SignalName':
               # start of a new signal group — save previous if complete
               if currentSignal.get('SignalName'):
                  signals.append(currentSignal)
               currentSignal = {'SignalName': attribute.GetValue(), 'SignalAddress': '', 'SignalNumber': '', 'SignalValue': ''}
            elif name == 'SignalAddress':
               currentSignal['SignalAddress'] = attribute.GetValue()
            elif name == 'SignalNumber':
               currentSignal['SignalNumber'] = str(attribute.GetValue())
            elif name == 'SignalValue':
               currentSignal['SignalValue'] = str(attribute.GetValue())
         # don't forget the last signal group
         if currentSignal.get('SignalName'):
            signals.append(currentSignal)
         # output one KRL command per signal
         if eventType == EventType.SetResourcePort:
            for sig in signals:
               self.AddLineToSource("\n;------------ SetResourcePort -----------------")
               self.AddLineToSource(";FOLD OUT " + sig['SignalNumber'] + " '" + sig['SignalName'] + "' State=" + sig['SignalValue'] + "  ;%{PE}")
               self.AddLineToSource("  ;FOLD Parameters ;%{h}")
               self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.logics.out.out; Kuka.Logics.Io=" + sig['SignalNumber'] + "; Kuka.Logics.IoName=" + sig['SignalName'] + "; Kuka.Logics.State=" + sig['SignalValue'] + "; Kuka.Logics.Cont=False")
               self.AddLineToSource("  ;ENDFOLD")
               self.AddLineToSource("  $OUT[" + sig['SignalNumber'] + "] = " + sig['SignalValue'])
               self.AddLineToSource(";ENDFOLD")
         else:  # WaitForResourcePort
            for sig in signals:
               self.AddLineToSource("\n;------------ WaitForResourcePort -----------------")
               waitForFalse = ""
               if sig['SignalValue'] == "False":
                  waitForFalse = "== False "
               self.AddLineToSource(";FOLD WAIT FOR ( IN " + sig['SignalNumber'] + " '" + sig['SignalName'] + "' )  ;%{PE}")
               self.AddLineToSource("  ;FOLD Parameters ;%{h}")
               self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.logics.waitfor; Kuka.WaitLogicTerm1=None; Kuka.WaitForNot1=False; Kuka.WaitLogicOp2.Term1=None; Kuka.WaitForNot2.Term1=False; Kuka.WaitForSysVar2.Term1=IN; Kuka.WaitForIndex2.Term1=" + sig['SignalNumber'] + "; Kuka.WaitForIndexName2.Term1=" + sig['SignalName'] + "; Kuka.WaitForTermNumbers=1; Kuka.WaitForOpNumbers=2; Kuka.WaitForCont=False")
               self.AddLineToSource("  ;ENDFOLD")
               self.AddLineToSource("  WAIT FOR  ( $IN[" + sig['SignalNumber'] + "] " + waitForFalse + ")")
               self.AddLineToSource(";ENDFOLD")
      elif eventType == EventType.LogicPort:
         # LogicPort — single signal with subtype dispatch
         eventSubType = ""
         eventSignalName = ""
         eventSignalNumber = ""
         eventSignalValue = ""
         for attribute in event.GetAttributes():
            currentAttribName = attribute.GetName()
            if currentAttribName == 'EventType':
               eventSubType = attribute.GetValue()
            elif currentAttribName == 'SignalName':
               eventSignalName = attribute.GetValue()
            elif currentAttribName == 'SignalNumber':
               eventSignalNumber = str(attribute.GetValue())
            elif currentAttribName == 'SignalValue':
               eventSignalValue = str(attribute.GetValue())
         # read typed value via specific getter for LogicPort subtypes
         if eventSubType == "CENE2SetSignal":
            eventSignalValue = str(event.GetBoolAttribute("SignalValue",True).GetValue())
            self.AddLineToSource("\n;------------ LogicPort CENE2SetSignal -----------------")
         elif eventSubType == "CENE2SetSignalInt":
            eventSignalValue = str(event.GetIntegerAttribute("SignalValue",True).GetValue())
            self.AddLineToSource("\n;------------ LogicPort CENE2SetSignalInt -----------------")
         elif eventSubType == "CENE2SetSignalShortInt":
            eventSignalValue = event.GetStringAttribute("SignalValue",True).GetValue()
            self.AddLineToSource("\n;------------ LogicPort CENE2SetSignalShortInt -----------------")
         elif eventSubType == "CENE2SetSignalFloat":
            eventSignalValue = str(event.GetDoubleAttribute("SignalValue",True).GetValue())
            self.AddLineToSource("\n;------------ LogicPort CENE2SetSignalFloat -----------------")
         if 'CENE2SetSignal' in eventSubType:
            self.AddLineToSource(";FOLD OUT " + eventSignalNumber + " '" + eventSignalName + "' State=" + eventSignalValue + "  ;%{PE}")
            self.AddLineToSource("  ;FOLD Parameters ;%{h}")
            self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.logics.out.out; Kuka.Logics.Io=" + eventSignalNumber + "; Kuka.Logics.IoName=" + eventSignalName + "; Kuka.Logics.State=" + eventSignalValue + "; Kuka.Logics.Cont=False")
            self.AddLineToSource("  ;ENDFOLD")
            self.AddLineToSource("  $OUT[" + eventSignalNumber + "] = " + eventSignalValue)
            self.AddLineToSource(";ENDFOLD")
         elif eventSubType == "CENE2WaitForSignal":
            self.AddLineToSource("\n;------------ LogicPort WaitForSignal -----------------")
            waitForFalse = ""
            if eventSignalValue == "False":
               waitForFalse = "== False "
            self.AddLineToSource(";FOLD WAIT FOR ( IN " + eventSignalNumber + " '" + eventSignalName + "' )  ;%{PE}")
            self.AddLineToSource("  ;FOLD Parameters ;%{h}")
            self.AddLineToSource("    ;Params IlfProvider=kukaroboter.basistech.inlineforms.logics.waitfor; Kuka.WaitLogicTerm1=None; Kuka.WaitForNot1=False; Kuka.WaitLogicOp2.Term1=None; Kuka.WaitForNot2.Term1=False; Kuka.WaitForSysVar2.Term1=IN; Kuka.WaitForIndex2.Term1=" + eventSignalNumber + "; Kuka.WaitForIndexName2.Term1=" + eventSignalName + "; Kuka.WaitForTermNumbers=1; Kuka.WaitForOpNumbers=2; Kuka.WaitForCont=False")
            self.AddLineToSource("  ;ENDFOLD")
            self.AddLineToSource("  WAIT FOR  ( $IN[" + eventSignalNumber + "] " + waitForFalse + ")")
            self.AddLineToSource(";ENDFOLD")
         else:
            logger.LogError("KukaPythonDownloader LogicPortEvent: SubType not found - event skipped   " + eventSignalName)
      else:
         logger.LogError("KukaPythonDownloader LogicPortEvent: EventType not handled - event skipped")

   def AddLineToHeader(self, newline: str):
      """Add a line to the program header

      Args:
         newline (str): add string line to the header 
      """      
      self.Header.append(newline)

   def AddLineToSourceHeader(self, newline: str):
      """Add a line to the source header

      Args:
         newline (str): add string line to the source header 
      """      
      self.SourceHeader.append(newline)

   def AddLineToSource(self, newline: str):
      """Add a new line to the source section and add the line number optional

      Args:
         newline (str): add string line to the source section
         newLineNumberPrefix (bool, optional): a new line starts with a new number of the line. Defaults to True.
      """
      self.Source.append(newline)

   def AddLineToSourceSuppressed(self, newline: str):
      """Add a new line to the source section and add the line number optional

      Args:
         newline (str): add string line to the source section
         newLineNumberPrefix (bool, optional): a new line starts with a new number of the line. Defaults to True.
      """
      self.SourceSuppressed.append(newline)

   def AddLineToSourceFooter(self, newline: str):
      """Add a new line to the footer section

      Args:
         newline (str): string added to the source footer section
      """
      self.SourceFooter.append(newline)

   def AddLineToDataHeader(self, newline: str):
      """Add a new line to the data header section

      Args:
         newline (str): string added to the data header section
      """      
      self.DataHeader.append(newline)

   def AddLineToData(self, newline: str):
      """Add a new line to the data section

      Args:
         newline (str): string added to the data section
      """      
      self.Data.append(newline)

   def AddLineToDataLDAT(self, newline: str):
      """Add a new line to the LDAT data section

      Args:
         newline (str): string added to the data section
      """      
      self.DataLDAT.append(newline)
      self.CurrentLDAT = newline

   def AddLineToDataFDAT(self, newline: str):
      """Add a new line to the FDAT data section

      Args:
         newline (str): string added to the data section
      """      
      self.DataFDAT.append(newline)
      self.CurrentFDAT = newline

   def AddLineToDataE6POS(self, newline: str):
      """Add a new line to the LDAT data section

      Args:
         newline (str): string added to the data section
      """      
      self.DataE6POS.append(newline)
      self.CurrentE6POS = newline

   def AddLineToDataE6AXIS(self, newline: str):
      """Add a new line to the E6AXIS data section

      Args:
         newline (str): string added to the data section
      """      
      self.DataE6AXIS.append(newline)
      self.CurrentE6AXIS = newline

   def AddLineToDataPDAT(self, newline: str):
      """Add a new line to the PDAT data section

      Args:
         newline (str): string added to the data section
      """      
      self.DataPDAT.append(newline)
      self.CurrentPDAT = newline

   def AddLineToDataFooter(self, newline: str):
      """Add a new line to the footer section

      Args:
         newline (str): string added to the footer section
      """
      self.DataFooter.append(newline)

   def GetDate(self):
      """Get the time string for the header specifically for KUKA_KRC5

      Return:
         Returns the date for KUKA_KRC5 header
      """
      date = datetime.today().strftime('%Y-%m-%d')
      # cut the first two number to fit to KUKA_KRC5 date format
      newDate = date[2:]
      # return current date
      return newDate

   def GetTime(self):
      """Get the time string for the header specifically for KUKA_KRC5
      
      Return:
         Returns the time for KUKA_KRC5 header
      """
      # return current time
      return datetime.today().strftime('%H:%M:%S')

   def ConvertVelocity(self, velocity: float, velocityUnit: str) -> float:
      """Converts the velocity from the specified unit into m/s.

      Args:
         velocity: The target velocity in the specified unit.
         velocityUnit: Given velocity unit ("m/min", "cm/min", or "m/s").

      Returns:
         The converted velocity in mm/s.
      """

      if velocityUnit == "m/min":
         return velocity / 60
      elif velocityUnit == "cm/min":
         return velocity / 600
      elif velocityUnit == "m/s":
         return velocity
      else:
         print("Invalid velocity unit.")

