# -------------------------------------------------------------------------------------------
# Name: arc welding connect touch points and process points
# Description: 
# Debug info: E2@localhost:5254
# Author: Hohmann
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

# Import libraries
from sqlite3 import connect
from centypes import *
import math
import sys, os, inspect
sys.dont_write_bytecode = True
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\Library\\")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\OlpProgram\\")
# from Helper import *
import tkinter as tk

WINDOW_BACKGROUND = '#2f2f2f'
BUTTON_BACKGROUND = '#2f2f2f'
BUTTON_FOREGROUND = '#ededed'
BUTTON_BACKGROUND_CLICKED = '#C8F01E'
BUTTON_FOREGROUND_CLICKED = '#2f2f2f'
ENUM_BACKGROUND = '#2f2f2f'
ENUM_FOREGROUND = '#ededed'
TEXTBOX_BACKGROUND = '#2f2f2f'
TEXTBOX_FOREGROUND = '#ededed'

PADDINGS = {'padx': 5, 'pady': 5}

# attributes
WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"
AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
AW_CONNECT_TOUCH_PROCESS_TYPE = "ConnectTouchProcessType"
# CONSTANTS
AW_CONNECT_OPERATION = 0
AW_CONNECT_START_END = 1
AW_CONNECT_SHORTEST_DISTANCE = 2
AW_CONNECT_NO = 3
WM_STICH = "StitchWeldingWorkMethod"
WM_TOUCH = "TouchSensingWorkMethod"
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

def GetCommandName():
   return "ConnectTouchAndProcessPoints"
   
def GetCommandUuId():
   return "EFF9ADBF-1A85-422E-8CFD-D00A10497707"
   
def GetIconName():
   return "COM_ScriptsRun"
   
# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogInfo("ModifyActiveProgram callback started.")

   # -- SEQUENCE --
   # 0) get user selection
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
   # global variable
   global connectionType
   connectionType = AW_CONNECT_NO

   # WINDOW
   sys.argv  = ['']
   # get new user interface
   global newUserInterface
   newUserInterface = UserInterface()
   
   icoPath = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\OlpProgram\\e2.ico"
   # create a new window
   global ui
   ui = newUserInterface.NewWindow("Connect touch and process points", 550, 110, icoPath)
   # resizable forbidden
   ui.resizable(False, False)
   # grid definition
   ui.columnconfigure(0, weight=1)
   ui.columnconfigure(1, weight=1)
   ui.columnconfigure(2, weight=1)
   ui.columnconfigure(3, weight=1)
   ui.rowconfigure(0, weight=1)
   ui.rowconfigure(1, weight=1)
   ui.rowconfigure(2, weight=1)

   # add label to display file path 
   label = newUserInterface.AddLabel(ui, "Choose connection type between touch and process points:", 400, 25, None)
   label.grid(row=0, column=0, columnspan=3, sticky=tk.E+tk.W, **PADDINGS)

   # add label to display file path 
   global lbSelectedOption
   lbSelectedOption = newUserInterface.AddLabel(ui, "No Connection", 100, 25, None)
   lbSelectedOption.grid(row=0, column=3, sticky=tk.E+tk.W, **PADDINGS)

   # button to choose a calibration file
   global btOperation
   btOperation = newUserInterface.AddButton(ui, "Operation", 120, 25, UiChooseConnectionTypeOperation)
   btOperation.grid(row=1, column=0, sticky=tk.W+tk.N, **PADDINGS)

   # button to choose a calibration file
   global btStartEnd
   btStartEnd = newUserInterface.AddButton(ui, "Start & End", 120, 25, UiChooseConnectionTypeStartEnd)
   btStartEnd.grid(row=1, column=1, sticky=tk.W+tk.N, **PADDINGS)

   # button to choose a calibration file
   global btShortestDistance
   btShortestDistance = newUserInterface.AddButton(ui, "Shortest Distance", 120, 25, UiChooseConnectionTypeShortestDistance)
   btShortestDistance.grid(row=1, column=2, sticky=tk.W+tk.N, **PADDINGS)

   # button to choose a calibration file
   global btNoSelection
   btNoSelection = newUserInterface.AddButton(ui, "No Connection", 120, 25, UiChooseConnectionTypeNoConnection)
   btNoSelection.grid(row=1, column=3, sticky=tk.W+tk.N, **PADDINGS)

   # button to choose a calibration file
   global btAbort
   btAbort = newUserInterface.AddButton(ui, "Execute Selection", 550, 25, ui.destroy)
   btAbort.grid(row=2, column=0, columnspan=4, sticky=tk.W+tk.N, **PADDINGS)

   ui.mainloop()

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
      if (workMethodName == WM_TOUCH):
         touchOps.append(operation)
      elif (workMethodName == WM_STICH) or (workMethodName == WM_CONTINUES):
         weldingOps.append(operation)

   # if one of the lists is empty, not necessary to continue
   if (len(touchOps) == 0) or (len(weldingOps) == 0):
      logging.LogWarn("auxiliary command couldn't find welding or touch operations. Execution aborted.")
      return

   # -------------------------------------
   # 3) create list with welding groups
   # -------------------------------------
   # if a welding operation has no corresponding touch operation,
   # the welding operation will be added to the previous welding group
   weldingGroups = []
   # init last weld group; save weld group of the operation before
   lastWeldGroup = None
   # iterate through all welding operations
   for weldingOp in weldingOps:
      # check if a touch operation belongs to the welding operation, otherwise add the welding operation belongs to the welding group before
      currentWeldGroup = None
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
         # add welding group to the list with welding groups
         weldingGroups.append(currentWeldGroup)
      else:
         # if connection type is shortest distance, each welding operation must have it's own corresponding touch operation
         # a mix is not supported. In that case all already created events are removed and execution is aborted.
         if connectionType == AW_CONNECT_SHORTEST_DISTANCE:
            logging.LogError("You selected connection type shortest distance, but a welding operation has no linked touch operation. Mix is not possible.")
            RemoveAllConnectEvents(eventHandler, program)
            return
         # add the welding operation to an existing welding group.
         # This welding operation will use the same seam calibration done by touch sensing
         lastWeldGroup.AddWeldingOperation(weldingOp)
      lastWeldGroup = currentWeldGroup

   # -------------------------------------
   # 4) add touch operations to the welding operations
   # -------------------------------------
   for touchOp in touchOps:
      touchOpIdentifier = touchOp.GetProcessGeometryIdentifier()
      for weldingGroup in weldingGroups:
         if (touchOpIdentifier == weldingGroup.GetIdentifier()):
            weldingGroup.AddTouchOperation(touchOp)
            break

   # -------------------------------------
   # 5) check connection type
   # -------------------------------------
   if (connectionType == AW_CONNECT_OPERATION):
      # remove all connect events
      RemoveAllConnectEvents(eventHandler, program)
      # create connect events at first process point and connect touch points to first process point
      ConnectionType_Operation(logging, eventHandler, teachHandler, weldingGroups)
   elif (connectionType == AW_CONNECT_START_END):
      # remove all connect events
      RemoveAllConnectEvents(eventHandler, program)
      # create connect events at first/last process point and connect touch points to start/end
      ConnectionType_StartEnd(logging, eventHandler, teachHandler, weldingGroups)
   elif (connectionType == AW_CONNECT_SHORTEST_DISTANCE):
      # remove all connect events
      RemoveAllConnectEvents(eventHandler, program)
      # create connect events at first/last process point and connect touch points to start/end
      ConnectionType_ShortestDistance(logging, eventHandler, teachHandler, weldingGroups)
   elif (connectionType == AW_CONNECT_NO):
      # remove all connect events
      RemoveAllConnectEvents(eventHandler, program)

   # -------------------------------------
   # 6) add number touches per ID to the connect event
   # -------------------------------------
   CalculateNumberOfTouchesPerTouchId(weldingGroups)

   return


# create connect events at first process point and connect touch points to first process point
def ConnectionType_Operation(Logging, EventHandler, TeachHandler, WeldingGroups):
   # iterate though each welding group
   counter = 0
   for weldingGroup in WeldingGroups:
      # increase counter
      counter += 1
      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()
      # iterate through touch operations
      for touchOperation in touchOperations:
         # add connect event
         event = AddConnectEvent(EventHandler, touchOperation.GetStartTpeInTouchOperation(), counter)
         touchOperation.SetConnectEvent(event)
         if event == None:
            Logging.LogError("could not add connect event.")
      # get all first process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for processTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
         # add connect event to the first and last toolpath element
         event = AddConnectEvent(EventHandler, processTpe, counter)
         if event == None:
            Logging.LogError("could not add connect event.")


# create connect events at first/last process point and connect touch points to start/end
def ConnectionType_StartEnd(Logging, EventHandler, TeachHandler, WeldingGroups):

   # check to which process point the touch points belong with reference welding operation
   # set "TouchPointBelongsTo variable in touch operation"
   # set touch connection events also to the other welding operations in the welding group

   # iterate though each welding group
   counter = 0
   for weldingGroup in WeldingGroups:
      # increase counter
      counter += 1

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
      counterFirstProcessTpe = counter
      counter +=1
      counterLastProcessTpe = counter

      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()

      # iterate through touch operations
      for touchOperation in touchOperations:
         # get the collision points to calculate the distance to the process point
         collisionTpe = touchOperation.GetCollisionTpeInTouchOperation()

         # get the distance to the first and last process point
         distanceToFirstTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, firstProcessTpe)
         distanceToLastTpe = GetAbsoluteLinearDistanceBetweenTwoTpes(TeachHandler, collisionTpe, lastProcessTpe)

         # check shortest distance
         if (distanceToFirstTpe <= distanceToLastTpe):
            # shortest distance to first process point
            event = AddConnectEvent(EventHandler, touchOperation.GetStartTpeInTouchOperation(), counterFirstProcessTpe)
            touchOperation.SetConnectEvent(event)
            if event == None:
               Logging.LogError("could not add connect event.")
         else:
            # shortest distance to last process point
            event = AddConnectEvent(EventHandler, touchOperation.GetStartTpeInTouchOperation(), counterLastProcessTpe)
            touchOperation.SetConnectEvent(event)
         if event == None:
            Logging.LogError("could not add connect event.")

      # get all first process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for firstTpe in weldingGroup.GetAllFirstProcessTpesOfAllWeldingOperation():
         event = AddConnectEvent(EventHandler, firstTpe, counterFirstProcessTpe)
         if event == None:
            Logging.LogError("could not add connect event.")
      # get all last process toolpath elements of all welding operation
      # and add the connect event with the same touch id
      for lastTpe in weldingGroup.GetAllLastProcessTpesOfAllWeldingOperation():
         event = AddConnectEvent(EventHandler, lastTpe, counterLastProcessTpe)
         if event == None:
            Logging.LogError("could not add connect event.")


# create connect events at first/last process point and connect touch points to start/end
def ConnectionType_ShortestDistance(Logging, EventHandler, TeachHandler, WeldingGroups):
   # iterate though each welding group
   counter = 0
   for weldingGroup in WeldingGroups:
      # get welding operation 
      weldingOperations = weldingGroup.GetReferenceWeldingOperation()
      # get all toolpath elements from the current welding operation
      weldingTpes = weldingOperations.GetTpElements()

      # get touch operations for the current welding operation
      touchOperations = weldingGroup.GetTouchOperations()

      for weldingTpe in weldingTpes:
         # add event to each process point
         if weldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE:
            # increment counter
            counter += 1
            # add connect event to the first and last toolpath element
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
         # iterate through all welding toolpath elements
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
            # get the already added connect event of the process toolpath element and read the touch id
            connectEventProcessPoint = EventHandler.GetEventsByName(shortestProcessPoint, TOUCH_CONNECT_EVENT)
            if any(connectEventProcessPoint):
               # get touch id
               touchId = connectEventProcessPoint[0].GetString(AW_EVT_TOUCH_ID)
               # shortest distance to last process point
               event = AddConnectEvent(EventHandler, touchOperation.GetStartTpeInTouchOperation(), touchId)
               touchOperation.SetConnectEvent(event)
               if event == None:
                  Logging.LogError("could not add connect event.")
         else:
            Logging.LogError("Touch operation couldn't find the shortest process toolpath element.")


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
      # iterate through the list and add the number of touch operations per touch id to the touch event
      for touchId in listTouchIds:
         listWithEvents = weldGroup.GetAllConnectEventsWithSameTouchId(touchId)
         if any(listWithEvents):
            for connectEvent in listWithEvents:
               if connectEvent != None:
                  connectEvent.SetInteger(AW_EVT_TOUCH_COUNTER, len(listWithEvents))



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


# return the ID of an already existing connect events of a dedicated toolpath element
def GetConnectIdOfExistingConnectEvent(EventHandler, Tpe):
   # get connect events
   event = CheckIfConnectEventExist(EventHandler, Tpe)
   # check if event exists
   if (event != None):
      # get touch Id
      touchId = event.GetString(AW_EVT_TOUCH_ID)
      # return touch Id
      return touchId
   # else return 0
   return 0


# add connect event with predefined id 
def AddConnectEvent(EventHandler, Tpe, Id):
   connectEvent = EventHandler.AddEventByName(Tpe, TOUCH_CONNECT_EVENT, TPINSERTPOS_INSERTBEFORE)
   connectEvent.SetString(AW_EVT_TOUCH_ID, str(Id))
   return connectEvent


# set an integer of an event
def SetIntegerOfEvent(event, numberOfTouches):
   event.SetInteger(AW_EVT_TOUCH_COUNTER, int(numberOfTouches))
   return event

# set an integer of an event
def SetIntegerOfEvent(event):
   value = event.GetInteger(AW_EVT_TOUCH_COUNTER)
   return value

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


# get absolute linear distance between two toolpath elements
def GetAbsoluteLinearDistanceBetweenTwoTpes(teachHandler, tpeOne, tpeTwo):
   # get olp position of first toolpath element
   tpePosOne = teachHandler.GetTpElementPosition(tpeOne, POSRELATION_BASEFRAME)
   # get coordinates of first toolpath element
   tpePosOneCoordinates = tpePosOne.GetCoordinates()
   # get olp position of second toolpath element
   tpePosTwo = teachHandler.GetTpElementPosition(tpeTwo, POSRELATION_BASEFRAME)
   # get coordinates of second toolpath element
   tpePosTwoCoordinates = tpePosTwo.GetCoordinates()
   # calculate absolute linear distance
   distance = abs(math.sqrt((tpePosOneCoordinates[0]-tpePosTwoCoordinates[0])**2 + (tpePosOneCoordinates[1]-tpePosTwoCoordinates[1])**2 + (tpePosOneCoordinates[2]-tpePosTwoCoordinates[2])**2))
   # return absolute linear distance
   return distance
# HELPER - END


class UserInterface:
	def __init__(self):
		pass

	def NewWindow(self, title, width, height, icoPath):
		app = tk.Tk()
		app.title(title)
		self._virtualPixel = tk.PhotoImage(width=1, height=1)
		if icoPath != "":
			app.iconbitmap(icoPath)
		app.configure(bg=WINDOW_BACKGROUND)
		app.geometry(self.GetGeometryString(width, height))
		return app

	def GetGeometryString(self, width, height):
		return str(width) + "x" + str(height)

	# height and width are defined in pixel
	def AddButton(self, window, text, width, height, function):
		bt = tk.Button(window, text=text, image=self._virtualPixel, relief=tk.RIDGE, font=("Arial", 10), width=width, height=height, fg=BUTTON_FOREGROUND, bg=BUTTON_BACKGROUND, activebackground=BUTTON_BACKGROUND_CLICKED, activeforeground=BUTTON_FOREGROUND_CLICKED, compound="c", command=function)
		return bt

	# height and width are defined in default tkinter
	def AddEnum(self, window, options, list, width, height, function):
		enum = tk.OptionMenu(window, options, *list, command=function)
		options.set(list[0])
		enum.configure(width=width, bg=ENUM_BACKGROUND, fg=ENUM_FOREGROUND, highlightthickness=0, justify=tk.LEFT, font=("Arial", 10))
		return enum

	# height and width are defined in pixel
	def AddLabel(self, window, text, width, height, function):
		lb = tk.Label(window, text=text, fg=BUTTON_FOREGROUND, bg=BUTTON_BACKGROUND, image=self._virtualPixel, font=("Arial", 10), width=width, height=height, compound="c", anchor='w', command=function)
		return lb

	# height and width are defined in default tkinter
	def AddTextBox(self, window, text, width, height, readonly=False, scrollbars=False):
		textBox = tk.Text(window, height=height, width=width, font=("Arial",10), fg=TEXTBOX_FOREGROUND, bg=TEXTBOX_BACKGROUND)
		if (scrollbars):
			scrollbar = tk.Scrollbar(window, command=textBox.yview)
			textBox.configure(yscrollcommand=scrollbar.set)
		if (readonly):
			textBox.configure(state=tk.DISABLED)
		textBox.insert(tk.END, text)
		return textBox


# function call after button is pressed in the user interface to set the corresponding touch connection type
def UiChooseConnectionTypeOperation():
   global connectionType
   # set connection type
   connectionType = AW_CONNECT_OPERATION
   # change label text to display the user the selection
   lbSelectedOption.configure(text="Operation")


# function call after button is pressed in the user interface to set the corresponding touch connection type
def UiChooseConnectionTypeStartEnd():
   global connectionType
   # set connection type
   connectionType = AW_CONNECT_START_END
   # change label text to display the user the selection
   lbSelectedOption.configure(text="Start & End")


# function call after button is pressed in the user interface to set the corresponding touch connection type
def UiChooseConnectionTypeShortestDistance():
   global connectionType
   # set connection type
   connectionType = AW_CONNECT_SHORTEST_DISTANCE
   # change label text to display the user the selection
   lbSelectedOption.configure(text="Shortest Dis.")


# function call after button is pressed in the user interface to set the corresponding touch connection type
def UiChooseConnectionTypeNoConnection():
   global connectionType
   # set connection type
   connectionType = AW_CONNECT_NO
   # change label text to display the user the selection
   lbSelectedOption.configure(text="")


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

   def GetAllTouchOperationConnectEventAndTouchId(self):
      listConnectEventTouchId = []
      for touchOp in self.__touchOperations:
         event = touchOp.GetConnectEvent()
         touchId = touchOp.GetTouchId()
         listConnectEventTouchId.append(event, touchId)

   def GetAllConnectEventsWithSameTouchId(self, Id):
      listWithConnectEvents = []
      for touchOperation in self.__touchOperations:
         touchId = touchOperation.GetTouchId()
         if touchId == Id:
            listWithConnectEvents.append(touchOperation.GetConnectEvent())
      return listWithConnectEvents


   # add a touch operation to the lit of touch operations
   def AddTouchOperation(self, operation):
      # new instance of touch operation
      touchOp = TouchOperation(operation, self.__eventHandler)
      # add instance of TouchOperation to the touch operation list
      self.__touchOperations.append(touchOp)
   
   # add a welding operation to the welding group
   def AddWeldingOperation(self, operation):
      self.__weldingOperations.append(operation)

   # ask the welding group if touch points exists
   def HasTouchOperations(self):
      if len(self.__touchOperations) == 0:
         return False
      else:
         True

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
            if (firstWeldingTpe.GetProcessType() == TPPROCESSTYPE_PROCESSCURVE):
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
      self.__belongsTwoStartPoint = True
      self.__connectEvent = None
      self.__touchId = 0
      self.__numberOfTouchesWithSameId = 0

   # set number of touches with same id
   def SetNumberOfTouchesWithSameId(self, value):
      self.__numberOfTouchesWithSameId = value

   # get number of touches with same id
   def GetNumberOfTouchesWithSameId(self):
      return self.__numberOfTouchesWithSameId

   # set the touch event
   def SetConnectEvent(self, event):
      self.__connectEvent = event
      self.__touchId = event.GetString(AW_EVT_TOUCH_ID)

   # get the touch event
   def GetConnectEvent(self):
      return self.__connectEvent

   def GetTouchId(self):
      return self.__touchId

   # set the touch connection with respect to the reference welding operation.
   def SetTouchBelongsTo(self, value):
      self.__belongsTwoStartPoint = value

   # get the touch connection with respect to the reference welding operation.
   def GetTouchBelongsTo(self):
      return self.__belongsTwoStartPoint

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

   # get the collision toolpath element of the touch operation
   def GetCollisionTpeInTouchOperation(self):
      return self.__tpeTouchOpCollisionPoint

   # get the start toolpath element of the touch operation
   def GetStartTpeInTouchOperation(self):
      return self.__tpeTouchOpStartPoint
