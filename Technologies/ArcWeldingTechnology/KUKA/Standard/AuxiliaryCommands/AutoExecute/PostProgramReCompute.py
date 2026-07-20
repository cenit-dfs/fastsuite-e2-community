# -------------------------------------------------------------------------------------------
# Name: arc welding connect touch points and process points automatically
# Description: 
# Debug info: E2@localhost:5254
# Author: CENIT AG
# Changelog:
#     Version: 1.0
#        Changed by:
#        Date: 
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
from cenpylib import *
from cenpylib.stubs.CENPyOlpTpElement import CENPyOlpTpElement
from cenpylib.stubs.CENPyOlpEventHandler import CENPyOlpEventHandler
from centypes import *
import math
import sys, os, inspect
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\AutoExecute\\")

# attributes
WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"
AW_TOUCHSENS_CONNECTION_TYPE = "TSConnectionType"
AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
AW_GLOBAL_TOUCH_COUNTER = "AWGlobalTouchCounter"
AW_TOUCHSENS_CONNECT_TYPE = "TSConnectionType"
AW_TOUCHSENS_OPERATIONS_SORTED = "TSOperationsSorted"
# CONSTANTS
AW_CONNECT_OPERATION = 0
AW_CONNECT_START_END = 1
AW_CONNECT_SHORTEST_DISTANCE = 2
AW_CONNECT_FRAME3P = 3
AW_CONNECT_NO = 4
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
AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP = "AvoidTouchIdWithoutTouchOp"
# event attributes
AW_EVT_TOUCH_ID = "TouchId"
AW_EVT_TOUCH_COUNTER = "Touch_Cntr"
# operation attribute, needed for the naming of the operations
AW_WELDING_GROUP = "WeldingGroup"

AW_TOUCHSENS_FRAME_PT="FramePt"
# each welding group will get a number to identify the touch
# and welding operation which belong to this group
weldingGroupNr = 0

def GetCommandName():
   return "PostProgramReCompute"
   
def GetCommandUuId():
   return "91D3CC91-565E-4D87-9B2C-FA551B6E2D30"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator: CENPyOlpProgramModifyOperator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogDebug("PostProgramProcessGeometry.py: Execution started.")
   global OnTouchPointLog
   global OnDevLog
   global GlobalLogging
   OnTouchPointLog = True
   OnDevLog = False
   GlobalLogging = logging

   # -- SEQUENCE --
   # 0) get last programmed operations
   # 1) check if connection type is no
   # 2) sort operation in weld operations and touch operations
   # 3) create WeldingGroups, based on welding operation process geometry identifier
   # 4) add touch operations to the welding groups
   # 5) check if connection type
   # 6) remove all connect events
   # 7) add connection events depending on connection type

   # -------------------------------------
   # 0) get user selection
   # -------------------------------------
   # get active program
   program = Operator.GetActiveProgram()

   # global variable
   global gConnectionType
   # gConnectionType  = AW_CONNECT_OPERATION
   gConnectionType = GetProgramEnumAttribute(program, AW_TOUCHSENS_CONNECT_TYPE)

   # global variable
   global gOperationsSorted
   # AW_TOUCHSENS_OPERATIONS_SORTED = "TSOperationsSorted"
   gOperationsSorted = GetProgramBoolAttribute(program, AW_TOUCHSENS_OPERATIONS_SORTED)
   
   # global variable
   global gHighestFoundTouchId
   gHighestFoundTouchId = 0
   global gLastFoundTouchId
   gLastFoundTouchId = 0

   if (gConnectionType == None):
      logging.LogError("PostProgramReCompute.py: could not get connection type from program. Execution aborted.")
      return
   # AW_CONNECT_OPERATION = 0
   # AW_CONNECT_START_END = 1
   # AW_CONNECT_SHORTEST_DISTANCE = 2 // missing: ignore box welding points
   # AW_CONNECT_NO = 3
   
   # -------------------------------------
   # 1) check if connection type no
   # -------------------------------------
   if (gConnectionType == AW_CONNECT_NO):
      return

   # get all operations
   operations = program.GetOperations()
   # get all operations
   opGroups = program.GetOperationGroups()
   # get teach handler
   teachHandler = Operator.GetTeachHandler()
   # get event handler
   eventHandler = Operator.GetEventHandler()

   # -------------------------------------
   # 2) sorting operations in welding and touch operations
   # -------------------------------------
   # if welding operation has no touch points, add the welding operation to the previews welding group with touch points
   lastProgrammedTouchOps = []
   lastProgrammedWeldingOps = []
   touchOps = []
   weldingOps = []
   # touchOps & weldingOps : List of the Operations AND its original OpGroup-Origin [operation, int]
   grCnt = 0
   for opGroup in opGroups:
      grCnt = grCnt + 1
      operations = opGroup.GetOperations()
      for operation in operations:
         lastProgrammedOperation = GetOperationBoolAttribute(operation, "TSLastComputedOperation")
         workMethodName = GetOperationStringAttribute(operation, WORKMETHOD_NAME)
         if gOperationsSorted == True:
            # if gOperationsSorted is True, don´t take GroupNumbers into Account --> always "0"
            grCnt = 0
         OpAndGroup = [operation, grCnt]
         if workMethodName in [WM_TOUCH, WM_SEAM]:
            touchOps.append(OpAndGroup)
            foundTouchId = GetOperationIntAttribute(operation, "TouchId")
            if foundTouchId > 0:
               gLastFoundTouchId = foundTouchId
            if foundTouchId > gHighestFoundTouchId:
               gHighestFoundTouchId = foundTouchId
            if lastProgrammedOperation == True:
               lastProgrammedTouchOps.append(operation)
         elif (workMethodName == WM_STICH) or (workMethodName == WM_CONTINUES):
            weldingOps.append(OpAndGroup)
            if lastProgrammedOperation == True:
               lastProgrammedWeldingOps.append(operation)
   
   # -------------------------------------
   # 3) create list with welding groups to add TouchID and ConnectEvents
   # -------------------------------------
   weldingGroups = []
   if (len(lastProgrammedWeldingOps) == 0 and len(lastProgrammedTouchOps) == 0):
      # no new OPs, nothing programmed, just return 
      return
   elif (len(lastProgrammedWeldingOps) != 0 and len(lastProgrammedTouchOps) == 0):
      # check previews welding operation if there are touch points exists
      allWeldingGroups = CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps)
      weldingGroups = GetWeldingGroupsWithWeldingOp(allWeldingGroups, lastProgrammedWeldingOps)
      pass
   elif (len(lastProgrammedWeldingOps) == 0 and len(lastProgrammedTouchOps) != 0):
      # only added a touch sensing operation, check which welding group is affected
      # find corresponding welding operation
      allWeldingGroups = CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps)
      weldingGroups = GetWeldingGroupsWithTouchOp(allWeldingGroups, lastProgrammedTouchOps)
   elif (len(lastProgrammedWeldingOps) != 0 and len(lastProgrammedTouchOps) != 0):
      # complete new welding operation including touch sensing
      weldingGroups = CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps)

   # was any welding operation found?
   if len(weldingGroups) == 0:
      return

   # ======================================================================================
   # re-set the attribute for last-computed-operations
   for lastProgrammedTouchOp in lastProgrammedTouchOps:
      SetOperationBoolAttribute(lastProgrammedTouchOp, "TSLastComputedOperation", False)
   for lastProgrammedWeldingOp in lastProgrammedWeldingOps:
      SetOperationBoolAttribute(lastProgrammedWeldingOp, "TSLastComputedOperation", False)
   # ======================================================================================

   # -------------------------------------
   # 5) check connection type
   # -------------------------------------
   if (gConnectionType == AW_CONNECT_OPERATION):
      # remove all connect events
      RemoveConnectEventsFromWeldingGroups(eventHandler, weldingGroups)
      # create connect events at first process point and connect touch points to first process point
      ConnectionType_Operation(logging, eventHandler, teachHandler, program, weldingGroups)
   elif (gConnectionType == AW_CONNECT_START_END):
      # remove all connect events
      RemoveConnectEventsFromWeldingGroups(eventHandler, weldingGroups)
      # create connect events at first/last process point and connect touch points to start/end
      ConnectionType_StartEnd(logging, eventHandler, teachHandler, program, weldingGroups)
   elif (gConnectionType == AW_CONNECT_SHORTEST_DISTANCE):
      # remove all connect events
      RemoveConnectEventsFromWeldingGroups(eventHandler, weldingGroups)
      # create connect events at first/last process point and connect touch points to start/end
      ConnectionType_ShortestDistance(logging, eventHandler, teachHandler, program, weldingGroups)
   elif (gConnectionType == AW_CONNECT_FRAME3P):
      # remove all connect events
      RemoveConnectEventsFromWeldingGroups(eventHandler, weldingGroups)
      # create connect events at first/last process point and connect touch points to start/end
      ConnectionType_Frame3P(logging, eventHandler, teachHandler, program, weldingGroups)
   elif (gConnectionType == AW_CONNECT_NO):
      # n.t.d., early return
      return

   # get the number of each welding group and set it as string to the several operations
   for weldingGroup in weldingGroups:
      wgNumber = weldingGroup.GetWeldingGroupNumber()
      # create the string
      opName = "WG" + str(wgNumber) + "_"
      # get welding and touch operations an set the string as attribute
      weldingOps = weldingGroup.GetWeldingOperations()
      for weldingOp in weldingOps:
         SetOperationStringAttribute(weldingOp, AW_WELDING_GROUP, opName)
      touchOps = weldingGroup.GetTouchOperations()
      for touchOp in touchOps:
         SetOperationStringAttribute(touchOp.GetTouchOperation(), AW_WELDING_GROUP, opName)

   logging.LogDebug("PostProgramProcessGeometry.py: Execution ended.")
   return
# --------------------------- End of ModifyActiveProgram -------------------------------------

# --------------------------------------------------------------------------------------------
def CreateWeldingGroups(teachHandler, eventHandler, logging, program, weldingOps, touchOps):
   # if a welding operation has no corresponding touch operation,
   # the welding operation will be added to the previous welding group
   # touchOps & weldingOps : List of the Operations AND its original OpGroup-Origin [operation, int]
   weldingGroups = []
   # temp. List with WeldingOps Origin
   origWeldGrp = []
   # init last weld group; save weld group of the operation before
   lastWeldGroup = None
   # check if a touch operation belongs to the welding operation, otherwise add the welding operation belongs to the welding group before
   currentWeldGroup = None
   # for storing last Weld Geo Identifier (trans/rot/mirr TP has always the same Geo Identifier)
   lastWeldGeoUuid = None
   weldingGroupNr = 0
   avoidTouchIdWithoutTouchOp = GetProgramBoolAttribute(program, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   # iterate through all welding operations
   for weldingOp in weldingOps:
      weldGeoUuid = weldingOp[0].GetProcessGeometryIdentifier()
      # init variable found touch corresponding touch operation
      touchOperationFound = False
      # check for TouchOp only if different WeldContour
      if lastWeldGeoUuid != weldGeoUuid:
         for tOp in touchOps:
            # check Geo Identifier
            if (tOp[0].GetProcessGeometryIdentifier() == weldGeoUuid):
               # corresponding touch operation was found
               touchOperationFound = True
               lastWeldGeoUuid = weldGeoUuid
               break
      # go for highest existing TouchID (it's a String !!) 
      # Loop through all Op-TPEs to get TOUCH_CONNECT_EVENT and its TouchID
      weldTpes = weldingOp[0].GetTpElements()
      wgNumber = 0
      for weldTpe in weldTpes:
         # check if process point is process point
         events = []
         events = eventHandler.GetEventsByName(weldTpe, TOUCH_CONNECT_EVENT)
         if any(events):
            for curEvent in events:
               strTouchNr = curEvent.GetString(AW_EVT_TOUCH_ID)
               wgNumber = int(strTouchNr)
      
      # store the TouchID from currenet OP, if it is bigger
      if wgNumber > weldingGroupNr:
         weldingGroupNr = wgNumber
      
      # continue with next OP if it was already analysed
      isNew = GetOperationBoolAttribute(weldingOp[0], "TSLastComputedOperation")
      if isNew == False:
         continue
      
      # if corresponding touch operation was found, create a new welding group
      # WeldingOP(s) without TouchOp(s) in Group : add to last Weld/Touch-Group and put Connect-Event with prev. TouchID
      # OR create a new WeldingGroup to avoid adding Connect-Event to single SeamOPs #49383
      # Settings.xml : <Attribute Name="AvoidTouchIdWithoutTouchOp" Order="8" Value="true" Visibility="false" Icon="OLP_Param_TouchWeldConnection" />
      # avoidTouchIdWithoutTouchOp = GetProgramBoolAttribute(program, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
      if avoidTouchIdWithoutTouchOp == False:
         touchOperationFound = True
      if touchOperationFound == True or avoidTouchIdWithoutTouchOp == True:
         # create new welding groups with welding operation
         currentWeldGroup = WeldingGroup(weldingOp[0], teachHandler, eventHandler)
         # increase the welding group number and set it to the new group
         weldingGroupNr += 1
         currentWeldGroup.SetWeldingGroupNumber(weldingGroupNr)
         #logging.LogInfo('***********************currentWeldGroup.SetWeldingGroupNumber(__' + str(weldingGroupNr) + '__)')
         weldingGroups.append(currentWeldGroup)
         origWeldGrp.append(weldingOp[1])
      else:
         # if connection type is shortest distance, each welding operation must have it's own corresponding touch operation
         # a mix is not supported. In that case all already created events are removed and execution is aborted.
         if gConnectionType == AW_CONNECT_SHORTEST_DISTANCE:
            logging.LogError("You selected connection type shortest distance, but a welding operation has no linked touch operation. Mix is not possible.")
            # RemoveAllConnectEvents(eventHandler, program)
            return None
         # add the current WeldingOperation from lastProgrammedList to the last WeldingGroup
         if len(weldingGroups) != 0:
            weldingGroups[len(weldingGroups)-1].AddWeldingOperation(weldingOp[0])

   # add touch operations to welding groups 
   for touchOp in touchOps:
      # only take TSLastComputedOperation into Account
      isNew = GetOperationBoolAttribute(touchOp[0], "TSLastComputedOperation")
      if isNew == False:
         continue

      touchOpIdentifier = touchOp[0].GetProcessGeometryIdentifier()
      gotIt = 0
      iC = 0
      for weldingGroup in weldingGroups:
         # loop through Welding Groups and search for same ProcessGeomID and same Group-Origin
         iC = iC + 1
         if (touchOpIdentifier == weldingGroup.GetIdentifier()) and (origWeldGrp[iC-1] == touchOp[1]):
            # ProcessGeometryId fits AND original GroupNumbers
            weldingGroup.AddTouchOperation(touchOp[0])
            gotIt = 1
            break
      if gotIt == 0:
          iC = 0
          # didn´t find a Match before -> loop through Welding Groups and search for same ProcessGeomID
          for weldingGroup in weldingGroups:
             iC = iC + 1
             if (touchOpIdentifier == weldingGroup.GetIdentifier()):
                # only ProcessGeometryId fits
                weldingGroup.AddTouchOperation(touchOp[0])
                break
   return weldingGroups


# --------------------------------------------------------------------------------------------
def GetWeldingGroupsWithTouchOp(AllWeldingGroups, LastProgrammedTouchOps):
   weldingGroups = []
   # iterate through the new created touch operations
   for lastProgrammedTouchOp in LastProgrammedTouchOps:
      for weldingGroup in AllWeldingGroups:
         if lastProgrammedTouchOp.GetProcessGeometryIdentifier() == weldingGroup.GetIdentifier():
            weldingGroupIsAlreadyInList = False
            # check if the there are two touch operation belong to the same operation. If yes then only add that welding group once
            for changedWeldingGroup in weldingGroups:
               # check if the found welding group is already in the list
               if changedWeldingGroup.GetIdentifier() == weldingGroup.GetIdentifier():
                  # set the found welding group is already in the welding group list
                  weldingGroupIsAlreadyInList = True
                  break
            if weldingGroupIsAlreadyInList == False:
               weldingGroups.append(weldingGroup)
            break
   return weldingGroups

def GetWeldingGroupsWithWeldingOp(AllWeldingGroups, LastProgrammedWeldingOps):
   weldingGroups = []
   # iterate through the new created touch operations
   for lastProgrammedWeldingOp in LastProgrammedWeldingOps:
      for weldingGroup in AllWeldingGroups:
         if weldingGroup.HasWeldingOperation(lastProgrammedWeldingOp):
            weldingGroupIsAlreadyInList = False
            # check if the there are two touch operation belong to the same operation. If yes then only add that welding group once
            for changedWeldingGroup in weldingGroups:
               # check if the found welding group is already in the list
               if changedWeldingGroup.HasWeldingOperation(lastProgrammedWeldingOp):
                  # set the found welding group is already in the welding group list
                  weldingGroupIsAlreadyInList = True
                  break
            if weldingGroupIsAlreadyInList == False:
               weldingGroups.append(weldingGroup)
            break
   return weldingGroups

# --------------------------------------------------------------------------------------------
# create connect events at first process point and connect touch points to first process point
def ConnectionType_Operation(Logging, EventHandler, TeachHandler, Program, WeldingGroups):
# --------------------------------------------------------------------------------------------
   # iterate though each welding group
   avoidTouchIdWithoutTouchOp = GetProgramBoolAttribute(Program, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   attTouchCnt = (GetProgramIntegerAttribute(Program, AW_GLOBAL_TOUCH_COUNTER) or 0) - 1
   grpAdd = 0
   for weldingGroup in WeldingGroups:
      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()
      # use GroupNumber (from CreateWeldingGroups) for TouchID
      if weldingGroup.GetWeldingGroupNumber() < attTouchCnt:
         counter = attTouchCnt + grpAdd + weldingGroup.GetWeldingGroupNumber()  # 1st Hit
      else:
         counter = weldingGroup.GetWeldingGroupNumber()+ grpAdd  # already upcount in CreateWeldingGroups
      #Logging.LogInfo('...................................counter = ' + str(counter) + ' from ' + str(weldingGroup.GetWeldingGroupNumber()))
      # iterate through touch operations
      groupHasTouchOps = False
      for touchOperation in touchOperations:
         # add the connection ID to the touch operation
         AddConnectionIdToOperation(touchOperation, counter)
         groupHasTouchOps = True
      grpAdd += 1
      # get all first process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for processTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
         # add connect event to the first and last toolpath element
         # ...but only if OpGroup contains TouchOp(s) #49383   ...but it might be desired
         if groupHasTouchOps == False and avoidTouchIdWithoutTouchOp == False:
            counter = gLastFoundTouchId
            groupHasTouchOps = True
         if groupHasTouchOps == True or avoidTouchIdWithoutTouchOp == False:
            event = AddConnectEvent(EventHandler, processTpe, counter)
            if event == None:
               Logging.LogError("could not add connect event.")

# --------------------------------------------------------------------------------------------
# create connect events at first/last process point and connect touch points to start/end
def ConnectionType_StartEnd(Logging, EventHandler, TeachHandler, Program, WeldingGroups):
# --------------------------------------------------------------------------------------------
   # check to which process point the touch points belong with reference welding operation
   # set "TouchPointBelongsTo variable in touch operation"
   # set touch connection events also to the other welding operations in the welding group

   avoidTouchIdWithoutTouchOp = GetProgramBoolAttribute(Program, AW_AVOID_TOUCHID_EVENT_WITHOUT_TOUCHOP)
   # iterate though each welding group
   attTouchCnt = (GetProgramIntegerAttribute(Program, AW_GLOBAL_TOUCH_COUNTER) or 0)
   grpAdd = 0
   for weldingGroup in WeldingGroups:

      # init first and last toolpath element with none to check later if successful
      firstProcessTpe = weldingGroup.GetFirstProcessTpeOfReferenceWeldingOperation()
      lastProcessTpe = weldingGroup.GetLastProcessTpeOfReferenceWeldingOperation()

      # Plausibility checks - check if there is only one process toolpath element
      if firstProcessTpe == lastProcessTpe:
         Logging.LogError("first and last process toolpath element are equal. Not supported yet.")
         return
      # Plausibility checks - check if both toolpath elements found
      if (firstProcessTpe == None) or (lastProcessTpe == None):
         Logging.LogError("Couldn't find fist or last process toolpath element")
         return
      
      # ID counter for first/last process toolpath element
      if weldingGroup.GetWeldingGroupNumber() < attTouchCnt:
         # GetWeldingGroupNumber = 0 --> DfltID
         counterFirstProcessTpe = attTouchCnt + grpAdd + weldingGroup.GetWeldingGroupNumber() - 1
         counterLastProcessTpe = attTouchCnt + grpAdd + weldingGroup.GetWeldingGroupNumber()
      else:
         # GetWeldingGroupNumber already increased : 1/2 --> 3
         counterFirstProcessTpe = weldingGroup.GetWeldingGroupNumber() + grpAdd
         counterLastProcessTpe = weldingGroup.GetWeldingGroupNumber() + grpAdd + 1
      #Logging.LogInfo('...................................counterFirstProcessTpe = ' + str(counterFirstProcessTpe) + ' from ' + str(weldingGroup.GetWeldingGroupNumber()))
      #Logging.LogInfo('...................................counterLastProcessTpe = ' + str(counterLastProcessTpe) + ' from ' + str(weldingGroup.GetWeldingGroupNumber()))
      grpAdd += 1

      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()
      groupHasTouchOps = False
      bTouchToFirst = False
      bTouchToLast = False

      # iterate through touch operations
      for touchOperation in touchOperations:
         groupHasTouchOps = True
         # get the collision points to calculate the distance to the process point
         collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()

         # get the distance to the first and last process point
         distanceToFirstTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, firstProcessTpe)
         distanceToLastTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, lastProcessTpe)

         # check shortest distance
         if (distanceToFirstTpe <= distanceToLastTpe):
            # add the connection ID to the touch operation
            # shortest distance to first process point
            AddConnectionIdToOperation(touchOperation, counterFirstProcessTpe)
            bTouchToFirst = True
         else:
            # add the connection ID to the touch operation
            # shortest distance to last process point
            AddConnectionIdToOperation(touchOperation, counterLastProcessTpe)
            bTouchToLast = True
      
      # check if TouchOPs ID are set for Start and End
      refOP = weldingGroup.GetReferenceWeldingOperation()
      if groupHasTouchOps == True:
         if bTouchToFirst == False:
            Logging.LogWarn("TouchConnect : could not find suitable TouchOperation to Start-TPE of Operation ''" + str(refOP.GetName()) + "''")
         if bTouchToLast == False:
            Logging.LogWarn("TouchConnect : could not find suitable TouchOperation to End-TPE of Operation ''" + str(refOP.GetName()) + "''")
      
      # if TouchConnect Event should be set also to single Seam OP
      if groupHasTouchOps == False and avoidTouchIdWithoutTouchOp == False:
         counterFirstProcessTpe = gLastFoundTouchId
         counterLastProcessTpe = gLastFoundTouchId + 1
         groupHasTouchOps = True
      # if there are no Touching, n.t.d., return
      if groupHasTouchOps == False:
         return
      
      # get all first process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for firstTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
         event = AddConnectEvent(EventHandler, firstTpe, counterFirstProcessTpe)
         if event == None:
            Logging.LogError("TouchConnect : could not add connect event.")
      # get all last process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for lastTpe in weldingGroup.GetAllLastProcessTpesOfAllWeldingOperation():
         event = AddConnectEvent(EventHandler, lastTpe, counterLastProcessTpe)
         if event == None:
            Logging.LogError("TouchConnect : could not add connect event.")

# --------------------------------------------------------------------------------------------
# create connect events at first/last process point and connect touch points to start/end
def ConnectionType_ShortestDistance(Logging, EventHandler, TeachHandler, Program, WeldingGroups):
# --------------------------------------------------------------------------------------------
   # iterate though each welding group
   attTouchCnt = (GetProgramIntegerAttribute(Program, AW_GLOBAL_TOUCH_COUNTER) or 0) - 1
   for weldingGroup in WeldingGroups:
      # get welding operation 
      weldingOperations = weldingGroup.GetReferenceWeldingOperation()
      # get all toolpath elements from the current welding operation
      weldingTpes = weldingOperations.GetTpElements()

      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()

      # use GroupNumber (from CreateWeldingGroups) for TouchID
      counter = gHighestFoundTouchId
      # loop through TPEs and TouchOps and only set TouchIds and Events on TPEs that has really a shortest Distance
      HasTpeShortestDistance(EventHandler, TeachHandler, weldingTpes, touchOperations, counter)
      # old Option until R2024.2
      # TouchIdForTpeShortestDistance(Logging, EventHandler, TeachHandler, weldingTpes, touchOperations, counter)

def HasTpeShortestDistance(EventHandler, TeachHandler, weldingTpes, touchOperations, counter):
   # check if TPE has shortest Distance to a TouchOP
   shortestProcessPoint = None
   for touchOperation in touchOperations:
      # loop through the TouchOps to get nearest Seam-TPE
      collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()
      shortestDistance = 999999.9
      for weldingTpe in weldingTpes:
         currentDistance = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, weldingTpe)
         if currentDistance < shortestDistance:
            shortestDistance = currentDistance
            shortestProcessPoint = weldingTpe
      # if the TouchOp shortest Point was found
      if shortestProcessPoint != None:
         # check if the Seam-TPE has already a TouchID
         connectEventProcessPoint = EventHandler.GetEventsByName(shortestProcessPoint, TOUCH_CONNECT_EVENT)
         if any(connectEventProcessPoint):
            # ... if true, use the ID
            counter = int(connectEventProcessPoint[0].GetString(AW_EVT_TOUCH_ID))
         else:
            # upcount the ID for next
            counter += 1
            # add connect event to the desired Seam-TPE
            AddConnectEvent(EventHandler, shortestProcessPoint, counter)
         # add the TouchId to the TouchOP
         AddConnectionIdToOperation(touchOperation, counter)

def TouchIdForTpeShortestDistance(Logging, EventHandler, TeachHandler, weldingTpes, touchOperations, counter):
   # old Version (pre R2024.2) TouchConnect-Event on each TPE
   for weldingTpe in weldingTpes:
      # add event to each process point
      if weldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE:
         # increment counter
         counter += 1
         event = AddConnectEvent(EventHandler, weldingTpe, counter)
         if event == None:
            Logging.LogError("could not add connect event.")

   # iterate through touch operations
   for touchOperation in touchOperations:
      # init distance
      shortestDistance = 999999.9
      # get the collision points to calculate the distance to the process point
      collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()
      # init shortest process toolpath element
      shortestProcessPoint = None
      # iterate through all welding TPEs
      for weldingTpe in weldingTpes:
         if weldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE:
            # get the distance to the first and last process point
            currentDistance = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, weldingTpe)
            # if the calculated distance is shorter than the shortest distance before,
            # temp save the toolpath element and update shortest distance variable
            if currentDistance < shortestDistance:
               shortestDistance = currentDistance
               shortestProcessPoint = weldingTpe
      # if shortest point was found
      if shortestProcessPoint != None:
         # get the already added connect event of the process TPE and read the TouchID
         connectEventProcessPoint = EventHandler.GetEventsByName(shortestProcessPoint, TOUCH_CONNECT_EVENT)
         if any(connectEventProcessPoint):
            # get TouchID from shortest ProcessPoint's TouchConnect-Event
            touchId = connectEventProcessPoint[0].GetString(AW_EVT_TOUCH_ID)
            # add the connection ID to the touch operation
            AddConnectionIdToOperation(touchOperation, touchId)
      else:
         Logging.LogError("Touch operation couldn't find the shortest process toolpath element.")

# --------------------------------------------------------------------------------------------
# create connect events at first/last process point and connect touch points to start/end
def ConnectionType_Frame3P(Logging, EventHandler, TeachHandler, Program, WeldingGroups):
# --------------------------------------------------------------------------------------------
   # check to which process point the touch points belong with reference welding operation
   # set "TouchPointBelongsTo variable in touch operation"
   # set touch connection events also to the other welding operations in the welding group
      
   # iterate though each welding group
   attTouchCnt = (GetProgramIntegerAttribute(Program, AW_GLOBAL_TOUCH_COUNTER) or 0) - 1
   grpAdd = 0
   for weldingGroup in WeldingGroups:
      
      # ID counter for first/last process toolpath element
      if weldingGroup.GetWeldingGroupNumber() < attTouchCnt:
         counterProcessTpe = attTouchCnt + grpAdd + weldingGroup.GetWeldingGroupNumber()  # 1st Hit
      else:
         counterProcessTpe = weldingGroup.GetWeldingGroupNumber()+ grpAdd  # already upcount in CreateWeldingGroups
      #Logging.LogInfo('...................................counterProcessTpe = ' + str(counterProcessTpe) + ' from ' + str(weldingGroup.GetWeldingGroupNumber()))
      # Flag to control TouchConnectEvent at EndTPE or not
      setEndEvent = False

      # init first and last toolpath element with none to check later if successful
      firstProcessTpe = weldingGroup.GetFirstProcessTpeOfReferenceWeldingOperation()
      lastProcessTpe = weldingGroup.GetLastProcessTpeOfReferenceWeldingOperation()

      # Plausibility checks - check if there is only one process toolpath element
      if firstProcessTpe == lastProcessTpe:
         Logging.LogError("first and last process toolpath element are equal. Not supported yet.")
         return

      # Plausibility checks - check if both toolpath elements found
      if (firstProcessTpe == None) or (lastProcessTpe == None):
         Logging.LogError("Couldn't find fist or last process toolpath element")
         return
      
      DevLogging('==================  ConnectionType_Frame3P  =======================')
      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()
      TouchPointLogging('============================= TouchSensing Information ===================================')
      TouchPointLogging('=')
      if (len(touchOperations) < 1 ):
         DevLogging('..................ConnectionType ''3-Point-Frame'' : no Touch-Operations given. Abort.')
         Logging.LogError('ConnectionType ''3-Point-Frame'' : no Touch-Operations given. Abort.')
         return
      if (len(touchOperations) == 1 ):
         TouchPointLogging('=   ConnectionType ''3-Point-Frame'' : ONE Touch-Operation found. Calibrate in one Direction relative to BaseFrame.')
      if (len(touchOperations) == 2 ):
         TouchPointLogging('=   ConnectionType ''3-Point-Frame'' : TWO Touch-Operations found. Calibrate in ??? relative to BaseFrame.')
      if (len(touchOperations) > 2 ):
         TouchPointLogging('=   ConnectionType ''3-Point-Frame'' : ' + str(len(touchOperations)) + ' Touch-Operations found. Calibrate in ??? relative to BaseFrame.')
      TouchPointLogging('=')

      takeNewProcedure = True
      if takeNewProcedure == True:
         iDummy = 0
         New_Frame3P_Procedure(Logging, EventHandler, TeachHandler, touchOperations, weldingGroup, firstProcessTpe, lastProcessTpe, counterProcessTpe, setEndEvent)
         TouchPointLogging('-------------------------------------------- End of Touch Point Analysis -----------------------------------------------')
      else:
         if (len(touchOperations) < 3 ):
            Logging.LogError("ConnectionType ''3-Point-Frame'' needs at least three touch points. Please modify the operation or select another connection type.")
            return
         Current_Frame3P_Procedure(Logging, EventHandler, TeachHandler, touchOperations, weldingGroup, firstProcessTpe, lastProcessTpe, counterProcessTpe, setEndEvent)
      grpAdd += 1

# ------- new Stuff ----------------------------------------------------------------------------------------------------------------
def New_Frame3P_Procedure(Logging, EventHandler, TeachHandler, touchOperations, weldingGroup, firstProcessTpe, lastProcessTpe, counterProcessTpe, setEndEvent):
   ''' new Procedure to handle TouchOperations for 3-Point-Frame'''
   DevLogging('~~~~~~~~~~~~~~ ConnectionType ''3-Point-Frame'' : New_Frame3P_Procedure')
   logString ='=   Touch Point Analysis :\n'
   # !!!!!!! Condition for the third Point of Frame : half the Distance between Start and End of the Contour !!!!!!
   # halfDistStartToEnd = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, firstProcessTpe, lastProcessTpe) / 2
   # nrOfStart = 0
   # nrOfEnd = 0
   # nrOf3rdPt = 0
   # for top in touchOperations:
      
   #    collisionTpe = top.GetCollisionTpeInTouchOperation()
   #    topName = top.GetTouchOPName()
   #    cpName = collisionTpe.GetName()
   #    stName = firstProcessTpe.GetName()
   #    endName = lastProcessTpe.GetName()
   #    distToStart = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, firstProcessTpe, collisionTpe)
   #    distToEnd = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, lastProcessTpe, collisionTpe)

   #    DevLogging('........... TouchOP : ' + str(topName) + '  Distance CollPnt:' + str(cpName) + '<-->StartPnt:' + str(stName) + ' = ' + str(distToStart*1000))
   #    DevLogging('........................................  Distance CollPnt:' + str(cpName) + '<-->EndPnt:' + str(endName) + ' = ' + str(distToEnd*1000))
   #    DevLogging('........................................  Startpnt<-->EndPnt / 2 = ' + str(halfDistStartToEnd*1000))
      
   #    logString += '\t\tTouch-Point ' + str(cpName)
   #    framePtNr = 0
   #    if distToStart > halfDistStartToEnd and distToEnd > halfDistStartToEnd and len(touchOperations) > 3:
   #       DevLogging('............................. TouchPoint 3RD POINT FRAME')
   #       logString += '\tdetected as 3rd-Frame-Point'
   #       nrOf3rdPt += 1
   #       framePtNr = 3
   #    elif distToEnd < distToStart:
   #       DevLogging('............................. TouchPoint to END')
   #       logString += '\tnearest to END\t(' + str(endName) + ')'
   #       nrOfEnd += 1
   #       framePtNr = 2
   #    else:
   #       DevLogging('............................. TouchPoint to START')
   #       logString += '\tnearest to START\t(' + str(stName) + ')'
   #       nrOfStart += 1
   #       framePtNr = 1
   #    logString += '\t ConnectID ' + str(counterProcessTpe) + '\tFramePt ' + str(framePtNr) + '\n'
   #    # ------- add the ConnectID and FramePointNr to the Touch OP ----------
   #    AddConnectionIdToOperation(top, counterProcessTpe)
   #    AddConnectionFramePtToOperation(top, framePtNr)
   # TouchPointLogging(logString)

   # ------------------------------------------------------
   # get all first process toolpath elements of all welding operations in weldingGroup (normally just one)
   # and add the connect event with the same touch id
   for firstTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
      event = AddConnectEvent(EventHandler, firstTpe, counterProcessTpe)
      if event == None:
         Logging.LogError("could not add connect event.")
   # ------------------------------------------------------

# ------ old Stuff -----------------------------------------------------------------------------------------------------------------
def Current_Frame3P_Procedure(Logging, EventHandler, TeachHandler, touchOperations, weldingGroup, firstProcessTpe, lastProcessTpe, counterProcessTpe, setEndEvent):
   ''' current Procedure to handle TouchOperations for 3-Point-Frame'''
   DevLogging('~~~~~~~~~~~~~~ ConnectionType ''3-Point-Frame'' : Current_Frame3P_Procedure')
   if 1 == 1:
      # First Point always FramePt 1
      AddConnectionFramePtToOperation(touchOperations[0], 1)
      # Second Last Point always FramePt 3
      AddConnectionFramePtToOperation(touchOperations[-2], 2)
      # Last Point always FramePt 3
      AddConnectionFramePtToOperation(touchOperations[-1], 3)

      # All other points have FramePt 1 or 2 -> Let's check for closest distance to First and Second Last Point
      if (len(touchOperations) > 3 ):
         collisionTpeFramePt1 = touchOperations[0].GetCollisionTpeInTouchOperation()
         collisionTpeFramePt2 = touchOperations[-2].GetCollisionTpeInTouchOperation()
         
         for i in range(1,len(touchOperations)-2): #DblCheck!
            touchOperation = touchOperations[i]
            collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()
            distanceToFramePt1 = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, collisionTpeFramePt1)
            distanceToFramePt2 = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, collisionTpeFramePt2)
            
            # check shortest distance
            if (distanceToFramePt1 <= distanceToFramePt2):
               # add the connection ID to the touch operation
               # shortest distance to first process point
               AddConnectionFramePtToOperation(touchOperation, 1)
               
            else:
               # add the connection ID to the touch operation
               # shortest distance to last process point
               AddConnectionFramePtToOperation(touchOperation, 2)

      # iterate through touch operations
      for touchOperation in touchOperations:
         # get the collision points to calculate the distance to the process point
         collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()

         # get the distance to the first and last process point
         distanceToFirstTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, firstProcessTpe)
         distanceToLastTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, lastProcessTpe)

         # check shortest distance
         if (distanceToFirstTpe <= distanceToLastTpe):
            # add the connection ID to the touch operation
            # shortest distance to first process point
            AddConnectionIdToOperation(touchOperation, counterProcessTpe)
            
         else:
            # add the connection ID to the touch operation
            # shortest distance to last process point
            AddConnectionIdToOperation(touchOperation, counterProcessTpe)   
         
      # get all first process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for firstTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
         event = AddConnectEvent(EventHandler, firstTpe, counterProcessTpe)
         if event == None:
            Logging.LogError("could not add connect event.")
      # get all last process toolpath elements of all welding operation
      # and add the connect event with the same touch id (...only if required)
      if setEndEvent == True:
         for lastTpe in weldingGroup.GetAllLastProcessTpesOfAllWeldingOperation():
            event = AddConnectEvent(EventHandler, lastTpe, counterProcessTpe)
            if event == None:
               Logging.LogError("could not add connect event.")

      
      DevLogging('-------------------------------------------------------------------')

# ===========================================================================================
# HELPER - START

def DevLogging(info):
   if OnDevLog == True and GlobalLogging != None:
      GlobalLogging.LogInfo(info)
      
def TouchPointLogging(info):
   if OnTouchPointLog == True and GlobalLogging != None:
      GlobalLogging.LogInfo(info)

# get operation bool attribute
def GetOperationBoolAttribute(Operation, AttribName):
   if (Operation == None):
      return None
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetBool(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# set operation bool attribute
def SetOperationBoolAttribute(Operation, AttribName, AttribValue):
   if (Operation == None):
      return False
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Operation.GetAttribSetter()
      attribSetter.SetBool(AttribName, AttribValue, ATTRIBOVERRIDEMODE_DEFAULT)
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

# set operation int attribute
def SetOperationIntAttribute(Operation, AttribName, AttribValue):
   if (Operation == None):
      return False
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Operation.GetAttribSetter()
      attribSetter.SetInteger(AttribName, int(AttribValue), ATTRIBOVERRIDEMODE_DEFAULT)
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

# get operation int attribute
def GetOperationIntAttribute(Operation, AttribName):
   if (Operation == None):
      return None
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetInteger(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# get Program bool attribute
def GetProgramBoolAttribute(Program, AttribName):
   if (Program == None):
      return None
   attribGetter = Program.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetBool(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# get program integer
def GetProgramEnumAttribute(Program, AttribName):
   if (Program == None):
      return None
   attribGetter = Program.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribValue = attribGetter.GetEnumIndex(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# get program integer
def GetProgramIntegerAttribute(Program, AttribName):
   if (Program == None):
      return None
   attribGetter = Program.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib is not None and opAttrib.IsValid():
      attribValue = attribGetter.GetInteger(AttribName)
      # set attribute was successfully
      return attribValue
   else:
      # set attribute was not successfully, maybe attribute doesn't exist
      return None

# set program integer
def SetProgramIntegerAttribute(Program, AttribName, AttribValue):
   if (Program == None):
      return False
   attribGetter = Program.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Program.GetAttribSetter()
      attribSetter.SetInteger(AttribName, AttribValue, ATTRIBOVERRIDEMODE_DEFAULT)
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

# get operation string attribute
def GetOperationStringAttribute(Operation, AttribName):
   if (Operation == None):
      return None
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
   if (Operation == None):
      return False
   attribGetter = Operation.GetAttribGetter()
   opAttrib = attribGetter.GetAttributeByName(AttribName)
   if opAttrib.IsValid():
      attribSetter = Operation.GetAttribSetter()
      attribSetter.SetString(AttribName, AttribValue, ATTRIBOVERRIDEMODE_DEFAULT)
      # force update of operation name
      Operation.UpdateNameFromRule()
      # set attribute was successful
      return True
   else:
      # set attribute was not successful, maybe attribute doesn't exist
      return False

# check if connect event exist and return the touch id
def CheckIfConnectEventExist(EventHandler, Tpe):
   # get connect events
   events = EventHandler.GetEventsByName(Tpe, TOUCH_CONNECT_EVENT)
   # check if event exists
   if any(events):
      # return touch Id
      return events[0]
   # else return 0
   return None

# return the touch ID of an existing touch operation
def GetConnectIdOfTouchOperation(Operation):
   if (Operation != None):
      # get touch ID from operation and return
      touchId = GetOperationIntAttribute(Operation, AW_EVT_TOUCH_ID)
      return touchId
   # else return 0
   return 0

# add connect event with predefined id 
def AddConnectEvent(EventHandler: CENPyOlpEventHandler, Tpe: CENPyOlpTpElement, Id: int):
   connectEvent = EventHandler.AddEventByName(Tpe, TOUCH_CONNECT_EVENT, TPINSERTPOS_INSERTBEFORE)
   connectEvent.SetString(AW_EVT_TOUCH_ID, str(Id))
   # set tangent and tool directions for KUKA touch sensing
   xDir = Tpe.GetInitialPathMatrix().GetXDirection().GetXYZ()
   zDir = Tpe.GetInitialPathMatrix().GetZDirection().GetXYZ()
   connectEvent.SetString('ApprDirX', str(xDir))
   connectEvent.SetString('ApprDirZ', str(zDir))
   return connectEvent

# Set the connection ID to an touch operation
def AddConnectionIdToOperation(TouchOperation, Id):
   SetOperationIntAttribute(TouchOperation.GetTouchOperation(), AW_EVT_TOUCH_ID, Id)


# Set the connection ID to an touch operation
def AddConnectionFramePtToOperation(TouchOperation, Id):
   SetOperationIntAttribute(TouchOperation.GetTouchOperation(), AW_TOUCHSENS_FRAME_PT, Id)
   
   
# delete all connect events in the program
def RemoveAllConnectEvents(EventHandler, Program):
   # get all toolpath elements
   tpes = Program.GetTpElements()
   for tpe in tpes:
      # check if process point is process point
      events = []
      events = EventHandler.GetEventsByName(tpe, TOUCH_CONNECT_EVENT)
      for i, event in enumerate(events):
         EventHandler.RemoveEvent(tpe, events[i])

# delete all connect events in the program
def RemoveConnectEventsFromWeldingGroups(EventHandler, WeldingGroups):
   # get all toolpath elements
   for weldingGroup in WeldingGroups:
      for weldingOp in weldingGroup.GetWeldingOperations():
         weldTpes = weldingOp.GetTpElements()
         for weldTpe in weldTpes:
            # check if process point is process point
            events = []
            events = EventHandler.GetEventsByName(weldTpe, TOUCH_CONNECT_EVENT)
            for i, event in enumerate(events):
               EventHandler.RemoveEvent(weldTpe, events[i])

# get absolute linear distance between two toolpath elements
def GetAbsoluteLinearDistanceBetweenTwoTpes(teachHandler, tpeOne, tpeTwo):
   # get distance between two TPEs using its matrices
   matrixOne = tpeOne.GetMatrixToActiveBaseFrame();
   matrixTwo = tpeTwo.GetMatrixToActiveBaseFrame();
   distance = matrixTwo.GetDistance(matrixOne)
   return distance
# HELPER - END


# ===========================================================================================
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

   # add a touch operation to the lit of touch operations
   def AddTouchOperation(self, operation):
      # new instance of touch operation
      touchOp = TouchOperation(operation, self.__eventHandler)
      # add instance of TouchOperation to the touch operation list
      self.__touchOperations.append(touchOp)
   
   # add a welding operation to the welding group
   def AddWeldingOperation(self, operation):
      self.__weldingOperations.append(operation)

   # ask the welding group if welding operation exists
   def HasWeldingOperation(self, operation):
      for weldOp in self.__weldingOperations:
         if (weldOp.GetProcessGeometryIdentifier() == operation.GetProcessGeometryIdentifier()):
            return True
      return False

   # return the unique identifier of the welding group
   def GetIdentifier(self):
      return self.__processGeometryIdentifier

   # return the welding operation
   def GetWeldingOperations(self):
      return self.__weldingOperations

   # returns the reference welding operation
   def GetReferenceWeldingOperation(self):
      return self.__referenceWeldingOperation

   # return a list of class TouchOperation
   def GetTouchOperations(self):
      return self.__touchOperations

   # returns first process toolpath element of the reference welding operation
   def GetFirstProcessTpeOfReferenceWeldingOperation(self):
      # get all toolpath elements from reference operation
      weldingTpes = self.__referenceWeldingOperation.GetTpElements()
      # init first and last toolpath element with none to check later if successful
      firstProcessTpe = None
      # find first process point
      for firstWeldingTpe in weldingTpes:
         if (firstWeldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE):
            firstProcessTpe = firstWeldingTpe
            break
      return firstProcessTpe
   # returns last process toolpath element of the reference welding operation
   def GetLastProcessTpeOfReferenceWeldingOperation(self):
      # get all toolpath elements from reference operation
      weldingTpes = self.__referenceWeldingOperation.GetTpElements()
      # init first and last toolpath element with none to check later if successful
      lastProcessTpe = None
      # find last process points
      for lastWeldingTpe in reversed(weldingTpes):
         if (lastWeldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE):
            lastProcessTpe = lastWeldingTpe
            break
      return lastProcessTpe

   # returns all first process toolpath elements of all welding operations of the welding group
   def GetAllFirstProcessTpesOfAllWeldingOperation(self):
      # get all toolpath elements from reference operation
      tpeList = []
      for weldingOp in self.__weldingOperations:
         # get toolpath elements of welding operation
         weldingTpes = weldingOp.GetTpElements()
         # find first process point
         for firstWeldingTpe in weldingTpes:
            if ((firstWeldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE) or (firstWeldingTpe.GetProcessType() == TPPROCESSTYPE_APPROACH)):
               tpeList.append(firstWeldingTpe)
               break
      return tpeList

   # returns all last process toolpath elements of all welding operations of the welding group
   def GetAllLastProcessTpesOfAllWeldingOperation(self):
      # get all toolpath elements from reference operation
      tpeList = []
      for weldingOp in self.__weldingOperations:
         # get toolpath elements of welding operation
         weldingTpes = weldingOp.GetTpElements()
         # find last process points
         for lastWeldingTpe in reversed(weldingTpes):
            if (lastWeldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE):
               tpeList.append(lastWeldingTpe)
               break
      return tpeList

   # set the welding group number
   def SetWeldingGroupNumber(self, number):
      self.__groupNumber = number

   # get the welding group number
   def GetWeldingGroupNumber(self):
      return self.__groupNumber

# ===========================================================================================
# TouchOperation: class with all necessary information about a touch sensing operation.
class TouchOperation:
   def __init__(self, operation, eventHandler):
      # touch operation
      self.__touchOperation = operation
      # event handler
      self.__eventHandler = eventHandler
      
      self.__opName = operation.GetName()

      self.__workMethodName = GetOperationStringAttribute(operation, WORKMETHOD_NAME)
      if self.__workMethodName == WM_TOUCH:
         # looking for CollisionPoint, but SeamSearch (WM_SEAM) has not one
         if gConnectionType == AW_CONNECT_SHORTEST_DISTANCE:
            # collision point of touch operation; only used if connection type is "shortest distance"
            self.__tpeTouchOpCollisionPoint = self.__FindCollisionTpeInTouchOperation(self.__touchOperation)
            if self.__tpeTouchOpCollisionPoint == None:
               raise "couldn't find collision toolpath element while initialize TouchOperation"
         else:
            # no CollisionPoint if not WM_TOUCH
            self.__tpeTouchOpCollisionPoint = None
      else:
         # no CollisionPoint if not WM_TOUCH
         self.__tpeTouchOpCollisionPoint = None
      # first automatically created touch point of the touch operation 
      self.__tpeTouchOpStartPoint = self.__FindStartTpeInTouchOperation(self.__touchOperation)
      if self.__FindStartTpeInTouchOperation == None:
         raise "couldn't find start toolpath element while initialize TouchOperation"

   # get the touch ID
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
         if (tpe.GetProcessType() == TPPROCESSTYPE_CYCLE):
            # found first cycle point, return the toolpath element
            return tpe
      # if no exploded cycle point was found, return null
      return None

   # get the touch operation
   def GetTouchOperation(self):
      return self.__touchOperation
   
   def GetTouchOPName(self):
       return self.__opName
   
   # get the collision toolpath element of the touch operation
   def GetCollisionTpeInTouchOperation(self):
      if self.__tpeTouchOpCollisionPoint != None:
         return self.__tpeTouchOpCollisionPoint
      # no Collision Point found, so use StartPoint
      return self.__tpeTouchOpStartPoint
