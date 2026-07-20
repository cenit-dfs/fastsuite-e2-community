# -------------------------------------------------------------------------------------------
# Name: UploadUtils
# Description: Uploader utility functions
# Debugg info: E2@localhost:5254
# Author: C. Berauer
# Changelog:
#     Version: 1.0
#        Changed by: 
#        Date: 
# -------------------------------------------------------------------------------------------

import tkinter as tk
from tkinter import simpledialog

# A Multi-Line editor to read and write text from a string attribute. Line separator is "|""
def edit_text_lines(initial_text, separator="|"):
   root = tk.Tk()
   root.title("Multi-Line Text Editor")
   root.overrideredirect(True)  # Hide default title bar

   # Keep the window always on top
   root.wm_attributes("-topmost", 1)

   # Background color
   bg_color = "#2F2F2F"
   title_bar_color = "#ACC334"
   text_bg_color = "#2F2F2F"

# Set window at current mouse pointer position
   x = root.winfo_pointerx()
   y = root.winfo_pointery()
   root.geometry(f"+{x}+{y}")

   # Window dragging variables
   def start_drag(event):
      root.x_offset = event.x
      root.y_offset = event.y

   def on_drag(event):
      x = root.winfo_pointerx() - root.x_offset
      y = root.winfo_pointery() - root.y_offset
      root.geometry(f"+{x}+{y}")

   # Create custom title bar
   title_bar = tk.Frame(root, bg=title_bar_color, relief="flat", bd=2)
   title_bar.pack(side="top", fill="x")
   title_bar.bind("<Button-1>", start_drag)  # Left mouse button pressed
   title_bar.bind("<B1-Motion>", on_drag)  # Mouse moves while button held

   # Title label
   title_label = tk.Label(title_bar, text="Edit Text Lines", bg=title_bar_color, fg="#696969", font=("Arial", 12))
   title_label.pack(side="left", padx=10)
   title_label.bind("<Button-1>", start_drag)
   title_label.bind("<B1-Motion>", on_drag)

   # Add close button
   close_button = tk.Button(
      title_bar,
      text="X",
      bg="#ACC334",
      fg="#696969",
      bd=0,
      font=("Arial", 12),
      command=root.destroy
   )
   close_button.pack(side="right", padx=5, pady=2)

   # Main text area
   text_widget = tk.Text(
      root,
      wrap="none",
      bg=text_bg_color,
      fg="white",
      font=("Arial", 10),
      padx=5, pady=5,
      insertbackground="white",  # Set cursor color to white
      highlightbackground="#ACC334",  # Border color
      highlightthickness=1,        # Border thickness
      bd=0                         # Remove the internal border
   )
   text_widget.pack(expand=True, fill="both", padx=0, pady=0)

   # Insert initial text
   initial_lines = initial_text.split(separator)
   for line in initial_lines:
      text_widget.insert("end", line + "\n")

   result = [None]

   # Buttons frame
   button_frame = tk.Frame(
      root,
      bg=bg_color,
      relief="flat",
      highlightbackground="#ACC334",  # Border color
      highlightthickness=1,           # Border thickness
      bd=0                            # Remove the internal border
   )
   button_frame.pack(side="bottom", fill="x")

   def on_save():
      edited_content = text_widget.get("1.0", "end").strip()
      edited_lines = edited_content.split("\n")
      result[0] = separator.join(edited_lines)
      root.destroy()

   # Cancel action
   def on_cancel(event=None):  # Accept event argument for shortcut
      result[0] = None
      root.destroy()

   save_button = tk.Button(
      button_frame,
      relief="flat",
      text="Save",
      bg="#ACC334",
      fg="#696969",
      font=("Arial", 12),
      command=on_save
   )
   save_button.pack(side="right", padx=5, pady=5)

   cancel_button = tk.Button(
      button_frame,
      relief="flat",
      text="Cancel",
      bg="#ACC334",
      fg="#696969",
      font=("Arial", 12),
      command=root.destroy
   )
   cancel_button.pack(side="right", padx=5, pady=5)

   # Bind keyboard shortcuts
   root.bind("<Escape>", on_cancel)  # Esc to cancel

   root.configure(bg=bg_color)
   root.mainloop()
   return result[0]
