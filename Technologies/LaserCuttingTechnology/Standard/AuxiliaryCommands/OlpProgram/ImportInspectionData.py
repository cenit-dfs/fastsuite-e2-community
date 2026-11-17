# -------------------------------------------------------------------------------------------
# Name: Modify Active Program
# Description: 
# Debugg info: E2@localhost:5254
# Author: Shabas
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

# Import libraries
from centypes import *
import sys, os, inspect
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter.messagebox import showinfo
import csv
import ctypes
import traceback
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\OlpProgram\\")

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

# to show message box with error

def GetCommandName():
   return "ImportInspectionData"
   
def GetCommandUuId():
   return "B7CDBF92-49A3-4014-B94E-79E527375B1A"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator):
   # get logger
   logging = Operator.GetLoggerOperator()
   # debug logging: create attributes
   logging.LogInfo("??????????????????????????????????????????????????????")
   logging.LogInfo("?????????? ModifyActiveProgram callback started. ??????????")

   # WINDOW
   sys.argv  = ['']
   # get new user interface
   global newUserInterface
   newUserInterface = UserInterface()
   
   newUserInterface.BuildGui(FileOpen)

   # PROGRAM
   program = Operator.GetActiveProgram()
   logging.LogInfo("Program name: "+str(program.GetName()))
   tpElements = program.GetTpElements()

   # get inspection points
   inspectionData = CalibPointImport

   # check if data was read
   if len(inspectionData.calibPoints) == 0:
      return

   # get teach handler
   teachHandler = Operator.GetTeachHandler()

   # remove from list not needed points
   TranslateAndRemoveEventsPointsFromList(program, teachHandler, inspectionData, "CIRCLE")
   TranslateAndRemoveEventsPointsFromList(program, teachHandler, inspectionData, "HEXAGON")
   TranslateAndRemoveEventsPointsFromList(program, teachHandler, inspectionData, "RECTANGLE")
   TranslateAndRemoveEventsPointsFromList(program, teachHandler, inspectionData, "SLOT")
   TranslateAndRemoveEventsPointsFromList(program, teachHandler, inspectionData, "KEYHOLE")
   # ??? other types??
   #REGSHAPE_QUADRILATERAL   = 5
   #REGSHAPE_PARALLELOGRAM   = 6
   #REGSHAPE_SQUARE          = 7
   #REGSHAPE_RHOMBUS         = 8

   # loop points
   for inspectionPoint in inspectionData.calibPoints:

      # Tp ELEMENTS
      for tpElement in tpElements:
         tpeName = tpElement.GetName()
         if tpeName is None: continue

         if inspectionPoint.tpeName == tpeName:
            if 3 > len(inspectionPoint.deviation) : continue
            tpePos = teachHandler.GetTpElementPosition(tpElement, POSRELATION_WORKPIECEROOT)
            if tpePos is None: continue
            # offset current position
            tpePos.TranslatePosition(inspectionPoint.deviation[0], inspectionPoint.deviation[1], inspectionPoint.deviation[2], POSRELATION_BASEFRAME)
            teachHandler.ModifyTpElement(tpePos)

         elif tpElement.GetMotionType() == MOTIONTYPE_CIR:
            tpePosVia = teachHandler.GetTpElementPosition(tpElement, POSRELATION_WORKPIECEROOT)
            if tpePosVia is None: continue
            viaPointName = tpePosVia.GetViaPointName()
            if viaPointName is None: continue
            if 3 > len(inspectionPoint.deviation) : continue
            
            if inspectionPoint.tpeName == viaPointName:
               tpePosVia.TranslateViaPointPosition(inspectionPoint.deviation[0], inspectionPoint.deviation[1], inspectionPoint.deviation[2], POSRELATION_BASEFRAME)
               teachHandler.ModifyTpElement(tpePosVia)
      

   #computeHandler.EnableAutoRecompute() 
   ## RECOMPUTE--_+++---
   #logging.LogInfo("Recompute was triggered on program: "+str(program.GetName()))
   # computeHandler.TriggerRecompute(program, ENTERSTATE_STARTWITHMANUALEVENTS)
   
   # debug logging
   logging.LogInfo("?????????? ModifyActiveProgram callback ended. ??????????")
   logging.LogInfo("??????????????????????????????????????????????????????")
# -------------------------------------------------------------------------------------------

def TranslateAndRemoveEventsPointsFromList(iProgram, iTeachHandler, iInspectionData, isEventName):
   if iProgram is None or iTeachHandler is None or iInspectionData is None: return

   regShapeElements = iProgram.GetTpElementsWithEvent(isEventName)
   for shapeElem in regShapeElements:
      for inspectionPoint in iInspectionData.calibPoints:
         # get shape element name
         tpeName = shapeElem.GetName()
         if tpeName is None: continue

         # get point name
         pointName = str(inspectionPoint.tpeName)
         if pointName is None: continue

         # deviation is not set -> go to next
         if 3 > len(inspectionPoint.deviation) : continue

         if 0 <= pointName.find(isEventName):
            tpePos = iTeachHandler.GetTpElementPosition(shapeElem, POSRELATION_WORKPIECEROOT)
            if tpePos is not None:
               # offset current position
               tpePos.TranslatePosition(inspectionPoint.deviation[0], inspectionPoint.deviation[1], inspectionPoint.deviation[2], POSRELATION_BASEFRAME)
               iTeachHandler.ModifyTpElement(tpePos)
               iInspectionData.calibPoints.remove(inspectionPoint)

def EnumPrintValue(selection):
   pass
   # print(str(options.get()))
   #_labelFilePath.configure(text=str(self.options.get()))
   #_labelFilePath.update()

# file open dialogue and fill text box
def  FileOpen():
   #to get the current working directory
   #directory = pathlib.Path(__file__).parent.resolve()
   directory =""
   # define supported file types for open file dialogue filetypes = (('Kalibration File', '*.csv'),('All files', '*.*'))
   filetypes = (('Kalibration File', '*.csv'),('All files', '*.*'))
   filePathCalibration = fd.askopenfilename(title='Select calibration file', initialdir=directory, filetypes=filetypes)

   # check if file is selected
   if (filePathCalibration == ""):
      return

   newUserInterface.SetSelectedPath(filePathCalibration)
   
   # import the file 
   calibration = CalibPointImport

   try: 
      calibration.ReadCalibFile(calibration, filePathCalibration)
      
      # define title row
      line = "Name " + "\t\t" + "Operation " + "\t\t" + "X " + "\t" + "Y " + "\t" + "Z " + "\t" + "R " + "\t" + "Deviation in X " + "\t\t" + "Deviation in Y " + "\t\t" + "Deviation in Z " +"\r\n" 
      newUserInterface.InsertTitleLine(line)

      # add to list
      # used for table later
      #lst = [("Name","Operation","X" ,"Y", "Z", "R", "Deviation in X", "Deviation in Y", "Deviation in Z")] 

      sEmpty = ""
      # add the point content
      for point in calibration.calibPoints:
         listOfValues = []

         if 3 > len(point.CoordinateInMilimeter) : continue
         # insert point coordinates to the list
         listOfValues.append(point.tpeName)
         listOfValues.append(point.opName)
         listOfValues.append(str(point.CoordinateInMilimeter[0]))
         listOfValues.append(str(point.CoordinateInMilimeter[1]))
         listOfValues.append(str(point.CoordinateInMilimeter[2]))

         # get and add radius if it exists
         radius = ""
         if 0.0 != point.r: radius = str(point.radInMilimeter)
         listOfValues.append(radius)

         # get and add deviation if it exists
         deviation = ""
         if 0 != len(point.deviationInMilimeter) :
            # build text with deviation values for text box
            deviation = sEmpty + str(point.deviationInMilimeter[0]) + "\t\t" + sEmpty + str(point.deviationInMilimeter[1]) + "\t\t" + sEmpty + str(point.deviationInMilimeter[2]) 
            # add deviation values to list
            listOfValues.append(str(point.deviationInMilimeter[0]))
            listOfValues.append(str(point.deviationInMilimeter[1]))
            listOfValues.append(str(point.deviationInMilimeter[2]))
         else:
            listOfValues.append("")
            listOfValues.append("")
            listOfValues.append("")

         # write data in text box
         line = listOfValues[0] + "\t\t" + listOfValues[1] + "\t\t" + listOfValues[2] + "\t" + listOfValues[3] + "\t" + listOfValues[4] + "\t" + radius + "\t" + deviation + "\r\n"
         newUserInterface.InsertTxtLine(line)

         # add to list
         #used for table
         #lst.append(listOfValues)
         
      # config text box 
      newUserInterface.ConfigTxtBox()

      # used for table creation later
      #tbl = newUserInterface.AddTableData(lst)

   except Exception as e:
      print("An error is occurred! Script is terminated.\n", e)

      MB_ICONERROR = 0x00000010
      title = u'E2 Error'
      # complete error with type and method name
      exc_type, exc_value, exc_traceback = sys.exc_info()
      lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
      # show error in a message box
      ctypes.windll.user32.MessageBoxW(0, "An error is occurred! Script is terminated.\nHere is the error message: \n \n" + ''.join(line for line in lines), title, MB_ICONERROR)

      # close the dialog
      newUserInterface.CloseWindow()


# import calibration file and write it into a separated class
class CalibPointImport:
	# array with calibration points 
	calibPoints = []

	# resd csv file 
	def __init__(self):
		pass
	
	# read the file
	def ReadCalibFile(self, fileName):
		with open(fileName, 'r') as csvfile:
			csv_reader = csv.reader(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_NONE, lineterminator = '\r\n')
			# iterate through the csv liset   
			firstRowSkipped = False  
			firstTpeSkipped = False
			x, y, z = 0.0, 0.0, 0.0
			devX, devY, devZ = 0.0, 0.0, 0.0
			radius = 0.0
			tpeName = ""
			opName = ""    
			# loop csv rows                          
			for row in csv_reader:
				if firstRowSkipped == False:
					firstRowSkipped = True
					continue
				if tpeName == str(row[0]):
					if str(row[2]) == "Y":
						# read Y value
						if str(row[4]) != "":	
							# take actual value					
							y = float(row[4])
						else:
							# take target value	
							y = float(row[3])
						# read deviation for Y, if it exists
						if str(row[5]) != "":
							devY = float(row[5])
						continue
						

					if str(row[2]) == "Z":
						# read Z value
						if str(row[4]) != "":
							# take actual value		
							z = float(row[4])
						else:
							# take target value		
							z = float(row[3])
						# read deviation for Z, if it exists
						if str(row[5]) != "":
							devZ = float(row[5])
						continue
						

					if str(row[2]) == "R":
						# read R value
						if str(row[3]) != "":
							radius = float(row[3])
							continue
						else:
							radius = 0.0
				else:
					if firstTpeSkipped == True:
						# append new point to list
						self.calibPoints.append(CalibPoint(tpeName, opName, x, y, z, radius, devX, devY, devZ))

					firstTpeSkipped = True
					# new point
					tpeName = str(row[0])
					opName = str(row[1])

					# reset values
					radius = 0.0
					devX, devY, devZ = 0.0, 0.0, 0.0

					if str(row[2]) == "X":
						# read X value
						if str(row[4]) != "":
							# take actual value		
							x = float(row[4])
						else:
							# take target value		
							x = float(row[3])
						# read deviation for X, if it exists
						if str(row[5]) != "":
							devX = float(row[5])

			# append new point to list
			self.calibPoints.append(CalibPoint(tpeName, opName, x, y, z, radius, devX, devY, devZ))

	# return the complete list of points 
	def GetCalibPoints(self):
		return self.calibPoints

# class with single point information
class CalibPoint:
	def __init__(self, isTpeName, isOpName, inX, inY, inZ, inR, inDeviationX, inDeviationY, inDeviationZ):
		self.tpeName = isTpeName
		self.opName = isOpName

		# convert all values from mm to meter
		# set point coordinates
		self.Coordinate = []
		self.Coordinate.append(round(inX/1000, 3))
		self.Coordinate.append(round(inY/1000, 3))
		self.Coordinate.append(round(inZ/1000, 3))

		self.CoordinateInMilimeter = []
		self.CoordinateInMilimeter.append(inX)
		self.CoordinateInMilimeter.append(inY)
		self.CoordinateInMilimeter.append(inZ)

		# set radius in point if it exists
		self.r = 0.0
		self.radInMilimeter = 0.0
		if 0 < inR: 
			self.r = round(inR/1000, 3)
			self.radInMilimeter = inR

		# set point coordinates deviation if it exists
		self.deviation = []
		self.deviationInMilimeter = []
		if 0.0 != inDeviationX or 0.0 != inDeviationY or 0.0 != inDeviationZ:
			self.deviation.append(round(inDeviationX/1000, 3))
			self.deviation.append(round(inDeviationY/1000, 3))
			self.deviation.append(round(inDeviationZ/1000, 3))
			# set deviation as is from exel in milimeter
			self.deviationInMilimeter.append(inDeviationX)
			self.deviationInMilimeter.append(inDeviationY)
			self.deviationInMilimeter.append(inDeviationZ)


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

	def AddFrame(self, window, text, width, height, readonly=False, scrollbars=False):
		frame = tk.LabelFrame(window, height=height, width=width, bg=TEXTBOX_BACKGROUND)
		
		if (scrollbars):
			scrollbar=tk.Scrollbar(window,orient='vertical')
			#scrollbar.pack(side='right',fill='y',expand='false')

			canvas=tk.Canvas(window,bd=0,highlightthickness=0)
			#canvas.pack(fill='both', expand='true')

			# -------------- make a frame with a vertical scrollbar ------------------------------------

			canvas.config(yscrollcommand=scrollbar.set)
			scrollbar.config(command=canvas.yview)
			interior_id = canvas.create_window(0, 0, window=frame,anchor='nw')

			# -------------- <Configure> events for the scrollbar frame ------------------------------------

			def canvas_configure(event,me=canvas,frame=frame,int_id = interior_id):
				if me.winfo_reqwidth() != frame.winfo_width(): me.itemconfigure(int_id, width=me.winfo_width())
			
			canvas.bind("<Configure>",canvas_configure)

			def frame_configure(event,me=frame,canvas=canvas):
				canvas.config(scrollregion="0 0 %s %s" % (me.winfo_reqwidth(), me.winfo_reqheight()))
				if me.winfo_reqwidth() != canvas.winfo_width(): canvas.config(width=me.winfo_reqwidth())
				if me.winfo_reqheight() > 340: canvas.config(height=340)
				else: canvas.config(height=me.winfo_reqheight())

			frame.bind("<Configure>",frame_configure)
			return frame

	def AddTable(self, master, lst):
		rows = len(lst)
		columns = len(lst[0]) 
		for i in range(rows):
			for j in range(columns): 
			
				#txtBx = tk.Text(master, font=("Arial",10), width=5, height=5, fg=TEXTBOX_FOREGROUND, bg=TEXTBOX_BACKGROUND, **PADDINGS)
				txtBx = tk.Text(master, font=("Arial",10), fg=TEXTBOX_FOREGROUND, bg=TEXTBOX_BACKGROUND)
				txtBx.grid(row=i, column=j, columnspan=1, rowspan=1, sticky=tk.W+tk.E+tk.N+tk.S) 
				txtBx.insert(tk.END, lst[i][j])
				# set txtbox not editable
				txtBx.config(state=tk.DISABLED)

	def BuildGui(self, FileOpenCmd):

		#try:

			icoPath = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))) + "\\OlpProgram\\e2.ico"
			# create a new window
			self.__newWindow = self.NewWindow("Inspection Data", 800, 250, icoPath)
			# forbidde resizable
			self.__newWindow.resizable(True, True)
			self.__newWindow.minsize(800, 250)
			# grid definition
			self.__newWindow.columnconfigure(0, weight=3)
			self.__newWindow.rowconfigure(1, weight=3)

			# add label to display file path 
			self.__labelFilePath = self.AddLabel(self.__newWindow, "Path:", 500, 20, None)
			self.__labelFilePath.grid(row=0, column=0, sticky=tk.E+tk.W, **PADDINGS)

			# button to choose a calibration file
			self.__btFileOpen = self.AddButton(self.__newWindow, "File Open", 80, 20, FileOpenCmd)
			self.__btFileOpen.grid(row=0, column=1, sticky=tk.W+tk.N, **PADDINGS)

			# define the text box to display the csv content
			quote = "choose a file first"
			self.__textBox = self.AddTextBox(self.__newWindow, quote, 600, 8, True, True)
			self.__textBox.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, **PADDINGS)
			self.__textBox.config(state=tk.DISABLED)

			#self.__tableFame = self.AddFrame(self.__newWindow, "", 100, 100, True, True)
			#self.__tableFame.grid(row=1, column=0, columnspan=2, sticky=tk.E+tk.W+tk.N+tk.S, **PADDINGS)

			# add button to close the application
			self.__btExit = self.AddButton(self.__newWindow, "Done", 80, 20, self.__newWindow.destroy)
			self.__btExit.grid(row=3, column=1, sticky=tk.W+tk.S, **PADDINGS)

			# run window- application will return, after window is closed.
			self.__newWindow.mainloop()
		#except BaseException:
		#	log = ValueError.__context__
		#	self.__newWindow.destroy()

	def AddTableData(self, lst):
		self.AddTable(self.__textBox, lst)

	def SetSelectedPath(self, isPath):
		self.__labelFilePath.configure(text=isPath)

	def InsertTitleLine(self, isTitleLine):
		textBoxState = self.__textBox.cget('state')
		if (textBoxState == tk.DISABLED):
			self.__textBox.configure(state=tk.NORMAL)
		self.__textBox.delete('1.0', tk.END)

		# define bold text line
		self.__textBox.tag_config("boldText", font=("Arial", 10, "bold"))
		self.__textBox.insert(tk.END, isTitleLine, "boldText")

	def InsertTxtLine(self, isTxt):
		self.__textBox.insert(tk.END, isTxt)

	def ConfigTxtBox(self):
		textBoxState = self.__textBox.cget('state')
		if (textBoxState == tk.DISABLED):
			self.__textBox.configure(state=tk.DISABLED)

	def CloseWindow(self):
		self.__newWindow.destroy()