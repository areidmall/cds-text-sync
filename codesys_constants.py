# -*- coding: utf-8 -*-
"""
codesys_constants.py - Shared constants for CODESYS scripts

Contains all CODESYS object type GUIDs, exportable types, and other
constants used across multiple scripts.
"""

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

# Implementation section marker used in ST files
IMPL_MARKER = "// === IMPLEMENTATION ==="

# Default sync timeout in milliseconds
DEFAULT_TIMEOUT_MS = 10000

# Characters forbidden in filenames
FORBIDDEN_CHARS = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
