# -*- coding: utf-8 -*-
import os

def set_base_directory():
    # CODESYS provides the 'system' object for UI interactions
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to read current value for better UX
    config_path = os.path.join(current_script_dir, "BASE_DIR")
    initial_dir = ""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            initial_dir = f.read().strip()

    # Open the dialog
    selected_path = system.ui.browse_directory_dialog("Select Sync Directory", initial_dir)
    
    if selected_path:
        # Save the path to the text file
        with open(config_path, "w") as f:
            f.write(selected_path)
        print("Success: Base directory updated to: " + selected_path)
    else:
        print("Operation cancelled by user.")

if __name__ == "__main__":
    set_base_directory()
