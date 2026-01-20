# -*- coding: utf-8 -*-
"""
Explore_types.py - Discover all object types in the current project
"""
import os
from codesys_utils import safe_str, load_base_dir
from codesys_constants import TYPE_GUIDS, EXPORTABLE_TYPES

def main():
    if not projects.primary:
        print("No project open!")
        return
    
    print("=== Project Object Types Discovery ===")
    all_objects = projects.primary.get_children(recursive=True)
    
    type_counts = {}
    type_names = {v: k for k, v in TYPE_GUIDS.items()}
    
    example_objects = {}
    
    for obj in all_objects:
        try:
            t = safe_str(obj.type)
            type_counts[t] = type_counts.get(t, 0) + 1
            if t not in example_objects:
                example_objects[t] = obj.get_name()
        except:
            continue
    
    print("{:<40} | {:<10} | {:<15} | {:<20}".format("Type GUID", "Count", "Known Name", "Example Object"))
    print("-" * 95)
    
    # Sort by count descending
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    
    for t, count in sorted_types:
        known_name = type_names.get(t, "Unknown")
        status = ""
        if t in EXPORTABLE_TYPES:
            status = "[EXPORTABLE]"
        
        example = example_objects.get(t, "")
        print("{:<40} | {:<10} | {:<15} | {:<20} {}".format(t, count, known_name, example, status))

if __name__ == "__main__":
    main()
