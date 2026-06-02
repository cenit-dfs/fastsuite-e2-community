# KAWASAKI ArcWelding — Reference → Golden Mapping

> **Purpose:** This document maps every section of the annotated Simple_Python_Translator
> reference dump to the corresponding Kawasaki AS-language output in the golden files.
> An agent should be able to read this mapping and produce a working downloader.

## Scenario Overview

| Program | WorkMethod | Features Exercised |
|---------|------------|-------------------|
| PG06_BASIC | StitchWelding (no weld) | Basic motions, speed, accuracy, approach/retract — **start here** |
| PG07_BASIC_EXP | StitchWelding (no weld) | Same as PG06 but with inline `TRANS(...)` output (explicit mode) |
| PG01_OP | TouchSensing + StitchWelding | Touch sensing (KR_TOUCH), arc welding (LWS/LWE), operation groups |
| PG02_SE | TouchSensing + StitchWelding | Start-end touch sensing, multi-TS-ID within one group |
| PG03_SE | TouchSensing + StitchWelding | TRSUB, ROTBASE_ON=1, signals, ArcWeldCondition, sensing, RTPM, LT, crater |
| PG04_SD | TouchSensing + StitchWelding | Seam-distance touch sensing, many TS_IDs per group |
| PG05_3PFR | TouchSensing + StitchWelding | 3-point frame, FRAME_PT variables, KR_FRAME |

## Output Style

Controlled by resource attribute `CENOlpDataOutputStyle`:

| Value | Position Format | Example | Program |
|-------|----------------|---------|---------|
| `"Implicit"` | Named point in `.TRANS` block | `LMOVE PG06_BASIC_P0002` | PG06_BASIC |
| `"Explicit"` | Inline `TRANS(x,y,z,o,a,t,ext1,ext2)` | `LMOVE TRANS(118.75, 1120.4, ...)` | PG07_BASIC_EXP |

---

## 1. File Structure

### AS-language file layout

```
.PROGRAM <program_name>()
<body: motion instructions, events, comments>
.END
.TRANS
<named_point_1> <x> <y> <z> <o> <a> <t> [<ext1> <ext2> ...]
<named_point_2> ...
.END
```

### API → Output

| API Call | Output |
|----------|--------|
| `program.GetName()` → `"PG06_BASIC"` | `.PROGRAM PG06_BASIC()` |
| End of all motions | `.END` |
| All accumulated position data | `.TRANS` block (implicit mode only) |
| End of file | `.END` |

---

## 2. Program Header

### Golden output (PG06_BASIC — simple)

```as
.PROGRAM PG06_BASIC()
BASE NULL
TOOL PG06_BASIC_TOOL1
RIGHTY
ABOVE
DWRIST
```

### Golden output (PG01_OP — with touch sensing)

```as
.PROGRAM PG01_OP()
;Compensate track/rail/positioner
ROTBASE_ON = 0
```

### API → Output mapping

| API Source | Output Line | Notes |
|-----------|-------------|-------|
| `program.GetName()` | `.PROGRAM PG06_BASIC()` | Always first line |
| *static* | `BASE NULL` | Emitted once at first operation (simple mode) |
| `program.GetUsedToolProfile().GetName()` → `"TOOL1"` | `TOOL PG06_BASIC_TOOL1` | Prefix = program name + `_` |
| *static* | `RIGHTY` / `ABOVE` / `DWRIST` | Robot configuration — always output |
| Touch sensing detected (workmethod = `"TouchSensingWorkMethod"`) | `;Compensate track/rail/positioner` + `ROTBASE_ON = 0` | Only when program has touch operations |

---

## 3. Tool Profile → .TRANS

### Reference dump

```
# [API: profile.GetXYZ() / GetOrientation() → DULPythonToolProfile] [XYZ: meters, Angles: degrees]
ToolProfile = "TOOL1"; X = "0.002200"; Y = "0.141714"; Z = "0.431714"; Rx = "-45.000000"; Ry = "-0.000274"; Rz = "-0.000327";
```

### Golden output

```
PG06_BASIC_TOOL1 2.2 141.71 431.71 -90 -45 90
```

### Conversion rules

| API Method | Value (meters) | Output (mm) | Format |
|-----------|----------------|-------------|--------|
| `profile.GetXYZ()[0]` (X) | 0.002200 | 2.2 | `×1000`, trim trailing zeros |
| `profile.GetXYZ()[1]` (Y) | 0.141714 | 141.71 | `×1000`, round to 2 decimals |
| `profile.GetXYZ()[2]` (Z) | 0.431714 | 431.71 | `×1000`, round to 2 decimals |

### Euler angle conversion (E2 XYZs → Kawasaki OAT = ZYZr)

Kawasaki uses **Z-Y'-Z'' intrinsic** Euler angles (not ZYX). Use `cenpymath`:

```python
from cenpymath.Euler.Converter import Converter
from cenpymath.Euler.Notations import Notations

converter = Converter()
rx, ry, rz = position.GetOrientation()  # E2 default: XYZs
oat = converter.ConvertEuler(rx, ry, rz, Notations.Euler_ZYZr, Notations.Euler_XYZs)
O, A, T = oat[0], oat[1], oat[2]
```

| E2 (Rx, Ry, Rz) XYZs | Kawasaki (O, A, T) ZYZr |
|-----------------------|-------------------------|
| (-45, ~0, ~0) | (-90, -45, 90) |
| (135, 0, 0) | (90, -135, -90) |
| (135, 0, 90) | (180, -135, -90) |
| (125.26, 30, -35.26) | (35.27, -120, -125.26) |

Verified against all 10 unique orientation pairs in the golden files.

---

## 4. Motion Points → Instruction + .TRANS

### Reference dump (Approach motion — PTP)

```
# [API: motion.GetMotionType() → MotionType, motion.GetPosition() → DULPythonPosition]
Motion: PG06_BASIC_P0001;  MotionType = "Pt2Pt";
 PositionName = "PG06_BASIC_P0001"; ProcessType = "Approach"; TargetType = "Cartesian";
# [API: position.GetXYZ() → tuple(x,y,z)] [unit: METERS — multiply by 1000 for mm]
 Cartesian target:
   X = "0.118750"; Y = "1.191111"; Z = "1.093611"; Rx = "135.000000"; Ry = "0.000000"; Rz = "-0.000000";
   Config = "RAD"; Turn = "0,0,0";
# [API: position.GetMainJointValues()] [unit: degrees]
 Joint target:
   MainJoint = "D1"; Value = "4.997488";
   ...
   ExtJoint = "JT7"; Value = "0.000000";
   ExtJoint = "JT8"; Value = "180.000000";
```

### Golden output

**Body:**
```as
JMOVE PG06_BASIC_P0001
```

**TRANS block:**
```
PG06_BASIC_P0001 118.75 1191.11 1093.61 90 -135 -90 0 180
```

### Motion type mapping

| `motion.GetMotionType()` | Kawasaki Instruction |
|--------------------------|---------------------|
| `Pt2Pt` | `JMOVE` |
| `Linear` | `LMOVE` |
| `Circular` | `C1MOVE` / `C2MOVE` (via + end) |

### Position data conversion (implicit mode)

| Field | API Source | Formula | Example |
|-------|-----------|---------|---------|
| Name | `position.GetName()` | direct | `PG06_BASIC_P0001` |
| X | `position.GetXYZ()[0]` | `× 1000`, round 2 dec | 0.118750 → 118.75 |
| Y | `position.GetXYZ()[1]` | `× 1000`, round 2 dec | 1.191111 → 1191.11 |
| Z | `position.GetXYZ()[2]` | `× 1000`, round 2 dec | 1.093611 → 1093.61 |
| O | from orientation | Euler conversion → OAT | 90 |
| A | from orientation | Euler conversion → OAT | -135 |
| T | from orientation | Euler conversion → OAT | -90 |
| Ext1 | `position.GetExternalJointValues()[0][1]` | direct (degrees) | 0 |
| Ext2 | `position.GetExternalJointValues()[1][1]` | direct (degrees) | 180 |

### Position data conversion (explicit mode — PG07_BASIC_EXP)

Instead of accumulating in `.TRANS`, emit inline:
```as
JMOVE TRANS (118.75, 1191.11, 1093.61, 90, -135, -90, 0, 180)
```

---

## 5. Speed Events → SPEED instruction

### Reference dump

```
EventName = "Speed"; EventType = "Speed";
 Name = "Value"; Value = "0.500000"; ValueUnitType = "Speed";
 Name = "PathType"; Value = "Contour";
```

### Conversion rules

| API | Condition | Output |
|-----|-----------|--------|
| `PathType = "Contour"` | Linear (CP) speed | `SPEED <value×1000> MM/S ALWAYS` |
| `PathType = "PointToPoint"` | PTP speed | `SPEED <value> ALWAYS` |
| `Value = 0.500000` | Contour example | `SPEED 500 MM/S ALWAYS` |
| `Value = 0.005833` | Contour example | `SPEED 5.833 MM/S ALWAYS` |
| `Value = 50.0` | PTP example | `SPEED 50 ALWAYS` |

> **Speed value for Contour is in m/s → multiply by 1000 for mm/s.**
> **Speed value for PTP is in % → output directly.**

---

## 6. Accuracy Events → ACCURACY + CP

### Reference dump

```
EventName = "Accuracy"; EventType = "Accuracy";
 Name = "Value"; Value = "0.010000"; (meters)
 Name = "Criteria"; Value = "On";
 Name = "PathType"; Value = "Contour";
```

### Conversion rules

| Criteria | Effect | Output |
|----------|--------|--------|
| `"Off"` | Disable fly-by | `CP OFF` (emitted once, never toggled back ON) |
| `"On"` + Value > 0 | Enable fly-by | `ACCURACY <value×1000> ALWAYS` |
| `"Distance"` + Value > 0 | Set distance | `ACCURACY <value×1000> ALWAYS` |
| `"Distance"` during weld | *(suppressed)* | No output when arcOnActive=True |

> **CP rule:** Only `CP OFF` is ever emitted. Never `CP ON`. Emitted once when
> first needed. Not emitted in touch sensing or explicit mode.

Value 0.010000 m → `ACCURACY 10 ALWAYS`.
Value 0.005000 m → `ACCURACY 5 ALWAYS`.

---

## 7. Approach / Retract Events

### Reference dump

```
EventName = "ApproachArcWeldingStitch"; EventType = "Approach";
 Name = "SpeedViaApproach"; Value = "0.500000"; ValueUnitType = "Speed";
```

### Output behavior

The Approach event doesn't produce its own output line. It sets context:
- The approach motion becomes a `JMOVE` (PTP approach)
- Speed comes from the Speed event that follows
- `ACCEL 100 ALWAYS` is emitted once

```
EventName = "RetractArcWeldingStitch"; EventType = "Retract";
```

Similarly, Retract doesn't produce its own instruction — it marks the retract motion context.

---

## 8. Arc Welding Events (ArcOn / ArcOff)

### Reference dump (ArcOnEvent — from PG01_OP Seam4)

```
EventName = "ArcOnEvent"; EventType = "Olp";
 Name = "DLJobNumber"; Value = "1";
 Name = "DLWC1WeldSpeed"; Value = "35";
 Name = "DLWeldConditionNumber"; Value = "1";
 Name = "DLWC1WireFeedSpeed"; Value = "0.0";
 Name = "DLWC1WeldCurrent"; Value = "0.0";
 Name = "DLWC1ArcLengthCorr"; Value = "0.0";
 Name = "DLWC1WeldVoltage"; Value = "0.0";
 Name = "DLWC1PulseDynamicCorr"; Value = "0.0";
 Name = "DLWC1WireRetractCorr"; Value = "0.0";
```

### Golden output

```as
SET_ARC_W1JOBNO 1 = 1
SETCONDW1 1 = 35,0,0,0,0,0,0,0
LWS <touch_offset> + <point>
```

### ArcOn attribute → output mapping

SETCONDW1 contains 8 parameters. The layout depends on `DLWeldConditionMode`:

**condMode=0 (Synergic mode):**

| Position | Attribute |
|----------|----------|
| 1 | `DLWC1WeldSpeed` |
| 2 | `DLWC1WireFeedSpeed` |
| 3 | `DLWC1ArcLengthCorr` |
| 4 | `DLWC1PulseDynamicCorr` |
| 5 | `DLWC1WireRetractCorr` |
| 6 | `DLWeaveWidth` (m→mm ×1000, round 1 dec) |
| 7 | `DLWeaveFrequenz` (round 1 dec) |
| 8 | `DLWeavePatternNumber` |

**condMode=1 (Manual mode):**

| Position | Attribute |
|----------|----------|
| 1 | `DLWC1WeldSpeed` |
| 2 | `DLWC1WeldCurrent` |
| 3 | `DLWC1WeldVoltage` |
| 4 | `DLWC1PulseDynamicCorr` |
| 5 | `DLWC1WireRetractCorr` |
| 6 | `DLWeaveWidth` (m→mm ×1000, round 1 dec) |
| 7 | `DLWeaveFrequenz` (round 1 dec) |
| 8 | `DLWeavePatternNumber` |

```
SET_ARC_W1JOBNO <DLWeldConditionNumber> = <DLJobNumber>
SETCONDW1 <DLWeldConditionNumber> = <p1>,<p2>,<p3>,<p4>,<p5>,<p6>,<p7>,<p8>
```

> **Note:** `W1SET` is NOT emitted. It was removed from the output format.

### Weld Start Motion

The motion following ArcOn uses `LWS` instead of `LMOVE`:
```as
LWS <offset> + <point_name>
```

### Weld Continuous Motions

All linear motions between LWS and LWE use `LWC`:
```as
LWC <point> ,<condition_number>
```

Circular motions during welding:
```as
C1WC <via_point> ,<condition_number>
C2WC <end_point> ,<condition_number>
```

### Weld End (implicit via last ProcessCurve motion)

```as
LWE <offset> + <point_name> ,<condition_number>
LWE <offset> + <point_name> ,<condition_number>,<crater_condition_number>
```

The `,1` after LWE is the weld condition number. If crater is enabled, a second
condition number is appended.

After LWE, cleanup is emitted if sensing/RTPM were active:
```as
SSENSING OFF    ; if sensing was active
RTPM OFF        ; if RTPM was active
```

### ArcOn Extended Blocks (conditional)

After SETCONDW1, the following blocks are emitted in order if their conditions are met:

**Crater (if `DLWC2Crater=True`):**
```as
SET_ARC_W2JOBNO <craterCondNum> = <craterJobNum>
SETCONDW2 <craterCondNum> = <time>,<p2>,<p3>,<p4>,<p5>
```

**Software Slowdown (if `DLSSDown=Enabled`):**
```as
SETCONDW3 <preHeatTime>,,,,,,<weaveWidth>,<weaveFreq>, <weaveNum>
```

**Seam Sensing (if `DLPatternNum > 1`):**
```as
SSENSPTN <mappedPattern>
SSENS_SET <startDist>, <reliefDist>, <distInGroove>
SSENSING ON
```

**RTPM (if `DLRTPM=Enabled` and `DLWCRTPMNum=2`):**
```as
RTPM2_STARTGain ON/OFF[, <gainTime>, <vertCur>, <horizCur>, <changeCur>]
RT2DLYTIME <delayTime>
SET_ARC_RTPMREF <wireStick>
RT2Gain <vertGain>, <horizGain>
RT2BIAS <vertBias>, <horizBias>
RTPM ON
```

---

## 9. Touch Sensing Events

### Reference dump

```
EventName = "TouchSensingEvent"; EventType = "Process";
 Name = "TSContourTpeUUID"; Value = "...";
```

### Touch sensing operation pattern

Touch operations follow a strict 3-point sequence:

1. **Approach** → `LMOVE <offset> + <P_approach>`
2. **Collision** → `CALL KR_TOUCH (&<P_collision>, &<TS_ID>, ROTBASE_ON, <SensingLength×1000>, <SensingSpeed×1000>, <touch_index>)`
3. **Retract** → `LMOVE <offset> + <P_retract>`

With `STABLE 0.1` after the KR_TOUCH call.

### Touch point event types and roles

| Event Name | EventType | Role |
|-----------|-----------|------|
| `TouchPointStartAppEvent` | `Olp` | Marks approach start — set speed |
| `TouchSensingEvent` | `Process` | Touch sensing trigger |
| `TouchPointCollisionEvent` | `Olp` | The actual sensing point — `CALL KR_TOUCH` |
| `TouchPointStartRetEvent` | `Olp` | Marks retract start — set speed |

### Touch ID variables

Each group of touch operations creates a `POINT <progname>_TS_ID_<n> = NULL` variable.
Touch offsets: `<TS_ID> + <point_name>`.

For `TSConnectionType = "Frame3pConnect"` (PG05_3PFR):
- Variables are named `FRAME_PT_1`, `FRAME_PT_2`, `FRAME_PT_3` instead
- First touch of each frame uses touch_index = 1, 2, 3 (not 0)

### KR_TOUCH parameters

```
CALL KR_TOUCH (&<collision_point>, &<TS_ID>, ROTBASE_ON, <sensing_length>, <sensing_speed>, <touch_index>)
```

| Parameter | API Source | Conversion |
|-----------|-----------|------------|
| collision_point | `position.GetName()` | Pass by reference (`&`) |
| TS_ID | Generated from group/operation context | Pass by reference (`&`) |
| ROTBASE_ON | Global variable (0) | Direct |
| sensing_length | Attribute `SensingLength` | `× 1000` (meters → mm) |
| sensing_speed | Attribute `SensingSpeed` | `× 1000` (m/s → mm/s) |
| touch_index | Sequence counter per TS_ID | 0 for most, 1/2/3 for 3PFR |

---

## 10. Operation Group Comments

### Reference dump

```
Operation group:  GRP001
```

### Golden output

```as
;Operation Group: GRP001
```

---

## 11. Operation Comments

### Reference dump

```
Operation: WG1_Seam4 OperationType = Normal
```

### Golden output

```as
;Operation: WG1_Seam4
```

---

## 12. Euler Angle Conversion (E2 XYZs → Kawasaki OAT ZYZr)

Kawasaki OAT is **Z-Y'-Z'' intrinsic** (also called Euler ZYZ rotating):
$$R = R_z(O) \cdot R_{y'}(A) \cdot R_{z''}(T)$$

E2 default is **XYZ static** (`Euler_XYZs`). Convert via `cenpymath`:

```python
from cenpymath.Euler.Converter import Converter
from cenpymath.Euler.Notations import Notations

converter = Converter()
oat = converter.ConvertEuler(rx, ry, rz, Notations.Euler_ZYZr, Notations.Euler_XYZs)
# oat = [O, A, T] in degrees
```

### Verified pairs (10/10 match)

| E2 (Rx, Ry, Rz) | Kawasaki (O, A, T) |
|------------------|--------------------|
| (135, 0, 0) | (90, -135, -90) |
| (135, 0, 90) | (180, -135, -90) |
| (135, 0, 180) | (-90, -135, -90) |
| (135, 0, -90) | (0, -135, -90) |
| (-45, ~0, ~0) | (-90, -45, 90) |
| (125.26, 30, -35.26) | (35.27, -120, -125.26) |
| (125.26, 30, 54.74) | (125.27, -120, -125.26) |
| (125.26, 30, 144.74) | (-144.73, -120, -125.26) |
| (125.26, 30, -125.26) | (-54.73, -120, -125.26) |
| (175, 0, ~0) | (90, -175, -90) |

> **Note:** This is NOT ZYX extrinsic (which KUKA uses). Kawasaki's Z-Y'-Z''
> is a fundamentally different decomposition. Do not confuse O/A/T naming
> with KUKA's A/B/C despite both being called "Euler angles."

---

## 13. .TRANS Block Format

### Format

```
<point_name> <x_mm> <y_mm> <z_mm> <O_deg> <A_deg> <T_deg> [<ext1_deg> <ext2_deg> ...]
```

- Values separated by spaces
- Coordinates in mm (rounded to 2 decimal places, trailing zeros trimmed)
- Angles in degrees (rounded to 2 decimal places, trailing zeros trimmed)
- External axes appended if present (0-based rounding)
- Tool profile entry uses same format: `<tool_name> <x> <y> <z> <O> <A> <T>`

### Rounding

From the golden files, values appear to use 2 decimal places with trailing zero trimming:
- `0.002200 m × 1000 = 2.200` → `2.2`
- `0.118750 m × 1000 = 118.750` → `118.75`
- `1.191111 m × 1000 = 1191.111` → `1191.11`

---

## 14. Complete Event Type Catalog

All event types observed in the KAWASAKI ArcWelding scenarios:

| EventType | EventName(s) | Output Effect |
|-----------|-------------|---------------|
| `Speed` | `Speed` | `SPEED <value> MM/S ALWAYS` or `SPEED <value> ALWAYS` |
| `Accuracy` | `Accuracy` | `CP OFF` + `ACCURACY <value> ALWAYS` |
| `Acceleration` | `Acceleration` | `ACCEL <value> ALWAYS` |
| `Approach` | `ApproachArcWeldingStitch`, `Approach` | Context: marks approach, sets ACCEL 100 + PTP speed |
| `Retract` | `RetractArcWeldingStitch`, `Retract` | Context: marks retract phase (no output) |
| `Olp` | `ArcOnEvent` | `SET_ARC_W1JOBNO` + `SETCONDW1` [+ crater/sensing/RTPM], motion → `LWS` |
| `Olp` | `ArcOffEvent` | Last ProcessCurve → `LWE` [+ SSENSING OFF / RTPM OFF] |
| `Olp` | `ArcWeldConditionEvent` | Mid-weld param change (§18) |
| `Olp` | `TouchPointStartAppEvent` | Set approach speed for touch |
| `Olp` | `TouchPointCollisionEvent` | `CALL KR_TOUCH(...)` + `BREAK` |
| `Olp` | `TouchPointStartRetEvent` | Set retract speed for touch |
| `Olp` | `ConnectTouchProcessPointEvent` | Connect TS_ID offset to weld start |
| `Process` | `TouchSensingEvent` | Touch sensing context |
| `Process` | `TpeAtStartEvent` | TPE start marker (UUID reference) |
| `Process` | `TpeAtEndEvent` | TPE end marker |
| `LogicPort` | `LogicPort` | `SIGNAL` or `SWAIT` (§17) |
| `SetResourcePort` | `SetResourcePort` | Multi-signal `SIGNAL` (§17) |
| `WaitForResourcePort` | `WaitForResourcePort` | Multi-signal `WAIT SIG()` (§17) |
| `Olp` | `LT_Param_Event` | `LJT` + `LTBIAS` [+ `LT OFF`] (§20) |
| `Olp` | `LTOnEvent` | `LT ON` |
| `Olp` | `LTOffEvent` | `LT OFF` |
| `Olp` | `SPSEvent` | `SSENSPTN` (§21) |
| `Olp` | `TextEvent` | Comment or raw text (§22) |
| `Tool` | `Tool` | *(no separate output — tool set in header)* |
| `Insert` | `BuiltInEvent` | Sets PTP speed (internal) |

---

## 15. Callback Implementation Contract

The downloader **must** implement these callbacks:

| Callback | Required | Purpose |
|----------|----------|---------|
| `Initialize` | YES | Set output file path |
| `CreateOutputFile` | YES | (can be empty) |
| `ProgramStart` | YES | Emit `.PROGRAM`, header, init variables |
| `OperationGroupStart` | YES | Emit group comment, init TS_ID variables |
| `OperationGroupEnd` | optional | (no output) |
| `OperationStart` | YES | Emit operation comment |
| `OperationEnd` | optional | (no output) |
| `HandleEvent` | YES | Dispatch on EventType, emit speed/accuracy/weld/touch |
| `HandleMotion` | YES | Process events-before, emit motion, process events-after |
| `ProgramEnd` | YES | Emit `.END`, `.TRANS` block, `.END` |
| `CloseOutputFile` | YES | Call `operator.AddOutputFilePath()` |
| `WriteOutputFile` | optional | (can be empty) |

---

## 16. Known Gotchas

1. **Positions are in METERS** — always `× 1000` for mm output
2. **Speed Contour values are in m/s** — `× 1000` for mm/s
3. **Accuracy values are in meters** — `× 1000` for mm
4. **SensingLength / SensingSpeed are in meters/m/s** — `× 1000` for mm/mm/s
5. **ProfileIndex = "notDefined"** → means unmapped, don't use the index
6. **External joint values** are in degrees for this scenario (rotary positioner)
7. **CENOlpDataOutputStyle** determines implicit vs explicit position output
8. **Touch index** is 0 for normal sensing, 1/2/3 for 3-point frame reference
9. **LWS/LWE** replace LMOVE for weld start/end motions
10. **BoolAttribute.GetValue() returns Python `bool`** — use `str(attr.GetValue()) == 'True'`
11. **SPEED suppressed during welding** — welder controls speed between LWS and LWE
12. **ACCURACY suppressed during welding** — continuous path assumed
13. **CP OFF only** — never emit CP ON. Emit CP OFF once when first needed
14. **TRSUB wrapping** — positions wrapped in `TRSUB(pos)` when ROTBASE_ON=1
15. **.TRANS block sorted alphabetically** — position entries sorted by name

---

## 17. Signal Events (LogicPort / SetResourcePort / WaitForResourcePort)

### LogicPort — Single Signal

```
EventName = "LogicPort"; EventType = "LogicPort";
 Name = "EventType"; Value = "CENE2SetSignal";
 Name = "SignalName"; Value = "GAS_ON";
 Name = "SignalAddress"; Value = "2001";
 Name = "SignalNumber"; Value = "2001";
 Name = "SignalValue"; Value = "True";    ← Python bool!
```

| eventSubType | AS Output |
|--------------|-----------|
| `CENE2SetSignal`, value=True | `SIGNAL 2001 ; GAS_ON=On` |
| `CENE2SetSignal`, value=False | `SIGNAL -2001 ; GAS_ON=Off` |
| `CENE2WaitForSignal`, value=True | `SWAIT 2001 ; GAS_ON=On` |
| `CENE2WaitForSignal`, value=False | `SWAIT -2001 ; GAS_ON=Off` |

### SetResourcePort — Multi-Signal Container

A single event can contain multiple signals (attributes repeat in groups):

```
EventName = "SetResourcePort";
 Name = "SignalName"; Value = "SIG_A";   ← signal 1
 Name = "SignalAddress"; Value = "3001";
 Name = "SignalValue"; Value = "True";
 Name = "SignalName"; Value = "SIG_B";   ← signal 2
 Name = "SignalAddress"; Value = "3002";
 Name = "SignalValue"; Value = "False";
```

Output per signal: `SIGNAL {sign}{address} ; {name}={On/Off}`

### WaitForResourcePort — Multi-Signal Container

Same structure as SetResourcePort, different output syntax:

Output per signal: `WAIT SIG({sign}{address}) ; {name}={On/Off}`

---

## 18. ArcWeldConditionEvent (Mid-Weld Parameter Change)

Fires during welding to change parameters without stopping the arc.
Output order is DIFFERENT from ArcOnEvent:

1. *(if weave pattern)* `;WeavePattern: {name}` + `;WeaveNum: {num}`
2. *(if DLSSDown=Enabled)* `SETCONDW3 ...`
3. *(if RTPM)* RTPM block
4. *(if DLPatternNum>1)* `SSENSPTN` + `SSENS_SET` + `SSENSING ON`
5. *(if DLSetArcWeldMode≠None)* `SET_ARC_WELDMODE {mode}`
6. `SET_ARC_W1JOBNO` + `SETCONDW1`
7. *(if crater)* `SET_ARC_W2JOBNO` + `SETCONDW2`

The `DLWeldConditionNumber` from this event updates the condition number
used for subsequent `LWC` and `LWE` instructions.

---

## 19. ROTBASE / TRSUB

### Detection

Per operation: if `baseProfile.GetName()` starts with `"ROT_BASE"`:
- Set `ROTBASE_ON = 1`
- Wrap cartesian positions in `TRSUB(posTarget)`

### Output in header

```as
;Compensate track/rail/positioner
ROTBASE_ON = 1
```

### Position wrapping rules

| Target Type | ROTBASE_ON | Output |
|-------------|-----------|--------|
| Cartesian | 0 | `LMOVE posName` |
| Cartesian | 1 | `LMOVE TRSUB(posName)` |
| Joint (#) | any | `JMOVE #posName` (never wrapped) |
| Explicit inline | any | `LMOVE TRANS(...)` (never wrapped) |
| With touch offset | 1 | `LMOVE TRSUB(offset + posName)` |

---

## 20. Laser Tracker (LT) Events

### LT_Param_Event

```
EventName = "LT_Param_Event";
 Name = "DLJobNumberLaser"; Value = "1";
 Name = "DLLTBiasX"; Value = "0.001000";  (meters)
 Name = "DLLTBiasY"; Value = "0.002000";
 Name = "DLLTBiasZ"; Value = "0.000000";
 Name = "DLLTOff"; Value = "True";        (bool!)
```

Output:
```as
LJT 1
LTBIAS 1,2,0
LT OFF     ; only if DLLTOff=True
```

### LTOnEvent / LTOffEvent

| Event | Output |
|-------|--------|
| `LTOnEvent` | `LT ON` |
| `LTOffEvent` | `LT OFF` |

---

## 21. SPS (Standalone Seam Pattern Sensing) Event

```
EventName = "SPSEvent";
 Name = "DLPatternNum"; Value = "3";
 Name = "DLStartDist"; Value = "10";
 Name = "DLReliefDist"; Value = "5";
 Name = "DLDistInGroove"; Value = "15";
```

Output: `SSENSPTN 3,10,5,15`

---

## 22. TextEvent

```
EventName = "TextEvent";
 Name = "Text"; Value = "Custom user text here";
 Name = "IsComment"; Value = "True";       (bool!)
```

| IsComment | Output |
|-----------|--------|
| True | `; Custom user text here` |
| False | `Custom user text here` (raw line) |

---

## 23. CP and Buffered Motion Data

### CP Rules

- Only `CP OFF` is emitted, never `CP ON`
- Emitted once when state first changes to OFF
- Never emitted in touch sensing mode or explicit mode

### Buffered Flush Pattern

Motion settings are buffered from events and flushed before each motion:

```
SPEED → ACCEL → CP → ACCURACY → [motion instruction]
```

Each setting only emits when its value differs from last output (deduplication).

### Suppression during welding

| Setting | arcOnActive=True | arcOnActive=False |
|---------|------------------|-------------------|
| SPEED | Suppressed | Emitted |
| ACCURACY | Suppressed | Emitted |
| ACCEL | Touch-suppressed | Touch-suppressed |
| CP | Touch/explicit-suppressed | Touch/explicit-suppressed |

---

## 24. Sensing Pattern Number Mapping

| DLPatternNum (E2) | AS Output Number |
|--------------------|-----------------|
| 2–7 | +99 (→ 101–106) |
| 8–12 | −7 (→ 1–5) |
| Other | direct |

---

## 25. Subroutines (kr_touch / kr_frame)

Emitted between `.END` (main program) and `.TRANS` when `hasTouchSensing=True`.

### kr_touch

Called per touch collision point. Handles:
- XAC command for touch sensing
- ROTBASE_ON coordinate transformation
- Offset calculation

### kr_frame (Frame3pConnect only)

Called after 3 frame reference points are measured. Calculates:
- Reference frame from 3 original points
- Corrected frame from 3 touched points
- Offset = difference between frames

---

## 26. Complete File Structure

```
.PROGRAM {name}()
  ; FASTSUITE_II – Kawasaki Translator
  [;Compensate track/rail/positioner]
  [ROTBASE_ON = 0/1]
  TOOL {toolIdx}
  BASE {baseIdx}
  [CP OFF]
  HOME
  ... motion/event body ...
  HOME
.END
[.PROGRAM kr_touch(...)]
[  ... subroutine body ...]
[.END]
[.PROGRAM kr_frame(...)]
[  ... subroutine body ...]
[.END]
.TRANS
  {sorted cartesian positions and tool profile}
.JOINTS
  {sorted joint positions}
```
