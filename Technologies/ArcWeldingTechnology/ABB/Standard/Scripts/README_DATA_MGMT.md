# ABB Data Management System - Implementation Summary

**Date:** 2026-01-27  
**Status:** ✅ Complete (Phases 1-5)

## Overview

Complete implementation of a schema-based data management system for ABB welding parameters (seamdata, welddata, weavedata, trackdata). Solves the problem of varying data structures across different power sources and robot integrators.

## Architecture

### Storage Structure
```
Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/Data/
├── Default/                          # Shared templates
│   ├── seamdata_schema.json
│   ├── seamdata_instances.json
│   ├── welddata_schema.json
│   ├── welddata_instances.json
│   ├── weavedata_schema.json
│   ├── weavedata_instances.json
│   ├── trackdata_schema.json
│   └── trackdata_instances.json
└── <ControllerName>/                 # Controller-specific overrides
    ├── seamdata_schema.json
    ├── seamdata_instances.json
    └── ...
```

### Path Resolution
1. Check `TechTabs/Data/<ControllerName>/`
2. Fallback to `TechTabs/Data/Default/`

## Implementation Phases

### ✅ Phase 0: Specification (Completed 2026-01-27)
- **File:** [docs/ABB/spec/abb_data_management.md](../../docs/ABB/spec/abb_data_management.md)
- **Features:**
  - JSON schema/instance format
  - `output_index` field to decouple UI from RAPID order
  - Array type with grid UI and column headers
  - Boolean attribute triggers (no pushbuttons)
  - Output control flags

### ✅ Phase 1: Core Infrastructure (Completed 2026-01-27)
- **Files:**
  - `data_utils.py` (556 lines)
  - `data_validator.py` (415 lines)

- **data_utils.py Functions:**
  - `get_data_path()` - Resolve controller-specific or default folder
  - `load_schema()` / `load_instances()` - JSON loading with error handling
  - `save_instances()` - JSON saving with auto-timestamp
  - `get_instance_by_id()` / `get_instance_by_name()` - Query helpers
  - `get_default_instance()` - Retrieve default_id instance
  - `create_new_instance()` - Generate instance with schema defaults
  - `add_instance()` / `update_instance()` - Modify collections
  - `is_name_unique()` / `generate_unique_name()` - Name validation
  - `format_rapid_declaration()` - Generate RAPID output
  - `get_controller_name()` - Extract controller from operator

- **data_validator.py Functions:**
  - `validate_schema()` - Check schema structure
  - `validate_instances()` - Validate instances against schema
  - `validate_field_value()` - Type and range checking
  - `validate_name()` - RAPID identifier rules
  - `convert_value_to_type()` - Type coercion for UI input

### ✅ Phase 2: Data Picker UI (Completed 2026-01-27)
- **File:** `data_picker.py` (389 lines)
- **Entry Point:** `launch_data_picker(Operator, dataType)`
- **Features:**
  - Resizable window (900x600, min 700x500)
  - Filter/search with live filtering
  - Sortable table (ID, Name, Description, Modified)
  - Preview pane with grid display for arrays
  - Select button updates `*_DATA_NAME` and `*_DATA_INDEX`
  - Cancel/Close resets `SELECT_*` boolean

### ✅ Phase 3: Data Editor UI (Completed 2026-01-27)
- **File:** `data_editor.py` (582 lines)
- **Entry Point:** `launch_data_editor(Operator, dataType)`
- **Features:**
  - Resizable window (900x700, min 700x600)
  - Two-section layout (instance list + edit form)
  - New Entry button with unique name generation
  - Field widgets by type:
    - Integer/Double: Entry with range display
    - Bool: Checkbox
    - Array: Grid with column headers
    - String: Text entry
  - Validation (type, range, uniqueness)
  - Dirty state tracking with save prompts
  - No delete functionality (preserves referential integrity)
  - Save writes to controller-specific folder
  - Cancel/Close resets `EDIT_*` boolean

### ✅ Phase 4: Technology Integration (Completed 2026-01-27)
- **File:** [ArcWeldingTechnology.py](../Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/ArcWeldingTechnology.py)
- **Changes:**
  - **PostTechInitAttributes:** Added 22 attributes (lines ~130-165)
    - Per data type: `*_DATA_NAME`, `*_DATA_INDEX`, `SELECT_*`, `EDIT_*`
    - Global controls: `USE_WEAVING`, `USE_TRACKING`, `GLOBAL_DATA`, `OUTPUT_DATA_MODULE`, `DATA_MODULE_NAME`
  - **PostTechOnAttribChanged:** Boolean trigger detection (lines ~376-408)
    - Detects `SELECT_*` / `EDIT_*` triggers
    - Dynamic import of `data_picker.py` / `data_editor.py`
    - Launches app with error handling
    - Auto-resets boolean to False

### ✅ Phase 5: Downloader Integration (Completed 2026-01-27)
- **File:** [ABB_IRC5.py](../OLPTranslators/ABB/ABB_IRC5.py)
- **Changes:**
  - Import `data_utils` with graceful fallback
  - Added state variables in `__init__`:
    - `_data_schemas`, `_data_instances`, `_data_used_indices`
    - Control flags from program attributes
  - **LoadDataManagement()** - Called in ProgramStart
    - Loads schemas and instances
    - Reads control flags from attributes
    - Initializes usage tracking
  - **CollectUsedDataIndices()** - Called in ProgramEnd
    - Scans operations for `*_DATA_INDEX` attributes
    - Collects set of used instance IDs
  - **FormatDataDeclaration()** - Helper
    - Formats RAPID from schema + instance
  - **OutputDataDeclarations()** - Called in ProgramEnd
    - Generates RAPID declarations
    - Respects `GLOBAL_DATA` flag (TASK PERS vs LOCAL PERS)
    - Only outputs used instances

### ✅ Phase 6: Example Templates (Completed 2026-01-27)
- **Files:** 8 JSON files in `TechTabs/Data/Default/`
- **Content:**
  - seamdata: seam_type, weld_on, seam_length, seam_width
  - welddata: voltage, current, wire_feed, gas_flow
  - weavedata: weave_type, enabled, amplitude, frequency, parameters[8]
  - trackdata: enabled, sensor_type, search_distance, gain
- **Features:**
  - Demonstrates all field types (Integer, Double, Bool, Array)
  - Range validation examples
  - Array with column headers (weavedata)
  - 2-3 instances per data type
  - Default instance (id=0)

## User Workflow

### 1. Configure Data (One-Time Setup)
1. Open E2 project
2. Select Global attributes
3. Set boolean `EDIT_SEAMDATA = True`
4. Data editor opens automatically
5. Create/modify data instances
6. Save and close

### 2. Assign Data to Operations
1. Select operation
2. Set boolean `SELECT_SEAMDATA = True`
3. Data picker opens automatically
4. Select desired instance
5. Close picker (updates `SEAMDATA_DATA_NAME` and `SEAMDATA_DATA_INDEX`)

### 3. Download Program
1. Run ABB_IRC5 downloader
2. Downloader:
   - Loads schemas and instances
   - Scans operations for used data indices
   - Generates RAPID declarations for used data only
   - Outputs to .MOD file

### 4. Customize Per Controller (Optional)
1. Copy Default/ templates to `Data/<ControllerName>/`
2. Edit JSON files for controller-specific schemas
3. Downloader automatically uses controller-specific data

## Output Control Flags

### Global Attributes (set at GLOBAL level)
- **USE_WEAVING** (Bool): Include weavedata in output
- **USE_TRACKING** (Bool): Include trackdata in output
- **GLOBAL_DATA** (Bool): Use TASK PERS instead of LOCAL PERS
- **OUTPUT_DATA_MODULE** (Bool): Generate separate global module (not yet implemented)
- **DATA_MODULE_NAME** (String): Global module name (default: ABB_Data)

### RAPID Output Examples

**Local declarations (GLOBAL_DATA = False):**
```rapid
! SEAMDATA declarations
LOCAL PERS seamdata sd_linear_100:=[1,1,100.0,5.0];
LOCAL PERS seamdata sd_circular:=[2,1,150.0,6.0];

! WELDDATA declarations  
LOCAL PERS welddata wd_thin:=[18.0,100.0,3.5,10.0];
```

**Global declarations (GLOBAL_DATA = True):**
```rapid
! SEAMDATA declarations
TASK PERS seamdata sd_linear_100:=[1,1,100.0,5.0];
TASK PERS seamdata sd_circular:=[2,1,150.0,6.0];

! WELDDATA declarations
TASK PERS welddata wd_thin:=[18.0,100.0,3.5,10.0];
```

## Graceful Degradation

- If `data_utils` not available, downloader continues without data output
- If attributes missing, uses defaults
- If JSON files missing, logs warning
- All errors logged, never crash

## Maintenance

### Adding New Field to Schema
1. Edit `*_schema.json`
2. Add field with `output_index`, `type`, `default`
3. All existing instances use default value automatically

### Changing Field Order in RAPID
1. Edit `output_index` values in schema
2. No code changes needed
3. Next download uses new order

### Supporting New Power Source
1. Copy Default/ templates to `Data/<PowerSourceName>/`
2. Edit schemas to match power source RAPID format
3. Modify `rapid_template` if needed
4. Update field definitions

## Testing Checklist

- [ ] Data picker displays instances correctly
- [ ] Data editor creates new instances
- [ ] Data editor validates field types and ranges
- [ ] Data editor prevents duplicate names
- [ ] Boolean triggers launch UIs
- [ ] Boolean triggers reset after UI closes
- [ ] Downloader loads schemas and instances
- [ ] Downloader collects used indices
- [ ] Downloader outputs only used data
- [ ] GLOBAL_DATA flag changes scope correctly
- [ ] USE_WEAVING/USE_TRACKING flags work
- [ ] Array fields display as grids
- [ ] Controller-specific override works
- [ ] Default fallback works

## Future Enhancements

### Phase 7: RAPID Parser (Migration Tool)
- Parse existing RAPID files
- Generate schemas from declarations
- Extract instances from PERS statements
- Bulk import utility

### Phase 8: Separate Global Module
- Implement `OUTPUT_DATA_MODULE` flag
- Generate separate `<DATA_MODULE_NAME>.MOD` file
- Reference from main program

### Phase 9: Export/Import
- Export JSON files as plugin package
- Import JSON files from other projects
- Share templates across teams

## File Inventory

### Core Infrastructure
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/data_utils.py` (556 lines)
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/data_validator.py` (415 lines)

### UI Applications
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/data_picker.py` (389 lines)
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/data_editor.py` (582 lines)

### Technology Integration
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/ArcWeldingTechnology.py` (538 lines, +30 lines modified)

### Downloader Integration
- `OLPTranslators/ABB/ABB_IRC5.py` (2691 lines, +180 lines modified)

### Templates
- `Technologies/ArcWeldingTechnology/ABB/Standard/TechTabs/Data/Default/*.json` (8 files, 357 lines)

### Documentation
- `docs/ABB/spec/abb_data_management.md` (920 lines)
- `docs/ABB/current.md` (updated with data mgmt feature)
- `Technologies/ArcWeldingTechnology/ABB/Standard/Scripts/README_DATA_MGMT.md` (this file)

## Total Implementation

- **Lines of Code:** ~2,500 (excluding comments/blank lines)
- **Files Created:** 16
- **Files Modified:** 4
- **Git Commits:** 7
- **Development Time:** Single session (2026-01-27)

## Dependencies

- **E2 API:** CENPyOlp (for operator, program, operation access)
- **Python Standard Library:** json, os, pathlib, datetime, tkinter
- **External:** None (fully self-contained)

## Contact / Support

For questions or issues with the ABB data management system, refer to:
- Specification: [docs/ABB/spec/abb_data_management.md](../../docs/ABB/spec/abb_data_management.md)
- Change log: [docs/ABB/current.md](../../docs/ABB/current.md)
- Code comments in implementation files
