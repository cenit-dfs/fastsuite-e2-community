# -------------------------------------------------------------------------------------------
# Name: arc welding connect touch points and process points automatically
# Description: 
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

# Import libraries
#from centypes import *
from cenpylib import *
import math
import sys, os, inspect
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\AutoExecute\\")

# attributes
WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"
AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_CONNECT_TOUCH_PROCESS_TYPE = "ConnectTouchProcessType"
# CONSTANTS
AW_CONNECT_OPERATION = 0
AW_CONNECT_START_END = 1
AW_CONNECT_SHORTEST_DISTANCE = 2
AW_CONNECT_NO = 3
WM_STICH = "StitchWeldingWorkMethod"
WM_TOUCH = "TouchSensingWorkMethod"
WM_SEAM = "SeamSearchWorkMethod"
WM_CONTINUES = "ContourPointWorkMethod"
TS_POINT_IDENTIFIER_START_APP = "TouchPointStartAppEvent"
TS_POINT_IDENTIFIER_COLLISION = "TouchPointCollisionEvent"
TS_POINT_IDENTIFIER_END = "TouchPointEndEvent"
TS_POINT_IDENTIFIER_START_RET = "TouchPointStartRetEvent"
# event names
TOUCH_CONNECT_EVENT = "ConnectTouchProcessPointEvent"
# event attributes
AW_EVT_TOUCH_ID = "TouchId"
AW_EVT_TOUCH_COUNTER = "Touch_Cntr"
# operation attribute, needed for the naming of the operations
AW_WELDING_GROUP = "WeldingGroup"

# Download Error codes
ERRDOWNLOAD_NOERROR = 0 
ERRDOWNLOAD_EMPTYPROGRAMNAME = 10002
ERRDOWNLOAD_UNKNOWNOUTPUTDIRECTORYPATH = 10055
ERRDOWNLOAD_PROGRAMNOTFOUND = 10080
ERRDOWNLOAD_TRANSLATORNOTSET = 10097
ERRDOWNLOAD_NOLICENCE = 10218
ERRDOWNLOAD_PROGRAMDOWNLOADFAILED = 10400

# each welding group will get a number to identify the touch
# and welding operation which belong to this group
weldingGroupNr = 0

def GetCommandName():
   return "PrevProgramDownload"
   
def GetCommandUuId():
   return "1E3301D4-3207-48F0-9D2F-EF96E04119F6"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogInfo("PrevProgramDownload.py: ")

   # -- SEQUENCE --
   # 0) get last programmed operations
   # 1) check if connection type is no
   # 2) sort operation in weld operations and touch operations
   # 3) add connection events depending on connection type

   # -------------------------------------
   # 0) get user selection
   # -------------------------------------
   # global variable
   global connectionType
   connectionType = AW_CONNECT_OPERATION
   
   # AW_CONNECT_OPERATION = 0
   # AW_CONNECT_START_END = 1
   # AW_CONNECT_SHORTEST_DISTANCE = 2 // missing: ignore box welding points
   # AW_CONNECT_NO = 3

   # -------------------------------------
   # 1) check if connection type no
   # -------------------------------------
   if (connectionType == AW_CONNECT_NO):
      return

   # get active program
   program = Operator.GetActiveProgram()
   # get all operations
   operations = program.GetOperations()
   # get teach handler
   teachHandler = Operator.GetTeachHandler()
   # get event handler
   eventHandler = Operator.GetEventHandler()

   # -------------------------------------
   # 2) sorting operations in welding and touch operations
   # -------------------------------------
   # if welding operation has no touch points, add the welding operation to the previews welding group with touch points
   touchOps = []
   weldingOps = []
   # sorting operations in welding and touch operations
   for operation in operations:
      workMethodName = GetOperationStringAttribute(operation, WORKMETHOD_NAME)
      if workMethodName in [WM_TOUCH, WM_SEAM]: # could be enhanced with more workmethods in future
         touchOps.append(operation)
      elif (workMethodName == WM_STICH) or (workMethodName == WM_CONTINUES):
         weldingOps.append(operation)

   weldingGroups = CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps)

   # get the number of each welding group and set it as string to the several operations
   for weldingGroup in weldingGroups:
      wgNumber = weldingGroup.GetWeldingGroupNumber()
      # create the string
      opName = "WG" + str(wgNumber) + "_"
      # get welding and touch operations an set the string as attribute
      weldingOps = weldingGroup.GetWeldingOperations()
      for weldingOp in weldingOps:
         SetAttributeRecompState(weldingOp, AW_WELDING_GROUP)
         SetOperationStringAttribute(weldingOp, AW_WELDING_GROUP, opName)
      touchOps = weldingGroup.GetTouchOperations()
      for touchOp in touchOps:
         SetAttributeRecompState(touchOp.GetTouchOperation(), AW_WELDING_GROUP)
         SetOperationStringAttribute(touchOp.GetTouchOperation(), AW_WELDING_GROUP, opName)

   # -------------------------------------
   # 3) add number touches per ID to the connect event
   # -------------------------------------
   CalculateNumberOfTouchesPerTouchId(weldingGroups)
   
   # In case of Cooperate Robots Programming by Team Controller and Usage of 2nd Robot by Current Mechanism, start Download of involved robots program
   # Currently only one slave robot support ('A')
   attribSetter = Operator.GetAttribSetter()
   attribGetter = Operator.GetAttribGetter()
   IsMasterProgram = False
   GeneratedDownloadFileName = ''
   SlaveRobotName = ''
   errmsg = ''
   # Check if selected Mechanism Master/Slave Mechanism ? 
   if attribGetter.GetAttributeEnumByName('Mechanism').GetValue().__contains__(',A'):
         IsMasterProgram = True  
   if Operator.GetController().GetTeamController().IsTeamController() and IsMasterProgram:
      # Master and Slave program has to have same names
      SlaveProgram=program.GetName()+'SL'         
      for contr in Operator.GetController().GetTeamController().GetControllers():
         if contr.GetName() != Operator.GetController().GetName():
            # Download Slave Program
            ret=contr.DownloadProgramByName (SlaveProgram)
            if ret>0:
               if ret == 10080:
                  errmsg = 'Program %s not exists on slave controller, same name like Master Program expected!' % SlaveProgram
               else:
                  errmsg = str(ret)
               mb = MessageBox()
               mb.Show('Panasonic Download Error', errmsg,1,0)
            else:
               GeneratedDownloadFileName=contr.GetOutputDirectory() +'\\' +SlaveProgram
               resources=contr.GetResources(1,1)
               for resource in resources:
                  if resource.GetItemType() == 1 and resource.GetItemSubType() ==1:
                     SlaveRobotName = resource.GetName()
               attribSetter.SetString('SlaveProgram',GeneratedDownloadFileName)
               attribSetter.SetString('SlaveRobotName',SlaveRobotName)     
   else:
      attribSetter.SetString('SlaveProgram','')
      attribSetter.SetString('SlaveRobotName','')      
   return


def CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps):
   # if a welding operation has no corresponding touch operation,
   # the welding operation will be added to the previous welding group
   weldingGroups = []
   # check if a touch operation belongs to the welding operation, otherwise add the welding operation belongs to the welding group before
   currentWeldGroup = None
   # iterate through all welding operations
   for weldingOp in weldingOps:
      # init variable found touch corresponding touch operation
      touchOperationFound = False
      for tOp in touchOps:
         # check identifier
         if (tOp.GetProcessGeometryIdentifier() == weldingOp.GetProcessGeometryIdentifier()):
            # corresponding touch operation was found
            touchOperationFound = True
            break
      # if corresponding touch operation was found, create a new welding group
      if touchOperationFound == True:
         # create new welding groups with welding operation
         currentWeldGroup = WeldingGroup(weldingOp, teachHandler, eventHandler)
         # increase the welding group number and set it to the new group
         global weldingGroupNr
         weldingGroupNr += 1
         currentWeldGroup.SetWeldingGroupNumber(weldingGroupNr)
         # add welding group to the list with welding groups
         weldingGroups.append(currentWeldGroup)
      else:
         # if connection type is shortest distance, each welding operation must have it's own corresponding touch operation
         # a mix is not supported. In that case all already created events are removed and execution is aborted.
         if connectionType == AW_CONNECT_SHORTEST_DISTANCE:
            logging.LogError("You selected connection type shortest distance, but a welding operation has no linked touch operation. Mix is not possible.")
            # RemoveAllConnectEvents(eventHandler, program)
            return None
         if len(weldingGroups) != 0:
            weldingGroups[len(weldingGroups)-1].AddWeldingOperation(weldingOp)

   # add touch operations to welding groups 
   for touchOp in touchOps:
      touchOpIdentifier = touchOp.GetProcessGeometryIdentifier()
      for weldingGroup in weldingGroups:
         if (touchOpIdentifier == weldingGroup.GetIdentifier()):
            weldingGroup.AddTouchOperation(touchOp)
            break

   # set the touch id found in touch connect event
   for weldingGroup in weldingGroups:
      for touchOperation in weldingGroup.GetTouchOperations():
         touchOperation.SetTouchId(eventHandler)
   return weldingGroups

def CalculateNumberOfTouchesPerTouchId(WeldGroups):
   # iterate through all welding groups
   for weldGroup in WeldGroups:
      # list with different touch IDs of the welding group 
      listTouchIds = []
      # iterate through the touch operation to get the touch ID
      for touchOperation in weldGroup.GetTouchOperations():
         currentTouchId = touchOperation.GetTouchId()
         # if the id is different add it to the list with IDs
         if currentTouchId not in listTouchIds:
            listTouchIds.append(currentTouchId)
      # iterate through the list and add the number of touch operations per touch id to the operation attribute
      for touchId in listTouchIds:
         listOfTouchOp = weldGroup.GetAllTouchOpWithSameTouchId(touchId)
         if any(listOfTouchOp):
            for touchOp in listOfTouchOp:
               if (touchOp != None):
                  SetOperationIntAttribute(touchOp.GetTouchOperation(), AW_EVT_TOUCH_COUNTER, len(listOfTouchOp))

# HELPER - START
# get operation string attribute
def GetOperationStringAttribute(Operation, AttribName):
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetString(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# set operation string attribute
def SetOperationStringAttribute(Operation, AttribName, AttribValue):
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Operation.GetAttribSetter()
      attribSetter.SetString(AttribName, AttribValue, ATTRIBOVERRIDEMODE_DEFAULT)
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

def SetAttributeRecompState(Operation, AttribName):
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      opAttrib.SetReComputeEnterState(ENTERSTATE_NORECOMPUTE)

# set operation int attribute
def SetOperationIntAttribute(Operation, AttribName, AttribValue):
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Operation.GetAttribSetter()
      attribSetter.SetInteger(AttribName, AttribValue, ATTRIBOVERRIDEMODE_DEFAULT)
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

# return the touch ID of an existing touch operation
def GetConnectIdOfTouchOperation(Operation):
   if (Operation != None):
      # get touch ID from operation and return
      touchId = GetOperationIntAttribute(Operation, AW_EVT_TOUCH_ID)
      return touchId
   # else return 0
   return 0

# get operation int attribute
def GetOperationIntAttribute(Operation, AttribName):
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetInteger(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# WeldingGroup: class with links to multiple operations
# a welding group contains all welding operations and touch operation which belong together.
class WeldingGroup:
   def __init__(self, operation, teachHandler, eventHandler):
      # local event handler
      self.__eventHandler = eventHandler
      # welding operation
      self.__referenceWeldingOperation = operation
      self.__weldingOperations = []
      self.__weldingOperations.append(operation)
      # get uuid of the welding operation
      self.__processGeometryIdentifier = operation.GetProcessGeometryIdentifier()
      # list of class TouchOperation 
      self.__touchOperations = []
      # welding group number
      self.__groupNumber = 0

   # return all touch operations with the same touch ID
   def GetAllTouchOpWithSameTouchId(self, Id):
      listOfTouchOp = []
      for touchOperation in self.__touchOperations:
         touchId = touchOperation.GetTouchId()
         if touchId == Id:
            listOfTouchOp.append(touchOperation)
      return listOfTouchOp

   # add a touch operation to the lit of touch operations
   def AddTouchOperation(self, operation):
      # new instance of touch operation
      touchOp = TouchOperation(operation, self.__eventHandler)
      # add instance of TouchOperation to the touch operation list
      self.__touchOperations.append(touchOp)
   
   # add a welding operation to the welding group
   def AddWeldingOperation(self, operation):
      self.__weldingOperations.append(operation)

   # return the unique identifier of the welding group
   def GetIdentifier(self):
      return self.__processGeometryIdentifier

   # return the welding operation
   def GetWeldingOperations(self):
      return self.__weldingOperations

   # return a list of class TouchOperation
   def GetTouchOperations(self):
      return self.__touchOperations

   # set the welding group number
   def SetWeldingGroupNumber(self, number):
      self.__groupNumber = number

   # get the welding group number
   def GetWeldingGroupNumber(self):
      return self.__groupNumber

# TouchOperation: class with all necessary information about a touch sensing operation.
class TouchOperation:
   def __init__(self, operation, eventHandler):
      # touch operation
      self.__touchOperation = operation
      # event handler
      self.__eventHandler = eventHandler

      if connectionType != AW_CONNECT_OPERATION:
         # collision point of touch operation; only used if connection type is "shortest distance"
         self.__tpeTouchOpCollisionPoint = self.__FindCollisionTpeInTouchOperation(self.__touchOperation)
         if self.__tpeTouchOpCollisionPoint == None:
            raise "couldn't find collision toolpath element while initialize TouchOperation"
      # first automatically created touch point of the touch operation 
      self.__tpeTouchOpStartPoint = self.__FindStartTpeInTouchOperation(self.__touchOperation)
      if self.__FindStartTpeInTouchOperation == None:
         raise "couldn't find start toolpath element while initialize TouchOperation"
      # if touch connection type is operation or start end, the touch operation can be added to start or end process point.
      # this is added to further operations, using the same calibration by touch.
      # self.__belongsTwoStartPoint = True
      self.__connectEvent = None
      self.__touchId = 0

   # get the touch event
   def SetTouchId(self, EventHandler):
      for tpe in self.__touchOperation.GetTpElements():
         connectEventProcessPoint = EventHandler.GetEventsByName(tpe, TOUCH_CONNECT_EVENT)
         if any(connectEventProcessPoint):
            # get touch id
            self.__touchId = connectEventProcessPoint[0].GetString(AW_EVT_TOUCH_ID)
            self.__connectEvent = connectEventProcessPoint[0]
            return True
      return False

   # get the touch event
   def GetConnectEvent(self):
      return self.__connectEvent

   # get touch ID from touch operation
   def GetTouchId(self):
      return GetConnectIdOfTouchOperation(self.GetTouchOperation())

   # find the collision point inside the touch operation
   def __FindCollisionTpeInTouchOperation(self, operation):
      # iterate through toolpath elements of the touch operation
      for tpe in operation.GetTpElements():
         # find toolpath element with collision event
         touchCollisionPointEvent = self.__eventHandler.GetEventsByName(tpe, TS_POINT_IDENTIFIER_COLLISION)
         # check if event exists
         if any(touchCollisionPointEvent):
            # found collision point, return the toolpath element
            return tpe
      # if no collision event was found, return null
      return None

   # find the collision point inside the touch operation
   def __FindStartTpeInTouchOperation(self, operation):
      # iterate through toolpath elements of the touch operation
      for tpe in operation.GetTpElements():
         if (tpe.GetProcessType() == TPPROCESSTYPE_EXPLODEDCYCLE):
            # found first exploded cycle point, return the toolpath element
            return tpe
      # if no exploded cycle point was found, return null
      return None

   # get the touch operation
   def GetTouchOperation(self):
      return self.__touchOperation
