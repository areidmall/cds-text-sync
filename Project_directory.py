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
        
        # Check _metadata.json for project path mismatch
        try:
            metadata_path = os.path.join(selected_path, "_metadata.json")
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                
                json_path = data.get('project_path', '')
                
                # Safe way to get current project path
                current_path = ""
                try:
                    if "projects" in globals() and projects.primary:
                        current_path = projects.primary.path
                except:
                    pass
                
                if current_path and json_path and json_path != current_path:
                    message = "Metadata Mismatch Detected!\n\n"
                    message += "The selected directory contains exports from a different project:\n"
                    message += "Metadata Path: " + json_path + "\n"
                    message += "Current Project: " + current_path + "\n\n"
                    message += "Do you want to update the metadata to match the current project?"
                    
                    # Offer to update
                    res = system.ui.choose(message, ("Yes, Update Metadata", "No, Keep As Is"))
                    
                    if res and res[0] == 0:
                        data['project_path'] = current_path
                        try:
                            data['project_name'] = str(projects.primary)
                        except:
                            pass
                            
                        with open(metadata_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        print("Updated _metadata.json project path to current project.")
                        system.ui.info("Metadata updated successfully.")
                        
        except Exception as e:
            print("Warning: Failed to check metadata: " + str(e))

    else:
        print("Operation cancelled by user.")

if __name__ == "__main__":
    set_base_directory()
