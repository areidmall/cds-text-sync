# -*- coding: utf-8 -*-
"""
Project_import.py - Import edited ST files back into CODESYS project

Reads _metadata.json to match files to CODESYS objects by GUID, then updates
the textual declaration and implementation from the ST files.

Usage: Run from CODESYS IDE after exporting with Project_export.py and editing files
"""
import os
import codecs
import json
import time
from codesys_constants import IMPL_MARKER, TYPE_GUIDS
from codesys_utils import (
    safe_str, parse_st_file, build_object_cache, 
    find_object_by_guid, find_object_by_name, load_base_dir,
    calculate_hash, save_metadata
)

# Shared constants and utilities imported from modules





def update_object_code(obj, declaration, implementation):
    """
    Update object's textual declaration and/or implementation.
    Returns True if any update was made.
    """
    updated = False
    obj_name = safe_str(obj.get_name())
    
    # Update declaration
    if declaration:
        try:
            if hasattr(obj, "has_textual_declaration") and obj.has_textual_declaration:
                obj.textual_declaration.replace(declaration)
                updated = True
            else:
                print("  Warning: " + obj_name + " has no textual declaration property")
        except Exception as e:
            print("  Error updating declaration for " + obj_name + ": " + safe_str(e))
    
    # Update implementation
    if implementation:
        try:
            if hasattr(obj, "has_textual_implementation") and obj.has_textual_implementation:
                obj.textual_implementation.replace(implementation)
                updated = True
            else:
                # This is normal for GVLs and DUTs - they only have declaration
                pass
        except Exception as e:
            print("  Error updating implementation for " + obj_name + ": " + safe_str(e))
    
    return updated





def determine_object_type(content):
    """Determine CODESYS object type from ST content"""
    content = content.strip()
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("(*") or line.startswith("//") or line.startswith("{"):
            continue
        
        # Check keywords
        parts = line.split()
        if not parts:
            continue
        word = parts[0].upper()
        
        if word == "PROGRAM":
            return TYPE_GUIDS["pou"]
        if word == "FUNCTION_BLOCK":
            return TYPE_GUIDS["pou"]
        if word == "FUNCTION":
            return TYPE_GUIDS["pou"]
        if word == "VAR_GLOBAL":
            return TYPE_GUIDS["gvl"]
        if word == "TYPE":
            return TYPE_GUIDS["dut"]
        if word == "INTERFACE":
            return TYPE_GUIDS["itf"]
        break
    return None


def ensure_folder_path(path_str):
    """
    Ensure folder structure exists in CODESYS project.
    path_str: relative path string e.g. "Folder/SubFolder"
    Returns the parent object (folder) or None if failed.
    """
    if not path_str or path_str == ".":
        return projects.primary
        
    parts = path_str.replace("\\", "/").split("/")
    current_obj = projects.primary
    
    for part in parts:
        if not part: continue
        
        # Try to find child with this name
        found = None
        for child in current_obj.get_children():
            if child.get_name() == part:
                found = child
                break
        
        if found:
            current_obj = found
        else:
            # Create folder
            try:
                print("  Creating folder: " + part)
                current_obj = current_obj.create_child(part, TYPE_GUIDS["folder"])
            except Exception as e:
                print("  Error creating folder " + part + ": " + safe_str(e))
                return None
                
    return current_obj


def import_project(import_dir):
    """Import ST files from folder structure back into CODESYS project"""
    
    if not projects.primary:
        system.ui.error("No project open!")
        return
    
    print("=== Starting Project Import ===")
    start_time = time.time()
    print("Import directory: " + import_dir)
    
    # Load metadata
    metadata_path = os.path.join(import_dir, "_metadata.json")
    if not os.path.exists(metadata_path):
        system.ui.error("_metadata.json not found!\n\nPlease run Project_export.py first to generate the metadata file.")
        return
    
    try:
        with codecs.open(metadata_path, "r", "utf-8") as f:
            metadata = json.load(f)
    except Exception as e:
        system.ui.error("Error reading _metadata.json: " + safe_str(e))
        return
    
    objects_meta = metadata.get("objects", {})
    print("Found " + str(len(objects_meta)) + " objects in metadata")
    
    # Build cache for fast lookup
    print("Building object cache...")
    guid_map, name_map = build_object_cache(projects.primary)
    
    untracked_items = []
    
    # Build a set of folders that ARE tracked (as parents of known objects)
    tracked_folders = set()
    for rel_path in objects_meta.keys():
        parts = rel_path.split("/")
        for i in range(1, len(parts)):
            tracked_folders.add("/".join(parts[:i]))
    
    # Identify new files not in metadata
    new_files = []
    for root, dirs, files in os.walk(import_dir):
        # Prune hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for name in files:
            if name in ["_metadata.json", "BASE_DIR"] or name.startswith('.'):
                continue
            if not name.endswith(".st"):
                continue
            
            rel_path = os.path.relpath(os.path.join(root, name), import_dir).replace(os.sep, "/")
            if rel_path not in objects_meta:
                new_files.append((rel_path, os.path.join(root, name)))
    
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    created_count = 0
    
    # Process each file in metadata
    for rel_path, obj_info in objects_meta.items():
        file_path = os.path.join(import_dir, rel_path.replace("/", os.sep))
        
        if not os.path.exists(file_path):
            print("Skipped (file missing): " + rel_path)
            skipped_count += 1
            continue
        
        obj_guid = obj_info.get("guid")
        obj_name = obj_info.get("name")
        parent_name = obj_info.get("parent")
        
        print("Processing: " + rel_path)
        
        # Find object - prefer GUID matching
        obj = None
        if obj_guid and obj_guid != "N/A":
            obj = find_object_by_guid(obj_guid, guid_map)
        
        # Fallback to name matching
        if obj is None and obj_name:
            obj = find_object_by_name(obj_name, name_map, parent_name)
        
        if obj is None:
            print("  Failed: Object not found in project")
            failed_count += 1
            continue
        
        # Parse file
        declaration, implementation = parse_st_file(file_path)
        
        if declaration is None and implementation is None:
            print("  Skipped: No content in file")
            skipped_count += 1
            continue
            
        # Check content hash
        # Reconstruct content exactly as export does to be sure
        full_content = declaration
        if implementation:
            full_content += "\n\n// === IMPLEMENTATION ===\n" + implementation
            
        current_hash = calculate_hash(full_content)
        stored_hash = obj_info.get("content_hash", "")
        
        if current_hash == stored_hash:
            print("  Skipped: Content unchanged (Hash match)")
            skipped_count += 1
            continue
        
        # Update object
        if update_object_code(obj, declaration, implementation):
            print("  Updated: " + safe_str(obj.get_name()))
            updated_count += 1
            # Update hash in metadata
            obj_info["content_hash"] = current_hash
        else:
            print("  No changes applied")
            skipped_count += 1
            
    # Process new files
    if new_files:
        print("=== Processing New Files ===")
        for rel_path, file_path in new_files:
            print("Found new file: " + rel_path)
            
            # Parse content
            declaration, implementation = parse_st_file(file_path)
            content_check = declaration if declaration else implementation
            if not content_check:
                print("  Skipped: Empty file")
                skipped_count += 1
                continue
                
            type_guid = determine_object_type(content_check)
            if not type_guid:
                print("  Skipped: Unknown object type")
                skipped_count += 1
                continue
            
            # Create logic
            path_parts = rel_path.split("/")
            obj_name = os.path.splitext(path_parts[-1])[0]
            parent_path = "/".join(path_parts[:-1])
            
            parent = ensure_folder_path(parent_path)
            if not parent:
                print("  Failed: Could not ensure parent folder")
                failed_count += 1
                continue
                
            try:
                # Check for existing
                existing = None
                for child in parent.get_children():
                    if child.get_name() == obj_name:
                        existing = child
                        break
                
                if existing:
                    print("  Object already exists: " + obj_name)
                    obj = existing
                else:
                    print("  Creating object: " + obj_name)
                    obj = parent.create_child(obj_name, type_guid)
                    created_count += 1
                    
                if update_object_code(obj, declaration, implementation):
                    print("  Code updated.")
                    updated_count += 1
                    
                    # Update metadata with new object and hash
                    # Reconstruct content
                    full_content = declaration
                    if implementation:
                        full_content += "\n\n// === IMPLEMENTATION ===\n" + implementation
                    
                    new_hash = calculate_hash(full_content)
                    
                    objects_meta[rel_path] = {
                        "guid": safe_str(obj.guid),
                        "type": type_guid,
                        "name": obj_name,
                        "parent": safe_str(parent.get_name()),
                        "content_hash": new_hash
                    }
            except Exception as e:
                print("  Error creating/updating: " + safe_str(e))
                failed_count += 1
    
    # Save updated metadata with new hashes
    if updated_count > 0 or created_count > 0:
        print("Saving updated metadata...")
        save_metadata(import_dir, metadata)
    
    print("=== Import Complete ===")
    print("Updated: " + str(updated_count) + " objects")
    print("Created: " + str(created_count) + " objects")
    print("Failed: " + str(failed_count) + " objects")
    print("Skipped: " + str(skipped_count) + " objects")
    
    elapsed_time = time.time() - start_time
    print("Time elapsed: {:.2f} seconds".format(elapsed_time))
    print("Completed at: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    system.ui.info("Import complete!\n\nUpdated: " + str(updated_count) + "\nCreated: " + str(created_count) + "\nFailed: " + str(failed_count) + "\nSkipped: " + str(skipped_count) + "\nTime elapsed: {:.2f} seconds".format(elapsed_time))
    
    # Untracked warning removed as we now handle new files


def main():
    base_dir, error = load_base_dir()
    if error:
        system.ui.warning(error)
        return
    
    # Confirmation dialog
    message = "WARNING: This operation will overwrite CODESYS objects with data from:\n" + base_dir + "\n\nAre you sure you want to proceed?"
    result = system.ui.choose(message, ("Yes, Overwrite Data", "No, Cancel"))
    
    if result[0] != 0:
        print("Import cancelled by user.")
        return

    import_project(base_dir)


if __name__ == "__main__":
    main()
