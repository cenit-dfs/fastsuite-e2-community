"""
COPYRIGHT Cenit AG Q3/2024
   Production ready KUKA Arc Welding downloader

   This downloader* SUPPORTs:
      Base arc commands like arc on/off:           YES
      touch sensing with wire:                     YES
      wire check for touch with wire:              NO
      touch sensing with nozzle:                   YES
      seam search in surface direction:            NO
      seam finding:                                NO
      seam tracking:                               YES
      arc sensing:                                 YES

      *this downloader only supports the mentioned functions above.
      It is possible, that the user is able to program more functionalities
"""

from __future__ import annotations
import sys, inspect, os, json
sys.dont_write_bytecode = True
sys.path.append(str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from enum import Enum
from datetime import datetime
from cenpylib import FileUtility
from cenpydownload import *
from cenpyolpcore import *
from centypes import *
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple, Callable
from collections import namedtuple
import importlib
import re
import math
import numpy as np
from pathlib import Path
import logging

RECIPES_FILENAME = "SeamFind_Recipes.json"
PROFILES_FILENAME = "SeamFind_Sensor_Profiles.json"

Pair = Tuple[str, str]

def ensure_module_is_updated(module_name):
      if module_name in sys.modules:
         importlib.reload(sys.modules[module_name])
      else:
         importlib.import_module(module_name)

# import base class and define class name of the current download
ensure_module_is_updated('KUKA_KRC5') #  <---- Perform module force-reload in order to apply hot changes

@dataclass
class ArcTech():
   # Add global Tech class attributes
   PowerSource:str = ''
   PowerSourceJobChannel = 0
   ArcTechVersionSRC = '3.5.4'
   ArcTechVersionDAT = ''
   ArcTechAdvVersionSRC = '3.5.4'
   ArcTechAdvVersionDAT = ''
   ArcTechSenseVersionSRC = '3.5.1'
   ArcTechSenseVersionDAT = ''
   SeamTechFindingVersionSRC = '4.0.3'
   SeamTechFindingVersionDAT = ''
   SeamTechTrackingVersionSRC = '4.0.3'
   SeamTechTrackingVersionDAT = ''
   TouchSenseVersionSRC = '3.8.1'
   TouchSenseVersionDAT = ''
   SingleWDat:bool = False
   AddWDatIndex:bool = False
   ArcTechAdv:bool = False
   WeaveType:str = ''
   # ArcTech event attributes
   # ArcTech flags, lists and counters
   ArcOnFlag:bool = False
   ArcSwitchFlag:bool = False
   TrackArcSense:bool = False
   CadMastered:bool = False
   ArcOffFlag:bool = False
   WDat:list = field(default_factory=list)
   WDatIndex:int = 0
   ArcOnInfos:list = field(default_factory=list)
   ArcIgnitionInfos:list = field(default_factory=list)
   ArcOffInfos:list = field(default_factory=list)
   #SeamFind flags, lists and counters
   SeamFindFlag:bool = False
   SeamFindFirstOp:bool = True
   SeamFindArcSpot:bool = False # SeamFindArcSpot workaround for ArcSpot operation
   SeamFindId:int = 0
   SeamFindSpeed:float = 0.0
   SeamFindCounter:int = 0
   SeamFindOpsInGroupCounter:int = 0
   SeamTrackFlag:bool = False
   SeamTrackFirstOp:bool = True
   FindFrameCounter:int = 0
   FindFrameCounterCurrent:int = -99
   FindFramePointCounter:int = 0
   FindFramePointCounterCurrent:int = -99
   FindMeaCounter:int = 0
   FindFramePointMeaCounter:int = 0
   TotalMeaCounter:int = 0
   FramePosName:str = ''
   OutputSeamTrackSearchStart:bool = False
   SeamTrackSearchSpeed:float = 0.01
   OutputSeamTrackStartFooterWritten:bool = False

#ArcTech event attributes filled by JSON string. The structure of those classes have to match the JSON string structure exactly!!!
@dataclass
class ArcIgnInfo():
   KukaArcSwitch: bool = False
   KukaIgnitionProgNumber: int = 0
   KukaIgnitionParmSet: str = '0'
   KukaPreflowTime: float = 0.0
   KukaOnTheFlyActive: bool = False
   KukaOnTheFlyGasPreflowTime: float = 0.0
   KukaWaitTimeAfterIgnition: float = 0.0
   KukaRuleEvent: bool = False

@dataclass
class ArcOnInfo():
   KukaProgNumber: int = 0
   KukaWeldParmSet: str = '0'
   KukaRobotVelocity1: float = 0.0
   KukaWeavePattern: str = ''
   KukaWeavePatternIndex: int = 0
   KukaWeavePatternList: list = field(default_factory=list)
   KukaWeaveLength: float = 0.0
   KukaWeaveFrequency: float = 0.0
   KukaWeaveDeflection: float = 0.0
   KukaWeaveAngle: float = 0.0

@dataclass
class ArcSenseInfo():
   KukaArcSense: bool = False
   KukaArcSensePattern: str = ''
   KukaArcSensePatternIndex: int = 0
   KukaArcSensePatternList: list = field(default_factory=list)
   KukaArcSenseLatCtrlGain: float = 0.0
   KukaArcSenseHeightCtrl: float = 0.0
   KukaArcSenseLatBias: float = 0.0
   KukaArcSenseMaxCorr: float = 0.0
   KukaArcSenseFindCenter: bool = False
   KukaArcSenseActivDelay: float = 0.0

@dataclass
class ArcOffInfo():
   KukaArcOffJobNumber: int = 0
   KukaArcOffParmSet: str = '0'
   KukaEndCraterTime: float = 0.0
   KukaPostFlowTime: float = 0.0
   KukaRuleEvent: bool = False

@dataclass
class TouchInfo():
   TouchInit: bool = False
   TouchGroupInit: bool = False
   TouchConnectionType: str = ''  # OperationConnect, StartEndConnect, ShortestDistanceConnect, Frame3pConnect
   TouchStartName: str = ''
   TouchStartPosition: list = field(default_factory=list)
   TouchUUID: str = ''
   TouchCorrectionId: str = ''
   TouchLinkedFlag: bool = False
   TouchLinkedCounter: int = 0
   TouchRecord: List[TouchRecord] = field(default_factory=list)
   TouchSets: List[SeamTouchSet] = field(default_factory=list)
   TouchCollName: str = ''
   TouchEndName: str = ''
   TouchOpCounter: int = 0
   TouchOpsForCurrentFrame: int = 0
   TouchCorrFrameIdList: list = field(default_factory=list)
   TouchCorrFrameName: str = ''
   MotionTypeToStart: str = '' # LIN or PTP
   CorrBaseIndex:int = 0
   CorrBaseName:str = ''
   UsedFramePosNames:list = field(default_factory=list)
   SensorToolType: str = ''
   SensorId: int = 0
   TouchSensAsSeamFind:bool = False # SeamFind operation due to "Line Laser"
   SeamFindingMountType: int = 1
   SeamFindingRecipe: int = 1
   SeamFindingId: int = 1
   SeamFindJsonFolder: str = ''

@dataclass
class SeamFindGenerator:
    """
    Build a fully-resolved KUKA SeamFind ILF block (header + ;Params + BF_BC6DCalc + BF_CorrSave)
    using a Recipe, a Sensor Profile, a SaveIndex, a JSON folder and the global ATTR counters.

    Constructor (backward compatible):
        SeamFindGenerator(recipe_sel, profile_sel, save_index, json_folder, total_mea_counter, group_scan_count=None)

    Parameters:
        recipe_sel:            Name or 1-based index of the recipe (as in SeamFind_Recipes.json)
        profile_sel:           Sensor profile name or 1-based index (as in SeamFind_Sensor_Profiles.json)
        save_index:            SaveIndex used in BF_CorrSave / CorrLoad
        json_folder:           Folder containing the two JSON files
        total_mea_counter:     **LAST** ATTR index of the current group (NOT the first)
        group_scan_count:      Optional override for number of scans in this group (e.g. TouchOpsForCurrentFrame).
                               If None, defaults to the recipe's scan_ops length.

    Attributes after build init:
        first_attr_index:  First ATTR index of the current group (computed)
        last_attr_index:   Last  ATTR index of the current group (= total_mea_counter)
        next_counter:      Alias of last_attr_index (preserves backward compatibility; you can set it to
                           a new value externally when chaining groups if you need the next group's last index).
    """
    def __init__(
        self,
        recipe_sel: str,
        profile_sel: str,
        save_index: int,
        json_folder: str,
        tech_tab_folder,
        total_mea_counter: int,
        group_scan_count: Optional[int] = None,
        seamfind_version: str = '400000000'
    ) -> None:
        self.recipe_sel = recipe_sel
        self.profile_sel = profile_sel
        self.save_index = int(save_index)
        self.json_dir = Path(json_folder) if json_folder else Path.cwd()
        self.json_dir = Path(os.path.dirname(tech_tab_folder))
        self.last_attr_index = int(total_mea_counter)  # now interpreted as LAST scan index of the group
        self.seamfind_version = seamfind_version

        # Load data
        self.recipes = self._load_json(self.json_dir / RECIPES_FILENAME)
        profiles_root = self._load_json(self.json_dir / PROFILES_FILENAME)
        self.profiles = profiles_root["profiles"]

        # Resolve selections
        self.recipe = self._select_by_name_or_index(self.recipes, self.recipe_sel)
        self.profile = self._select_by_name_or_index(self.profiles, self.profile_sel)

        # Determine scan count
        recipe_scan_ops: List[str] = self.recipe.get("scan_ops", [])
        self.n_scans: int = int(group_scan_count) if group_scan_count is not None else len(recipe_scan_ops)
        if self.n_scans <= 0:
            raise ValueError("group_scan_count determined as 0; recipe must declare at least 1 scan or pass override.")

        # Compute first ATTR index of this group from last index + count
        self.first_attr_index: int = self.last_attr_index - self.n_scans + 1
        if self.first_attr_index < 1:
            raise ValueError(f"Computed first_attr_index={self.first_attr_index} < 1. "
                             f"Check total_mea_counter={self.last_attr_index} and group_scan_count={self.n_scans}.")

        # Build logical→real ATTR map for this group
        # logical ATTR1..ATTRn → real ATTR{first_attr_index..last_attr_index}
        self.attr_map: Dict[str, str] = {
            f"ATTR{i+1}": f"ATTR{self.first_attr_index + i}"
            for i in range(self.n_scans)
        }

        # Keep a compatibility alias (previously used as "counter after reserving this group's ATTRs")
        # With "last index" semantics, this equals last_attr_index.
        self.next_counter: int = self.last_attr_index

    # ---------------- utils ----------------
    @staticmethod
    def _load_json(path: Path):
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _select_by_name_or_index(items: List[dict], sel: str) -> dict:
        """sel may be a human-readable name or a 1-based index string/int"""
        # try index
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(items):
                raise IndexError
            return items[idx]
        except Exception:
            pass
        # try name
        for it in items:
            if it.get("name") == sel:
                return it
        raise ValueError(f"Selection not found: {sel}")

    @staticmethod
    def _cd_letter_to_num(cd: str) -> Optional[int]:
        m = re.fullmatch(r"CD([a-dhvA-DHV])", str(cd).strip())
        if not m:
            return None
        return {"a":1, "b":2, "c":3, "d":4, "v":1, "h":3}[m.group(1).lower()]

    # ---------------- core build ----------------
    def build(self) -> str:
        """Return the fully-resolved ILF block as string."""
        p = self.recipe["ilf_params"]

        # Resolve ATTR labels with the group's mapping
        XCorr = self._resolve_attr(p.get("XCorre","EMPTY"))
        YCorr = self._resolve_attr(p.get("YCorr","EMPTY"))
        ZCorr = self._resolve_attr(p.get("ZCorr","EMPTY"))
        Y2Corr= self._resolve_attr(p.get("Y2Corr","EMPTY"))
        Z2Corr= self._resolve_attr(p.get("Z2Corr","EMPTY"))
        Z3Corr= self._resolve_attr(p.get("Z3Corr","EMPTY"))

        # Resolve generic channel tokens <ALONG>/<LATERAL>/<HEIGHT> with profile CD*
        Xcd  = self._apply_profile_token(p.get("XcdParam","EMPTY"))
        Ycd  = self._apply_profile_token(p.get("YcdParam","EMPTY"))
        Zcd  = self._apply_profile_token(p.get("ZcdParam","EMPTY"))
        Y2cd = self._apply_profile_token(p.get("Y2cdParam","EMPTY"))
        Z2cd = self._apply_profile_token(p.get("Z2cdParam","EMPTY"))
        Z3cd = self._apply_profile_token(p.get("Z3cdParam","EMPTY"))

        # Build header with actual ATTRn and CD* letters
        header = self._build_header(
            x_pair=None if XCorr=="EMPTY" or Xcd=="EMPTY" else (XCorr, Xcd),
            y_pairs=self._pairs_non_empty([(YCorr,Ycd), (Y2Corr,Y2cd)]),
            z_triple=self._pairs_non_empty([(ZCorr,Zcd), (Z2Corr,Z2cd), (Z3Corr,Z3cd)]),
        )

        # Build params line
        if self.seamfind_version < '400000000':
           ilf_provider = "SeamFind.CorrUniversal"
        else:
           ilf_provider = "SeamFind.CorrCalcAndOn;SeamFind.CorrType=FREE"

        params = (
            f"IlfProvider={ilf_provider};"
            f"SeamFind.XCorre={XCorr};SeamFind.XcdParam={Xcd};"
            f"SeamFind.YCorr={YCorr};SeamFind.YcdParam={Ycd};"
            f"SeamFind.ZCorr={ZCorr};SeamFind.ZcdParam={Zcd};"
            f"SeamFind.Y2Corr={Y2Corr};SeamFind.Y2cdParam={Y2cd};"
            f"SeamFind.Z2Corr={Z2Corr};SeamFind.Z2cdParam={Z2cd};"
            f"SeamFind.Z3Corr={Z3Corr};SeamFind.Z3cdParam={Z3cd};"
            f"SeamFind.SaveIndex={self.save_index}"
        )

        # Build BF_BC6DCalc(Z1, Z2, Z3, Y1, Y2, reserved) with BFATTRn_CDk
        x1 = self._bf_arg(XCorr, Xcd)
        z1 = self._bf_arg(ZCorr, Zcd)
        z2 = self._bf_arg(Z2Corr, Z2cd)
        z3 = self._bf_arg(Z3Corr, Z3cd)
        y1 = self._bf_arg(YCorr, Ycd)
        y2 = self._bf_arg(Y2Corr, Y2cd)
        bf = f"BF_BC6DCalc({z1}, {z2}, {z3}, {y1}, {y2}, {x1})"
      #   bf = f"BF_BC6DCalc({z1}, {z2}, {z3}, {y1}, {y2}, BFg_PColl0_CD)"
        if self.seamfind_version < '400000000':
            free_str = 'ABC'
        else:
            free_str = 'FREE'
        block = (
            f";FOLD SeamFind Corr {free_str} {header} Save [{self.save_index}]:   ;%{{PE}}\n"
            f"  ;FOLD Parameters Parameters ;%{{h}}\n"
            f"    ;Params {params}\n"
            f"  ;ENDFOLD\n"
            f"  {bf}\n"
            f"  BF_CorrSave({self.save_index}, \" \")\n"
            f";ENDFOLD\n\n"

            f";FOLD SeamFind Corr Load [{self.save_index}]:   and On ;%{{PE}}\n"
            f"  ;FOLD Parameters Parameters ;%{{h}}\n"
            f"    ;Params IlfProvider=SeamFind.CorrLoadAndOn;SeamFind.LoadIndex={self.save_index}\n"
            f"  ;ENDFOLD\n"
            f"  BF_CorrLoadAndOn({self.save_index})\n"
            f";ENDFOLD\n"
        )
        return block

    # ---------------- helpers ----------------
    def _resolve_attr(self, logical: str) -> str:
        if logical in (None, "EMPTY"):
            return "EMPTY"
        return self.attr_map.get(logical, logical)

    def _apply_profile_token(self, val: str) -> str:
        if val in (None, "EMPTY"):
            return "EMPTY"
        out = str(val)
        for k in ("ALONG","LATERAL","HEIGHT"):
            out = out.replace(f"<{k}>", self.profile[k])
        return out

    def _bf_arg(self, attr_label: str, cd_letter: str) -> str:
        """Return BFATTRn_CDk or BFg_PColl0_CD if empty/unknown."""
        if attr_label in (None, "EMPTY") or cd_letter in (None, "EMPTY"):
            return "BFg_PColl0_CD"
        idx = self._cd_letter_to_num(cd_letter)
        if not idx:
            return "BFg_PColl0_CD"
        return f"BF{attr_label}_CD{idx}"

    @staticmethod
    def _pairs_non_empty(pairs: List[Pair]) -> List[Pair]:
        out: List[Pair] = []
        for a, b in pairs:
            if a != "EMPTY" and b != "EMPTY":
                out.append((a,b))
        return out

    @staticmethod
    def _fmt_pair(pair: Optional[Pair]) -> str:
        if not pair or pair[0] == "EMPTY" or pair[1] == "EMPTY":
            return "."
        return f"{pair[0]}.{pair[1]}"

    def _build_header(self, x_pair: Optional[Pair], y_pairs: List[Pair], z_triple: List[Pair]) -> str:
        if self.seamfind_version < '400000000':
            x_str = f"1:{self._fmt_pair(x_pair)}" if x_pair else ". "
            y1 = f"1:{self._fmt_pair(y_pairs[0])}" if len(y_pairs) >= 1 else "1:. "
            y2 = f"2:{self._fmt_pair(y_pairs[1])}" if len(y_pairs) >= 2 else "2:. "
            z1 = f"1:{self._fmt_pair(z_triple[0])}" if len(z_triple) >= 1 else "1:. "
            z2 = f"2:{self._fmt_pair(z_triple[1])}" if len(z_triple) >= 2 else "2:. "
            z3 = f"3:{self._fmt_pair(z_triple[2])}" if len(z_triple) >= 3 else "3:. "
            return f"X:( {x_str}) Y-A:({y1} {y2}) Z-BC:({z1}  {z2}  {z3})"
        else:
            x_str = f"{self._fmt_pair(x_pair)}" if x_pair else ". "
            y1 = f"{self._fmt_pair(y_pairs[0])}" if len(y_pairs) >= 1 else ". "
            y2 = f"{self._fmt_pair(y_pairs[1])}" if len(y_pairs) >= 2 else ". "
            z1 = f"{self._fmt_pair(z_triple[0])}" if len(z_triple) >= 1 else ". "
            z2 = f"{self._fmt_pair(z_triple[1])}" if len(z_triple) >= 2 else ". "
            z3 = f"{self._fmt_pair(z_triple[2])}" if len(z_triple) >= 3 else ". "
            return f"{{{x_str}}} {{{y1},{y2}}} {{{z1},{z2},{z3}}}"

# touch_router.py =============================================================
log = logging.getLogger(__name__)

# --------------------------- constants & types -------------------------------

TSG_CD0 = "TSg_CD0"
ANGLE_THRESH_DEG = 30.0  # for clustering when needed
Bucket = Literal["X", "Y", "Z"]

# ----------------------------- data models -----------------------------------

@dataclass
class TouchRecord:
    touch_corr_id: str                      # <-- the key for SeamTouchSet
    uuid: str
    touch_identifier: str                   # bare id, e.g. "TS2M3"
    symbol: str                             # e.g. "VCDTS2M1" -> exact KRL var to pass
    start_xyz: Tuple[float, float, float]   # BASE
    collision_xyz: Tuple[float, float, float]  # BASE
    linked: bool = False                    # for progressive 1D/2D/3D
    link_seq: Optional[int] = None          # 1,2,3
    weight: float = 1.0                     # quality weight (multiplies alignment scores)
    bucket_hint: Optional[Bucket] = None    # hard constraint: "X"|"Y"|"Z"|None

@dataclass
class SeamTouchSet:
    touch_corr_id: str    # e.g. "S1"
    touches: List[TouchRecord] = field(default_factory=list)
    uuid:  str = ''  # tie to seam op
    # Seam frame at ArcOn:
    tangent_at_arcon_xyz: Optional[Tuple[float, float, float]] = None  # X axis
    tool_z_at_arcon_in_base: Optional[Tuple[float, float, float]] = None  # Z = -ToolZ

@dataclass
class RoutedBins:
    Z: List[str]                     # touch_identifiers (len in {0,1,3})
    Y: List[str]                     # touch_identifiers (len in {0,1,2})
    X: List[str]                     # touch_identifiers (len in {0,1})
    args6: List[str]                 # [Z1,Z2,Z3,Y1,Y2,X1] padded with TSg_CD0

# ----------------------------- math helpers ----------------------------------

def _np(v): return np.asarray(v, dtype=float)

def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    ua, ub = _unit(a), _unit(b)
    c = float(np.clip(np.dot(ua, ub), -1.0, 1.0))
    return math.degrees(math.acos(c))

def _seam_frame_from_arcon(
    tangent_at_arcon_xyz: Optional[Tuple[float, float, float]],
    tool_z_at_arcon_in_base: Optional[Tuple[float, float, float]],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build an orthonormal frame: X=tangent, Z=-ToolZ, Y=Z×X. Fallback: world axes.
    """
    X = _unit(_np(tangent_at_arcon_xyz)) if tangent_at_arcon_xyz is not None else np.array([1.0, 0.0, 0.0])
    Z = _unit(-_np(tool_z_at_arcon_in_base)) if tool_z_at_arcon_in_base is not None else np.array([0.0, 0.0, 1.0])
    # Gram-Schmidt to ensure orthonormality
    X = _unit(X - np.dot(X, Z) * Z) if np.linalg.norm(np.cross(Z, X)) > 1e-9 else X
    Y = _unit(np.cross(Z, X))
    X = _unit(np.cross(Y, Z))
    return X, Y, Z

def _cd(tid: Optional[str]) -> str:
    return f"CD{tid}" if tid else "EMPTY"

def _vcd(tid: Optional[str]) -> str:
    return f"VCD{tid}" if tid else TSG_CD0

def _pick_fold_title(routed: RoutedBins) -> str:
    buckets = int(bool(routed.X)) + int(bool(routed.Y)) + int(bool(routed.Z))
    total = len(routed.X) + len(routed.Y) + len(routed.Z)
    if buckets == 1: return "TouchSense Corr 1D"
    if buckets == 2: return "TouchSense Corr 2D"
    if buckets == 3 and total == 3: return "TouchSense Corr 3D"
    return "TouchSense Corr Free"

# ------------------------------ router ---------------------------------------

class TouchRouter:
    """
    Assigns 1-6 touch results to Z/Y/X buckets per spec (TouchSens_Router_spec.md).
    
    Key features:
    - Legal counts: Z in {0,1,3}, Y in {0,1,2}, X in {0,1}
    - Global optimization over all feasible patterns
    - Diversity-aware selection for Z=3
    - Bucket hints (hard constraints)
    - Deterministic tie-breaking
    """
    
    def __init__(
        self,
        tau_Z: float = 0.55,
        tau_Y: float = 0.45,
        tau_X: float = 0.45,
        lambda_div: float = 0.05,
        logger: Optional[logging.Logger] = None
    ):
        """
        Parameters:
            tau_Z, tau_Y, tau_X: Minimum alignment thresholds for each axis
            lambda_div: Diversity weight for Z=3 selection
            logger: Optional logger (defaults to module logger)
        """
        self.tau_Z = tau_Z
        self.tau_Y = tau_Y
        self.tau_X = tau_X
        self.lambda_div = lambda_div
        self.log = logger or log

    def route(
        self,
        seam: SeamTouchSet,
        subset_filter: Optional[Callable[[TouchRecord], bool]] = None,
        mode: Literal["final", "progressive"] = "final",
    ) -> RoutedBins:
        """
        Route touches into Z/Y/X buckets and build args6 = [Z1,Z2,Z3,Y1,Y2,X1].
        
        Parameters:
            seam: SeamTouchSet with touches and optional seam frame
            subset_filter: Optional predicate to select subset of touches
            mode: "final" (use seam frame) or "progressive" (honor hints, allow fallback)
        
        Returns:
            RoutedBins with Z/Y/X lists and args6
        """
        # --- Collect touches ---
        touches = [t for t in seam.touches if (subset_filter(t) if subset_filter else True)]
        if not touches:
            return RoutedBins([], [], [], [TSG_CD0] * 6)

        # --- Build touch vectors ---
        valid_touches: List[TouchRecord] = []
        vecs: Dict[str, np.ndarray] = {}
        
        for t in touches:
            tid = t.touch_identifier
            delta = _np(t.collision_xyz) - _np(t.start_xyz)
            norm = np.linalg.norm(delta)
            if norm < 1e-9:
                # Zero-magnitude vector (start == collision) - CRITICAL ERROR
                # This means the approach position wasn't reachable and robot went directly to collision point
                raise ValueError(
                    f"Touch {tid} has degenerate geometry: start position equals collision position. "
                    f"The approach position is likely unreachable. Please check robot kinematics and path planning. "
                    f"Start: {t.start_xyz}, Collision: {t.collision_xyz}"
                )
            vecs[tid] = delta / norm
            valid_touches.append(t)
        
        if not valid_touches:
            return RoutedBins([], [], [], [TSG_CD0] * 6)

        # --- Build seam frame ---
        have_frame = (seam.tangent_at_arcon_xyz is not None and 
                      seam.tool_z_at_arcon_in_base is not None)
        
        if mode == "final" and not have_frame:
            self.log.warning(
                f"Final routing without seam frame (uuid={seam.uuid}). "
                f"Using fallback axes; results may be suboptimal."
            )
        
        Xs, Ys, Zs = _seam_frame_from_arcon(
            seam.tangent_at_arcon_xyz, 
            seam.tool_z_at_arcon_in_base
        )

        # --- Compute weighted alignment scores ---
        scores: Dict[str, Tuple[float, float, float]] = {}  # tid -> (sZ, sY, sX)
        
        for t in valid_touches:
            tid = t.touch_identifier
            v = vecs[tid]
            w = t.weight
            # Sign-agnostic alignment (spec §3)
            sZ = w * abs(float(np.dot(v, Zs)))
            sY = w * abs(float(np.dot(v, Ys)))
            sX = w * abs(float(np.dot(v, Xs)))
            scores[tid] = (sZ, sY, sX)

        # --- Assign automatic hints to linked touches without hints ---
        # Progressive linked touches follow fixed mapping: seq=1→Z, seq=2→Y, seq=3→X
        for t in valid_touches:
            if t.linked and t.bucket_hint is None:
                if t.link_seq == 1:
                    t.bucket_hint = "Z"
                elif t.link_seq == 2:
                    t.bucket_hint = "Y"
                elif t.link_seq == 3:
                    t.bucket_hint = "X"
        
        # --- Separate hinted vs free touches ---
        # Hints from clustering are HARD CONSTRAINTS - don't filter by alignment threshold
        hinted_Z = [t for t in valid_touches if t.bucket_hint == "Z"]
        hinted_Y = [t for t in valid_touches if t.bucket_hint == "Y"]
        hinted_X = [t for t in valid_touches if t.bucket_hint == "X"]
        
        hinted_set = set(t.touch_identifier for t in hinted_Z + hinted_Y + hinted_X)
        
        # CRITICAL: Linked touches are now in hinted lists (via automatic hints above)
        # Any remaining linked touches without valid seq are treated as flexible
        linked_touches = [t for t in valid_touches if t.linked and t.touch_identifier not in hinted_set]
        
        # Free touches = non-linked AND not hinted
        free_touches = [t for t in valid_touches 
                        if not t.linked and t.touch_identifier not in hinted_set]

        # Check hint overflow
        if len(hinted_Z) > 3:
            self._resolve_hint_overflow(hinted_Z, 3, "Z", scores, 0)
        if len(hinted_Y) > 2:
            self._resolve_hint_overflow(hinted_Y, 2, "Y", scores, 1)
        if len(hinted_X) > 1:
            self._resolve_hint_overflow(hinted_X, 1, "X", scores, 2)

        # --- Enumerate feasible patterns and find global optimum ---
        best_pattern = None
        best_score = -float('inf')
        best_assignment = None

        legal_z = [0, 1, 3]
        legal_y = [0, 1, 2]
        legal_x = [0, 1]

        for z_count in legal_z:
            if z_count < len(hinted_Z):
                continue  # Can't satisfy hints
            
            for y_count in legal_y:
                if y_count < len(hinted_Y):
                    continue
                
                for x_count in legal_x:
                    if x_count < len(hinted_X):
                        continue
                    
                    if z_count + y_count + x_count > len(valid_touches):
                        continue
                    
                    # Try to build assignment for this pattern
                    assignment = self._try_pattern(
                        z_count, y_count, x_count,
                        hinted_Z, hinted_Y, hinted_X,
                        free_touches, linked_touches,
                        scores, vecs, Zs, Ys, Xs
                    )
                    
                    if assignment is None:
                        continue  # Infeasible
                    
                    Z_set, Y_set, X_set, pattern_score = assignment
                    
                    # Tie-breaking (spec §5): prefer higher z, then y, then x, then lexicographic
                    tie_key = (
                        pattern_score,
                        z_count,
                        y_count,
                        x_count,
                        tuple(sorted(t.touch_identifier for t in Z_set)),
                        tuple(sorted(t.touch_identifier for t in Y_set)),
                        tuple(sorted(t.touch_identifier for t in X_set))
                    )
                    
                    if best_pattern is None or tie_key > best_pattern:
                        best_pattern = tie_key
                        best_score = pattern_score
                        best_assignment = (Z_set, Y_set, X_set)

        # --- Handle no feasible pattern ---
        if best_assignment is None:
            self.log.error(f"No feasible bucket assignment for seam {seam.uuid} (all touches below thresholds).")
            return RoutedBins([], [], [], [TSG_CD0] * 6)

        Z_set, Y_set, X_set = best_assignment

        # --- Order within buckets (temporal order: linked by seq, non-linked by identifier) ---
        Z_ordered = self._order_touches_temporal(Z_set)
        Y_ordered = self._order_touches_temporal(Y_set)
        X_ordered = self._order_touches_temporal(X_set)

        # --- Build args6 ---
        args6 = self._build_args6(Z_ordered, Y_ordered, X_ordered)

        return RoutedBins(
            Z=[t.touch_identifier for t in Z_ordered],
            Y=[t.touch_identifier for t in Y_ordered],
            X=[t.touch_identifier for t in X_ordered],
            args6=args6
        )

    # -------------------------- Pattern enumeration --------------------------

    def _try_pattern(
        self,
        z_count: int, y_count: int, x_count: int,
        hinted_Z: List[TouchRecord],
        hinted_Y: List[TouchRecord],
        hinted_X: List[TouchRecord],
        free_touches: List[TouchRecord],
        linked_touches: List[TouchRecord],
        scores: Dict[str, Tuple[float, float, float]],
        vecs: Dict[str, np.ndarray],
        Zs: np.ndarray, Ys: np.ndarray, Xs: np.ndarray
    ) -> Optional[Tuple[List[TouchRecord], List[TouchRecord], List[TouchRecord], float]]:
        """
        Try to build an assignment for pattern (z_count, y_count, x_count).
        Returns (Z_set, Y_set, X_set, score) or None if infeasible.
        
        Priority order:
        1. Hinted touches (from clustering) - hard constraints
        2. Linked touches (progressive measurement) - bypass thresholds
        3. Free touches - must pass alignment thresholds
        """
        # --- Select Z ---
        # Include: hinted_Z + linked (no threshold) + free (with threshold)
        pool_Z = (hinted_Z + 
                  linked_touches +  # All linked (bypass threshold)
                  [t for t in free_touches if scores[t.touch_identifier][0] >= self.tau_Z])
        
        if len(pool_Z) < z_count:
            return None
        
        # Must include: hinted + linked (both have priority over free touches)
        must_include_Z = hinted_Z + linked_touches
        Z_set = self._select_Z_set(pool_Z, z_count, must_include_Z, scores, vecs, Zs)
        
        if len(Z_set) != z_count:
            return None

        # --- Select Y from remaining ---
        used_tids = {t.touch_identifier for t in Z_set}
        remaining_linked = [t for t in linked_touches if t.touch_identifier not in used_tids]
        remaining_free = [t for t in free_touches if t.touch_identifier not in used_tids]
        remaining_hinted_Y = [t for t in hinted_Y if t.touch_identifier not in used_tids]
        
        pool_Y = (remaining_hinted_Y + 
                  remaining_linked +  # All linked (bypass threshold)
                  [t for t in remaining_free if scores[t.touch_identifier][1] >= self.tau_Y])
        
        if len(pool_Y) < y_count:
            return None
        
        # Must include: hinted + linked (both have priority)
        must_include_Y = remaining_hinted_Y + remaining_linked
        Y_set = self._select_best_by_score(pool_Y, y_count, must_include_Y, scores, 1)
        
        if len(Y_set) != y_count:
            return None

        # --- Select X from remaining ---
        used_tids.update(t.touch_identifier for t in Y_set)
        remaining_linked = [t for t in linked_touches if t.touch_identifier not in used_tids]
        remaining_free = [t for t in free_touches if t.touch_identifier not in used_tids]
        remaining_hinted_X = [t for t in hinted_X if t.touch_identifier not in used_tids]
        
        pool_X = (remaining_hinted_X + 
                  remaining_linked +  # All linked (bypass threshold)
                  [t for t in remaining_free if scores[t.touch_identifier][2] >= self.tau_X])
        
        if len(pool_X) < x_count:
            return None
        
        # Must include: hinted + linked (both have priority)
        must_include_X = remaining_hinted_X + remaining_linked
        X_set = self._select_best_by_score(pool_X, x_count, must_include_X, scores, 2)
        
        if len(X_set) != x_count:
            return None

        # --- Compute pattern score (spec §5) ---
        score_Z = sum(scores[t.touch_identifier][0] for t in Z_set)
        score_Y = sum(scores[t.touch_identifier][1] for t in Y_set)
        score_X = sum(scores[t.touch_identifier][2] for t in X_set)
        
        diversity_term = 0.0
        if z_count == 3:
            diversity_term = self.lambda_div * self._compute_spread(Z_set, vecs)
        
        total_score = score_Z + diversity_term + score_Y + score_X

        return (Z_set, Y_set, X_set, total_score)

    # -------------------------- Z selection with diversity -------------------

    def _select_Z_set(
        self,
        pool: List[TouchRecord],
        count: int,
        must_include: List[TouchRecord],
        scores: Dict[str, Tuple[float, float, float]],
        vecs: Dict[str, np.ndarray],
        Zs: np.ndarray
    ) -> List[TouchRecord]:
        """
        Select count touches from pool, ensuring must_include are included.
        For count=3, maximize score + lambda_div * spread.
        
        Priority: must_include touches are selected first, then best from remaining.
        """
        if count == 0:
            return []
        
        if count == 1:
            # Prioritize must_include (hinted + linked), then pick highest sZ
            if must_include:
                # Pick best from must_include
                candidates = list(must_include)
                candidates.sort(key=lambda t: (-scores[t.touch_identifier][0], t.touch_identifier))
                return candidates[:1]
            else:
                # Pick best from entire pool
                candidates = [t for t in pool]
                candidates.sort(key=lambda t: (-scores[t.touch_identifier][0], t.touch_identifier))
                return candidates[:1]
        
        if count == 3:
            # Enumerate all combinations and pick best by score + diversity
            from itertools import combinations
            
            must_tids = {t.touch_identifier for t in must_include}
            free_pool = [t for t in pool if t.touch_identifier not in must_tids]
            
            need_free = count - len(must_include)
            
            # Handle must_include overflow
            if need_free < 0:
                # Too many must_include - select best subset of 3 by score+diversity
                best_combo = None
                best_value = -float('inf')
                
                for combo in combinations(must_include, count):
                    candidate_set = list(combo)
                    score_sum = sum(scores[t.touch_identifier][0] for t in candidate_set)
                    spread = self._compute_spread(candidate_set, vecs)
                    value = score_sum + self.lambda_div * spread
                    
                    tie_key = (value, tuple(sorted(t.touch_identifier for t in candidate_set)))
                    if best_combo is None or tie_key > best_combo:
                        best_combo = tie_key
                        best_value = value
                        best_combo_set = candidate_set
                
                return best_combo_set if best_combo else []
            
            # Normal case: must_include fits, add free touches
            if len(free_pool) < need_free:
                return []
            
            best_combo = None
            best_value = -float('inf')
            
            for combo in combinations(free_pool, need_free):
                candidate_set = list(must_include) + list(combo)
                score_sum = sum(scores[t.touch_identifier][0] for t in candidate_set)
                spread = self._compute_spread(candidate_set, vecs)
                value = score_sum + self.lambda_div * spread
                
                # Tie-break by sorted identifiers
                tie_key = (value, tuple(sorted(t.touch_identifier for t in candidate_set)))
                if best_combo is None or tie_key > best_combo:
                    best_combo = tie_key
                    best_value = value
                    best_combo_set = candidate_set
            
            return best_combo_set if best_combo else []
        
        return []

    def _compute_spread(self, touches: List[TouchRecord], vecs: Dict[str, np.ndarray]) -> float:
        """
        Compute diversity spread for 3 touches (spec §5 + decision #1).
        spread = min_angle + 0.10 * avg_angle (in degrees)
        """
        if len(touches) != 3:
            return 0.0
        
        tids = [t.touch_identifier for t in touches]
        v1, v2, v3 = vecs[tids[0]], vecs[tids[1]], vecs[tids[2]]
        
        a12 = _angle_deg(v1, v2)
        a13 = _angle_deg(v1, v3)
        a23 = _angle_deg(v2, v3)
        
        min_angle = min(a12, a13, a23)
        avg_angle = (a12 + a13 + a23) / 3.0
        
        return min_angle + 0.10 * avg_angle

    # -------------------------- Y/X selection --------------------------------

    def _select_best_by_score(
        self,
        pool: List[TouchRecord],
        count: int,
        must_include: List[TouchRecord],
        scores: Dict[str, Tuple[float, float, float]],
        axis_idx: int  # 0=Z, 1=Y, 2=X
    ) -> List[TouchRecord]:
        """
        Select count touches maximizing sum of scores[tid][axis_idx].
        
        If must_include has more touches than count, select best subset by score.
        """
        if count == 0:
            return []
        
        # Handle must_include overflow: too many must_include for bucket size
        if len(must_include) > count:
            # Select best 'count' from must_include by score
            candidates = list(must_include)
            candidates.sort(key=lambda t: (-scores[t.touch_identifier][axis_idx], t.touch_identifier))
            return candidates[:count]
        
        # Normal case: must_include fits, fill remaining with free touches
        must_tids = {t.touch_identifier for t in must_include}
        free_pool = [t for t in pool if t.touch_identifier not in must_tids]
        
        need_free = count - len(must_include)
        
        # Sort free pool by score descending, then by identifier
        free_pool.sort(key=lambda t: (-scores[t.touch_identifier][axis_idx], t.touch_identifier))
        
        selected_free = free_pool[:need_free]
        return list(must_include) + selected_free

    # -------------------------- Ordering within buckets ----------------------

    def _order_touches_temporal(self, touches: List[TouchRecord]) -> List[TouchRecord]:
        """
        Order touches by temporal sequence:
        1. Linked touches first (sorted by link_seq ascending)
        2. Non-linked touches second (sorted by touch_identifier ascending)
        
        This preserves measurement order: linked touches maintain their execution
        sequence, and non-linked touches follow in the order they were measured.
        """
        result = list(touches)
        result.sort(key=lambda t: (
            not t.linked,                                    # False (linked) sorts before True (non-linked)
            t.link_seq if t.linked else float('inf'),        # Sort linked by link_seq
            t.touch_identifier if not t.linked else ""       # Sort non-linked by identifier
        ))
        return result

    # -------------------------- Helpers --------------------------------------

    def _resolve_hint_overflow(
        self,
        hinted: List[TouchRecord],
        capacity: int,
        bucket_name: str,
        scores: Dict[str, Tuple[float, float, float]],
        axis_idx: int
    ):
        """
        Drop least-aligned hinted touches when hints exceed capacity.
        Modifies hinted list in-place.
        """
        if len(hinted) <= capacity:
            return
        
        # Sort by score ascending (worst first)
        hinted.sort(key=lambda t: (scores[t.touch_identifier][axis_idx], t.touch_identifier))
        
        dropped = hinted[:len(hinted) - capacity]
        kept = hinted[len(hinted) - capacity:]
        
        for t in dropped:
            self.log.warning(
                f"Bucket {bucket_name} hint overflow: dropping {t.touch_identifier} "
                f"(score={scores[t.touch_identifier][axis_idx]:.3f})"
            )
        
        hinted[:] = kept

    def _build_args6(
        self,
        Z_ordered: List[TouchRecord],
        Y_ordered: List[TouchRecord],
        X_ordered: List[TouchRecord]
    ) -> List[str]:
        """
        Build args6 = [Z1, Z2, Z3, Y1, Y2, X1] with TSg_CD0 padding.
        """
        def get_symbol(touches: List[TouchRecord], idx: int) -> str:
            return f"VCD{touches[idx].touch_identifier}" if idx < len(touches) else TSG_CD0
        
        return [
            get_symbol(Z_ordered, 0),
            get_symbol(Z_ordered, 1),
            get_symbol(Z_ordered, 2),
            get_symbol(Y_ordered, 0),
            get_symbol(Y_ordered, 1),
            get_symbol(X_ordered, 0),
        ]

    # -------------------------- FOLD emitter ---------------------------------

    @staticmethod
    def emit_fold(routed: RoutedBins, title_hint: Optional[str] = None) -> str:
        """
        Emit a TouchSense correction fold per spec §8.
        
        Parameters:
            routed: RoutedBins with Z/Y/X lists and args6
            title_hint: Optional override for fold title
        
        Returns:
            KRL fold text
        """
        title = title_hint or _pick_fold_title(routed)

        def brace_x(lst: List[str]) -> str:
            return "{" + (f"CD{lst[0]}" if lst else "-") + "}"

        def brace_y(lst: List[str]) -> str:
            a = [f"CD{x}" for x in lst] + ["-"] * (2 - len(lst))
            return "{" + ",".join(a[:2]) + "}"

        def brace_z(lst: List[str]) -> str:
            a = [f"CD{x}" for x in lst] + ["-"] * (3 - len(lst))
            return "{" + ",".join(a[:3]) + "}"

        header = f";FOLD {title} {brace_x(routed.X)} {brace_y(routed.Y)} {brace_z(routed.Z)} ;%{{PE}}\n"

        # Params use reverse mapping: Correction1D=X, Correction2D/3D=Y, Correction4D/5D/6D=Z
        params = (
            "  ;FOLD Parameters ;%{h}\n"
            f"    ;Params IlfProvider=KukaRoboter.TouchSense.Correction6D;"
            f"Correction1D={_cd(routed.X[0] if len(routed.X)>=1 else None)};"
            f"Correction2D={_cd(routed.Y[0] if len(routed.Y)>=1 else None)};"
            f"Correction3D={_cd(routed.Y[1] if len(routed.Y)>=2 else None)};"
            f"Correction4D={_cd(routed.Z[0] if len(routed.Z)>=1 else None)};"
            f"Correction5D={_cd(routed.Z[1] if len(routed.Z)>=2 else None)};"
            f"Correction6D={_cd(routed.Z[2] if len(routed.Z)>=3 else None)}\n"
            "  ;ENDFOLD\n"
        )

        # Macro call uses args6 directly: [Z1,Z2,Z3,Y1,Y2,X1]
        a = routed.args6
        call = f"  TS_BC6DCalc({a[0]}, {a[1]}, {a[2]}, {a[3]}, {a[4]}, {a[5]})\n"
        tail = ";ENDFOLD"
        
        return header + params + call + tail

# ----------------- progressive (linked) emission helper ----------------------

# -----------------------------
# Helpers to format named 1D / 2D / 3D folds (translation-only progressive)
# Mapping rule for linked trio: 1st->Z1, 2nd->Y1, 3rd->X1
# -----------------------------

def _emit_named_1d(z1: str) -> str:
    header = f";FOLD TouchSense Corr 1D {z1} ;%{{PE}}\n"
    params = (
        "  ;FOLD Parameters ;%{h}\n"
        f"    ;Params IlfProvider=KukaRoboter.TouchSense.Correction1D;"
        f"Correction1D={z1}\n"
        "  ;ENDFOLD\n"
    )
    call = f"  TS_BC6DCalc(V{z1}, {TSG_CD0}, {TSG_CD0}, {TSG_CD0}, {TSG_CD0}, {TSG_CD0})\n"
    tail = ";ENDFOLD"
    return header + params + call + tail

def _emit_named_2d(z1: str, y1: str) -> str:
    header = f";FOLD TouchSense Corr 2D {z1} {y1} ;%{{PE}}\n"
    params = (
        "  ;FOLD Parameters ;%{h}\n"
        f"    ;Params IlfProvider=KukaRoboter.TouchSense.Correction2D;"
        f"Correction1D={z1};Correction2D={y1}\n"
        "  ;ENDFOLD\n"
    )
    call = f"  TS_BC6DCalc(V{z1}, {TSG_CD0}, {TSG_CD0}, V{y1}, {TSG_CD0}, {TSG_CD0})\n"
    tail = ";ENDFOLD"
    return header + params + call + tail

def _emit_named_3d(z1: str, y1: str, x1: str) -> str:
    header = f";FOLD TouchSense Corr 3D {z1} {y1} {x1} ;%{{PE}}\n"
    params = (
        "  ;FOLD Parameters ;%{h}\n"
        f"    ;Params IlfProvider=KukaRoboter.TouchSense.Correction3D;"
        f"Correction1D={z1};Correction2D={y1};Correction3D={x1}\n"
        "  ;ENDFOLD\n"
    )
    call = f"  TS_BC6DCalc(V{z1}, {TSG_CD0}, {TSG_CD0}, V{y1}, {TSG_CD0}, V{x1})\n"
    tail = ";ENDFOLD"
    return header + params + call + tail

def _emit_progressive_named_fold(linked_syms_sorted: List[str]) -> Optional[str]:
    """
    linked_syms_sorted: symbols of linked touches sorted by link_seq (1..k)
    Returns the fold text (1D/2D/3D) or None if nothing to emit.
    """
    k = len(linked_syms_sorted)
    if k == 0:
        return None
    # 1st -> Z1, 2nd -> Y1, 3rd -> X1
    z1 = linked_syms_sorted[0]
    if k == 1:
        return _emit_named_1d(z1)
    y1 = linked_syms_sorted[1]
    if k == 2:
        return _emit_named_2d(z1, y1)
    x1 = linked_syms_sorted[2]
    return _emit_named_3d(z1, y1, x1)

# --- End of touch_router --------------------------------------------------

from KUKA_KRC5 import KUKA_KRC5
DOWNLOAD_CLASS_NAME = "KUKA_KRC5_Arc_Welding"

class KUKA_KRC5_Arc_Welding(KUKA_KRC5):
   """KUKA_KRC5_Arc_Welding downloader
   Arc Welding robot vendor downloader
   Derived from: KUKA_KRC5 downloader
   """
   DOWNLOADER_VERSION = '1.2'
   # attribute name of the work method to get the workmethod name
   WORKMETHOD_NAME = "ArcWeldingOperationWorkMethodName"
   # stitching work method name
   WM_NAME_STICH = "StitchWeldingWorkMethod"
   # touch sensing operation name
   WM_NAME_TOUCH = "TouchSensingWorkMethod"
   # seam search operation name
   WM_NAME_SEAM = "SeamSearchWorkMethod"
   # seam search operation name
   WM_NAME_SEAM_FIND = "SeamFindingWorkMethod"
   # continues welding operation name
   WM_NAME_CONTINUES = "ContourPointWorkMethod"
   # arcspot operation name
   WM_NAME_ARCSPOT = "ArcSpotWorkMethod"

   # connection type between touch sensing and welding operation (operation-start/end-shortest distance)
   AW_TOUCHSENSE_CONNECT_TYPE = "TSConnectionType"

   # identifiers are events added to the touch sensing points in the within the touch sensing cycle.
   TS_POINT_IDENTIFIER_START_APP = "TouchPointStartAppEvent"
   TS_POINT_IDENTIFIER_COLLISION = "TouchPointCollisionEvent"
   TS_POINT_IDENTIFIER_END = "TouchPointEndEvent"
   TS_POINT_IDENTIFIER_START_RET = "TouchPointStartRetEvent"

   AW_CONNECT_TOUCH_PROCESS_TYPE = "ConnectTouchProcessType"
   # touch operation attribute
   AW_TOUCHSENS_TOUCH_ID = "TSTouchID"
   AW_TOUCHSENS_TOUCH_OPS_FOR_FRAME = "Touch_Cntr"
   AW_WELDING_GROUP_TOUCH_ID = "TouchId"
   AW_TOUCHSENS_SENSING_SPEED = "SensingSpeed"
   AW_TOUCHSENS_UUID = "TSContourTpeUUID"
   AW_TOUCHSENS_LINKED_FLAG = "TSLinkedTouch"
   # touch sensing digital output
   AW_TOUCHSENS_DIGITAL_INPUT = "TSDigitalInput"
   # touch sensing sensor output
   AW_TOUCHSENS_DIGITAL_OUTPUT = "TSDigitalOutput"
   #
   AW_SEAM_CALIB_CAD_MASTERED = "SeamCalibCadMastered"
   AW_SENSOR_TOOL_TYPE = "SensorToolType"
   AW_SENSOR_TOOL_TYPE_LITERALS = ["Touch Sensor", "Point Laser", "Line Laser"]
   AW_SENSOR_ID_TOUCH = "SensorIdTouch"
   AW_SENSOR_ID_POINT = "SensorIdPoint"
   AW_SENSOR_ID_LINE = "SensorIdLine"
   # KUKA specific SeamFinding inside TouchSensing (LineLaser)
   KUKA_SEAM_FINDING_MOUNT_TYPE = "KukaSeamFindingMountType"
   KUKA_SEAM_FINDING_RECIPE = "KukaSeamFindingRecipe"
   KUKA_SEAMFIND_ID = "SeamFindingId"

   # "ConnectTouchProcessPointEvent" event attribute
   AW_EVT_TOUCH_ID        = "TouchId"
   AW_EVT_TOUCH_FRAME_PT  = "FramePt"
   AW_EVT_TOUCH_COUNTER   = "Touch_Cntr"
   AW_EVT_TOUCH_ID_VIACIR = "TouchID_ViaCir"
   # Calibration methods
   AW_SEAM_CALIBRATION_METHOD = "SeamCalibrationMethod"
   AW_SEAMSEARCHING = "SeamSearching"
   AW_SEAMFINDING = "SeamFinding"
   AW_SEAMTRACKING = "SeamTracking"
   AW_SEAMFIND_SENSING_SPEED = "SeamFindingSensingSpeed"
   #ArcTech Global settings
   KUKA_POWER_SOURCE = "KukaPowerSource"
   KUKA_POWER_SOURCE_LIST = ["Standard","Fronius"]
   KUKA_POWER_SOURCE_JOB_CANNEL = "KukaPowerSourceJobChannel"
   KUKA_SINGLE_WDAT = "KukaSingleWDat"
   KUKA_ADD_WDAT_INDEX = "KukaAddWDatIndex"
   KUKA_ARCTECH_ADV = "KukaArcTechAdv"
   KUKA_WEAVE_TYPE = "KukaWeaveType"
   KUKA_WEAVE_TYPE_LIST = ["Weave length","Weave frequency"]
   KUKA_SORT_DAT = "KukaSortDat"
   KUKA_TRACK_ARCSENSE = "KukaTrackArcSense"
   KUKA_SPTP_SLIN = "SPtpSLin"

   #ArcOff Operation Default Definition
   KUKA_ARC_OFF_JOB_NUMBER_DEFINE = "KukaArcOffJobNumberDefine"
   KUKA_ARC_OFF_PARAM_SET_DEFINE = "KukaArcOffParmSetDefine"
   KUKA_END_CRATER_TIME_DEFINE = "KukaEndCraterTimeDefine"
   KUKA_POST_FLOW_TIME_DEFINE = "KukaPostFlowTimeDefine"

   SOURCEFILE_EXTENSION = '.src'
   DATAFILE_EXTENSION = '.dat'

   KUKA_SEAMTRACK_SEARCH_START = "SeamTrackSearchStart"
   KUKA_SEAMTRACK_SEARCH_SPEED = "SeamTrackSearchSpeed"

   AW_KUKA_TECH_TAB_FOLDER = "KUKATechTabFolder"

#################### BASE FUNCTIONS ####################
   def __init__(self) -> None:
      """Class initialization
      """
      super().__init__()

      self.Tech.ReadAheadEvents = ['ArcOnEvent', 'ArcOffEvent', 'SeamTrackingLeadInEvent', 'SeamTrackingOffEvent', 'SeamTrackingEvent']

      # Initialize the data classes and assign it to an instance variable
      self.ArcTech = ArcTech()
      self.ArcIgnInfo = ArcIgnInfo()
      self.ArcOnInfo = ArcOnInfo()
      self.ArcSenseInfo = ArcSenseInfo()
      self.ArcOffInfo = ArcOffInfo()
      self.TouchInfo = TouchInfo()
      self.TouchInfo.TouchSets = {}  # Initialize TouchSets as an empty dictionary

      # WDAT identifier related attributes and flags:
      # WDATXX_YYY_ZZ: XX = Weld Job Nr., YYY = Robot Velocity (0.35 m/s => YYY = 035), ZZ = optional WDat Index
      self.WDatIndex:int = 0
      self.WDatIndexOnOff:int = 0
      self.WDatIndexList = []

      # store SeamFInd position
      self.SeamFindPosition = ''
      self.SeamFindJointType = ''
      # self.WDatSwiIndex = []
      # self.WDatOffIndex = []
      # used language in user interface
      self.Language = ""

   def OutputHeader(self, operator: DULPythonDownloadOperator, controller : DULPythonController):
      self.DownloaderName = DOWNLOAD_CLASS_NAME
      super().OutputHeader(operator, controller)
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputHeader called")

      #Get downloader flags from controller attributes
      version = ''
      try:
         # Get ArcTech version numbers from controller attributes if available
         version = controller.GetString('ArcTechVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " ArcTechVersion")
      if version != '':
         self.ArcTech.ArcTechVersionSRC = version
         self.ArcTech.ArcTechVersionDAT = self.ConvertVersionString(version)
      else:
         version = '3.4.5.6'
         self.ArcTech.ArcTechVersionSRC = version
         self.ArcTech.ArcTechVersionDAT = self.ConvertVersionString(version)
         logger.LogWarn("Downloader Warning: Attribute ''ArcTechVersion'' could not be found. Version ''3.4.5.6'' is taken as Default")
      self.AddLineToSourceHeader('; ArcTech Version       = %s' % (version))

      versionAdv = ''
      try:
         # Get ArcTechAdv version numbers from controller attributes if available
         versionAdv = controller.GetString('ArcTechAdvVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " ArcTechAdvVersion")
      if versionAdv != '':
         self.ArcTech.ArcTechAdvVersionSRC = versionAdv
         self.ArcTech.ArcTechAdvVersionDAT = self.ConvertVersionString(versionAdv)
      else:
         versionAdv = '3.4.5.6'
         self.ArcTech.ArcTechAdvVersionSRC = versionAdv
         self.ArcTech.ArcTechAdvVersionDAT = self.ConvertVersionString(versionAdv)
         logger.LogWarn("Downloader Warning: Attribute ''ArcTechAdvVersion'' could not be found. Version ''3.4.5.6'' is taken as Default")
      self.AddLineToSourceHeader('; ArcTech Adv. Ver.     = %s' % (versionAdv))

      versionSense = ''  # Initialize with a default value
      try:
         # Get ArcTechSense version numbers from controller attributes if available
         versionSense = controller.GetString('ArcTechSenseVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " ArcTechSenseVersion")
      if versionSense != '':
         self.ArcTech.ArcTechSenseVersionSRC = versionSense
         self.ArcTech.ArcTechSenseVersionDAT = self.ConvertVersionString(versionSense)
      else:
         versionSense = '3.5.1.21'
         self.ArcTech.ArcTechSenseVersionSRC = versionSense
         self.ArcTech.ArcTechSenseVersionDAT = self.ConvertVersionString(versionSense)
         logger.LogWarn("Downloader Warning: Attribute ''ArcTechSenseVersion'' could not be found. Version ''3.5.1.21'' is taken as Default")
      self.AddLineToSourceHeader('; ArcTechSense Ver.     = %s' % (versionSense))

      versionTouch = ''  # Initialize with a default value
      try:
         # Get ArcTechSense version numbers from controller attributes if available
         versionTouch = controller.GetString('TouchSenseVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " TouchSenseVersion")
      if versionTouch != '':
         self.ArcTech.TouchSenseVersionSRC = versionTouch
         self.ArcTech.TouchSenseVersionDAT = self.ConvertVersionString(versionTouch)
      else:
         versionTouch = '3.8.1.0'
         self.ArcTech.TouchSenseVersionSRC = versionTouch
         self.ArcTech.TouchSenseVersionDAT = self.ConvertVersionString(versionTouch)
         logger.LogWarn("Downloader Warning: Attribute ''TouchSenseVersion'' could not be found. Version ''3.8.1'' is taken as Default")
      self.AddLineToSourceHeader('; TouchSense Ver.       = %s' % (versionTouch))

      versionFinding = ''  # Initialize with a default value
      try:
         # Get ArcTechSense version numbers from controller attributes if available
         versionFinding = controller.GetString('SeamTechFindingVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " SeamTechFindingVersion")
      if versionFinding != '':
         self.ArcTech.SeamTechFindingVersionSRC = versionFinding
         self.ArcTech.SeamTechFindingVersionDAT = self.ConvertVersionString(versionFinding)
      else:
         versionFinding = '3.8.1.0'
         self.ArcTech.SeamTechFindingVersionSRC = versionFinding
         self.ArcTech.SeamTechFindingVersionDAT = self.ConvertVersionString(versionFinding)
         logger.LogWarn("Downloader Warning: Attribute ''SeamTechFindingVersion'' could not be found. Version ''3.8.1'' is taken as Default")
      self.AddLineToSourceHeader('; SeamTechFinding Ver.  = %s' % (versionFinding))

      versionTracking = ''  # Initialize with a default value
      try:
         # Get ArcTechSense version numbers from controller attributes if available
         versionTracking = controller.GetString('SeamTechTrackingVersion',False)
      except:
         logger.LogWarn("Downloader Warning: Can't access controller attribute: " + " SeamTechTrackingVersion")
      if versionTracking != '':
         self.ArcTech.SeamTechTrackingVersionSRC = versionTracking
         self.ArcTech.SeamTechTrackingVersionDAT = self.ConvertVersionString(versionTracking)
      else:
         versionTracking = '3.8.1.0'
         self.ArcTech.SeamTechTrackingVersionSRC = versionTracking
         self.ArcTech.SeamTechTrackingVersionDAT = self.ConvertVersionString(versionTracking)
         logger.LogWarn("Downloader Warning: Attribute ''SeamTechTrackingVersion'' could not be found. Version ''3.8.1'' is taken as Default")
      self.AddLineToSourceHeader('; SeamTechTracking Ver. = %s' % (versionTracking))

      self.AddLineToSourceHeader(';***************************************************')


   def ConvertVersionString(self, version_string: str):
      """Converts a version string in the format '3.4.5.6' to '304050006'.
      Args:
         version_string: The input version string.
      Returns:
         The converted version string in the desired format.
      """

      version_parts = version_string.split(".")
      if len(version_parts) not in (3, 4):
         print("Invalid Option Pack version string format.")
         # raise ValueError("Invalid Option Pack version string format.")

      version, release, servicepack = version_parts[:3]
      build_number = version_parts[3] if len(version_parts) == 4 else "0000"

      return f"{int(version):d}{int(release):02d}{int(servicepack):02d}{int(build_number):04d}"

   def ProgramStart(self, operator: DULPythonDownloadOperator, program: DULPythonProgram):
      """Called on each program start.

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program, controller and resources
         program (DULPythonProgram): access to the program object
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader ProgramStart called")
      logger.LogDebug(program.GetName())

      # Get global attribs
      self.ArcTech.PowerSource = program.GetLiteral(self.KUKA_POWER_SOURCE, False)
      self.ArcTech.PowerSourceJobChannel = program.GetInteger(self.KUKA_POWER_SOURCE_JOB_CANNEL, False)
      self.ArcTech.SingleWDat = program.GetBool(self.KUKA_SINGLE_WDAT, False)
      self.ArcTech.AddWDatIndex = program.GetBool(self.KUKA_ADD_WDAT_INDEX, False)
      self.ArcTech.ArcTechAdv = program.GetBool(self.KUKA_ARCTECH_ADV, False)
      self.ArcTech.WeaveType = program.GetLiteral(self.KUKA_WEAVE_TYPE, False)
      self.ArcTech.TrackArcSense = program.GetBool(self.KUKA_TRACK_ARCSENSE, False)
      self.ArcTech.CadMastered = program.GetBool(self.AW_SEAM_CALIB_CAD_MASTERED, False)
      self.ArcTech.OutputSeamTrackSearchStart = program.GetBool(self.KUKA_SEAMTRACK_SEARCH_START, False)
      self.ArcTech.SeamTrackSearchSpeed = program.GetDouble(self.KUKA_SEAMTRACK_SEARCH_SPEED, True)
      self.Tech.SortDat = program.GetBool(self.KUKA_SORT_DAT, False)

   def OperationGroupStart(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      super().OperationGroupStart(operator, operationGroup)
      self.ArcTech.OutputSeamTrackSearchStart = operationGroup.GetBool(self.KUKA_SEAMTRACK_SEARCH_START, True)
      self.ArcTech.SeamTrackSearchSpeed = operationGroup.GetDouble(self.KUKA_SEAMTRACK_SEARCH_SPEED, True)
      self.TouchInfo.TouchOpCounter = 0

   def OperationStart(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      super().OperationStart(operator, operation)

      ttt=[]
      ttt= operator.GetController().GetResources()
      t1= ttt[0].GetItemSubType()
   
      self.ArcTech.OutputSeamTrackSearchStart = operation.GetBool(self.KUKA_SEAMTRACK_SEARCH_START, True)
      self.ArcTech.SeamTrackSearchSpeed = operation.GetDouble(self.KUKA_SEAMTRACK_SEARCH_SPEED, True)

      # Get WM name
      self.WorkmethodName = operation.GetString(self.WORKMETHOD_NAME, False)
      # stich welding operation
      if self.WorkmethodName == self.WM_NAME_STICH:
         # -------------------------------- WELDING (STITCH) -------------------------------------------------
         #Spline Definition
         self.Tech.SplinesWhenNotProcessing = operation.GetBool(self.KUKA_SPTP_SLIN, True)
         # Each weld seam gets their own WDAT
         self.ArcTech.WDatIndex += 1
         # Get ARcOff default values from operation panel
         self.ArcOffInfo.KukaArcOffJobNumber = operation.GetInteger(self.KUKA_ARC_OFF_JOB_NUMBER_DEFINE, True)
         self.ArcOffInfo.KukaArcOffParmSet = operation.GetString(self.KUKA_ARC_OFF_PARAM_SET_DEFINE, True)
         self.ArcOffInfo.KukaEndCraterTime = operation.GetDouble(self.KUKA_END_CRATER_TIME_DEFINE, True)
         self.ArcOffInfo.KukaPostFlowTime = operation.GetDouble(self.KUKA_POST_FLOW_TIME_DEFINE, True)
         # Get SeamTracking information
         # self.ArcTech.SeamTrackFlag = operation.GetBool(self.AW_SEAMTRACKING, True)

      elif self.WorkmethodName == self.WM_NAME_TOUCH:
         # -------------------------------- TOUCH SENSING -------------------------------------------------
         # Initilize touch sensing parameters
         self.TouchInfo.TouchConnectionType = operation.GetLiteralAttribute(self.AW_TOUCHSENSE_CONNECT_TYPE, True).GetValue()
         # Get sensor id
         self.TouchInfo.SensorToolType = operation.GetLiteralAttribute(self.AW_SENSOR_TOOL_TYPE, True).GetValue()
         if self.TouchInfo.SensorToolType not in self.AW_SENSOR_TOOL_TYPE_LITERALS:
            logger = operator.GetLogOperator()
            logger.LogError(f"Touch Sensor Tool Type '{self.TouchInfo.SensorToolType}' is not supported. Supported types are: {', '.join(self.AW_SENSOR_TOOL_TYPE_LITERALS)}")
            raise ValueError(f"Touch Sensor Tool Type '{self.TouchInfo.SensorToolType}' is not supported. Supported types are: {', '.join(self.AW_SENSOR_TOOL_TYPE_LITERALS)}")
         sensor_id_map = {
            self.AW_SENSOR_TOOL_TYPE_LITERALS[0]: self.AW_SENSOR_ID_TOUCH,  # Touch Sensor
            self.AW_SENSOR_TOOL_TYPE_LITERALS[1]: self.AW_SENSOR_ID_POINT,  # Point Laser
            self.AW_SENSOR_TOOL_TYPE_LITERALS[2]: self.AW_SENSOR_ID_LINE    # Line Laser
         }
         if self.TouchInfo.SensorToolType  in sensor_id_map:
            self.TouchInfo.SensorId = operation.GetInteger(sensor_id_map[self.TouchInfo.SensorToolType], True)

         if self.TouchInfo.SensorToolType == self.AW_SENSOR_TOOL_TYPE_LITERALS[2]:
            self.TouchInfo.TouchSensAsSeamFind = True # with Line Laser handle TS as SeamFinding on KUKA
            self.ArcTech.SeamFindId = operation.GetInteger('SeamFindingId', True)
            self.ArcTech.SeamFindSpeed = operation.GetDouble('SensingSpeed', True)
            self.SeamFindJointType = operation.GetLiteralAttribute('SeamFindingJointType', True).GetValue().split('-')[0]
            self.ArcTech.SeamFindOpsInGroupCounter+=1
         else:
            self.TouchInfo.TouchSensAsSeamFind = False

         if not(self.TouchInfo.TouchInit) and (not self.TouchInfo.TouchSensAsSeamFind):
            tempStr1 = 'DECL TSg_PCollCD_T NullTouch={CD_IPO_MODE #BASE,Mastered TRUE,SDir_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},'\
                     + 'Ref_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},'\
                     +'Meas_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},Diff_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},VecLenDiff_W 0.0,MEnum #CDEmpty,MC 1}'
            # bPerformTouchSense commented out, To be debugged
            if self.Tech.SortDat:
               self.DataTechDAT2.append(tempStr1)
               # self.DataTechDAT2.append('DECL BOOL bPerformTouchSense = TRUE')
            else:
               self.AddLineToData(tempStr1)
               # self.AddLineToData('DECL BOOL bPerformTouchSense = TRUE\n\n')
            self.TouchInfo.TouchInit = True
            # Initialize touch sensing execution flag
            # self.AddLineToSource('bPerformTouchSense = TRUE\n\n')
         if self.TouchInfo.TouchGroupInit == False:
            # Initialize touch sensing group
            # self.AddLineToSource('IF bPerformTouchSense == TRUE THEN')
            self.TouchInfo.TouchGroupInit = True

         # Get touch sensing parameters
         self.ArcTech.FindFrameCounter = operation.GetInteger(self.AW_WELDING_GROUP_TOUCH_ID, True)
         self.ArcTech.FindFramePointCounter = operation.GetInteger(self.AW_EVT_TOUCH_FRAME_PT, True)
         self.TouchInfo.TouchOpsForCurrentFrame = operation.GetInteger(self.AW_TOUCHSENS_TOUCH_OPS_FOR_FRAME, True)
         self.TouchInfo.TouchUUID = operation.GetString(self.AW_TOUCHSENS_UUID, True)
         self.TouchInfo.TouchLinkedFlag = operation.GetBool(self.AW_TOUCHSENS_LINKED_FLAG, True)
         if self.TouchInfo.TouchLinkedFlag:
            self.TouchInfo.TouchLinkedCounter += 1
         if self.ArcTech.FindFrameCounterCurrent == self.ArcTech.FindFrameCounter:
            self.TouchInfo.TouchOpCounter += 1
         else:
            self.TouchInfo.TouchOpCounter = 1
         
         self.TouchInfo.MotionTypeToStart = operation.GetLiteral('TouchSensMotionTypeFirstTpe', True) # LIN/PTP
         # get SeamFinding Parameters in Case of "Line Laser" (=SeamFinding)
         self.TouchInfo.SeamFindingMountType = operation.GetLiteralAttribute(self.KUKA_SEAM_FINDING_MOUNT_TYPE, True).GetIndex() # "KukaSeamFindingMountType"
         self.TouchInfo.SeamFindingRecipe = operation.GetLiteralAttribute(self.KUKA_SEAM_FINDING_RECIPE, True).GetIndex() # "KukaSeamFindingRecipe"
         self.TouchInfo.SeamFindingId = operation.GetInteger(self.KUKA_SEAMFIND_ID, True) # "SeamFindingId"
         self.TouchInfo.SeamFindJsonFolder = operation.GetString(self.AW_KUKA_TECH_TAB_FOLDER, True)
         pass

   def OperationEnd(self, operator : DULPythonDownloadOperator, operation : DULPythonOperation):
      super().OperationEnd(operator, operation)
      # Call correction frame macro once all touch points are processed in that group
      if self.WorkmethodName == self.WM_NAME_TOUCH:
            # add current touch to correction frame list for processing
            if self.TouchInfo.TouchOpCounter == self.TouchInfo.TouchOpsForCurrentFrame:
               self.OutputTouchSenseRegisterReset()
               # bPerformTouchSense condition commented out, To be debugged
               # self.Source.append('ENDIF')

      # Clear SeamTracking offset
      if self.WorkmethodName == self.WM_NAME_STICH and self.ArcTech.SeamTrackFlag:
         self.Source.append('\n;FOLD SeamTrack Clear ;%{PE}')
         self.Source.append('  ;FOLD Parameters Parameters ;%{h}')
         self.Source.append('    ;Params IlfProvider=SeamTrack.Clear')
         self.Source.append('  ;ENDFOLD')
         self.Source.append('  STTg_SensorClear()')
         self.Source.append(';ENDFOLD\n')
         #Reset SeamTracking flag
         self.ArcTech.SeamTrackFlag = False

   def OperationGroupEnd(self, operator : DULPythonDownloadOperator, operationGroup : DULPythonOperationGroup):
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OperationGroupEnd called")
      logger.LogDebug(operationGroup.GetName())

      # Reset touch sensing parameters
      self.TouchInfo.TouchLinkedFlag = False
      self.TouchInfo.TouchLinkedCounter = 0
      self.TouchInfo.TouchOpCounter = 0

      super().OperationGroupEnd(operator, operationGroup)

   def HandleReadAheadEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      """Handle Read Ahead event (After Events to be processed Before motion) e.g. GunOn/Off,GlueOn/Off,ArcOn/Off

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader HandleReadAheadEvent called")
      logger.LogDebug(event.GetName())

      # handle custom events
      self.HandleCustomReadAheadEvents(operator, event, motion)

      eventMotions = event.GetMotions()
      for eventMotion in eventMotions:
         self.HandleMotion(operator, eventMotion)

   def HandleCustomReadAheadEvents(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      eventName = event.GetName()
      # check if ARC ON event
      if eventName == 'ArcOnEvent':
         self.OutputArcOnEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if ARC OFF event
      elif eventName == 'ArcOffEvent':
         self.OutputArcOffEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # # check if SeamFindTeach event
      elif eventName == 'SeamFindTeach':
         # self.ArcTech.FindFrameCounter = event.GetIntegerAttribute(self.AW_EVT_TOUCH_ID, True).GetValue()
         # self.ArcTech.FindFramePointCounter = event.GetIntegerAttribute(self.AW_EVT_TOUCH_FRAME_PT, True).GetValue()
         self.OutputSeamFindingRefEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if SeamTrackingLeadIn event
      elif eventName == 'SeamTrackingLeadInEvent' or eventName == 'SeamTrackingEvent':
         self.OutputSeamTrackingLeadinEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if SeamTrackingOff event
      elif eventName == 'SeamTrackingOffEvent':
         self.OutputSeamTrackingOffEvent(operator, event, motion)
         # return to avoid potential double handling
         return

   def HandleEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      """Handle event

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader HandleEvents called")
      logger.LogDebug(event.GetName())

      # handle custom events
      self.HandleCustomEvents(operator, event, motion)

      super().HandleEvent(operator, event, motion)

   def HandleCustomEvents(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      eventName = event.GetName()
      # check if ARC ON event
      if eventName == 'ArcOnEvent':
         self.OutputArcOnEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if ARC OFF event
      elif eventName == 'ArcOffEvent':
         # Set processing flag for arc welding in original 'After' event (see base downloader for details)
         self.Tech.Processing = False

         self.OutputArcOffEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # apply correction frame computed by touch, seam search or seam finding operations
      elif eventName == 'ConnectTouchProcessPointEvent':
         # output E2 touch sensing
         self.HandleConnectTouchProcessPointEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # # check if TouchPointStartAppEvent
      elif eventName == 'TouchPointStartAppEvent':
         self.OutputTouchPointStartAppEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # # check if TouchPointCollisionEvent
      elif eventName == 'TouchPointCollisionEvent':
         self.OutputTouchPointCollisionEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # # check if TouchPointStartRetEvent
      elif eventName == 'TouchPointStartRetEvent':
         self.OutputTouchPointStartRetEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if SeamFindTeachEvent event
      # elif eventName == 'SeamFindTeachEvent' and self.TouchInfo.TouchSensAsSeamFind:
      elif eventName == 'SeamFindingScanEvent' and self.TouchInfo.TouchSensAsSeamFind:
         self.OutputSeamFindingScanEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # check if SeamTrackingOff event
      elif eventName == 'SeamTrackSearchStart':
         self.OutputSeamTrackingSearchStartEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      elif eventName == 'TpeAtStartEvent':
         # self.OutputTpeAtEndEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      elif eventName == 'TpeAtEndEvent':
         self.OutputTpeAtEndEvent(operator, event, motion)
         # return to avoid potential double handling
         return

      # # check if SeamTrackingOff event
      # elif eventName == 'SeamTrackingOffEvent':
      #    self.OutputSeamTrackingOffEvent(operator, event, motion)
      #    # return to avoid potential double handling
      #    return

   def OutputTpeAtStartEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputTpeAtStartEvent called")

   def OutputTpeAtEndEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputTpeAtEndEvent called")

   def _cluster_touches_by_direction(self, seam):
      """
      Cluster touch points by approach direction using agglomerative clustering.
      
      Uses 30° threshold and complete linkage (max distance within cluster).
      Sign-agnostic angle computation (treats opposite vectors as similar).
      
      Args:
         seam: SeamTouchSet containing touches with collision_xyz and start_xyz
         
      Returns:
         List of clusters, where each cluster is a list of TouchRecord objects
      """
      import math
      import numpy as np
      
      def normalize(v):
         """Normalize a vector."""
         mag = math.sqrt(sum(x*x for x in v))
         if mag < 1e-9:
            return v
         return tuple(x/mag for x in v)
      
      def angle_between_vectors(v1, v2):
         """Compute angle between two vectors in degrees (sign-agnostic)."""
         # Normalize
         n1 = normalize(v1)
         n2 = normalize(v2)
         
         # Dot product
         dot = sum(a*b for a, b in zip(n1, n2))
         # Clamp to [-1, 1] to handle numerical errors
         dot = max(-1.0, min(1.0, dot))
         
         # Sign-agnostic: use abs(dot)
         angle_rad = math.acos(abs(dot))
         return math.degrees(angle_rad)
      
      touches = seam.touches
      n = len(touches)
      
      if n == 0:
         return []
      if n == 1:
         return [[touches[0]]]
      
      # Compute approach vectors for all touches (in world/base frame)
      touch_vectors = {}
      for touch in touches:
         # Approach vector = collision - start (normalized)
         delta = tuple(c - s for c, s in zip(touch.collision_xyz, touch.start_xyz))
         mag = math.sqrt(sum(x*x for x in delta))
         if mag < 1e-9:
            touch_vectors[touch.touch_identifier] = (0.0, 0.0, 0.0)
         else:
            touch_vectors[touch.touch_identifier] = tuple(x/mag for x in delta)
      
      # Initialize: each touch in its own cluster
      clusters = [[touch] for touch in touches]
      
      # Agglomerative clustering with 30° threshold
      threshold = 30.0
      
      while True:
         # Find closest pair of clusters
         min_dist = float('inf')
         merge_i, merge_j = -1, -1
         
         for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
               # Complete linkage: max distance between any pair
               max_angle = 0.0
               for t1 in clusters[i]:
                  for t2 in clusters[j]:
                     v1 = touch_vectors[t1.touch_identifier]
                     v2 = touch_vectors[t2.touch_identifier]
                     angle = angle_between_vectors(v1, v2)
                     max_angle = max(max_angle, angle)
               
               if max_angle < min_dist:
                  min_dist = max_angle
                  merge_i, merge_j = i, j
         
         # Stop if closest pair exceeds threshold
         if min_dist > threshold:
            break
         
         # Merge clusters
         if merge_i != -1 and merge_j != -1:
            clusters[merge_i].extend(clusters[merge_j])
            del clusters[merge_j]
         else:
            break
      
      return clusters

   def _assign_cluster_hints(self, clusters, seam):
      """
      Assign bucket hints to touches based on cluster sizes.
      
      Cluster size 3 → "Z", size 2 → "Y", size 1 → "X"
      
      IMPORTANT: Skips touches that already have hints (e.g., from progressive linked mapping).
      
      Args:
         clusters: List of clusters from _cluster_touches_by_direction
         seam: SeamTouchSet (used for logging context)
      """
      # Sort clusters by size (descending) for consistent assignment
      sorted_clusters = sorted(clusters, key=len, reverse=True)
      
      for cluster in sorted_clusters:
         size = len(cluster)
         
         if size == 3:
            hint = "Z"
         elif size == 2:
            hint = "Y"
         else:  # size == 1
            hint = "X"
         
         # Assign hint to touches in cluster that don't already have a hint
         for touch in cluster:
            if touch.bucket_hint is None:
               touch.bucket_hint = hint

   def HandleConnectTouchProcessPointEvent(self, operator : DULPythonDownloadOperator, event : DULPythonEvent, motion : DULPythonMotion):
      controller = operator.GetController()
      techTabFolder = controller.GetTechTabFolder(RECIPES_FILENAME)
      if self.TouchInfo.SensorToolType == 'Line Laser':
         # Create an instance of the SeamFind Output Class
         # KUKA_SEAM_FINDING_MOUNT_TYPE = "KukaSeamFindingMountType"
         # KUKA_SEAM_FINDING_RECIPE = "KukaSeamFindingRecipe"
         # KUKA_SEAMFIND_ID = "SeamFindingId"
         builder = SeamFindGenerator(
               self.TouchInfo.SeamFindingRecipe+1,
               self.TouchInfo.SeamFindingMountType+1,
               self.TouchInfo.SeamFindingId,
               self.TouchInfo.SeamFindJsonFolder,
               techTabFolder,
               self.ArcTech.TotalMeaCounter,
               None,
               # self.TouchInfo.TouchOpsForCurrentFrame
               self.ArcTech.SeamTechFindingVersionDAT
         )
         # Get the generated string
         self.AddLineToSource(builder.build())
         self.TouchInfo.TouchSensAsSeamFind = False
         self.ArcTech.SeamFindOpsInGroupCounter = 0

         return # !!! exit, if "Line Laser" == 3  ["Touch Sensor", "Point Laser", "Line Laser"] !! [1,2,3]
      
      if self.TouchInfo.TouchConnectionType == 'Frame3pConnect':
         touchCorrectionID = str(event.GetStringAttribute(self.AW_EVT_TOUCH_ID, True).GetValue())
         
         # Find seam by touchCorrectionID
         seam: SeamTouchSet = self.TouchInfo.TouchSets.get(touchCorrectionID, None)
         if seam is None:
            logger = operator.GetLogOperator()
            logger.LogError(f"SeamTouchSet with TouchId {touchCorrectionID} not found")
            return
         
         # Parse direction strings and convert to tuples
         appr_dir_str = event.GetStringAttribute('ApprDirX', True).GetValue()
         tool_dir_str = event.GetStringAttribute('ApprDirZ', True).GetValue()
         
         # Convert strings to tuples
         try:
            import ast
            appr_dir_tuple = ast.literal_eval(appr_dir_str)
            tool_dir_tuple = ast.literal_eval(tool_dir_str)
            
            # Validate that they're tuples with 3 elements
            if isinstance(appr_dir_tuple, tuple) and len(appr_dir_tuple) == 3:
               seam.tangent_at_arcon_xyz = appr_dir_tuple
            else:
               seam.tangent_at_arcon_xyz = (1.0, 0.0, 0.0)  # Default
                
            if isinstance(tool_dir_tuple, tuple) and len(tool_dir_tuple) == 3:
               seam.tool_z_at_arcon_in_base = tool_dir_tuple
            else:
               seam.tool_z_at_arcon_in_base = (0.0, 0.0, 1.0)  # Default
         except (ValueError, IndexError) as e:
             logger = operator.GetLogOperator()
             logger.LogWarn(f"Could not parse direction vectors: ApprDirX='{appr_dir_str}', ApprDirZ='{tool_dir_str}', Error: {e}")
             seam.tangent_at_arcon_xyz = (1.0, 0.0, 0.0)  # Default X direction
             seam.tool_z_at_arcon_in_base = (0.0, 0.0, 1.0)  # Default Z direction

         # Debug: Check seam contents
         logger = operator.GetLogOperator()
         logger.LogDebug(f"Seam {touchCorrectionID} contains {len(seam.touches)} touches:")
         for i, touch in enumerate(seam.touches):
             logger.LogDebug(f"  Touch {i+1}: {touch.touch_identifier}, linked={touch.linked}, link_seq={touch.link_seq}")

         # PROGRESSIVE HINTS: Assign automatic bucket hints to linked touches
         # This must happen BEFORE clustering to ensure progressive seq mapping takes priority
         for touch in seam.touches:
             if touch.linked and touch.bucket_hint is None:
                 if touch.link_seq == 1:
                     touch.bucket_hint = "Z"
                     logger.LogDebug(f"  Auto-assigned {touch.touch_identifier} (seq=1) → Z-bucket")
                 elif touch.link_seq == 2:
                     touch.bucket_hint = "Y"
                     logger.LogDebug(f"  Auto-assigned {touch.touch_identifier} (seq=2) → Y-bucket")
                 elif touch.link_seq == 3:
                     touch.bucket_hint = "X"
                     logger.LogDebug(f"  Auto-assigned {touch.touch_identifier} (seq=3) → X-bucket")

         # CLUSTERING: Assign bucket hints based on directional clustering
         # Only clusters touches WITHOUT existing hints (i.e., non-linked touches)
         clusters = self._cluster_touches_by_direction(seam)
         self._assign_cluster_hints(clusters, seam)
         
         # Debug: Show clustering results
         logger.LogDebug(f"Directional clustering found {len(clusters)} clusters:")
         for i, cluster in enumerate(clusters):
            hint = cluster[0].bucket_hint if cluster else "None"
            identifiers = [t.touch_identifier for t in cluster]
            logger.LogDebug(f"  Cluster {i+1} (size={len(cluster)}, hint={hint}): {identifiers}")

         # Route ALL touches in the seam using the actual seam frame
         router = TouchRouter()
         try:
            routed_full = router.route(seam, subset_filter=None, mode="final")
         except ValueError as e:
            # Log the error with FASTSUITE logger and re-raise
            logger = operator.GetLogOperator()
            logger.LogError(str(e))
            raise
         
         logger.LogDebug(f"Routed bins - X: {routed_full.X}, Y: {routed_full.Y}, Z: {routed_full.Z}")
         logger.LogDebug(f"Total touches routed: {len(routed_full.X) + len(routed_full.Y) + len(routed_full.Z)}")
         
         # Emit "Corr Free" fold with all touches
         # self.AddLineToSource('; Seam: '+str(seam))
         # self.AddLineToSource('; Tangent: '+str(seam.tangent_at_arcon_xyz)+', ToolZ: '+str(seam.tool_z_at_arcon_in_base))
         
         # Determine if rotation is involved:
         # - 2 touches in Y bucket → rotation around Z axis
         # - 3 touches in Z bucket → full 6D correction
         # Otherwise → translation-only (use progressive named fold)
         has_rotation = (len(routed_full.Y) >= 2) or (len(routed_full.Z) >= 2)
         
         if has_rotation:
            # Use full 6D fold for rotation cases
            fold_text = TouchRouter.emit_fold(routed_full, title_hint="TouchSense Corr Free")
            self.AddLineToSource(fold_text)
         else:
            # Use progressive named fold for translation-only cases
            # Gather all routed touches in spec order: Z→Y→X
            # routed_full contains touch_identifiers (e.g., "TS1M1"), need symbols with "CD" prefix
            all_syms = []
            for tid in routed_full.Z:
               all_syms.append("CD" + tid)
            for tid in routed_full.Y:
               all_syms.append("CD" + tid)
            for tid in routed_full.X:
               all_syms.append("CD" + tid)
            
            fold_text = _emit_progressive_named_fold(all_syms)
            if fold_text:
               self.AddLineToSource(fold_text)

   def OutputTouchPointStartAppEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputTouchPointStartAppEvent called")
      self.TouchInfo.TouchStartName = motion.GetName()
      self.TouchInfo.TouchStartPosition = motion.GetPosition().GetXYZ()
      if motion.IsLinearMotion():
         self.TouchInfo.MotionTypeToStart = "LIN"
      else:
         self.TouchInfo.MotionTypeToStart = "PTP"
      self.SuppressNextSource = True
      self.NoNextSource = True
      # self.DownloadReferenceMotion = True

   def OutputTouchSenseRegisterReset(self):
      if self.TouchInfo.TouchConnectionType == 'Frame3pConnect':
         self.TouchInfo.TouchGroupInit = False
         # Reset the touch operation counter
         self.TouchInfo.TouchOpsForCurrentFrame = 0
         self.TouchInfo.TouchOpCounter = 0

      self.Source.append(';Register reset/resetting records')
      self.Source.append(';FOLD TouchSense Corr Off ;%{PE}')
      self.Source.append('  ;FOLD Parameters Corr Off ;%{h}')
      self.Source.append('    ;Params IlfProvider=KukaRoboter.TouchSense.CorrectionOFF')
      self.Source.append('    ;ENDFOLD')
      self.Source.append('  TS_CorrOff()')
      self.Source.append(';ENDFOLD')
      # Reset the touch operation counter

   def OutputTouchPointCollisionEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputTouchPointCollisionEvent called")

      if self.ArcTech.FindFrameCounterCurrent == self.ArcTech.FindFrameCounter:
         # New 6D touch correction handling - no more point counter
         self.ArcTech.FindFramePointMeaCounter += 1
      else:
         self.ArcTech.FindFrameCounterCurrent = self.ArcTech.FindFrameCounter
         # New 6D touch correction handling - no more point counter
         self.ArcTech.FindFramePointMeaCounter = 1

      self.ArcTech.TotalMeaCounter += 1

      if self.TouchInfo.TouchConnectionType == 'Frame3pConnect':
         self.SpecialPosName = 'TS'+f'{self.ArcTech.FindFrameCounter:d}'+'M'+f'{self.ArcTech.FindFramePointMeaCounter:d}'
      else:
         self.SpecialPosName = 'TS'+f'{self.ArcTech.FindFrameCounter:d}'+'M'+f'{self.ArcTech.FindFramePointMeaCounter:d}'

      self.ArcTech.FramePosName = self.SpecialPosName
      self.TouchInfo.TouchCorrFrameIdList.append('VCD'+self.ArcTech.FramePosName)
      self.NoNextSource = True
      self.SuppressNextSource = False
      self.DownloadReferenceMotion = True

      # reset the touch sensing at the beginning of the touch operation
      if not (self.TouchInfo.TouchConnectionType == 'Frame3pConnect'):
         if self.TouchInfo.TouchOpCounter == 1:
            self.OutputTouchSenseRegisterReset()
            self.TouchInfo.UsedFramePosNames.clear()

      # Source output Linear
      if self.TouchInfo.MotionTypeToStart == 'LIN':
         self.Source.append(';FOLD TouchSense SEARCH LIN '+self.TouchInfo.TouchStartName+' Vel='+ str(self.CurrentLinVelocity) +' m/s CPDAT'+self.TouchInfo.TouchStartName+' VIA '+self.ArcTech.FramePosName+' CD'+self.ArcTech.FramePosName+' SP'+self.ArcTech.FramePosName+
                                 " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName +
                                 " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         self.Source.append('  ;FOLD Parameters ;%{h}')
         self.Source.append('    ;Params IlfProvider=kukaroboter.touchsense.searchlin; Kuka.IsGlobalPoint=False; Kuka.PointName='+self.TouchInfo.TouchStartName+';'\
            +' Kuka.BlendingEnabled=False; Kuka.MoveDataName=CPDAT'+self.TouchInfo.TouchStartName+'; Kuka.VelocityPath='+ str(self.CurrentLinVelocity) +'; Kuka.CurrentCDSetIndex=0;'\
            +' Kuka.MovementParameterFieldEnabled=True; MoveType=LIN')
      else:
         self.Source.append(';FOLD TouchSense SEARCH PTP '+self.TouchInfo.TouchStartName+' Vel='+ str(self.CurrentPtpVelocity) +' % PDAT'+self.TouchInfo.TouchStartName+' VIA '+self.ArcTech.FramePosName+' CD'+self.ArcTech.FramePosName+' SP'+self.ArcTech.FramePosName+
                                 " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName +
                                 " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         self.Source.append('  ;FOLD Parameters ;%{h}')
         self.Source.append('    ;Params IlfProvider=kukaroboter.touchsense.searchptp; Kuka.IsGlobalPoint=False; Kuka.PointName='+self.TouchInfo.TouchStartName+';'\
            +' Kuka.BlendingEnabled=False; Kuka.MoveDataPtpName=PDAT'+self.TouchInfo.TouchStartName+'; Kuka.VelocityPtp='+ str(self.CurrentPtpVelocity) +'; Kuka.CurrentCDSetIndex=0;'\
            +' Kuka.MovementParameterFieldEnabled=True; MoveType=PTP')

      self.Source.append('    ;FOLD Parameters TouchSense ;%{h}')
      self.Source.append('      ;Params TouchSense.SearchViaPoint='+self.ArcTech.FramePosName+'; TouchSense.ReferenceMove=CD'+self.ArcTech.FramePosName+'; TouchSense.SearchParam=SP'+self.ArcTech.FramePosName+'; TouchSense.Sensor='+str(self.TouchInfo.SensorId))
      self.Source.append('    ;ENDFOLD')
      self.Source.append('  ;ENDFOLD')
         
      self.Source.append('  $BWDSTART = FALSE')
      if self.TouchInfo.MotionTypeToStart == 'LIN':
         self.Source.append('  LDAT_ACT = LCPDAT'+self.TouchInfo.TouchStartName+'')
         self.Source.append('  FDAT_ACT = F'+self.TouchInfo.TouchStartName+'')
         self.Source.append('  BAS(#CP_PARAMS, '+ str(self.CurrentLinVelocity) +')')
         self.Source.append('  SET_CD_PARAMS (0)')
         self.Source.append('  LIN X'+self.TouchInfo.TouchStartName+'')
      else:
         self.Source.append('  PDAT_ACT = PPDAT'+self.TouchInfo.TouchStartName+'')
         self.Source.append('  FDAT_ACT = F'+self.TouchInfo.TouchStartName+'')
         self.Source.append('  BAS(#PTP_PARAMS, '+ str(self.CurrentPtpVelocity) +')')
         self.Source.append('  SET_CD_PARAMS (0)')
         self.Source.append('  PTP X'+self.TouchInfo.TouchStartName+'')

      self.Source.append('  TS_InitMovement($POS_ACT, X'+self.ArcTech.FramePosName+', ZSP'+self.ArcTech.FramePosName+')')
      self.Source.append('  TS_ManMoveToVia(X'+self.ArcTech.FramePosName+')')
      self.Source.append('  TS_Search(X'+self.ArcTech.FramePosName+', ZSP'+self.ArcTech.FramePosName+', VCD'+self.ArcTech.FramePosName+')')
      self.Source.append('  TS_SetCorrData(ZSP'+self.ArcTech.FramePosName+', VCD'+self.ArcTech.FramePosName+')')
      self.Source.append(';ENDFOLD\n')

      # Populate TouchRecord class and append to SeamTouchSet if using Frame3pConnect
      # Then output progressive fold if linked touch
      if self.TouchInfo.TouchConnectionType == 'Frame3pConnect':
         # --- Create or retrieve the seam ---
         collisionPosition = motion.GetPosition().GetXYZ()
         touch_corr_id = str(self.ArcTech.FindFrameCounter)
         if touch_corr_id not in self.TouchInfo.TouchSets:
            # First touch for this correction ID - create new SeamTouchSet
            self.TouchInfo.TouchSets[touch_corr_id] = SeamTouchSet(
               touch_corr_id=touch_corr_id,
               uuid=self.TouchInfo.TouchUUID,
               tangent_at_arcon_xyz=(1.0, 0.0, 0.0),          # Default: X direction
               tool_z_at_arcon_in_base=(0.0, 0.0, 1.0),       # Default: Z direction
            )
         
         seam = self.TouchInfo.TouchSets[touch_corr_id]
         
         # --- Create TouchRecord (bucket_hint will be assigned by clustering) ---
         touch_record = TouchRecord(
            touch_corr_id=touch_corr_id,
            uuid=seam.uuid,
            touch_identifier=self.SpecialPosName,
            symbol='CD' + self.SpecialPosName,
            start_xyz=tuple(self.TouchInfo.TouchStartPosition),
            collision_xyz=tuple(collisionPosition),
            linked=self.TouchInfo.TouchLinkedFlag,
            link_seq=self.TouchInfo.TouchLinkedCounter if self.TouchInfo.TouchLinkedFlag else None,
            bucket_hint=None,  # Will be assigned by directional clustering
         )
         seam.touches.append(touch_record)
         
         # --- Emit progressive fold if this is a linked touch ---
         if self.TouchInfo.TouchLinkedFlag and self.TouchInfo.TouchLinkedCounter in (1, 2, 3):
            # Gather all linked touches up to current link_seq, sorted
            linked_touches = [
               t for t in seam.touches 
               if t.linked and t.link_seq is not None and t.link_seq <= self.TouchInfo.TouchLinkedCounter
            ]
            linked_touches.sort(key=lambda t: t.link_seq)
            linked_syms = [t.symbol for t in linked_touches]
            
            fold_text = _emit_progressive_named_fold(linked_syms)
            if fold_text:
               self.AddLineToSource(fold_text)
               logger.LogDebug(f"Emitted progressive {self.TouchInfo.TouchLinkedCounter}D fold for {self.SpecialPosName}")


      # DATA output
      currBaseXYZ = self.CurrentBase.GetXYZ()
      currBaseRot = self.CurrentBase.GetOrientation()
      xyz = motion.GetPosition().GetXYZ()
      angles = motion.GetPosition().GetOrientation()
      refWPos_world = "X {:.6f}".format(xyz[0]*1000) + ",Y {:.6f}".format(xyz[1]*1000) + ",Z {:.6f}".format(xyz[2]*1000) +\
               ",A {:.6f}".format(angles[2]) + ",B {:.6f}".format(angles[1]) + ",C {:.6f}".format(angles[0])

      tempStr1 = 'DECL TSg_PCollCD_T VCD'+self.ArcTech.FramePosName+'={CD_IPO_MODE #BASE,Mastered '+str(self.ArcTech.CadMastered).upper()+',SDir_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},Ref_W {'+refWPos_world+\
               '},Meas_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},Diff_W {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},VecLenDiff_W 0.0,MEnum #CDEmpty,MC 1}'
      tempStr2 = 'DECL TSg_SearchProperty_T ZSP'+self.ArcTech.FramePosName+'={MoveType #MoveWithLin,TouchType #Single,DynamicStep #Slow,'+\
               'SensorNum '+str(self.TouchInfo.SensorId)+',SearchDepth_Tol 50.0000,bBackToStartPos TRUE,PartThickness 0.0}'

      if self.Tech.SortDat:
         self.DataTechDAT2.append(tempStr1)
         self.DataTechDAT2.append(tempStr2)
      else:
         self.AddLineToData(tempStr1)
         self.AddLineToData(tempStr2)
      # Reset special naming
      # self.SpecialPosName = ''

      # self.SuppressNextSource = True
      # self.DownloadReferenceMotion = True

   def OutputTouchPointStartRetEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputTouchPointStartRetEvent called")
      self.TouchInfo.TouchEndName = motion.GetName()
      # self.SuppressNextSource = False
      ## self.DownloadReferenceMotion = True
      self.SuppressNextSource = True
      self.NoNextSource = True

   def OutputSeamFindingRefEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputArcOnEvent called")

      if self.ArcTech.SeamFindFirstOp:
         self.AddLineToSourceHeader(';FOLD SeamFind Init ;%{PE}')
         self.AddLineToSourceHeader(';FOLD Parameters Parameters ;%{h}')
         self.AddLineToSourceHeader(';Params IlfProvider=SeamFind.SensorInit')
         self.AddLineToSourceHeader(';ENDFOLD')
         self.AddLineToSourceHeader('BF_INIT(true)')
         self.AddLineToSourceHeader(';ENDFOLD')
         self.ArcTech.SeamFindFirstOp = False

      self.ArcTech.SeamFindFlag = True

   def OutputSeamFindingScanEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputSeamFindingScanEvent called")

      if self.ArcTech.SeamFindFirstOp:
         if self.ArcTech.SeamTechFindingVersionDAT < '400000000':
            self.AddLineToSourceHeader(';FOLD SeamFind Init ;%{PE}')
            self.AddLineToSourceHeader(';FOLD Parameters Parameters ;%{h}')
            self.AddLineToSourceHeader(';Params IlfProvider=SeamFind.SensorInit')
            self.AddLineToSourceHeader(';ENDFOLD')
            self.AddLineToSourceHeader('BF_INIT(true)')
            self.AddLineToSourceHeader(';ENDFOLD')
         else:
            self.AddLineToSourceHeader(';FOLD SeamFind Init Sensor '+f'{self.TouchInfo.SensorId:d}'+':;%{PE}')
            self.AddLineToSourceHeader(';FOLD Parameters Parameters ;%{h}')
            self.AddLineToSourceHeader(';Params IlfProvider=SeamFind.SensorInit;SeamFind.SensorNo='+f'{self.TouchInfo.SensorId:d}')
            self.AddLineToSourceHeader(';ENDFOLD')
            self.AddLineToSourceHeader('BF_Init(1)')
            self.AddLineToSourceHeader(';ENDFOLD')


         self.AddLineToSourceHeader('\n')
         self.AddLineToSourceHeader(';FOLD SeamFind Corr Off ;%{PE}')
         self.AddLineToSourceHeader(';FOLD Parameters Parameters ;%{h}')
         self.AddLineToSourceHeader(';Params IlfProvider=SeamFind.CorrOff')
         self.AddLineToSourceHeader(';ENDFOLD')
         self.AddLineToSourceHeader('BF_CorrOff()')
         self.AddLineToSourceHeader(';ENDFOLD')
         self.ArcTech.SeamFindFirstOp = False

      self.ArcTech.TotalMeaCounter += 1
      # self.SpecialPosName is used in basic downloader and then reset to ''
      self.SpecialPosName = motion.GetName()  # use the motion name as the special position name

      self.NoNextSource = True
      self.SuppressNextSource = False
      self.DownloadReferenceMotion = True

      # Source output
      if self.ArcTech.SeamTechFindingVersionDAT >= '400000000':
         jointTypeStr = 'Task'
      else:
         jointTypeStr = 'JointTypeIDX'

      if self.TouchInfo.MotionTypeToStart == 'LIN':
         self.Source.append(';FOLD SeamFind Measure LIN '+self.SpecialPosName+' Vel='+ str(self.CurrentLinVelocity) +' m/s CPDAT'+self.SpecialPosName+
                                 ' Measure ATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+' Static '
                                 " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName +
                                 " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         self.Source.append('  ;FOLD Parameters ;%{h}')
         self.Source.append('    ;Params IlfProvider=seamfind.measurelin; Kuka.IsGlobalPoint=False; Kuka.PointName='+self.SpecialPosName+
                           '; Kuka.BlendingEnabled=False; Kuka.MoveDataName=CPDAT'+self.SpecialPosName+'; Kuka.VelocityPath='+ str(self.CurrentLinVelocity) +'; Kuka.CurrentCDSetIndex=0;'+
                           ' Kuka.MovementParameterFieldEnabled=True; SeamFind.Attribute=ATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'; SeamFind.Behavior=Static')
         self.Source.append('  ;ENDFOLD')
         self.Source.append('  $BWDSTART = FALSE')
         self.Source.append('  LDAT_ACT = LCPDAT'+self.SpecialPosName)
         self.Source.append('  FDAT_ACT = F'+self.SpecialPosName)
         self.Source.append('  BAS(#CP_PARAMS, '+ str(self.CurrentLinVelocity) +')')
         self.Source.append('  SET_CD_PARAMS (0)')
         self.Source.append('  LIN X'+self.SpecialPosName+'')
      else:
         self.Source.append(';FOLD SeamFind Measure PTP '+self.SpecialPosName+' Vel='+ str(self.CurrentPtpVelocity) +' % PDAT'+self.SpecialPosName+
                                 ' '+jointTypeStr+'='+self.SeamFindJointType+' ATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+' Static '
                                 " Tool[" + str(self.CurrentToolIndex) + "]:" + self.CurrentToolName +
                                 " Base[" + str(self.CurrentBaseIndex) + "]:" + self.CurrentBaseName + " ;%{PE}")
         self.Source.append('  ;FOLD Parameters ;%{h}')
         self.Source.append('    ;Params IlfProvider=seamfind.measureptp; Kuka.IsGlobalPoint=False; Kuka.PointName='+self.SpecialPosName+
                                 '; Kuka.BlendingEnabled=False; Kuka.MoveDataPtpName=PDAT'+self.SpecialPosName+'; Kuka.VelocityPtp='+ str(self.CurrentPtpVelocity) +'; Kuka.CurrentCDSetIndex=0;'+
                                 ' Kuka.MovementParameterFieldEnabled=True; SeamFind.Attribute=ATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'; SeamFind.Behavior=Static')
         self.Source.append('  ;ENDFOLD')
         self.Source.append('  $BWDSTART = FALSE')
         self.Source.append('  PDAT_ACT = PPDAT'+self.SpecialPosName)
         self.Source.append('  FDAT_ACT = F'+self.SpecialPosName)
         self.Source.append('  BAS(#PTP_PARAMS, '+ str(self.CurrentPtpVelocity) +')')
         self.Source.append('  SET_CD_PARAMS (0)')
         self.Source.append('  PTP X'+self.SpecialPosName+'')
 
      self.Source.append('  BF_InitMovement($POS_ACT, $POS_ACT, BFMPDefault)')
      self.Source.append('  BF_Search($POS_ACT, BFMPDefault, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d})')
      self.Source.append('  BF_SetCorrData(BFMPDefault, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+
                        ', BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'_CD1, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+
                        '_CD2, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'_CD3, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+
                        '_CD4, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'_CD5, BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'_CD6)')
      self.Source.append(';ENDFOLD')

      # DATA output
      if self.ArcTech.SeamTechFindingVersionDAT >= '400000000':
         jointTypeStr = 'TaskId'
      else:
         jointTypeStr = 'JointTypeIDX'

      tempStr1 = '' ; tempStr2 = ''; tempStr3 = ''; tempStr4 = ''; tempStr5 = ''; tempStr6 = ''; tempStr7 = ''
      if not self.ArcTech.CadMastered:
         tempStr1 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD1={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr2 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD2={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr3 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD3={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr4 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD4={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr5 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD5={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr6 = 'DECL BFg_PCollCD_T BFATTR' +f'{self.ArcTech.TotalMeaCounter:d}'+'_CD6={CD_IPO_MODE #NotDefined,Mastered FALSE,MEnum #CDEmpty,MC 1}'
         tempStr7 = 'DECL BFg_PColl_T BFATTR'+f'{self.ArcTech.TotalMeaCounter:d}'+'={Name[] "'+self.SpecialPosName+'",'+jointTypeStr+' '+self.SeamFindJointType+',Dimension 0,ForceMastering TRUE,SensMeasData {MeasFrame {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},MeasFrameRaw {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},Area 0.0,Gap 0.0,Mismatch 0.0,Angle2 0.0,Reserve1 0.0,Reserve2 0.0,Quality 0.0,SensResponse FALSE},MEnum #PCollEmpty,MC 1}'
      else:
         logger.LogInfo("KukaPythonDownloader: Using CAD Mastered data for Seam Finding not supported")
         logger.LogInfo("KukaPythonDownloader: Effort to calibrate cell too high to achive usable results")

      if self.Tech.SortDat:
         self.DataTechDAT2.append(tempStr1)
         self.DataTechDAT2.append(tempStr2)
         self.DataTechDAT2.append(tempStr3)
         self.DataTechDAT2.append(tempStr4)
         self.DataTechDAT2.append(tempStr5)
         self.DataTechDAT2.append(tempStr6)
         self.DataTechDAT2.append(tempStr7)
      else:
         self.AddLineToData(tempStr1)
         self.AddLineToData(tempStr2)
         self.AddLineToData(tempStr3)
         self.AddLineToData(tempStr4)
         self.AddLineToData(tempStr5)
         self.AddLineToData(tempStr6)
         self.AddLineToData(tempStr7)
      # Reset special naming
      # self.SpecialPosName = ''

   def OutputSeamTrackingLeadinEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputSeamTrackingLeadinEvent called")

      # Source output
      # if self.ArcTech.SeamTrackFirstOp:
      #    self.SourceHeader.append('\n;FOLD SeamTrack Init ;%{PE}')
      #    self.SourceHeader.append('  ;FOLD Parameters Parameters ;%{h}')
      #    self.SourceHeader.append('    ;Params IlfProvider=SeamTrack.SensorInit')
      #    self.SourceHeader.append('  ;ENDFOLD')
      #    self.SourceHeader.append('  STTg_SensorInit(False)')
      #    self.SourceHeader.append(';ENDFOLD')
      #    self.ArcTech.SeamTrackFirstOp = False

      # Get SeamTracking attributes
      trackingOnDistance = self.CurrentOperation.GetDouble('KukaTrackingOnDistance', True)*1000
      # trackingOnDistance = self.CurrentOperation.GetDouble('SeamTrackingDistance', True)*1000
      trackingSetId = self.CurrentOperation.GetString('KukaTrackingSetId', True)
      trackingSeamPatternNr = self.CurrentOperation.GetInteger('KukaTrackingSeamPatternNr', True)
      trackingSearchLength = self.CurrentOperation.GetDouble('KukaTrackingSearchLength', True)*1000
      trackingContAfterErrIdx = self.CurrentOperation.GetLiteralAttribute('KukaTrackingContAfterErr', True).GetIndex()
      if trackingContAfterErrIdx == 0:
         trackingContAfterErr = '#RestartWithoutOffset'
      else:
         trackingContAfterErr = '#RestartWithOffset'
      # CBe: to clearify
      trackingContAfterErr = '#RestartWithOffset'

      trackingMaxLinCorrection = self.CurrentOperation.GetDouble('KukaTrackingMaxLinCorrection', True)*1000
      trackingCorrElimDistance = self.CurrentOperation.GetDouble('KukaTrackingCorrElimDistance', True)*1000

      # Source output
      self.Source.append('\n;FOLD SeamTrack Init ;%{PE}')
      self.Source.append('  ;FOLD Parameters Parameters ;%{h}')
      self.Source.append('    ;Params IlfProvider=SeamTrack.SensorInit')
      self.Source.append('  ;ENDFOLD')
      self.Source.append('  STTg_SensorInit(False)')
      self.Source.append(';ENDFOLD')

      self.Source.append('\n;FOLD SeamTrack On Dist='+f'{trackingOnDistance:.1f}'+' mm Set='+trackingSetId+' ;%{PE}')
      self.Source.append('  ;FOLD Parameters Parameters ;%{h}')
      self.Source.append('    ;Params IlfProvider=SeamTrack.SensorDynamic;SeamTrack.DistanceOn='+f'{trackingOnDistance:.1f}'+';SeamTrack.SensorSet='+trackingSetId+'')
      self.Source.append('  ;ENDFOLD')
      self.Source.append('  STTg_Para_Act = STT'+trackingSetId+'')
      self.Source.append('  STTg_Para_Act.GainOrientation = STTDefault.GainOrientation')
      self.Source.append('  STTg_Para_Act.GainToolNormale = STTDefault.GainToolNormale')
      self.Source.append('  TRIGGER WHEN PATH='+f'{trackingOnDistance:.1f}'+' DELAY=0 DO STTg_SensorOn(STTg_Para_Act) PRIO = -1')
      self.Source.append(';ENDFOLD')

      # Track the values of trackingSetId
      if not hasattr(self, 'trackingSetIds'):
         self.trackingSetIds = set()

      if trackingSetId not in self.trackingSetIds:
         self.trackingSetIds.add(trackingSetId)

         tempStr1 = 'DECL STTg_SensorSet_T STT'+trackingSetId+'={SeamFileNr '+f'{trackingSeamPatternNr:d}'+',SearchLength '+f'{int(trackingSearchLength):d}'\
            +',ErrorReaction '+trackingContAfterErr+',AbsPositionCorr '+f'{trackingMaxLinCorrection:.4f}'+',AbsAngleCorr 0.0,Vel_LeavePositionCorr '+f'{trackingCorrElimDistance:.3f}'+',Vel_LeaveAngleCorr 0.0,GainOrientation 0.0,GainToolNormale 0.0,WeldProcessOn 1.00000,OutOfBoundTol 5.00000,SeamLostTol 10.0000}'
         if self.Tech.SortDat:
            self.DataTechDAT2.append(tempStr1)
         else:
            self.AddLineToData(tempStr1)

      # Set SeamTracking flag
      self.ArcTech.SeamTrackFlag = True

   def OutputSeamTrackingSearchStartEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      positionName = motion.GetPosition().GetName()
      motionFrames = 'F' + positionName
      motionProfile = 'CPDAT' + positionName
      robotVelocity = self.ConvertVelocity(self.ArcOnInfo.KukaRobotVelocity1, self.Tech.VelocityUnitTechnology)/60

      if self.ArcTech.OutputSeamTrackSearchStart:
         dirInc = self.increment_string(motion.GetName())
         posInc = self.increment_string('X' + positionName)
         motionFramesInc = self.increment_string(motionFrames)

         if motion.IsPtPMotion():
            motionProfileActSet = "P" + motionProfile
         else:
            motionProfileActSet = "L" + motionProfile
         motionProfileActSetInc = self.increment_string(motionProfileActSet)

         self.Source.append(f'\n;FOLD SeamTrack Search Start Target={motion.GetName()} Dir={dirInc} Vel='+str(self.ArcTech.SeamTrackSearchSpeed)+' m/s ;%{{PE}}')
         self.Source.append(f'  ;FOLD Parameters Parameters ;%{{h}}')
         self.Source.append(f'    ;Params IlfProvider=SeamTrack.SearchStart;SeamTrack.Target={motion.GetName()};SeamTrack.Dir={dirInc};Kuka.VelocityPath='+str(self.ArcTech.SeamTrackSearchSpeed))
         self.Source.append(f'  ;ENDFOLD')
         self.Source.append(f'  INTERRUPT DECL STTg_SearchInterrupt WHEN $SEN_PINT[STTg_FindReturn_Indx] == 1 DO STTg_BrakeMove( X{motion.GetName()} )')
         self.Source.append(f'  INTERRUPT ON STTg_SearchInterrupt')
         self.Source.append(f'  STTg_SearchLin({'X' + positionName},{motionFrames},{motionProfileActSet},{posInc},{motionFramesInc},{motionProfileActSetInc},'+str(self.ArcTech.SeamTrackSearchSpeed)+')')
         self.Source.append(f';ENDFOLD')

         if self.ArcTech.OutputSeamTrackStartFooterWritten == False:
            self.AddLineToDataFooter(f'DECL MODULEPARAM_T LAST_TP_PARAMS={{PARAMS[] "SeamTrack.Target={motion.GetName()}; SeamTrack.Dir={dirInc}; Kuka.VelocityPath={robotVelocity}"}}')
            self.ArcTech.OutputSeamTrackStartFooterWritten = True

   def OutputSeamTrackingEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputSeamTrackingEvent called")

   def OutputSeamTrackingOffEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputSeamTrackingOffEvent called")

      # Get SeamTracking attributes
      trackingOffDistance = self.CurrentOperation.GetDouble('KukaTrackingOffDistance', True)*1000
      # trackingOffDistance = self.CurrentOperation.GetDouble('SeamTrackingDistance', True)*1000
      trackingOffKeepDistance = self.CurrentOperation.GetBool('KukaTrackingOffKeepDistance', True)

      # Source output before ARCOFF
      self.Source.append('\n;FOLD SeamTrack Off Dist='+f'{trackingOffDistance:.1f}'+' mm Keep Offset='+str(trackingOffKeepDistance).upper()+' ;%{PE}')
      self.Source.append('  ;FOLD Parameters Parameters ;%{h}')
      self.Source.append('    ;Params IlfProvider=SeamTrack.SensorOff;SeamTrack.DistanceOff='+f'{trackingOffDistance:.1f}'+';SeamTrack.KeepOffset='+str(trackingOffKeepDistance).upper()+'')
      self.Source.append('  ;ENDFOLD')
      self.Source.append('  STTg_OffVar = '+f'{trackingOffDistance:.1f}'+' + STTg_DeltaPath')
      self.Source.append('  TRIGGER WHEN PATH=STTg_OffVar DELAY=STTg_DeltaTime DO STTg_SensorOff3('+str(trackingOffKeepDistance).upper()+') PRIO = -1')
      self.Source.append('  TRIGGER WHEN PATH=STTg_OffVar DELAY = 0 DO STTg_SensorOff2('+str(trackingOffKeepDistance).upper()+') PRIO = -1')
      self.Source.append(';ENDFOLD')

   def OutputArcOnEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      """KUKA arc on command

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      # get log operator
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputArcOnEvent called")

      # Set processing flag for arc welding
      self.Tech.Processing = True
      # initialize persistent flags
      if not hasattr(KUKA_KRC5_Arc_Welding.OutputArcOnEvent, "skipNext"):
         KUKA_KRC5_Arc_Welding.OutputArcOnEvent.skipNext = False # type: ignore

      if not KUKA_KRC5_Arc_Welding.OutputArcOnEvent.skipNext: # type: ignore
         # variable definition
         KUKA_ARCIGNITION_JSON = "KukaArcIgnitionJson"
         KUKA_ARCON_JSON = "KukaArcOnJson"
         KUKA_ARCSENSE_JSON = "KukaArcSenseJson"

         # get all attributes from event
         arcIgnitionStr = ''
         arcOnStr = ''
         arcSenseStr = ''
         # try to get the attributes from the event
         try:
            arcIgnitionStr = event.GetStringAttribute(KUKA_ARCIGNITION_JSON, False).GetValue()
         except:
            logger.LogError("Downloader Error: Can't access attribute: " + KUKA_ARCIGNITION_JSON)
            logger.LogError("Downloader Error: Matching Kuka Arc Weld Technology plugin missing?")
         try:
            arcOnStr = event.GetStringAttribute(KUKA_ARCON_JSON, False).GetValue()
         except:
            logger.LogError("Downloader Error: Can't access attribute: " + KUKA_ARCON_JSON)
            logger.LogError("Downloader Error: Matching Kuka Arc Weld Technology plugin missing?")
         try:
            arcSenseStr = event.GetStringAttribute(KUKA_ARCSENSE_JSON, False).GetValue()
         except:
            logger.LogError("Downloader Error: Can't access attribute: " + KUKA_ARCSENSE_JSON)
            logger.LogError("Downloader Error: Matching Kuka Arc Weld Technology plugin missing?")

         # Convert JSON string back to JSON and fill class attributes
         data = json.loads(arcIgnitionStr)
         for key, value in data.items():
            setattr(self.ArcIgnInfo, key, value)
         data = json.loads(arcOnStr)
         for key, value in data.items():
            setattr(self.ArcOnInfo, key, value)
         data = json.loads(arcSenseStr)
         for key, value in data.items():
            setattr(self.ArcSenseInfo, key, value)

         self.ArcTech.ArcSwitchFlag = False
         self.ArcTech.ArcOnFlag = True

         self.ArcTech.ArcOffFlag = False

         if not self.ArcIgnInfo.KukaArcSwitch:
            KUKA_KRC5_Arc_Welding.OutputArcOnEvent.skipNext = True # type: ignore

      else:
         self.ArcTech.ArcOnFlag = False
         self.ArcTech.ArcSwitchFlag = True
         self.ArcTech.ArcOffFlag = False
         KUKA_KRC5_Arc_Welding.OutputArcOnEvent.skipNext = False # type: ignore

   def OutputArcOffEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      """Arc off and track off instructions

      Args:
         operator: download operator
         motion: current motion object
         event: event object
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader OutputArcOffEvent called")

      if not hasattr(KUKA_KRC5_Arc_Welding.OutputArcOffEvent, "skipNext"):
         KUKA_KRC5_Arc_Welding.OutputArcOffEvent.skipNext = False # type: ignore

      if not KUKA_KRC5_Arc_Welding.OutputArcOffEvent.skipNext: # type: ignore
         # variable definition
         KUKA_ARCOFF_JSON = "KukaArcOffJson"

         arcOffStr = ''
         # get all attributes from event
         try:
            arcOffStr = event.GetStringAttribute(KUKA_ARCOFF_JSON, False).GetValue()
         except:
            logger.LogError("Downloader Error: Can't access attribute: " + KUKA_ARCOFF_JSON)
            logger.LogError("Downloader Error: Matching Kuka Arc Weld Technology plugin missing?")

         # Convert JSON string back to JSON and fill class attributes
         data = json.loads(arcOffStr)
         for key, value in data.items():
            setattr(self.ArcOffInfo, key, value)

         self.ArcTech.ArcOnFlag = False
         self.ArcTech.ArcSwitchFlag = False
         self.ArcTech.ArcOffFlag = True

         KUKA_KRC5_Arc_Welding.OutputArcOffEvent.skipNext = True # type: ignore

      else:
         KUKA_KRC5_Arc_Welding.OutputArcOffEvent.skipNext = False # type: ignore
         self.ArcTech.ArcOnFlag = False
         self.ArcTech.ArcSwitchFlag = False
         self.ArcTech.ArcOffFlag = False

   def OutputSplineEvent(self, operator: DULPythonDownloadOperator, event: DULPythonEvent, motion : DULPythonMotion):
      """SplineEvent event implementation

      Args:
         operator (DULPythonDownloadOperator): Download operator gives access to the complete program
         event (DULPythonEvent): Event object gives access to the event attributes
      """
      logger = operator.GetLogOperator()
      logger.LogDebug("KukaPythonDownloader TextEvent called")
      # get all attributes
      # attributes = event.GetAttributes()
      # initialize variables

   def GenerateChannelString(self, program_number_attribute: int):
      """Create the appropriate Channel string depending on the channel configured in the controller

      Args:
         program_number_attribute (str): ProgNumber attribute, e.g. self.ArcIgnInfo.KukaIgnitionProgNumber,
                     self.ArcOnInfo.KukaProgNumber or self.ArcOffInfo.KukaArcOffJobNumber

      Returns:
         _type_: Channel string for DAT file
      """
      channel_strings = []
      for channel_number in range(1, 9):
         if channel_number == self.ArcTech.PowerSourceJobChannel:
                  channel_strings.append(f"Channel{channel_number} {program_number_attribute:.1f}")
         else:
               channel_strings.append(f"Channel{channel_number} 0.0")
      return ", ".join(channel_strings)

   import re

   def increment_string(self, s: str) -> str:
      match = re.match(r"(.*?)(\d+)$", s)
      if match:
         prefix, number = match.groups()
         incremented = str(int(number) + 1).zfill(len(number))
         return prefix + incremented
      else:
         raise ValueError(f"Kein gültiges Format: '{s}' (es muss mit einer Zahl enden)")


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
      logger = operator.GetLogOperator()

      if self.ArcTech.ArcOnFlag or self.ArcTech.ArcSwitchFlag or self.ArcTech.ArcOffFlag:

         wdatIdString = ''
         arcType = ''
         motionFlag = ''

         robotVelocity = f'{self.ArcOnInfo.KukaRobotVelocity1:1.2f}'.replace('.','')
         if self.ArcIgnInfo.KukaArcSwitch and not self.ArcTech.ArcOffFlag:
            self.ArcTech.ArcOnFlag = False
            self.ArcTech.ArcSwitchFlag = True
         if self.ArcTech.ArcOnFlag:
            self.WDatIndex += 1
            self.WDatIndexOnOff = self.WDatIndex
            arcType = 'arcon'
            wdatIdString += f'{self.ArcOnInfo.KukaProgNumber:02d}'+'_'+robotVelocity
         elif self.ArcTech.ArcSwitchFlag:
            self.WDatIndex += 1
            arcType = 'arcswi'
            wdatIdString += f'{self.ArcOnInfo.KukaProgNumber:02d}'+'_'+robotVelocity
         elif self.ArcTech.ArcOffFlag:
            arcType = 'arcoff'
            wdatIdString += f'{self.ArcOffInfo.KukaArcOffJobNumber:02d}'+'_'+robotVelocity
            # set velocity parameter to an attribute name for ARCOFF
            self.VelocityParamSet = "#CP_PARAMS, gArcBasVelDefinition"

         if self.ArcTech.AddWDatIndex:
            if self.ArcTech.ArcSwitchFlag:
               wdatIdString = f'{self.WDatIndex:02d}'+'_'+wdatIdString
            else:
               wdatIdString = f'{self.WDatIndexOnOff:02d}'+'_'+wdatIdString

         robotVelocity = self.ConvertVelocity(self.ArcOnInfo.KukaRobotVelocity1, self.Tech.VelocityUnitTechnology)/60
         self.CurrentLinVelocityTechnology = robotVelocity
         # if self.ArcIgnInfo.KukaIgnitionProgNumber == self.ArcOnInfo.KukaProgNumber and  self.ArcIgnInfo.KukaIgnitionProgNumber == self.ArcOffInfo.KukaArcOffJobNumber:
         #    singleWdat = True
         # else:
         #    singleWdat = False

         if motion.IsLinearMotion():
            motionFlag = 'lin'
         elif motion.IsCircularMotion():
            motionFlag = 'circ'
         elif motion.IsPtPMotion():
            motionFlag = 'ptp'

         # if self.ArcTech.ArcOnFlag and self.ArcTech.SeamTrackFlag and self.ArcTech.OutputSeamTrackSearchStart:
         #    dirInc = self.increment_string(motion.GetName())
         #    posInc = self.increment_string('X' + positionName)
         #    motionFramesInc = self.increment_string(motionFrames)

         #    if motionType == "PTP":
         #       motionProfileActSet = "P" + motionProfile
         #    else:
         #       motionProfileActSet = "L" + motionProfile
         #    motionProfileActSetInc = self.increment_string(motionProfileActSet)

         #    self.Source.append(f';FOLD SeamTrack Search Start Target={motion.GetName()} Dir={dirInc} Vel='+str(self.ArcTech.SeamTrackSearchSpeed)+' m/s ;%{{PE}}')
         #    self.Source.append(f'  ;FOLD Parameters Parameters ;%{{h}}')
         #    self.Source.append(f'    ;Params IlfProvider=SeamTrack.SearchStart;SeamTrack.Target={motion.GetName()};SeamTrack.Dir={dirInc};Kuka.VelocityPath='+str(self.ArcTech.SeamTrackSearchSpeed))
         #    self.Source.append(f'  ;ENDFOLD')
         #    self.Source.append(f'  INTERRUPT DECL STTg_SearchInterrupt WHEN $SEN_PINT[STTg_FindReturn_Indx] == 1 DO STTg_BrakeMove( X{motion.GetName()} )')
         #    self.Source.append(f'  INTERRUPT ON STTg_SearchInterrupt')
         #    self.Source.append(f'  STTg_SearchLin({'X' + positionName},{motionFrames},{motionProfileActSet},{posInc},{motionFramesInc},{motionProfileActSetInc},'+str(self.ArcTech.SeamTrackSearchSpeed)+')')
         #    self.Source.append(f';ENDFOLD')
         #    self.Source.append(f'')

         #    if self.ArcTech.OutputSeamTrackStartFooterWritten == False:
         #       self.AddLineToDataFooter(f'DECL MODULEPARAM_T LAST_TP_PARAMS={{PARAMS[] "SeamTrack.Target={motion.GetName()}; SeamTrack.Dir={dirInc}; Kuka.VelocityPath={robotVelocity}"}}')
         #       self.ArcTech.OutputSeamTrackStartFooterWritten = True

         # Common SRC output
         self.Tech.ParamFoldIlfProviderEntry = 'kukaroboter.arctech.' + arcType + motionFlag
         if self.ArcSenseInfo.KukaArcSense and (self.ArcTech.ArcOnFlag or self.ArcTech.ArcSwitchFlag):
            self.Tech.SourceFirstMotionFold = arcType.upper()+' TRACK WDAT'+wdatIdString+' '
         else:
            self.Tech.SourceFirstMotionFold = arcType.upper()+' WDAT'+wdatIdString+' '
         if self.ArcTech.ArcOnFlag and self.ArcSenseInfo.KukaArcSense:
            arcSenseVer = '; ArcTech.Sense=3.5.1.21'
         else:
            arcSenseVer = ''
         self.Tech.ParamFoldEndTech = 'ArcTech.WdatVarName=WDAT'+wdatIdString+'; ArcTech.Basic='+self.ArcTech.ArcTechVersionSRC+'; ArcTech.Advanced='+self.ArcTech.ArcTechAdvVersionSRC+'; ArcTech.Sense='+self.ArcTech.ArcTechSenseVersionSRC

         if self.ArcTech.ArcOnFlag:
            # SRC output
            self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN DISTANCE = 1 DELAY = ArcGetDelay(#PreDefinition, WDAT'+wdatIdString+') DO ArcMainNG(#PreDefinition, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#OnTheFlyArcOn, WDAT'+wdatIdString+') DELAY = ArcGetDelay(#GasPreflow, WDAT'+wdatIdString+') DO ArcMainNG(#GasPreflow, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            if self.ArcSenseInfo.KukaArcSense:
               self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#OnTheFlyArcOn, WDAT'+wdatIdString+') DELAY = ArcGetDelay(#ArcPreOn, WDAT'+wdatIdString+') DO ArcMainNG(#ArcOnMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1 ')
            else:
               self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#OnTheFlyArcOn, WDAT'+wdatIdString+') DELAY = ArcGetDelay(#ArcPreOn, WDAT'+wdatIdString+') DO ArcMainNG(#ArcOnMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1 ')
            self.Tech.SourceBeforeMotion.append('  ArcMainNG(#ArcOnBeforeMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')

            if self.ArcTech.SeamTrackFlag:
               self.Tech.SourceBeforeMotion.append('  STT_PrepareWeave (WDAT'+wdatIdString+')')
               self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = 0 DELAY = 0 DO STT_SensorWeave(WDAT'+wdatIdString+') PRIO = -1')

            self.Tech.SourceAfterMotion.append('  ArcMainNG(#ArcOnAfterMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')
            self.ArcTech.ArcOnFlag = False
            self.ArcTech.ArcSwitchFlag = True

            # Is ArcOn WDAT already output?
            if not wdatIdString in self.WDatIndexList:
               # DAT output
               # WDAT
               # DECL stArcDat_T WDAT_S1_01={WdatId[] "WDAT_S1_01",Info {Version 0,WId 0,WName[] " "},Strike {JobModeId[] "Jobbetrieb",StartTime 0.0,PreFlowTime 0.0,Channel1 0.0,Channel2 0.0,Channel3 0.0,Channel4 0.0,Channel5 0.0,Channel6 0.0,Channel7 0.0,Channel8 0.0,PurgeTime 0.0},Weld {JobModeId[] "Jobbetrieb",ParamSetId[] "Set1",Velocity 0.00500000,Channel1 9.00000,Channel2 0.0,Channel3 0.0,Channel4 0.0,Channel5 0.0,Channel6 0.0,Channel7 0.0,Channel8 0.0},Weave {Pattern #None,Length 4.00000,Amplitude 2.00000,Angle 0.0,Frequency 2.00000,LeftSideDelay 0.0,RightSideDelay 0.0},Advanced {IgnitionErrorStrategy 1,WeldErrorStrategy 1,SlopeOption #None,SlopeOptionOff #None,SlopeTime 0.0,SlopeDistance 0.0,SlopeTimeOff 0.0,SlopeDistanceOff 0.0,SlopeStartOptionOff #AtArcOff,OnTheFlyActiveOn FALSE,OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0,PreStartOn FALSE,PreStartLocal FALSE,PreStartTime 0.0,MoveBackAtArcOffOption #None,MoveBackAtArcOffDistance 0.0}}
               # DECL stArcDat_T WS1_01={WdatId[] "WS1_01",Info {Version 305030490},Strike {SeamName[] " ",PartName[] " ",SeamNumber 0,PartNumber 0,DesiredLength 0.0,LengthTolNeg 0.0,LengthTolPos 0.0,LengthCtrlActive FALSE},Advanced {BitCodedRobotMark 0}}
               tempData = []
               tempLine = ''
               # Ignition options
               tempLine += 'DECL stArcDat_T WDAT'+wdatIdString+'={WdatId[] "WDAT'+wdatIdString+'",Strike {JobModeId[] "Jobmodus",ParamSetId[] "'+self.ArcIgnInfo.KukaIgnitionParmSet+'",StartTime '\
                  +f'{self.ArcIgnInfo.KukaWaitTimeAfterIgnition:.2f}'+',PreFlowTime '+f'{self.ArcIgnInfo.KukaPreflowTime:.2f}'+','\
                  +self.GenerateChannelString(self.ArcIgnInfo.KukaIgnitionProgNumber)+',PurgeTime '+f'{self.ArcIgnInfo.KukaOnTheFlyGasPreflowTime:.2f}'+'},'
               # Weld options
               tempLine += 'Weld {JobModeId[] "Jobmodus",ParamSetId[] "'+self.ArcOnInfo.KukaWeldParmSet+'",Velocity '+f'{robotVelocity:.8f}'+','\
                  +self.GenerateChannelString(self.ArcOnInfo.KukaProgNumber)+'},'
               # Weaving options
               if self.ArcSenseInfo.KukaArcSense:
                  tempLine += 'Weave {Pattern #'+self.ArcSenseInfo.KukaArcSensePattern
               else:
                  tempLine += 'Weave {Pattern #'+self.ArcOnInfo.KukaWeavePattern
               # Weaving Length option
               if int(self.ArcTech.ArcTechVersionDAT) >= 305000000 or self.ArcTech.WeaveType == 'Weave length':
                  tempLine += ',Length '+f'{self.ArcOnInfo.KukaWeaveLength:.2f}'
               tempLine += ',Amplitude '+f'{self.ArcOnInfo.KukaWeaveDeflection:.2f}'+',Angle '+f'{self.ArcOnInfo.KukaWeaveAngle:.2f}'
               # Weaving Frequency option
               if int(self.ArcTech.ArcTechVersionDAT) >= 305000000 or self.ArcTech.WeaveType == 'Weave frequency':
                  tempLine += ',Frequency '+f'{self.ArcOnInfo.KukaWeaveFrequency:.2f}'
               tempLine += ',LeftSideDelay 0.0,RightSideDelay 0.0}'
               # Crater options if one WDAT
               tempLine += ',Crater {JobModeId[] "Jobmodus",ParamSetId[] "'+self.ArcOffInfo.KukaArcOffParmSet+'",CraterTime '+f'{self.ArcOffInfo.KukaEndCraterTime:.2f}'+',PostflowTime '+f'{self.ArcOffInfo.KukaPostFlowTime:.2f}'+', '\
                  +self.GenerateChannelString(self.ArcOffInfo.KukaArcOffJobNumber)+',BurnBackTime 0.0}'
               # ArcTech Advanced options
               if self.ArcTech.ArcTechAdv:
                  tempLine += ',Advanced {IgnitionErrorStrategy 1,'\
                     +'WeldErrorStrategy 1,SlopeOption #None,SlopeTime 0.0,SlopeDistance 0.0,OnTheFlyActiveOn '+str(self.ArcIgnInfo.KukaOnTheFlyActive).upper()+',OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0}'
               # ArcSense tracking options
               if self.ArcSenseInfo.KukaArcSense:
                  if not self.ArcSenseInfo.KukaArcSenseFindCenter:
                     self.ArcSenseInfo.KukaArcSenseActivDelay = 0
                  tempLine += ',Track {IsArcSenseEnabled TRUE,ControlEnabled TRUE,KeepOffset TRUE,TeachNew FALSE,FindSeamMiddle '+str(self.ArcSenseInfo.KukaArcSenseFindCenter).upper()\
                     +',TrackingDelay '+f'{self.ArcSenseInfo.KukaArcSenseActivDelay:.4f}'+',ControlSensibility '+f'{self.ArcSenseInfo.KukaArcSenseLatCtrlGain:.4f}'+',MaxDeviation '+f'{self.ArcSenseInfo.KukaArcSenseMaxCorr:.4f}'\
                     +',ControlSensibilityHeight '+f'{self.ArcSenseInfo.KukaArcSenseHeightCtrl:.4f}'+',Bias '+f'{self.ArcSenseInfo.KukaArcSenseLatBias:.4f}'+',WeaveOffset 0.0,HeightCorrValue 0.0}'
               tempLine += '}' # End of 1st stArcDat_T line
               tempData.append(tempLine)
               tempLine = 'DECL stArcDat_T WS'+wdatIdString+'={WdatId[] "WS'+wdatIdString+'",Info {Version '+self.ArcTech.ArcTechVersionDAT+'},Strike {SeamName[] " ",PartName[] " ",SeamNumber 0,PartNumber 0,'\
                     +'DesiredLength 0.0,LengthTolNeg 0.0,LengthTolPos 0.0,LengthCtrlActive FALSE}'
               if self.ArcTech.ArcTechAdv:
                  tempLine += ',Advanced {BitCodedRobotMark 0}'
               tempLine += '}' # End of 2nd stArcDat_T line
               tempData.append(tempLine)
               if self.Tech.SortDat:
                  for line in tempData:
                     self.DataTechDAT1.append(line)
               else:
                  for line in tempData:
                     self.Data.append(line)

               self.WDatIndexList.append(wdatIdString)

         elif self.ArcTech.ArcSwitchFlag:
            # SRC output
            self.VelocityParamSet = "#CP_PARAMS, gArcBasVelDefinition"
            self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN DISTANCE = 1 DELAY = 0 DO ArcMainNG(#ArcSwiMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            self.Tech.SourceBeforeMotion.append('  ArcMainNG(#ArcSwiBeforeMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')

            if self.ArcTech.SeamTrackFlag and self.ArcOnInfo.KukaWeavePattern != 'None':
               self.Tech.SourceBeforeMotion.append('  STT_PrepareWeave (WDAT'+wdatIdString+')')
               self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = 0 DELAY = 0 DO STT_SensorWeave(WDAT'+wdatIdString+') PRIO = -1')

            self.Tech.SourceAfterMotion.append('  ArcMainNG(#ArcSwiAfterMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')

            # Is ArcSwi WDAT already output?
            if not wdatIdString in self.WDatIndexList:
               # DAT output
               # WDAT
               # DECL stArcDat_T WDAT_1_02={Weld {JobModeId[] "Job Mode",ParamSetId[] "Set2",Velocity 0.01000000,Channel1 0.0,Channel2 0.0,Channel3 2.00000,Channel4 0.0,Channel5 0.0,Channel6 0.0,Channel7 0.0,Channel8 0.0}
               # ,Weave {Pattern #None,Length 4.00000,Amplitude 2.00000,Angle 0.0,Frequency 0.0 LeftSideDelay 0.0,RightSideDelay 0.0}
               # ,Advanced {IgnitionErrorStrategy 1,WeldErrorStrategy 1,SlopeOption #None,SlopeTime 0.0,SlopeDistance 0.0,OnTheFlyActiveOn FALSE,OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0}}
               # DECL stArcDat_T WS1_02={WdatId[] "WS1_02",Info {Version 305030490}}
               tempData = []
               tempLine = ''
               # Weld options
               tempLine += 'DECL stArcDat_T WDAT'+wdatIdString+'={WdatId[] "WDAT'+wdatIdString+'",Weld {JobModeId[] "Jobmodus",'\
                  +'ParamSetId[] "'+self.ArcOnInfo.KukaWeldParmSet+'",Velocity '+f'{robotVelocity:.8f}'\
                  +','+self.GenerateChannelString(self.ArcOnInfo.KukaProgNumber)+'},'
               # Weaving options
               # Weaving options
               if self.ArcSenseInfo.KukaArcSense:
                  tempLine += 'Weave {Pattern #'+self.ArcSenseInfo.KukaArcSensePattern
               else:
                  tempLine += 'Weave {Pattern #'+self.ArcOnInfo.KukaWeavePattern
               tempLine += ',Length '+f'{self.ArcOnInfo.KukaWeaveLength:.2f}'+',Amplitude '\
                  +f'{self.ArcOnInfo.KukaWeaveDeflection:.2f}'+',Angle '+f'{self.ArcOnInfo.KukaWeaveAngle:.2f}'+',Frequency '+f'{self.ArcOnInfo.KukaWeaveFrequency:.2f}'+',LeftSideDelay 0.0,RightSideDelay 0.0}'
               # ArcTech Advanced options
               if self.ArcTech.ArcTechAdv:
                  tempLine += ',Advanced {IgnitionErrorStrategy 1,'\
                     +'WeldErrorStrategy 1,SlopeOption #None,SlopeTime 0.0,SlopeDistance 0.0,OnTheFlyActiveOn '+str(self.ArcIgnInfo.KukaOnTheFlyActive).upper()+',OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0}'
               # ArcSense tracking options
               if self.ArcSenseInfo.KukaArcSense:
                  if not self.ArcSenseInfo.KukaArcSenseFindCenter:
                     self.ArcSenseInfo.KukaArcSenseActivDelay = 0
                  tempLine += ',Track {IsArcSenseEnabled TRUE,ControlEnabled TRUE,KeepOffset TRUE,TeachNew FALSE,FindSeamMiddle '+str(self.ArcSenseInfo.KukaArcSenseFindCenter).upper()\
                     +',TrackingDelay '+f'{self.ArcSenseInfo.KukaArcSenseActivDelay:.4f}'+',ControlSensibility '+f'{self.ArcSenseInfo.KukaArcSenseLatCtrlGain:.4f}'+',MaxDeviation '+f'{self.ArcSenseInfo.KukaArcSenseMaxCorr:.4f}'\
                     +',ControlSensibilityHeight '+f'{self.ArcSenseInfo.KukaArcSenseHeightCtrl:.4f}'+',Bias '+f'{self.ArcSenseInfo.KukaArcSenseLatBias:.4f}'+',WeaveOffset 0.0,HeightCorrValue 0.0}'
               tempLine += '}' # End of 1st stArcDat_T line
               tempData.append(tempLine)
               tempLine = 'DECL stArcDat_T WS'+wdatIdString+'={WdatId[] "WS'+wdatIdString+'",Info {Version '+self.ArcTech.ArcTechVersionDAT+'}}'
               tempData.append(tempLine)
               if self.Tech.SortDat:
                  for line in tempData:
                     self.DataTechDAT1.append(line)
               else:
                  for line in tempData:
                     self.Data.append(line)

               self.WDatIndexList.append(wdatIdString)

         # ArcOff output
         elif self.ArcTech.ArcOffFlag:
            # if motionType == 'CIRC':
            #    logger.LogFatal("CIRC motion not supported for ArcOff")
            #    logger.LogFatal("1. Please insert a process point close to the ArcOff point.")
            #    logger.LogFatal("2. Set the motion type of the ArcOff point to Linear.")
            # else:
            # SRC output
            self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#ArcOffBefore, WDAT'+wdatIdString+') DELAY = 0 DO ArcMainNG(#ArcOffBeforeOffStd, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            # Next line only for ArcTechBasic version 3.5.0 and up
            if int(self.ArcTech.ArcTechVersionDAT) >= 305000000:
               self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#ArcOffBefore2, WDAT'+wdatIdString+') DELAY = 0 DO ArcMainNG(#ArcOffBeforeOffStd2, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            self.Tech.SourceBeforeMotion.append('  TRIGGER WHEN PATH = ArcGetPath(#OnTheFlyArcOff, WDAT'+wdatIdString+') DELAY = 0 DO ArcMainNG(#ArcOffMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+') PRIO = -1')
            self.Tech.SourceBeforeMotion.append('  ArcMainNG(#ArcOffBeforeMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')
            self.Tech.SourceAfterMotion.append('  ArcMainNG(#ArcOffAfterMoveStd, WDAT'+wdatIdString+', WS'+wdatIdString+')')

            # Is ArcOff WDAT already output?
            if not wdatIdString in self.WDatIndexList:
               # DAT output
               # WDAT
               # DECL stArcDat_T WDAT_1_03={Crater {JobModeId[] "Job Mode",ParamSetId[] "Set3",CraterTime 0.0,PostflowTime 0.0,Channel1 0.0,Channel2 0.0,Channel3 0.0,Channel4 0.0,Channel5 0.0,Channel6 0.0,Channel7 0.0,Channel8 0.0,BurnBackTime 0.0}
               # ,Advanced {IgnitionErrorStrategy 1,WeldErrorStrategy 1,SlopeOption #None,SlopeTime 0.0,SlopeDistance 0.0,OnTheFlyActiveOn FALSE,OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0}}
               # DECL stArcDat_T WS1_10={WdatId[] "WS1_10",Info {Version 305030490}}
               tempData = []
               tempLine = ''
               # Ignition options
               tempLine += 'DECL stArcDat_T WDAT'+wdatIdString+'={WdatId[] "WDAT'+wdatIdString+'",Crater {JobModeId[] "Jobmodus",ParamSetId[] "'+self.ArcOffInfo.KukaArcOffParmSet+'",CraterTime '+f'{self.ArcOffInfo.KukaEndCraterTime:.2f}'+',PostflowTime '+f'{self.ArcOffInfo.KukaPostFlowTime:.2f}'+', '\
                  +self.GenerateChannelString(self.ArcOffInfo.KukaArcOffJobNumber)+',BurnBackTime 0.0}'
               # ArcTech Advanced options
               if self.ArcTech.ArcTechAdv:
                  tempLine += ',Advanced {IgnitionErrorStrategy 1,'\
                     +'WeldErrorStrategy 1,SlopeOption #None,SlopeTime 0.0,SlopeDistance 0.0,OnTheFlyActiveOn '+str(self.ArcIgnInfo.KukaOnTheFlyActive).upper()+',OnTheFlyActiveOff FALSE,OnTheFlyDistanceOn 0.0,OnTheFlyDistanceOff 0.0}'
               # ArcSense tracking options
               if self.ArcSenseInfo.KukaArcSense:
                  if not self.ArcSenseInfo.KukaArcSenseFindCenter:
                     self.ArcSenseInfo.KukaArcSenseActivDelay = 0
                  tempLine += ',Track {IsArcSenseEnabled TRUE,ControlEnabled TRUE,KeepOffset TRUE,TeachNew FALSE,FindSeamMiddle '+str(self.ArcSenseInfo.KukaArcSenseFindCenter).upper()\
                     +',TrackingDelay '+f'{self.ArcSenseInfo.KukaArcSenseActivDelay:.4f}'+',ControlSensibility '+f'{self.ArcSenseInfo.KukaArcSenseLatCtrlGain:.4f}'+',MaxDeviation '+f'{self.ArcSenseInfo.KukaArcSenseMaxCorr:.4f}'\
                     +',ControlSensibilityHeight '+f'{self.ArcSenseInfo.KukaArcSenseHeightCtrl:.4f}'+',Bias '+f'{self.ArcSenseInfo.KukaArcSenseLatBias:.4f}'+',WeaveOffset 0.0,HeightCorrValue 0.0}'
               tempLine += '}' # End of 1st stArcDat_T line
               tempData.append(tempLine)
               tempLine = 'DECL stArcDat_T WS'+wdatIdString+'={WdatId[] "WS'+wdatIdString+'",Info {Version '+self.ArcTech.ArcTechVersionDAT+'},Strike {SeamName[] " ",PartName[] " ",SeamNumber 0,PartNumber 0,'\
                     +'DesiredLength 0.0,LengthTolNeg 0.0,LengthTolPos 0.0,LengthCtrlActive FALSE}'
               if self.ArcTech.ArcTechAdv:
                  tempLine += ',Advanced {BitCodedRobotMark 0}'
               tempLine += '}' # End of 2nd stArcDat_T line
               tempData.append(tempLine)
               if self.Tech.SortDat:
                  for line in tempData:
                     self.DataTechDAT1.append(line)
               else:
                  for line in tempData:
                     self.Data.append(line)

               self.WDatIndexList.append(wdatIdString)

            self.ArcTech.ArcOnFlag = False
            self.ArcTech.ArcSwitchFlag = False
            self.ArcTech.ArcOffFlag = False
            # Reset manual ArcOnEvent switch flag
            self.ArcIgnInfo.KukaArcSwitch = False

   # Helper function to compute a rotation matrix from Euler angles (ZYX order)
   @staticmethod
   def euler_to_rotation_matrix(euler_angles):
      z, y, x = np.deg2rad(euler_angles)  # Convert degrees to radians
      Rz = np.array([
         [np.cos(z), -np.sin(z), 0],
         [np.sin(z), np.cos(z), 0],
         [0, 0, 1]
      ])
      Ry = np.array([
         [np.cos(y), 0, np.sin(y)],
         [0, 1, 0],
         [-np.sin(y), 0, np.cos(y)]
      ])
      Rx = np.array([
         [1, 0, 0],
         [0, np.cos(x), -np.sin(x)],
         [0, np.sin(x), np.cos(x)]
      ])
      return Rz @ Ry @ Rx  # Combine rotations in ZYX order

   # Function to calculate the touch correction frame parameters
   @staticmethod
   def calculate_touch_correction_params(touch_corr_frame_id_list):
      # Initialize the result list with "NullTouch" placeholders for all 6 possible touches
      touch_correction_frame_params = ["NullTouch"] * 6

      # Define the mapping of touch indices to their positions in the result list
      touch_mapping = {
         (1, 1): 0,  # FramePoint 1, Touch 1
         (1, 2): 1,  # FramePoint 1, Touch 2
         (1, 3): 2,  # FramePoint 1, Touch 3
         (2, 1): 3,  # FramePoint 2, Touch 1
         (2, 2): 4,  # FramePoint 2, Touch 2
         (3, 1): 5   # FramePoint 3, Touch 1
      }

      # Iterate through the provided list and populate the result list
      for touch_id in touch_corr_frame_id_list:
         # Extract FramePoint and Touch # from the touch ID
         match = re.match(r"VCDFR\d+FP(\d+)M(\d+)", touch_id)
         if match:
               frame_point = int(match.group(1))
               touch_number = int(match.group(2))
               # Check if the FramePoint and Touch # are valid
               if (frame_point, touch_number) in touch_mapping:
                  index = touch_mapping[(frame_point, touch_number)]
                  touch_correction_frame_params[index] = touch_id

      return touch_correction_frame_params
