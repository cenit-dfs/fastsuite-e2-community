# -------------------------------------------------------------------------------------------
# Name: data_picker.py
# Description: Data picker UI for ABB data management system
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

def launch_data_picker(Operator, dataType, attribName=None):
    """
    Launch data picker UI for selecting existing data entries.
    
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
            messagebox.showwarning("Warning", f"No instances found for {dataType}\\n\\nPlease use the editor to create data first.")
            return None
        
        # Create and run picker UI
        picker = DataPickerUI(Operator, dataType, schema, instances, attribName)
        picker.run()
        return picker.root
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch data picker: {str(e)}")
        return None


# -------------------------------------------------------------------------------------------
# Data Picker UI
# -------------------------------------------------------------------------------------------

class DataPickerUI:
    def __init__(self, Operator, dataType, schema, instances, attribName=None):
        """
        Initialize data picker UI.
        
        Args:
            Operator: CENPyOlp operator
            dataType: Data type string
            schema: Schema dict
            instances: Instances dict
            attribName: Attribute name for cleanup (optional)
        """
        self.Operator = Operator
        self.dataType = dataType
        self.schema = schema
        self.instances = instances
        self.attribName = attribName
        self.selectedId = None
        
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
        self.root.geometry("900x600")
        self.root.minsize(700, 500)
        
        # Configure color scheme
        self.root.configure(bg='#2F2F2F')
        
        # Window title for custom title bar
        self.windowTitle = f"Select {dataType.upper()}"
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#2F2F2F', foreground='#ffffff', fieldbackground='#3e3e42')
        style.configure('TFrame', background='#2F2F2F')
        style.configure('TLabel', background='#2F2F2F', foreground='#ffffff')
        style.configure('TLabelframe', background='#2F2F2F', foreground='#ffffff', borderwidth=2)
        style.configure('TLabelframe.Label', background='#2F2F2F', foreground='#ACC334')
        style.configure('TButton', background='#ACC334', foreground='#000000')
        style.configure('TEntry', fieldbackground='#3e3e42', foreground='#ffffff')
        style.configure('Treeview', background='#2F2F2F', foreground='#ffffff', fieldbackground='#2F2F2F')
        style.configure('Treeview.Heading', background='#ACC334', foreground='#000000')
        style.map('Treeview', background=[('selected', '#094771')])
        style.configure('Vertical.TScrollbar', background='#4B4B4B', troughcolor='#2F2F2F', borderwidth=0, arrowcolor='#ffffff')
        style.map('Vertical.TScrollbar', background=[('active', '#252525')])
        style.configure('Horizontal.TScrollbar', background='#4B4B4B', troughcolor='#2F2F2F', borderwidth=0, arrowcolor='#ffffff')
        style.map('Horizontal.TScrollbar', background=[('active', '#252525')])
        
        # Configure grid weights for resizing
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Create custom title bar
        self._create_title_bar()
        
        # Create UI components
        self._create_filter_frame()
        self._create_table_frame()
        self._create_preview_frame()
        self._create_button_frame()
        
        # Populate table
        self._populate_table()
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        
        # Bind double-click to select and close
        self.tree.bind("<Double-Button-1>", lambda e: self._on_select())
        
        # Bind ESC key to cancel
        self.root.bind("<Escape>", lambda e: self._on_cancel())
        
        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
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
        closeBtn.bind('<Button-1>', lambda e: self._on_cancel())
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
    
    def _create_filter_frame(self):
        """Create filter/search frame."""
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(row=1, column=0, sticky="ew")
        
        ttk.Label(frame, text="Filter:").pack(side="left", padx=5)
        
        self.filterVar = tk.StringVar()
        self.filterVar.trace("w", lambda *args: self._apply_filter())
        
        filterEntry = ttk.Entry(frame, textvariable=self.filterVar, width=40)
        filterEntry.pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(frame, text="Clear", command=self._clear_filter).pack(side="left", padx=5)
    
    def _create_table_frame(self):
        """Create table frame with scrollbars."""
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        
        # Create treeview
        columns = ("ID", "Name", "Description", "Modified")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.tree.heading("ID", text="ID", command=lambda: self._sort_column("ID"))
        self.tree.heading("Name", text="Name", command=lambda: self._sort_column("Name"))
        self.tree.heading("Description", text="Description", command=lambda: self._sort_column("Description"))
        self.tree.heading("Modified", text="Modified", command=lambda: self._sort_column("Modified"))
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("Description", width=300, anchor="w")
        self.tree.column("Modified", width=150, anchor="center")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
    
    def _create_preview_frame(self):
        """Create preview frame with grid display."""
        frame = ttk.LabelFrame(self.root, text="Preview", padding="5")
        frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)
        
        # Create canvas with scrollbar for preview
        canvas = tk.Canvas(frame, height=150, bg='#2F2F2F', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        self.previewFrame = ttk.Frame(canvas)
        self.previewFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.previewFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.previewCanvas = canvas
        
        # Initial message
        ttk.Label(self.previewFrame, text="Select an entry to preview", foreground="gray").pack(pady=20)
    
    def _create_button_frame(self):
        """Create button frame."""
        frame = ttk.Frame(self.root, padding="5")
        frame.grid(row=4, column=0, sticky="ew")
        
        ttk.Button(frame, text="Select", command=self._on_select).pack(side="right", padx=5)
        ttk.Button(frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=5)
    
    def _populate_table(self):
        """Populate table with instances."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get instances
        instanceList = self.instances.get("instances", [])
        
        # Add instances to tree
        for instance in instanceList:
            instanceId = instance.get("id", -1)
            name = instance.get("name", "")
            description = instance.get("description", "")
            modified = instance.get("modified", "")
            
            # Apply filter
            filterText = self.filterVar.get().lower()
            if filterText:
                if filterText not in name.lower() and filterText not in description.lower():
                    continue
            
            self.tree.insert("", "end", iid=str(instanceId), values=(instanceId, name, description, modified))
        
        # Select first item if none selected
        if not self.tree.selection():
            children = self.tree.get_children()
            if children:
                self.tree.selection_set(children[0])
                self.tree.focus(children[0])
    
    def _apply_filter(self):
        """Apply filter to table."""
        self._populate_table()
    
    def _clear_filter(self):
        """Clear filter."""
        self.filterVar.set("")
    
    def _sort_column(self, column):
        """Sort table by column."""
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children()]
        
        # Determine sort order
        reverse = False
        if hasattr(self, "_last_sort_column") and self._last_sort_column == column:
            reverse = not getattr(self, "_last_sort_reverse", False)
        
        # Sort
        if column == "ID":
            items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)
        
        # Reorder
        for index, (val, item) in enumerate(items):
            self.tree.move(item, "", index)
        
        # Remember sort state
        self._last_sort_column = column
        self._last_sort_reverse = reverse
    
    def _on_selection_changed(self, event):
        """Handle selection change."""
        selection = self.tree.selection()
        if not selection:
            self._clear_preview()
            return
        
        # Get selected instance ID
        item = selection[0]
        instanceId = int(item)
        
        # Get instance
        instance = data_utils.get_instance_by_id(self.instances, instanceId)
        if not instance:
            self._clear_preview()
            return
        
        # Update preview
        self._update_preview(instance)
    
    def _clear_preview(self):
        """Clear preview frame."""
        for widget in self.previewFrame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.previewFrame, text="Select an entry to preview", foreground="gray").pack(pady=20)
    
    def _update_preview(self, instance):
        """Update preview with instance data."""
        # Clear existing widgets
        for widget in self.previewFrame.winfo_children():
            widget.destroy()
        
        # Get named fields
        namedFields = data_utils.get_named_fields(self.schema)
        if not namedFields:
            ttk.Label(self.previewFrame, text="No fields to preview", foreground="gray").pack(pady=20)
            return
        
        # Get values
        values = instance.get("values", {})
        
        # Create grid
        row = 0
        for field in namedFields:
            fieldName = field.get("name")
            fieldType = field.get("type")
            value = values.get(fieldName, field.get("default"))
            
            # Field label
            label = ttk.Label(self.previewFrame, text=f"{fieldName}:", font=("TkDefaultFont", 9, "bold"))
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            
            # Field value
            if fieldType == "Array":
                # Display array as grid
                arrayFrame = ttk.Frame(self.previewFrame)
                arrayFrame.grid(row=row, column=1, sticky="w", padx=5, pady=2)
                
                if isinstance(value, list):
                    # Get column headers
                    columnHeaders = field.get("column_headers", [])
                    
                    # Display array values
                    for i, v in enumerate(value):
                        # Column header (if available)
                        if i < len(columnHeaders):
                            header = ttk.Label(arrayFrame, text=columnHeaders[i], font=("TkDefaultFont", 8))
                            header.grid(row=0, column=i, padx=2)
                        
                        # Value
                        valueLabel = ttk.Label(arrayFrame, text=str(v), relief="sunken", width=8)
                        valueLabel.grid(row=1, column=i, padx=2)
                else:
                    ttk.Label(arrayFrame, text=str(value)).pack()
            else:
                # Display simple value
                valueLabel = ttk.Label(self.previewFrame, text=str(value), relief="sunken", width=30)
                valueLabel.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            
            row += 1
    
    def _on_select(self):
        """Handle Select button."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry")
            return
        
        # Get selected instance
        item = selection[0]
        instanceId = int(item)
        instance = data_utils.get_instance_by_id(self.instances, instanceId)
        
        if not instance:
            messagebox.showerror("Error", "Failed to get selected instance")
            return
        
        # Update operator attributes
        self._update_operator_attributes(instance)
        
        # Close windows (this will exit mainloop)
        try:
            self.root.destroy()
        except:
            pass
        try:
            self.overlay.quit()  # Exit mainloop
        except:
            pass
    
    def _on_cancel(self):
        """Handle Cancel button or window close."""
        # Reset SELECT boolean to False
        _SELECT_MAP = {
            'machineprocess': 'SELECT_MACHPROCESS',
            'machiningpose':  'SELECT_MACHPOSE',
        }
        attrName = _SELECT_MAP.get(self.dataType, f"SELECT_{self.dataType.upper()}DATA")
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
    
    def _update_operator_attributes(self, instance):
        """
        Update operator attributes with selected instance.
        
        Args:
            instance: Selected instance dict
        """
        try:
            # Get attribute setter
            attribSetter = self.Operator.GetAttribSetter()
            
            # Map dataType to attribute name prefix
            # Standard types (seamdata, welddata, etc.) use: PREFIX_DATA_NAME / PREFIX_DATA_INDEX / SELECT_PREFIXdata
            # Machining types use custom attribute names
            _ATTR_MAP = {
                'machineprocess': ('MACH_PROCESS_NAME', 'MACH_PROCESS_INDEX', 'SELECT_MACHPROCESS'),
                'machiningpose':  ('MACH_POSE_NAME',    'MACH_POSE_INDEX',    'SELECT_MACHPOSE'),
            }
            
            if self.dataType in _ATTR_MAP:
                nameAttr, indexAttr, selectAttr = _ATTR_MAP[self.dataType]
            else:
                # Standard convention: seamdata → SEAM, welddata → WELD, etc.
                prefix = self.dataType.replace('data', '').upper()
                nameAttr = f"{prefix}_DATA_NAME"
                indexAttr = f"{prefix}_DATA_INDEX"
                selectAttr = f"SELECT_{prefix}DATA"
            
            # Set attributes
            attribSetter.SetString(nameAttr, instance.get("name", ""))
            attribSetter.SetInteger(indexAttr, instance.get("id", -1))
            
            # Reset SELECT boolean to False
            attribSetter.SetBool(selectAttr, False)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update attributes: {str(e)}")
    
    def run(self):
        """Run the picker UI."""
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
