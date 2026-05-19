# -------------------------------------------------------------------------------------------
# Name: data_editor.py
# Description: Data editor UI for ABB data management system
# Author: CENIT
# Date: 2026-01-27
# -------------------------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
import data_utils
import data_validator

# -------------------------------------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------------------------------------

def launch_data_editor(Operator, dataType, attribName=None):
    """
    Launch data editor UI for creating/modifying data entries.
    
    Args:
        Operator: CENPyOlp operator
        dataType: "seamdata", "welddata", "weavedata", or "trackdata"
        attribName: Attribute name for window tracking (optional)
    
    Returns:
        tk.Tk: Window reference for tracking, or None if failed
    """
    try:
        # Get controller name
        controllerName = data_utils.get_controller_name(Operator)
        
        # Load schema and instances
        schema = data_utils.load_schema(controllerName, dataType)
        instances = data_utils.load_instances(controllerName, dataType)
        
        if not schema:
            messagebox.showerror("Error", f"Could not load schema for {dataType}")
            return None
        
        if not instances:
            messagebox.showerror("Error", f"Could not load instances for {dataType}")
            return None
        
        # Create and run editor UI
        editor = DataEditorUI(Operator, controllerName, dataType, schema, instances, attribName)
        editor.run()
        return editor.root
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch data editor: {str(e)}")
        return None


# -------------------------------------------------------------------------------------------
# Data Editor UI
# -------------------------------------------------------------------------------------------

class DataEditorUI:
    def __init__(self, Operator, controllerName, dataType, schema, instances, attribName=None):
        """
        Initialize data editor UI.
        
        Args:
            Operator: CENPyOlp operator
            controllerName: Controller name
            dataType: Data type string
            schema: Schema dict
            instances: Instances dict
            attribName: Attribute name for cleanup (optional)
        """
        self.Operator = Operator
        self.controllerName = controllerName
        self.dataType = dataType
        self.schema = schema
        self.instances = instances
        self.attribName = attribName
        self.selectedId = None
        self.fieldWidgets = {}
        self.isDirty = False
        
        # Create blocking overlay (fullscreen transparent window to block E2 interaction)
        self.overlay = tk.Tk()
        self.overlay.attributes("-alpha", 0.01)  # Nearly invisible
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.configure(bg='black')
        self.overlay.overrideredirect(True)
        # Block all events on overlay
        self.overlay.bind("<Button>", lambda e: "break")
        self.overlay.bind("<Key>", lambda e: "break")
        
        # Create main window
        self.root = tk.Toplevel(self.overlay)  # Make child of overlay
        self.root.overrideredirect(True)  # Remove default title bar
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Configure color scheme
        self.root.configure(bg='#2F2F2F')
        
        # Window title for custom title bar
        self.windowTitle = f"Edit {dataType.upper()}"
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#2F2F2F', foreground='#ffffff', fieldbackground='#3e3e42')
        style.configure('TFrame', background='#2F2F2F')
        style.configure('TLabel', background='#2F2F2F', foreground='#ffffff')
        style.configure('TLabelframe', background='#2F2F2F', foreground='#ffffff', borderwidth=2)
        style.configure('TLabelframe.Label', background='#2F2F2F', foreground='#ACC334')
        style.configure('TButton', background='#ACC334', foreground='#000000')
        style.configure('TEntry', fieldbackground='#3e3e42', foreground='#ffffff', insertcolor='#ffffff', borderwidth=1)
        style.configure('TCheckbutton', background='#2F2F2F', foreground='#ffffff')
        style.configure('Vertical.TScrollbar', background='#4B4B4B', troughcolor='#2F2F2F', borderwidth=0, arrowcolor='#ffffff')
        style.map('TButton', background=[('active', '#252525')])
        style.map('TEntry', fieldbackground=[('focus', '#3e3e42')])
        style.map('Vertical.TScrollbar', background=[('active', '#252525')])
        
        # Configure grid weights
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Create custom title bar
        self._create_title_bar()
        
        # Create UI components
        self._create_instance_list_frame()
        self._create_edit_form_frame()
        self._create_button_frame()
        
        # Populate instance list
        self._populate_instance_list()
        
        # Bind selection event
        self.instanceList.bind("<<ListboxSelect>>", self._on_instance_selected)
        
        # Bind ESC key to close
        self.root.bind("<Escape>", lambda e: self._on_close())
        
        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_title_bar(self):
        """Create custom title bar."""
        titleBar = tk.Frame(self.root, bg='#ACC334', height=30, relief='flat')
        titleBar.grid(row=0, column=0, sticky="ew")
        titleBar.grid_propagate(False)
        
        # Title label
        titleLabel = tk.Label(titleBar, text=self.windowTitle, bg='#ACC334', fg='#2F2F2F', 
                             font=('Segoe UI', 9, 'bold'), anchor='w')
        titleLabel.pack(side='left', padx=10, fill='both', expand=True)
        
        # Close button
        closeBtn = tk.Label(titleBar, text='✕', bg='#ACC334', fg='#2F2F2F', 
                           font=('Segoe UI', 12), cursor='hand2', width=3)
        closeBtn.pack(side='right')
        closeBtn.bind('<Button-1>', lambda e: self._on_close())
        closeBtn.bind('<Enter>', lambda e: closeBtn.config(bg='#8BA324'))
        closeBtn.bind('<Leave>', lambda e: closeBtn.config(bg='#ACC334'))
        
        # Enable window dragging
        titleBar.bind('<Button-1>', self._start_move)
        titleBar.bind('<B1-Motion>', self._on_move)
        titleLabel.bind('<Button-1>', self._start_move)
        titleLabel.bind('<B1-Motion>', self._on_move)
    
    def _start_move(self, event):
        """Start window move."""
        self.root._drag_start_x = event.x
        self.root._drag_start_y = event.y
    
    def _on_move(self, event):
        """Handle window move."""
        x = self.root.winfo_x() + event.x - self.root._drag_start_x
        y = self.root.winfo_y() + event.y - self.root._drag_start_y
        self.root.geometry(f"+{x}+{y}")
    
    def _create_instance_list_frame(self):
        """Create instance list frame (top section)."""
        frame = ttk.LabelFrame(self.root, text="Instances", padding="5")
        frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)
        
        # Create listbox with scrollbar
        listFrame = ttk.Frame(frame)
        listFrame.grid(row=0, column=0, sticky="ew")
        listFrame.columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(listFrame, orient="vertical")
        self.instanceList = tk.Listbox(listFrame, height=6, yscrollcommand=scrollbar.set,
                                       bg='#2F2F2F', fg='#ffffff', selectbackground='#094771',
                                       selectforeground='#ffffff', borderwidth=1, relief='solid',
                                       highlightthickness=0)
        scrollbar.configure(command=self.instanceList.yview)
        
        self.instanceList.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # New button
        ttk.Button(frame, text="New Entry", command=self._on_new_entry).grid(row=1, column=0, sticky="w", pady=5)
    
    def _create_edit_form_frame(self):
        """Create edit form frame (bottom section)."""
        frame = ttk.LabelFrame(self.root, text="Edit Entry", padding="5")
        frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        
        # Create canvas with scrollbar for form
        canvas = tk.Canvas(frame, bg='#2F2F2F', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        self.formFrame = ttk.Frame(canvas)
        self.formFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.formFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.formCanvas = canvas
        
        # Initial message
        ttk.Label(self.formFrame, text="Select an instance or create a new entry", foreground="gray").pack(pady=20)
    
    def _create_button_frame(self):
        """Create button frame."""
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(frame, text="Save", command=self._on_save).pack(side="right", padx=5)
        ttk.Button(frame, text="Cancel", command=self._on_close).pack(side="right", padx=5)
    
    def _populate_instance_list(self):
        """Populate instance list."""
        self.instanceList.delete(0, tk.END)
        
        instanceList = self.instances.get("instances", [])
        for instance in instanceList:
            instanceId = instance.get("id", -1)
            name = instance.get("name", "")
            description = instance.get("description", "")
            
            displayText = f"[{instanceId}] {name}"
            if description:
                displayText += f" - {description}"
            
            self.instanceList.insert(tk.END, displayText)
    
    def _on_instance_selected(self, event):
        """Handle instance selection."""
        if self.isDirty:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                 "You have unsaved changes. Do you want to save them?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                if not self._save_current():
                    return
        
        selection = self.instanceList.curselection()
        if not selection:
            self._clear_form()
            return
        
        # Get selected instance
        index = selection[0]
        instanceList = self.instances.get("instances", [])
        if index < len(instanceList):
            instance = instanceList[index]
            self.selectedId = instance.get("id")
            self._load_form(instance)
    
    def _on_new_entry(self):
        """Handle New Entry button."""
        if self.isDirty:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                 "You have unsaved changes. Do you want to save them?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                if not self._save_current():
                    return
        
        # Clear selection
        self.instanceList.selection_clear(0, tk.END)
        self.selectedId = None
        
        # Generate unique name
        baseName = f"{self.dataType[:2]}_new"
        uniqueName = data_utils.generate_unique_name(self.instances, baseName)
        
        # Create new instance
        newInstance = data_utils.create_new_instance(self.instances, self.schema, uniqueName, "")
        
        # Load form
        self._load_form(newInstance)
        self.isDirty = True
    
    def _clear_form(self):
        """Clear edit form."""
        for widget in self.formFrame.winfo_children():
            widget.destroy()
        
        self.fieldWidgets.clear()
        self.selectedId = None
        self.isDirty = False
        
        ttk.Label(self.formFrame, text="Select an instance or create a new entry", foreground="gray").pack(pady=20)
    
    def _load_form(self, instance):
        """
        Load form with instance data.
        
        Args:
            instance: Instance dict
        """
        # Clear existing widgets
        for widget in self.formFrame.winfo_children():
            widget.destroy()
        
        self.fieldWidgets.clear()
        
        # Get values
        values = instance.get("values", {})
        
        # Get named fields (sorted by output_index for consistent ordering)
        namedFields = sorted(data_utils.get_named_fields(self.schema), 
                           key=lambda f: f.get("output_index", 0))
        
        if not namedFields:
            ttk.Label(self.formFrame, text="No editable fields", foreground="gray").pack(pady=20)
            return
        
        # Create form fields
        row = 0
        
        # ID field (read-only)
        ttk.Label(self.formFrame, text="ID:", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="e", padx=5, pady=5)
        idLabel = ttk.Label(self.formFrame, text=str(instance.get("id", "new")), relief="sunken", width=10)
        idLabel.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Name field (required)
        ttk.Label(self.formFrame, text="Name: *", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="e", padx=5, pady=5)
        nameVar = tk.StringVar(value=instance.get("name", ""))
        nameVar.trace("w", lambda *args: self._on_field_changed())
        nameEntry = ttk.Entry(self.formFrame, textvariable=nameVar, width=40)
        nameEntry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.fieldWidgets["__name__"] = nameVar
        row += 1
        
        # Description field
        ttk.Label(self.formFrame, text="Description:", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="e", padx=5, pady=5)
        descVar = tk.StringVar(value=instance.get("description", ""))
        descVar.trace("w", lambda *args: self._on_field_changed())
        descEntry = ttk.Entry(self.formFrame, textvariable=descVar, width=40)
        descEntry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.fieldWidgets["__description__"] = descVar
        row += 1
        
        # Separator
        ttk.Separator(self.formFrame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Data fields
        for field in namedFields:
            fieldName = field.get("name")
            fieldType = field.get("type")
            value = values.get(fieldName, field.get("default"))
            
            # Field label
            labelText = f"{fieldName}:"
            if field.get("required", False):
                labelText += " *"
            
            label = ttk.Label(self.formFrame, text=labelText, font=("TkDefaultFont", 9, "bold"))
            label.grid(row=row, column=0, sticky="ne", padx=5, pady=5)
            
            # Field widget
            if fieldType == "Array":
                widget = self._create_array_widget(field, value, row)
            elif fieldType == "Bool":
                widget = self._create_bool_widget(field, value, row)
            elif fieldType == "Integer":
                widget = self._create_integer_widget(field, value, row)
            elif fieldType == "Double":
                widget = self._create_double_widget(field, value, row)
            else:
                widget = self._create_string_widget(field, value, row)
            
            self.fieldWidgets[fieldName] = widget
            row += 1
        
        # Configure column weights
        self.formFrame.columnconfigure(1, weight=1)
        
        self.isDirty = False
    
    def _create_array_widget(self, field, value, row):
        """Create array widget with grid display."""
        arrayFrame = ttk.Frame(self.formFrame)
        arrayFrame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        arraySize = field.get("array_size", 0)
        arrayType = field.get("array_type", "Integer")
        columnHeaders = field.get("column_headers", [])
        
        if not isinstance(value, list):
            value = [0] * arraySize
        
        widgets = []
        for i in range(arraySize):
            # Column header (if available)
            if i < len(columnHeaders):
                header = ttk.Label(arrayFrame, text=columnHeaders[i], font=("TkDefaultFont", 8))
                header.grid(row=0, column=i, padx=2)
            
            # Entry widget
            var = tk.StringVar(value=str(value[i]) if i < len(value) else "0")
            var.trace("w", lambda *args: self._on_field_changed())
            
            entry = ttk.Entry(arrayFrame, textvariable=var, width=8)
            entry.grid(row=1, column=i, padx=2)
            
            widgets.append((var, arrayType))
        
        return widgets
    
    def _create_bool_widget(self, field, value, row):
        """Create boolean widget (checkbox)."""
        var = tk.BooleanVar(value=bool(value))
        var.trace("w", lambda *args: self._on_field_changed())
        
        checkbox = ttk.Checkbutton(self.formFrame, variable=var)
        checkbox.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        return var
    
    def _create_integer_widget(self, field, value, row):
        """Create integer widget with validation."""
        frame = ttk.Frame(self.formFrame)
        frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        var = tk.StringVar(value=str(value))
        var.trace("w", lambda *args: self._on_field_changed())
        
        entry = ttk.Entry(frame, textvariable=var, width=20)
        entry.grid(row=0, column=0, padx=(0, 10))
        
        # Show range if specified
        minVal = field.get("min")
        maxVal = field.get("max")
        if minVal is not None or maxVal is not None:
            rangeText = f"Range: "
            if minVal is not None:
                rangeText += f"{minVal}"
            else:
                rangeText += "−∞"
            rangeText += " to "
            if maxVal is not None:
                rangeText += f"{maxVal}"
            else:
                rangeText += "∞"
            
            ttk.Label(frame, text=rangeText, foreground="gray", font=("TkDefaultFont", 8)).grid(
                row=0, column=1)
        
        return var
    
    def _create_double_widget(self, field, value, row):
        """Create double widget with validation."""
        frame = ttk.Frame(self.formFrame)
        frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        var = tk.StringVar(value=str(value))
        var.trace("w", lambda *args: self._on_field_changed())
        
        entry = ttk.Entry(frame, textvariable=var, width=20)
        entry.grid(row=0, column=0, padx=(0, 10))
        
        # Show range if specified
        minVal = field.get("min")
        maxVal = field.get("max")
        if minVal is not None or maxVal is not None:
            rangeText = f"Range: "
            if minVal is not None:
                rangeText += f"{minVal}"
            else:
                rangeText += "−∞"
            rangeText += " to "
            if maxVal is not None:
                rangeText += f"{maxVal}"
            else:
                rangeText += "∞"
            
            ttk.Label(frame, text=rangeText, foreground="gray", font=("TkDefaultFont", 8)).grid(
                row=0, column=1)
        
        return var
    
    def _create_string_widget(self, field, value, row):
        """Create string widget."""
        var = tk.StringVar(value=str(value))
        var.trace("w", lambda *args: self._on_field_changed())
        
        entry = ttk.Entry(self.formFrame, textvariable=var, width=40)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        return var
    
    def _on_field_changed(self):
        """Handle field change."""
        self.isDirty = True
    
    def _on_save(self):
        """Handle Save button."""
        if not self._save_current():
            return
        
        messagebox.showinfo("Success", "Data saved successfully")
    
    def _save_current(self):
        """
        Save current form data.
        
        Returns:
            bool: True if saved successfully
        """
        if not self.fieldWidgets:
            return True
        
        # Get form values
        try:
            name = self.fieldWidgets["__name__"].get().strip()
            description = self.fieldWidgets["__description__"].get().strip()
        except:
            messagebox.showerror("Error", "Failed to get name/description")
            return False
        
        # Validate name
        valid, error = data_validator.validate_name(name)
        if not valid:
            messagebox.showerror("Validation Error", f"Invalid name: {error}")
            return False
        
        # Check name uniqueness
        valid, error = data_validator.validate_unique_name(self.instances, name, self.selectedId)
        if not valid:
            messagebox.showerror("Validation Error", error)
            return False
        
        # Get field values
        values = {}
        namedFields = data_utils.get_named_fields(self.schema)
        
        for field in namedFields:
            fieldName = field.get("name")
            fieldType = field.get("type")
            
            if fieldName not in self.fieldWidgets:
                continue
            
            widget = self.fieldWidgets[fieldName]
            
            # Extract value based on widget type
            if fieldType == "Array":
                arrayValues = []
                arrayType = field.get("array_type", "Integer")
                for var, vType in widget:
                    rawValue = var.get()
                    converted = data_validator.convert_value_to_type(rawValue, vType)
                    if converted is None:
                        messagebox.showerror("Validation Error", 
                                           f"Invalid value for {fieldName}: {rawValue}")
                        return False
                    arrayValues.append(converted)
                values[fieldName] = arrayValues
            
            elif fieldType == "Bool":
                values[fieldName] = widget.get()
            
            else:
                rawValue = widget.get()
                converted = data_validator.convert_value_to_type(rawValue, fieldType)
                if converted is None:
                    messagebox.showerror("Validation Error", 
                                       f"Invalid value for {fieldName}: {rawValue}")
                    return False
                values[fieldName] = converted
            
            # Validate value
            valid, error = data_validator.validate_field_value(field, values[fieldName])
            if not valid:
                messagebox.showerror("Validation Error", f"{fieldName}: {error}")
                return False
        
        # Create or update instance
        if self.selectedId is None:
            # New instance
            newInstance = data_utils.create_new_instance(self.instances, self.schema, name, description)
            newInstance["values"] = values
            data_utils.add_instance(self.instances, newInstance)
            self.selectedId = newInstance["id"]
        else:
            # Update existing
            updatedData = {
                "name": name,
                "description": description,
                "values": values
            }
            data_utils.update_instance(self.instances, self.selectedId, updatedData)
        
        # Save to file
        if not data_utils.save_instances(self.controllerName, self.dataType, self.instances):
            messagebox.showerror("Error", "Failed to save data to file")
            return False
        
        # Refresh list
        self._populate_instance_list()
        
        self.isDirty = False
        return True
    
    def _on_close(self):
        """Handle window close."""
        if self.isDirty:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                                 "You have unsaved changes. Do you want to save them?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                if not self._save_current():
                    return
        
        # Reset EDIT boolean to False
        _EDIT_MAP = {
            'machineprocess': 'EDIT_MACHPROCESS',
            'machiningpose':  'EDIT_MACHPOSE',
        }
        attrName = _EDIT_MAP.get(self.dataType, f"EDIT_{self.dataType.upper()}DATA")
        try:
            attribSetter = self.Operator.GetAttribSetter()
            attribSetter.SetBool(attrName, False)
        except:
            pass
        
        # Close windows (this will exit mainloop)
        try:
            self.root.destroy()
        except:
            pass
        try:
            self.overlay.quit()  # Exit mainloop
        except:
            pass
    
    def run(self):
        """Run the editor UI."""
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Keep dialog window on top
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.grab_set()
        
        # Run main loop (overlay blocks all E2 interaction)
        try:
            self.overlay.mainloop()
        finally:
            # Cleanup
            try:
                self.root.grab_release()
            except:
                pass
            try:
                self.overlay.destroy()
            except:
                pass
