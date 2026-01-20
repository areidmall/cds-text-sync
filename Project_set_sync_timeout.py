# -*- coding: utf-8 -*-
"""
Project_set_sync_timeout.py - Configure AutoSync timeout interval

Sets the sync_timeout parameter in _metadata.json for Project_AutoSync.py

Features:
- Predefined timeout options (2s, 5s, 10s, 15s, 30s)
- Changes apply immediately if AutoSync is running (no restart needed)
- Updates sync_timeout field in metadata with consistent field order

Usage: Run this script and select the desired timeout from the menu
"""
import os
import codecs
import json
from codesys_utils import safe_str, load_base_dir, load_metadata, save_metadata

# Shared utilities imported from modules

def main():
    base_dir, error = load_base_dir()
    if error:
        system.ui.warning(error)
        return
    
    # Load metadata
    metadata = load_metadata(base_dir)
    if not metadata:
        system.ui.error("_metadata.json not found! Run 'Project_export.py' first.")
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
    
    if save_metadata(base_dir, metadata):
        print("Sync timeout updated: " + str(new_timeout) + "ms")
        system.ui.info("AutoSync timeout updated!\n\nNew interval: " + str(new_timeout) + "ms (" + str(new_timeout / 1000.0) + " seconds)\n\nIf AutoSync is running, the change will apply on the next sync cycle (immediately).")
    else:
        system.ui.error("Error writing metadata")

if __name__ == "__main__":
    main()
