# ABB Data Management - Customization Guide

**Version:** 1.0  
**Date:** January 28, 2026  
**Audience:** OLP Programmers, Project Engineers, System Integrators

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Storage Structure](#storage-structure)
4. [Schema Files](#schema-files)
5. [Instance Files](#instance-files)
6. [Controller Configuration](#controller-configuration)
7. [Default JSON Options](#default-json-options)
8. [Maintaining Data Lists](#maintaining-data-lists)
9. [Operation Attributes](#operation-attributes)
10. [Output Control](#output-control)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

---

## Overview

The ABB Data Management system allows you to customize arc welding data (seamdata, welddata, weavedata, trackdata) per controller without modifying Python code.

**Key Benefits:**
- ✅ Cell-specific data configurations
- ✅ Easy maintenance through JSON files
- ✅ No code changes required
- ✅ Version control friendly
- ✅ Non-destructive editing (no deletion)

**How It Works:**
1. Technology scripts present data pickers to users
2. Selected data names stored in Operation attributes
3. Downloader reads attributes and outputs declarations
4. Only used data instances appear in final RAPID code

---

## Quick Start

### For New Controllers

**Step 1:** Create controller folder structure
```
Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/Data/
  MyCell_IRC5/
```

**Step 2:** Copy default templates
```powershell
Copy-Item Default/Fronius_CMT/* MyCell_IRC5/
```

**Step 3:** Edit instance files with your data
```json
// MyCell_IRC5/seamdata_instances.json
{
  "version": "1.0",
  "controller": "MyCell_IRC5",
  "instances": [
    {
      "name": "sd_thin_3mm",
      "description": "Thin material 3mm",
      "values": {"seam_type": 1, "seam_tracking": false, "seam_speed": 30.0, "seam_accel": 5.0}
    }
  ]
}
```

**Step 4:** Technology scripts automatically find and use the data

---

## Storage Structure

### Directory Layout

```
Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/
  Data/
    <ControllerName>/              # Per-cell data folder
      seamdata_schema.json         # Schema definition
      seamdata_instances.json      # Data instances
      welddata_schema.json
      welddata_instances.json
      weavedata_schema.json
      weavedata_instances.json
      trackdata_schema.json
      trackdata_instances.json
    Default/                       # Default templates
      Fronius_CMT/                 # Fronius power source
      Kemppi/                      # Kemppi power source
      Generic_ABB/                 # Generic ABB structure
  naming.json                      # Legacy touch sensing config
```

### File Naming Convention

- Schema files: `<datatype>_schema.json`
- Instance files: `<datatype>_instances.json`
- Controller name must match E2 controller name exactly
- Use consistent naming across all files

---

## Schema Files

### Complete Schema Definitions

All four ABB data types now have complete schemas with nested arrays matching ABB RAPID structure:

#### welddata
```
TASK PERS welddata MBM_Fe_Puls_a5:=[7,0,[29,0,0,0,0,230,0,0,0],[0,0,0,0,0,0,0,0,0]];
```
Fields: `[weld_speed, org_weld_speed, [main_arc[9]], [reserved[9]]]`

#### seamdata
```
TASK PERS seamdata sm1:=[0.5,0.2,[0,0,0,0,0,0,0,0,0],0,1,0,0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0,0,[0,0,0,0,0,0,0,0,0],0.2];
```
Fields: 16 elements including purge_time, preflow_time, scrape_start, postflow_time, and 4 reserved arrays[9]

#### weavedata
```
TASK PERS weavedata wv_5mm:=[1,0,4,5,0,0,0,0,0,0,0,0,0,0,0];
```
Fields: 15 elements covering weave shape, dimensions, dwell times, orientation

#### trackdata
```
TASK PERS trackdata tr_a3:=[0,FALSE,0,[0,25,30,0,0,0,0,0,0],[0,0,0,0,0,0,0]];
```
Fields: `[track_system, store_path, max_corr, [arctrack[9]], [reserved[7]]]`

**Note:** Bool fields output as uppercase RAPID keywords (`TRUE`/`FALSE`), not lowercase.

### Purpose

Schema files define the **structure** of a data type for a specific controller. They specify:
- Field names and types
- Output order (RAPID declaration order)
- UI display settings
- Default values
- Validation rules
- Array dimensions for nested structures

### Schema File Format

**File:** `seamdata_schema.json`

```json
{
  "version": "1.0",
  "data_type": "seamdata",
  "rapid_type": "seamdata",
  "description": "Seam tracking parameters for Fronius CMT",
  
  "fields": [
    {
      "name": "seam_type",
      "display_name": "Seam Type",
      "type": "Integer",
      "output_index": 0,
      "default": 1,
      "description": "Seam type: 1=Linear, 2=Circular",
      "min": 1,
      "max": 2
    },
    {
      "name": "seam_tracking",
      "display_name": "Seam Tracking",
      "type": "Bool",
      "output_index": 1,
      "default": false,
      "description": "Enable seam tracking"
    },
    {
      "name": "seam_speed",
      "display_name": "Speed (mm/s)",
      "type": "Double",
      "output_index": 2,
      "default": 100.0,
      "description": "Seam welding speed",
      "unit": "mm/s",
      "min": 10.0,
      "max": 500.0
    },
    {
      "name": "seam_accel",
      "display_name": "Acceleration",
      "type": "Double",
      "output_index": 3,
      "default": 5.0,
      "description": "Seam acceleration",
      "min": 1.0,
      "max": 20.0
    }
  ],
  
  "declaration_template": "{scope} PERS {rapid_type} {name}:=[{values}];"
}
```

### Field Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `name` | Yes | String | Internal field name (use for values object keys) |
| `display_name` | Yes | String | UI label |
| `type` | Yes | String | `Integer`, `Double`, `Bool`, `String`, `Array` |
| `output_index` | Yes | Integer | Position in RAPID declaration (0-based) |
| `default` | Yes | Mixed | Default value matching type |
| `description` | No | String | Help text for UI |
| `unit` | No | String | Unit suffix for UI (e.g., "mm", "°") |
| `min` | No | Number | Minimum value (Integer/Double) |
| `max` | No | Number | Maximum value (Integer/Double) |
| `hidden` | No | Bool | Hide from UI (for reserved fields) |
| `ui_hint` | No | String | UI widget hint: `combo`, `slider`, `grid` |
| `options` | No | Array | Options for combo box |

### Field Types

**Integer:** Whole numbers
```json
{"type": "Integer", "default": 1, "min": 0, "max": 10}
```

**Double:** Decimal numbers
```json
{"type": "Double", "default": 100.0, "min": 10.0, "max": 500.0}
```

**Bool:** Boolean values (true/false in JSON, TRUE/FALSE in RAPID)
```json
{"type": "Bool", "default": false}
```

**String:** Text values (rarely used in RAPID data)
```json
{"type": "String", "default": ""}
```

**Array:** Array of values (for nested structures like main_arc parameters)
```json
{
  "name": "main_arc",
  "type": "Array",
  "array_type": "Integer",
  "array_size": 9,
  "output_index": 2,
  "default": [29, 0, 0, 0, 0, 230, 0, 0, 0],
  "column_headers": ["sched", "current", "voltage", "wire_feed", "dyn_corr", "arc_length", "gas_flow", "res1", "res2"],
  "description": "Main arc parameters [9 elements]"
}
```
Output in RAPID: `[29,0,0,0,0,230,0,0,0]` (enclosed in brackets)

**Note on Bool formatting:** JSON uses lowercase `true`/`false`, but RAPID output is uppercase `TRUE`/`FALSE`.

### Reserved/Unnamed Fields

Some power sources have reserved positions in data declarations:

```json
{
  "name": "",
  "display_name": "",
  "type": "Integer",
  "output_index": 1,
  "default": 0,
  "hidden": true,
  "description": "Reserved field - do not modify"
}
```

**Important:** Keep reserved fields to maintain compatibility with existing RAPID code.

---

## Instance Files

### Purpose

Instance files contain the **actual data values** that users can select. Each instance is a named set of values.

### Instance File Format

**File:** `welddata_instances.json`

```json
{
  "version": "1.0",
  "controller": "MyCell_IRC5",
  "data_type": "welddata",
  
  "instances": [
    {
      "name": "wd_default",
      "description": "Default welding parameters",
      "values": {
        "voltage": 20.0,
        "current": 150.0,
        "wire_speed": 5.0,
        "gas_flow": 12.0
      }
    },
    {
      "name": "wd_thin",
      "description": "Thin material (1-3mm)",
      "values": {
        "voltage": 18.0,
        "current": 100.0,
        "wire_speed": 3.5,
        "gas_flow": 10.0
      }
    },
    {
      "name": "wd_thick",
      "description": "Thick material (5mm+)",
      "values": {
        "voltage": 22.0,
        "current": 180.0,
        "wire_speed": 6.5,
        "gas_flow": 15.0
      }
    }
  ]
}
```

### Instance Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `name` | Yes | String | Unique identifier for RAPID (e.g., "wd_thin") |
| `description` | Yes | String | User-friendly description for UI |
| `values` | Yes | Object | Field values (keys match schema field names) |
| `tags` | No | Array | Tags for filtering/search (e.g., ["thin", "aluminum"]) |
| `readonly` | No | Bool | Prevent editing in UI |

### Naming Conventions

**Best Practices:**
- Use descriptive prefixes: `sd_`, `wd_`, `wv_`, `tr_`
- Include key parameters: `wd_thin_18V`, `wv_triangle_5mm`
- Avoid spaces and special characters (use underscores)
- Maximum 16 characters for RAPID compatibility

**Examples:**
```
sd_linear_50       - Seamdata, linear, 50mm/s
wd_thick55         - Welddata, thick material, 55% power
wv_triangle_5mm    - Weavedata, triangle pattern, 5mm width
tr_default         - Trackdata, default tracking
```

---

## Controller Configuration

### Technology Configuration

Technology scripts load data based on controller name from E2 project.

**Location:** `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/`

**Key Files:**
- `ArcWeldingTechnology.py` - Technology initialization
- `ArcWeldingDataPicker.py` - Data picker UI (future)
- `ArcWeldingDataEditor.py` - Data editor UI (future)

### Controller Name Matching

The system automatically finds data for the controller:

```python
# In Technology script
controller = GetController()
controllerName = controller.GetName()  # e.g., "MyCell_IRC5"

# System looks for:
# TechTabs/Data/MyCell_IRC5/seamdata_schema.json
# TechTabs/Data/MyCell_IRC5/seamdata_instances.json
```

**Fallback:** If controller-specific data not found, uses `Default/Generic_ABB/`

---

## Default JSON Options

### ABB_IRC5_DL.json Configuration

**Location:** `OLPTranslators/ABB/ABB_IRC5_DL.json`

This file controls downloader behavior. Data management uses these sections:

```json
{
  "defaults": {
    "data_management": {
      "enabled": true,
      "use_weaving": true,
      "use_tracking": true,
      "default_scope": "local"
    }
  },
  
  "stations": {
    "default": 2,
    "enabled": true,
    "list": [
      {"index": 1, "setup_proc": "StartStn1", "wobj": "wobjUse"},
      {"index": 2, "setup_proc": "StartStn2", "wobj": "wobjUse"}
    ]
  }
}
```

### Data Management Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | Bool | true | Enable data management system |
| `use_weaving` | Bool | true | Enable weavedata declarations |
| `use_tracking` | Bool | true | Enable trackdata declarations |
| `default_scope` | String | "local" | Default scope: "local" or "task" |

**Note:** These are defaults. Operation attributes override at runtime.

### naming.json (TechTab)

**Location:** `Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/naming.json`

This file now only contains legacy touch sensing configuration:

```json
{
  "naming": {
    "touch_shift_base": "pose"
  }
}
```

**Historical Note:** Previously contained data naming config. Now uses Operation attributes instead.

---

## Maintaining Data Lists

### Adding New Data Instances

**Step 1:** Open instance file
```powershell
notepad TechTabs/Data/MyCell_IRC5/welddata_instances.json
```

**Step 2:** Add new instance to `instances` array
```json
{
  "name": "wd_aluminum_thin",
  "description": "Aluminum thin sheets (1-2mm)",
  "values": {
    "voltage": 17.5,
    "current": 95.0,
    "wire_speed": 3.0,
    "gas_flow": 11.0
  }
}
```

**Step 3:** Save file (system automatically reloads)

**Important Rules:**
- **Never delete instances** (breaks existing programs)
- Always add to end of list
- Ensure `name` is unique
- All schema fields must have values

### Modifying Existing Data

**Safe Modifications:**
- ✅ Change `description` (UI only)
- ✅ Update `values` if program behavior change is intended
- ✅ Add `tags` or other metadata

**Dangerous Modifications:**
- ⚠️ Changing `name` breaks existing programs
- ⚠️ Removing instances breaks existing programs
- ⚠️ Changing value types can cause RAPID syntax errors

**Best Practice:** Create new instance with corrected values instead of modifying:
```json
{
  "name": "wd_thin_v2",
  "description": "Thin material (revised)",
  "values": {...}
}
```

### Deprecating Old Data

Instead of deleting, mark as deprecated:

```json
{
  "name": "wd_old",
  "description": "[DEPRECATED] Use wd_new instead",
  "values": {...},
  "readonly": true,
  "tags": ["deprecated"]
}
```

### Bulk Import from RAPID

If you have existing RAPID data declarations, use migration tool:

```powershell
# Extract data from RAPID file
python rapid_parser.py MyProgram.mod MyCell_IRC5

# Generates:
# - seamdata_instances.json
# - welddata_instances.json
# - etc.
```

**Note:** Migration tool under development. Manual extraction for now.

---

## Operation Attributes

### How Data Names are Set

Technology scripts populate Operation attributes when user selects data:

| Attribute Name | Type | Scope | Purpose |
|----------------|------|-------|---------|
| `SEAM_DATA_NAME` | String | Operation | Selected seamdata instance name |
| `WELD_DATA_NAME` | String | Operation | Selected welddata instance name |
| `WEAVE_DATA_NAME` | String | Operation | Selected weavedata instance name (optional) |
| `TRACK_DATA_NAME` | String | Operation | Selected trackdata instance name (optional) |

**Example:** User selects "wd_thick55" → Technology sets `WELD_DATA_NAME = "wd_thick55"`

### Attribute Flow

```
Technology Script (ArcWeldingTechnology.py)
    ↓ User selects data from picker
    ↓ Sets Operation attribute: WELD_DATA_NAME = "wd_thick55"
    ↓
Downloader (ABB_IRC5.py)
    ↓ operation_start() reads attribute
    ↓ Calls _track_data_usage('welddata', 'wd_thick55')
    ↓ Accumulates in _data_used_names dict
    ↓
ProgramEnd()
    ↓ OutputDataDeclarations() matches used names
    ↓ Looks up instance in welddata_instances.json
    ↓ Formats declaration: LOCAL PERS welddata wd_thick55:=[...]
    ↓ Outputs to Data section before PROC
```

### Fallback Behavior

If Operation attribute not set, uses legacy index-based naming:

```python
# SEAM_DATA_NAME not set
seam_num = operation.GetInteger('Seamdata Number')  # → 1
→ Uses "seam1" as name

# WELD_DATA_NAME not set
weld_num = operation.GetInteger('Welddata Number')  # → 2
→ Uses "weld2" as name
```

**Legacy Support:** Ensures compatibility with old programs that don't use new system.

---

## Output Control

### Declaration Scope

Controlled by `GLOBAL_DATA` attribute (Global level):

**LOCAL PERS (default):**
```rapid
LOCAL PERS seamdata sd_linear_50:=[1,FALSE,50.0,5.0];
LOCAL PERS welddata wd_thick55:=[22.0,180.0,6.5,15.0];
```

**TASK PERS (GLOBAL_DATA = true):**
```rapid
TASK PERS seamdata sd_linear_50:=[1,FALSE,50.0,5.0];
TASK PERS welddata wd_thick55:=[22.0,180.0,6.5,15.0];
```

**When to Use:**
- `LOCAL PERS`: Data private to one module (default, recommended)
- `TASK PERS`: Data shared across modules (rare, legacy systems)

### Optional Parameters

Weave and Track parameters automatically appended when set:

```rapid
ArcLStart P027,v500,sd_default,wd_thick55\Weave:=wv_triangle_5mm\Track:=tr_default,fine,tWeldGun\WObj:=obNEW_1;
```

**Rules:**
- Weave output if `WEAVE_DATA_NAME` is set
- Track output if `TRACK_DATA_NAME` is set
- No comma before `\Weave` or `\Track` (appended to welddata)

### Only Used Data

**Optimization:** Only data instances actually used in operations are declared.

**Example:**
- Instance file has 10 welddata entries
- Program only uses `wd_default` and `wd_thick55`
- Only those 2 appear in RAPID output

**Benefits:**
- Cleaner output
- Faster robot loading
- Easier debugging

---

## Troubleshooting

### Data Not Appearing in Output

**Symptom:** No data declarations in RAPID file

**Checks:**
1. Verify data management enabled:
   ```json
   // ABB_IRC5_DL.json
   "data_management": {"enabled": true}
   ```

2. Check Operation attributes are set:
   ```python
   # In Technology script
   operation.SetStringAttribute('SEAM_DATA_NAME', 'sd_linear_50')
   ```

3. Verify instance file exists and loads:
   ```
   TechTabs/Data/<ControllerName>/seamdata_instances.json
   ```

4. Check E2 log for errors:
   ```
   Failed to load data management: ...
   Data management not available - skipping
   ```

### Wrong Data Values in Output

**Symptom:** Declaration has unexpected values

**Checks:**
1. Verify instance name matches:
   ```json
   {"name": "sd_linear_50", ...}  // Must match attribute value exactly
   ```

2. Check values object has all required fields:
   ```json
   "values": {
     "seam_type": 1,      // ← All schema fields must be present
     "seam_tracking": false,
     "seam_speed": 50.0,
     "seam_accel": 5.0
   }
   ```

3. Verify schema `output_index` order:
   ```json
   [
     {"output_index": 0, ...},  // → First value in RAPID
     {"output_index": 1, ...},  // → Second value
     ...
   ]
   ```

### Schema/Instance Mismatch

**Symptom:** Missing values or wrong type in output

**Fix:** Ensure instance values match schema field names:

**Schema:**
```json
{"name": "seam_speed", "type": "Double", "output_index": 2}
```

**Instance (Correct):**
```json
{"values": {"seam_speed": 50.0}}
```

**Instance (Wrong):**
```json
{"values": {"speed": 50.0}}  // ← Wrong key name
```

### Weave/Track Not Appearing

**Symptom:** `\Weave:=` or `\Track:=` missing from Arc commands

**Checks:**
1. Verify attribute is set:
   ```python
   operation.SetStringAttribute('WEAVE_DATA_NAME', 'wv_triangle_5mm')
   ```

2. Check weavedata instance exists:
   ```
   TechTabs/Data/<ControllerName>/weavedata_instances.json
   ```

3. Ensure name matches:
   ```json
   {"name": "wv_triangle_5mm", ...}
   ```

### Controller Name Mismatch

**Symptom:** Using Default data instead of controller-specific

**Fix:** Ensure folder name matches E2 controller name exactly:
```
E2 Controller Name:  MyCell_IRC5
Folder Name:         Data/MyCell_IRC5/  ← Must match exactly
```

**Case Sensitive:** Windows is case-insensitive, but git is case-sensitive. Use exact case.

---

## Examples

### Example 1: Simple Seamdata Setup

**Goal:** Create seamdata instances for a new cell.

**Step 1:** Create controller folder
```
TechTabs/Data/Cell_A/
```

**Step 2:** Create schema (copy from Default/Fronius_CMT)
```json
// Cell_A/seamdata_schema.json
{
  "version": "1.0",
  "data_type": "seamdata",
  "rapid_type": "seamdata",
  "fields": [
    {"name": "seam_type", "type": "Integer", "output_index": 0, "default": 1},
    {"name": "seam_tracking", "type": "Bool", "output_index": 1, "default": false},
    {"name": "seam_speed", "type": "Double", "output_index": 2, "default": 100.0},
    {"name": "seam_accel", "type": "Double", "output_index": 3, "default": 5.0}
  ]
}
```

**Step 3:** Create instances
```json
// Cell_A/seamdata_instances.json
{
  "version": "1.0",
  "controller": "Cell_A",
  "instances": [
    {
      "name": "sd_default",
      "description": "Default seam",
      "values": {"seam_type": 1, "seam_tracking": false, "seam_speed": 100.0, "seam_accel": 5.0}
    },
    {
      "name": "sd_fast",
      "description": "Fast welding",
      "values": {"seam_type": 1, "seam_tracking": false, "seam_speed": 150.0, "seam_accel": 8.0}
    }
  ]
}
```

**Step 4:** Technology script sets attribute
```python
operation.SetStringAttribute('SEAM_DATA_NAME', 'sd_fast')
```

**Step 5:** Download produces
```rapid
LOCAL PERS seamdata sd_fast:=[1,FALSE,150.0,8.0];
...
ArcLStart P1,v500,sd_fast,wd_default,fine,tWeldGun\WObj:=wobj;
```

### Example 2: Weavedata with Array Fields

**Goal:** Add weavedata with complex pattern array.

**Schema:**
```json
{
  "fields": [
    {"name": "weave_type", "type": "Integer", "output_index": 0, "default": 0},
    {"name": "weave_on", "type": "Bool", "output_index": 1, "default": false},
    {"name": "weave_width", "type": "Double", "output_index": 2, "default": 0.0},
    {"name": "weave_speed", "type": "Double", "output_index": 3, "default": 0.0},
    {
      "name": "weave_pattern",
      "type": "Array",
      "array_length": 8,
      "element_type": "Double",
      "output_index": 4,
      "default": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }
  ]
}
```

**Instance:**
```json
{
  "name": "wv_triangle_5mm",
  "description": "Triangle weave 5mm",
  "values": {
    "weave_type": 1,
    "weave_on": true,
    "weave_width": 5.0,
    "weave_speed": 4.0,
    "weave_pattern": [0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  }
}
```

**Output:**
```rapid
LOCAL PERS weavedata wv_triangle_5mm:=[1,TRUE,5.0,4.0,[0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0]];
```

### Example 3: TASK PERS for Global Data

**Goal:** Use TASK PERS scope for data shared across modules.

**Technology Script:**
```python
# Set Global level attribute
program.SetBoolAttribute('GLOBAL_DATA', True)
```

**Output:**
```rapid
TASK PERS seamdata sd_default:=[1,FALSE,100.0,5.0];
TASK PERS welddata wd_default:=[20.0,150.0,5.0,12.0];
```

**Use Case:** Legacy systems that share data across multiple program modules.

### Example 4: Migrating Existing RAPID Data

**Goal:** Convert existing RAPID declarations to JSON instances.

**Existing RAPID:**
```rapid
TASK PERS welddata wd_steel_thin:=[18.5,120.0,4.2,11.0];
TASK PERS welddata wd_steel_thick:=[22.0,180.0,6.8,14.5];
TASK PERS welddata wd_aluminum:=[17.0,95.0,3.5,10.0];
```

**Create Instances:**
```json
{
  "instances": [
    {
      "name": "wd_steel_thin",
      "description": "Steel thin 1-3mm",
      "values": {"voltage": 18.5, "current": 120.0, "wire_speed": 4.2, "gas_flow": 11.0}
    },
    {
      "name": "wd_steel_thick",
      "description": "Steel thick 5mm+",
      "values": {"voltage": 22.0, "current": 180.0, "wire_speed": 6.8, "gas_flow": 14.5}
    },
    {
      "name": "wd_aluminum",
      "description": "Aluminum general",
      "values": {"voltage": 17.0, "current": 95.0, "wire_speed": 3.5, "gas_flow": 10.0}
    }
  ]
}
```

**Verify Schema Matches:**
```json
{
  "fields": [
    {"name": "voltage", "output_index": 0},
    {"name": "current", "output_index": 1},
    {"name": "wire_speed", "output_index": 2},
    {"name": "gas_flow", "output_index": 3}
  ]
}
```

---

## Summary

**Key Takeaways:**

1. **One Controller, One Folder:** Each ABB controller has its own data folder
2. **Schema + Instances:** Schema defines structure, instances contain values
3. **No Deletion:** Add new instances, mark old ones as deprecated
4. **Operation Attributes:** Technology sets attributes, downloader reads them
5. **Only Used Data:** Declarations only for data actually used in program
6. **Scope Control:** GLOBAL_DATA attribute controls LOCAL vs TASK PERS
7. **Optional Parameters:** Weave/Track automatically appended when set

**Best Practices:**

- ✅ Use descriptive instance names (sd_linear_50, wd_thick55)
- ✅ Add descriptions for all instances (helps users choose)
- ✅ Keep schemas synchronized across related controllers
- ✅ Version control JSON files (git)
- ✅ Test after modifications (download sample program)
- ✅ Document custom configurations in controller folder README

**Resources:**

- Full specification: `docs/ABB/spec/abb_data_management.md`
- Change log: `docs/ABB/current.md`
- Default templates: `TechTabs/Data/Default/`

---

**Document Version:** 1.0  
**Date:** January 28, 2026  
**Author:** System Documentation  
**Status:** Complete
