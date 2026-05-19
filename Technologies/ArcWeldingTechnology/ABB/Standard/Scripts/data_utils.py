# -------------------------------------------------------------------------------------------
# Name: data_utils.py
# Description: Utility functions for ABB data management system
# Author: CENIT
# Date: 2026-01-27
# -------------------------------------------------------------------------------------------

import os
import json
from pathlib import Path
from datetime import datetime

# -------------------------------------------------------------------------------------------
# Path Resolution
# -------------------------------------------------------------------------------------------

def _find_tech_folder():
    """
    Find the technology folder by searching filesystem.
    
    Returns:
        str: Path to Standard folder, or None if not found
    """
    import sys
    
    # Try sys.path first
    for path in sys.path:
        if os.path.isdir(path):
            # Check if this looks like the Scripts folder
            test_file = os.path.join(path, 'data_utils.py')
            if os.path.exists(test_file):
                # Go up one level to Standard
                return os.path.dirname(path)
            # Check if this is inside Technologies folder structure
            if 'Technologies' in path and 'Scripts' in path:
                return os.path.dirname(path)
    
    # Search from current working directory
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        if 'data_utils.py' in files and 'ArcWeldingTechnology.py' in files:
            # Found Scripts folder, go up to Standard
            return os.path.dirname(root)
        # Limit search depth
        if root.count(os.sep) - cwd.count(os.sep) > 5:
            break
    
    return None


def get_technology_data_path(controllerName):
    """
    Get technology data path for a specific controller.
    
    Args:
        controllerName: Controller name (e.g., "ABB_IRC5_Station1")
    
    Returns:
        str: Path to controller-specific data folder
    """
    standardPath = _find_tech_folder()
    if not standardPath:
        return None
    dataPath = os.path.join(standardPath, "TechTabs", "Data", controllerName)
    return dataPath


def get_default_data_path():
    """
    Get default template data path.
    
    Returns:
        str: Path to default templates folder
    """
    standardPath = _find_tech_folder()
    if not standardPath:
        return None
    dataPath = os.path.join(standardPath, "TechTabs", "Data", "Default")
    return dataPath


def get_data_path(controllerName, dataType):
    """
    Resolve path to data files for a controller.
    
    Search order:
    1. Controller-specific: TechTabs/Data/<ControllerName>/
    2. Default: TechTabs/Data/Default/
    
    Args:
        controllerName: Controller name
        dataType: "seamdata", "welddata", "weavedata", or "trackdata"
    
    Returns:
        str: Path to data folder, or None if not found
    """
    searchPaths = [
        get_technology_data_path(controllerName),
        get_default_data_path()
    ]
    
    for basePath in searchPaths:
        instanceFile = os.path.join(basePath, f"{dataType}_instances.json")
        if os.path.exists(instanceFile):
            return basePath
    
    return None


def ensure_controller_data_folder(controllerName):
    """
    Ensure controller-specific data folder exists.
    
    Args:
        controllerName: Controller name
    
    Returns:
        str: Path to controller data folder
    """
    dataPath = get_technology_data_path(controllerName)
    os.makedirs(dataPath, exist_ok=True)
    return dataPath


# -------------------------------------------------------------------------------------------
# JSON File Operations
# -------------------------------------------------------------------------------------------

def load_json(filePath):
    """
    Load JSON file with error handling.
    
    Args:
        filePath: Path to JSON file
    
    Returns:
        dict: Loaded JSON data, or None if error
    """
    try:
        if not os.path.exists(filePath):
            return None
        
        with open(filePath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filePath}: {str(e)}")
        return None


def save_json(filePath, data):
    """
    Save JSON file with formatting and error handling.
    
    Args:
        filePath: Path to JSON file
        data: Data to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        
        # Update last_modified timestamp if present
        if isinstance(data, dict) and "last_modified" in data:
            data["last_modified"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Write with formatting
        with open(filePath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving JSON to {filePath}: {str(e)}")
        return False


# -------------------------------------------------------------------------------------------
# Schema Operations
# -------------------------------------------------------------------------------------------

def load_schema(controllerName, dataType):
    """
    Load schema for a data type.
    
    Args:
        controllerName: Controller name
        dataType: Data type ("seamdata", "welddata", etc.)
    
    Returns:
        dict: Schema data, or None if not found
    """
    # Try controller-specific folder first
    dataPath = get_data_path(controllerName, dataType)
    if dataPath:
        schemaFile = os.path.join(dataPath, f"{dataType}_schema.json")
        schema = load_json(schemaFile)
        if schema:
            return schema
    
    # Fall back to Default folder
    defaultPath = get_default_data_path()
    if defaultPath:
        schemaFile = os.path.join(defaultPath, f"{dataType}_schema.json")
        return load_json(schemaFile)
    
    return None


def get_schema_fields(schema):
    """
    Get list of fields from schema.
    
    Args:
        schema: Schema dict
    
    Returns:
        list: List of field dicts
    """
    if not schema or "fields" not in schema:
        return []
    return schema.get("fields", [])


def get_named_fields(schema):
    """
    Get list of named (visible) fields from schema.
    
    Args:
        schema: Schema dict
    
    Returns:
        list: List of field dicts with non-empty names
    """
    fields = get_schema_fields(schema)
    return [f for f in fields if f.get("name", "").strip() != ""]


def get_field_by_name(schema, fieldName):
    """
    Get field definition by name.
    
    Args:
        schema: Schema dict
        fieldName: Field name
    
    Returns:
        dict: Field definition, or None if not found
    """
    for field in get_schema_fields(schema):
        if field.get("name") == fieldName:
            return field
    return None


# -------------------------------------------------------------------------------------------
# Instance Operations
# -------------------------------------------------------------------------------------------

def load_instances(controllerName, dataType):
    """
    Load instances for a data type.
    
    Args:
        controllerName: Controller name
        dataType: Data type ("seamdata", "welddata", etc.)
    
    Returns:
        dict: Instances data, or None if not found
    """
    dataPath = get_data_path(controllerName, dataType)
    if not dataPath:
        return None
    
    instanceFile = os.path.join(dataPath, f"{dataType}_instances.json")
    return load_json(instanceFile)


def save_instances(controllerName, dataType, instances):
    """
    Save instances for a data type.
    
    Args:
        controllerName: Controller name
        dataType: Data type
        instances: Instances data dict
    
    Returns:
        bool: True if successful
    """
    # Ensure controller-specific folder exists
    dataPath = ensure_controller_data_folder(controllerName)
    
    # Copy schema from Default if not present in controller folder
    schemaFile = os.path.join(dataPath, f"{dataType}_schema.json")
    if not os.path.exists(schemaFile):
        defaultPath = get_default_data_path()
        if defaultPath:
            defaultSchema = os.path.join(defaultPath, f"{dataType}_schema.json")
            if os.path.exists(defaultSchema):
                import shutil
                try:
                    shutil.copy2(defaultSchema, schemaFile)
                except:
                    pass  # Continue even if schema copy fails
    
    instanceFile = os.path.join(dataPath, f"{dataType}_instances.json")
    return save_json(instanceFile, instances)


def get_instance_by_id(instances, instanceId):
    """
    Get instance by ID.
    
    Args:
        instances: Instances dict
        instanceId: Instance ID (integer)
    
    Returns:
        dict: Instance data, or None if not found
    """
    if not instances or "instances" not in instances:
        return None
    
    for instance in instances.get("instances", []):
        if instance.get("id") == instanceId:
            return instance
    
    return None


def get_instance_by_name(instances, name):
    """
    Get instance by name.
    
    Args:
        instances: Instances dict
        name: Instance name (string)
    
    Returns:
        dict: Instance data, or None if not found
    """
    if not instances or "instances" not in instances:
        return None
    
    for instance in instances.get("instances", []):
        if instance.get("name") == name:
            return instance
    
    return None


def get_default_instance(instances):
    """
    Get default instance.
    
    Args:
        instances: Instances dict
    
    Returns:
        dict: Default instance data, or None if not found
    """
    if not instances:
        return None
    
    defaultId = instances.get("default_id", -1)
    if defaultId >= 0:
        return get_instance_by_id(instances, defaultId)
    
    # Fallback to first instance
    instanceList = instances.get("instances", [])
    if instanceList:
        return instanceList[0]
    
    return None


def create_new_instance(instances, schema, name, description=""):
    """
    Create new instance with default values.
    
    Args:
        instances: Instances dict
        schema: Schema dict
        name: Instance name
        description: Instance description
    
    Returns:
        dict: New instance data
    """
    # Get next ID
    nextId = instances.get("next_id", 0)
    
    # Build default values from schema
    values = {}
    for field in get_schema_fields(schema):
        fieldName = field.get("name")
        if fieldName:
            default = field.get("default")
            
            # Handle array fields
            if field.get("type") == "Array":
                if isinstance(default, list):
                    values[fieldName] = default.copy()
                else:
                    arraySize = field.get("array_size", 0)
                    arrayType = field.get("array_type", "Integer")
                    if arrayType == "Double":
                        values[fieldName] = [0.0] * arraySize
                    elif arrayType == "Bool":
                        values[fieldName] = [False] * arraySize
                    else:
                        values[fieldName] = [0] * arraySize
            else:
                values[fieldName] = default
    
    # Create instance
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    newInstance = {
        "id": nextId,
        "name": name,
        "description": description,
        "created": now,
        "modified": now,
        "values": values
    }
    
    return newInstance


def add_instance(instances, newInstance):
    """
    Add new instance to instances dict.
    
    Args:
        instances: Instances dict
        newInstance: New instance data
    
    Returns:
        dict: Updated instances dict
    """
    if "instances" not in instances:
        instances["instances"] = []
    
    instances["instances"].append(newInstance)
    instances["next_id"] = newInstance["id"] + 1
    
    return instances


def update_instance(instances, instanceId, updatedData):
    """
    Update existing instance.
    
    Args:
        instances: Instances dict
        instanceId: Instance ID to update
        updatedData: Updated instance data (partial or full)
    
    Returns:
        bool: True if updated successfully
    """
    for i, instance in enumerate(instances.get("instances", [])):
        if instance.get("id") == instanceId:
            # Update modified timestamp
            updatedData["modified"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            
            # Merge updates
            instance.update(updatedData)
            instances["instances"][i] = instance
            return True
    
    return False


# -------------------------------------------------------------------------------------------
# Name Validation
# -------------------------------------------------------------------------------------------

def is_name_unique(instances, name, excludeId=None):
    """
    Check if instance name is unique.
    
    Args:
        instances: Instances dict
        name: Name to check
        excludeId: Instance ID to exclude from check (for editing)
    
    Returns:
        bool: True if name is unique
    """
    for instance in instances.get("instances", []):
        if instance.get("name") == name:
            if excludeId is None or instance.get("id") != excludeId:
                return False
    return True


def generate_unique_name(instances, baseName):
    """
    Generate unique instance name by appending number.
    
    Args:
        instances: Instances dict
        baseName: Base name (e.g., "wv_new")
    
    Returns:
        str: Unique name (e.g., "wv_new_1")
    """
    if is_name_unique(instances, baseName):
        return baseName
    
    counter = 1
    while True:
        name = f"{baseName}_{counter}"
        if is_name_unique(instances, name):
            return name
        counter += 1


# -------------------------------------------------------------------------------------------
# RAPID Output Formatting
# -------------------------------------------------------------------------------------------

def format_rapid_value(field, value):
    """
    Format value for RAPID output based on field type.
    
    Args:
        field: Field definition dict
        value: Value to format
    
    Returns:
        str: Formatted value for RAPID
    """
    fieldType = field.get("type")
    
    if fieldType == "Bool":
        return "TRUE" if value else "FALSE"
    
    elif fieldType == "Integer":
        return str(int(value))
    
    elif fieldType == "Double":
        # Format with 1 decimal place by default
        decimals = field.get("decimals", 1)
        return f"{float(value):.{decimals}f}"
    
    elif fieldType == "Array":
        # Format array elements
        arrayType = field.get("array_type", "Integer")
        if not isinstance(value, list):
            return str(value)
        
        formattedValues = []
        for v in value:
            if arrayType == "Bool":
                formattedValues.append("TRUE" if v else "FALSE")
            elif arrayType == "Double":
                decimals = field.get("decimals", 1)
                formattedValues.append(f"{float(v):.{decimals}f}")
            else:
                formattedValues.append(str(int(v)))
        
        return "[" + ",".join(formattedValues) + "]"
    
    elif fieldType == "String":
        # Wrap in RAPID double-quotes
        s = str(value) if value else ""
        return f'"{s}"'
    
    else:
        return str(value)


def format_rapid_declaration(schema, instance):
    """
    Format RAPID declaration from schema and instance.
    
    Args:
        schema: Schema dict
        instance: Instance dict
    
    Returns:
        str: RAPID declaration line
    
    Example:
        "TASK PERS weavedata wv_5mm:=[1,0,4.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0];"
    """
    rapidType = schema.get("rapid_type", "data")
    name = instance.get("name", "unnamed")
    
    # Build value array in output_index order
    fields = sorted(get_schema_fields(schema), key=lambda f: f.get("output_index", 0))
    values = []
    
    for field in fields:
        fieldName = field.get("name", "")
        
        # Get value (use default if not in instance)
        if fieldName and fieldName in instance.get("values", {}):
            value = instance["values"][fieldName]
        else:
            value = field.get("default")
        
        # Format value
        formattedValue = format_rapid_value(field, value)
        values.append(formattedValue)
    
    # Build declaration using template
    template = schema.get("rapid_template", "TASK PERS {rapid_type} {name}:=[{values}];")
    valuesStr = ",".join(values)
    
    return template.format(
        rapid_type=rapidType,
        name=name,
        values=valuesStr
    )


# -------------------------------------------------------------------------------------------
# Controller Name Extraction
# -------------------------------------------------------------------------------------------

def get_controller_name(Operator):
    """
    Get controller name from operator.
    
    Args:
        Operator: CENPyOlp operator with GetController() method
    
    Returns:
        str: Controller name, or "Default" if unavailable
    """
    try:
        controller = Operator.GetController()
        if controller:
            return controller.GetName()
    except:
        pass
    
    return "Default"
