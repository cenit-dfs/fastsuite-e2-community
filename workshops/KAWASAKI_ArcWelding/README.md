# Workshop: KAWASAKI Arc Welding Downloader

Build a Kawasaki AS-language downloader from scratch using Copilot — step by step, from planning to a working plugin.

## What You Will Build

| Phase | What | Golden file(s) | Coordinate mode |
|-------|------|----------------|-----------------|
| **Warm-up** | Create a Kawasaki controller skill so Copilot understands AS syntax | — | — |
| **Phase 1** | Basic downloader — JMOVE/LMOVE, speed, accel, CP, accuracy, tool, base | `PG06_BASIC.as`, `PG07_BASIC_EXP.as` | Implicit + Explicit |
| **Phase 2** | Arc welding plugin — touch sensing, weld commands, job numbers | `PG01_OP.as`, `PG02_SE.as` | Implicit only |
| **Stretch** | More touch sensing patterns (ShortestDistance, 3-point frame) | `PG04_SD.as`, `PG05_3PFR.as` | Implicit only |

## What's in This Folder

| Folder | Content |
|--------|---------|
| `scenarios/` | `Kawasaki_WS_Small.cendoc` — E2 project file, load this into FASTSUITE E2 |
| `reference/` | Simple Translator tree dumps (`.txt`) for each program + legacy CD XML (`.xml`) |
| `golden/` | Expected output programs — your downloader should produce these |
| `docs/` | Kawasaki AS Language Reference Manual (converted from PDF) |

## Prerequisites

- FASTSUITE E2 R2026.1 installed and licensed
- VS Code with Copilot set up (see [Getting Started](https://github.com/cenit-dfs/fastsuite-copilot-starter/blob/master/docs/workshop/getting-started.md))
- Your own clone of the starter repo
- Recommended: switch to **E2Downloader** agent mode in Copilot Chat

---

## Warm-Up: Create a Controller Skill (15 min)

> **Why this matters:** Copilot doesn't know Kawasaki AS syntax by default. A skill file teaches it the robot language so it can generate correct output. This is the first thing you do for any new controller.

### Step 1: Read the reference material

Before writing anything, spend a few minutes looking at:
- `golden/PG06_BASIC.as` — a simple program showing the output format
- `docs/90209-1022DED_E-Series-AS-Language_Reference_Manual.md` — the full AS language reference

### Step 2: Ask Copilot to create a skill

Open Copilot Chat and prompt:

> *I need a Kawasaki AS language skill file for creating a FASTSUITE E2 downloader. Read the AS language reference manual at `community/workshops/KAWASAKI_ArcWelding/docs/90209-1022DED_E-Series-AS-Language_Reference_Manual.md` and the golden output file at `community/workshops/KAWASAKI_ArcWelding/golden/PG06_BASIC.as`. Create a concise skill file that covers:*
> - *Program structure (.PROGRAM / .END / .TRANS)*
> - *Motion commands (JMOVE, LMOVE) and position naming*
> - *Speed/acceleration/accuracy/CP commands*
> - *Tool and base frame setup (TOOL, BASE, RIGHTY, ABOVE, DWRIST)*
> - *Implicit vs explicit coordinate output*
> - *Arc welding commands (LWS/LWE/LWC, C1WC/C2WC, W1SET, SETCONDW1, SET_ARC_W1JOBNO)*
> - *Touch sensing (KR_TOUCH call, POINT declarations, TS_ID offsets)*
> - *.TRANS block format (mm, degrees)*

### Step 3: Save the skill

Save the generated file to `skills/kawasaki/SKILL.md` in your repo. Review it — does it match what you see in the golden files? Adjust if needed.

### Step 4: Register the skill

Copilot will automatically find skills in the `skills/` folder. You can verify by asking:

> *What do you know about Kawasaki AS language?*

---

## Phase 1: Basic Downloader (60-90 min)

### Goal

Create `OLPTranslators/KAWASAKI/KAWASAKI_E.py` that produces output matching `golden/PG06_BASIC.as`.

PG06_BASIC is a simple program with:
- 4 weld seam operations (approach → process → retract pattern, repeated 4 times)
- JMOVE for approach (PTP), LMOVE for process/retract (linear)
- Speed changes (50% PTP, 500 mm/s linear approach, 5.833 mm/s process, 500 mm/s retract)
- CP ON/OFF toggling with accuracy for fly-by motions
- Tool and base frame output in `.TRANS` block
- All coordinates **implicit** (named positions like `PG06_BASIC_P0001`)

### Step 1: Create a spec

Ask Copilot to analyze the reference data and write a specification:

> *Read the tree dump at `community/workshops/KAWASAKI_ArcWelding/reference/PG06_BASIC.txt` and the expected output at `community/workshops/KAWASAKI_ArcWelding/golden/PG06_BASIC.as`. Write a specification for a Kawasaki E-Series downloader that produces this output. Include:*
> - *File structure (.PROGRAM header, motion body, .TRANS block)*
> - *How E2 motion types map to AS commands (Pt2Pt → JMOVE, Linear → LMOVE)*
> - *How E2 events (Speed, Accuracy) map to AS commands*
> - *Position naming convention*
> - *Unit conversions (E2 uses meters, AS uses mm; E2 uses m/s, AS uses mm/s)*
> - *Tool/base frame format in .TRANS*
> - *Config flags (RIGHTY/LEFTY, ABOVE/BELOW, DWRIST/UWRIST)*
> - *Support for both implicit and explicit coordinate output (based on the CENOlpDataOutputStyle resource attribute)*

Review the spec. Does it match the golden file? Correct anything the agent got wrong.

Save the spec to `docs/KAWASAKI/spec/basic_downloader.md` in your repo.

### Step 2: Generate the downloader

> *Using the spec at `docs/KAWASAKI/spec/basic_downloader.md`, the Kawasaki skill, the base downloader template at `skills/downloader/templates/base_downloader.py`, and the canonical ABB_IRC5 example at `community/OLPTranslators/ABB/ABB_IRC5.py` — create a Kawasaki E-Series downloader at `OLPTranslators/KAWASAKI/KAWASAKI_E.py`.*
>
> *Important:*
> - *Set `DOWNLOAD_CLASS_NAME = "KAWASAKI_E"`*
> - *Support both implicit and explicit coordinate modes*
> - *Read the `CENOlpDataOutputStyle` resource attribute to determine the mode*
> - *In implicit mode, collect positions and output them in the .TRANS block*
> - *In explicit mode, output coordinates inline (e.g., `LMOVE TRANS(x, y, z, rx, ry, rz)`)*
> - *E2 positions are in meters — convert to mm for AS output*
> - *Speed values: PTP in %, linear in mm/s*

### Step 3: Test in E2

1. Copy `KAWASAKI_E.py` to E2's translator folder (or configure E2 to use your repo path)
2. Load `scenarios/Kawasaki_WS_Small.cendoc` in E2
3. Run the download for PG06_BASIC
4. Compare the output against `golden/PG06_BASIC.as`:
   - Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Compare Output vs Golden"
   - Or: right-click your output file → "Select for Compare", then right-click the golden → "Compare with Selected"

### Step 4: Debug

If the output doesn't match, show Copilot the diff:

> *Compare my downloader output (paste or reference the file) with the expected golden file at `community/workshops/KAWASAKI_ArcWelding/golden/PG06_BASIC.as`. Identify the differences and fix them in my downloader.*

Common issues to watch for:
- **Position values wrong** — check unit conversion (meters → mm, rounding)
- **Speed format wrong** — PTP uses `SPEED 50 ALWAYS` (%), linear uses `SPEED 500 MM/S ALWAYS`
- **Missing CP/ACCURACY** — these are driven by Accuracy events; check event handling
- **Point names wrong** — naming convention: `<PROGNAME>_P<NNNN>` (4-digit, zero-padded)
- **Tool/base in .TRANS** — format: `name x y z rz ry rx` (note angle order: OAT)

### Step 5: Test explicit mode

Once implicit mode works:
1. In E2, change the `CENOlpDataOutputStyle` resource attribute to `"Explicit"`
2. Download PG07_BASIC_EXP (this is the same geometry as PG06 but configured for explicit output)
3. Compare against `golden/PG07_BASIC_EXP.as`

Key differences from implicit mode:
- Positions are inline: `LMOVE TRANS (118.75, 1191.11, 1093.61, 90, -135, -90, 0, 180)`
- No named position variables — no `.TRANS` block for positions (only for the tool frame)
- Same motion structure otherwise (JMOVE/LMOVE, speed, accuracy, CP)

### Checkpoint

Before moving to Phase 2, your downloader should:
- ☑ Produce PG06_BASIC.as output matching the golden (implicit mode)
- ☑ Produce correct explicit output when CENOlpDataOutputStyle = "Explicit"
- ☑ Handle JMOVE (PTP) and LMOVE (Linear) correctly
- ☑ Handle Speed, Accuracy, and CP events
- ☑ Output tool and base frames in .TRANS block

---

## Phase 2: Arc Welding Plugin (60-90 min)

### Goal

Add an arc welding plugin (following the ABB_IRC5.py plugin pattern) that handles:
- Touch sensing operations (KR_TOUCH calls, POINT TS_ID declarations, offset coordinates)
- Weld commands (LWS/LWE, W1SET, SETCONDW1, SET_ARC_W1JOBNO)
- Operation group structure (comments, TS_ID per group)

Arc welding uses **implicit mode only** — inline TRANS() coordinates are not supported for welded/touched positions.

### Step 1: Study the arc welding golden

Open `golden/PG01_OP.as` and `reference/PG01_OP.txt`. Notice:
- **Operation groups** with `POINT <prog>_TS_ID_<n> = NULL` declarations
- **Touch sensing** operations call `KR_TOUCH` with approach/sense/retract pattern
- **Seam welding** operations use `LWS` / `LWE` with weld conditions
- All positions use **TS_ID offsets**: `LMOVE PG01_OP_TS_ID_1 + PG01_P0002`

### Step 2: Create an arc welding spec

> *Read the tree dump at `community/workshops/KAWASAKI_ArcWelding/reference/PG01_OP.txt` and the golden output at `community/workshops/KAWASAKI_ArcWelding/golden/PG01_OP.as`. Also read `community/workshops/KAWASAKI_ArcWelding/golden/PG02_SE.as` and its tree dump. Create a specification for an arc welding plugin that extends my KAWASAKI_E.py downloader. Cover:*
> - *How operation groups map to TS_ID POINT declarations*
> - *Touch sensing operation pattern (approach → sense with KR_TOUCH → retract)*
> - *KR_TOUCH call parameters and how they come from E2 attributes*
> - *Seam welding commands (LWS/LWE) and weld conditions (SETCONDW1, W1SET, SET_ARC_W1JOBNO)*
> - *How PG01_OP (OperationConnect) differs from PG02_SE (StartEndConnect) in TS_ID usage*
> - *The ROTBASE_ON variable and positioner compensation comment*

Save to `docs/KAWASAKI/spec/arcwelding_plugin.md`.

### Step 3: Generate the plugin

> *Using the arc welding spec, extend my KAWASAKI_E.py downloader with an arc welding plugin. Follow the plugin architecture from `community/OLPTranslators/ABB/ABB_IRC5.py` — use a separate plugin class that the main downloader delegates to when the technology is ArcWeldingTechnology. The plugin should handle:*
> - *Operation group setup (TS_ID POINT declarations)*
> - *Touch sensing operations (KR_TOUCH call pattern)*
> - *Seam welding (LWS/LWE with weld conditions)*
> - *TS_ID-offset position output*
> - *Reading operation and event attributes from E2*

### Step 4: Test against PG01_OP

1. Download PG01_OP from E2
2. Compare output against `golden/PG01_OP.as`
3. Debug with Copilot until it matches

### Step 5: Test against PG02_SE

PG02_SE uses `StartEndConnect` pattern — touch sensing references two TS_IDs for seam start and end. Download and compare.

### Checkpoint

- ☑ PG01_OP output matches golden (OperationConnect pattern)
- ☑ PG02_SE output matches golden (StartEndConnect pattern)
- ☑ Touch sensing, weld commands, and TS_ID offsets all work
- ☑ Basic mode (PG06_BASIC) still works — no regressions

---

## Stretch Goals

If you finish early, try these more complex touch sensing patterns:

| Program | Pattern | What's different |
|---------|---------|-----------------|
| `PG03_SE.as` | StartEndConnect with approach JMOVEs | Extra approach motions before first touch |
| `PG04_SD.as` | ShortestDistanceConnect | Multiple TS_IDs across many operation groups |
| `PG05_3PFR.as` | Frame3pConnect (3-point frame) | `FRAME_PT_*` point names, `KR_FRAME` call, circular weld commands (C1WC/C2WC) |

---

## Tips for Working with the Agent

1. **Show it the diff, not just the error** — "My output has `SPEED 500` but the golden has `SPEED 500 MM/S ALWAYS`" is more helpful than "speed is wrong"
2. **One problem at a time** — fix position output first, then events, then arc welding
3. **Reference the golden file explicitly** — the agent can read files in `community/`
4. **Check the tree dump when stuck** — it shows exactly what E2 provides (attribute names, types, values)
5. **Commit after each phase** — save your progress so you can roll back if something breaks
6. **Don't modify community files** — all your code goes in `OLPTranslators/KAWASAKI/` in your repo
