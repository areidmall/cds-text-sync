# -*- coding: utf-8 -*-
"""
Project_set_sync_timeout.py - Configure AutoSync timeout interval

Sets the sync_timeout parameter in _metadata.json for Project_AutoSync.py

Usage: Run this script and enter the desired timeout in milliseconds
"""
import os
import codecs
import json

def safe_str(value):
    """Safely convert value to string"""
    try:
        return str(value)
    except:
        return "N/A"

def main():
    # Load base directory
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BASE_DIR")
    
    if not os.path.exists(config_path):
        system.ui.warning("Base directory not set! Run 'Project_directory.py' first.")
        return
    
    with open(config_path, "r") as f:
        base_dir = f.read().strip()
    
    if not os.path.exists(base_dir):
        system.ui.error("Base directory does not exist: " + base_dir)
        return
    
    # Load metadata
    metadata_path = os.path.join(base_dir, "_metadata.json")
    if not os.path.exists(metadata_path):
        system.ui.error("_metadata.json not found! Run 'Project_export.py' first.")
        return
    
    try:
        with codecs.open(metadata_path, "r", "utf-8") as f:
            metadata = json.load(f)
    except Exception as e:
        system.ui.error("Error reading metadata: " + safe_str(e))
        return
    
    # Get current timeout
    current_timeout = metadata.get("sync_timeout", 10000)
    
    # Offer predefined timeout options
    message = "Current AutoSync timeout: " + str(current_timeout) + "ms\n\nSelect new timeout interval:"
    options = (
        "2 seconds (2000ms)",
        "5 seconds (5000ms)",
        "10 seconds (10000ms) - Default",
        "15 seconds (15000ms)",
        "30 seconds (30000ms)",
        "Cancel"
    )
    
    result = system.ui.choose(message, options)
    
    if result[0] == 5:  # Cancel
        print("Cancelled by user")
        return
    
    # Map selection to timeout value
    timeout_map = {
        0: 2000,
        1: 5000,
        2: 10000,
        3: 15000,
        4: 30000
    }
    
    new_timeout = timeout_map.get(result[0])
    if new_timeout is None:
        print("Invalid selection")
        return
    
    # Update metadata
    metadata["sync_timeout"] = new_timeout
    
    try:
        with codecs.open(metadata_path, "w", "utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print("Sync timeout updated: " + str(new_timeout) + "ms")
        system.ui.info("AutoSync timeout updated!\n\nNew interval: " + str(new_timeout) + "ms (" + str(new_timeout / 1000.0) + " seconds)\n\nIf AutoSync is running, the change will apply on the next sync cycle (immediately).")
    except Exception as e:
        system.ui.error("Error writing metadata: " + safe_str(e))

if __name__ == "__main__":
    main()
