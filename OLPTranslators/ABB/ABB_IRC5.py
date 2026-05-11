"""
COPYRIGHT Cenit AG Q1/2024
   ABB RAPID Downloader

   This downloader* SUPPORTs:
      - Motion commands MoveJ/MoveL/MoveC
      - tool & base frame mapping  (base)
      - motion events (speed, accuracy, acceleration, dwell, logic port)
      - Digital signals (set/wait) – only boolean type
      
   NOTE: This downloader only supports the listed functions.
"""

from __future__ import annotations

import math
import json
import re
import sys, inspect, os
import importlib
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple

sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from datetime import datetime
from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *
from centypes import *

try:
   import data_utils as dm_utils
except ImportError:
   dm_utils = None  # type: ignore[assignment]


class _ABBSharedState:
   """Shared state between ABB downloader and plugins.
   
   This object provides explicit API contract for state that plugins
   need to read/write and downloader uses for code generation.
   
   Attributes:
      touchid_mode_map: Maps TouchId to TSConnectionType ("OperationConnect", 
                        "StartEndConnect", "ShortestDistanceConnect", "Frame3pConnect")
      current_point_ref: Last emitted point reference (e.g., "P005")
      last_point_ref: Previous point reference
      active_wobj_name: Current work object name (station wobj or obNEW_<TouchId>)
      station_wobj_name: Station-specific work object (e.g., "wobjUse")
      frame3p_wobj_active: True when using Frame3pConnect corrected work object
   """
   def __init__(self):
      self.touchid_mode_map = {}  # type: Dict[int, str]
      self.current_point_ref = None  # type: Optional[str]
      self.last_point_ref = None  # type: Optional[str]
      self.active_wobj_name = None  # type: Optional[str]
      self.station_wobj_name = None  # type: Optional[str]
      self.frame3p_wobj_active = False  # type: bool


class _ABBPluginBase:
   """Minimal plugin API for ABB downloader.

   Plugins may:
   - react to events (before/after)
   - participate in read-ahead (events-after that affect current motion output)
   - decorate/replace the emitted motion command
   """

   @property
   def name(self) -> str:
      return self.__class__.__name__

   @property
   def read_ahead_events(self):
      return set()

   # Per-operation activation flag — set by operation_start based on MACHINING_TECH_TYPE
   _active = True

   def initialize(self, operator: DULPythonDownloadOperator, downloader: 'ABB_IRC5') -> None:
      return

   def program_start(self, operator: DULPythonDownloadOperator, program: DULPythonProgram, downloader: 'ABB_IRC5') -> None:
      return

   def program_end(self, operator: DULPythonDownloadOperator, program: DULPythonProgram, downloader: 'ABB_IRC5') -> None:
      return

   def operation_start(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      return

   def operation_end(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      return

   def handle_event_before(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      return

   def handle_read_ahead_event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      return

   def decorate_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, cmd: str, downloader: 'ABB_IRC5') -> str:
      return cmd


class _ABBPluginManager:
   def __init__(self) -> None:
      self._plugins = []  # type: List[_ABBPluginBase]
      self.read_ahead_events = set()  # type: Set[str]

   @property
   def plugins(self):
      return self._plugins

   def set_plugins(self, plugins):
      self._plugins = plugins
      self.read_ahead_events = set()
      for plugin in plugins:
         self.read_ahead_events |= set(plugin.read_ahead_events)

   def initialize(self, operator: DULPythonDownloadOperator, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.initialize(operator, downloader)

   def program_start(self, operator: DULPythonDownloadOperator, program: DULPythonProgram, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.program_start(operator, program, downloader)

   def program_end(self, operator: DULPythonDownloadOperator, program: DULPythonProgram, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.program_end(operator, program, downloader)

   def operation_start(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.operation_start(operator, operation, downloader)

   def operation_end(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.operation_end(operator, operation, downloader)

   def handle_event_before(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.handle_event_before(operator, motion, event, downloader)

   def handle_read_ahead_event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      for plugin in self._plugins:
         plugin.handle_read_ahead_event(operator, motion, event, downloader)

   def decorate_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, cmd: str, downloader: 'ABB_IRC5') -> str:
      for plugin in self._plugins:
         cmd = plugin.decorate_motion_command(operator, motion, cmd, downloader)
      return cmd


class _ABBTouchSensingMixin:
   """Mixin providing Touch Sensing functionality for ABB downloader plugins.

   Handles:
   - TouchPointCollisionEvent → Search_1D generation
   - Frame3pConnect (3-point frame correction via OFrameChange)
   - Displacement modes (OperationConnect, StartEndConnect, ShortestDistanceConnect)
   - Via-point tracking for Search_1D approach points

   Usage: Include as a base class alongside _ABBPluginBase.  Call _init_touch_state()
   from the subclass __init__, and delegate to _touch_handle_read_ahead_event() and
   _touch_decorate_motion_command() from the plugin's own methods.
   """

   TOUCH_EVT_START = 'TouchPointStartAppEvent'
   TOUCH_EVT_COLLISION = 'TouchPointCollisionEvent'

   TOUCH_READ_AHEAD_EVENTS = frozenset({
      'TouchPointStartAppEvent', 'TouchPointCollisionEvent',
      'TouchPointStartRetEvent', 'TouchPointEndEvent'
   })

   def _init_touch_state(self):
      """Initialize touch sensing state.  Call from subclass __init__."""
      self._pending_search = False
      self._record_via_from_this_motion = False
      self._via_point_ref = None  # type: Optional[str]
      self._via_point_robtarget = None  # type: Optional[str]  # For Explicit mode
      self._touch_point_robtarget = None  # type: Optional[str]  # For Explicit mode
      self._warned_explicit_once = False

      # TSConnectionType detection: OperationConnect, StartEndConnect, ShortestDistanceConnect, Frame3pConnect
      self._ts_connection_type = ""  # type: str

      # Frame3pConnect (3 FramePts) state
      self._frame3p_pt = None  # FramePt from Frame3pConnect event
      self._frame3p_touch_id = None  # TouchId from Frame3pConnect event
      self._frame3p_mea_counters = {}  # type: dict[tuple[int, int], int]  # (TouchId, FramePt) -> mea counter
      self._is_frame3p_touch = False

      # Displacement modes (OperationConnect, StartEndConnect, ShortestDistanceConnect) state
      self._displacement_touch_id = None  # TouchId for current touch
      self._displacement_mea_counters = {}  # type: dict[int, int]  # TouchId -> mea counter
      self._displacement_touch_cntr = {}  # type: dict[int, int]  # TouchId -> Touch_Cntr (total touches per TouchId)

   def _touch_handle_read_ahead_event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> bool:
      """Handle touch-specific read-ahead events.

      Returns True if the event was consumed by touch sensing (caller should not process further).
      """
      name = event.GetName()

      if name == self.TOUCH_EVT_START:
         self._record_via_from_this_motion = True
         return True

      if name == self.TOUCH_EVT_COLLISION:
         # Detect TSConnectionType at OperationGroup level
         if downloader._current_operation_group is not None:
            try:
               self._ts_connection_type = downloader._current_operation_group.GetLiteralAttribute('TSConnectionType', True).GetValue()
            except Exception:
               self._ts_connection_type = ""

         # Read Touch_Cntr from current operation (per TouchId)
         touch_cntr = 0
         if downloader._current_operation is not None:
            try:
               touch_cntr = downloader._current_operation.GetIntegerAttribute('Touch_Cntr', True).GetValue()
            except Exception:
               pass

         operator.GetLogOperator().LogDebug(f"TouchSensing: TouchPointCollisionEvent TSConnectionType='{self._ts_connection_type}', Touch_Cntr={touch_cntr}")

         if self._ts_connection_type == "Frame3pConnect":
            # Frame3pConnect: Use tid<TouchId>_pt<FramePt>_mea<N> naming
            self._frame3p_pt = event.GetIntegerAttribute('FramePt', True).GetValue()
            self._frame3p_touch_id = event.GetIntegerAttribute('TouchId', True).GetValue()
            operator.GetLogOperator().LogInfo(f"TouchSensing: Frame3pConnect detected - TouchId={self._frame3p_touch_id}, FramePt={self._frame3p_pt}")
            self._is_frame3p_touch = True
            self._pending_search = True  # Plugin will generate Search_1D with PrePDisp
            # Track this TouchId as Frame3pConnect mode (in shared state)
            downloader.shared.touchid_mode_map[self._frame3p_touch_id] = "Frame3pConnect"
            # Let downloader track reference points
            downloader.HandleTouchPointCollisionEvent(operator, motion, event)
            return True
         elif self._ts_connection_type in ("OperationConnect", "StartEndConnect", "ShortestDistanceConnect"):
            # Displacement modes: Use tid<TouchId>_mea<N> naming (no FramePt)
            self._is_frame3p_touch = False
            self._displacement_touch_id = event.GetIntegerAttribute('TouchId', True).GetValue()
            # Store Touch_Cntr for this TouchId to determine last touch
            if touch_cntr > 0:
               self._displacement_touch_cntr[self._displacement_touch_id] = touch_cntr
               operator.GetLogOperator().LogDebug(f"Stored Touch_Cntr={touch_cntr} for TouchId={self._displacement_touch_id}")
            # Track this TouchId as displacement mode (in shared state)
            downloader.shared.touchid_mode_map[self._displacement_touch_id] = self._ts_connection_type
            # Plugin handles Search_1D generation for displacement modes
            self._pending_search = True
            operator.GetLogOperator().LogInfo(f"TouchSensing: Set _pending_search=True for displacement mode TouchId={self._displacement_touch_id}")
         return True  # consumed even if no specific branch matched

      return False

   def _touch_decorate_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, cmd: str, downloader: 'ABB_IRC5') -> tuple:
      """Apply touch sensing decoration to a motion command.

      Returns (cmd, was_search):
      - was_search=True: cmd was replaced with Search_1D (caller should not decorate further)
      - was_search=False: cmd unchanged (caller should continue with its own decoration)
      """
      # Defensive: ensure _is_frame3p_touch exists (E2 may cache old plugin instances)
      if not hasattr(self, '_is_frame3p_touch'):
         self._is_frame3p_touch = False

      # If TouchPointStartAppEvent was seen for this motion, capture its point ref
      # but keep emitting the normal motion command.
      if self._record_via_from_this_motion:
         try:
            self._via_point_ref = downloader.shared.current_point_ref
            # For Explicit mode, also store the robtarget string
            if downloader.ABBTargetOutputStyle == "Explicit":
               self._via_point_robtarget = downloader.ExplixitDataStorage[0] if downloader.ExplixitDataStorage[0] else None
         except (AttributeError, IndexError):
            self._via_point_ref = None
            self._via_point_robtarget = None
         self._record_via_from_this_motion = False

      # Process touch sensing Search_1D
      if self._pending_search:
         operator.GetLogOperator().LogInfo(f"TouchSensing: _pending_search is True, attempting Search_1D generation")
         try:
            # Search_1D is only valid for linear moves.
            is_linear = motion.IsLinearMotion()
            operator.GetLogOperator().LogInfo(f"TouchSensing: motion.IsLinearMotion() = {is_linear}")
            if is_linear:
               # Generate shift variable name based on TSConnectionType
               shift_var = "pose1"  # default fallback

               if self._ts_connection_type == "Frame3pConnect":
                  # Frame3pConnect: tid_pt<FramePt>_mea<N> (reusable across TouchIds)
                  key = (self._frame3p_touch_id, self._frame3p_pt)
                  measure_id = self._frame3p_mea_counters.get(key, 0) + 1
                  self._frame3p_mea_counters[key] = measure_id
                  shift_var = f"tid_pt{self._frame3p_pt}_mea{measure_id}"
               elif self._ts_connection_type in ("OperationConnect", "StartEndConnect", "ShortestDistanceConnect"):
                  # Displacement modes: tid_mea<N> (reusable across TouchIds)
                  # On last touch, write directly to result variable peDisp<TouchId>
                  measure_id = self._displacement_mea_counters.get(self._displacement_touch_id, 0) + 1
                  self._displacement_mea_counters[self._displacement_touch_id] = measure_id

                  # Get Touch_Cntr for this TouchId
                  touch_cntr = self._displacement_touch_cntr.get(self._displacement_touch_id, 0)

                  # Determine if this is the last touch
                  # Use Touch_Cntr if available, otherwise fallback to measure_id == 3
                  is_last_touch = (measure_id == touch_cntr) if touch_cntr > 0 else (measure_id == 3)

                  operator.GetLogOperator().LogDebug(f"Displacement mode: TouchId={self._displacement_touch_id}, measure_id={measure_id}, Touch_Cntr={touch_cntr}, is_last={is_last_touch}")

                  if is_last_touch:
                     # Last touch: write directly to peDisp<TouchId>
                     shift_var = f"peDisp{self._displacement_touch_id}"
                  else:
                     # Intermediate touch: write to tid_mea<N>
                     shift_var = f"tid_mea{measure_id}"
               else:
                  # Standard touch sensing (legacy): pose<N>
                  shift_base = downloader._defaults_get_str(['naming', 'touch_shift_base'], 'pose')
                  touch_id = -1
                  if downloader._current_operation is not None:
                     touch_id = downloader._safe_get_operation_int(downloader._current_operation, 'TouchID', -1)
                  if touch_id < 0:
                     downloader._abb_touch_fallback_counter += 1
                     touch_id = downloader._abb_touch_fallback_counter
                  shift_var = "%s%d" % (shift_base, touch_id)

               # We need a via-point and a touch-point.
               # In Explicit mode, use inline robtargets; otherwise use point references
               if downloader.ABBTargetOutputStyle == "Explicit":
                  # Store current touch point robtarget
                  self._touch_point_robtarget = downloader.ExplixitDataStorage[0] if downloader.ExplixitDataStorage[0] else None
                  via_point = self._via_point_robtarget
                  touch_point = self._touch_point_robtarget
               else:
                  via_point = self._via_point_ref or downloader.shared.last_point_ref
                  touch_point = downloader.shared.current_point_ref

               if (via_point is not None) and (touch_point is not None):
                  operator.GetLogOperator().LogInfo(f"TouchSensing: Generating Search_1D with via={via_point is not None}, touch={touch_point is not None}")
                  speed_token = downloader._abb_get_speed_token_for_motion(motion)
                  tool_token = downloader._abb_get_tool_token()

                  # Work object: Use station wobj (same priority system as other motions)
                  wobj_token = downloader._abb_get_wobj_token()

                  indent = ''
                  try:
                     if cmd:
                        indent = cmd[: len(cmd) - len(cmd.lstrip())]
                  except Exception:
                     indent = ''
                  if not indent:
                     indent = '    '

                  search_cmd = "%sSearch_1D %s,%s,%s,%s,%s%s" % (indent, shift_var, via_point, touch_point, speed_token, tool_token, wobj_token)

                  # Add PrePDisp for 2nd and 3rd measurements
                  if self._ts_connection_type == "Frame3pConnect":
                     # Frame3pConnect: PrePDisp per FramePt (reusable variable names)
                     key = (self._frame3p_touch_id, self._frame3p_pt)
                     measure_id = self._frame3p_mea_counters.get(key, 1)
                     if measure_id == 2:
                        predisp_var = f"tid_pt{self._frame3p_pt}_mea1"
                        search_cmd += f"\\PrePDisp:={predisp_var}"
                     elif measure_id == 3:
                        mea1 = f"tid_pt{self._frame3p_pt}_mea1"
                        mea2 = f"tid_pt{self._frame3p_pt}_mea2"
                        search_cmd += f"\\PrePDisp:=PoseAdd({mea1},{mea2})"
                  elif self._ts_connection_type in ("OperationConnect", "StartEndConnect", "ShortestDistanceConnect"):
                     # Displacement modes: PrePDisp uses reusable variable names
                     measure_id = self._displacement_mea_counters.get(self._displacement_touch_id, 1)
                     if measure_id == 2:
                        predisp_var = "tid_mea1"
                        search_cmd += f"\\PrePDisp:={predisp_var}"
                     elif measure_id == 3:
                        mea1 = "tid_mea1"
                        mea2 = "tid_mea2"
                        search_cmd += f"\\PrePDisp:=PoseAdd({mea1},{mea2})"

                  search_cmd += ";"

                  self._pending_search = False
                  self._via_point_ref = None
                  operator.GetLogOperator().LogInfo(f"TouchSensing: Search_1D generated successfully")
                  return search_cmd, True
               else:
                  operator.GetLogOperator().LogInfo(f"TouchSensing: via_point or touch_point is None (via={via_point is not None}, touch={touch_point is not None})")

            self._pending_search = False
            self._via_point_ref = None
         except Exception as e:
            operator.GetLogOperator().LogInfo(f"TouchSensing: Exception in Search_1D generation: {e}")
            self._pending_search = False
            self._via_point_ref = None

      return cmd, False


class _ABBArcWeldingPlugin(_ABBPluginBase, _ABBTouchSensingMixin):
   """Arc Welding plugin with integrated Touch Sensing:
   - ArcOnEvent / ArcOffEvent are expected as *events-after* on the same motion.
   - Uses integer attributes on the operation: 'Seamdata Number' and 'Welddata Number'.
   - Weaving / tracking are optional and included when corresponding names are resolved.
   - Touch Sensing via _ABBTouchSensingMixin: Search_1D, Frame3pConnect support
   """

   EVT_ARC_ON = 'ArcOnEvent'
   EVT_ARC_OFF = 'ArcOffEvent'

   @property
   def read_ahead_events(self):
      return {
         self.EVT_ARC_ON, self.EVT_ARC_OFF,
         'SeamTrackingLeadInEvent', 'SeamTrackingEvent', 'SeamTrackingOffEvent', 'SeamTrackOn', 'SeamTrackOff',
      } | self.TOUCH_READ_AHEAD_EVENTS

   def __init__(self) -> None:
      # Touch sensing state (from _ABBTouchSensingMixin)
      self._init_touch_state()

      # Arc welding state
      self._arc_on = False
      self._arc_start_this_motion = False
      self._arc_end_this_motion = False
      self._track_on = False
      self._weave_on = False

      self._seamdata_name = 'seam1'
      self._welddata_name = 'weld1'
      self._weavedata_name = None  # type: Optional[str]
      self._trackdata_name = None  # type: Optional[str]

   def operation_start(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      # Check technology type — ArcWelding plugin only active when tech type is ArcWelding (or unset)
      tech_type = downloader._safe_get_operation_enum(operation, 'MACHINING_TECH_TYPE', 'ArcWelding')
      self._active = (tech_type != 'Machining')
      if not self._active:
         return

      # Use Operation-level DATA_NAME attributes for variable naming
      # This allows users to select specific data instances from the data management system
      try:
         self._seamdata_name = downloader._safe_get_operation_str(operation, 'SEAM_DATA_NAME', 'seam1')
         if not self._seamdata_name or not self._seamdata_name.strip():
            # Fallback to legacy index-based naming if name not set
            seam_num = downloader._safe_get_operation_int(operation, 'Seamdata Number', 1)
            self._seamdata_name = f"seam{seam_num}"
         # Track usage for declarations
         downloader._track_data_usage('seamdata', self._seamdata_name)
      except Exception:
         self._seamdata_name = 'seam1'
      
      try:
         self._welddata_name = downloader._safe_get_operation_str(operation, 'WELD_DATA_NAME', 'weld1')
         if not self._welddata_name or not self._welddata_name.strip():
            # Fallback to legacy index-based naming if name not set
            weld_num = downloader._safe_get_operation_int(operation, 'Welddata Number', 1)
            self._welddata_name = f"weld{weld_num}"
         # Track usage for declarations
         downloader._track_data_usage('welddata', self._welddata_name)
      except Exception:
         self._welddata_name = 'weld1'

      # Read operation-level USE_WEAVING flag
      try:
         self._use_weaving = operation.GetBoolAttribute('USE_WEAVING', True).GetValue()
      except (AttributeError, ValueError):
         self._use_weaving = False

      # Weavedata - only if operation-level USE_WEAVING enabled
      self._weavedata_name = None
      if self._use_weaving:
         try:
            weave_name = downloader._safe_get_operation_str(operation, 'WEAVE_DATA_NAME', '')
            if weave_name and weave_name.strip():
               self._weavedata_name = weave_name.strip()
               self._weave_on = True  # Enable weave parameter in Arc commands
            else:
               # Fallback to legacy index-based naming
               weave_num = downloader._safe_get_operation_int(operation, 'Weavedata Number', -1)
               if weave_num >= 0:
                  self._weavedata_name = f"weave{weave_num}"
                  self._weave_on = True  # Enable weave parameter in Arc commands
               else:
                  self._weave_on = False
            if self._weavedata_name:
               downloader._track_data_usage('weavedata', self._weavedata_name)
         except Exception:
            self._weave_on = False
            pass
      else:
         self._weave_on = False

      # Read operation-level USE_TRACKING flag
      try:
         self._use_tracking = operation.GetBoolAttribute('USE_TRACKING', True).GetValue()
      except (AttributeError, ValueError):
         self._use_tracking = False

      # Trackdata - only if operation-level USE_TRACKING enabled
      self._trackdata_name = None
      if self._use_tracking:
         try:
            track_name = downloader._safe_get_operation_str(operation, 'TRACK_DATA_NAME', '')
            if track_name and track_name.strip():
               self._trackdata_name = track_name.strip()
               # Track on/off is typically controlled by SeamTracking events,
               # but if a trackdata name is explicitly set, enable it by default
               if not self._track_on:
                  self._track_on = True
            else:
               # Fallback to legacy index-based naming
               track_num = downloader._safe_get_operation_int(operation, 'Trackdata Number', -1)
               if track_num >= 0:
                  self._trackdata_name = f"track{track_num}"
                  if not self._track_on:
                     self._track_on = True
            if self._trackdata_name:
               downloader._track_data_usage('trackdata', self._trackdata_name)
         except Exception:
            pass
      else:
         # USE_TRACKING disabled for this operation - force track off
         self._track_on = False

      self._arc_start_this_motion = False
      self._arc_end_this_motion = False

   def handle_read_ahead_event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      if not self._active:
         return
      # Touch sensing events (delegated to mixin)
      if self._touch_handle_read_ahead_event(operator, motion, event, downloader):
         return

      # Arc welding events
      name = event.GetName()
      if name == self.EVT_ARC_ON:
         self._arc_on = True
         self._arc_start_this_motion = True
         return
      if name == self.EVT_ARC_OFF:
         self._arc_end_this_motion = True
         return

      if name in ('SeamTrackingLeadInEvent', 'SeamTrackingEvent', 'SeamTrackOn'):
         self._track_on = True
         return
      if name in ('SeamTrackingOffEvent', 'SeamTrackOff'):
         self._track_on = False
         return

   def decorate_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, cmd: str, downloader: 'ABB_IRC5') -> str:
      if not self._active:
         return cmd
      # If command is already suppressed (e.g., by another plugin), don't process it
      if not cmd or not cmd.strip():
         return cmd

      # Touch sensing decoration first (may replace cmd with Search_1D)
      cmd, was_search = self._touch_decorate_motion_command(operator, motion, cmd, downloader)
      if was_search:
         return cmd

      # Arc welding decoration (ArcL/ArcC commands)
      # Only decorate linear/circular motions.
      if not (motion.IsLinearMotion() or motion.IsCircularMotion()):
         self._arc_start_this_motion = False
         self._arc_end_this_motion = False
         return cmd

      if not (self._arc_on or self._arc_end_this_motion or self._arc_start_this_motion):
         self._arc_start_this_motion = False
         self._arc_end_this_motion = False
         return cmd

      if cmd.strip().startswith('MoveL'):
         base = 'ArcL'
         if self._arc_start_this_motion:
            base = 'ArcLStart'
         elif self._arc_end_this_motion:
            base = 'ArcLEnd'
         cmd = cmd.replace('MoveL', base, 1)

      elif cmd.strip().startswith('MoveC'):
         base = 'ArcC'
         if self._arc_start_this_motion:
            base = 'ArcCStart'
         elif self._arc_end_this_motion:
            base = 'ArcCEnd'
         cmd = cmd.replace('MoveC', base, 1)

      options = []  # type: List[str]
      # ArcWare expects: ArcLStart p, v, seamdata, welddata, z, tool\Wobj:=wobj ... [\Weave:=...] [\Track:=...]
      # Existing prototype does not yet insert seam/weld operands; we append them after the speed operand if possible.
      options.extend([self._seamdata_name, self._welddata_name])

      # Append weave/track based on operation-level USE_* flags and data name
      # Track must be appended AFTER \WObj:=, so handle it separately
      track_param = None
      if self._use_weaving and self._weavedata_name is not None and self._weave_on:
         options.append("\\Weave:=%s" % self._weavedata_name)
      if self._use_tracking and self._trackdata_name is not None and self._track_on:
         track_param = "\\Track:=%s" % self._trackdata_name

      cmd = downloader._abb_try_inject_arcware_operands(cmd, options)
      
      # Append Track parameter at the end (after \WObj:=)
      if track_param:
         cmd = cmd.rstrip(';') + track_param + ';'

      if self._arc_end_this_motion:
         self._arc_on = False

      self._arc_start_this_motion = False
      self._arc_end_this_motion = False
      return cmd


class _ABBMachiningPlugin(_ABBPluginBase, _ABBTouchSensingMixin):
   """Machining plugin for RobotWare Machining (Plasma / Grinding / Sanding).

   Converts Move* commands into MachL / MachJ / MachC with:
   - prepended offset (identity pose) + RelEuler (MachiningPose variable)
   - appended MachineProcess variable as last argument

   Reuses Touch Sensing via _ABBTouchSensingMixin for Search_1D / Frame3pConnect.

   Events:
   - ArcOnEvent / ArcOffEvent are reused as process on/off markers.

   Data types:
   - MachineProcess: 5-field record [EngageDistance, TiltAngle, LeadAngle, PreRoutine, PostRoutine]
   - MachiningPose:  6-field record [x, y, z, Rx, Ry, Rz]
   """

   # Reuse existing E2 events as process on/off markers
   EVT_PROCESS_ON = 'ArcOnEvent'
   EVT_PROCESS_OFF = 'ArcOffEvent'

   # Default inline offset value (identity pose)
   _IDENTITY_OFFSET = '[[0,0,0],[1,0,0,0]]'

   @property
   def read_ahead_events(self):
      return {
         self.EVT_PROCESS_ON, self.EVT_PROCESS_OFF,
      } | self.TOUCH_READ_AHEAD_EVENTS

   @property
   def name(self) -> str:
      return 'Machining'

   def __init__(self) -> None:
      # Touch sensing state (from _ABBTouchSensingMixin)
      self._init_touch_state()

      # Process state
      self._process_on = False
      self._process_start_this_motion = False
      self._process_end_this_motion = False

      # Data names (resolved at operation_start)
      self._machprocess_name = 'mp_default'   # MachineProcess variable name
      self._machpose_name = 'relDefault'       # MachiningPose (RelEuler) variable name
      self._approach_type = 'MachJ'            # "MachJ" or "MoveJ"

   def operation_start(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation, downloader: 'ABB_IRC5') -> None:
      """Read machining data names and approach/depart preference from operation attributes."""
      # Check technology type — Machining plugin only active when tech type is Machining
      tech_type = downloader._safe_get_operation_enum(operation, 'MACHINING_TECH_TYPE', 'ArcWelding')
      self._active = (tech_type == 'Machining')
      if not self._active:
         return

      # MachineProcess name
      try:
         name = downloader._safe_get_operation_str(operation, 'MACH_PROCESS_NAME', 'mp_default')
         if name and name.strip():
            self._machprocess_name = name.strip()
         else:
            self._machprocess_name = 'mp_default'
         downloader._track_data_usage('machineprocess', self._machprocess_name)
      except Exception:
         self._machprocess_name = 'mp_default'

      # MachiningPose (RelEuler) name
      try:
         name = downloader._safe_get_operation_str(operation, 'MACH_POSE_NAME', 'relDefault')
         if name and name.strip():
            self._machpose_name = name.strip()
         else:
            self._machpose_name = 'relDefault'
         downloader._track_data_usage('machiningpose', self._machpose_name)
      except Exception:
         self._machpose_name = 'relDefault'

      # Approach/depart type
      try:
         self._approach_type = downloader._safe_get_operation_enum(operation, 'MACH_APPROACH_TYPE', 'MachJ')
         if self._approach_type not in ('MachJ', 'MoveJ'):
            self._approach_type = 'MachJ'
      except Exception:
         self._approach_type = 'MachJ'

      # Reset process flags
      self._process_start_this_motion = False
      self._process_end_this_motion = False

   def handle_read_ahead_event(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, downloader: 'ABB_IRC5') -> None:
      if not self._active:
         return
      # Touch sensing events (delegated to mixin)
      if self._touch_handle_read_ahead_event(operator, motion, event, downloader):
         return

      # Process on/off events
      name = event.GetName()
      if name == self.EVT_PROCESS_ON:
         self._process_on = True
         self._process_start_this_motion = True
         return
      if name == self.EVT_PROCESS_OFF:
         self._process_end_this_motion = True
         return

   def decorate_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, cmd: str, downloader: 'ABB_IRC5') -> str:
      if not self._active:
         return cmd
      if not cmd or not cmd.strip():
         return cmd

      # Touch sensing decoration first (may replace cmd with Search_1D)
      cmd, was_search = self._touch_decorate_motion_command(operator, motion, cmd, downloader)
      if was_search:
         return cmd

      # Determine whether to apply Mach* decoration
      should_decorate = False
      if self._process_on or self._process_start_this_motion or self._process_end_this_motion:
         # Inside process block: always decorate
         should_decorate = True
      elif self._approach_type == 'MachJ':
         # Outside process: approach_type MachJ → decorate all motions
         should_decorate = True
      # else: approach_type == "MoveJ" and outside process → leave as Move*

      if should_decorate:
         cmd = self._mach_decorate_command(cmd)

      # Update process state
      if self._process_end_this_motion:
         self._process_on = False
      self._process_start_this_motion = False
      self._process_end_this_motion = False
      return cmd

   def _mach_decorate_command(self, cmd: str) -> str:
      """Transform a Move* command into a Mach* command.

      MoveL P,v,z,tool\\WObj:=wobj;  →  MachL offset,releuler,P,v,z,tool\\WObj:=wobj,process;
      MoveJ P,v,z,tool\\WObj:=wobj;  →  MachJ offset,releuler,P,v,z,tool\\WObj:=wobj,process;
      MoveC V,P,v,z,tool\\WObj:=wobj; → MachC offset,releuler,V,P,v,z,tool\\WObj:=wobj,process;
      MoveAbsJ → left unchanged (no MachAbsJ instruction)
      """
      stripped = cmd.strip()
      replacements = {'MoveL': 'MachL', 'MoveJ': 'MachJ', 'MoveC': 'MachC'}

      mach_instr = None
      move_instr = None
      for move, mach in replacements.items():
         if stripped.startswith(move + ' ') or stripped.startswith(move + '\t'):
            move_instr = move
            mach_instr = mach
            break

      if mach_instr is None:
         # MoveAbsJ or unknown — leave as-is
         return cmd

      indent = cmd[:len(cmd) - len(cmd.lstrip())]
      rest = stripped[len(move_instr):].lstrip()
      rest = rest.rstrip(';')

      # Build: MachX offset,releuler,<original args>,process;
      return "%s%s %s,%s,%s,%s;" % (
         indent, mach_instr, self._IDENTITY_OFFSET, self._machpose_name, rest, self._machprocess_name
      )


#################### CONSTANTS ####################
# Name of the downloader class
DOWNLOAD_CLASS_NAME = "ABB_IRC5"

class ABB_IRC5(Downloader):
   """Downloader for ABB robots in RAPID language.
   Inherits from the Downloader class and its task is to generate
   a .mod file with correctly formatted RAPID code.
   """

   # Output file extension
   FILE_EXTENSION = '.MOD'

   # Logical value definitions for signals in ABB
   ABB_TRUE = 'TRUE'
   ABB_FALSE = 'FALSE'

#################### BASIC FUNCTIONS ####################

   def __init__(self) -> None:
      """Initialize ABB IRC5 downloader.
      
      Sets up output sections, plugins, and state management.
      Detailed configuration loaded later in Initialize().
      """
      super().__init__()
      self.FileUtil = FileUtility()
      
      # Initialize core components
      self._init_output_sections()
      self._init_legacy_attributes()
      self._init_plugins()
      self._init_state()
   
   def _init_output_sections(self) -> None:
      """Initialize RAPID output section arrays."""
      self.OutputFilePath = ''
      self.ProgramName = ''
      self.Header = []
      self.DataHeader = []
      self.Data = []
      self.SourceHeader = []
      self.Source = []
      self.Footer = []
   
   def _init_legacy_attributes(self) -> None:
      """Initialize legacy attributes (kept for backward compatibility).
      
      These are overridden by JSON defaults in Initialize().
      """
      # Base/tool frame indices
      self.CurrentBaseFrameIndex = -1
      self.baseFrameName = ""
      self.BaseFrameMinIndex = 0
      self.BaseFrameMaxIndex = 9
      self.CurrentToolFrameIndex = -1
      self.ToolFrameName = ""
      self.ToolFrameMinIndex = 0
      self.ToolFrameMaxIndex = 10
      
      # Speed and accuracy
      self.CurrentPtpFeedrate = 1000
      self.CurrentLinFeedrate = 1000
      self.DataSectionSpeedProfiles = []
      self.CurrentPtpAccuracy = 0
      self.CurrentLinAccuracy = 0
      self.CurrentAccuracyActive = False
      self.DataSectionAccuracyProfiles = []
      self.CurrentPtpAcceleration = 100
      self.CurrentLinAcceleration = 100
      
      self.MaxCharComments = 16
      self.PointCounter = 0
      self.SourceLineCounter = 0
      self.Language = ""
      
      # Output control
      self.ABBTargetOutputStyle = "Explicit"
      self.ExplixitDataStorage = ["", ""]
      self.ABBProfilesOutput = False
      
      # Arc welding (legacy - now handled by plugin)
      self.ArcweldingActive = False
      self.IsWeldingStartPoint = False
      self.IsWeldingEndPoint = False
      
      # Module/proc naming (overridden by JSON defaults)
      self.ModuleName = 'MainProgram'
      self.ProcName = 'MainProc'
      self.ActUnitName = 'TISCH_1'
      self.CurrentSeamDataNumber = -1
      self.CurrentWeldDataNumber = -1
      
      # Subprogram control (legacy)
      self.AvoidOutputOfExceptionalSubprograms = True
      self.ExceptionalSubprograms = ['FreiVorTisch']
      self.AvoidExceptionalSubprogramsCalls = True
      self.ExceptionalSubprogramsCalls = ['FreiVorTisch']
      self.DontWriteAnySubprogram = False
   
   def _init_plugins(self) -> None:
      """Initialize plugin manager (before defaults loaded)."""
      self._plugins = _ABBPluginManager()
   
   def _init_state(self) -> None:
      """Initialize downloader state variables."""
      # Shared state (accessed by plugins)
      self.shared = _ABBSharedState()
      
      # Module/program state
      self._abb_module_open = False
      self._abb_touch_fallback_counter = 0
      self._abb_ref_motion_counter = 0
      
      # Point reference tracking
      self._abb_motion_point_ref_by_id = {}  # type: Dict[int, str]
      self._abb_motion_via_point_ref_by_id = {}  # type: Dict[int, str]
      
      # Configuration (loaded in Initialize)
      self._defaults = {}  # type: Dict[str, Any]
      self._abb_use_e2_position_names = True
      
      # Current operation tracking
      self._current_operation = None  # type: Optional[DULPythonOperation]
      self._current_operation_group = None  # type: Optional[DULPythonOperationGroup]
      
      # Frame3P touch sensing state
      self._frame3p_refpoints = {}  # type: Dict[tuple, Dict[str, Any]]
      self._frame3p_measurements = {}  # type: Dict[tuple, List[str]]
      self._frame3p_active_touchid = None  # type: Optional[int]
      self._frame3p_touch_data = {}  # type: Dict[int, Dict[str, Any]]
      self._frame3p_measurement_counter = {}  # type: Dict[tuple, int]
      self._frame3p_approach_point_ref = None
      self._frame3p_approach_motion = None
      
      # Station management
      self._station_active_index = None  # type: Optional[int]
      self._station_setup_proc = None  # type: Optional[str]
      self._station_active_groups = set()  # type: Set[int]
      
      # External axis mapping
      self._extax_map = {}  # type: Dict[Tuple[int, int], int]
      self._rail_group_index = None  # type: Optional[int]
      self._rail_adjustment = 0.0  # type: float
      
      # Data management
      self._data_schemas = {}  # type: Dict[str, Any]
      self._data_instances = {}  # type: Dict[str, Any]
      self._data_used_names = {}  # type: Dict[str, Set[str]]
      self._data_use_weaving = False
      self._data_use_tracking = False
      self._data_global_data = False
      self._data_output_module = False
      self._data_module_name = "ABB_Data"

   def HandleSubprogramInLoop(self):
      return False
   
   def OutputSubprogramInSeparateFiles(self):
      # User preference: subprograms in same module
      return False

   def Initialize(self, operator: DULPythonDownloadOperator):
      """Initialization of the Translator. Called only once for the entire download."""
      self.Language = operator.GetCurrentLanguage()

      controller = operator.GetController()

      defaults_file = ''
      try:
         defaults_file = controller.GetString('CENOlpABBDefaultsFile', False)
      except Exception:
         defaults_file = ''
      if not defaults_file:
         defaults_file = 'ABB_IRC5_DL.json'

      self._defaults = self._load_defaults_json(operator, defaults_file)

      # Build external axis mappings for station-based filtering
      # NOTE: Joint indices repeat across mechanism groups, so use (group_index, joint_index) as key
      # E1-E6 positions are assigned based on joint_index (Joint 1 → E1, Joint 5 → E5)
      logger = operator.GetLogOperator()
      logger.LogInfo("ABB Initialize: Building joint mappings...")
      try:
         connected_joints = controller.GetConnectedJoints()
         
         # Sort by (group_index, joint_index) for deterministic E1-E6 assignment
         sorted_joints = sorted(connected_joints, key=lambda j: (j.GetJointGroupIndex(), j.GetJointIndex()))
         
         logger.LogInfo(f"ABB Initialize: Found {len(sorted_joints)} connected joints")
         
         for joint in sorted_joints:
            joint_index = joint.GetJointIndex()
            group_index = joint.GetJointGroupIndex()
            is_external = joint.IsExternal()
            
            if is_external:
               # Map joint_index directly to E1-E6 position
               # Joint index 1 → E1 (position 0), Joint index 6 → E6 (position 5)
               extax_position = joint_index - 1  # Convert 1-based to 0-based
               
               if 0 <= extax_position < 6:
                  key = (group_index, joint_index)
                  self._extax_map[key] = extax_position
                  logger.LogInfo(f"ABB External Axis: Group {group_index}, Joint {joint_index} → E{joint_index}")
               else:
                  logger.LogWarn(f"ABB External Axis: Group {group_index}, Joint {joint_index} out of E1-E6 range")
            else:
               logger.LogInfo(f"ABB Robot Axis: Group {group_index}, Joint {joint_index}")
         
         logger.LogInfo(f"ABB Initialize: Mapped {len(self._extax_map)} external axes")
      except Exception as e:
         logger.LogError(f"ABB: Could not build joint mappings: {e}")
         import traceback
         logger.LogError(traceback.format_exc())
      except Exception as e:
         logger.LogError(f"ABB: Could not build joint mappings: {e}")
         import traceback
         logger.LogError(traceback.format_exc())

      self.ModuleName = self._defaults_get_str(['output', 'module_name'], self.ModuleName)
      self.ActUnitName = self._defaults_get_str(['output', 'act_unit_name'], self.ActUnitName)
      self.ProcName = self._defaults_get_str(['output', 'default_proc_name'], self.ProcName)
      self.ABBTargetOutputStyle = self._defaults_get_str(['output', 'target_output_type'], 'Implicit')

      # When enabled, use E2 position names (e.g. P001, P014) for emitted RAPID
      # robtarget names and Move* command arguments.
      try:
         self._abb_use_e2_position_names = bool(self._defaults_get_bool(['output', 'use_e2_position_names'], True))
      except Exception:
         self._abb_use_e2_position_names = True

      enabled_list = self._defaults_get_list(['plugins', 'enabled'], [])
      enabled_set = set([str(s).strip().lower() for s in enabled_list if str(s).strip()])
      
      # Store for later use
      self._enabled_plugin_names = enabled_list
      self._defaults_file = defaults_file

      plugins = []  # type: List[_ABBPluginBase]
      # Note: TouchSensing is integrated into ArcWelding plugin
      if 'arcwelding' in enabled_set or 'touchsensing' in enabled_set:
         plugins.append(_ABBArcWeldingPlugin())
      if 'machining' in enabled_set:
         plugins.append(_ABBMachiningPlugin())

      self._plugins.set_plugins(plugins)
      self._plugins.initialize(operator, self)

   def _defaults_get_bool(self, path: List[str], default: bool) -> bool:
      node = self._defaults
      for p in path:
         if isinstance(node, dict) and p in node:
            node = node[p]
         else:
            return default
      if isinstance(node, bool):
         return node
      if isinstance(node, (int, float)):
         return bool(node)
      if isinstance(node, str):
         return node.strip().lower() in ('1', 'true', 'yes', 'on')
      return default

   def _defaults_get_int(self, path: List[str], default: int) -> int:
      node = self._defaults
      for p in path:
         if isinstance(node, dict) and p in node:
            node = node[p]
         else:
            return default
      if isinstance(node, int):
         return node
      if isinstance(node, float):
         return int(node)
      if isinstance(node, str):
         try:
            return int(node)
         except ValueError:
            return default
      return default

   def _normalize_missing_int(self, value: int, default: int) -> int:
      # E2 sometimes returns a sentinel for "unset" int attributes.
      if value == -2147483648:
         return default
      return value

   def LoadDataManagement(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Load data management schemas and instances.
      
      Called once at program start to load seamdata, welddata, weavedata, trackdata
      schemas and instances from TechTabs/Data/<ControllerName>/.
      
      Note: USE_WEAVING and USE_TRACKING are now operation-level attributes.
      We scan all operations to determine if any use weaving/tracking.
      """
      if dm_utils is None:
         return

      try:
         controller = operator.GetController()
         controllerName = controller.GetName()
         logger = operator.GetLogOperator()
         
         # Scan all operations to check if ANY operation uses weaving or tracking
         any_use_weaving = False
         any_use_tracking = False
         
         operationGroups = program.GetOperationGroups()
         for opGroup in operationGroups:
            operations = opGroup.GetOperations()
            for operation in operations:
               try:
                  use_weaving = operation.GetBoolAttribute('USE_WEAVING', True).GetValue()
                  if use_weaving:
                     any_use_weaving = True
               except (AttributeError, ValueError):
                  pass
               
               try:
                  use_tracking = operation.GetBoolAttribute('USE_TRACKING', True).GetValue()
                  if use_tracking:
                     any_use_tracking = True
               except (AttributeError, ValueError):
                  pass
         
         self._data_use_weaving = any_use_weaving
         self._data_use_tracking = any_use_tracking
         logger.LogInfo(f"Data management: USE_WEAVING={any_use_weaving}, USE_TRACKING={any_use_tracking} (scanned operations)")
         
         # Load GLOBAL_DATA and module settings from program attributes
         try:
            self._data_global_data = program.GetBoolAttribute('GLOBAL_DATA', True).GetValue()
         except (AttributeError, ValueError):
            self._data_global_data = False
         
         try:
            self._data_output_module = program.GetBoolAttribute('OUTPUT_DATA_MODULE', True).GetValue()
         except (AttributeError, ValueError):
            self._data_output_module = False
         
         try:
            moduleName = program.GetStringAttribute('DATA_MODULE_NAME', True).GetValue()
            if moduleName and moduleName.strip():
               self._data_module_name = moduleName.strip()
         except (AttributeError, ValueError):
            pass
         
         # Load schemas and instances for each data type
         dataTypes = ['seamdata', 'welddata']
         if self._data_use_weaving:
            dataTypes.append('weavedata')
         if self._data_use_tracking:
            dataTypes.append('trackdata')

         # Add machining data types if Machining plugin is enabled
         enabled_lower = set(str(s).strip().lower() for s in getattr(self, '_enabled_plugin_names', []) if str(s).strip())
         if 'machining' in enabled_lower:
            dataTypes.extend(['machineprocess', 'machiningpose'])
         
         for dataType in dataTypes:
            schema = dm_utils.load_schema(controllerName, dataType)
            instances = dm_utils.load_instances(controllerName, dataType)
            
            if schema:
               self._data_schemas[dataType] = schema
            if instances:
               self._data_instances[dataType] = instances
            
            # Initialize usage tracking (now by name, not index)
            self._data_used_names[dataType] = set()
      
      except Exception as e:
         logger = operator.GetLogOperator()
         logger.LogInfo(f"Failed to load data management: {str(e)}")

   def _track_data_usage(self, dataType: str, name: str):
      """Track that a data instance is being used (called from operation_start callbacks).
      
      Args:
          dataType: 'seamdata', 'welddata', 'weavedata', or 'trackdata'
          name: Instance name (e.g., 'sd_linear_50')
      """
      if not hasattr(self, '_data_used_names'):
         self._data_used_names = {}
      
      if dataType not in self._data_used_names:
         self._data_used_names[dataType] = set()
      
      if name and name.strip():
         self._data_used_names[dataType].add(name.strip())

   def CollectUsedDataNames(self, operator: DULPythonDownloadOperator):
      """Scan all operations to collect used data instance names.
      
      Reads *_DATA_NAME attributes from operations to determine which
      data instances are referenced and need declarations.
      """
      try:
         controller = operator.GetController()
         activeProgram = controller.GetActiveProgram()
         logger = operator.GetLogOperator()
         
         # Scan all operations - iterate through OperationGroups first
         operationGroups = activeProgram.GetOperationGroups()
         for opGroup in operationGroups:
            operations = opGroup.GetOperations()
            for operation in operations:
               # Check each data type
               for dataType in ['SEAM', 'WELD', 'WEAVE', 'TRACK']:
                  # Skip WEAVE/TRACK data if operation doesn't use it
                  if dataType == 'WEAVE':
                     try:
                        use_weaving = operation.GetBoolAttribute('USE_WEAVING', True).GetValue()
                        if not use_weaving:
                           continue
                     except (AttributeError, ValueError):
                        continue
                  elif dataType == 'TRACK':
                     try:
                        use_tracking = operation.GetBoolAttribute('USE_TRACKING', True).GetValue()
                        if not use_tracking:
                           continue
                     except (AttributeError, ValueError):
                        continue
                  
                  attrName = f"{dataType}_DATA_NAME"
                  try:
                     # Use GetStringAttribute for String attributes, not GetLiteralAttribute
                     name = operation.GetStringAttribute(attrName, True)
                     if name and name.strip():
                        fullType = dataType.lower() + 'data'
                        if fullType in self._data_used_names:
                           self._data_used_names[fullType].add(name.strip())
                           logger.LogDebug(f"Collected {fullType}: {name.strip()}")
                  except (AttributeError, ValueError):
                     pass

               # Collect machining data names
               for mach_attr, mach_type in [('MACH_PROCESS_NAME', 'machineprocess'), ('MACH_POSE_NAME', 'machiningpose')]:
                  try:
                     name = operation.GetStringAttribute(mach_attr, True)
                     if name and name.strip():
                        if mach_type in self._data_used_names:
                           self._data_used_names[mach_type].add(name.strip())
                           logger.LogDebug(f"Collected {mach_type}: {name.strip()}")
                  except (AttributeError, ValueError):
                     pass
      
      except Exception as e:
         logger = operator.GetLogOperator()
         logger.LogInfo(f"Failed to collect data names: {str(e)}")

   def FormatDataDeclaration(self, dataType: str, instance: Dict[str, Any]) -> str:
      """Format RAPID declaration from schema and instance.
      
      Args:
         dataType: Data type ("seamdata", "welddata", "weavedata", "trackdata")
         instance: Instance dict
      
      Returns:
         str: RAPID declaration line
      """
      if dm_utils is None:
         return ""

      try:
         schema = self._data_schemas.get(dataType)
         if not schema:
            return ""
         
         return dm_utils.format_rapid_declaration(schema, instance)
      
      except Exception:
         return ""

   def OutputDataDeclarations(self, operator: DULPythonDownloadOperator):
      """Output RAPID declarations for used data instances.
      
      Generates declarations in Data section based on:
      - Collected usage names from Operations
      - USE_WEAVING / USE_TRACKING flags
      - GLOBAL_DATA flag (LOCAL PERS vs TASK PERS scope)
      """
      logger = operator.GetLogOperator()
      
      try:
         logger.LogInfo("OutputDataDeclarations: Starting")
         
         # Skip if GLOBAL_DATA is True (declarations output in separate module)
         if self._data_global_data:
            logger.LogInfo("GLOBAL_DATA is True - skipping local data declarations")
            return
         
         # GLOBAL_DATA is False: use LOCAL PERS scope
         scope = "LOCAL PERS"
         logger.LogInfo(f"Data scope: {scope}")
         
         # Output declarations for each data type
         dataTypes = ['seamdata', 'welddata']
         if self._data_use_weaving:
            dataTypes.append('weavedata')
         if self._data_use_tracking:
            dataTypes.append('trackdata')

         # Add machining data types if schemas were loaded
         for mdt in ('machineprocess', 'machiningpose'):
            if mdt in self._data_schemas:
               dataTypes.append(mdt)
         
         logger.LogInfo(f"Data types to process: {dataTypes}")
         
         for dataType in dataTypes:
            usedNames = self._data_used_names.get(dataType, set())
            logger.LogInfo(f"{dataType}: Used names = {usedNames}")
            
            if not usedNames:
               continue
            
            instances = self._data_instances.get(dataType, {})
            instanceList = instances.get('instances', [])
            logger.LogInfo(f"{dataType}: Found {len(instanceList)} instances")
            
            # Add comment header
            self.AddLineToData(f"  ! {dataType.upper()} declarations")
            
            # Output declarations for used instances (matched by name)
            for instance in instanceList:
               instanceName = instance.get('name', '')
               if instanceName in usedNames:
                  logger.LogInfo(f"Formatting declaration for {dataType}: {instanceName}")
                  declaration = self.FormatDataDeclaration(dataType, instance)
                  if declaration:
                     # Replace template scope with actual scope
                     if declaration.startswith('TASK PERS'):
                        declaration = scope + declaration[9:]  # Replace "TASK PERS"
                     elif declaration.startswith('LOCAL PERS'):
                        declaration = scope + declaration[10:]  # Replace "LOCAL PERS"
                     
                     # Ensure proper indentation
                     if not declaration.startswith('  '):
                        declaration = '  ' + declaration
                     
                     logger.LogInfo(f"Adding declaration: {declaration[:50]}...")
                     self.AddLineToData(declaration)
            
            self.AddLineToData("")  # Blank line separator
         
         logger.LogInfo("OutputDataDeclarations: Complete")
      
      except Exception as e:
         logger.LogError(f"Failed to output data declarations: {str(e)}")
         import traceback
         logger.LogError(traceback.format_exc())

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called at the beginning of each program.
      
      Creates a DATA section header compliant with RAPID and declares the module.
      """
      self.ProgramName = program.GetName()
      
      # Set ModuleName from program name for main program (first call)
      if not self._abb_module_open:
         self.ModuleName = self.ProgramName + '_MOD'

      # Control program output for exceptional subprograms
      if self.AvoidOutputOfExceptionalSubprograms:
         if self.ProgramName in self.ExceptionalSubprograms:
            self.DontWriteAnySubprogram = True
            self.AddLineToDataHeader('! Cenit E2 Programm: %s is exceptional program where program output is avoid!' % (self.ProgramName))
            return 
         else:
            self.DontWriteAnySubprogram = False            
      else:
            self.DontWriteAnySubprogram = False


      logger = operator.GetLogOperator()
      controller = operator.GetController()
      activeProgram = controller.GetActiveProgram()
      programName = activeProgram.GetName()
      # Create module header once (single-module output)
      if not self._abb_module_open:
         self.AddLineToDataHeader('%'*3)
         self.AddLineToDataHeader('  VERSION:1')
         self.AddLineToDataHeader('  LANGUAGE:ENGLISH')
         self.AddLineToDataHeader('%'*3)
         self.AddLineToDataHeader('MODULE %s' % (self.ModuleName))
         self.AddLineToDataHeader('')

         # create motion profiles once
         self.HandleMotionProfiles(operator, activeProgram)

         self.AddLineToDataHeader('! Cenit E2 Program: %s' % (programName))
         
         # Load data management schemas and instances
         self.LoadDataManagement(operator, program)
         
         self._abb_module_open = True

      # Procedure per program (main + subs)
      proc_name = program.GetName()
      
      # For the first program (main), initialize data tracking
      if not hasattr(self, '_data_declarations_output') or not self._data_declarations_output:
         # Initialize tracking if needed
         if not hasattr(self, '_data_used_names'):
            self._data_used_names = {}
         # Note: data names collected during operation_start callbacks
         # Output declarations after all operations processed in ProgramEnd
      
      self.AddLineToSourceHeader('  PROC %s()' % (proc_name))
      self.AddLineToSourceHeader('    ! ABB Configuration')
      self.AddLineToSourceHeader('    ConfJ\\On;')
      
      # Station setup: Read from JSON, override with E2 program attribute if present
      station_enabled = self._defaults_get_bool(['stations', 'enabled'], False)
      station_index = self._defaults_get_int(['stations', 'default'], None)
      station_list = self._defaults_get_list(['stations', 'list'], [])
      
      # Check if E2 global attribute ABBStation is set (enum with setup_proc name).
      # Only attempt when stations are enabled; ignore the special sentinel "None"
      # (index 0) which means "no station" and is the tech default.
      if station_enabled:
         try:
            e2_station_name = program.GetLiteralAttribute('ABBStation', True).GetValue()
            if e2_station_name and e2_station_name.strip() and e2_station_name.strip() != 'None':
               # Find station by setup_proc name
               for station in station_list:
                  if isinstance(station, dict) and station.get('setup_proc', '') == e2_station_name:
                     station_index = station.get('index')
                     logger.LogInfo(f"ABB Station: E2 attribute ABBStation='{e2_station_name}' overrides JSON default -> index {station_index}")
                     break
         except Exception:
            pass
      
      if station_enabled and station_index is not None and station_index > 0:
         # Load station configuration from list structure
         setup_proc = None
         wobj = None
         
         for station in station_list:
            if isinstance(station, dict) and station.get('index') == station_index:
               setup_proc = station.get('setup_proc', '')
               wobj = station.get('wobj', '')
               
               # Parse rail configuration
               rail_group_str = station.get('rail_group_index', '')
               rail_adjustment_str = station.get('rail_ajustment', '0.0')
               
               break
         
         if setup_proc and wobj:
            self._station_active_index = station_index
            self._station_setup_proc = setup_proc
            self.shared.station_wobj_name = wobj
            self.shared.active_wobj_name = wobj
            
            # Parse active mechanism groups for external axis filtering
            ext_mechanism_str = station.get('ext_mechanism', '')
            self._station_active_groups = set()
            if ext_mechanism_str:
               try:
                  group_parts = str(ext_mechanism_str).split(',')
                  for part in group_parts:
                     group_idx = int(part.strip())
                     self._station_active_groups.add(group_idx)
                  logger.LogDebug(f"ABB Station {station_index}: Active mechanism groups = {sorted(self._station_active_groups)}")
               except Exception as e:
                  logger.LogWarn(f"ABB Station {station_index}: Failed to parse ext_mechanism '{ext_mechanism_str}': {e}")
            
            # Parse rail adjustment configuration
            self._rail_group_index = None
            self._rail_adjustment = 0.0
            if rail_group_str:
               try:
                  self._rail_group_index = int(rail_group_str.strip())
                  self._rail_adjustment = float(rail_adjustment_str)
                  logger.LogInfo(f"ABB Station {station_index}: Rail group {self._rail_group_index} adjustment = {self._rail_adjustment} mm")
               except Exception as e:
                  logger.LogWarn(f"ABB Station {station_index}: Failed to parse rail config: {e}")
            
            # Emit setup procedure call
            self.AddLineToSourceHeader(f'    {setup_proc};')
            logger.LogInfo(f"ABB Station: Activated station {station_index} - setup={setup_proc}, wobj={wobj}, mechanisms={sorted(self._station_active_groups)}")
         else:
            logger.LogDebug(f"ABB Station: Index {station_index} has no setup_proc or wobj, using OLP wobj")
      else:
         logger.LogDebug("ABB Station: No station configured, using OLP wobj")

      # Output PARTDATA declaration at the beginning
      program_name = self.ProgramName if self.ProgramName else "MainProgram"
      partdata_name = f"pd_{program_name}"
      station_index = self._station_active_index if self._station_active_index is not None else 0
      partdata_line = f'  TASK PERS partdata {partdata_name}:=["{program_name}","Comment","",{station_index},0,"",""];'
      self.AddLineToDataHeader(partdata_line)
      self.AddLineToDataHeader("")

      self.Source = []
      self._plugins.program_start(operator, program, self)
      
   def OperationGroupStart(self, operator: DULPythonDownloadOperator, operationGroup: DULPythonOperationGroup):
      """Called at the start of each Operation Group.
      
      Stores the current operation group for attribute access.
      """
      logger = operator.GetLogOperator()
      logger.LogDebug(f"ABB_IRC5 OperationGroupStart: {operationGroup.GetName()}")
      self._current_operation_group = operationGroup
      
      # Reset Frame3pConnect detection flag for new operation group
      # Plugin will re-detect based on TSConnectionType for this group's operations
      for plugin in self._plugins.plugins:
         if hasattr(plugin, '_is_frame3p_touch'):
            plugin._is_frame3p_touch = False
      
   def OperationStart(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Called at the beginning of each operation.
      
      Checks and updates base frames and tools.
      """
      logger = operator.GetLogOperator()
      if self.DontWriteAnySubprogram:
         return
      self._current_operation = operation
      
      # Reset per-operation point-ref mapping. PointCounter itself remains global for the module,
      # but E2's motion objects and names can repeat across operations.
      try:
         self._abb_motion_point_ref_by_id = {}
         self._abb_motion_via_point_ref_by_id = {}
      except Exception:
         pass
      self._abb_ref_motion_counter = 0

      # Get the base frame index
      baseFrameProfile = operation.GetUsedBaseProfile()
      baseFrameName = baseFrameProfile.GetName()
      baseFrameIndex = baseFrameProfile.GetIndex()
      #self.CheckAndUpdateBaseFrame(operator, logger, baseFrameIndex, baseFrameName)
      self.baseFrameName= baseFrameName
      self.CurrentBaseFrameIndex = baseFrameIndex
      # Get the tool frame index
      toolFrameProfile = operation.GetUsedToolProfile()
      toolFrameName = toolFrameProfile.GetName()
      toolFrameIndex = toolFrameProfile.GetIndex()
      self.CurrentToolFrameIndex = toolFrameIndex
      self.ToolFrameName = toolFrameName
      #self.CheckAndUpdateToolFrame(operator, logger, toolFrameIndex, toolFrameName)
      self.CurrentSeamDataNumber = operation.GetInteger('Seamdata Number',True)
      self.CurrentWeldDataNumber = operation.GetInteger('Welddata Number',True)
      
      # Track work method type for displacement_auto_off
      try:
         self._current_workmethod = operation.GetString('ArcWeldingOperationWorkMethodName', False)
      except Exception:
         self._current_workmethod = None
      
      # Comment for Seam
      self.AddLineToSource('    ! Operation: %s' % (operation.GetName()))

      self._plugins.operation_start(operator, operation, self)

   def OperationEnd(self, operator: DULPythonDownloadOperator, operation: DULPythonOperation):
      """Called at the end of each operation.
      
      Handles:
      1. Frame3P assignments + OFrameChange after last touch operation
      2. Auto PDispOff for non-touch work methods when displacement_auto_off is enabled
      """
      if self.DontWriteAnySubprogram:
         return
      
      logger = operator.GetLogOperator()
      
      # Check if this operation is a Frame3P touch operation with measurements
      if hasattr(self, '_current_frame3p_touch_id') and self._current_frame3p_touch_id:
         touch_id = self._current_frame3p_touch_id
         
         # Emit Frame3P assignments + OFrameChange at end of last touch operation
         logger.LogDebug(f"Frame3pConnect: OperationEnd for TouchId {touch_id}, emitting assignments + OFrameChange")
         
         # Get measurement counters from the active plugin with touch sensing
         # (both plugins have the mixin, but only the active one has real counters)
         mea_counters = {}
         for plugin in self._plugins.plugins:
            if isinstance(plugin, _ABBTouchSensingMixin) and getattr(plugin, '_frame3p_mea_counters', {}):
               mea_counters = plugin._frame3p_mea_counters
               if mea_counters:
                  break
         
         refp1_key = (touch_id, 1)
         refp2_key = (touch_id, 2)
         refp3_key = (touch_id, 3)
         
         # Emit assignments to pMea1/2/3
         refp1_mea_count = mea_counters.get(refp1_key, 0)
         if refp1_mea_count == 1:
            self.AddLineToSource(f"    pMea1 := tid_pt1_mea1;")
         elif refp1_mea_count == 2:
            self.AddLineToSource(f"    pMea1 := tid_pt1_mea2;")
         elif refp1_mea_count == 3:
            self.AddLineToSource(f"    pMea1 := tid_pt1_mea3;")
         
         refp2_mea_count = mea_counters.get(refp2_key, 0)
         if refp2_mea_count == 1:
            self.AddLineToSource(f"    pMea2 := tid_pt2_mea1;")
         elif refp2_mea_count == 2:
            self.AddLineToSource(f"    pMea2 := tid_pt2_mea2;")
         
         refp3_mea_count = mea_counters.get(refp3_key, 0)
         if refp3_mea_count == 1:
            self.AddLineToSource(f"    pMea3 := tid_pt3_mea1;")
         
         # Emit OFrameChange
         base_wobj = self.shared.station_wobj_name if self.shared.station_wobj_name else self.baseFrameName
         self.AddLineToSource(f"    obNEW_{touch_id} := OFrameChange({base_wobj}, pRef1, pRef2, pRef3, pMea1, pMea2, pMea3);")
         
         # Clear the current Frame3P touch ID
         self._current_frame3p_touch_id = None
      
      # Check if displacement_auto_off is enabled
      auto_off_enabled = self._defaults_get_bool(['output', 'displacement_auto_off'], False)
      
      if auto_off_enabled and self._current_workmethod:
         # Check if this is a non-touch work method
         non_touch_workmethods = ['StitchWeldingWorkMethod', 'ContourPointWorkMethod']
         if self._current_workmethod in non_touch_workmethods:
            # Output PDispOff at end of non-touch operations
            self.AddLineToSource("    PDispOff;")
            logger.LogDebug(f"Auto PDispOff: Emitted for {self._current_workmethod}")
            
            # Also deactivate Frame3P work object if active (same as TouchId=0 revert)
            if self.shared.frame3p_wobj_active:
               self.shared.frame3p_wobj_active = False
               self.shared.active_wobj_name = self.shared.station_wobj_name
               self._frame3p_active_touchid = None
               wobj_name = self.shared.station_wobj_name if self.shared.station_wobj_name else self.baseFrameName
               logger.LogDebug(f"Auto PDispOff: Deactivated Frame3P wobj, reverted to {wobj_name}")

   def HandleMotion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Processing of path elements and motion events.
      Depending on the type of motion (point-to-point, linear, circular)
      the corresponding functions are called that generate RAPID commands."""
      if self.DontWriteAnySubprogram:
         return

      is_reference = False
      try:
         is_reference = bool(motion.IsReferenceMotion())
      except Exception:
         is_reference = False

      read_ahead_event_ids = set()  # type: Set[int]

      eventsBefore = motion.GetEventsBefore()
      for event in eventsBefore:
         # Some events-before affect how the *current* motion should be emitted.
         # Read-ahead events are consumed by plugins for motion decoration and
         # must not be emitted again via HandleEvent.
         try:
            name = event.GetName()
         except Exception:
            name = ''

         try:
            if name in self._plugins.read_ahead_events:
               self._plugins.handle_read_ahead_event(operator, motion, event, self)
               try:
                  read_ahead_event_ids.add(id(event))
               except Exception:
                  pass
               continue
            self._plugins.handle_event_before(operator, motion, event, self)
         except Exception:
            self._plugins.handle_event_before(operator, motion, event, self)

         self.HandleEvent(operator, motion, event)

      eventsAfter = motion.GetEventsAfter()

      cmd_before = ''
      cmd_after = ''

      if not is_reference:
         # Generate point definitions (data section)
         self.HandleDataSection(operator, motion)

         # Build motion command without emitting it (so plugins can replace it).
         # Also capture the emitted point reference(s) from the command and reuse them
         # for TouchSensing bookkeeping and capture-trace identity.
         cmd_before = self._abb_build_motion_command(operator, motion)
         emitted_refs = self._abb_extract_point_refs_from_cmd(cmd_before)
         if emitted_refs:
            try:
               # For MoveC we get [via, target]; treat the target as the motion identity.
               self._abb_motion_point_ref_by_id[id(motion)] = emitted_refs[-1]
               if len(emitted_refs) >= 2:
                  self._abb_motion_via_point_ref_by_id[id(motion)] = emitted_refs[0]
            except Exception:
               pass

         self.shared.last_point_ref = self.shared.current_point_ref
         self.shared.current_point_ref = emitted_refs[-1] if emitted_refs else self._abb_get_point_ref_for_motion(motion)
         
         # Track approach point for Frame3pConnect Search_1D (store before TouchPointCollisionEvent fires)
         if not is_reference:
            self._frame3p_approach_point_ref = self.shared.current_point_ref
            self._frame3p_approach_motion = motion  # Store motion object for Explicit mode

         # Dispatch read-ahead events-after now that the current point ref is known.
         for event in eventsAfter:
            try:
               if event.GetName() in self._plugins.read_ahead_events:
                  try:
                     eid = id(event)
                  except Exception:
                     eid = None
                  if eid is not None and eid in read_ahead_event_ids:
                     continue
                  self._plugins.handle_read_ahead_event(operator, motion, event, self)
                  if eid is not None:
                     read_ahead_event_ids.add(eid)
            except Exception:
               continue

         cmd_after = self._plugins.decorate_motion_command(operator, motion, cmd_before, self)
         if cmd_after:
            self.AddLineToSource(cmd_after)

         # Only non-reference motions consume point numbers.
         if motion.IsCircularMotion():
            self.PointCounter += 2
         else:
            self.PointCounter += 1
      else:
         # Reference motions are typically event containers; they should not consume
         # point numbers nor disturb the current/last point refs.
         try:
            key = id(motion)
            if key not in self._abb_motion_point_ref_by_id:
               self._abb_motion_point_ref_by_id[key] = 'REF%04d' % self._abb_ref_motion_counter
               self._abb_ref_motion_counter += 1
         except Exception:
            pass

      # Then handle events after the motion (non read-ahead)
      for event in eventsAfter:
         if event.GetName() not in self._plugins.read_ahead_events:
            self.HandleEvent(operator, motion, event)

   def SubprogramStart(self, operator: DULPythonDownloadOperator, subProgram: DULPythonSubprogram):
      """Called when a subprogram is called.

      Args:
      operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      subprogram (DULPythonSubprogram): sub program operator gives access to the complete sub program
      
      Adds a subprogram call command in the source section.
      """
      _ = operator      # If "operator" is not used
      subProgramName = subProgram.GetName()
      # Control program output for exceptional subprogram calls
      if self.AvoidExceptionalSubprogramsCalls:
         if subProgramName in self.ExceptionalSubprogramsCalls:            
            return      
      self.AddLineToSource('  ! Subprogram call')
      self.AddLineToSource('  CALL %s' % subProgramName)

   def ProgramEnd(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called at the end of the program.

      Ends the main procedure and module.
      """
      if self.DontWriteAnySubprogram:
         return
      
      logger = operator.GetLogOperator()
      
      # Output data declarations at end of first program (after all operations collected)
      if not hasattr(self, '_data_declarations_output') or not self._data_declarations_output:
         self.CollectUsedDataNames(operator)
         self.OutputDataDeclarations(operator)
         self._data_declarations_output = True
      
      self.AddLineToSource('  EndProc')
      self._plugins.program_end(operator, program, self)

      # Close the module only once; E2 will typically call WriteOutputFile after all programs.
      if self._abb_module_open:
         # Defer ENDMODULE to footer only once.
         if not self.Footer or self.Footer[-1] != 'ENDMODULE':
            self.AddLineToFooter('ENDMODULE')

   def CreateOutputFile(self, operator: DULPythonDownloadOperator):
      """Creates the .mod output file. 
      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
      
      Sets the file path, creates the header, and prepares data structures.
      """
      outputDir = self.GetOutputDirectory(operator)
      # Original
      # self.OutputFilePath = os.path.join(outputDir, self.ProgramName + self.FILE_EXTENSION)
      # Single-module output: use module name
      self.OutputFilePath = os.path.join(outputDir, self.ModuleName + self.FILE_EXTENSION)

      self.CreateHeader(operator)

      # This line defines a method in the ABBDownloader class that is responsible for writing the output file (i.e., the .mod file).
   def WriteOutputFile(self, operator: DULPythonDownloadOperator):
      """Saves the output file.
      
      Combines all sections: header, data, source, and footer
      and saves them to a .mod file.
      """
      # Save the header (e.g., variable declarations, dates, etc.)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Header)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.DataHeader)
      '''%%%
      ABB-Downloader - Technikerarbeit Mulewski'
      RAPID Data Section
      LANGUAGE:ENGLISH
      %%%
      MODULE PRG001_mod'''
      # This line saves the collected data (header, position data, movements, etc.) in .mod format.
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Data) 
      '''
      LOCAL PERS robtarget P001:=[[1292.56,0,993.585],[0.224101,0,0.974566,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
      LOCAL PERS robtarget P002:=[[1343.216,0,889.264],[0.224101,0,0.974566,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
      LOCAL PERS robtarget P003:=[[863.104,0,656.134],[0.224101,0,0.974566,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
      LOCAL PERS robtarget P004:=[[798.538,0,789.101],[0.224101,0,0.974566,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
      LOCAL PERS tooldata T0:=[TRUE,[[0,0,0],[1,0,0,0]],[0.1,[0,0,0.1],[1,0,0,0],0,0,0.1]];
      LOCAL PERS wobjdata B0:=[FALSE,TRUE,"",[[1171.787,1211.364,403.303],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
      LOCAL PERS speeddata uv1000:=[1000,500,5000,1000];
      LOCAL PERS speeddata up50:=[3500,500,5000,1000];
      '''
      # Save the source section – declaration of the main procedure
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.SourceHeader)
      '''PROC PRG001()
      ! Configuration Setting
      ConfJ[backslash]On;'''
      # Save motion commands
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Source)  
      '''MoveJ P001,up50,fine,T0[backslash]Wobj:=B0;
      MoveL P002,uv1000,fine,T0[backslash]Wobj:=B0;
      MoveL P003,uv1000,fine,T0[backslash]Wobj:=B0;
      MoveL P004,uv1000,fine,T0[backslash]Wobj:=B0;'''
      # Save the footer (ENDMODULE)
      self.FileUtil.AppendTextArrayToFile(self.OutputFilePath, self.Footer)
      '''
      ENDPROC
      ENDMODULE'''
      # Clear buffered data
      self.Header.clear()
      self.DataHeader.clear()
      self.Data.clear()
      self.SourceHeader.clear()
      self.Source.clear()
      self.Footer.clear()

      operator.AddOutputFilePath(self.OutputFilePath)

      # Optionally write a .pgf program file alongside the .mod
      if self._defaults_get_bool(['output', 'output_pgf'], False):
         self._write_pgf_file(operator)

   def _write_pgf_file(self, operator: DULPythonDownloadOperator) -> None:
      """Write an ABB .pgf (Program) file listing the .mod module.

      The .pgf sits next to the .mod and tells the controller which modules
      belong to the program.  Format::

         <?xml version="1.0" encoding="ISO-8859-1" ?>
         <Program>
            <Module>ModuleName.mod</Module>
         </Program>
      """
      mod_basename = os.path.basename(self.OutputFilePath)          # e.g. "MainModule.mod"
      pgf_path = self.GetOutputDirectory(operator) + '\\'+ self.ProgramName + '.pgf'  # same dir, .pgf ext, named after program

      lines = [
         '<?xml version="1.0" encoding="ISO-8859-1" ?>',
         '<Program>',
         f'\t<Module>{mod_basename}</Module>',
         '</Program>',
      ]
      with open(pgf_path, 'w', encoding='iso-8859-1') as f:
         f.write('\n'.join(lines) + '\n')

      operator.AddOutputFilePath(pgf_path)

#################### SOURCE SECTION ####################

   def HandleSourceSection(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Processes motion commands depending on the type of motion.

      For linear, point-to-point, or circular motion
      calls the appropriate method that generates the RAPID command.
      """
      # If the motion is not just a reference:
      if not motion.IsReferenceMotion():
         if motion.IsLinearMotion():
            cmd = self.OutputSourceLin(operator, motion)
            self.AddLineToSource(cmd)
         elif motion.IsCircularMotion():
            cmd = self.OutputSourceCirc(operator, motion)
            self.AddLineToSource(cmd)
         else:
            # Assume the rest are point-to-point motion
            cmd = self.OutputSourcePtp(operator, motion)
            self.AddLineToSource(cmd)

   def _abb_build_motion_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion) -> str:
      if motion.IsReferenceMotion():
         return ''
      if motion.IsLinearMotion():
         return self.OutputSourceLin(operator, motion)
      if motion.IsCircularMotion():
         return self.OutputSourceCirc(operator, motion)
      return self.OutputSourcePtp(operator, motion)

   def _abb_extract_point_refs_from_cmd(self, cmd: str) -> List[str]:
      """Extract RAPID point references (e.g. ['P001'] or ['P010','P011']) from a Move* line.

      This is intentionally simple and tolerant; it is used for bookkeeping/capture only.
      """
      try:
         if not cmd:
            return []
         s = cmd.strip()
         if not s:
            return []
         # Expected formats:
         #   MoveJ P001,...
         #   MoveL P001,...
         #   MoveC P001,P002,...
         # Keep it simple: grab the token segment after the mnemonic and before the next ','
         parts = s.split()
         if len(parts) < 2:
            return []
         token = parts[1]
         # token may include trailing ';' if no commas (unlikely) or be 'P001,P002,...'
         token = token.rstrip(';')
         token = token.split(',')[0] if ',' not in token else token
         # For MoveC token can include 'P001,P002'
         refs = []
         for t in token.split(','):
            t = t.strip()
            if t.startswith('P') and len(t) >= 2:
               refs.append(t)
         return refs
      except Exception:
         return []

   def _abb_get_point_ref_for_motion(self, motion: DULPythonMotion) -> Optional[str]:
      # Reference name used in capture/plugin bookkeeping.
      # Prefer the emitted RAPID point token extracted from the generated command.
      try:
         key = id(motion)
         v = self._abb_motion_point_ref_by_id.get(key)
         if v:
            return v
      except Exception:
         pass

      # Fallback to E2 motion name (can repeat per operation).
      try:
         name = motion.GetName()
         if name:
            return name
      except Exception:
         pass
      return None

   def _abb_sanitize_rapid_identifier(self, name: str) -> str:
      # RAPID identifiers must start with a letter; keep it conservative.
      try:
         s = str(name or '').strip()
      except Exception:
         s = ''
      if not s:
         return ''

      out = []
      for ch in s:
         if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or ('0' <= ch <= '9') or (ch == '_'):
            out.append(ch)
         else:
            out.append('_')
      s2 = ''.join(out).strip('_')
      if not s2:
         return ''
      if not (('a' <= s2[0] <= 'z') or ('A' <= s2[0] <= 'Z')):
         s2 = 'P' + s2
      # Keep names reasonably short.
      return s2[:32]

   def _abb_get_rapid_point_name_from_position(self, position: Any, default_index: int) -> str:
      if not getattr(self, '_abb_use_e2_position_names', True):
         return 'P%03d' % int(default_index)
      try:
         if position is not None:
            n = position.GetName()
            n2 = self._abb_sanitize_rapid_identifier(n)
            if n2:
               return n2
      except Exception:
         pass
      return 'P%03d' % int(default_index)

   def _abb_get_rapid_point_name_from_motion(self, motion: DULPythonMotion, default_index: int) -> str:
      try:
         pos = motion.GetPosition()
      except Exception:
         pos = None
      return self._abb_get_rapid_point_name_from_position(pos, default_index)

   def _abb_get_rapid_joint_name_from_motion(self, motion: DULPythonMotion, default_index: int) -> str:
      """Generate jointtarget name for joint-based motion.
      
      Uses 'J' prefix instead of 'P' for joint targets.
      Example: J001, J002, etc.
      """
      try:
         name = motion.GetName()
         if name and name.strip():
            # Clean name: remove special characters, limit length
            clean_name = ''.join(c for c in name if c.isalnum() or c == '_')
            if clean_name:
               return 'J' + clean_name[:15]
      except Exception:
         pass
      return 'J%03d' % int(default_index)

   def _abb_round_to_predefined_speed(self, speed_value: float) -> int:
      """Round speed value to nearest predefined ABB speed.
      
      Predefined speeds: v5, v10, v20, v30, v40, v50, v60, v80, v100,
                        v200, v300, v400, v500, v600, v800, v1000,
                        v1500, v2000, v2500, v3000, v4000, v5000, v6000, v7000
      """
      predefined_speeds = [
         5, 10, 20, 30, 40, 50, 60, 80, 100,
         200, 300, 400, 500, 600, 800, 1000,
         1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000
      ]
      
      # Find closest predefined speed
      closest = min(predefined_speeds, key=lambda x: abs(x - speed_value))
      return closest

   def _abb_get_speed_token_for_motion(self, motion: DULPythonMotion) -> str:
      def _as_speed_token(value: Any, default_value: int) -> str:
         # Accept typical E2/ABB shapes:
         #   - 600 / 600.0  -> v600
         #   - '600'        -> v600
         #   - 'V600'/'v600'-> keep as-is (already a token)
         #   - other strings -> best-effort digits parse, else fallback
         if value is None:
            return 'v%d' % int(default_value)
         if isinstance(value, (int, float)):
            try:
               rounded = self._abb_round_to_predefined_speed(float(value))
               return 'v%d' % rounded
            except Exception:
               return 'v%d' % int(default_value)
         try:
            s = str(value).strip()
         except Exception:
            return 'v%d' % int(default_value)
         if not s:
            return 'v%d' % int(default_value)

         # If it's already a speed token like V600/v600, keep it.
         if (len(s) >= 2) and (s[0] in ('v', 'V')) and all(ch.isdigit() for ch in s[1:]):
            return s

         # If it's a pure number string, prefix with v.
         if all(ch.isdigit() for ch in s):
            return 'v%s' % s

         # Best-effort: extract first integer-like sequence.
         digits = []
         for ch in s:
            if ch.isdigit():
               digits.append(ch)
            elif digits:
               break
         if digits:
            return 'v%s' % ''.join(digits)

         return 'v%d' % int(default_value)

      if motion.IsLinearMotion() or motion.IsCircularMotion():
         return _as_speed_token(self.CurrentLinFeedrate, 1000)
      return _as_speed_token(self.CurrentPtpFeedrate, 100)

   def _abb_get_tool_token(self) -> str:
      # Existing output uses tool name token directly.
      # OutputSource* already includes tool/wobj for normal moves; Search_1D wants just tool + wobj.
      if self.ToolFrameName:
         return self.ToolFrameName
      return 'tool0'

   def _abb_get_wobj_token(self) -> str:
      # Priority: Frame3pConnect obNEW > Station wobj > OLP baseFrameName
      
      # 1. Frame3pConnect active work object (obNEW_<TouchId>)
      if self.shared.frame3p_wobj_active and self.shared.active_wobj_name and self.shared.active_wobj_name.startswith('obNEW_'):
         return "\\Wobj:=%s" % self.shared.active_wobj_name
      
      # 2. Station work object (e.g., wobjUse)
      if self.shared.station_wobj_name:
         return "\\Wobj:=%s" % self.shared.station_wobj_name
      
      # 3. OLP base frame name
      if self.baseFrameName:
         return "\\Wobj:=%s" % self.baseFrameName
      
      return ''
   
   def _get_active_wobj_name(self) -> str:
      """Get the currently active work object name for motion commands.
      
      Priority: Frame3pConnect obNEW > Station wobj > OLP baseFrameName
      """
      # 1. Frame3pConnect active (obNEW_<TouchId>)
      if self.shared.frame3p_wobj_active and self.shared.active_wobj_name and self.shared.active_wobj_name.startswith('obNEW_'):
         return self.shared.active_wobj_name
      
      # 2. Station wobj
      if self.shared.station_wobj_name:
         return self.shared.station_wobj_name
      
      # 3. OLP baseFrameName
      return self.baseFrameName if self.baseFrameName else 'wobj0'

   def _defaults_get_str(self, path: List[str], default: str) -> str:
      node = self._defaults
      for key in path:
         if not isinstance(node, dict) or key not in node:
            return default
         node = node.get(key)
      if node is None:
         return default
      return str(node)

   def _defaults_get_list(self, path: List[str], default: List[Any]) -> List[Any]:
      node = self._defaults
      for key in path:
         if not isinstance(node, dict) or key not in node:
            return default
         node = node.get(key)
      if isinstance(node, list):
         return node
      return default

   def _load_defaults_json(self, operator: DULPythonDownloadOperator, defaults_file: str) -> Dict[str, Any]:
      logger = operator.GetLogOperator()
      
      # Use TechTab folder: Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/

      # Obsolete way to retrieve E2Plugin's TechTab folder (since R20205.2.4 new method to get path from 
      # # Calculate relative path from downloader directory
      # downloader_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
      # # Navigate from OLPTranslators/ABB to Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs
      # technology = operator.GetController().GetActiveProgram().GetGroupsAndSubprograms()[0].GetTechnology().GetName()  # Assuming first group/subprogram indicates technology

      # base_dir = os.path.join(downloader_dir, '..', '..', 'Technologies', technology, 'ABB', 'Standard', 'TechTabs')
      # base_dir = os.path.abspath(base_dir)

      # candidate = defaults_file
      # if not os.path.isabs(candidate):
      #    candidate = os.path.join(base_dir, candidate)

      candidate = operator.GetController().GetTechTabFolder(defaults_file)

      try:
         with open(candidate, 'r', encoding='utf-8') as f:
            return json.load(f)
      except Exception as exc:
         try:
            logger.LogWarn("ABB downloader: could not load defaults JSON '%s' (%s). Using in-code defaults." % (candidate, str(exc)))
         except Exception:
            pass
         return {}

   def _safe_get_operation_int(self, operation: DULPythonOperation, name: str, default: int) -> int:
      try:
         return int(operation.GetInteger(name, True))
      except Exception:
         return default

   def _safe_get_operation_str(self, operation: DULPythonOperation, name: str, default: str) -> str:
      """Get string attribute value from operation."""
      try:
         return str(operation.GetString(name, True))
      except Exception:
         return default

   def _safe_get_operation_enum(self, operation: DULPythonOperation, name: str, default: str) -> str:
      """Get enum attribute value (literal name) from operation.

      Tries a strict (this-object) lookup first, then a full-tree lookup so that
      attributes set at operation-group level (e.g. MACHINING_TECH_TYPE) are
      found even when the individual operation doesn't carry its own value.
      """
      try:
         val = operation.GetLiteralAttribute(name, True).GetValue()
         if val:
            return val
      except Exception:
         pass
      # Fallback: search the complete attribute tree (operation group / global)
      try:
         val = operation.GetLiteralAttribute(name, False).GetValue()
         if val:
            return val
      except Exception:
         pass
      return default

   def _abb_try_inject_arcware_operands(self, cmd: str, operands: List[str]) -> str:
      # Best-effort injection after the speed token. Keeps existing output intact if parsing fails.
      # ArcWare expects: 
      #   Linear: ArcLStart p, v, seamdata, welddata\Weave:=...\Track:=..., z, tool\Wobj:=wobj
      #   Circular: ArcCStart p1, p2, v, seamdata, welddata\Weave:=...\Track:=..., z, tool\Wobj:=wobj
      # Optional parameters (starting with \) are appended to the previous parameter without comma
      try:
         # Parse command respecting bracket nesting (for explicit mode robtargets)
         parts = []
         current = ""
         bracket_depth = 0
         
         for char in cmd.rstrip(';'):
            if char == '[':
               bracket_depth += 1
               current += char
            elif char == ']':
               bracket_depth -= 1
               current += char
            elif char == ',' and bracket_depth == 0:
               parts.append(current)
               current = ""
            else:
               current += char
         if current:
            parts.append(current)
         
         if len(parts) < 3:
            return cmd

         # Detect circular motion (MoveC/ArcC) which has two points before speed
         is_circular = 'MoveC' in parts[0] or 'ArcC' in parts[0]
         
         # Separate required operands from optional ones
         required = []
         optional = []
         for op in operands:
            if op.startswith('\\'):
               optional.append(op)
            else:
               required.append(op)
         
         if is_circular:
            # Circular: MoveC via,target,speed,zone,tool\Wobj:=wobj
            # Inject after parts[2] (speed)
            head = parts[0]
            p1 = parts[1]
            p2 = parts[2]
            injected = [head, p1, p2] + required
            # Append optional parameters to the last injected item (no comma)
            if optional and len(injected) > 0:
               injected[-1] = injected[-1] + ''.join(optional)
            tail = parts[3:]
            injected.extend(tail)
         else:
            # Linear: MoveL point,speed,zone,tool\Wobj:=wobj
            # Inject after parts[1] (speed)
            head = parts[0]
            p0 = parts[1]
            injected = [head, p0] + required
            # Append optional parameters to the last injected item (no comma)
            if optional and len(injected) > 0:
               injected[-1] = injected[-1] + ''.join(optional)
            tail = parts[2:]
            injected.extend(tail)
         
         return ','.join(injected) + ';'
      except Exception:
         return cmd

   def OutputSourcePtp(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Generates a point-to-point motion command (MoveJ or MoveAbsJ) in RAPID.

      Example RAPID command:
         MoveJ P1, v1000, z10, T0[backslash]WObj:=B0;  (Cartesian)
         MoveAbsJ [[0,0,0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]], v1000, z10, T0[backslash]WObj:=B0;  (Joint)

      Also changes the point counter value.
      """
      # Check if motion target is joint-based
      position = motion.GetPosition()
      motionTargetType = position.GetTargetType()
      # Check if target type is Joint (compare by name to avoid import issues)
      is_joint_target = (str(motionTargetType.name) == 'Joint' if hasattr(motionTargetType, 'name') else False)
      
      # Get the point name from FastSuite – shorten to max 16 characters
      # comment = self.CheckPointCommentLength(motion.GetName())
      # For ABB: if accuracy = 0, use "fine", otherwise zone (e.g., z10)
      if self.CurrentPtpAccuracy == 0:
         zone = 'fine'
      else:
         zone = 'uz' + str(self.CurrentPtpAccuracy)
         # TBD: Use ABB default Zonedata values , so far use constant "V100"
         zone = 'z100'
      # Get speed token from motion (uses CurrentPtpFeedrate with rounding to predefined speeds)
      speed_token = self._abb_get_speed_token_for_motion(motion)
      
      # Generate joint-based or Cartesian command
      if is_joint_target:
         # Use MoveAbsJ for joint targets
         if self.ABBTargetOutputStyle != "Explicit":
            # Implicit: use named jointtarget (e.g., J001)
            j = self._abb_get_rapid_joint_name_from_motion(motion, self.PointCounter)
            cmd = "    MoveAbsJ %s,%s,%s,%s\\WObj:=%s;" % (j, speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
         else:
            # Explicit: inline joint values [[A1..A6],[EA1..EA6]]
            cmd = "    MoveAbsJ %s,%s,%s,%s\\WObj:=%s;" % (self.ExplixitDataStorage[0], speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
      else:
         # Use MoveJ for Cartesian targets
         # ABB Output style check
         if self.ABBTargetOutputStyle != "Explicit":
            p = self._abb_get_rapid_point_name_from_motion(motion, self.PointCounter)
            cmd = "    MoveJ %s,%s,%s,%s\\WObj:=%s;" % (p, speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
         else:
            cmd = "    MoveJ %s,%s,%s,%s\\WObj:=%s;" % (self.ExplixitDataStorage[0], speed_token, zone,  self.ToolFrameName, self._get_active_wobj_name())
      return cmd

   def OutputSourceLin(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Generates a linear motion command (MoveL) in RAPID.

      Example RAPID command:
         MoveL P2, v1000, zfine, T0[backslash]WObj:=B0;
      """
      # comment = self.CheckPointCommentLength(motion.GetName())
      if self.CurrentLinAccuracy == 0:
         zone = 'fine'
      else:
         zone = 'uz' + str(self.CurrentLinAccuracy)
         # TBD: Use ABB default Zonedata values , so far use constant "V100"
         zone = 'z100'
      # Get speed token from motion (uses CurrentLinFeedrate with rounding to predefined speeds)
      speed_token = self._abb_get_speed_token_for_motion(motion)
      # ABB Output style check
      if self.ABBTargetOutputStyle != "Explicit":
         p = self._abb_get_rapid_point_name_from_motion(motion, self.PointCounter)
         if self.ArcweldingActive or self.IsWeldingStartPoint or self.IsWeldingEndPoint:            
            cmd = "    MoveL %s,%s,sd%02d, wd%02s, %s,%s\\WObj:=%s;" % (p, speed_token,self.CurrentSeamDataNumber,self.CurrentWeldDataNumber,zone,  self.ToolFrameName, self._get_active_wobj_name())
         else:
            cmd = "    MoveL %s,%s,%s,%s\\WObj:=%s;" % (p, speed_token, zone,  self.ToolFrameName, self._get_active_wobj_name())
      else:
         # For explicit mode: generate base command, let ArcWare plugin inject seam/weld
         cmd = "    MoveL %s,%s,%s,%s\\WObj:=%s;" % (self.ExplixitDataStorage[0], speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
      # In case welding is active...   
      if self.ArcweldingActive:         
         if self.IsWeldingEndPoint:
            cmd=cmd.replace("MoveL","ArcLEnd")
            self.IsWeldingEndPoint = False
         else:
            cmd=cmd.replace("MoveL","ArcL")

      elif self.IsWeldingStartPoint:
            cmd=cmd.replace("MoveL","ArcLStart")
            self.IsWeldingStartPoint = False
      
      return cmd

   def OutputSourceCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion):
      """Generates a circular motion command (MoveC) in RAPID.

      Example RAPID command:
         MoveC P3, P4, v1000, zfine, T0[backslash]WObj:=B0;
      
      Note: for circular motion, we need to generate two points:
         - the via point
         - the target point
      """
      # First point (via) and second point (target)
      viaPosition = motion.GetViaPosition()
      targetPosition = motion.GetPosition()
      via_name = self._abb_get_rapid_point_name_from_position(viaPosition, self.PointCounter)
      target_name = self._abb_get_rapid_point_name_from_position(targetPosition, self.PointCounter + 1)
      #commentTarget = self.CheckPointCommentLength(motion.GetName())
      if self.CurrentLinAccuracy == 0:
         zone = 'fine'
      else:
         zone = 'uz' + str(self.CurrentLinAccuracy)
         # TBD: Use ABB default Zonedata values , so far use constant "V100"
         zone = 'z100'
      # Get speed token from motion (uses CurrentLinFeedrate with rounding to predefined speeds)
      speed_token = self._abb_get_speed_token_for_motion(motion)
      # ABB Output style check
      if self.ABBTargetOutputStyle != "Explicit":
         # For implicit mode: generate base command, let ArcWare plugin inject seam/weld
         cmd = "    MoveC %s,%s,%s,%s,%s\\WObj:=%s;" % (via_name, target_name, speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
      else:
         # For explicit mode: generate base command, let ArcWare plugin inject seam/weld
         cmd = "    MoveC %s,%s,%s,%s,%s\\WObj:=%s;" % (self.ExplixitDataStorage[0], self.ExplixitDataStorage[1], speed_token, zone, self.ToolFrameName, self._get_active_wobj_name())
      # In case welding is active...   
      if self.ArcweldingActive:         
         if self.IsWeldingEndPoint:
            cmd=cmd.replace("MoveC","ArcCEnd")
            self.IsWeldingEndPoint = False
         else:
            cmd=cmd.replace("MoveC","ArcC")
      elif self.IsWeldingStartPoint:
            cmd=cmd.replace("MoveC","ArcCStart")
            self.IsWeldingStartPoint = False
      return cmd

#################### DATA SECTION ####################

   def HandleDataSection(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = True):
      """Generates a point definition (robtarget) in the DATA section.

      For linear and point-to-point motions, creates a definition
      with position and example orientation and configuration data.
      """
      # If the motion is not just a reference:
      if not motion.IsReferenceMotion():
         if motion.IsCircularMotion():
            # For circular motion, generate definitions for two points
            dataLines = self.OutputDataCirc(operator, motion, dataOutputOnly)
            iLineCounter=0
            for line in dataLines:
               if self.ABBTargetOutputStyle != "Explicit":
                  self.AddLineToData(line)
               else:
                  self.ExplixitDataStorage[iLineCounter]=line
               iLineCounter += 1
         else:
            # For linear or point-to-point motion
            dataLines = self.OutputDataPtp(operator, motion, dataOutputOnly)
            for line in dataLines:
               if self.ABBTargetOutputStyle != "Explicit":
                  self.AddLineToData(line)
               else:
                  self.ExplixitDataStorage[0]=line


   def OutputDataPtp(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = True):
      """Generates a robtarget or jointtarget definition for point-to-point motion.

      Example definition formats:
      LOCAL PERS robtarget P1:=[[X,Y,Z],[q1,q2,q3,q4],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
      LOCAL PERS jointtarget J1:=[[A1,A2,A3,A4,A5,A6],[EA1,EA2,EA3,EA4,EA5,EA6]];
      
      For simplicity, the orientation and configuration data are set to example values.
      """
      #if dataOutputOnly:
      #self.PointCounter += 1
      # Get the position from FastSuite
      position = motion.GetPosition()
      
      # Check if motion target is joint-based
      motionTargetType = position.GetTargetType()
      is_joint_target = (str(motionTargetType.name) == 'Joint' if hasattr(motionTargetType, 'name') else False)
      
      if is_joint_target:
         # Generate jointtarget declaration
         joints = position.GetMainJointValues()
         # Extract robot axes (first 6 values from tuples)
         robot_axes = [joints[i][1] for i in range(min(6, len(joints)))]
         # Pad with zeros if less than 6 axes
         while len(robot_axes) < 6:
            robot_axes.append(0.0)
         
         # Use same external axis filtering as robtarget (station-based)
         extax = self.GetABBExternalAxes(position)
         
         jname = self._abb_get_rapid_joint_name_from_motion(motion, self.PointCounter)
         
         # ABB Output style check
         if self.ABBTargetOutputStyle != "Explicit":
            line = "  LOCAL PERS jointtarget %s:=[[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f],%s];" % (
                  jname,
                  robot_axes[0], robot_axes[1], robot_axes[2], robot_axes[3], robot_axes[4], robot_axes[5],
                  extax
            )
         else:
            # For Explicit Output return only joint values
            line = "[[%.3f,%.3f,%.3f,%.3f,%.3f,%.3f],%s]" % (
                  robot_axes[0], robot_axes[1], robot_axes[2], robot_axes[3], robot_axes[4], robot_axes[5],
                  extax
            )
      else:
         # Generate robtarget declaration (Cartesian)
         pos = position.GetXYZ()
         rpy = position.GetOrientation()
         # Convert Euler angles to quaternion
         orientation = self.euler_to_quaternion(rpy[0], rpy[1], rpy[2])
         # Retrieve Turn values from XML
         turnValues = self.get_turn_value_from_xml(motion)
         configABB = self.compute_config_from_turn(motion)
         # Example configuration and external axis values
         extax = '[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]'
         extax=self.GetABBExternalAxes(position)

         pname = self._abb_get_rapid_point_name_from_position(position, self.PointCounter)

         # ABB Output style check
         if self.ABBTargetOutputStyle != "Explicit":
            line = "  LOCAL PERS robtarget %s:=[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s];" % (pname,
                  pos[0]*1000, pos[1]*1000, pos[2]*1000,
                  orientation[0], orientation[1], orientation[2], orientation[3],
                  str(turnValues),str(configABB),
                  str(extax))
         else:
            # For Explicit Output return only point cart.,ori, extaxes and config/turn
            line = "[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s]" % (
                  pos[0]*1000, pos[1]*1000, pos[2]*1000,
                  orientation[0], orientation[1], orientation[2], orientation[3],
                  str(turnValues),str(configABB),
                  str(extax))
      return [line]


   def OutputDataCirc(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, dataOutputOnly: bool = False):
      """Generates definitions of two robtargets for circular motion: via point and target point."""
      dataLines = []
      #if dataOutputOnly:
      #self.PointCounter += 1
      # Via point
      viaPosition = motion.GetViaPosition()
      via_name = self._abb_get_rapid_point_name_from_position(viaPosition, self.PointCounter)
      posVia = viaPosition.GetXYZ()
      rpyVia = viaPosition.GetOrientation()
      orientationVia = self.euler_to_quaternion(rpyVia[0], rpyVia[1], rpyVia[2])
      # Retrieve Turn values from XML
      turnValues = self.get_turn_value_from_xml(motion)
      configABB = self.compute_config_from_turn(motion)
      extax = '[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]'
      extax=self.GetABBExternalAxes(viaPosition)
      # ABB Output style check
      if self.ABBTargetOutputStyle != "Explicit":
         lineVia = "  LOCAL PERS robtarget %s:=[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s];" % (via_name,
               posVia[0]*1000, posVia[1]*1000, posVia[2]*1000,
               orientationVia[0], orientationVia[1], orientationVia[2], orientationVia[3],
               str(turnValues),str(configABB),
               str(extax))
      else:
         lineVia = "[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s]" % (
               posVia[0]*1000, posVia[1]*1000, posVia[2]*1000,
               orientationVia[0], orientationVia[1], orientationVia[2], orientationVia[3],
               str(turnValues),str(configABB),
               str(extax))
      dataLines.append(lineVia)
      # Target point
      targetPosition = motion.GetPosition()
      target_name = self._abb_get_rapid_point_name_from_position(targetPosition, self.PointCounter + 1)
      posTarget = targetPosition.GetXYZ()
      rpyTarget = targetPosition.GetOrientation()
      orientationTarget = self.euler_to_quaternion(rpyTarget[0], rpyTarget[1], rpyTarget[2])
      extax = '[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]'
      extax=self.GetABBExternalAxes(targetPosition)
      # ABB Output style check
      if self.ABBTargetOutputStyle != "Explicit":
         lineTarget = "  LOCAL PERS robtarget %s:=[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s];" % (target_name,
            posTarget[0]*1000, posTarget[1]*1000, posTarget[2]*1000,
               orientationTarget[0], orientationTarget[1], orientationTarget[2], orientationTarget[3],
               str(turnValues),str(configABB),
               str(extax))
      else:
         lineTarget = "[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f],[%s,%s],%s]" % (
               posTarget[0]*1000, posTarget[1]*1000, posTarget[2]*1000,
               orientationTarget[0], orientationTarget[1], orientationTarget[2], orientationTarget[3],
               str(turnValues),str(configABB),
               str(extax))
      dataLines.append(lineTarget)
      return dataLines
   
   def GetABBExternalAxes(self, motion: DULPythonPosition):
      """Get external axis values filtered by active station mechanisms.
      
      For each external joint:
      - If its mechanism group is in the active station's ext_mechanism list → use actual value
      - Otherwise → set to 9E9 (inactive)
      
      Linear joints (rails, etc.) are converted from meters to mm.
      Rotary joints remain in degrees.
      
      Always returns 6 values: [E1, E2, E3, E4, E5, E6]
      """
      # Initialize all external axes to 9E9 (inactive)
      extax_values = [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]
      
      # Get logger for debugging (no operator available here, so skip logging for now)
      # Will need to pass operator if detailed logging is required
      
      try:
         joints = motion.GetExternalJointValues()
         
         # GetExternalJointValues() returns [(joint_object, value), ...] where joint_object has GetJointIndex() and GetJointGroupIndex()
         # Sort by (group_index, joint_index) to match our mapping order
         sorted_joints = sorted(joints, key=lambda j: (j[0].GetJointGroupIndex(), j[0].GetJointIndex()))
         
         # Match each external joint value to its mapping
         for joint_tuple in sorted_joints:
            joint_object = joint_tuple[0]  # DULPythonJoint object
            joint_value = joint_tuple[1]   # Value in meters (linear) or degrees (rotary)
            
            group_index = joint_object.GetJointGroupIndex()
            joint_index = joint_object.GetJointIndex()
            key = (group_index, joint_index)
            
            # Check if this group is active for the current station
            if group_index not in self._station_active_groups:
               continue  # Skip inactive mechanisms
            
            # Look up the external axis position (E1-E6) for this joint
            extax_position = self._extax_map.get(key, -1)
            if extax_position < 0 or extax_position >= 6:
               continue  # Not mapped
            
            # Convert units: Prismatic (linear) joints are in meters → convert to mm
            # Rotational joints are already in degrees → no conversion
            kinematic_type = joint_object.GetJointType()
            if kinematic_type == JointKinematicType.Prismatic:
               # Linear axis: meters → mm
               final_value = joint_value * 1000.0
            else:
               # Rotational axis: already in degrees
               final_value = joint_value
            
            # Apply rail adjustment if this is the rail group
            if self._rail_group_index is not None and group_index == self._rail_group_index:
               final_value += self._rail_adjustment
            
            extax_values[extax_position] = final_value
      except Exception as e:
         # Fallback: return all 9E9 on error
         pass
      
      # Format as RAPID array string
      return '[' + ','.join(f"{val:.4f}" if val != 9E9 else '9E+09' for val in extax_values) + ']'

   def euler_to_quaternion(self, roll, pitch, yaw):
      """
      Converts Euler angles (roll, pitch, yaw) to a quaternion.
      
      Arguments:
         roll  - rotation around the X-axis (in radians)
         pitch - rotation around the Y-axis (in radians)
         yaw   - rotation around the Z-axis (in radians)
         
      Returns:
         list: [q_x, q_y, q_z, q_w] (quaternion)
      """

      
      # Umrechnung der Winkel von Grad in Radian
      roll = math.radians(roll)
      pitch = math.radians(pitch)
      yaw = math.radians(yaw)
      
      # Berechnung der Quaternions
      q_w = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
      q_x = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
      q_y = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
      q_z = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
      
      return q_w, q_x, q_y, q_z


      # cy = math.cos(yaw * 0.5)
      # sy = math.sin(yaw * 0.5)
      # cp = math.cos(pitch * 0.5)
      # sp = math.sin(pitch * 0.5)
      # cr = math.cos(roll * 0.5)
      # sr = math.sin(roll * 0.5)
# 
      # q_w = cr * cp * cy + sr * sp * sy
      # q_x = sr * cp * cy - cr * sp * sy
      # q_y = cr * sp * cy + sr * cp * sy
      # q_z = cr * cp * sy - sr * sp * cy
# 
      # return [q_x, q_y, q_z, q_w]

#################### EVENT HANDLING ####################

   def HandleEvent(self, operator: DULPythonDownloadOperator, currentMotion: DULPythonMotion, event: DULPythonEvent):
      """Handles motion events.
      
      For each event, calls the processing function (speed, accuracy, acceleration, dwell, logic port).
      """
      self.HandleBuildInEvents(operator, event)
      motions = event.GetMotions()
      for motion in motions:
         self.HandleMotion(operator, motion)
      eventName = event.GetName()
      # check if ARC ON event
      if eventName == 'ArcOnEvent':
         self.ArcweldingActive=True
         # return to avoid potential double handling
         return
      if eventName == 'ArcOffEvent':
         self.ArcweldingActive=False
         # return to avoid potential double handling
         return
      # Handle touch sensing events for Frame3pConnect
      if eventName == 'TouchPointCollisionEvent':
         self.HandleTouchPointCollisionEvent(operator, currentMotion, event)
         return
      if eventName == 'ConnectTouchProcessPointEvent':
         self.HandleConnectTouchProcessPointEvent(operator, currentMotion, event)
         return

   def HandleBuildInEvents(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handles built-in events (speed, accuracy, acceleration, text, dwell, logic port)."""
      if event.GetName() == 'Speed':
         self.SetSpeed(operator, event)
      elif event.GetName() == 'Accuracy':
         self.SetAccuracy(operator, event)
      elif event.GetName() == 'Acceleration':
         self.SetAcceleration(operator, event)
      elif event.GetName() == 'TextEvent':
         self.TextEvent(operator, event)
      elif event.GetName() == 'Dwell':
         self.OutputDwellEvent(operator, event)
      elif event.GetName() == 'LogicPort':
         self.LogicPortEvent(operator, event)

   def SetSpeed(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Sets the motion speed based on the Speed event.

      For linear motion, converts to mm/sec, and for point-to-point sets the value.
      """
      pathtype = ''
      speed = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            speed = attribute.GetValue()
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      if pathtype == 'Contour':
         cmd  = 'uv' + str(int(speed * 1000))
         self.CurrentLinFeedrate = int(speed * 1000)
      else:
         cmd = 'up' + str(int(speed))
         self.CurrentPtpFeedrate = int(speed)
      
      entryAlreadyExist = False

      for entry in self.DataSectionSpeedProfiles:
         if entry == cmd:
            entryAlreadyExist = True
            break
         # check if motion profile already exists in the list
      if entryAlreadyExist == False:
         self.DataSectionSpeedProfiles.append(cmd)
         # create motion profile string
         if pathtype == 'Contour':
            # uv
            if self.ABBProfilesOutput: self.AddLineToDataHeader('  LOCAL PERS speeddata ' + cmd + ':=[' + str(int(speed * 1000)) + ',500,5000,1000];') 
         else:
            # up
            if self.ABBProfilesOutput: self.AddLineToDataHeader('  LOCAL PERS speeddata %s:=[7000,500,5000,%d];' % (cmd, int(speed*10)))

   def SetAccuracy(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Sets the motion accuracy based on the Accuracy event."""
      logger = operator.GetLogOperator()
      pathtype = ''
      accuracy = -1
      criteria = ''
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            accuracy = attribute.GetValue()
         if attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
         if attribute.GetName() == 'Criteria':
            criteria = attribute.GetValue()
      if criteria == 'On':
         self.CurrentAccuracyActive = True
         if accuracy > 0.0:
            if pathtype == 'Contour':
               self.CurrentLinAccuracy = int(accuracy * 1000)
               cmd  = 'uz' + str(int(accuracy * 1000))
               if self.CurrentLinAccuracy > 100:
                  logger.LogError('Linear motion accuracy out of range.')
                  self.CurrentLinAccuracy = 100
            else:
               self.CurrentPtpAccuracy = int(accuracy)
               cmd  = 'uz' + str(int(accuracy))
      elif criteria == 'Off':
         self.CurrentAccuracyActive = False
         self.CurrentLinAccuracy = 0.0
         cmd  = 'uz0'
      elif criteria == 'Distance':
         self.CurrentLinAccuracy = int(accuracy * 1000)
         cmd  = 'uz' + str(int(accuracy * 1000))
         if self.CurrentLinAccuracy > 100:
            logger.LogError('Linear motion accuracy out of range.')
            self.CurrentLinAccuracy = 100
         self.CurrentAccuracyActive = (accuracy > 0.0)
      elif criteria == 'JointDistance':
         self.CurrentPtpAccuracy = int(accuracy)
         self.CurrentAccuracyActive = (accuracy > 0.0)
         cmd  = 'uz' + str(int(accuracy))

      

      entryAlreadyExist = False

      for entry in self.DataSectionAccuracyProfiles:
         if entry == cmd:
            entryAlreadyExist = True
            break
         # check if motion profile already exists in the list
      if entryAlreadyExist == False:
         self.DataSectionAccuracyProfiles.append(cmd)
         # create motion profile string
         if self.ABBProfilesOutput: self.AddLineToDataHeader('  LOCAL PERS zonedata ' + cmd + ':=[FALSE,5,5,5,0.5,5,0.5];')

   def SetAcceleration(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Sets the acceleration based on the Acceleration event.

      In ABB, acceleration is not directly passed in the motion command,
      but it can be recorded in a comment or used later in calculations.
      """
      logger = operator.GetLogOperator()
      pathtype = ''
      acceleration = 0.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            acceleration = attribute.GetValue()
         elif attribute.GetName() == 'PathType':
            pathtype = attribute.GetValue()
      if pathtype == 'Contour':
         self.CurrentLinAcceleration = int(acceleration * 100)
         if self.CurrentLinAcceleration > 150:
            logger.LogError('Linear motion acceleration out of range.')
            self.CurrentLinAcceleration = 150
      else:
         self.CurrentPtpAcceleration = int(acceleration)
         if self.CurrentPtpAcceleration > 150:
            logger.LogError('Point-to-point motion acceleration out of range.')
            self.CurrentPtpAcceleration = 150

   def TextEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handles a text event – depending on whether it is a comment or a command."""
      attributes = event.GetAttributes()
      text = ''
      isComment = True
      for attribute in attributes:
         if attribute.GetName() == 'Text':
            text = attribute.GetValue()
         elif attribute.GetName() == 'IsComment':
            isComment = attribute.GetValue()
      if isComment:
         self.OutputABBComment(operator, text)
      else:
         self.AddLineToSource(text)

   def OutputABBComment(self, operator: DULPythonDownloadOperator, comment: str):
      """Adds a comment to the source section.

      If the comment is longer than the allowed number of characters,
      it is truncated.
      """
      logger = operator.GetLogOperator()
      if len(comment) > self.MaxCharComments:
         logger.LogInfo('Event comment is too long, it will be truncated: %s' % comment)
         comment = comment[:self.MaxCharComments]
      self.AddLineToSource('    ! %s' % comment)

   def OutputDwellEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent):
      """Handles the dwell event.

      In RAPID, we use the WAIT command.
      """
      logger = operator.GetLogOperator()
      timeVal = -1.0
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'Value':
            timeVal = attribute.GetValue()
      if timeVal == -1.0:
         logger.LogError("Failed to read the dwell event time.")
         self.AddLineToSource('  ! ERROR DWELL EVENT')
      else:
         self.AddLineToSource('  Wait %.3f sec' % timeVal)

   def LogicPortEvent(self, operator: DULPythonDownloadOperator, event):
      """Handles events related to digital signals.

      For setting a signal (SetSignal) or waiting (WaitForSignal)
      the appropriate RAPID commands are generated: SetDO or WaitDI.
      """
      logger = operator.GetLogOperator()
      eventType = ''
      signalName = ''
      signalAddress = ''
      signalNumber = 0
      signalValue = None
      attributes = event.GetAttributes()
      for attribute in attributes:
         if attribute.GetName() == 'EventType':
            eventType = attribute.GetValue()
         elif attribute.GetName() == 'SignalName':
            signalName = attribute.GetValue()
         elif attribute.GetName() == 'SignalAddress':
            signalAddress = attribute.GetValue()
            try:
               signalNumber = int(signalAddress[2:])
            except (ValueError, TypeError, IndexError):
               logger.LogError("Unable to process signal address: %s" % signalAddress)
               self.AddLineToSource('  ! ERROR converting signal address')
         elif attribute.GetName() == 'SignalValue':
            signalValue = attribute.GetValue()
      try:
         if isinstance(signalValue, bool):
            if eventType == 'CENE2SetSignal':
               self.OutputSetSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            elif eventType == 'CENE2WaitForSignal':
               self.OutputWaitForSignalBoolEvent(operator, signalName, signalNumber, signalValue)
            else:
               logger.LogInfo('Unsupported signal event type.')
               self.AddLineToSource('  ! EVENT TYPE NOT SUPPORTED')
            self.AddEmptyLineToSource()
      except Exception as ex:
         logger.LogError('Error handling logic port event: %s' % str(ex))

   def OutputSetSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool):
      """Generates a command to set a digital signal (SetDO) in RAPID."""
      self.OutputABBComment(operator, '#%s' % signalName)
      if signalValue:
         self.AddLineToSource('  SetDO do%d, %s' % (signalNumber, self.ABB_TRUE))
      else:
         self.AddLineToSource('  SetDO do%d, %s' % (signalNumber, self.ABB_FALSE))

   def OutputWaitForSignalBoolEvent(self, operator: DULPythonDownloadOperator, signalName: str, signalNumber: int, signalValue: bool):
      """Generates a command to wait for a digital signal (WaitDI) in RAPID."""
      self.OutputABBComment(operator, '#%s' % signalName)
      if signalValue:
         self.AddLineToSource('  WaitDI di%d, %s' % (signalNumber, self.ABB_TRUE))
      else:
         self.AddLineToSource('  WaitDI di%d, %s' % (signalNumber, self.ABB_FALSE))

#################### FRAME 3-POINT TOUCH SENSING (Frame3pConnect) ####################

   def HandleTouchPointCollisionEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Handle TouchPointCollisionEvent - track reference points for Frame3pConnect.
      
      For Frame3pConnect (TSConnectionType=3):
      - First collision event per FramePt defines the reference point (RefP1/2/3)
      - Motion position at collision = nominal SearchPoint
      - Track measurement counters for PrePDisp generation
      
      Note: Plugin generates Search_1D during motion processing for correct ordering.
      """
      logger = operator.GetLogOperator()
      
      # Get FramePt and TouchId from event attributes
      frame_pt = event.GetIntegerAttribute('FramePt', True).GetValue()
      touch_id = event.GetIntegerAttribute('TouchId', True).GetValue()
      
      if touch_id is None or frame_pt is None:
         # Not Frame3pConnect - standard TouchSensing
         logger.LogDebug(f"HandleTouchPointCollisionEvent: TouchId={touch_id}, FramePt={frame_pt} - skipping (not Frame3pConnect)")
         return
      
      logger.LogInfo(f"Frame3pConnect: Tracking TouchId={touch_id}, FramePt={frame_pt}")
      
      # Track the highest FramePt seen for this TouchId
      if not hasattr(self, '_frame3p_max_framept'):
         self._frame3p_max_framept = {}
      
      current_max = self._frame3p_max_framept.get(touch_id, 0)
      if frame_pt > current_max:
         self._frame3p_max_framept[touch_id] = frame_pt
         logger.LogDebug(f"Frame3pConnect: Updated max FramePt to {frame_pt} for TouchId {touch_id}")
      
      # Only set current_frame3p_touch_id if this is the LAST FramePt (3)
      # This ensures OperationEnd only emits assignments after the final touch operation
      if not hasattr(self, '_current_frame3p_touch_id'):
         self._current_frame3p_touch_id = None
      if frame_pt == 3:
         self._current_frame3p_touch_id = touch_id
         logger.LogDebug(f"Frame3pConnect: Setting current_frame3p_touch_id={touch_id} (FramePt=3, will emit in OperationEnd)")
      
      # Check if this is the FIRST collision for this FramePt - store reference point
      key = (touch_id, frame_pt)
      if key not in self._frame3p_refpoints:
         # First collision - store reference point
         ref_point = self._format_robtarget_from_motion(operator, motion)
         self._frame3p_refpoints[key] = {
            'robtarget': ref_point,
            'motion': motion
         }
         logger.LogDebug(f"Frame3pConnect: Stored RefP{frame_pt} for TouchId {touch_id}")
      
      # Increment measurement counter (used by plugin for PrePDisp logic)
      self._frame3p_measurement_counter[key] = self._frame3p_measurement_counter.get(key, 0) + 1

   def HandleConnectTouchProcessPointEvent(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent):
      """Handle ConnectTouchProcessPointEvent - emit PDispSet or OFrameChange based on TSConnectionType.
      
      Triggered at weld points to apply displacement correction:
      - OperationConnect: Emit PDispSet once before first weld
      - StartEndConnect: Emit PDispSet for each TouchId (start/end)
      - ShortestDistanceConnect: Emit PDispSet for each TouchId along path
      - Frame3pConnect: Emit assignments + OFrameChange
      """
      logger = operator.GetLogOperator()
      
      # Get TouchId from event
      attributes = event.GetAttributes()
      touch_id = None
      for attr in attributes:
         if attr.GetName() == 'TouchId':
            touch_id = int(attr.GetValue())
            break
      
      if touch_id is None:
         return
      
      # Use remembered TSConnectionType for this TouchId, or detect from current OperationGroup
      ts_conn_type = ""
      
      # First, check if we have a remembered mode for this TouchId
      if touch_id in self.shared.touchid_mode_map:
         ts_conn_type = self.shared.touchid_mode_map[touch_id]
         logger.LogDebug(f"ConnectTouchProcessPointEvent: Using remembered mode for TouchId={touch_id}: '{ts_conn_type}'")
      else:
         # Fallback: read from current OperationGroup (may be incorrect if GRP doesn't have touches)
         if self._current_operation_group is not None:
            try:
               ts_conn_type = self._current_operation_group.GetLiteralAttribute('TSConnectionType', True).GetValue()
            except Exception:
               pass
         logger.LogDebug(f"ConnectTouchProcessPointEvent: TSConnectionType from OperationGroup='{ts_conn_type}', TouchId={touch_id}")
      
      if touch_id == 0:
         # TouchId=0: Cancel displacement offset
         self._frame3p_active_touchid = None
         self.shared.frame3p_wobj_active = False
         self.shared.active_wobj_name = self.shared.station_wobj_name  # Revert to station wobj
         wobj_name = self.shared.station_wobj_name if self.shared.station_wobj_name else self.baseFrameName
         logger.LogInfo(f"TouchSensing: TouchId=0 detected, reverted to {wobj_name}")
         
         # Output PDispOff to cancel displacement
         self.AddLineToSource("    PDispOff;")
         return
      
      # Handle Frame3pConnect mode
      if ts_conn_type == "Frame3pConnect":
         # Check if we need to emit declarations or activation
         need_declarations = False
         need_activation_comment = False
         
         if self._frame3p_active_touchid != touch_id:
            # Different TouchId - need both declarations and activation
            need_declarations = True
            need_activation_comment = True
         elif not self.shared.frame3p_wobj_active:
            # Same TouchId but was deactivated - need activation comment
            need_activation_comment = True
         
         if need_declarations:
            # Emit PERS declarations first
            self._emit_frame3p_declarations(operator, touch_id)
         
         # Note: OFrameChange is emitted in OperationEnd after last touch completes
         
         if need_activation_comment or need_declarations:
            # Activate obNEW_<TouchId> for subsequent motions in StitchWelding operations
            self._frame3p_active_touchid = touch_id
            self.shared.frame3p_wobj_active = True
            self.shared.active_wobj_name = f'obNEW_{touch_id}'
            
            # Add activation comment
            self.AddLineToSource(f"    ! Activating TS Frame WObj: obNEW_{touch_id}")
            logger.LogInfo(f"Frame3pConnect: Activated obNEW_{touch_id} for StitchWelding operations")
         return
      
      # Handle displacement modes (OperationConnect, StartEndConnect, ShortestDistanceConnect)
      if ts_conn_type in ("OperationConnect", "StartEndConnect", "ShortestDistanceConnect"):
         # Displacement mode - clear Frame3P active state
         self.shared.frame3p_wobj_active = False
         self.shared.active_wobj_name = self.shared.station_wobj_name  # Revert to station wobj
         
         # Ensure declarations are emitted (may reference TouchId from different OperationGroup)
         if not hasattr(self, '_displacement_declared_touchids'):
            self._displacement_declared_touchids = set()
         
         if touch_id not in self._displacement_declared_touchids:
            # TouchId declarations not yet emitted - emit them now
            # Note: measurement count comes from plugin tracking during Search_1D generation
            self._emit_displacement_declarations(operator, touch_id, ts_conn_type)
         
         # Track which TouchIds have been activated
         if not hasattr(self, '_displacement_activated_touchids'):
            self._displacement_activated_touchids = set()
         
         # Emit PDispSet command (with reuse check)
         self._emit_pdisp_set(operator, touch_id, ts_conn_type)
         
         # Mark as activated
         self._displacement_activated_touchids.add(touch_id)
         return

   def _emit_search_1d_command(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, event: DULPythonEvent, touch_id: int, frame_pt: int):
      """Emit Search_1D command with proper PrePDisp handling.
      
      Supports both Implicit (named targets) and Explicit (inline robtargets) modes.
      """
      logger = operator.GetLogOperator()
      
      key = (touch_id, frame_pt)
      mea_count = self._frame3p_measurement_counter.get(key, 1)
      
      # Generate measurement variable name: tid<TouchId>_pt<FramePt>_mea<N>
      mea_var = f"tid{touch_id}_pt{frame_pt}_mea{mea_count}"
      
      # Get reference point (SearchPoint)
      ref_point_data = self._frame3p_refpoints.get(key)
      if not ref_point_data:
         logger.LogError(f"Frame3pConnect: No reference point found for TouchId {touch_id}, FramePt {frame_pt}")
         return
      
      # Get approach point (StartPoint)
      if self.ABBTargetOutputStyle == "Explicit":
         # Explicit mode: use inline robtargets
         # StartPoint comes from the approach motion (tracked in _frame3p_approach_point_ref)
         # But we need the actual robtarget data, not just the ref name
         # Use the motion that was tracked before this touch
         start_point = self._abb_get_explicit_target_for_motion(operator, motion, is_start_point=True)
         search_point = ref_point_data['robtarget']  # Already formatted as explicit robtarget
      else:
         # Implicit mode: use named robtarget references
         start_point = self._frame3p_approach_point_ref or "P_UNKNOWN"
         search_point = f"pRef{frame_pt}_{touch_id}"
      
      # Get speed from motion
      speed_token = self._abb_get_speed_token_for_motion(motion)
      
      # Build Search_1D command (4 spaces for PROC body)
      cmd = f"    Search_1D {mea_var}, {start_point}, {search_point}, {speed_token}, {self.ToolFrameName}\\WObj:={self._frame3p_active_wobj}"
      
      # Add PrePDisp if not first measurement
      if mea_count > 1:
         predisp_expr = self._build_predisp_expression(touch_id, frame_pt, mea_count)
         cmd += f"\\PrePDisp:={predisp_expr}"
      
      cmd += ";"
      self.AddLineToSource(cmd)
      
      logger.LogDebug(f"Frame3pConnect: Emitted {mea_var} for RefP{frame_pt}")

   def _build_predisp_expression(self, touch_id: int, frame_pt: int, current_mea: int) -> str:
      """Build PrePDisp expression for cumulative displacement.
      
      For mea2: tid1_pt1_mea1
      For mea3: PoseAdd(tid1_pt1_mea1, tid1_pt1_mea2)
      """
      if current_mea == 2:
         return f"tid{touch_id}_pt{frame_pt}_mea1"
      elif current_mea == 3:
         return f"PoseAdd(tid{touch_id}_pt{frame_pt}_mea1, tid{touch_id}_pt{frame_pt}_mea2)"
      else:
         return "UNKNOWN"

   def _emit_pdisp_set(self, operator: DULPythonDownloadOperator, touch_id: int, ts_conn_type: str):
      """Emit PDispSet command for displacement modes.
      
      OperationConnect: PDispSet peDisp1:=PoseAdd(...);
      StartEndConnect: PDispSet peDisp<N>:=PoseAdd(...); for each TouchId
      ShortestDistanceConnect: PDispSet peDisp<N>:=PoseAdd(...); for each TouchId
      
      Combines all measurements for the given TouchId.
      """
      logger = operator.GetLogOperator()
      
      # Remove tracking to allow PDispSet reuse for same TouchId
      # (No longer check _pdisp_emitted_touchids)
      
      # First emit PERS declarations for this TouchId if not already done
      self._emit_displacement_declarations(operator, touch_id, ts_conn_type)
      
      # Get measurement counter for this TouchId from the plugin that actually tracked it
      mea_count = 0
      for plugin in self._plugins.plugins:
         if isinstance(plugin, _ABBTouchSensingMixin):
            cnt = plugin._displacement_mea_counters.get(touch_id, 0)
            if cnt > 0:
               mea_count = cnt
               break
      
      if mea_count == 0:
         logger.LogWarn(f"TouchSensing: No measurements found for TouchId {touch_id}")
         return
      
      # The last touch wrote directly to peDisp<TouchId>, so just emit PDispSet
      # No need to build PoseAdd expression or assignment
      
      # Determine peDisp variable name based on TouchId (not connection type)
      # All displacement modes use peDisp<TouchId>
      pedisp_var = f"peDisp{touch_id}"
      
      # Emit PDispSet command (peDisp variable already contains final measurement)
      self.AddLineToSource(f"    PDispSet {pedisp_var};")
      
      logger.LogDebug(f"{ts_conn_type}: Emitted PDispSet {pedisp_var} for TouchId {touch_id}")

   def _emit_displacement_declarations(self, operator: DULPythonDownloadOperator, touch_id: int, ts_conn_type: str):
      """Emit module-level PERS declarations for displacement modes.
      
      Generates:
      - peDisp<N> displacement variables
      - tid<TouchId>_mea<N> measurement poses
      """
      logger = operator.GetLogOperator()
      
      # Track which TouchIds have been declared
      if not hasattr(self, '_displacement_declared_touchids'):
         self._displacement_declared_touchids = set()
      
      if touch_id in self._displacement_declared_touchids:
         return
      
      self._displacement_declared_touchids.add(touch_id)
      
      logger.LogDebug(f"{ts_conn_type}: Emitting PERS declarations for TouchId {touch_id}")
      
      # Emit peDisp<TouchId> variable (all displacement modes use TouchId-based naming)
      self.AddLineToDataHeader(f"  LOCAL PERS pose peDisp{touch_id} := [[0,0,0],[1,0,0,0]];")
      
      # Get measurement count from the plugin that actually tracked it
      mea_count = 0
      for plugin in self._plugins.plugins:
         if isinstance(plugin, _ABBTouchSensingMixin):
            cnt = plugin._displacement_mea_counters.get(touch_id, 0)
            if cnt > 0:
               mea_count = cnt
               break
      
      # Emit reusable measurement variables (shared across all TouchIds)
      # Last touch writes directly to peDisp<TouchId>, so only emit intermediate variables
      if not hasattr(self, '_displacement_mea_vars_declared'):
         self._displacement_mea_vars_declared = set()
      
      for i in range(1, mea_count):  # Note: range(1, mea_count) excludes last touch
         var_name = f"tid_mea{i}"
         if var_name not in self._displacement_mea_vars_declared:
            self.AddLineToDataHeader(f"  LOCAL PERS pose {var_name} := [[0,0,0],[1,0,0,0]];")
            self._displacement_mea_vars_declared.add(var_name)
      
      logger.LogDebug(f"{ts_conn_type}: Declared {mea_count-1} intermediate measurement variables for TouchId {touch_id}")

   def _emit_oframe_change(self, operator: DULPythonDownloadOperator, touch_id: int):
      """Emit OFrameChange call and PoseAdd combinations.
      
      Generates:
      - PoseAdd combinations for multi-touch reference points
      - OFrameChange function call
      - Switches active work object to obNEW_<TouchId>
      """
      logger = operator.GetLogOperator()
      
      # Get measurement counters from the plugin that actually tracked them
      mea_counters = {}
      for plugin in self._plugins.plugins:
         if isinstance(plugin, _ABBTouchSensingMixin) and getattr(plugin, '_frame3p_mea_counters', {}):
            mea_counters = plugin._frame3p_mea_counters
            if mea_counters:
               break
      
      # Build combined displacements
      refp1_key = (touch_id, 1)
      refp2_key = (touch_id, 2)
      refp3_key = (touch_id, 3)
      
      # Generate assignments to pMea1/2/3 - use only final measurement as it already includes previous displacements
      refp1_mea_count = mea_counters.get(refp1_key, 0)
      if refp1_mea_count == 1:
         self.AddLineToSource(f"    pMea1 := tid_pt1_mea1;")
      elif refp1_mea_count == 2:
         self.AddLineToSource(f"    pMea1 := tid_pt1_mea2;")
      elif refp1_mea_count == 3:
         self.AddLineToSource(f"    pMea1 := tid_pt1_mea3;")
      
      # Generate assignment for RefP2
      refp2_mea_count = mea_counters.get(refp2_key, 0)
      if refp2_mea_count == 1:
         self.AddLineToSource(f"    pMea2 := tid_pt2_mea1;")
      elif refp2_mea_count == 2:
         self.AddLineToSource(f"    pMea2 := tid_pt2_mea2;")
      
      # RefP3 handling (single touch or dummy)
      refp3_mea_count = mea_counters.get(refp3_key, 0)
      if refp3_mea_count == 1:
         self.AddLineToSource(f"    pMea3 := tid_pt3_mea1;")
      # else pMea3 remains identity (dummy RefP3)
      
      # Emit OFrameChange with reusable variable names
      base_wobj = self.shared.station_wobj_name if self.shared.station_wobj_name else self.baseFrameName
      cmd = f"    obNEW_{touch_id} := OFrameChange({base_wobj}, pRef1, pRef2, pRef3, pMea1, pMea2, pMea3);"
      self.AddLineToSource(cmd)
      
      logger.LogDebug(f"Frame3pConnect: Emitted OFrameChange for TouchId {touch_id}")
      
      logger.LogInfo(f"Frame3pConnect: Emitted OFrameChange for TouchId {touch_id}")

   def _format_robtarget_from_motion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion) -> str:
      """Format motion position as RAPID robtarget string."""
      # Get position object from motion
      position = motion.GetPosition()
      
      # Get XYZ and orientation (Euler angles)
      xyz = position.GetXYZ()
      rpy = position.GetOrientation()
      
      # Convert Euler angles to quaternion
      quat = self.euler_to_quaternion(rpy[0], rpy[1], rpy[2])
      
      # Get turn and config values
      turn_values = self.get_turn_value_from_xml(motion)
      config_abb = self.compute_config_from_turn(motion)
      
      # Get external axes
      extax = self.GetABBExternalAxes(position)
      
      # Format: [[X,Y,Z],[Q1,Q2,Q3,Q4],[CF1,CF4,CF6,CFx],[E1,E2,E3,E4,E5,E6]]
      return f"[[{xyz[0]*1000:.2f},{xyz[1]*1000:.2f},{xyz[2]*1000:.2f}],[{quat[0]:.6f},{quat[1]:.6f},{quat[2]:.6f},{quat[3]:.6f}],[{turn_values},{config_abb}],{extax}]"

   def _abb_get_explicit_target_for_motion(self, operator: DULPythonDownloadOperator, motion: DULPythonMotion, is_start_point: bool = False) -> str:
      """Get explicit robtarget string for a motion (for Explicit mode).
      
      For StartPoint, use the tracked approach motion.
      For SearchPoint, use the current motion.
      """
      if is_start_point and self._frame3p_approach_motion:
         return self._format_robtarget_from_motion(operator, self._frame3p_approach_motion)
      else:
         return self._format_robtarget_from_motion(operator, motion)

   def _emit_frame3p_declarations(self, operator: DULPythonDownloadOperator, touch_id: int):
      """Emit module-level PERS declarations for Frame3pConnect.
      
      Generates:
      - obNEW_<TouchId> work object
      - pRef1/2/3_<TouchId> reference robtargets
      - peDisp1/2/3_<TouchId> displacement poses
      - tid<TouchId>_pt<FramePt>_mea<N> measurement poses
      """
      logger = operator.GetLogOperator()
      
      # Check if already emitted
      if not hasattr(self, '_frame3p_declared_touchids'):
         self._frame3p_declared_touchids = set()
      
      if touch_id in self._frame3p_declared_touchids:
         return
      
      self._frame3p_declared_touchids.add(touch_id)
      
      logger.LogDebug(f"Frame3pConnect: Emitting PERS declarations for TouchId {touch_id}")
      
      # Work object - unique per TouchId
      self.AddLineToDataHeader(f"  LOCAL PERS wobjdata obNEW_{touch_id} := [FALSE, FALSE, \"STN{self._station_active_index}\", [[0,0,0],[1,0,0,0]], [[0,0,0],[1,0,0,0]]];")
      
      # Reference points - reusable (no TouchId suffix)
      if not hasattr(self, '_frame3p_ref_vars_declared'):
         self._frame3p_ref_vars_declared = False
      
      if not self._frame3p_ref_vars_declared:
         refp1_key = (touch_id, 1)
         refp2_key = (touch_id, 2)
         refp3_key = (touch_id, 3)
         
         if refp1_key in self._frame3p_refpoints:
            refp1_str = self._frame3p_refpoints[refp1_key]['robtarget']
            self.AddLineToDataHeader(f"  LOCAL PERS robtarget pRef1 := {refp1_str};")
         
         if refp2_key in self._frame3p_refpoints:
            refp2_str = self._frame3p_refpoints[refp2_key]['robtarget']
            self.AddLineToDataHeader(f"  LOCAL PERS robtarget pRef2 := {refp2_str};")
         
         # RefP3: actual touch or dummy calculation
         if refp3_key in self._frame3p_refpoints:
            refp3_str = self._frame3p_refpoints[refp3_key]['robtarget']
            self.AddLineToDataHeader(f"  LOCAL PERS robtarget pRef3 := {refp3_str};")
         else:
            # Calculate dummy RefP3
            refp3_str = self._calculate_dummy_refp3(operator, touch_id)
            self.AddLineToDataHeader(f"  LOCAL PERS robtarget pRef3 := {refp3_str};")
         
         # Intermediate result variables - reusable (pMea1/2/3)
         self.AddLineToDataHeader(f"  LOCAL PERS pose pMea1 := [[0,0,0],[1,0,0,0]];")
         self.AddLineToDataHeader(f"  LOCAL PERS pose pMea2 := [[0,0,0],[1,0,0,0]];")
         self.AddLineToDataHeader(f"  LOCAL PERS pose pMea3 := [[0,0,0],[1,0,0,0]];")
         
         self._frame3p_ref_vars_declared = True
      
      # Individual touch measurement variables - get counts from the plugin that tracked them
      mea_counters = {}
      for plugin in self._plugins.plugins:
         if isinstance(plugin, _ABBTouchSensingMixin) and getattr(plugin, '_frame3p_mea_counters', {}):
            mea_counters = plugin._frame3p_mea_counters
            if mea_counters:
               break
      
      # Emit reusable measurement variables (shared across all TouchIds)
      if not hasattr(self, '_frame3p_measurement_vars_declared'):
         self._frame3p_measurement_vars_declared = set()
      
      # Emit measurement variables for each FramePt that was used
      for frame_pt in [1, 2, 3]:
         key = (touch_id, frame_pt)
         mea_count = mea_counters.get(key, 0)
         for i in range(1, mea_count + 1):
            var_name = f"tid_pt{frame_pt}_mea{i}"
            if var_name not in self._frame3p_measurement_vars_declared:
               self.AddLineToDataHeader(f"  LOCAL PERS pose {var_name} := [[0,0,0],[1,0,0,0]];")
               self._frame3p_measurement_vars_declared.add(var_name)
      
      self.AddLineToDataHeader("")
      
      refp1_count = mea_counters.get((touch_id, 1), 0)
      refp2_count = mea_counters.get((touch_id, 2), 0)
      refp3_count = mea_counters.get((touch_id, 3), 0)
      logger.LogDebug(f"Frame3pConnect: Declared RefP1={refp1_count}, RefP2={refp2_count}, RefP3={refp3_count} measurements")

   def _calculate_dummy_refp3(self, operator: DULPythonDownloadOperator, touch_id: int) -> str:
      """Calculate dummy RefP3 when FramePt=3 not present.
      
      Algorithm:
      1. V_seam = normalize(RefP2 - RefP1)
      2. V_z = [0, 0, 1] in work object frame
      3. V_perp = normalize(cross(V_seam, V_z))
      4. RefP3 = RefP1 + V_perp * 2000.0
      
      Returns: robtarget string format
      """
      import math
      logger = operator.GetLogOperator()
      
      refp1_key = (touch_id, 1)
      refp2_key = (touch_id, 2)
      
      if refp1_key not in self._frame3p_refpoints or refp2_key not in self._frame3p_refpoints:
         logger.LogError(f"Frame3pConnect: Cannot calculate dummy RefP3 - missing RefP1 or RefP2 for TouchId {touch_id}")
         return "[[0,0,0],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]"
      
      # Parse RefP1 and RefP2 positions (simple extraction from stored motion)
      refp1_motion = self._frame3p_refpoints[refp1_key]['motion']
      refp2_motion = self._frame3p_refpoints[refp2_key]['motion']
      
      p1 = refp1_motion.GetPosition()
      p2 = refp2_motion.GetPosition()
      
      # Get XYZ coordinates (in meters, E2 units)
      p1_xyz = p1.GetXYZ()
      p2_xyz = p2.GetXYZ()
      
      # Seam direction vector
      v_seam_x = p2_xyz[0] - p1_xyz[0]
      v_seam_y = p2_xyz[1] - p1_xyz[1]
      v_seam_z = p2_xyz[2] - p1_xyz[2]
      
      seam_length = math.sqrt(v_seam_x**2 + v_seam_y**2 + v_seam_z**2)
      if seam_length < 0.010:  # RefP1 and RefP2 too close (10mm)
         logger.LogWarn(f"Frame3pConnect: RefP1 and RefP2 are very close ({seam_length*1000:.2f}mm) for TouchId {touch_id}")
         seam_length = max(seam_length, 0.001)  # Avoid division by zero
      
      v_seam_x /= seam_length
      v_seam_y /= seam_length
      v_seam_z /= seam_length
      
      # Work object Z-axis (assuming obREF is world frame, Z = [0,0,1])
      v_z_x, v_z_y, v_z_z = 0.0, 0.0, 1.0
      
      # Perpendicular direction: cross(v_seam, v_z)
      v_perp_x = v_seam_y * v_z_z - v_seam_z * v_z_y
      v_perp_y = v_seam_z * v_z_x - v_seam_x * v_z_z
      v_perp_z = v_seam_x * v_z_y - v_seam_y * v_z_x
      
      perp_length = math.sqrt(v_perp_x**2 + v_perp_y**2 + v_perp_z**2)
      if perp_length < 0.001:  # Seam is vertical (parallel to Z)
         logger.LogWarn(f"Frame3pConnect: Seam is nearly vertical for TouchId {touch_id}, using default perpendicular")
         v_perp_x, v_perp_y, v_perp_z = 1.0, 0.0, 0.0
      else:
         v_perp_x /= perp_length
         v_perp_y /= perp_length
         v_perp_z /= perp_length
      
      # RefP3 at 2000mm perpendicular to seam (2.0m in E2 units)
      dummy_offset = 2.0  # meters
      p3_x = p1_xyz[0] + v_perp_x * dummy_offset
      p3_y = p1_xyz[1] + v_perp_y * dummy_offset
      p3_z = p1_xyz[2] + v_perp_z * dummy_offset
      
      # Convert to mm for RAPID output
      p3_x_mm = p3_x * 1000.0
      p3_y_mm = p3_y * 1000.0
      p3_z_mm = p3_z * 1000.0
      
      # Use RefP1's orientation and config
      refp1_str = self._frame3p_refpoints[refp1_key]['robtarget']
      # Extract orientation and config from RefP1 string (simple parse)
      # Format: [[X,Y,Z],[Q1,Q2,Q3,Q4],[CF1,CF4,CF6,CFx],[E1,E2,E3,E4,E5,E6]]
      import re
      match = re.search(r'\[\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\]\]', refp1_str)
      if match:
         quat_str = match.group(2)
         cf_str = match.group(3)
         ext_str = match.group(4)
         refp3_str = f"[[{p3_x_mm:.2f},{p3_y_mm:.2f},{p3_z_mm:.2f}],[{quat_str}],[{cf_str}],[{ext_str}]]"
      else:
         # Fallback
         refp3_str = f"[[{p3_x_mm:.2f},{p3_y_mm:.2f},{p3_z_mm:.2f}],[1,0,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]"
      
      logger.LogDebug(f"Frame3pConnect: Calculated dummy RefP3 at ({p3_x_mm:.2f},{p3_y_mm:.2f},{p3_z_mm:.2f}) for TouchId {touch_id}")
      return refp3_str

#################### HELPER FUNCTIONS ####################

   def CreateHeader(self, operator: DULPythonDownloadOperator):
      ''' Creates the RAPID program header.

      In this function, program metadata such as date, time, and file name are set.
      '''
      #self.AddLineToHeader('! ABB RAPID Program generated by Cenit')
      #self.AddLineToHeader('! Program: %s' % self.ProgramName)
      now = datetime.now()
      dateStr = now.strftime("%d-%m-%y")
      timeStr = now.strftime("%H:%M:%S")
      #self.AddLineToHeader('! Created: DATE %s TIME %s' % (dateStr, timeStr))
      #self.AddLineToHeader('! Created by: Mulewski Dariusz')
      #self.AddLineToHeader('')

   def HandleMotionProfiles(self, operator: DULPythonDownloadOperator, activeProgram: DULPythonProgram):
      controller = operator.GetController()
      acProgram = controller.GetActiveProgram()
      opgs = acProgram.GetOperationGroups()
      for opg in opgs:
         ops = opg.GetOperations()
         for op in ops:
            motions = op.GetMotions()
            for motion in motions:
               eventsBefore = motion.GetEventsBefore()
               eventsAfter = motion.GetEventsAfter()

   def CheckAndUpdateBaseFrame(self, operator: DULPythonDownloadOperator, logger, index: int, name: str):
      """Checks if the base frame index is within the allowed range and generates the corresponding line in the code.

      If the index has changed, generates a comment and command indicating the change of reference frame.
      """
      if self.CurrentBaseFrameIndex != index:
         if self.RangeCheck(index, self.BaseFrameMinIndex, self.BaseFrameMaxIndex):
            self.CurrentBaseFrameIndex = index
            self.baseFrameName = name
            self.OutputABBComment(operator, 'BF: %s' % name)
            self.AddLineToData('  LOCAL PERS wobjdata B%d:=[FALSE,TRUE,"",[[-698.157,-1075.81,821.023],[0.707107,0,0,0.707107]],[[0,0,0],[1,0,0,0]]];' % (index))
         else:
            self.AddLineToSource('  ! UFRAME OUT_OF_RANGE')
            logger.LogError('Base frame index out of range')

   def CheckAndUpdateToolFrame(self, operator: DULPythonDownloadOperator, logger, index: int, name: str):
      """Checks if the tool frame index is within the allowed range and generates the corresponding line in the code."""
      if self.CurrentToolFrameIndex != index:
         if self.RangeCheck(index, self.ToolFrameMinIndex, self.ToolFrameMaxIndex):
            self.CurrentToolFrameIndex = index
            self.OutputABBComment(operator, 'TF: %s' % name)
            self.AddLineToData('  LOCAL PERS tooldata T%d:=[TRUE,[[3.732,0,364.681],[0.952938,0,0.303164,0]],[0.1,[0,0,0.1],[1,0,0,0],0,0,0.1]];' % (index))
         else:
            self.AddLineToSource('  ! UTOOL OUT_OF_RANGE')
            logger.LogError('Tool frame index out of range')

   def CheckPointCommentLength(self, pointName: str):
      """Shortens the point name to a maximum of 16 characters, adding a colon at the beginning."""
      return ':' + pointName[:self.MaxCharComments]

   def RangeCheck(self, value, minVal, maxVal):
      """Checks if the value is within the specified range."""
      try:
         if value < minVal or value > maxVal:
            return False
         return True
      except (TypeError, ValueError):
         return None

   def AddLineToHeader(self, newline: str):
      """Adds a line to the header section."""
      self.Header.append(newline)

   def AddLineToSourceHeader(self, newline: str):
      """Adds a line to the source header section (e.g., PROC declaration)."""
      self.SourceHeader.append(newline)

   def AddLineToSource(self, newline: str):
      """Adds a line to the command section (source)."""
      self.Source.append(newline)

   def AddEmptyLineToSource(self):
      """Adds a blank line to the source section."""
      self.AddLineToSource('')

   def AddLineToDataHeader(self, newline: str):
      """Adds a line to the data header section."""
      self.DataHeader.append(newline)

   def AddLineToData(self, newline: str):
      """Adds a line to the data section."""
      self.Data.append(newline)

   def AddLineToFooter(self, newline: str):
      """Adds a line to the program footer."""
      self.Footer.append(newline)

   def GetOutputDirectory(self, operator: DULPythonDownloadOperator):
      """Returns the path to the output directory."""
      controller = operator.GetController()
      return controller.GetOutputDirectory()

   def GetActiveProgramName(self, operator: DULPythonDownloadOperator):
      """Returns the name of the active program."""
      controller = operator.GetController()
      program = controller.GetActiveProgram()
      return program.GetName()

   def get_turn_value_from_xml(self,motion: DULPythonMotion):
      """Retrieves Turn values from motion"""
      #turnValues = [0, 0, 0, 0]  # Default values if not found in XML
      # Add code here to retrieve the Turn values from the XML file
      return str(motion.GetPosition().GetTurn())

   def compute_config_from_turn(self, motion: DULPythonMotion):
      try:
         raw = motion.GetPosition().GetConfig()
         if isinstance(raw, int):
            return str(raw)
         s = str(raw).strip()
         match = re.search(r'-?\d+', s)
         if match:
            return str(int(match.group()))
         return '0'
      except Exception:
         return '0'