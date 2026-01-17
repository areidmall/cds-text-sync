# -*- coding: utf-8 -*-
"""
Project_export.py - Export CODESYS project to git-friendly folder structure

Exports all textual objects (POUs, GVLs, DUTs) to .st files organized in
folders matching the CODESYS project hierarchy. Creates a single _metadata.json
file containing GUID mappings for reliable import.

Usage: Run from CODESYS IDE after setting BASE_DIR with Project_directory.py
"""
import os
import codecs
import json
import time

# Object type GUIDs for reference
TYPE_GUIDS = {
    "pou": "6f9dac99-8de1-4efc-8465-68ac443b7d08",           # PROGRAM, FUNCTION, FUNCTION_BLOCK
    "gvl": "ffbfa93a-b94d-45fc-a329-229860183b1d",           # Global Variable List
    "dut": "2db5746d-d284-4425-9f7f-2663a34b0ebc",           # Data Types (STRUCT, ENUM, etc.)
    "action": "8ac092e5-3128-4e26-9e7e-11016c6684f2",        # Action
    "method": "f8a58466-d7f6-439f-bbb8-d4600e41d099",        # Method
    "property": "5a3b8626-d3e9-4f37-98b5-66420063d91e",      # Property
    "property_accessor": "792f2eb6-721e-4e64-ba20-bc98351056db", # Property Get/Set
    "folder": "738bea1e-99bb-4f04-90bb-a7a567e74e3a",        # Folder
    "device": "225bfe47-7336-4dbc-9419-4105a7c831fa",        # Device
    "plc_logic": "40b404f9-e5dc-42c6-907f-c89f4a517386",     # Plc Logic
    "application": "639b491f-5557-464c-af91-1471bac9f549",   # Application
    "library_manager": "adb5cb65-8e1d-4a00-b70a-375ea27582f3", # Library Manager
    "task_config": "ae1de277-a207-4a28-9efb-456c06bd52f3",   # Task Configuration
    "task": "98a2708a-9b18-4f31-82ed-a1465b24fa2d",          # Task
}

# Types that contain exportable ST code
EXPORTABLE_TYPES = [
    TYPE_GUIDS["pou"],
    TYPE_GUIDS["gvl"],
    TYPE_GUIDS["dut"],
    TYPE_GUIDS["action"],
    TYPE_GUIDS["method"],
    TYPE_GUIDS["property"],
    TYPE_GUIDS["property_accessor"],
]

def clean_filename(name):
    """Clean filename from invalid characters"""
    forbidden = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
    clean_name = name
    for char in forbidden:
        clean_name = clean_name.replace(char, "_")
    return clean_name


def safe_str(value):
    """Safely convert value to string"""
    try:
        return str(value)
    except:
        return "N/A"


def get_object_path(obj, stop_at_application=True):
    """
    Build the path from object to Application root.
    Returns list of folder names from Application (exclusive) to object (exclusive).
    """
    path_parts = []
    current = obj
    
    while current is not None:
        try:
            if not hasattr(current, "parent") or current.parent is None:
                break
            
            parent = current.parent
            parent_type = safe_str(parent.type)
            
            # Stop at Application level
            if stop_at_application and parent_type == TYPE_GUIDS["application"]:
                break
            
            # Stop at Plc Logic or Device level
            if parent_type in [TYPE_GUIDS["plc_logic"], TYPE_GUIDS["device"]]:
                break
            
            # Add parent name to path if it's a folder or other container
            parent_name = clean_filename(parent.get_name())
            path_parts.insert(0, parent_name)
            current = parent
            
        except Exception as e:
            print("Error building path: " + safe_str(e))
            break
    
    return path_parts


def get_parent_pou_name(obj):
    """Get parent POU name for nested objects (actions, methods, properties)"""
    try:
        if hasattr(obj, "parent") and obj.parent:
            parent_type = safe_str(obj.parent.type)
            if parent_type == TYPE_GUIDS["pou"]:
                return obj.parent.get_name()
    except:
        pass
    return None


def export_object_content(obj):
    """
    Extract declaration and implementation text from object.
    Returns tuple (declaration, implementation) or (None, None) if no content.
    """
    declaration = None
    implementation = None
    
    try:
        if hasattr(obj, "has_textual_declaration") and obj.has_textual_declaration:
            declaration = obj.textual_declaration.text
    except Exception as e:
        print("Warning: Could not read declaration for " + safe_str(obj.get_name()) + ": " + safe_str(e))
    
    try:
        if hasattr(obj, "has_textual_implementation") and obj.has_textual_implementation:
            implementation = obj.textual_implementation.text
    except Exception as e:
        print("Warning: Could not read implementation for " + safe_str(obj.get_name()) + ": " + safe_str(e))
    
    return declaration, implementation


def format_st_content(declaration, implementation, obj_type_guid):
    """
    Format ST file content with clean structure.
    Uses markers for import script to parse sections.
    """
    content = []
    
    if declaration:
        content.append(declaration)
    
    if implementation:
        if content:
            content.append("")  # Empty line separator
        content.append("// === IMPLEMENTATION ===")
        content.append(implementation)
    
    return "\n".join(content)


def export_project(export_dir):
    """Export all project objects to folder structure with metadata"""
    
    if not projects.primary:
        system.ui.error("No project open!")
        return
    
    # Create export directory
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    print("=== Starting Project Export ===")
    start_time = time.time()
    print("Export directory: " + export_dir)
    
    # Metadata structure
    current_project_name = safe_str(projects.primary)
    metadata = {
        "project_name": current_project_name,
        "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "autosync": "STOPPED",
        "sync_timeout": 10000,
        "objects": {}
    }
    
    try:
        if hasattr(projects.primary, "path"):
            metadata["project_path"] = safe_str(projects.primary.path)
    except:
        pass
    
    # Check if metadata already exists with different project
    metadata_path = os.path.join(export_dir, "_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with codecs.open(metadata_path, "r", "utf-8") as f:
                existing_metadata = json.load(f)
            
            existing_project = existing_metadata.get("project_name", "")
            if existing_project and existing_project != current_project_name:
                message = "WARNING: This directory contains exports from a different project!\n\n"
                message += "Current project: " + current_project_name + "\n"
                message += "Existing exports: " + existing_project + "\n\n"
                message += "Exporting will OVERWRITE the existing files.\n\n"
                message += "Are you sure you want to proceed?"
                
                result = system.ui.choose(message, ("Yes, Overwrite", "No, Cancel"))
                
                if result[0] != 0:
                    print("Export cancelled by user - project mismatch")
                    return
        except:
            # If we can't read existing metadata, continue with export
            pass
    
    # Get all objects recursively
    all_objects = projects.primary.get_children(recursive=True)
    print("Found " + str(len(all_objects)) + " total objects")
    
    exported_count = 0
    skipped_count = 0
    
    for obj in all_objects:
        try:
            obj_type = safe_str(obj.type)
            obj_name = obj.get_name()
            obj_guid = safe_str(obj.guid)
            
            # Skip non-exportable types
            if obj_type not in EXPORTABLE_TYPES:
                continue
            
            # Check if object has any textual content
            has_content = False
            try:
                if hasattr(obj, "has_textual_declaration") and obj.has_textual_declaration:
                    has_content = True
                if hasattr(obj, "has_textual_implementation") and obj.has_textual_implementation:
                    has_content = True
            except:
                pass
            
            if not has_content:
                skipped_count += 1
                continue
            
            # Build file path
            path_parts = get_object_path(obj)
            clean_name = clean_filename(obj_name)
            
            # Handle nested objects (actions, methods, properties)
            parent_pou = get_parent_pou_name(obj)
            if parent_pou and obj_type in [TYPE_GUIDS["action"], TYPE_GUIDS["method"], 
                                           TYPE_GUIDS["property"], TYPE_GUIDS["property_accessor"]]:
                # Nested objects: ParentPOU.MethodName.st
                file_name = clean_filename(parent_pou) + "." + clean_name + ".st"
                # Remove parent POU from path since it's in filename
                if path_parts and path_parts[-1] == parent_pou:
                    path_parts = path_parts[:-1]
            else:
                file_name = clean_name + ".st"
            
            # Create target directory
            target_dir = os.path.join(export_dir, *path_parts) if path_parts else export_dir
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Get content
            declaration, implementation = export_object_content(obj)
            content = format_st_content(declaration, implementation, obj_type)
            
            if not content.strip():
                skipped_count += 1
                continue
            
            # Write ST file
            file_path = os.path.join(target_dir, file_name)
            with codecs.open(file_path, "w", "utf-8") as f:
                f.write(content)
            
            # Build relative path for metadata
            if path_parts:
                parts_for_join = path_parts + [file_name]
                rel_path = os.path.join(*parts_for_join)
            else:
                rel_path = file_name
            rel_path = rel_path.replace("\\", "/")  # Normalize path separators
            
            # Store metadata
            metadata["objects"][rel_path] = {
                "guid": obj_guid,
                "type": obj_type,
                "name": obj_name,
                "parent": safe_str(obj.parent.get_name()) if hasattr(obj, "parent") and obj.parent else None
            }
            
            print("Exported: " + rel_path)
            exported_count += 1
            
        except Exception as e:
            print("Error exporting " + safe_str(obj) + ": " + safe_str(e))
    
    # Write metadata file with consistent field order
    metadata_path = os.path.join(export_dir, "_metadata.json")
    try:
        # Reconstruct with desired field order
        ordered_metadata = {}
        
        # Configuration fields first
        if "project_name" in metadata:
            ordered_metadata["project_name"] = metadata["project_name"]
        if "project_path" in metadata:
            ordered_metadata["project_path"] = metadata["project_path"]
        if "export_timestamp" in metadata:
            ordered_metadata["export_timestamp"] = metadata["export_timestamp"]
        if "autosync" in metadata:
            ordered_metadata["autosync"] = metadata["autosync"]
        if "sync_timeout" in metadata:
            ordered_metadata["sync_timeout"] = metadata["sync_timeout"]
        
        # Objects last
        if "objects" in metadata:
            ordered_metadata["objects"] = metadata["objects"]
        
        with codecs.open(metadata_path, "w", "utf-8") as f:
            json.dump(ordered_metadata, f, indent=2, ensure_ascii=False)
        print("Created: _metadata.json")
    except Exception as e:
        print("Error writing metadata: " + safe_str(e))
    
    print("=== Export Complete ===")
    elapsed_time = time.time() - start_time
    print("Exported: " + str(exported_count) + " files")
    print("Skipped: " + str(skipped_count) + " objects (no textual content)")
    print("Time elapsed: {:.2f} seconds".format(elapsed_time))
    print("Completed at: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    system.ui.info("Export complete!\n\nExported: " + str(exported_count) + " files\nLocation: " + export_dir + "\nTime elapsed: {:.2f} seconds".format(elapsed_time))


def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BASE_DIR")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_dir = f.read().strip()
    else:
        system.ui.warning("Base directory is not set! Please run 'Project_directory.py' first.")
        return
    
    export_project(base_dir)


if __name__ == "__main__":
    main()