"""Kawasaki AS-language downloader for FASTSUITE E2.

Supports standard PTP, linear, and circular motion; separate subprogram files;
signals; ROT_BASE compensation; arc welding; seam tracking; and touch-sensing
helper programs. Reference dumps and golden output live under
scenarios/ArcWeldingTechnology/KAWASAKI/Standard/.
"""

import sys, inspect, os
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *
from centypes import *
from cenpymath.Euler.Converter import Converter
from cenpymath.Euler.Notations import Notations

DOWNLOAD_CLASS_NAME = "KAWASAKI_AS"


class KAWASAKI_AS(Downloader):
   FILE_EXTENSION = '.as'
   SEPARATE_SUBPROGRAM_FILES = True

   def __init__(self) -> None:
      super().__init__()
      self.FileUtil = FileUtility()
      self.EulerConverter = Converter()
      self.outputFilePath = ''
      self.outputDir = ''
      self.programName = ''
      # Output buffers
      self.Source = []
      self.TransBlock = []
      self.JointsBlock = []
      # State
      self.headerEmitted = False
      self.hasTouchSensing = False
      self.explicitMode = False
      self.currentTsOffset = ''
      self.weldConditionNumber = 1
      self.arcOnActive = False
      self.arcOnIsFirstMotion = False
      self.arcOnLastProcessCurve = False
      self.inWeldSection = False
      self.isFirstOperationInGroup = False
      self.sensingLength = 30.0
      self.sensingSpeed = 15.0
      self.tsConnectionType = 'OperationConnect'
      self.frameRefPoints = []
      self.ptpSpeed = 50.0
      # Touch sensing offset state
      self.currentTouchId = 0
      self.currentFramePt = 0
      self.lastFramePt = 0
      self.currentGroupTsIdName = ''
      self.collisionPending = False
      self.collisionSensingLen = 0.0
      self.collisionSensingSpd = 0.0
      self.collisionRefId = 0
      self.rotbaseOn = 0
      # Weld state for arc-off cleanup
      self.hasCrater = False
      self.craterCondNumber = 0
      self.hasSensing = False
      self.hasRtpm = False
      # Buffered motion data (flushed before each motion in fixed order)
      self.pendingSpeed = None       # (formatted_value, suffix_or_None)
      self.pendingAccel = None       # formatted_value
      self.pendingCp = None          # 'ON' or 'OFF'
      self.pendingAccuracy = None    # formatted_value
      # Last output tracking (for output-only-if-changed)
      self.lastSpeed = None
      self.lastAccel = None
      self.lastCp = None
      self.lastAccuracy = None

   # ==================== FRAMEWORK OVERRIDES ====================

   def OutputSubprogramInSeparateFiles(self):
      return self.SEPARATE_SUBPROGRAM_FILES

   def HandleSubprogramInLoop(self):
      return False

   # ==================== LIFECYCLE ====================

   def Initialize(self, operator: DULPythonDownloadOperator):
      logger = operator.GetLogOperator()
      logger.LogDebug("KAWASAKI Initialize")

   def OutputHeader(self, operator: DULPythonDownloadOperator, controller: DULPythonController):
      logger = operator.GetLogOperator()
      logger.LogDebug("KAWASAKI OutputHeader")
      self.outputDir = controller.GetOutputDirectory()
      # Extract PTP speed from motion profiles
      for profile in controller.GetMotionProfiles():
         if 'PTP' in profile.GetName():
            self.ptpSpeed = profile.GetSpeedValue()
            break
      # Check output style from robot resource
      for res in controller.GetResources():
         for attr in res.GetAttributes():
            if attr.GetName() == 'CENOlpDataOutputStyle':
               self.explicitMode = (attr.GetValue() == 'Explicit')
               break

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      self.programName = program.GetName()
      self.isContainerProgram = program.IsMainProgram() and len(program.GetSubprograms()) > 0
      # Reset per-program state
      self.TransBlock = []
      self.JointsBlock = []
      self.headerEmitted = False
      self.hasTouchSensing = False
      self.rotbaseOn = 0
      self.arcOnActive = False
      self.arcOnIsFirstMotion = False
      self.arcOnLastProcessCurve = False
      self.inWeldSection = False
      self.hasCrater = False
      self.craterCondNumber = 0
      self.hasSensing = False
      self.hasRtpm = False
      self.weldConditionNumber = 1
      self.currentTouchId = 0
      self.currentFramePt = 0
      self.lastFramePt = 0
      self.currentGroupTsIdName = ''
      self.collisionPending = False
      self.currentTsOffset = ''
      self.pendingSpeed = None
      self.pendingAccel = None
      self.pendingCp = None
      self.pendingAccuracy = None
      self.lastSpeed = None
      self.lastAccel = None
      self.lastCp = None
      self.lastAccuracy = None
      groupNumber = 0
      # Read program-level attributes
      for attr in program.GetAttributes():
         name = attr.GetName()
         if name == 'GroupNumber':
            groupNumber = int(attr.GetValue())
         elif name == 'SensingLength':
            self.sensingLength = float(attr.GetValue()) * 1000
         elif name == 'SensingSpeed':
            self.sensingSpeed = float(attr.GetValue()) * 1000
         elif name == 'TSConnectionType':
            self.tsConnectionType = attr.GetValue()
      # Store tool profile for .TRANS block (skip for container main programs)
      if not self.isContainerProgram:
         toolProfile = program.GetUsedToolProfile()
         if toolProfile:
            toolName = self.programName + '_' + toolProfile.GetName()
            xyz = toolProfile.GetXYZ()
            angles = toolProfile.GetOrientation()
            oat = self.EulerConverter.ConvertEuler(angles[0], angles[1], angles[2],
                  Notations.Euler_ZYZr, Notations.Euler_XYZs)
            self.TransBlock.append(self._formatTransLine(toolName,
                  xyz[0]*1000, xyz[1]*1000, xyz[2]*1000, oat[0], oat[1], oat[2]))
      # Pre-scan subprograms for touch sensing so we can emit subroutines in the main file
      self._treeHasTouchSensing = False
      if self.isContainerProgram:
         self._treeHasTouchSensing = self._scanTreeForTouchSensing(program)
      self.Source.append('.PROGRAM ' + self.programName + '()')
      if groupNumber != 0:
         self.Source.append('GROUP ' + str(groupNumber))
      self.Source.append(';Compensate track/rail/positioner')
      self.Source.append('ROTBASE_ON = 0')

   def ProgramEnd(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      self.Source.append('.END')
      # Emit touch subroutines once: in the main program file only
      if self.isContainerProgram:
         if self._treeHasTouchSensing:
            self._emitTouchSubroutines()
      elif program.IsMainProgram() and self.hasTouchSensing:
         self._emitTouchSubroutines()
      if self.TransBlock:
         self.Source.append('.TRANS')
         self.TransBlock.sort(key=lambda line: line.split()[0])
         self.Source.extend(self.TransBlock)
         self.Source.append('.END')
      if self.JointsBlock:
         self.Source.append('.JOINTS')
         self.Source.extend(self.JointsBlock)
         self.Source.append('.END')

   def OperationGroupStart(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      logger = operator.GetLogOperator()
      self.isFirstOperationInGroup = True
      self.currentTouchId = 0
      self.lastFramePt = 0
      # Detect touch sensing from workmethod names in operations
      hasTouchOp = False
      groupName = operationGroup.GetName()
      for op in operationGroup.GetOperations():
         for attr in op.GetAttributes():
            if attr.GetName() == 'ArcWeldingOperationWorkMethodName':
               wmName = attr.GetValue()
               if 'TouchSensing' in wmName:
                  hasTouchOp = True
                  break
      if hasTouchOp and not self.hasTouchSensing:
         self.hasTouchSensing = True
      self.Source.append(';Operation Group: ' + groupName)
      if hasTouchOp:
         self._emitTsIdDeclarations(operationGroup)
         self.currentGroupTsIdName = self._maxTsIdName(operationGroup)
      else:
         self.currentGroupTsIdName = ''

   def OperationGroupEnd(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      self.currentTsOffset = ''
      self.currentGroupTsIdName = ''

   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      logger = operator.GetLogOperator()
      opName = operation.GetName()
      wmName = ''
      touchId = 0
      framePt = 0
      for attr in operation.GetAttributes():
         name = attr.GetName()
         if name == 'ArcWeldingOperationWorkMethodName':
            wmName = attr.GetValue()
         elif name == 'TouchId':
            touchId = int(attr.GetValue())
         elif name == 'FramePt':
            framePt = int(attr.GetValue())
      # Set touch offset variable based on connection type and workmethod
      if self.currentGroupTsIdName:
         isTouchOp = 'TouchSensing' in wmName
         isFrame3p = self.tsConnectionType == 'Frame3pConnect'
         if isTouchOp:
            self.currentTouchId = touchId
            self.currentFramePt = framePt
            if isFrame3p and framePt > 0:
               self.currentTsOffset = 'FRAME_PT_' + str(framePt)
            else:
               self.currentTsOffset = self.programName + '_TS_ID_' + str(touchId)
         else:
            # Stitch welding: use the group's TS_ID with the last known touch ID
            if isFrame3p:
               self.currentTsOffset = self.currentGroupTsIdName
            else:
               self.currentTsOffset = self.programName + '_TS_ID_' + str(self.currentTouchId)
      self.Source.append(';Operation: ' + opName)
      # Check base profile for ROTBASE_ON
      baseProfile = operation.GetUsedBaseProfile()
      newRotbase = 1 if self._isRotBaseProfile(baseProfile) else 0
      if newRotbase != self.rotbaseOn:
         self.rotbaseOn = newRotbase
         self.Source.append(';Compensate track/rail/positioner')
         self.Source.append('ROTBASE_ON = ' + str(self.rotbaseOn))
      if not self.headerEmitted:
         self._emitProgramHeader(operation)
         self.headerEmitted = True
      self.arcOnActive = False
      self.arcOnIsFirstMotion = False
      self.arcOnLastProcessCurve = False
      self.inWeldSection = False
      self.isFirstOperationInGroup = False

   def OperationEnd(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      pass

   # ==================== MOTION ====================

   def HandleMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      for event in motion.GetEventsBefore():
         self.HandleEvent(operator, event, motion)
      eventsAfter = motion.GetEventsAfter()
      readAheadIndices = set()
      if not motion.IsReferenceMotion():
         # Handle collision point: emit position, flush speed, output KR_TOUCH, skip LMOVE
         if self.collisionPending:
            self.collisionPending = False
            position = motion.GetPosition()
            posName = position.GetName()
            if not self.explicitMode:
               xyz = position.GetXYZ()
               angles = position.GetOrientation()
               oat = self.EulerConverter.ConvertEuler(angles[0], angles[1], angles[2],
                     Notations.Euler_ZYZr, Notations.Euler_XYZs)
               externals = position.GetExternalJointValues()
               externals.sort(key=lambda ext: ext[0].GetJointIndex())
               extValues = []
               for joint_obj, value in externals:
                  if joint_obj.GetJointType() == JointKinematicType.Prismatic:
                     extValues.append(value * 1000)
                  else:
                     extValues.append(value)
               self.TransBlock.append(self._formatTransLine(posName,
                     xyz[0]*1000, xyz[1]*1000, xyz[2]*1000,
                     oat[0], oat[1], oat[2], extValues))
            self._flushPendingMotionData()
            self.Source.append('CALL KR_TOUCH (&' + posName + ', &' + self.currentTsOffset +
                  ', ROTBASE_ON, ' + '{:.1f}'.format(self.collisionSensingLen) + ', ' +
                  '{:.1f}'.format(self.collisionSensingSpd) + ', ' + str(self.collisionRefId) + ')')
            self.Source.append('STABLE 0.1')
            # Emit KR_FRAME after final frame point in Frame3pConnect
            if self.collisionRefId == 3 and self.tsConnectionType == 'Frame3pConnect':
               self.Source.append('CALL KR_FRAME (&FRAME_REF_PT_1, &FRAME_REF_PT_2, &FRAME_REF_PT_3, ' +
                     '&FRAME_PT_1, &FRAME_PT_2, &FRAME_PT_3, &' + self.currentGroupTsIdName + ')')
            for i, event in enumerate(eventsAfter):
               if i not in readAheadIndices:
                  self.HandleEvent(operator, event, motion)
            return
         # Read-ahead: scan events-after for ArcOn/ArcOff/Accuracy(Off) before outputting motion
         for i, event in enumerate(eventsAfter):
            name = event.GetName()
            if name == 'ArcOnEvent':
               self._handleArcOn(event)
               readAheadIndices.add(i)
            elif name == 'ArcOffEvent':
               self._handleArcOff(event, motion)
               readAheadIndices.add(i)
            elif name == 'Accuracy':
               criteria = ''
               for attr in event.GetAttributes():
                  if attr.GetName() == 'Criteria':
                     criteria = attr.GetValue()
               if criteria == 'Off':
                  self._handleAccuracy(event)
                  readAheadIndices.add(i)
         # Flush pending motion data before the motion command
         self._flushPendingMotionData()
         position = motion.GetPosition()
         posName = position.GetName()
         isJointTarget = position.GetTargetType() == TargetType.Joint
         xyz = position.GetXYZ()
         angles = position.GetOrientation()
         oat = self.EulerConverter.ConvertEuler(angles[0], angles[1], angles[2],
               Notations.Euler_ZYZr, Notations.Euler_XYZs)
         externals = position.GetExternalJointValues()
         externals.sort(key=lambda ext: ext[0].GetJointIndex())
         extValues = []
         for joint_obj, value in externals:
            if joint_obj.GetJointType() == JointKinematicType.Prismatic:
               extValues.append(value * 1000)
            else:
               extValues.append(value)
         # Build position target string
         if isJointTarget:
            mainJoints = position.GetMainJointValues()
            mainJoints.sort(key=lambda j: j[0].GetJointIndex())
            jointVals = [self._formatTransNum(j[1]) for j in mainJoints]
            jointVals.extend([self._formatTransNum(v) for v in extValues])
            if self.explicitMode:
               posTarget = '#[' + ', '.join(jointVals) + ']'
            else:
               posTarget = '#' + posName
               self.JointsBlock.append('#' + posName + ' ' + ' '.join(jointVals))
         elif self.explicitMode:
            posTarget = self._formatTransInline(
                  xyz[0]*1000, xyz[1]*1000, xyz[2]*1000,
                  oat[0], oat[1], oat[2], extValues)
         else:
            posTarget = posName
            self.TransBlock.append(self._formatTransLine(posName,
                  xyz[0]*1000, xyz[1]*1000, xyz[2]*1000,
                  oat[0], oat[1], oat[2], extValues))
         # Apply touch offset if active (not for joint targets or explicit mode)
         if self.currentTsOffset and not self.explicitMode and not isJointTarget:
            posTarget = self.currentTsOffset + ' + ' + posTarget
         # Wrap in TRSUB if rotary base is active
         if self.rotbaseOn and not isJointTarget and not self.explicitMode:
            posTarget = 'TRSUB(' + posTarget + ')'
         # Handle circular via-point first
         if motion.IsCircularMotion():
            viaPos = motion.GetViaPosition()
            if viaPos:
               self._emitCircularVia(viaPos, extValues)
         # Motion instruction
         condSep = ',' if self.explicitMode else ' ,'
         if self.arcOnIsFirstMotion:
            self.Source.append('LWS ' + posTarget + ' ')
            self.arcOnIsFirstMotion = False
         elif self.arcOnLastProcessCurve:
            lweEnd = condSep + str(self.weldConditionNumber)
            if self.hasCrater:
               lweEnd += ',' + str(self.craterCondNumber)
            self.Source.append('LWE ' + posTarget + lweEnd)
            self.arcOnLastProcessCurve = False
            self.arcOnActive = False
            if self.hasSensing:
               self.Source.append('SSENSING OFF')
            if self.hasRtpm:
               self.Source.append('RTPM OFF')
         elif self.arcOnActive:
            if motion.IsCircularMotion():
               self.Source.append('C2WC ' + posTarget + condSep + str(self.weldConditionNumber))
            elif motion.IsLinearMotion():
               self.Source.append('LWC ' + posTarget + condSep + str(self.weldConditionNumber))
            else:
               self.Source.append('JMOVE ' + posTarget)
         elif motion.IsLinearMotion():
            self.Source.append('LMOVE ' + posTarget)
         elif motion.IsCircularMotion():
            self.Source.append('C2MOVE ' + posTarget)
         else:
            self.Source.append('JMOVE ' + posTarget)
      for i, event in enumerate(eventsAfter):
         if i not in readAheadIndices:
            self.HandleEvent(operator, event, motion)

   def _emitCircularVia(self, viaPos, parentExtValues):
      viaXyz = viaPos.GetXYZ()
      viaAngles = viaPos.GetOrientation()
      viaOat = self.EulerConverter.ConvertEuler(viaAngles[0], viaAngles[1], viaAngles[2],
            Notations.Euler_ZYZr, Notations.Euler_XYZs)
      viaExternals = viaPos.GetExternalJointValues()
      viaExternals.sort(key=lambda ext: ext[0].GetJointIndex())
      viaExt = []
      for joint_obj, value in viaExternals:
         if joint_obj.GetJointType() == JointKinematicType.Prismatic:
            viaExt.append(value * 1000)
         else:
            viaExt.append(value)
      if self.explicitMode:
         viaTarget = self._formatTransInline(
               viaXyz[0]*1000, viaXyz[1]*1000, viaXyz[2]*1000,
               viaOat[0], viaOat[1], viaOat[2], viaExt)
      else:
         viaTarget = viaPos.GetName()
         self.TransBlock.append(self._formatTransLine(viaPos.GetName(),
               viaXyz[0]*1000, viaXyz[1]*1000, viaXyz[2]*1000,
               viaOat[0], viaOat[1], viaOat[2], viaExt))
      if self.currentTsOffset and not self.explicitMode:
         viaTarget = self.currentTsOffset + ' + ' + viaTarget
      if self.rotbaseOn and not self.explicitMode:
         viaTarget = 'TRSUB(' + viaTarget + ')'
      if self.arcOnActive:
         condSep = ',' if self.explicitMode else ' ,'
         self.Source.append('C1WC ' + viaTarget + condSep + str(self.weldConditionNumber))
      else:
         self.Source.append('C1MOVE ' + viaTarget)

   # ==================== EVENTS ====================

   def HandleEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion: DULPythonMotion):
      name = event.GetName()
      if name == 'Speed':
         self._handleSpeed(event)
      elif name == 'Accuracy':
         self._handleAccuracy(event)
      elif name in ('ApproachArcWeldingStitch', 'Approach'):
         self._handleApproach(event)
      elif name in ('RetractArcWeldingStitch', 'Retract'):
         pass
      elif name == 'ArcOnEvent':
         self._handleArcOn(event)
      elif name == 'ArcOffEvent':
         self._handleArcOff(event, motion)
      elif name == 'ArcWeldConditionEvent':
         self._handleArcWeldCondition(event)
      elif name == 'LogicPort':
         self._handleLogicPort(event)
      elif name == 'SetResourcePort':
         self._handleSetResourcePort(event)
      elif name == 'WaitForResourcePort':
         self._handleWaitResourcePort(event)
      elif name == 'TextEvent':
         self._handleTextEvent(event)
      elif name == 'LT_Param_Event':
         self._handleLTParam(event)
      elif name == 'LTOnEvent':
         self.Source.append('LT ON')
      elif name == 'LTOffEvent':
         self.Source.append('LT OFF')
      elif name == 'SPSEvent':
         self._handleSPSEvent(event)
      elif name == 'TouchPointStartAppEvent':
         pass
      elif name == 'TouchPointCollisionEvent':
         self._handleTouchCollision(event, motion)
      elif name == 'TouchPointStartRetEvent':
         pass
      elif name == 'ConnectTouchProcessPointEvent':
         self._handleConnectTouchProcess(event)
      elif name == 'TouchSensingEvent':
         pass
      elif name == 'Acceleration':
         self._handleAcceleration(event)
      elif name == 'BuiltInEvent':
         self.pendingSpeed = (self._formatNum(self.ptpSpeed), None)
      for eventMotion in event.GetMotions():
         self.HandleMotion(operator, eventMotion)

   def _handleSpeed(self, event: DULPythonEvent):
      pathtype = ''
      speed = 0.0
      for attr in event.GetAttributes():
         if attr.GetName() == 'Value':
            speed = float(attr.GetValue())
         elif attr.GetName() == 'PathType':
            pathtype = attr.GetValue()
      if pathtype == 'Contour':
         mmps = speed * 1000
         self.pendingSpeed = (self._formatNum(mmps), 'MM/S')
      else:
         self.pendingSpeed = (self._formatNum(speed), None)

   def _handleAccuracy(self, event: DULPythonEvent):
      criteria = ''
      value = 0.0
      for attr in event.GetAttributes():
         if attr.GetName() == 'Value':
            value = float(attr.GetValue())
         elif attr.GetName() == 'Criteria':
            criteria = attr.GetValue()
      if criteria == 'Off':
         self.pendingCp = 'OFF'
      elif criteria == 'Distance':
         if self.inWeldSection and not self.arcOnActive:
            return
         if self.inWeldSection and self.arcOnActive:
            mm = value * 1000
            if mm > 0:
               self.pendingAccuracy = self._formatNum(mm)
         else:
            self.pendingCp = 'ON'
            mm = value * 1000
            if mm > 0:
               self.pendingAccuracy = self._formatNum(mm)
      elif criteria == 'On':
         self.pendingCp = 'ON'
         mm = value * 1000
         if mm > 0:
            self.pendingAccuracy = self._formatNum(mm)

   def _handleApproach(self, event: DULPythonEvent):
      self.pendingAccel = '100'
      self.pendingSpeed = (self._formatNum(self.ptpSpeed), None)

   def _handleAcceleration(self, event: DULPythonEvent):
      value = 100.0
      for attr in event.GetAttributes():
         if attr.GetName() == 'Value':
            value = float(attr.GetValue())
      self.pendingAccel = self._formatNum(value)

   def _handleLogicPort(self, event: DULPythonEvent):
      eventType = ''
      sigName = ''
      sigAddress = ''
      sigValue = True
      for attr in event.GetAttributes():
         name = attr.GetName()
         if name == 'EventType':
            eventType = attr.GetValue()
         elif name == 'SignalName':
            sigName = attr.GetValue()
         elif name == 'SignalAddress':
            sigAddress = attr.GetValue()
         elif name == 'SignalValue':
            sigValue = attr.GetValue()
      sign = '' if str(sigValue) == 'True' else '-'
      onOff = 'On' if str(sigValue) == 'True' else 'Off'
      if eventType == 'CENE2SetSignal':
         self.Source.append('SIGNAL ' + sign + sigAddress + ' ; ' + sigName + '=' + onOff)
      elif eventType == 'CENE2WaitForSignal':
         self.Source.append('SWAIT ' + sign + sigAddress + ' ; ' + sigName + '=' + onOff)

   def _handleSetResourcePort(self, event: DULPythonEvent):
      names = []
      addresses = []
      values = []
      for attr in event.GetAttributes():
         n = attr.GetName()
         if n == 'SignalName':
            names.append(attr.GetValue())
         elif n == 'SignalAddress':
            addresses.append(attr.GetValue())
         elif n == 'SignalValue':
            values.append(attr.GetValue())
      for i in range(len(names)):
         sign = '' if str(values[i]) == 'True' else '-'
         onOff = 'On' if str(values[i]) == 'True' else 'Off'
         self.Source.append('SIGNAL ' + sign + addresses[i] + ' ; ' + names[i] + '=' + onOff)

   def _handleWaitResourcePort(self, event: DULPythonEvent):
      names = []
      addresses = []
      values = []
      for attr in event.GetAttributes():
         n = attr.GetName()
         if n == 'SignalName':
            names.append(attr.GetValue())
         elif n == 'SignalAddress':
            addresses.append(attr.GetValue())
         elif n == 'SignalValue':
            values.append(attr.GetValue())
      for i in range(len(names)):
         sign = '' if str(values[i]) == 'True' else '-'
         onOff = 'On' if str(values[i]) == 'True' else 'Off'
         self.Source.append('WAIT SIG(' + sign + addresses[i] + ') ; ' + names[i] + '=' + onOff)

   def _handleTextEvent(self, event: DULPythonEvent):
      text = ''
      isComment = False
      for attr in event.GetAttributes():
         if attr.GetName() == 'Text':
            text = attr.GetValue()
         elif attr.GetName() == 'IsComment':
            isComment = str(attr.GetValue()) == 'True'
      if isComment:
         self.Source.append('; ' + text)
      else:
         self.Source.append(text)

   def _handleLTParam(self, event: DULPythonEvent):
      jobNum = 0
      biasX = 0.0
      biasY = 0.0
      biasZ = 0.0
      ltOff = False
      for attr in event.GetAttributes():
         name = attr.GetName()
         if name == 'DLJobNumberLaser':
            jobNum = int(attr.GetValue())
         elif name == 'DLLTBiasX':
            biasX = float(attr.GetValue()) * 1000
         elif name == 'DLLTBiasY':
            biasY = float(attr.GetValue()) * 1000
         elif name == 'DLLTBiasZ':
            biasZ = float(attr.GetValue()) * 1000
         elif name == 'DLLTOff':
            ltOff = str(attr.GetValue()) == 'True'
      self.Source.append('LJT ' + str(jobNum))
      self.Source.append('LTBIAS ' + str(round(biasX)) + ',' + str(round(biasY)) + ',' + str(round(biasZ)))
      if ltOff:
         self.Source.append('LT OFF')

   def _handleSPSEvent(self, event: DULPythonEvent):
      patternNum = 0
      startDist = 0
      reliefDist = 0
      distInGroove = 0
      for attr in event.GetAttributes():
         name = attr.GetName()
         if name == 'DLPatternNum':
            patternNum = int(attr.GetValue())
         elif name == 'DLStartDist':
            startDist = int(attr.GetValue())
         elif name == 'DLReliefDist':
            reliefDist = int(attr.GetValue())
         elif name == 'DLDistInGroove':
            distInGroove = int(attr.GetValue())
      self.Source.append('SSENSPTN ' + ','.join([str(patternNum), str(startDist), str(reliefDist), str(distInGroove)]))

   def _flushPendingMotionData(self):
      if self.pendingSpeed is not None:
         if not self.arcOnActive:
            if self.pendingSpeed != self.lastSpeed:
               val, suffix = self.pendingSpeed
               if suffix:
                  self.Source.append('SPEED ' + val + ' ' + suffix + ' ALWAYS')
               else:
                  self.Source.append('SPEED ' + val + ' ALWAYS')
               self.lastSpeed = self.pendingSpeed
         self.pendingSpeed = None
      if self.pendingAccel is not None:
         if not self.hasTouchSensing:
            if self.pendingAccel != self.lastAccel:
               self.Source.append('ACCEL ' + self.pendingAccel + ' ALWAYS')
               self.lastAccel = self.pendingAccel
         self.pendingAccel = None
      if self.pendingCp is not None:
         if not self.hasTouchSensing and not self.explicitMode:
            if self.pendingCp == 'OFF' and self.lastCp != 'OFF':
               self.Source.append('CP OFF')
               self.lastCp = 'OFF'
         self.pendingCp = None
      if self.pendingAccuracy is not None:
         if not self.arcOnActive:
            if self.pendingAccuracy != self.lastAccuracy:
               self.Source.append('ACCURACY ' + self.pendingAccuracy + ' ALWAYS')
               self.lastAccuracy = self.pendingAccuracy
         self.pendingAccuracy = None

   def _handleArcOn(self, event: DULPythonEvent):
      attrs = {}
      for attr in event.GetAttributes():
         attrs[attr.GetName()] = str(attr.GetValue())
      condMode = int(attrs.get('DLWeldConditionMode', '0'))
      self.inWeldSection = True
      if condMode >= 2:
         return
      condNumber = int(attrs.get('DLWeldConditionNumber', '1'))
      jobNumber = int(attrs.get('DLJobNumber', '1'))
      self.weldConditionNumber = condNumber
      # SETCONDW1
      weldSpeed = int(float(attrs.get('DLWC1WeldSpeed', '0')))
      wireFeed = int(float(attrs.get('DLWC1WireFeedSpeed', '0')))
      weldCurrent = int(float(attrs.get('DLWC1WeldCurrent', '0')))
      arcLength = int(float(attrs.get('DLWC1ArcLengthCorr', '0')))
      weldVoltage = int(float(attrs.get('DLWC1WeldVoltage', '0')))
      pulseDynamic = int(float(attrs.get('DLWC1PulseDynamicCorr', '0')))
      wireRetract = int(float(attrs.get('DLWC1WireRetractCorr', '0')))
      weaveWidthMM = float(attrs.get('DLWeaveWidth', '0')) * 1000
      weaveFreq = float(attrs.get('DLWeaveFrequenz', '0'))
      weavePatternNum = int(attrs.get('DLWeavePatternNumber', '0'))
      self.Source.append('SET_ARC_W1JOBNO ' + str(condNumber) + ' = ' + str(jobNumber))
      if condMode == 0:
         w1 = [str(weldSpeed), str(wireFeed), str(arcLength),
               str(pulseDynamic), str(wireRetract)]
      else:
         w1 = [str(weldSpeed), str(weldCurrent), str(weldVoltage),
               str(pulseDynamic), str(wireRetract)]
      w1.extend([self._fmtRound1(weaveWidthMM), self._fmtRound1(weaveFreq), str(weavePatternNum)])
      self.Source.append('SETCONDW1 ' + str(condNumber) + ' = ' + ','.join(w1))
      # Crater (SETCONDW2)
      self.hasCrater = attrs.get('DLWC2Crater', 'False') == 'True'
      if self.hasCrater:
         craterCondNum = int(attrs.get('DLCraterSpotConditionNumber', '1'))
         craterJobNum = int(attrs.get('DLCraterSpotJobNumber', '1'))
         self.craterCondNumber = craterCondNum
         self.Source.append('SET_ARC_W2JOBNO ' + str(craterCondNum) + ' = ' + str(craterJobNum))
         t = self._fmtRound1(float(attrs.get('DLWC2Time', '0')))
         if condMode == 0:
            w2 = [str(t), str(int(float(attrs.get('DLWC2WireFeedSpeed', '0')))),
                  str(int(float(attrs.get('DLWC2ArcLengthCorr', '0')))),
                  str(int(float(attrs.get('DLWC2PulseDynamicCorr', '0')))),
                  str(int(float(attrs.get('DLWC2WireRetractCorr', '0'))))]
         else:
            w2 = [str(t), str(int(float(attrs.get('DLWC2WeldCurrent', '0')))),
                  str(int(float(attrs.get('DLWC2WeldVoltage', '0')))),
                  str(int(float(attrs.get('DLWC2PulseDynamicCorr', '0')))),
                  str(int(float(attrs.get('DLWC2WireRetractCorr', '0'))))]
         self.Source.append('SETCONDW2 ' + str(craterCondNum) + ' = ' + ','.join(w2))
      # SETCONDW3 (software slowdown)
      ssDown = attrs.get('DLSSDown', 'None')
      if ssDown == 'Enabled':
         preHeatTime = '{:f}'.format(float(attrs.get('DLWCPreHeatTime', '0')))
         ssdWeaveWidth = '{:f}'.format(float(attrs.get('DLWCWeaveWidth', '0')))
         ssdWeaveFreq = '{:f}'.format(float(attrs.get('DLWCWeaveFreq', '0')))
         ssdWeaveNum = str(int(attrs.get('DLWCWeaveNum', '0')))
         self.Source.append('SETCONDW3 ' + preHeatTime + ',,,,,' + ssdWeaveWidth + ',' + ssdWeaveFreq + ', ' + ssdWeaveNum)
      # Seam sensing pattern
      dlPatternNum = int(attrs.get('DLPatternNum', '1'))
      self.hasSensing = dlPatternNum > 1
      if self.hasSensing:
         self.Source.append('SSENSPTN ' + str(self._mapSensingPattern(dlPatternNum)))
         startDist = '{:f}'.format(float(attrs.get('DLStartDist', '0')))
         reliefDist = '{:f}'.format(float(attrs.get('DLReliefDist', '0')))
         distInGroove = '{:f}'.format(float(attrs.get('DLDistInGroove', '0')))
         self.Source.append('SSENS_SET ' + startDist + ', ' + reliefDist + ', ' + distInGroove)
         self.Source.append('SSENSING ON')
      # RTPM block
      rtpmMode = attrs.get('DLRTPM', 'None')
      rtpmNum = int(attrs.get('DLWCRTPMNum', '0'))
      self.hasRtpm = rtpmMode == 'Enabled' and rtpmNum == 2
      if self.hasRtpm:
         startGain = attrs.get('DLWCStartGain', 'False') == 'True'
         if startGain:
            gainTime = '{:f}'.format(float(attrs.get('DLWCInitialGainTime', '0')))
            vertCur = str(int(attrs.get('DLWCInitialVerticalCurrent', '0')))
            horizCur = str(int(attrs.get('DLWCInitialHorizontalCurrent', '0')))
            changeCur = str(int(attrs.get('DLWCInitialChangeCurrent', '0')))
            self.Source.append('RTPM2_STARTGain ON, ' + gainTime + ', ' + vertCur + ', ' + horizCur + ', ' + changeCur)
         else:
            self.Source.append('RTPM2_STARTGain OFF')
         self.Source.append('RT2DLYTIME ' + str(int(attrs.get('DLWCDelayTime', '0'))))
         self.Source.append('SET_ARC_RTPMREF ' + str(int(attrs.get('DLWCWireStick', '0'))))
         vertGain = str(int(attrs.get('DLWCVerticalGain', '0')))
         horizGain = str(int(attrs.get('DLWCHorizontalGain', '0')))
         self.Source.append('RT2Gain ' + vertGain + ', ' + horizGain)
         vertBias = str(int(attrs.get('DLWCVerticalBIAS', '0')))
         horizBias = str(int(attrs.get('DLWCHorizontalBIAS', '0')))
         self.Source.append('RT2BIAS ' + vertBias + ', ' + horizBias)
         self.Source.append('RTPM ON')
      self.arcOnActive = True
      self.arcOnIsFirstMotion = True

   def _handleArcOff(self, event: DULPythonEvent, motion: DULPythonMotion):
      self.inWeldSection = False
      if not self.arcOnActive:
         return
      self.arcOnLastProcessCurve = True

   def _mapSensingPattern(self, dlPatternNum):
      if 2 <= dlPatternNum <= 7:
         return dlPatternNum + 99
      elif 8 <= dlPatternNum <= 12:
         return dlPatternNum - 7
      return dlPatternNum

   def _handleArcWeldCondition(self, event: DULPythonEvent):
      attrs = {}
      for attr in event.GetAttributes():
         attrs[attr.GetName()] = str(attr.GetValue())
      condMode = int(attrs.get('DLWeldConditionMode', '0'))
      if condMode >= 2:
         return
      condNumber = int(attrs.get('DLWeldConditionNumber', '1'))
      jobNumber = int(attrs.get('DLJobNumber', '1'))
      self.weldConditionNumber = condNumber
      # Weave comments
      weavePatternName = attrs.get('DLWCWeavePattern', 'no weaving')
      if weavePatternName != 'no weaving':
         self.Source.append(';WeavePattern: ' + weavePatternName)
         self.Source.append(';WeaveNum: ' + str(int(attrs.get('DLWCWeaveNum', '0'))))
      # SETCONDW3 (software slowdown)
      ssDown = attrs.get('DLSSDown', 'None')
      if ssDown == 'Enabled':
         preHeatTime = '{:f}'.format(float(attrs.get('DLWCPreHeatTime', '0')))
         ssdWeaveWidth = '{:f}'.format(float(attrs.get('DLWCWeaveWidth', '0')))
         ssdWeaveFreq = '{:f}'.format(float(attrs.get('DLWCWeaveFreq', '0')))
         ssdWeaveNum = str(int(attrs.get('DLWCWeaveNum', '0')))
         self.Source.append('SETCONDW3 ' + preHeatTime + ',,,,,' + ssdWeaveWidth + ',' + ssdWeaveFreq + ', ' + ssdWeaveNum)
      # RTPM block
      rtpmMode = attrs.get('DLRTPM', 'None')
      rtpmNum = int(attrs.get('DLWCRTPMNum', '0'))
      self.hasRtpm = rtpmMode == 'Enabled' and rtpmNum == 2
      if self.hasRtpm:
         startGain = attrs.get('DLWCStartGain', 'False') == 'True'
         if startGain:
            gainTime = '{:f}'.format(float(attrs.get('DLWCInitialGainTime', '0')))
            vertCur = str(int(attrs.get('DLWCInitialVerticalCurrent', '0')))
            horizCur = str(int(attrs.get('DLWCInitialHorizontalCurrent', '0')))
            changeCur = str(int(attrs.get('DLWCInitialChangeCurrent', '0')))
            self.Source.append('RTPM2_STARTGain ON, ' + gainTime + ', ' + vertCur + ', ' + horizCur + ', ' + changeCur)
         else:
            self.Source.append('RTPM2_STARTGain OFF')
         self.Source.append('SET_ARC_RTPMREF ' + str(int(attrs.get('DLWCWireStick', '0'))))
         self.Source.append('RT2DLYTIME ' + str(int(attrs.get('DLWCDelayTime', '0'))))
         vertGain = str(int(attrs.get('DLWCVerticalGain', '0')))
         horizGain = str(int(attrs.get('DLWCHorizontalGain', '0')))
         self.Source.append('RT2Gain ' + vertGain + ', ' + horizGain)
         vertBias = str(int(attrs.get('DLWCVerticalBIAS', '0')))
         horizBias = str(int(attrs.get('DLWCHorizontalBIAS', '0')))
         self.Source.append('RT2BIAS ' + vertBias + ', ' + horizBias)
         self.Source.append('RTPM ON')
      # Seam sensing pattern
      dlPatternNum = int(attrs.get('DLPatternNum', '1'))
      self.hasSensing = dlPatternNum > 1
      if self.hasSensing:
         self.Source.append('SSENSPTN ' + str(self._mapSensingPattern(dlPatternNum)))
         startDist = '{:f}'.format(float(attrs.get('DLStartDist', '0')))
         reliefDist = '{:f}'.format(float(attrs.get('DLReliefDist', '0')))
         distInGroove = '{:f}'.format(float(attrs.get('DLDistInGroove', '0')))
         self.Source.append('SSENS_SET ' + startDist + ', ' + reliefDist + ', ' + distInGroove)
         self.Source.append('SSENSING ON')
      # SET_ARC_WELDMODE
      arcWeldMode = attrs.get('DLSetArcWeldMode', 'None')
      if arcWeldMode != 'None':
         self.Source.append('SET_ARC_WELDMODE ' + arcWeldMode)
      # SETCONDW1
      weldSpeed = int(float(attrs.get('DLWC1WeldSpeed', '0')))
      wireFeed = int(float(attrs.get('DLWC1WireFeedSpeed', '0')))
      weldCurrent = int(float(attrs.get('DLWC1WeldCurrent', '0')))
      arcLength = int(float(attrs.get('DLWC1ArcLengthCorr', '0')))
      weldVoltage = int(float(attrs.get('DLWC1WeldVoltage', '0')))
      pulseDynamic = int(float(attrs.get('DLWC1PulseDynamicCorr', '0')))
      wireRetract = int(float(attrs.get('DLWC1WireRetractCorr', '0')))
      weaveWidthMM = float(attrs.get('DLWeaveWidth', '0')) * 1000
      weaveFreq = float(attrs.get('DLWeaveFrequenz', '0'))
      weavePatternNum = int(attrs.get('DLWeavePatternNumber', '0'))
      self.Source.append('SET_ARC_W1JOBNO ' + str(condNumber) + ' = ' + str(jobNumber))
      if condMode == 0:
         w1 = [str(weldSpeed), str(wireFeed), str(arcLength),
               str(pulseDynamic), str(wireRetract)]
      else:
         w1 = [str(weldSpeed), str(weldCurrent), str(weldVoltage),
               str(pulseDynamic), str(wireRetract)]
      w1.extend([self._fmtRound1(weaveWidthMM), self._fmtRound1(weaveFreq), str(weavePatternNum)])
      self.Source.append('SETCONDW1 ' + str(condNumber) + ' = ' + ','.join(w1))
      # Crater (SETCONDW2)
      self.hasCrater = attrs.get('DLWC2Crater', 'False') == 'True'
      if self.hasCrater:
         craterCondNum = int(attrs.get('DLCraterSpotConditionNumber', '1'))
         craterJobNum = int(attrs.get('DLCraterSpotJobNumber', '1'))
         self.craterCondNumber = craterCondNum
         self.Source.append('SET_ARC_W2JOBNO ' + str(craterCondNum) + ' = ' + str(craterJobNum))
         t = self._fmtRound1(float(attrs.get('DLWC2Time', '0')))
         if condMode == 0:
            w2 = [str(t), str(int(float(attrs.get('DLWC2WireFeedSpeed', '0')))),
                  str(int(float(attrs.get('DLWC2ArcLengthCorr', '0')))),
                  str(int(float(attrs.get('DLWC2PulseDynamicCorr', '0')))),
                  str(int(float(attrs.get('DLWC2WireRetractCorr', '0'))))]
         else:
            w2 = [str(t), str(int(float(attrs.get('DLWC2WeldCurrent', '0')))),
                  str(int(float(attrs.get('DLWC2WeldVoltage', '0')))),
                  str(int(float(attrs.get('DLWC2PulseDynamicCorr', '0')))),
                  str(int(float(attrs.get('DLWC2WireRetractCorr', '0'))))]
         self.Source.append('SETCONDW2 ' + str(craterCondNum) + ' = ' + ','.join(w2))

   # ==================== TOUCH SENSING ====================

   def _handleTouchCollision(self, event: DULPythonEvent, motion: DULPythonMotion):
      sensingLen = self.sensingLength
      sensingSpd = self.sensingSpeed
      # Compute refId from FramePt (for Frame3pConnect) or 0 (for others)
      if self.tsConnectionType == 'Frame3pConnect':
         if self.currentFramePt != self.lastFramePt:
            refId = self.currentFramePt
            self.lastFramePt = self.currentFramePt
         else:
            refId = 0
      else:
         refId = 0
      for attr in event.GetAttributes():
         name = attr.GetName()
         if name == 'SensingLength':
            sensingLen = float(attr.GetValue()) * 1000
         elif name == 'SensingSpeed':
            sensingSpd = float(attr.GetValue()) * 1000
      self.collisionPending = True
      self.collisionSensingLen = sensingLen
      self.collisionSensingSpd = sensingSpd
      self.collisionRefId = refId

   def _handleConnectTouchProcess(self, event: DULPythonEvent):
      for attr in event.GetAttributes():
         if attr.GetName() == 'TouchId':
            touchId = int(attr.GetValue())
            self.currentTsOffset = self.programName + '_TS_ID_' + str(touchId)
            break

   def _emitTsIdDeclarations(self, operationGroup: DULPythonOperationGroup):
      is3pFrame = self.tsConnectionType == 'Frame3pConnect'
      if is3pFrame:
         self.Source.append('POINT FRAME_PT_1 = NULL')
         self.Source.append('POINT FRAME_PT_2 = NULL')
         self.Source.append('POINT FRAME_PT_3 = NULL')
      # Collect unique TouchId values from touch operations
      touchIds = set()
      for op in operationGroup.GetOperations():
         wmName = ''
         touchId = 0
         for attr in op.GetAttributes():
            if attr.GetName() == 'ArcWeldingOperationWorkMethodName':
               wmName = attr.GetValue()
            elif attr.GetName() == 'TouchId':
               touchId = int(attr.GetValue())
         if 'TouchSensing' in wmName and touchId > 0:
            touchIds.add(touchId)
      for tid in sorted(touchIds):
         tsIdName = self.programName + '_TS_ID_' + str(tid)
         self.Source.append('POINT ' + tsIdName + ' = NULL')

   def _maxTsIdName(self, operationGroup: DULPythonOperationGroup):
      maxTid = 0
      for op in operationGroup.GetOperations():
         wmName = ''
         touchId = 0
         for attr in op.GetAttributes():
            if attr.GetName() == 'ArcWeldingOperationWorkMethodName':
               wmName = attr.GetValue()
            elif attr.GetName() == 'TouchId':
               touchId = int(attr.GetValue())
         if 'TouchSensing' in wmName and touchId > maxTid:
            maxTid = touchId
      return self.programName + '_TS_ID_' + str(maxTid) if maxTid > 0 else ''

   def _scanTreeForTouchSensing(self, program):
      for sub in program.GetSubprograms():
         calledProg = sub.GetCalledProgram()
         for opGroup in calledProg.GetOperationGroups():
            for op in opGroup.GetOperations():
               for attr in op.GetAttributes():
                  if attr.GetName() == 'ArcWeldingOperationWorkMethodName' and 'TouchSensing' in attr.GetValue():
                     return True
      return False

   # ==================== HEADER ====================

   def _isRotBaseProfile(self, baseProfile):
      return baseProfile is not None and baseProfile.GetName().upper().startswith('ROT_BASE')

   def _emitProgramHeader(self, operation: DULPythonOperation):
      baseProfile = operation.GetUsedBaseProfile()
      if self._isRotBaseProfile(baseProfile):
         baseName = baseProfile.GetName()
         self.Source.append('BASE ' + baseName)
         xyz = baseProfile.GetXYZ()
         angles = baseProfile.GetOrientation()
         oat = self.EulerConverter.ConvertEuler(angles[0], angles[1], angles[2],
               Notations.Euler_ZYZr, Notations.Euler_XYZs)
         self.TransBlock.append(self._formatTransLine(baseName,
               xyz[0]*1000, xyz[1]*1000, xyz[2]*1000, oat[0], oat[1], oat[2]))
      else:
         self.Source.append('BASE NULL')
      toolProfile = operation.GetUsedToolProfile()
      if toolProfile:
         self.Source.append('TOOL ' + self.programName + '_' + toolProfile.GetName())
      self.Source.append('RIGHTY')
      self.Source.append('ABOVE')
      self.Source.append('DWRIST')

   # ==================== SUBROUTINES ====================

   def _emitTouchSubroutines(self):
      self.Source.append('.PROGRAM kr_touch(.&ref,.&offset,.l_rot_base,.search_dist,.search_speed,.frm_ref_id) ; Kawasaki Robotics Touch Sensing')
      self.Source.append('  ; *******************************************************************')
      self.Source.append('  ;')
      self.Source.append('  ; Program:      kr_touch')
      self.Source.append('  ; Comment:      Kawasaki Robotics Touch Sensing')
      self.Source.append('  ; Author:       CENIT AG')
      self.Source.append('  ;')
      self.Source.append('  ; Date:         8/8/2023')
      self.Source.append('  ;')
      self.Source.append('  ; *******************************************************************')
      self.Source.append('  ;')
      self.Source.append('  ;Assign reference points for frame calculation')
      self.Source.append('  CASE INT(.frm_ref_id) OF')
      self.Source.append('  VALUE 1')
      self.Source.append('    POINT FRAME_PT_1 = NULL')
      self.Source.append('    POINT FRAME_PT_2 = NULL')
      self.Source.append('    POINT FRAME_PT_3 = NULL')
      self.Source.append('    POINT FRAME_REF_PT_1 = NULL')
      self.Source.append('    POINT FRAME_REF_PT_2 = NULL')
      self.Source.append('    POINT FRAME_REF_PT_3 = NULL')
      self.Source.append('    POINT FRAME_REF_PT_1 = .ref')
      self.Source.append('  VALUE 2')
      self.Source.append('    POINT FRAME_REF_PT_2 = .ref')
      self.Source.append('  VALUE 3')
      self.Source.append('    POINT FRAME_REF_PT_3 = .ref')
      self.Source.append('  ANY')
      self.Source.append('    PRINT "Frame point index is greater than 3!"')
      self.Source.append('  END')
      self.Source.append('  ;')
      self.Source.append('  if .l_rot_base == 1 THEN')
      self.Source.append('    ; Transform reference point from Rot_Base to B0 since XAC requires B0 coordinates')
      self.Source.append('    POINT .ref_in_b0 = TRSUB (.offset + .ref)')
      self.Source.append('    POINT .ref_in_rb = .offset + .ref')
      self.Source.append('    XAC .ref_in_b0, .touch, .search_dist, .search_speed')
      self.Source.append('    BREAK')
      self.Source.append('    ; Transform touch result from B0 to Rot_Base')
      self.Source.append('    POINT .touch_rb = TRADD (.touch)')
      self.Source.append('    ;remove the TCPs OAT and EXT values from reference and touch positions')
      self.Source.append('    POINT/OAT .ref_in_rb = NULL')
      self.Source.append('    POINT/OAT .touch_rb = NULL')
      self.Source.append('    POINT/EXT .ref_in_rb = NULL')
      self.Source.append('    POINT/EXT .touch_rb = NULL')
      self.Source.append('    ;calculate offset values in rb coordinates')
      self.Source.append('    POINT .offset = .offset + (.touch_rb -.ref_in_rb)')
      self.Source.append('  ELSE')
      self.Source.append('    POINT .ref_in_base = .offset + .ref')
      self.Source.append('    XAC .ref_in_base, .touch, .search_dist, .search_speed')
      self.Source.append('    BREAK')
      self.Source.append('    POINT .ref_in_base_xyz = .ref_in_base')
      self.Source.append('    POINT .touch_xyz = .touch')
      self.Source.append('    POINT/OAT .ref_in_base_xyz = NULL')
      self.Source.append('    POINT/OAT .touch_xyz = NULL')
      self.Source.append('    POINT/EXT .ref_in_rb = NULL')
      self.Source.append('    POINT/EXT .touch_rb = NULL')
      self.Source.append('    POINT .offset = .offset + (.touch_xyz - .ref_in_base_xyz)')
      self.Source.append('  END')
      self.Source.append('.END')
      self.Source.append('.PROGRAM kr_frame(.&ref_pt1,.&ref_pt2,.&ref_pt3,.&frm_pt1,.&frm_pt2,.&frm_pt3,.&offset) ; Kawasaki Robotics Frame Calculation')
      self.Source.append('  ; *******************************************************************')
      self.Source.append('  ;')
      self.Source.append('  ; Program:      kr_frame')
      self.Source.append('  ; Comment:      Kawasaki Robotics Frame Calculation')
      self.Source.append('  ; Author:       CENIT AG')
      self.Source.append('  ;')
      self.Source.append('  ; Date:         9/6/2023')
      self.Source.append('  ;')
      self.Source.append('  ; *******************************************************************')
      self.Source.append('  ;')
      self.Source.append('  ; Define reference frame')
      self.Source.append('  POINT .frm_ref = FRAME (.ref_pt1, .ref_pt2, .ref_pt3, .ref_pt1)')
      self.Source.append('  ; Define corrected reference frame')
      self.Source.append('  POINT .frm_touch = FRAME (.frm_pt1 + .ref_pt1, .frm_pt2 + .ref_pt2, .frm_pt3 + .ref_pt3, .frm_pt1 + .ref_pt1)')
      self.Source.append('  ; Calculate correction and assign to correction ID')
      self.Source.append('  POINT .offset = .frm_touch - .frm_ref')
      self.Source.append('.END')

   # ==================== FORMATTING ====================

   def _fmtRound1(self, value):
      r = round(value, 1)
      return str(int(r)) if r == int(r) else str(r)

   def _formatNum(self, value):
      if value == int(value):
         return str(int(value))
      formatted = '{:.3f}'.format(value).rstrip('0').rstrip('.')
      return formatted

   def _formatTransNum(self, value):
      if abs(value) < 0.005:
         return '0'
      if abs(abs(value) - 180) < 0.005:
         value = 180.0
      if value == int(value):
         return str(int(value))
      formatted = '{:.2f}'.format(value).rstrip('0').rstrip('.')
      return formatted

   def _formatTransLine(self, name, x, y, z, o, a, t, extValues=None):
      parts = [name,
            self._formatTransNum(x), self._formatTransNum(y), self._formatTransNum(z),
            self._formatTransNum(o), self._formatTransNum(a), self._formatTransNum(t)]
      if extValues:
         for v in extValues:
            parts.append(self._formatTransNum(v))
      return ' '.join(parts)

   def _formatTransInline(self, x, y, z, o, a, t, extValues=None):
      parts = [self._formatTransNum(x), self._formatTransNum(y), self._formatTransNum(z),
            self._formatTransNum(o), self._formatTransNum(a), self._formatTransNum(t)]
      if extValues:
         for v in extValues:
            parts.append(self._formatTransNum(v))
      return 'TRANS (' + ', '.join(parts) + ')'

   # ==================== FILE OUTPUT ====================

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      self.outputFilePath = self.outputDir + '\\' + self.programName + self.FILE_EXTENSION

   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      self.FileUtil.AppendTextArrayToFile(self.outputFilePath, self.Source)
      self.Source.clear()

   def CloseOutputFile(self, operator: DULPythonDownloadOperator):
      operator.AddOutputFilePath(self.outputFilePath)

   def SubprogramStart(self, operator: DULPythonDownloadOperator, subprogram: DULPythonSubprogram):
      self.Source.append('CALL ' + subprogram.GetName())

   def SubProgramEnd(self, operator: DULPythonDownloadOperator, subprogram: DULPythonSubprogram):
      pass
