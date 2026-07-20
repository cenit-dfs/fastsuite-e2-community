# -------------------------------------------------------------------------------------------
# Name: Update Touch Direction Vectors Before Download
# Description: Updates ApprDirX and ApprDirZ attributes in ConnectTouchProcessPointEvent
#              events to reflect current workpiece position
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
from cenpylib.stubs.CENPyOlpMatrix import CENPyOlpMatrix
from centypes import *
import sys, os, inspect
sys.dont_write_bytecode = True

# event names
TOUCH_CONNECT_EVENT = "ConnectTouchProcessPointEvent"
ARC_ON_EVENT = "ArcOnEvent"

def GetCommandName():
   return "PrevProgramDownload"
   
def GetCommandUuId():
   return "A1B2C3D4-565E-4D87-9B2C-FA551B6E2D31"
   
def GetIconName():
   return "COM_ScriptsRun"

# -------------------------------------------------------------------------------------------
def ModifyActiveProgram(Operator: CENPyOlpProgramModifyOperator):
   """
   Updates ApprDirX and ApprDirZ direction vectors in all ConnectTouchProcessPointEvent
   events based on current TPE matrices (accounting for workpiece repositioning).
   """
   # get logger
   logging = Operator.GetLoggerOperator()
   logging.LogDebug("PrevProgramDownload.py: Execution started - Updating touch direction vectors.")

   # get active program
   program = Operator.GetActiveProgram()
   if program is None:
      logging.LogWarn("PrevProgramDownload.py: No active program found.")
      return

   # get event handler
   eventHandler = Operator.GetEventHandler()
   if eventHandler is None:
      logging.LogWarn("PrevProgramDownload.py: Could not get event handler.")
      return

   # get all toolpath elements in the active program
   tpes = program.GetTpElements()
   if not tpes:
      logging.LogDebug("PrevProgramDownload.py: No toolpath elements found in program.")
      return

   # counters for summary
   events_updated = 0
   events_failed = 0
   tpes_processed = 0

   # iterate through all toolpath elements
   for tpe in tpes:
      try:
         # get all ConnectTouchProcessPointEvent events for this TPE
         events = eventHandler.GetEventsByName(tpe, TOUCH_CONNECT_EVENT)
         # events = eventHandler.GetEventsByName(tpe, ARC_ON_EVENT)
         
         if not events or len(events) == 0:
            continue
         
         tpes_processed += 1
         
         # get current matrix (accounts for workpiece position changes)
         try:
            currBF = Operator.GetController().GetActiveBaseFrameMatrix()
            # currBfPos = currBF.GetPosition().GetXYZ()
            # currBF_X = currBF.GetXDirection().GetXYZ()
            # currBF_Y = currBF.GetYDirection().GetXYZ()
            # currBF_Z = currBF.GetZDirection().GetXYZ()

            unalignedWorldStateMatrix = Operator.CreateMatrix()
            unalignedWorldStateMatrix = tpe.GetBaseFrameTransformedMatrixUnaligned()
            # posU = unalignedWorldStateMatrix.GetPosition().GetXYZ()
            # x2U = unalignedWorldStateMatrix.GetXDirection().GetXYZ()
            # y2U = unalignedWorldStateMatrix.GetYDirection().GetXYZ()
            # z2U = unalignedWorldStateMatrix.GetZDirection().GetXYZ()
            
            current_matrix3 = unalignedWorldStateMatrix.Multiply(currBF.Inverse(), unalignedWorldStateMatrix)
            # pos3 = current_matrix3.GetPosition().GetXYZ()
            xDir = current_matrix3.GetXDirection().GetXYZ()
            # yDir = current_matrix3.GetYDirection().GetXYZ()
            zDir = current_matrix3.GetZDirection().GetXYZ()

         except Exception as matrix_ex:
            logging.LogWarn(f"PrevProgramDownload.py: Could not get Path matrix or direction vectors for TPE '{tpe.GetName()}': {str(matrix_ex)}")
            events_failed += len(events)
            continue
         
         # update all ConnectTouchProcessPointEvent events for this TPE
         for event in events:
            try:
               # update the direction attributes
               event.SetString('ApprDirX', str(xDir))
               event.SetString('ApprDirZ', str(zDir))
               events_updated += 1
               
            except Exception as event_ex:
               logging.LogWarn(f"PrevProgramDownload.py: Failed to update event on TPE '{tpe.GetName()}': {str(event_ex)}")
               events_failed += 1
               continue
      
      except Exception as tpe_ex:
         logging.LogWarn(f"PrevProgramDownload.py: Error processing TPE: {str(tpe_ex)}")
         continue

   # log summary
   logging.LogDebug(f"PrevProgramDownload.py: Execution completed.")
   logging.LogDebug(f"  TPEs with ConnectTouchProcessPointEvent: {tpes_processed}")
   logging.LogDebug(f"  Events successfully updated: {events_updated}")
   if events_failed > 0:
      logging.LogDebug(f"  Events failed to update: {events_failed}")

   return
# --------------------------- End of ModifyActiveProgram -------------------------------------