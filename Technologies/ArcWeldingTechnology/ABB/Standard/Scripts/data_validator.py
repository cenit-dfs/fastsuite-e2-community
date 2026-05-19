# -------------------------------------------------------------------------------------------
# Name: data_validator.py
# Description: Validation functions for ABB data management system
# Author: CENIT
# Date: 2026-01-27
# -------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# Schema Validation
# -------------------------------------------------------------------------------------------

def validate_schema(schema):
    """
    Validate schema structure.
    
    Args:
        schema: Schema dict
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    if not schema:
        return (False, "Schema is None or empty")
    
    if not isinstance(schema, dict):
        return (False, "Schema must be a dictionary")
    
    # Check required top-level fields
    required = ["version", "data_type", "rapid_type", "fields"]
    for field in required:
        if field not in schema:
            return (False, f"Missing required field: {field}")
    
    # Validate fields array
    fields = schema.get("fields", [])
    if not isinstance(fields, list):
        return (False, "fields must be a list")
    
    if len(fields) == 0:
        return (False, "Schema must have at least one field")
    
    # Validate each field
    for i, field in enumerate(fields):
        valid, error = validate_field_definition(field, i)
        if not valid:
            return (False, f"Field {i}: {error}")
    
    return (True, "")


def validate_field_definition(field, index):
    """
    Validate field definition.
    
    Args:
        field: Field dict
        index: Field index (for error messages)
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    if not isinstance(field, dict):
        return (False, "Field must be a dictionary")
    
    # Check required field properties
    required = ["type", "output_index", "default"]
    for prop in required:
        if prop not in field:
            return (False, f"Missing required property: {prop}")
    
    # Validate type
    fieldType = field.get("type")
    validTypes = ["Integer", "Double", "Bool", "String", "Array"]
    if fieldType not in validTypes:
        return (False, f"Invalid type: {fieldType}. Must be one of {validTypes}")
    
    # Validate array-specific properties
    if fieldType == "Array":
        if "array_type" not in field:
            return (False, "Array field must have array_type")
        if "array_size" not in field:
            return (False, "Array field must have array_size")
        
        arrayType = field.get("array_type")
        if arrayType not in ["Integer", "Double", "Bool"]:
            return (False, f"Invalid array_type: {arrayType}")
    
    # Validate output_index
    outputIndex = field.get("output_index")
    if not isinstance(outputIndex, int) or outputIndex < 0:
        return (False, f"output_index must be non-negative integer, got: {outputIndex}")
    
    return (True, "")


# -------------------------------------------------------------------------------------------
# Instance Validation
# -------------------------------------------------------------------------------------------

def validate_instances(instances, schema):
    """
    Validate instances structure against schema.
    
    Args:
        instances: Instances dict
        schema: Schema dict
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    if not instances:
        return (False, "Instances is None or empty")
    
    if not isinstance(instances, dict):
        return (False, "Instances must be a dictionary")
    
    # Check required top-level fields
    required = ["version", "data_type", "instances", "next_id"]
    for field in required:
        if field not in instances:
            return (False, f"Missing required field: {field}")
    
    # Validate instances array
    instanceList = instances.get("instances", [])
    if not isinstance(instanceList, list):
        return (False, "instances must be a list")
    
    # Validate each instance
    for i, instance in enumerate(instanceList):
        valid, error = validate_instance(instance, schema, i)
        if not valid:
            return (False, f"Instance {i}: {error}")
    
    # Validate next_id
    nextId = instances.get("next_id")
    if not isinstance(nextId, int) or nextId < 0:
        return (False, f"next_id must be non-negative integer, got: {nextId}")
    
    return (True, "")


def validate_instance(instance, schema, index):
    """
    Validate single instance against schema.
    
    Args:
        instance: Instance dict
        schema: Schema dict
        index: Instance index (for error messages)
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    if not isinstance(instance, dict):
        return (False, "Instance must be a dictionary")
    
    # Check required instance properties
    required = ["id", "name", "values"]
    for prop in required:
        if prop not in instance:
            return (False, f"Missing required property: {prop}")
    
    # Validate ID
    instanceId = instance.get("id")
    if not isinstance(instanceId, int) or instanceId < 0:
        return (False, f"id must be non-negative integer, got: {instanceId}")
    
    # Validate name
    name = instance.get("name")
    if not isinstance(name, str) or name.strip() == "":
        return (False, f"name must be non-empty string, got: {name}")
    
    # Validate values against schema
    values = instance.get("values", {})
    if not isinstance(values, dict):
        return (False, "values must be a dictionary")
    
    # Check all named fields have values
    from data_utils import get_named_fields
    namedFields = get_named_fields(schema)
    
    for field in namedFields:
        fieldName = field.get("name")
        if fieldName not in values:
            return (False, f"Missing value for field: {fieldName}")
        
        # Validate value type and range
        valid, error = validate_field_value(field, values[fieldName])
        if not valid:
            return (False, f"Field '{fieldName}': {error}")
    
    return (True, "")


def validate_field_value(field, value):
    """
    Validate field value against field definition.
    
    Args:
        field: Field definition dict
        value: Value to validate
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    fieldType = field.get("type")
    fieldName = field.get("name", "unknown")
    
    # Type validation
    if fieldType == "Integer":
        if not isinstance(value, int):
            try:
                value = int(value)
            except:
                return (False, f"Must be integer, got: {type(value).__name__}")
        
        # Range validation
        if "min" in field and value < field["min"]:
            return (False, f"Value {value} below minimum {field['min']}")
        if "max" in field and value > field["max"]:
            return (False, f"Value {value} above maximum {field['max']}")
    
    elif fieldType == "Double":
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except:
                return (False, f"Must be numeric, got: {type(value).__name__}")
        
        # Range validation
        if "min" in field and value < field["min"]:
            return (False, f"Value {value} below minimum {field['min']}")
        if "max" in field and value > field["max"]:
            return (False, f"Value {value} above maximum {field['max']}")
    
    elif fieldType == "Bool":
        if not isinstance(value, bool):
            return (False, f"Must be boolean, got: {type(value).__name__}")
    
    elif fieldType == "String":
        if not isinstance(value, str):
            return (False, f"Must be string, got: {type(value).__name__}")
    
    elif fieldType == "Array":
        if not isinstance(value, list):
            return (False, f"Must be array/list, got: {type(value).__name__}")
        
        # Validate array size
        arraySize = field.get("array_size", 0)
        if len(value) != arraySize:
            return (False, f"Array size must be {arraySize}, got {len(value)}")
        
        # Validate array element types
        arrayType = field.get("array_type", "Integer")
        for i, elem in enumerate(value):
            if arrayType == "Integer":
                if not isinstance(elem, int):
                    try:
                        elem = int(elem)
                    except:
                        return (False, f"Array element {i} must be integer")
            elif arrayType == "Double":
                if not isinstance(elem, (int, float)):
                    try:
                        elem = float(elem)
                    except:
                        return (False, f"Array element {i} must be numeric")
            elif arrayType == "Bool":
                if not isinstance(elem, bool):
                    return (False, f"Array element {i} must be boolean")
    
    return (True, "")


# -------------------------------------------------------------------------------------------
# Value Conversion
# -------------------------------------------------------------------------------------------

def convert_value_to_type(value, fieldType, arrayType=None):
    """
    Convert value to appropriate type.
    
    Args:
        value: Value to convert (can be string from UI)
        fieldType: Field type ("Integer", "Double", "Bool", "String", "Array")
        arrayType: Array element type (if fieldType is "Array")
    
    Returns:
        Converted value, or None if conversion fails
    """
    try:
        if fieldType == "Integer":
            return int(float(value))  # Handle "5.0" -> 5
        
        elif fieldType == "Double":
            return float(value)
        
        elif fieldType == "Bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ["true", "1", "yes"]
            return bool(value)
        
        elif fieldType == "String":
            return str(value)
        
        elif fieldType == "Array":
            if not isinstance(value, list):
                return None
            
            converted = []
            for v in value:
                if arrayType == "Integer":
                    converted.append(int(float(v)))
                elif arrayType == "Double":
                    converted.append(float(v))
                elif arrayType == "Bool":
                    if isinstance(v, bool):
                        converted.append(v)
                    elif isinstance(v, str):
                        converted.append(v.lower() in ["true", "1", "yes"])
                    else:
                        converted.append(bool(v))
                else:
                    converted.append(v)
            return converted
        
        return value
    
    except:
        return None


# -------------------------------------------------------------------------------------------
# Name Validation
# -------------------------------------------------------------------------------------------

def validate_name(name):
    """
    Validate instance name.
    
    Args:
        name: Instance name string
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    if not name or not isinstance(name, str):
        return (False, "Name cannot be empty")
    
    name = name.strip()
    if len(name) == 0:
        return (False, "Name cannot be empty")
    
    if len(name) > 100:
        return (False, "Name too long (max 100 characters)")
    
    # Check for valid characters (RAPID identifier rules)
    # Allow letters, numbers, underscore
    if not all(c.isalnum() or c == '_' for c in name):
        return (False, "Name can only contain letters, numbers, and underscore")
    
    # Must start with letter or underscore
    if not (name[0].isalpha() or name[0] == '_'):
        return (False, "Name must start with letter or underscore")
    
    return (True, "")


def validate_unique_name(instances, name, excludeId=None):
    """
    Validate that name is unique.
    
    Args:
        instances: Instances dict
        name: Name to validate
        excludeId: Instance ID to exclude (when editing existing)
    
    Returns:
        tuple: (bool: is_valid, str: error_message)
    """
    from data_utils import is_name_unique
    
    if not is_name_unique(instances, name, excludeId):
        return (False, f"Name '{name}' already exists")
    
    return (True, "")
