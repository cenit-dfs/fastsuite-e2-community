"""
COPYRIGHT Cenit AG Q2/2024
   Production ready NeuraRobot downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off            YES
      touch sensing in base frame direction:       NO
      touch sensing in surface direction:          NO
      touch sensing with wire:                     NO
      wire check for touch with wire:              NO
      touch sensing with nozzle:                   NO
      seam search in surface direction:            NO
      seam finding:                                NO
      seam tracking:                               NO
      
      NEURA SSH Remote Access
      User : hrg
      Psw  : 4MiRaelFiN;
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
ensure_module_is_updated('NEURA_LARA_specific') #  <---- Perform module force-reload in order to apply hot changes



#################### CONSTANTS ####################
# name of the download class
DOWNLOAD_CLASS_NAME = "NEURA_LARA_specific"
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

# processTypes
TPPROCESSTYPE_NONE           = 0
TPPROCESSTYPE_PROCESSPOINT   = 1
TPPROCESSTYPE_TEACHINSERT    = 2
TPPROCESSTYPE_PROCESSCURVE   = 3
TPPROCESSTYPE_APPROACH       = 4
TPPROCESSTYPE_RETRACT        = 5
TPPROCESSTYPE_TRACKLINK      = 6
TPPROCESSTYPE_CYCLE          = 7
TPPROCESSTYPE_AUXILIARY      = 8
TPPROCESSTYPE_TOOLCHANGE     = 9
TPPROCESSTYPE_LEADIN         = 10
TPPROCESSTYPE_LEADOUT        = 11
TPPROCESSTYPE_GAP            = 12
TPPROCESSTYPE_EXPLODEDCYCLE  = 13
TPPROCESSTYPE_PROCESSSURFACE = 14
TPPROCESSTYPE_PROCESSINSERT  = 15
TPPROCESSTYPE_VIAPOINT       = 16
TPPROCESSTYPE_TPLINK         = 17
TPPROCESSTYPE_TPLINKVIA      = 18

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

import math
PI = math.pi

class NEURA_LARA_specific(Downloader):
   '''NeuraRobot downloader
   Base robot vendor downloader
   Derived from: Base downloader
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

   JSON_COMMENT = '//'
   FILE_EXTENSION_PY = '.py'
   FILE_EXTENSION_JSON = 'js.py'
   PYTHON_FILE_OUTPUT = 1
   JSON_FILE_OUTPUT = 2
   # Files for output &1 &2
   FILE_OUTPUT = 2

   def __init__(self) -> None:
      '''Class initialization
      '''
      super().__init__()
      self.OnDev = False
      self.OnDevID = False
      #
      self.FileUtil = FileUtility()
      # Robot Name
      self.RobotName = ''
      self.NeuraRobotName = 'rr'
      self.ToolIdName = 'tool_id'
      #
      self.outputPython = False
      self.outputJson = False
      # output file path
      self.OutputFilePathPython = ""
      self.OutputFilePathJson = ""
      # store the program name
      self.ProgramName = ""
      # array to store header content
      self.HeaderPY = []
      #self.HeaderPY.append('# Generic E2 Python Downloader Program for Neura Robots')
      self.HeaderJS = []
      #self.HeaderJS.append('// Generic E2 Json Downloader Program for Neura Robots')
      
      self.PTPinJointsJS = True
      self.LINCIRinJointsJS = False

      #-------------------------------------------------------
      # array to store application Commands with its Positions
      self.CommandsHeaderPY = []
      self.CommandsHeaderPY.append('')
      self.CommandsHeaderPY.append('# _________ PY Command List _________')
      # array to store motion commands
      self.CommandsPY = []
            
      #-------------------------------------------------------
      # array to store application  Positions
      self.PointsHeaderJS = []
      self.PointsHeaderJS.append('')
      #self.PointsHeaderJS.append('%s ----------- JSON POINTS ----------' % self.JSON_COMMENT)
      self.PointsHeaderJS.append('point_dict = {')
      # array to store point coordinates and joints
      self.PointsJS = []
      self.PointsFooterJS = []
      self.PointsFooterJS.append('}')
      self.PointsFooterJS.append('')
      #-------------------------------------------------------
      # array to store intermediate Commands
      self.IntermediateJS = []
      self.IntermediateJS.append('')
      self.IntermediateJS.append('point_names = rr.get_point_names()')
      self.IntermediateJS.append('for point_name, point_data in point_dict.items():')
      self.IntermediateJS.append('    if point_data["type"] == "Cartesian":')
      self.IntermediateJS.append('        if not point_name in point_names:')

      self.IntermediateJS.append('           %s.create_point(name=point_name,' % self.NeuraRobotName)
      self.IntermediateJS.append('              reference_frame_name=point_data.get("Frame"),')
      self.IntermediateJS.append('              target_end_effector_pose=point_data.get("CartesianPose"),')
      self.IntermediateJS.append('              target_joint_angles=point_data.get("JointConfiguration"))')
      
      self.IntermediateJS.append('    elif(point_data["type"] == "Joint"):')
      self.IntermediateJS.append('        if not point_name in point_names:')
      self.IntermediateJS.append('           %s.create_point(name=point_name,' % self.NeuraRobotName)
      self.IntermediateJS.append('              reference_frame_name=point_data.get("Frame"),')
      self.IntermediateJS.append('              target_joint_angles=point_data.get("JointConfiguration"))')
      self.IntermediateJS.append('    point_id = %s.get_pose_id_from_name(point_name)' % self.NeuraRobotName)
      self.IntermediateJS.append('    point_data["ID"] = point_id')
      self.IntermediateJS.append('')
      #-------------------------------------------------------
      # array to store application Commands
      self.CommandsHeaderJS = []
      self.CommandsHeaderJS.append('')
      #self.CommandsHeaderJS.append('%s ----------- JSON COMMANDS ----------' % self.JSON_COMMENT)
      self.CommandsHeaderJS.append('program_data = {')
      # array to store point coordinates and joints
      self.CommandsJS = []
      self.CommandsFooterJS = []
      #-------------------------------------------------------
      # program footer text
      self.FooterPY = []      
      self.FooterJS = []      
      
      self.Logging = None

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
      
      self.ToolResources = []

      # convert Factors for Python Values Output (1=mm/0.001=meters ; 1=degrees/PI/180=radians)
      # note : Motion LIN Values are already in mm
      self.CvrtMeter = 0.001
      self.CvrtMilliM = 1
      self.CvrtDegrs = 1
      self.CvrtRadian = PI / 180.0
      #
      self.JointLinFactorPY = self.CvrtMeter
      self.JointRotFactorPY = self.CvrtRadian
      self.CartesianLinFactorPY = self.CvrtMeter
      self.CartesianRotFactorPY = self.CvrtRadian
      # convert Factors for JSON Values Output
      self.JointLinFactorJS = self.CvrtMeter
      self.JointRotFactorJS = self.CvrtRadian
      self.CartesianLinFactorJS = self.CvrtMeter
      self.CartesianRotFactorJS = self.CvrtRadian

      self.LastOrientation = [0.0, 0.0, 0.0]

      # store the currently used feedrate; expected unit = [%]
      # min = 0; max = 100
      self.CurrentPtpFeedrate = 50
      # store the currently used feedrate; expected unit = [mm/sec]
      self.CurrentLinFeedrate = .1
      self.CurrentRotFeedrate = 360.0
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
      self.CurrentPtpAcceleration = 25
      # store the currently used acceleration; expected unit = [%]
      # min = 0; max = 150
      self.CurrentLinAcceleration = 1000
      self.CurrentRotAcceleration = 573
      # point counter
      self.PointCounter = int(0)
      self.CmdIDCounter = int(0)
      self.PointCounterPTP = int(0)
      self.PointCounterLIN = int(0)
      self.PointCounterCIR = int(0)
      self.CustomAppCounter = int(0)
      self.CompositeCounter = int(0)
      # Uniques for Database
      self.PointUniqueNameExt = '_22222222222222'
      self.StartID = 10220090000
      # DateTime
      self.DateCreated = "14.11.2024   15:38:35"
      self.DateModified = "14.11.2024   15:38:35"

      # string for program header to define used motion groups
      self.UsedGroups = ""

      # NeuraRobot Mechanism
      self.GetMechanismAxes =[]

      # Robots max. Feedrate [mm/s] get from E2
      self.RobotMaxTCPFeedrate = 3999
      # Robots max. Acceleration [mm/s²]
      self.RobotMaxAcceleration = 1999

      self.PtpAccelerationinPercent = True
      self.LinAccelerationinPercent = False
      self.PtpFeedrateinPercent = True
      self.LinFeedrateinPercent = False

      # NeuraRobot Process Command,can be overwritten
      self.ArcOffEventAfterCurrentMotion = False
      self.ArcOnEventAfterCurrentMotion = False

      # ArcWelding 
      self.IsTouchPointCollision = False
      self.IsTouchPointStartApp = False
      self.IsTouchPointRetApp = False
      self.CurrentTSCounter = 0
      self.CurrentTSCount = -1
      self.CurrentTouchID = -1
      self.PreviousTouchID = -1

      self.ArcOnActive = False
      self.ArcOnProgramNumber = 0
      self.CurrentWeaveOnOff = False
      self.CurrentWeaveFrequenz = 0.0
      self.CurrentWeaveWidth = 0.0
      self.CurrentWeaveTime1  = 0.0
      self.CurrentWeaveTime2 = 0.0

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

      self.IsFirstMotion = True
      self.LastMotion = None
      self.CurrentMotion = None
      self.NumberTpes = -1
      self.BundleMotionsJS = True
      self.OutputNewCommandJS = True
      self.OutputNewCommandResetFlagJS = False
      self.FirstCircularFlagJS = True
      self.LastPointOutputJS = ''
      self.PtpAsCartesianDict = {}
      self.LastWasPTP = False
      self.ResetControllerParametersJS = True
      self.ResetGoTilForceParametersJS = True
      self.CustomAppListBefore = []
      self.CustomAppListAfter = []
      self.CustomAppType = "Fronius"
      self.CustomAppTypeIndex = 0
      self.CustomAppEnabled = True

      self.UseComposite = True
      self.CompositeFlag = False
      self.CompositeFlagSet = False
      self.IsCompositeLinear = False
      self.IsCompositeCircular = False
      self.NewFeedrateSetFlag = False
      self.CustomAppFlag = False
      self.CompositeStoreHousePointsPY = []
      self.CompositeStoreHouseDataPY = []
      self.BlanksPY = ''
      self.BlanksJS = ''
      self.Short = False

      self.OpenCompositeSectionFlag = False
      self.OpenMoveOrSubSectionFlag = False
      self.CloseCompositeSectionFlag = False
      self.CloseMoveOrSubSectionFlag = False

   # ========================================================================================
   def doOutput(self, type):
      if type == self.PYTHON_FILE_OUTPUT and (self.FILE_OUTPUT & self.PYTHON_FILE_OUTPUT):
         return True
      if type == self.JSON_FILE_OUTPUT and (self.FILE_OUTPUT & self.JSON_FILE_OUTPUT):
         return True
      return False
   
   def DevLogging(self, info):
      if self.OnDev == True:
         self.Logging.LogInfo(info)

   # ========================================================================================

   def Initialize(self, Operator):
      '''
      Initialize at download begin
      Args:
         operator: download operator
      '''
      controller=Operator.GetController()
      self.Logging = Operator.GetLogOperator()
      
      self.DevLogging("================= " + str(DOWNLOAD_CLASS_NAME) + " Download started =================")
      if self.doOutput(self.PYTHON_FILE_OUTPUT):
         self.DevLogging("Python File will be downloaded.")
         self.outputPython = True
      if self.doOutput(self.JSON_FILE_OUTPUT):
         self.DevLogging("Json File will be downloaded.")
         self.outputJson = True
      
      # create UniqueID for Points
      self.PointUniqueNameExt = '_' + datetime.today().strftime('%Y%m%d%H%M%S')
      self.StartID = int(datetime.today().strftime('%m%d%H%M%S'))
      if self.OnDev == True:
         self.OnDevID = True
      if self.OnDevID == True:
         self.PointUniqueNameExt = '_20250220090000'
         self.StartID = 10220090000

      # "$date": "2025-02-14T09:08:58.262Z"
      ktaTest = os.environ.get("CPOST_TESTLAUF_CENIT", "FALSE")
      #ktaTest = Operator.GetWindowsEnvironmentVariable("CPOST_TESTLAUF_CENIT")
      if ktaTest == "TRUE":
         self.DateCreated = "2025-01-01T10:00:00Z"
         self.DateModified = "2025-01-01T10:00:00Z"
      else:
         self.DateCreated = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
         self.DateModified = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
         
      if self.UseComposite == True:
         self.BundleMotionsJS = True
      
      program=controller.GetActiveProgram()
      self.NumberTpes = 0
      for opGroup in program.GetOperationGroups():
         for operation in opGroup.GetOperations():
            tpes = operation.GetTPElements()
            self.NumberTpes += operation.GetNumberTPElements()
            # for tpe in tpes:
            #    self.DevLogging("..........Name TPE = " + str(tpe.GetName()))
            #    self.DevLogging(".............ProcessType = " + str(tpe.GetProcessType()))
            #    self.DevLogging(".............MotionType = " + str(tpe.GetMotionType()))
            #    self.DevLogging(".............TargetType = " + str(tpe.GetTargetType()))
            #    self.DevLogging(".............XYZ Coords = " + str(tpe.GetXYZ()))
            self.DevLogging("....Number of ToolPathElements = " + str(self.NumberTpes))
            self.DevLogging("....ArraySize ToolPathElements = " + str(len(tpes)) + "   excl. ViaP")
            self.DevLogging("-----------------------------")
            
      resources=controller.GetResources()
      # get max. Feedrate
      self.DevLogging("......Default max. Feedrate = " + str(self.RobotMaxTCPFeedrate))
      for resource in resources:
         
         if int(resource.GetItemType()) == 4 and int(resource.GetItemSubType()) ==5:
            self.ToolResources.append(resource)
         if int(resource.GetItemType()) == 1 and int(resource.GetItemSubType()) ==1:
            self.RobotMaxTCPFeedrate = resource.GetMaxSpeed() / self.CvrtMeter
            self.RobotMaxAcceleration = resource.GetMaxAcceleration() / self.CvrtMeter
            self.DevLogging("....Robot new max. Feedrate = " + str(self.RobotMaxTCPFeedrate))
            self.DevLogging("....Robot MaxAcceleration = " + str(self.RobotMaxAcceleration))
            # self.DevLogging("....Robot MaxDeceleration = " + str(resource.GetMaxDeceleration()))
            # self.DevLogging("....Robot KinematicType = " + str(resource.GetKinematicTypeAsString()))
      
      # motionProfiles=controller.GetMotionProfiles()
      # self.DevLogging(".... found motionProfiles = " + str(len(motionProfiles)))
      # for motionProfile in motionProfiles:
      #    self.DevLogging("................GetSpeedValue = " + str(motionProfile.GetSpeedValue()))
      # accuProfiles=controller.GetAccuracyProfiles()
      # self.DevLogging(".... found accuProfiles = " + str(len(accuProfiles)))
      # for accuProfile in accuProfiles:
      #    self.DevLogging("................GetAccuracyCriteria = " + str(accuProfile.GetAccuracyCriteria()))

   # --------------------------------------------------
   def ProgramStart(self, operator, program):
      '''
      Program start   
      Args:
         operator: download operator
         program: access to the program
      '''
      self.Logging.LogDebug("SimplePython ProgramStart called")
      self.Logging.LogDebug(program.GetName())
      
      programAttributes = program.GetAttributes()
      for attrib in programAttributes:
         if attrib.GetName() == 'CustomAppType':
            self.CustomAppType=attrib.GetValue()
            self.CustomAppTypeIndex = self.setWeldEffectorIndex(self.CustomAppType)
            self.DevLogging("....found for Custom App = " + str(self.CustomAppType) + " with Index " + str(self.CustomAppTypeIndex))

      self.CommandsHeaderJS.append('    "tools": [')
      self.CommandsHeaderJS.append('        %s' % (self.ToolIdName))
      self.CommandsHeaderJS.append('    ],')
      self.CommandsHeaderJS.append('    "tree": [')

   # --------------------------------------------------
   def OperationStart(self, operator, operation):
      '''Operation start   
      Args:
         operator: download operator
         operation: access to the operation
      '''
      # Add operation name
      #operationName = ["# pOperation " + operation.GetName(), "# jOperation " + operation.GetName()]
      operationName = []
      # Output for Python
      operationName.append("# Operation " + operation.GetName())
      # Output for JSON
      operationName.append("")
      # pass Line-List [P,J]
      self.AddLineToCommands(operationName)
      
      self.LastOrientation = [0.0, 0.0, 0.0]

   # --------------------------------------------------
   def CreateHeader(self, operator):
      '''Create program header.
      Separated function, because some information doesn't exist at the beginning

      Args:
         operator: download operator
      '''
      # get controller
      controller = operator.GetController()
      # Get Resource Attributes
      resources=controller.GetResources()
      for resource in resources:
         if int(resource.GetItemType()) == 1 and int(resource.GetItemSubType()) ==1:
            self.RobotName = resource.GetName()
      
      # passing Line-List [P,J]
      self.AddLineToHeader(['# Generic E2 Python Downloader for Neura Robots', ''])
      self.AddLineToHeader(['# =============================================', ''])
      self.AddLineToHeader(['# Downloader : %s' % DOWNLOAD_CLASS_NAME, ''])
      self.AddLineToHeader(['# Robot : %s' % self.RobotName, ''])
      self.AddLineToHeader(['# Comment : ', ''])
      self.AddLineToHeader(['# Created : %s' % self.DateCreated, ''])
      self.AddLineToHeader(['# Updated : %s' % self.DateModified, ''])
      self.AddLineToHeader(['\n', ''])
      self.AddLineToHeader(['from time import sleep', 'import requests'])
      self.AddLineToHeader(['', 'import json'])
      self.AddLineToHeader(['from neurapy.robot import Robot', 'from neurapy.robot import Robot'])
      #self.AddLineToHeader(['', ''])
      self.AddLineToHeader(['%s = Robot()' % self.NeuraRobotName, '%s = Robot()' % self.NeuraRobotName])
      self.AddLineToHeader(['\n', ' '])
      self.AddLineToHeader(['', 'api_url = f"http://{%s.kURL}:8081/api/programs"' % self.NeuraRobotName])
      self.AddLineToHeader(['', ' '])
      self.AddLineToHeader(['%s.power_on()' % self.NeuraRobotName, ''])
      self.AddLineToHeader([' ', ''])
      self.AddLineToHeader(['%s.switch_to_semi_automatic_mode()' % self.NeuraRobotName, ''])
      self.AddLineToHeader(['%s.init_program()' % self.NeuraRobotName, ''])
      # only Python here
      for tool in self.ToolResources:
         toolName = tool.GetName()
      self.AddLineToHeader(['%s.set_tool(tool_name="%s")' % (self.NeuraRobotName, toolName), ''])
      # this for JSON
      for tool in self.ToolResources:
         toolName = tool.GetName()
         toolProfiles = controller.GetToolProfiles()
         for toolProfile in toolProfiles:
            self.OutputToolDefinition(toolProfile, toolName)

   # ------------ end of header -------------------------------------------------
      
   def OutputToolDefinition(self, toolProfile, toolName):
      position = toolProfile.GetXYZ()
      orientation = toolProfile.GetOrientation()
      tempJS = ''
      tempJS += '# "DateTime" : "%s"\n\n' % (self.DateCreated)
      tempJS += '\ntool_list = %s.get_tools()\n' % (self.NeuraRobotName)
      tempJS += 'tool_Exist = False\n'
      tempJS += 'for tool in tool_list:\n'
      tempJS += '   if tool["name"] == "%s":\n' % (toolName)
      tempJS += '      tool_Exist = True\n'
      tempJS += 'if tool_Exist == False:\n'
      if 1 == 2:
         tempJS += '    %s.create_tool("%s",tool_data={})\n' % (self.NeuraRobotName, toolName)
      else:
         tempJS += self.CreateToolData(orientation, position, toolName) + '\n'
         tempJS += '    success = %s.create_tool(tool_data)\n' % (self.NeuraRobotName)

      #tempJS += '#%s = %s.get_tool_id_in_gui("%s")' % (self.ToolIdName, self.NeuraRobotName, toolName)
      #tempJS += '\n%s = "67efd6aaf98bc009fc1b4064"' % (self.ToolIdName)

      tempJS += '\ntool_list = %s.get_tools()\n' % (self.NeuraRobotName)
      tempJS += 'for tool in tool_list:\n'
      tempJS += '   if tool["name"] == "%s":\n' % (toolName)
      tempJS += '      tool_id = tool["_id"]\n'
      tempJS += '%s.set_tool(tool_name="%s")' % (self.NeuraRobotName, toolName)

      self.AddLineToHeader(['', tempJS])
   # --------------------------------------------------

   def CreateToolData(self, orientation, position, toolName):
      '''write Tool_Data for a DB-non-existing Tool'''
      tempJS = ''
      blanks = '    '
      tempJS += blanks  + 'tool_data = {\n'
      tempJS += blanks  + '"_controlOA": False,\n'
      tempJS += blanks  + '"_controlOD": False,\n'
      tempJS += blanks  + '"_toolOA": False,\n'
      tempJS += blanks  + '"_toolOD": False,\n'
      tempJS += blanks  + '"autoM": 0,\n'
      tempJS += blanks  + '"autoMeasureX": 0,\n'
      tempJS += blanks  + '"autoMeasureY": 0,\n'
      tempJS += blanks  + '"autoMeasureZ": 0,\n'
      tempJS += blanks  + '"closeInput": 0,\n'
      tempJS += blanks  + '"cmdID": 16,\n'
      tempJS += blanks  + '"description": "Cenit Tool Description",\n'
      tempJS += blanks  + '"force": 0,\n'
      tempJS += blanks  + '"gripper": "",\n'
      tempJS += blanks  + '"grippertype": "Standard Gripper",\n'
      tempJS += blanks  + '"inertiaXX": 0,\n'
      tempJS += blanks  + '"inertiaXY": 0,\n'
      tempJS += blanks  + '"inertiaXZ": 0,\n'
      tempJS += blanks  + '"inertiaYY": 0,\n'
      tempJS += blanks  + '"inertiaYZ": 0,\n'
      tempJS += blanks  + '"inertiaZZ": 0,\n'
      tempJS += blanks  + '"name": "%s",\n' % (toolName)
      tempJS += blanks  + '"offCOA": [0, 0, 0, 0, 0, 0, 0, 0],\n'
      tempJS += blanks  + '"offCOD1": 0,\n'
      tempJS += blanks  + '"offCOD2": 0,\n'
      tempJS += blanks  + '"offTOA": [0, 0],\n'
      tempJS += blanks  + '"offTOD": 0,\n'
      tempJS += blanks  + '"offsetA": %.6f,\n' % (orientation[0]*self.CvrtRadian)
      tempJS += blanks  + '"offsetB": %.6f,\n' % (orientation[1]*self.CvrtRadian)
      tempJS += blanks  + '"offsetC": %.6f,\n' % (orientation[2]*self.CvrtRadian)
      tempJS += blanks  + '"offsetX": %.6f,\n' % (position[0])
      tempJS += blanks  + '"offsetY": %.6f,\n' % (position[1])
      tempJS += blanks  + '"offsetZ": %.6f,\n' % (position[2])
      tempJS += blanks  + '"onCOA": [0, 0, 0, 0, 0, 0, 0, 0],\n'
      tempJS += blanks  + '"onCOD1": 0,\n'
      tempJS += blanks  + '"onCOD2": 0,\n'
      tempJS += blanks  + '"onTOA": [0, 0],\n'
      tempJS += blanks  + '"onTOD": 0,\n'
      tempJS += blanks  + '"openInput": 0,\n'
      tempJS += blanks  + '"portID": "",\n'
      tempJS += blanks  + '"protocol": 0,\n'
      tempJS += blanks  + '"robot_type": "Tool",\n'
      tempJS += blanks  + '"slaveID": 0,\n'
      tempJS += blanks  + '"speed": 0\n'
      tempJS += blanks  + '}'
      return tempJS
   # --------------------------------------------------
   def ProgramEnd(self, Operator, program):
      '''
      Program end   
      Args:
         operator: download operator
         program: access to the program
      '''
      self.FooterPY.append('\n')
      if self.UseComposite == True:
         self.FooterPY.append('%s.stop()' % self.NeuraRobotName)
      self.FooterPY.append('%s.power_off()' % self.NeuraRobotName)
      # ------------------------------------
      if self.BundleMotionsJS == True:
         self.HandleLastBundledItem()        # Remove the Comma from the last Point of bundled Points
         self.CommandsFooterJS.append(self.CloseCommandsCommonJS())
      
      #self.CommandsFooterJS.append('           ]\n        }') #----------------!!!!!!!!dev
      
      self.CommandsFooterJS.append('    ],')
      self.CommandsFooterJS.append('    "isCompleted": False,')
      #self.CommandsFooterJS.append('    "localPoints": [')
      #self.CommandsFooterJS.append('    ],')
      self.CommandsFooterJS.append('    "name": "%s",' % program.GetName())
      self.CommandsFooterJS.append('    "description": ""')
      #"description": "",
      # self.CommandsFooterJS.append('    "createdAt": {')
      # self.CommandsFooterJS.append('        "$date": "%s"' % self.DateCreated)
      # self.CommandsFooterJS.append('    },')
      # self.CommandsFooterJS.append('    "updatedAt": {')
      # self.CommandsFooterJS.append('        "$date": "%s"' % self.DateModified)
      # self.CommandsFooterJS.append('    },')
      # self.CommandsFooterJS.append('    "__v": 0')
      self.CommandsFooterJS.append('}')
      self.CommandsFooterJS.append('# "DateTime" : "%s"' % self.DateCreated)
      self.FooterJS.append('\n')
      #self.FooterJS.append('#Finalize Program')
      self.FooterJS.append('headers = {')
      self.FooterJS.append('    "Content-Type": "application/json"')
      self.FooterJS.append('}')
      self.FooterJS.append('')
      self.FooterJS.append('#Add the Program to the database')
      self.FooterJS.append('response = requests.post(api_url, data=json.dumps(program_data), headers=headers)')
      self.FooterJS.append('')
      self.FooterJS.append('# Check the response')
      self.FooterJS.append('if response.status_code == 200:')
      self.FooterJS.append('    print("Program data successfully posted!")')
      self.FooterJS.append('    print("Response:", response.json())')
      self.FooterJS.append('else:')
      self.FooterJS.append('    print(f"Failed to post program data. Status code: {response.status_code}")')
      self.FooterJS.append('    print("Response:", response.text)')

   # --------------------------------------------------
   def HandleMotion(self, operator, motion):
      '''
      Evaluation of toolpath elements and events
      Args:
         operator: download operator
         motion: current motion
      '''
      self.DevLogging('- - - - Motion : ' + str(motion.GetName()))
      # handle events, inserted before. Do not handle events which to change toolpath element output
      eventsBefore = motion.GetEventsBefore()
      # iterate through events
      for event in eventsBefore:
         self.DevLogging(".....................found before Event : " + event.GetName() +  "  ,  " + str(event. GetInsertPosition())[15:27])
         self.HandleEvent(operator, motion, event)
      
      # Check if motion has ARC OFF or ARC ON Event after (which influences Motion output)
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         if event.GetName() == 'ArcOffEvent':
            self.ArcOffEventAfterCurrentMotion = True
         elif event.GetName() == 'ArcOnEvent':
            self.ArcOnEventAfterCurrentMotion = True
      mName = motion.GetName()
      # #################################################
      # handle source section of the motion
      self.HandleCommandsSection(operator, motion)
      # handle data section of the motion
      self.HandlePointsSection(operator, motion)
      # #################################################

      # handle events, inserted after. Do not handle events which to change toolpath element output
      eventsAfter = motion.GetEventsAfter()
      for event in eventsAfter:
         self.DevLogging(".....................found after Event : " + event.GetName() +  "  ,  " + str(event. GetInsertPosition())[15:27])
         self.HandleEvent(operator, motion, event)

   # --------------------------------------------------
   def HandleEvent(self, operator, currentMotion, event):
      '''
      Handle event
      Args:
         operator: download operator
         event: access to the event object
      '''
      self.CurrentMotion = currentMotion
      # handle build in events like speed, accuracy
      self.HandleBuildInEvents(operator, event)
      # output Event
      self.OutputEvent(operator, event)
     # get motions of the event
      motions = event.GetMotions()
      # handle each motion of the event
      for motion in motions:
         self.HandleMotion(operator, motion)

   # --------------------------------------------------
   def OutputEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """
      Output event
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes      
      """
      self.DevLogging("............................output Event = " + str(event.GetName()))
      if event.GetName() == 'TouchPointStartAppEvent':
         self.IsTouchPointStartApp = True
         self.skipSourceMotion = True          
      if event.GetName() == 'TouchPointCollisionEvent':
         self.IsTouchPointCollision = True
         self.skipSourceMotion = True
         self.suppressBCECOutput = True
         #self.AddLineToCommands(['OUT O1#(8:O1#008)=ON', 'OUT O1#(8:O1#008)=ON'])         
         #self.AddLineToCommands(['TCHSNS, 0.9', 'TCHSNS, 0.9'])
      if event.GetName() == 'TouchPointStartRetEvent':
         self.IsTouchPointRetApp = True
         self.skipSourceMotion = True  
         #self.AddLineToCommands(['SNSSFTLD, GD#(1:GD001)','SNSSFTLD, GD#(1:GD001)'])
         #self.AddLineToCommands(['OUT O1#(8:O1#008)=OFF', 'OUT O1#(8:O1#008)=OFF'])  
      if event.GetName() == 'ConnectTouchProcessPointEvent':
         #self.SetConnectionID(operator,event)
         self.CurrentTouchID = int(event.GetAttributes()[0].GetValue())
         #self.AddLineToCommands(['# TOUCHID'+str(self.CurrentTouchID), '# TOUCHID'+str(self.CurrentTouchID)])
      if event.GetName() == 'ArcOnEvent':
         self.OutputArcOnEvent(event)
      if event.GetName() == 'ArcOffEvent':
         self.OutputArcOffEvent(event)
      
   # --------------------------------------------------
   def OutputArcOnEvent(self, event: DULPythonEvent):
      """
      Arc on command
      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      #return
      
      for att in event.GetAttributes():
         if att.GetName() == 'ProgNumber':
            self.ArcOnProgramNumber = att.GetValue()
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
         self.DevLogging("..................................ArcOnEvent Attr.Name = " + str(att.GetName()) + " = " + str(att.GetValue()))
   
      self.ArcOnActive == True
      # -------- Python Output ----------
      #self.CommandsPY.append("# ---- ARC ON ----")
      processPY = '# ---- ARC ON ----'
      parametersPY =[]
      # -------- JSON Output ----------
      self.OutputNewCommandResetFlagJS = True
      self.CompositeFlag = False
      self.NewFeedrateSetFlag = False
      processJS = self.CustomAppType + '.json' # 'Fronius.json'   #  'ArcOnTest.json'
      parametersJS =[]
      parametersJS.append(['Job Number', '%s' %(str(self.ArcOnProgramNumber))])
      parametersJS.append(['Simulation', 'True'])
      self.CustomAppEnabled = True
      self.WriteAndStoreCustomApp(processPY, parametersPY, processJS, parametersJS)

   # --------------------------------------------------
   def OutputArcOffEvent(self, event: DULPythonEvent):
      """Arc off command

      Args:
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      #return

      # !! no Attributes
      for att in event.GetAttributes():
         if att.GetName() == 'ProgNumber':
            self.ArcOnProgramNumber = att.GetValue()
         self.DevLogging("..................................ArcOffEvent Attr.Name = " + str(att.GetName()) + " = " + str(att.GetValue()))

      self.ArcOnActive = False
      self.CurrentWeaveOnOff = False

      # -------- Python Output ----------
      # self.CommandsPY.append("# ---- ARC OFF ----")
      processPY = '# ---- ARC OFF ----'
      parametersPY =[]
      # -------- JSON Output ----------
      self.OutputNewCommandResetFlagJS = True
      self.CompositeFlag = False
      self.NewFeedrateSetFlag = False
      processJS = self.CustomAppType + '.json' # 'Fronius.json'   #  'ArcOffTest.json'
      parametersJS =[]
      parametersJS.append(['Job Number', '%s' %(str(self.ArcOnProgramNumber))])
      parametersJS.append(['Simulation', 'True'])
      self.CustomAppEnabled = False
      self.WriteAndStoreCustomApp(processPY, parametersPY, processJS, parametersJS)

   # --------------------------------------------------
   def WriteAndStoreCustomApp(self, processPY, parametersPY, processJS, parametersJS):
      '''
      Stores a Custom App for any Functionallity in a global before/after List for later Output
      Args:
         process : the name of the required Script
         parameters : a List of String-Pairs with desired Parameters "Name":"Value"\n
         e.g.\n
         parameters =[]\n
         parameters.append(['Job Number', '123'])\n
         parameters.append(['Simulation', 'true'])
      '''
      retstrPY = ''
      retstrPY += processPY
      
      self.CustomAppCounter += 1
      self.CmdIDCounter += 1
      filepath = '/home/hrg/data/process/%s' % (processJS)
      
      retstrJS = ''
      retstrJS += '        {\n'
      retstrJS += '            "id": %s,\n' % (self.StartID + self.CmdIDCounter)
      retstrJS += '            "type": "CustomApp",\n'
      retstrJS += '            "payload": {\n'
      retstrJS += '            "name": "ca_%03d",\n' % self.CustomAppCounter
      retstrJS += '            "enabled": %s,\n' % self.CustomAppEnabled
      retstrJS += '            "description": "",\n'
      retstrJS += '            "process": "%s",\n' % processJS
      retstrJS += '            "process_config": "Job Mode",\n'
      if len(parametersJS):
         retstrJS += '            "parameters": {\n'
         for param in parametersJS:
            retstrJS += '                "%s": %s,\n' % (param[0], param[1])
         retstrJS = retstrJS[:-2] # cut the last Comma (bec. Loop)
         retstrJS += '\n'
         retstrJS += '               },\n'
      retstrJS += '            "filepath": "%s",\n' % filepath
      retstrJS += '            },\n'
      retstrJS += '            "children": []\n'
      retstrJS += '        },'
      
      #retstrJS = processPY + '\n'   # ! ! ! ! ! ! ! ! ! only Comment for JSON (dev)
      self.CustomAppListAfter.append([retstrPY, retstrJS])
      self.CustomAppFlag = True

   # --------------------------------------------------
   def OutputCustomApp(self, after):
      '''
      Outputs a previously stored Custom App for any Functionallity from a global before/after List
      Args:
         after : bool which List (before/after) should be taken
      '''
      if after == True:
         if len(self.CustomAppListAfter):
            for app in self.CustomAppListAfter:
               appStr = [app[0], app[1]]
               # pass Line-List [P,J]
               self.AddLineToCommands(appStr)
            self.CustomAppListAfter = []
      else:
         if len(self.CustomAppListBefore):
            for app in self.CustomAppListBefore:
               appStr = [app[0], app[1]]
               # pass Line-List [P,J]
               self.AddLineToCommands(appStr)
            self.CustomAppListBefore = []

   # --------------------------------------------------
   def HandleBuildInEvents(self,operator, event):
      '''Handle build in events like speed, accuracy, ...

      Args:
         operator: download operator
         event: access to the event object
      '''
      self.DevLogging("............................output BuildInEvent = " + str(event.GetName()))
      # check if speed event
      if event.GetName() == 'Speed':
         self.setSpeed(event)
      # check if accuracy event 
      elif event.GetName() == 'Accuracy':
          self.SetAccuracy(operator, event)
      # check if acceleration event
      elif event.GetName() == 'Acceleration':
         self.SetAcceleration(operator, event)
      # # text event
      # elif event.GetName() == 'Text':
      #    self.OutputTextEvent(operator, event)
      # dwell event
      elif event.GetName() == 'Dwell':
         self.OutputDwellEvent(event)
      # set signal event
      elif event.GetName() == 'LogicPort':
         self.setLogicPort(event)
      elif event.GetName() == 'SyncRobots':
         self.SetSyncRobotsEvent(event)
      # # wait for signal event
      # elif event.GetName() == 'WaitForSignalBool':
      #    self.OutputWaitForSignalBoolEvent(operator, event)
      pass

   # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
   def HandleCommandsSection(self, operator, motion):
      '''
      '''
      # contains the string of one source line.
      commandSection = []
      # check if motion pre processing necessary and if the normal/general motion output must be skipped
      isRef = motion.IsReferenceMotion()
      self.PointCounter += 1
      self.OutputNewCommandJS = True
      self.FirstCircularFlagJS = True
      # -------------------------------------------------------------------------------------
      # set Flags in Case of / for Composite Output
      # compositeEnd = False
      # if self.UseComposite == True:
      #    compositeEnd = False
      #    # Composite only for PROCESSCURVE
      #    if int(motion.GetPosition().GetProcessType()) == TPPROCESSTYPE_PROCESSCURVE:
      #       if self.CompositeFlag == False:
      #          self.OutputNewCommandResetFlagJS = True   # force new Command
      #       if self.CompositeFlag == False and self.CompositeFlagSet == True:
      #          compositeEnd = True  # if already in a Composite and new Command needed, close old Composite
      #       if self.NewFeedrateSetFlag == True:
      #          self.OutputNewCommandResetFlagJS = True
      #          compositeEnd = False # only force a new Children if Speed changed
      #       self.CompositeFlag = True
      #    # else if Composite was active, close it
      #    elif int(motion.GetPosition().GetProcessType()) != TPPROCESSTYPE_PROCESSCURVE and self.CompositeFlagSet == True:
      #       compositeEnd = True  # if Composite is open and this TPE isn't a ProcCurve anymore
         
      # else:
      #    self.CompositeFlag = False   # don´t do Composite
      #    self.CompositeFlagSet = False
      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
      # set Flags in Case of / for Composite Output
      
      compositeEnd = False
      if self.UseComposite == True:
         compositeEnd = False
         # Composite only for PROCESSCURVE

         if int(motion.GetPosition().GetProcessType()) == TPPROCESSTYPE_PROCESSCURVE:
            if self.CompositeFlag == False:
               self.OutputNewCommandResetFlagJS = True   # force new Command
            # -------------------------------------------
            if self.CompositeFlag == False and self.CompositeFlagSet == True:
               compositeEnd = True  # if already in a Composite and new Command needed, close old Composite
            # -------------------------------------------
            if self.NewFeedrateSetFlag == True:
               self.OutputNewCommandResetFlagJS = True
               compositeEnd = False # only force a new Children if Speed changed
            # -------------------------------------------
            if self.CustomAppFlag == True:
               self.OutputNewCommandResetFlagJS = True
               compositeEnd = True # only force a new Composite
            # -------------------------------------------
            self.CompositeFlag = True
         # else if Composite was active, close it
         elif int(motion.GetPosition().GetProcessType()) != TPPROCESSTYPE_PROCESSCURVE and self.CompositeFlagSet == True:
            compositeEnd = True  # if Composite is open and this TPE isn't a ProcCurve anymore
            self.CompositeFlag = False
            self.OutputNewCommandResetFlagJS = True   # force new Command
         
         aaa = motion.GetName()
         closeStr = '         # ' + str(aaa) 
         closeStr += '  PT=' + str(int(motion.GetPosition().GetProcessType()))
         closeStr += '  self.CompositeFlag=' + str(self.CompositeFlag)
         closeStr += '  self.CompositeFlagSet=' + str(self.CompositeFlagSet) 
         closeStr += ' |ppp'
         #self.AddLineToCommands(['', closeStr])
         # -------------------------------------------
      else:
         self.CompositeFlag = False   # don´t do Composite
         self.CompositeFlagSet = False
      # -------------------------------------------------------------------------------------

      # check if the motion is a reference motion or if the motion was already processed
      if not isRef and not self.SkipSourceMotion:
         
         if self.BundleMotionsJS == False:
            # output Custom App before (if unbundled)
            self.OutputCustomApp(False)
         
         # check if motion is of type linear
         if motion.IsLinearMotion():
            # check for "bundled Motions" if Command Settings kept (IF,just add the Point) or if a new CommandSection is required (ELSE, perform new Command)
            if self.LastMotion != None and self.LastMotion.IsLinearMotion() and self.BundleMotionsJS == True and self.OutputNewCommandResetFlagJS == False:
               self.OutputNewCommandJS = False
            else:
               # close current Section before performing a new Command
               self.ClosePreviousSection(compositeEnd)
               self.PointCounterLIN += 1
            # create LIN source string (Line-List [P,J])
            commandSection = self.OutputCommandsLin(operator, motion)
            # pass Line-List [P,J]
            self.AddLineToCommands(commandSection)

         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # check for "bundled Motions" if Command Settings kept (IF,just add the Point) or if a new CommandSection is required (ELSE, perform new Command)
            if self.LastMotion != None and self.LastMotion.IsCircularMotion() and self.BundleMotionsJS == True and self.OutputNewCommandResetFlagJS == False:
               self.OutputNewCommandJS = False
               self.FirstCircularFlagJS = False
            else:
               # close current Section before performing a new Command
               self.ClosePreviousSection(compositeEnd)
               self.PointCounterCIR += 1
            self.PointCounter += 1 # upcount for VIA
            # create CIRC source string (Line-List [P,J])
            commandSection = self.OutputCommandsCirc(operator, motion)
            # pass Line-List [P,J]
            self.AddLineToCommands(commandSection)

         # check if the motion is of type point to point
         else:
            # check for "bundled Motions" if Command Settings kept (IF,just add the Point) or if a new CommandSection is required (ELSE, perform new Command)
            if self.LastMotion != None and self.LastMotion.IsPtPMotion() and self.BundleMotionsJS == True and self.OutputNewCommandResetFlagJS == False:
               self.OutputNewCommandJS = False
            else:
               # close current Section before performing a new Command
               self.ClosePreviousSection(compositeEnd)
               self.PointCounterPTP += 1
            # create PTP source string (Line-List [P,J])
            commandSection = self.OutputCommandsPtp(operator, motion)
            # pass Line-List [P,J]
            self.AddLineToCommands(commandSection)
         
         # output Custom App after (if unbundled)
         self.OutputCustomApp(True)

         # reset skip source creation
         self.SkipSourceMotion = False
         # reset Look ahead Arc ON/Off
         self.ArcOnEventAfterCurrentMotion = False
         self.ArcOffEventAfterCurrentMotion = False
         self.OutputNewCommandResetFlagJS = False
         self.NewFeedrateSetFlag = False
         self.CustomAppFlag = False

   # --------------------------------------------------
   def ClosePreviousSection(self, compositeEnd):
      '''close current Section before performing a new Command'''
      if self.BundleMotionsJS == True and self.LastMotion != None:
         if self.LastWasPTP != True:
            self.HandleLastBundledItem()        # Remove the Comma from the last Point of bundled Points
         closeStr = ['', self.CloseCommandsCommonJS()]    # close the Section
         self.AddLineToCommands(closeStr)    # pass Line-List [P,J]
         self.CloseCompositeSection(compositeEnd)     # close the Composite if neccessary
         self.OutputCustomApp(True)    # output Custom App after (if bundled)
   # --------------------------------------------------
   def HandleLastBundledItem(self):
      '''Remove the Comma from the last Point of bundled Points'''
      lastPoint = self.CommandsJS[-1]
      self.CommandsJS.pop()
      lastPoint = lastPoint[:-1]
      self.CommandsJS.append(lastPoint)
   # --------------------------------------------------
   def ControlCompositeSectionOutputPY(self):
      '''Switch on and off Condition for Composite Output'''
      retstrPY = ''
      lastType = ''
      
      # self.CompositeStoreHousePointsPY = ['cartX, cartY, ...']
      # self.CompositeStoreHouseDataPY = ['LIN/CIR', accur.Val, 'P001']
      if len(self.CompositeStoreHousePointsPY):
         type = self.CompositeStoreHouseDataPY[0][0]
         accuracy = self.CompositeStoreHouseDataPY[0][1]
         if type == 'CIR':
            retstrPY += '            "circular": {\n'
         else:
            retstrPY += '            "linear": {\n            "blend_radius": %.4f,\n' % (accuracy * 0.001)
         retstrPY += '            "targets": [\n'
      else:
         return "# COULD NOT CREATE COMPOSITE SECTION"
      lastType = type
      iC = 0
      for line in self.CompositeStoreHousePointsPY:
         type = self.CompositeStoreHouseDataPY[iC][0]
         accuracy = self.CompositeStoreHouseDataPY[iC][1]
         pname = self.CompositeStoreHouseDataPY[iC][2]
         #retstrPY += '# ' + type + '\n'
         iC += 1
         # if the Type changes LIN->CIR / CIR->LIN
         if type != lastType:
            retstrPY = retstrPY[:-2]
            retstrPY += '\n            ]\n'
            retstrPY += '            }\n'
            retstrPY += '         },\n'
            retstrPY += '         {\n'
            if type == 'CIR':
               retstrPY += '            "circular": {\n'
            else:
               retstrPY += '            "linear": {\n            "blend_radius": %.4f,\n' % (accuracy * 0.001)
            retstrPY += '            "targets": [\n'
         #retstrPY += '               # ' + pname + '\n'
         retstrPY += line
         if iC < len(self.CompositeStoreHousePointsPY):
            retstrPY += ',' # if not the End ","
         retstrPY += '\n'
         lastType = type
      retstrPY += '            ]\n'
      retstrPY += '            }\n'
      # empty the StoreHouse for next Composite
      self.CompositeStoreHousePointsPY = []
      self.CompositeStoreHouseDataPY = []

      return retstrPY
   # --------------------------------------------------
   def CloseCompositeSection(self, close):
      '''Closes the Composite-Section and format the Points-Sections(for Python)'''
      if close == True:
         tmpPY = ''
         tmpPY += self.ControlCompositeSectionOutputPY()
         tmpPY += '      }\n   ]\n}\n'
         tmpPY += '%s.move_composite(**composite_motion_property)\n' % (self.NeuraRobotName)
         tmpPY += '# ------------ Composite END --------------*\n'

         tmpJS = '            ]\n'
         tmpJS += '        },  # end of composite\n'
         tmpJS += '        # ------------ Composite END --------------*\n'
         closeStr = [tmpPY, tmpJS]
         self.AddLineToCommands(closeStr)
         self.CompositeFlagSet = False
         self.IsCompositeLinear = False
         self.IsCompositeCircular = False
         self.BlanksJS = ''
   # --------------------------------------------------
   def OutputCommandsPtp(self, operator, motion):
      '''Output point to point motion
      J P[1] 50% FINE ACC80;

      Args:
         operator: download operator
         motion: current motion
      '''
      retstrPY = ''
      retstrJS = ''

      # Output for Python
      retstrPY = self.OutputCommandsCommonPY(operator, motion)

      # Output for JSON
      if self.OutputNewCommandJS == True:
         retstrJS = self.OutputCommandsCommonJS(operator, motion)
      else:
         retstrJS = self.OutputCommandsPointsJS(operator, motion)
      
      if self.UseComposite == True and self.CompositeFlag == True and self.CompositeFlagSet != True:
         self.CompositeFlagSet = True
      
      return [retstrPY, retstrJS]

   # --------------------------------------------------
   def OutputCommandsLin(self, operator, motion):
      '''Output linear motion
      L P[1] 50% FINE ACC80;

      Args:
         operator: download operator
         motion: current motion
      '''
      retstrPY = ''
      retstrJS = ''
      # Set Accuracy
      if self.CurrentAccuracyActive:
         self.LastLinAccuracy=self.CurrentLinAccuracy
      else:
         acc = '-1 '
      
      # Output for Python
      retstrPY = self.OutputCommandsCommonPY(operator, motion)

      # Output for JSON
      if self.OutputNewCommandJS == True:
         retstrJS = self.OutputCommandsCommonJS(operator, motion)
      else:
         retstrJS = self.OutputCommandsPointsJS(operator, motion)
      
      if self.UseComposite == True and self.CompositeFlag == True and self.CompositeFlagSet != True:
         self.CompositeFlagSet = True
      
      return [retstrPY, retstrJS]

   # --------------------------------------------------
   def OutputCommandsCirc(self, operator, motion):
      '''Output linear motion
      L P[1] 50% FINE ACC80;

      Args:
         operator: download operator
         motion: current motion
      '''
      retstrPY = ''
      retstrJS = ''
      # Set Accuracy
      if self.CurrentAccuracyActive:
         self.LastLinAccuracy=self.CurrentLinAccuracy
      else:
         acc = '-1'
      
      # Output for Python
      retstrPY = self.OutputCommandsCommonPY(operator, motion)

      # Output for JSON
      if self.OutputNewCommandJS == True:
         retstrJS = self.OutputCommandsCommonJS(operator, motion)
      else:
         retstrJS = self.OutputCommandsPointsJS(operator, motion)
      
      if self.UseComposite == True and self.CompositeFlag == True and self.CompositeFlagSet != True:
         self.CompositeFlagSet = True

      return [retstrPY, retstrJS]

   # --------------------------------------------------
   def OutputCommandsCommonPY(self, operator, motion):
      '''Output Motion for Python PTP/LIN/CIR
      Args:
         operator: download operator
         motion: current motion
      '''
      retstrPY = ''
      
      if self.UseComposite == True and self.CompositeFlag == True:
         # if Composite activated but not opened yet
         if self.CompositeFlagSet != True:
            retstrPY += '# ------------ Composite START --------------*\n'
            retstrPY += 'composite_motion_property = {\n   "speed": %.4f,\n   "acceleration": %.4f,\n' % (self.CurrentLinFeedrate, self.CurrentLinAcceleration)
            retstrPY += '   "current_joint_angles":rr.get_current_joint_angles(),\n'
            retstrPY += '   "commands": [\n         {\n'
         
      else:
         # usual un-composite Output
         retstrPY += '# Point %s\n' % (motion.GetName())
         if motion.IsLinearMotion():
            retstrPY += 'linear_property = {\n   "speed": %.4f,\n   "acceleration": %.4f,\n   "blend_radius": %.4f,' % (self.CurrentLinFeedrate, self.CurrentLinAcceleration, self.CurrentLinAccuracy * 0.001)
         elif motion.IsCircularMotion():
            retstrPY += 'circular_property = {\n   "speed": %.4f,\n   "acceleration": %.4f,' % (self.CurrentLinFeedrate, self.CurrentLinAcceleration)
         else:
            retstrPY += 'joint_property = {\n   "speed": %.2f,\n   "acceleration": %.2f,\n   "enable_safety" : False,' % (self.CurrentPtpFeedrate, self.CurrentLinAcceleration*0.01)
      
      return retstrPY
   # --------------------------------------------------
   def OutputCommandsCommonJS(self, operator, motion):
      '''Output Motion for JSON PTP/LIN/CIR
      Args:
         operator: download operator
         motion: current motion
      '''
      retstrJS = ''
      localOpenComposite = False
      forceLastPoint = False

      if self.UseComposite == True and self.CompositeFlag == True:
         # if Composite activated but not opened yet
         if self.CompositeFlagSet != True:
            retstrJS += '        # ------------ Composite START --------------*\n'
            localOpenComposite = True
            self.CompositeCounter += 1
            self.CmdIDCounter += 1
            retstrJS += '        {\n'
            retstrJS += '            "id": %s,\n' % (self.StartID + self.CmdIDCounter)
            retstrJS += '            "type": "MoveComposite",\n'
            retstrJS += '            "payload": {\n'
            retstrJS += '                "information": {\n'
            retstrJS += '                    "name": "mcom_%03d",\n' % self.CompositeCounter
            retstrJS += '                    "description": ""\n'
            retstrJS += '                },\n'
            # Parameters
            retstrJS += self.WriteCommandParameterJS(operator, motion)
            retstrJS = retstrJS[:-2]  # cut last Comma
            retstrJS += '\n            },\n'
            retstrJS += '            "children": [\n               {\n'
            self.BlanksJS = '   '
         else:
            if self.OutputNewCommandJS == True and motion.IsLinearMotion():
               # in case new, further Composite Item is LIN, force output last Point (CIR has already)
               forceLastPoint = True
      
      furtherID = True
      if localOpenComposite == False and self.CompositeFlagSet == False:
         # usual open new Move
         retstrJS += '        {\n'
         self.CmdIDCounter += 1
         retstrJS += '            "id": %s,\n' % (self.StartID + self.CmdIDCounter)
         furtherID = False
      if self.CompositeFlagSet == True:
         # ...or new Composite Item
         retstrJS += '                ,\n'
         retstrJS += '                {\n'
      if furtherID == True:
         self.CmdIDCounter += 1
         retstrJS += '               "id": %s,\n' % (self.StartID + self.CmdIDCounter)

      if motion.IsLinearMotion():
         retstrJS += self.BlanksJS + '            "type": "MoveLinear",\n'
      elif motion.IsCircularMotion():
         retstrJS += self.BlanksJS + '            "type": "MoveCircular",\n'
      else:
         retstrJS += self.BlanksJS + '            "type": "MoveJoint",\n'

      retstrJS += self.BlanksJS + '            "payload": {\n'
      retstrJS += self.BlanksJS + '                "information": {\n'
      if motion.IsLinearMotion():
         retstrJS += self.BlanksJS + '                    "name": "ml_%03d",\n' % self.PointCounterLIN
      elif motion.IsCircularMotion():
         retstrJS += self.BlanksJS + '                    "name": "mc_%03d",\n' % self.PointCounterCIR
      else:
         retstrJS += self.BlanksJS + '                    "name": "mj_%03d",\n' % self.PointCounterPTP
      retstrJS += self.BlanksJS + '                    "description": "%s"\n' % motion.GetPosition().GetProcessType()
      #retstrJS += self.BlanksJS + '                    "description": ""\n'
      retstrJS += self.BlanksJS + '                },\n'
      
      # output Parameters : "motion_parameter", "controller_parameter", "weaving_parameter", "go_till_force"
      retstrJS += self.WriteCommandParameterJS(operator, motion)

      # Calling the Points
      retstrJS += self.BlanksJS + '                "point_data": {\n'
      retstrJS += self.BlanksJS + '                    "points": [\n'

      # repeat last motion-point if composite is opened, got from stored Data
      if localOpenComposite == True or forceLastPoint == True:
         lastPoint = self.LastPointOutputJS[1]
         if self.LastPointOutputJS[0] in self.PtpAsCartesianDict:
            # if the last Point was a PTP (found in self.PtpAsCartesianDict), it should be output as a second Point in cartesian
            lastPoint = self.LastPointOutputJS[2]
            line = ['', self.PtpAsCartesianDict[self.LastPointOutputJS[0]]]
            # add the PTP-Point in cartesian Format to the Points Dictionary
            self.AddLineToPoints(line)
         retstrJS += self.BlanksJS + '                        ' + lastPoint + ',\n'
      
      # output the Point  point_dict["P010_20250220090000"].get("ID")
      retstrJS += self.OutputCommandsPointsJS(operator, motion)

      if self.BundleMotionsJS == False:
         retstrJS += '\n' + self.CloseCommandsCommonJS()

      return retstrJS
      
   # --------------------------------------------------
   def WriteCommandParameterJS(self, operator, motion):
      retstrJS = ''
      retstrJS += self.OutputCommandsMotionParameterJS(operator, motion)
      retstrJS += self.OutputCommandsControllerParameterJS(operator, motion)
      if motion.IsLinearMotion() or motion.IsCircularMotion():
         retstrJS += self.OutputCommandsWeavingParameterJS(operator, motion)
         retstrJS += self.OutputCommandsGoTillForceJS(operator, motion)
      
      return retstrJS
   # --------------------------------------------------
   def OutputCommandsMotionParameterJS(self, operator, motion):
      retstrJS = ''
      if motion.IsPtPMotion():
         retstrJS += self.BlanksJS + '                "motion_parameter": {\n'
         retstrJS += self.BlanksJS + '                    "speed": %.2f,\n'% (self.CurrentPtpFeedrate)   # in % max F
         if self.Short == True:
            retstrJS += self.BlanksJS + '                },\n'
            return retstrJS
         retstrJS += self.BlanksJS + '                    "acceleration": %.2f,\n'% (self.CurrentPtpAcceleration)   # in % max Acc
         retstrJS += self.BlanksJS + '                    "is_blending": False\n'
      else:
         retstrJS += self.BlanksJS + '                "motion_parameter": {\n'
         retstrJS += self.BlanksJS + '                    "speed": %.2f,\n'% (self.CurrentLinFeedrate)   # in mm/s
         if self.Short == True:
            retstrJS += self.BlanksJS + '                },\n'
            return retstrJS
         retstrJS += self.BlanksJS + '                    "acceleration": %.2f,\n'% (self.CurrentLinAcceleration)   # in mm/s²
         retstrJS += self.BlanksJS + '                    "rotation_speed": %.2f,\n'% (self.CurrentRotFeedrate)   # in deg/s
         retstrJS += self.BlanksJS + '                    "rotation_acceleration": %.2f,\n'% (self.CurrentRotAcceleration)   # in deg/s²
         retstrJS += self.BlanksJS + '                    "jerk": 500000,\n'
         retstrJS += self.BlanksJS + '                    "rotation_jerk": 28648,\n'
         if self.CurrentAccuracyActive == True:
            retstrJS += self.BlanksJS + '                    "is_blending": True,\n'
         else:
            retstrJS += self.BlanksJS + '                    "is_blending": False,\n'
         retstrJS += self.BlanksJS + '                    "blending_type": "dynamic",\n'
         retstrJS += self.BlanksJS + '                    "blending_radius": %.3f\n' % (self.CurrentLinAccuracy)
      retstrJS += self.BlanksJS + '                },\n'
      return retstrJS
   # --------------------------------------------------
   def OutputCommandsControllerParameterJS(self, operator, motion):
      '''Force Control, just move or take Forces into Account'''
      retstrJS = ''
      retstrJS += self.BlanksJS + '                "controller_parameter": {\n'
      #retstrJS += self.BlanksJS + '                    "selected_control_mode": "impendance",\n'
      #retstrJS += self.BlanksJS + '                    "selected_control_mode": "hybrid",\n'
      retstrJS += self.BlanksJS + '                    "selected_control_mode": "position",\n'
      if self.Short == True:
         retstrJS += self.BlanksJS + '                },\n'
         return retstrJS
      retstrJS += self.BlanksJS + '                    "fx_active": False,\n'
      retstrJS += self.BlanksJS + '                    "fx_value": 0,\n'
      retstrJS += self.BlanksJS + '                    "fy_active": False,\n'
      retstrJS += self.BlanksJS + '                    "fy_value": 0,\n'
      retstrJS += self.BlanksJS + '                    "fz_active": False,\n'
      retstrJS += self.BlanksJS + '                    "fz_value": 0\n'
      retstrJS += self.BlanksJS + '                },\n'
      self.ResetControllerParametersJS = False
      return retstrJS
   # --------------------------------------------------
   def OutputCommandsWeavingParameterJS(self, operator, motion):
      retstrJS = ''
      retstrJS += self.BlanksJS + '                "weaving_parameter": {\n'
      if self.CurrentWeaveOnOff == True:
         retstrJS += self.BlanksJS + '                    "is_weaving": True,\n'
      else:
         retstrJS += self.BlanksJS + '                    "is_weaving": False,\n'
      if self.Short == True:
         retstrJS += self.BlanksJS + '                },\n'
         return retstrJS
      retstrJS += self.BlanksJS + '                    "selected_pattern": "sine",\n'
      retstrJS += self.BlanksJS + '                    "left_amplitude": %3f,\n' % (self.CurrentWeaveWidth/self.CvrtMeter)   # in mm
      retstrJS += self.BlanksJS + '                    "right_amplitude": %3f,\n' % (self.CurrentWeaveWidth/self.CvrtMeter)   # in mm
      retstrJS += self.BlanksJS + '                    "azimuth": 0,\n'   # in deg
      retstrJS += self.BlanksJS + '                    "elevation": 0,\n'   # in deg
      retstrJS += self.BlanksJS + '                    "left_delay": %3f,\n' % (self.CurrentWeaveTime1)   # in sec
      retstrJS += self.BlanksJS + '                    "right_delay": %3f,\n' % (self.CurrentWeaveTime2)   # in sec
      retstrJS += self.BlanksJS + '                    "frequency": %3f\n' % (self.CurrentWeaveFrequenz)   # in Hz
      retstrJS += self.BlanksJS + '                },\n'
      # else:
      #    retstrJS += self.BlanksJS + '                "weaving_parameter": {\n'
      #    retstrJS += self.BlanksJS + '                    "is_weaving": False\n'
      #    retstrJS += self.BlanksJS + '                },\n'
      return retstrJS
   # --------------------------------------------------
   def OutputCommandsGoTillForceJS(self, operator, motion):
      retstrJS = ''
      if self.ResetGoTilForceParametersJS == True:
         retstrJS += self.BlanksJS + '                "go_till_force": {\n'
         retstrJS += self.BlanksJS + '                    "is_enabled": False,\n'
         if self.Short == True:
            retstrJS += self.BlanksJS + '                },\n'
            return retstrJS
         retstrJS += self.BlanksJS + '                    "extra_search_offset": 0,\n'
         retstrJS += self.BlanksJS + '                    "fx_active": False,\n'
         retstrJS += self.BlanksJS + '                    "fx_value": 0,\n'
         retstrJS += self.BlanksJS + '                    "fy_active": False,\n'
         retstrJS += self.BlanksJS + '                    "fy_value": 0,\n'
         retstrJS += self.BlanksJS + '                    "fz_active": False,\n'
         retstrJS += self.BlanksJS + '                    "fz_value": 0,\n'
         retstrJS += self.BlanksJS + '                    "reflex_enabled": False,\n'
         retstrJS += self.BlanksJS + '                    "search_distance": 0\n'
         retstrJS += self.BlanksJS + '                },\n'
      # self.ResetGoTilForceParametersJS = False # for modality
      return retstrJS
   # --------------------------------------------------
   def OutputCommandsPointsJS(self, operator, motion):
      retstrJS = ''
      self.LastWasPTP = False
      if motion.IsLinearMotion():
         retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID")' % (motion.GetName()+ self.PointUniqueNameExt)
      elif motion.IsCircularMotion():
         if self.FirstCircularFlagJS == True:
            retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID"),\n' % (self.LastMotion.GetName()+ self.PointUniqueNameExt)
         retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID"),\n' % (motion.GetViaPosition().GetName()+ self.PointUniqueNameExt)
         retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID")' % (motion.GetName()+ self.PointUniqueNameExt)
      else:
         retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID"),' % (motion.GetName()+ self.PointUniqueNameExt)
         #retstrJS += ',\n' + self.BlanksJS + '                        point_dict["%s"].get("ID")' % (motion.GetName()+ 'C' + self.PointUniqueNameExt)
         #self.LastWasPTP = True

      # save ['P001', 'point_dict["P001_2025...', 'point_dict["P001C_2025...'] for re-use in Composite
      normalpointJS = 'point_dict["%s"].get("ID")' % (motion.GetName()+ self.PointUniqueNameExt)
      ptpascartesianJS = 'point_dict["%s"].get("ID")' % (motion.GetName()+ 'C' + self.PointUniqueNameExt)
      self.LastPointOutputJS = [motion.GetName(), normalpointJS, ptpascartesianJS]
      
      if self.BundleMotionsJS == True and not motion.IsPtPMotion():
         retstrJS += ','
      return retstrJS
   # --------------------------------------------------
   def CloseCommandsCommonJS(self):
      '''
      Close the Composite or Point Item Section
      '''
      retstrJS = ''
      if self.LastWasPTP == True:
         # if last Motion was a PTP a Cartesian Point (from the JointPoint) is needed
         retstrJS += self.BlanksJS + '                        point_dict["%s"].get("ID")\n' % (self.LastMotion.GetName()+ 'C' + self.PointUniqueNameExt)
      retstrJS += self.BlanksJS + '                    ]\n'
      retstrJS += self.BlanksJS + '                }\n'
      if self.CompositeFlagSet == True:
         retstrJS += self.BlanksJS + '             }\n'
         retstrJS += self.BlanksJS + '             }'
      else:
         retstrJS += self.BlanksJS + '            },\n'
         retstrJS += self.BlanksJS + '            "children": []\n'
         retstrJS += self.BlanksJS + '        },'
      return retstrJS
   # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
   
   def HandlePointsSection(self, operator, motion):
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
            # create LIN source string (Line-List [P,J])
            dataPosition = self.OutputPointsLin(operator, motion)
            for line in dataPosition:
               # pass Line-List [P,J], ...in case of Python and Composite, send them to the StoreHouse
               data = ['LIN', self.CurrentLinAccuracy, motion.GetPosition().GetName()]
               self.OutputPointsToDesiredTarget(line, data)

         # check if the motion is of type circular
         elif motion.IsCircularMotion():
            # create CIRC source string (Line-List [P,J])
            dataPositions = self.OutputPointsCirc(operator, motion)
            for line in dataPositions:
               # pass Line-List [P,J], ...in case of Python and Composite, send them to the StoreHouse
               data = ['CIR', self.CurrentLinAccuracy, motion.GetPosition().GetName()]
               self.OutputPointsToDesiredTarget(line, data)

         # check if the motion is of type point to point
         else:
            # create PTP source string (Line-List [P,J])
            dataPosition = self.OutputPointsPtp(operator, motion)
            for line in dataPosition:
                  # pass Line-List [P,J]
                  self.AddLineToPoints(line)

         # reset skip data creation
         self.SkipDataMotion = False

   # --------------------------------------------------
   def OutputPointsToDesiredTarget(self, pointData, data):
      '''
      Output point in desired Target : directly in Output-List or Intermediate-Composite-List (StoreHouse)
      Args:
         pointData : the Points Data [0]=Python  [1]=Json
         data : ['LIN/CIR', accu.Val, 'P001']
      '''
      if self.CompositeFlagSet == True:
         self.CompositeStoreHousePointsPY.append(pointData[0])
         self.CompositeStoreHouseDataPY.append(data)
         pointData[0] = ""
         self.AddLineToPoints(pointData)
      else:
         self.AddLineToPoints(pointData)
   # --------------------------------------------------
   def OutputPointsPtp(self,operator, motion):
      '''
      Output point to point position in data section\n
      Args:
         operator: download operator
         motion: current motion object
         dataOutputOnly:   False: the point is also output in source section
                              and point counter is already increased
                           True:  the point is NOT output is source section
                              and point counter needs to be increased
      Return:
         returns the string of the data section for the point to point motion
      '''
      
      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      data = []
      # NeuraRobot Ptp points always generated as with joint output
      data.append(self.OutputNeuraMotionData(operator, motionGroups[0], motion.GetName(), motion))
      self.LastMotion = motion
      return data

   # --------------------------------------------------
   def OutputPointsLin(self, operator, motion):
      '''
      Output linear position in data section\n
      Args:
         operator: download operator
         motion: current motion object
         dataOutputOnly:   False: the point is also output in source section
                              and point counter is already increased
                           True:  the point is NOT output is source section
                              and point counter needs to be increased
      Return:
         returns the string of the data section for the point to point motion
      '''
      
      # get position of motion
      position = motion.GetPosition()
      # get motion target type 
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())
      if self.CompositeFlagSet == True:
         motionLast = self.CreateMotionGroupStructure(operator, self.LastMotion.GetPosition())
      
      data = []
      if self.CompositeFlagSet == True and motionLast != None and self.IsCompositeLinear != True:
         # in Case of Composite recall last Position as first Comp-Pos
         data.append(self.OutputNeuraMotionData(operator, motionLast[0], self.LastMotion.GetPosition().GetName(), motion, 1))
         self.IsCompositeLinear = True
         self.IsCompositeCircular = False
      data.append(self.OutputNeuraMotionData(operator, motionGroups[0], motion.GetName(), motion))
      self.LastMotion = motion
      return data

   # --------------------------------------------------
   def OutputPointsCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      '''
      Output circular position in data section\n
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         motion (DULPythonMotion): motion operator gives access to positions and events
         dataOutputOnly (bool, optional): Set to True if the point is not output in source section. In that case the point
                                          counter needs to be increased in data section. Defaults to False.
      Return:
         returns the string of the data section for the point to point motion
      '''
      
      # get position
      position = motion.GetPosition()
      # get motion target type
      motionTargetType = position.GetTargetType()

      # create motion group structure
      motionLast = self.CreateMotionGroupStructure(operator, self.LastMotion.GetPosition())
      motionGroupsViaPoint = self.CreateMotionGroupStructure(operator, motion.GetViaPosition())
      motionGroups = self.CreateMotionGroupStructure(operator, motion.GetPosition())

      data = []
      data.append(self.OutputNeuraMotionData(operator, motionLast[0], self.LastMotion.GetPosition().GetName(), motion, 1))
      data.append(self.OutputNeuraMotionData(operator, motionGroupsViaPoint[0], motion.GetViaPosition().GetName(), motion, 2))
      data.append(self.OutputNeuraMotionData(operator, motionGroups[0], motion.GetPosition().GetName(), motion, 3))
      self.LastMotion = motion
      self.IsCompositeLinear = False
      self.IsCompositeCircular = True
      return data  
   # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
   

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
  

   # --------------------------------------------------
   def OutputNeuraMotionData(self, operator : DULPythonDownloadOperator, motionGroup, pointName, motion, complete = 0):
      #stringArray = []
      tempstrPY= ''
      tempstrJS= ''
      log= operator.GetLogOperator()
      
      # beginning write Target (PTP, LIN, 1st CIR-Pnt)
      # for PYTHON
      blanks = ''
      if self.CompositeFlagSet == True and not(motion.IsPtPMotion()):
         blanks = '         '
      if complete == 0 or complete == 1:
         if motion.IsPtPMotion():
            tempstrPY = '   "target_joint": [\n      [\n'
         else:
            if self.CompositeFlagSet == True:
               tempstrPY = blanks + '      [\n'
               # tempstrPY = blanks + '   "targets": [\n' + blanks + '      [\n'
            else:
               tempstrPY = '   "target_pose": [\n      [\n'
      else:
         tempstrPY += blanks + '      [\n'
      
      # for JSON
      tempstrJS = '    "%s":\n        {\n            "Frame": "Base",' % (pointName + self.PointUniqueNameExt)
      
      # write Target Values Group
      # Write all joints
      joints = motionGroup.GetAllJoints()
      # separate different joint types
      RobotJoints=self.GetRobotJoints(joints)
      RailJoints=self.GetRailJoints(joints)
      WPPositionerJoints=self.GetWPPositionerJoints(joints)
      
      # -------- only for Python --------
      if motion.IsPtPMotion():
         # output in Joints
         for joint in RobotJoints:            
               tempstrPY += '      %.8f,\n' % (joint.Value * self.JointRotFactorPY)
         for joint in RailJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  tempstrPY += '      %.8f,\n' % (joint.Value * self.JointRotFactorPY)
            else:
                  log.LogInfo('Error: %s not matching NeuraRobot Mechanism Signature' % (joint.JointName))
         for joint in WPPositionerJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  tempstrPY += '      %.8f,\n' % (joint.Value * self.JointRotFactorPY)
            else:
                  log.LogInfo('Error: %s not matching NeuraRobot Mechanism Signature' % (joint.JointName))
         tempstrPY = tempstrPY[:-2] # cut the last Comma (bec. Loop)
         tempstrPY += '\n'
      else:
         # output in Cartesian/Coordinates
         tempstrPY += blanks + '      %.5f,\n' % (motionGroup.X * self.CartesianLinFactorPY) 
         tempstrPY += blanks + '      %.5f,\n' % (motionGroup.Y * self.CartesianLinFactorPY) 
         tempstrPY += blanks + '      %.5f,\n' % (motionGroup.Z * self.CartesianLinFactorPY) 
         tempstrPY += blanks + '      %.8f,\n' % (motionGroup.W * self.CartesianRotFactorPY) 
         tempstrPY += blanks + '      %.8f,\n' % (motionGroup.P * self.CartesianRotFactorPY) 
         tempstrPY += blanks + '      %.8f' % (motionGroup.R * self.CartesianRotFactorPY) 
         tempstrPY += '\n'
      # finalize Target Group (1st/Via CIR-Pnt to be continued)
      if complete == 1 or complete == 2:
         if self.CompositeFlagSet == True:
            tempstrPY += blanks + '      ]'
         else:
            tempstrPY += blanks + '      ],'
      else:
         if self.CompositeFlagSet == True:
            tempstrPY += blanks + '      ]'
         else:
            tempstrPY += blanks + '      ]\n'
      # ending write Target (PTP, LIN, last CIR-Pnt)
      if complete == 0 or complete == 3:
         if self.CompositeFlagSet == True:
            iDummy = 1
            #tempstrPY += blanks + '   #]'
         else:
            tempstrPY += '   ],\n'
            tempstrPY += '   "current_joint_angles":%s.get_current_joint_angles()\n}\n' % (self.NeuraRobotName)
            tempstrPY += '%s' % (self.NeuraRobotName)
            if motion.IsLinearMotion():
               #tempstrPY += '.move_linear_from_current_position(**linear_property)'
               tempstrPY += '.move_linear(**linear_property)'
            elif motion.IsCircularMotion():
               tempstrPY += '.move_circular(**circular_property)'
            else:
               tempstrPY += '.move_joint(**joint_property)'

      # -------- only for JSON --------
      # for JSON create both Lines for Joint and Cartesian Values
      doJointsOutput = True
      doCartesianOutput = True
      jointDefinition = ''
      cartesianDefinition = ''
      
      # for JSON store PTPs in cartesian Format (for Composite)
      ptpascartesianJS = ''
      ptpascartesianJS = '    "%s":\n        {\n            "Frame": "Base",' % (pointName + 'C' + self.PointUniqueNameExt)
      ptpascartesianJS += '\n            "CartesianPose": ['

      if doJointsOutput == True:
         # output in Joints
         jointDefinition = '\n            "JointConfiguration": ['
         for joint in RobotJoints:            
               jointDefinition += '%.5f, ' % (joint.Value * self.JointRotFactorJS)
         for joint in RailJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  jointDefinition += '%.5f, ' % (joint.Value * self.JointRotFactorJS)
            else:
                  log.LogInfo('Error: %s not matching NeuraRobot Mechanism Signature' % (joint.JointName))
         for joint in WPPositionerJoints:
            if self.GetMechanismAxes.__contains__(joint.JointName):
                  jointDefinition += '%.5f, ' % (joint.Value * self.JointRotFactorJS)
            else:
                  log.LogInfo('Error: %s not matching NeuraRobot Mechanism Signature' % (joint.JointName))
         jointDefinition = jointDefinition[:-2] # cut the last Comma (bec. Loop)
         jointDefinition += '],'

         if 1 == 1:
            # for JSON store PTPs in cartesian Format (for Composite)
            ptpascartesianJS += '%.5f, ' % (motionGroup.X * self.CartesianLinFactorJS) 
            ptpascartesianJS += '%.5f, ' % (motionGroup.Y * self.CartesianLinFactorJS) 
            ptpascartesianJS += '%.5f, ' % (motionGroup.Z * self.CartesianLinFactorJS) 
            ptpascartesianJS += '%.5f, ' % (motionGroup.W * self.CartesianRotFactorJS) 
            ptpascartesianJS += '%.5f, ' % (motionGroup.P * self.CartesianRotFactorJS) 
            ptpascartesianJS += '%.5f' % (motionGroup.R * self.CartesianRotFactorJS) 
      
      if doCartesianOutput == True:
         # output in Cartesian/Coordinates
         cartesianDefinition = '\n            "CartesianPose": ['
         cartesianDefinition += '%.5f, ' % (motionGroup.X * self.CartesianLinFactorJS) 
         cartesianDefinition += '%.5f, ' % (motionGroup.Y * self.CartesianLinFactorJS) 
         cartesianDefinition += '%.5f, ' % (motionGroup.Z * self.CartesianLinFactorJS) 
         cartesianDefinition += '%.5f, ' % (motionGroup.W * self.CartesianRotFactorJS) 
         cartesianDefinition += '%.5f, ' % (motionGroup.P * self.CartesianRotFactorJS) 
         cartesianDefinition += '%.5f' % (motionGroup.R * self.CartesianRotFactorJS) 
         cartesianDefinition += '],\n'

      # add both definitions to the Point
      if doJointsOutput == True:
         tempstrJS += jointDefinition
      if doCartesianOutput == True:
         tempstrJS += cartesianDefinition
      #tempstrJS += self.PointsAsComment(RobotJoints,motionGroup)
      if motion.IsPtPMotion():
         tempstrJS += '            "type": "Joint"\n'
      else:
         tempstrJS += '            "type": "Cartesian"\n'
      
      # no Comma after the last TPE
      if self.NumberTpes == self.PointCounter:
         tempstrJS += '        }'
      else:
         tempstrJS += '        },'

      if complete == 1:
         # 1st CircPoint is the last Motion, empty it (JsonPointDict), already outputted
         tempstrJS = ''

      # for JSON store PTPs in cartesian Format (for Composite)
      ptpascartesianJS += '],\n'
      ptpascartesianJS += '            "type": "Cartesian"\n'
      ptpascartesianJS += '        },'
      #if motion.IsPtPMotion():
         # PtpAsCartesianDict['P001'] = '"P001C_20250220090000": {"Frame": "Base",....}'
         #self.PtpAsCartesianDict[pointName] = ptpascartesianJS

      return [tempstrPY, tempstrJS]
   
   # --------------------------------------------------
   def PointsAsComment(self, RobotJoints,motionGroup):
      '''Output Points Coordinates and Joints as Comment'''
      comment = '            # Joints : '
      for joint in RobotJoints:            
         comment += '%.5f, ' % (joint.Value * 1)
      comment += '\n            # Coords : '
      comment += '%.5f, ' % (motionGroup.X * 1) 
      comment += '%.5f, ' % (motionGroup.Y * 1) 
      comment += '%.5f, ' % (motionGroup.Z * 1) 
      comment += '%.5f, ' % (motionGroup.W * 1) 
      comment += '%.5f, ' % (motionGroup.P * 1) 
      comment += '%.5f\n' % (motionGroup.R * 1) 
      return comment
   # --------------------------------------------------
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
      self.OutputFilePathPython = outputDir + "\\" + program.GetName() + self.FILE_EXTENSION_PY
      self.OutputFilePathJson = outputDir + "\\" + program.GetName() + self.FILE_EXTENSION_JSON
      # Get RobotName 
      # Get Resource Attributes
      resources=controller.GetResources()
      for resource in resources:
         if int(resource.GetItemType()) == 1 and int(resource.GetItemSubType()) ==1:
            self.RobotName = resource.GetName()         
      # create Header
      self.CreateHeader(operator)

   # --------------------------------------------------
   def CheckAndUpdateBaseFrame(self, index):
      '''Checks if base frame index is within range and generate a output line
      '''
      if self.CurrentBaseFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.BaseFrameMinIndex, self.BaseFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentBaseFrameIndex = index
         else:
            self.Logging.LogError('Base frame index out of range')
   
   def CheckAndUpdateToolFrame(self, index):
      '''Checks if tool frame index is within range and generate a output line
      '''
      if self.CurrentToolFrameIndex != index:
         frameRangeCheck = self.RangeCheck(index, self.ToolFrameMinIndex, self.ToolFrameMaxIndex)
         if frameRangeCheck == True:
            self.CurrentToolFrameIndex = index
         else:
            self.Logging.LogError('Tool frame index out of range')

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
   

   # ------------------------------------------------------------------------------
   def AddLineToHeader(self, newline):
      '''
      Add a line to the program header\n
      Args:
         newline : List/Pair of the new Line for Python[0] and Json[1]
      '''
      if newline[0] != '':
         self.HeaderPY.append(newline[0])
      if newline[1] != '':
         self.HeaderJS.append(newline[1])
   # --------------------------------------
   def AddLineToCommands(self, newline):
      '''
      Add a new line to the Command section\n
      Args:
         newline : List/Pair of the new Line for Python[0] and Json[1]
      '''
      if newline[0] != '':
         self.CommandsPY.append(newline[0])
      if newline[1] != '':
         self.CommandsJS.append(newline[1])
   # --------------------------------------
   def AddLineToPoints(self, newline):
      '''
      Add a new line to the Point section\n
      Args:
         newline : List/Pair of the new Line for Python[0] and Json[1]
      '''
      if newline[0] != '':
         self.CommandsPY.append(newline[0])   # Python has embedded Command&Point
      if newline[1] != '':
         self.PointsJS.append(newline[1])     # Json seperate Points List
   # --------------------------------------
   def WriteOutputFile(self, operator):
      '''
      Write output file
      Args:
         operator: download operator
      '''
      # create file and output the program for JSON
      if (self.outputJson):
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.HeaderJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.PointsHeaderJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.PointsJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.PointsFooterJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.IntermediateJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.CommandsHeaderJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.CommandsJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.CommandsFooterJS)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathJson, self.FooterJS)
         operator.AddOutputFilePath(self.OutputFilePathJson)
      
      # create file and output the program for PYTHON
      if (self.outputPython):
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathPython, self.HeaderPY)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathPython, self.CommandsHeaderPY)
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathPython, self.CommandsPY)      
         self.FileUtil.AppendTextArrayToFile(self.OutputFilePathPython, self.FooterPY)
         operator.AddOutputFilePath(self.OutputFilePathPython)


   # ==================================================
   def AdjustOrientation(self, orientation):
      '''prevent -0.00 or +/- 180 degree output'''
      if self. PointCounter > 29 and self. PointCounter < 35:
         iDummy = 0
      tempOrientation = self.LastOrientation
      # self.LastOrientation = [
      #    0.0 if abs(ax) < 0.001 else
      #    180.0 if ax < -179.999 and tempOrientation[iC] > 179.999 else
      #    -180.0 if ax > 179.999 and tempOrientation[iC] < -179.999 else ax
      #   for iC, ax in enumerate(orientation)
      # ]
      # self.LastOrientation = [
      #    0.0 if abs(ax) < 0.001 else
      #    180.0 if ax < -179.999 and tempOrientation[iC] - ax >  180.0 else
      #    -180.0 if ax > 179.999 and tempOrientation[iC] - ax < -180.0 else ax
      #   for iC, ax in enumerate(orientation)
      # ]
      self.LastOrientation = [
         0.0 if abs(ax) < 0.001 else
         ax+360.0 if tempOrientation[iC] - ax >  180.0 else
         ax-360.0 if tempOrientation[iC] - ax < -180.0 else ax
        for iC, ax in enumerate(orientation)
      ]
      return self.LastOrientation
   # --------------------------------------------------
   def CreateMotionGroupStructure(self, operator, positionObject):
      '''
      Create the motion group structure depending on axes mapping in layout builder
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
      #orientation = self.AdjustOrientation(positionObject.GetOrientation()) # positionObject.GetOrientation()
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

   # --------------------------------------------------
   def GetMotionGroupByIndex(self, motionGroups, index):
      '''
      Get the motion group by index
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
   
   # --------------------------------------------------
   # Set Current Feedrate from Speed Event 
   def setSpeed(self, event):
      pathtype = ''
      speed = 0.0
      attributes = event.GetAttributes()
      for att in attributes:
         if att.GetName() == 'Value':
            speed=att.GetValue()
         if att.GetName() == 'PathType':
            pathtype=att.GetValue()
         self.DevLogging("..................................SpeedEvent Attr.Name = " + str(att.GetName()) + " = " + str(att.GetValue()))
      
      unit = 'Percentage'  #  Value 1...100%
      if speed < 10:
         unit = 'Speed'  # 0.xx m/s  ...assuming <10 is not percent
      
      if unit == 'Percentage':
         percVal = speed
         feedVal = (speed/100) * self.RobotMaxTCPFeedrate
      else:
         speed *= 1000  # from meter to mm
         feedVal = speed
         percVal = (speed*100) / self.RobotMaxTCPFeedrate

      if pathtype == 'Contour':
         if self.LinFeedrateinPercent == True:
            self.CurrentLinFeedrate = percVal
         else:
            self.CurrentLinFeedrate = feedVal
      else:
         if self.PtpFeedrateinPercent == True:
            self.CurrentPtpFeedrate = percVal
         else:
            self.CurrentPtpFeedrate = feedVal
      
      # force new CommandSection if neccessary
      if self.CurrentMotion.IsPtPMotion():
         check = 'PointToPoint'
      else:
         check = 'Contour'
      # if the Event´s PathType is the same like the current Motion´s, then reset
      if pathtype == check:
          iDummy = 0
          self.NewFeedrateSetFlag = True
          #self.OutputNewCommandResetFlagJS = False  # ...True
          #self.CompositeFlag = False

   # --------------------------------------------------
   def SetAccuracy(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      '''
      Set current accuracy from accuracy event
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      '''
      
      # variable initialization
      pathtype= ''
      accuracy = -1
      criteria = ''
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for att in attributes:
         # get accuracy value
         if att.GetName() == 'Value':
            accuracy = att.GetValue()
         # get path type
         if att.GetName() == 'PathType':
            pathtype = att.GetValue()
         # get criteria On/Off/Distance/JointDistance/
         if att.GetName() == 'Criteria':
            criteria = att.GetValue()
         self.DevLogging("..................................AccuracyEvent Attr.Name = " + str(att.GetName()) + " = " + str(att.GetValue()))
      
      # check if criteria is On
      if criteria =='On':
         self.CurrentAccuracyActive = True
         if accuracy > 0.0:
            # distinguish between contour and point to point
            if pathtype == 'Contour':
               self.CurrentLinAccuracy = int(accuracy * 1000)
               if self.CurrentLinAccuracy > 100:
                  self.Logging.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
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
            self.Logging.LogError('Accuracy value for linear motion is out of range (%d). Max value is 100.' % (self.CurrentLinAccuracy))
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

      # force new CommandSection if neccessary
      if self.CurrentMotion.IsPtPMotion():
         check = 'PointToPoint'
      else:
         check = 'Contour'
      # if the Event´s PathType is the same like the current Motion´s, then reset
      if pathtype == check:
          iDummy = 0
         #self.OutputNewCommandResetFlagJS = False # ....True
         #self.CompositeFlag = False

   # --------------------------------------------------
   def SetAcceleration(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      '''
      Set current acceleration from acceleration event
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      '''
      
      # variable initialization
      pathtype= ''
      acceleration = -1
      # get event attributes
      attributes = event.GetAttributes()
      # iterate through event attributes
      for att in attributes:
         #self.DevLogging("..........ArcOnEvent Attr.Name = " + str(att.GetName()))
         # get acceleration value
         if att.GetName() == 'Value':
            acceleration = att.GetValue()
         # get path type
         if att.GetName() == 'PathType':
            pathtype = att.GetValue()
         self.DevLogging("..................................AccelerationEvent Attr.Name = " + str(att.GetName()) + " = " + str(att.GetValue()))
      
      unit = 'Percentage'  #  Value 1...100%
      if acceleration < 10:
         unit = 'Acceleration'  # 0.xx m/s²  ...assuming <10 is not percent
      
      if unit == 'Percentage':
         percVal = acceleration
         acclVal = (acceleration/100) * self.RobotMaxAcceleration
      else:
         acceleration *= 1000  # from meter to mm
         acclVal = acceleration
         percVal = (acceleration*100) / self.RobotMaxAcceleration

      if pathtype == 'Contour':
         if self.LinAccelerationinPercent == True:
            self.CurrentLinAcceleration = percVal
         else:
            self.CurrentLinAcceleration = acclVal
      else:
         if self.PtpAccelerationinPercent == True:
            self.CurrentPtpAcceleration = percVal
         else:
            self.CurrentPtpAcceleration = acclVal

   # --------------------------------------------------
   def OutputDwellEvent(self, event):
      time = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            time=attribute.GetValue()
            if time > 0.0:
               tmpStr = "sleep(%.1f)" % (time)
               self.CommandsPY.append(tmpStr)

   # --------------------------------------------------
   # Set Logic Port Event
   def setLogicPort(self, event):
      atts = event.GetAttributes()
      for att in atts:
         self.CommandsPY.append(att.GetName() + ',' + str(att.GetValue()))

   # --------------------------------------------------
   # Sync Robot Event NeuraRobot (Handshake)
   def SetSyncRobotsEvent(self,event):
      atts = event.GetAttributes()
      bHandshake=False
      for att in atts:
         if att.GetName() == 'SyncMode':
            bHandshake=True
         if att.GetName() == 'SyncText':
           if bHandshake == True:
              self.CommandsPY.append('SEMNUM, 1, ' +str(att.GetValue()))
              bHandshake=False
   
   # --------------------------------------------------
   # Check for Tool Provider
   def setWeldEffectorIndex(self, name):
      # set Weld Effector Manufacturer to Index
      index = 0
      if name == "Fronius":
         index = 0
      elif name == "DhRobotics_PGC_140_RTU_RS485":
         index = 1
      elif name == "Dhrobotics_PGC_RTU":
         index = 2
      elif name == "Kempi":
         index = 3
      elif name == "SKS":
         index = 4
      elif name == "SKS_dryweld":
         index = 5
      elif name == "iMIG":
         index = 6
      elif name == "iMIG_dryweld":
         index = 7
      elif name == "iROB401":
         index = 8
      elif name == "iROB401_dryweld":
         index = 9
      return index
   # ========================================================================================
   class MotionGroup():
      '''
      Class that emulates the Fanuc Data section and thus simplifies output/customizing.
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
         '''
         Class initialization
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
         '''
         Add a joint to the motion group
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
         '''
         get all joints of the motion group
         Return:
            Returns a list of all joint of the motion group
         '''
         return self.Joints
      
      def GetAllSynchronousJoints(self):
         '''
         Get all synchronous joints from motion group
         Return:
            Returns a list of all synchronous joints of the motion group
         '''
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == self.SYNCHRONOUS_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def GetAllDrivenJoints(self):
         '''
         Get all synchronous joints from motion group
         Return:
            Returns a list of all synchronous joints of the motion group
         '''
         synchronousJoints = []
         for joint in self.Joints:
            if joint.ResourceJointType == self.DRIVEN_JOINT:
               synchronousJoints.append(joint)
         return synchronousJoints
      
      def HasDrivenJoints(self):
         '''
         Check if a robot/machine is part of the motion group
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
         
      # ========================================================================================
      class Joint():
         '''
         Joint class to store important joint information in a separated object
         '''
         # kinematic type
         JOINT_TYPE_LINEAR = 0
         JOINT_TYPE_ROTATION = 1

         def __init__(self, index, kinematicType, resourceJointType, jointRole, value, name):
            '''
            Class initialization
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