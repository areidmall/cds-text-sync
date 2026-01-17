# cds-text-sync

**Version**: `0.9.1-beta`

> [!WARNING]
> **⚠️ BETA SOFTWARE - USE WITH CAUTION ⚠️**
>
> This product is **NOT YET RELEASED** and is currently in active development.
> - Features may be incomplete or unstable
> - Breaking changes may occur without notice
> - **ALWAYS backup your CODESYS project before using these scripts**
> - Test thoroughly in non-production environments first

> [!IMPORTANT]
> **Disclaimer**: This is a third-party tool. It is NOT an official product of CODESYS Group and is not affiliated with, sponsored by, or endorsed by CODESYS Group. This tool is provided "as is" and is not a replacement for official CODESYS products (such as CODESYS Git).

This repository contains a set of Python scripts for **CODESYS** that enable a reversible, text-based workflow for project development. It allows you to export your CODESYS project code to a structured folder system, edit it using modern tools (like VS Code or LLMs), and import the changes back into CODESYS.

![Workflow Preview](img/WorkflowPreview.gif)

## 🚀 Key Features

- **Reversible Sync**: Round-trip export and import of POUs, GVLs, and DUTs.
- **Git Friendly**: Exports code to standard `.st` (Structured Text) files organized by project hierarchy.
- **Metadata-Driven**: Uses GUIDs and metadata to ensure reliable updates even if objects are moved or renamed in the project.
- **Clean Code**: Includes tools to strip comments for LLM processing or clean builds.

---

## 🛠️ Installation

1. **Copy Files**: Copy all `.py` files to the CODESYS scripts directory:
   `C:\Users\<YourUsername>\AppData\Local\CODESYS\ScriptDir\`

2. **Access in CODESYS**:
   - The scripts will be available in **Tools > Scripting > Scripts > P**.
   - Note: They appear in the "P" sub-menu because they all start with `Project_`.

3. **Add to Toolbar (Optional but Recommended)**:
   - Go to **Tools > Customize > Toolbars**.
   - Select **Standard** (or create a new one).
   - Click **Add Command**.
   - Look for **ScriptEngine Commands > P**.
   - Add the desired scripts to your toolbar for one-click access.

---

## 📖 Script Overview

### 1. `Project_directory.py`
**The First Step.** Run this to select the folder on your computer where your code should be synced. This creates a `BASE_DIR` file in the script directory to remember your choice.

### 2. `Project_export.py`
Exports the current CODESYS project to the selected directory.
- Creates `.st` files for all POUs, Methods, Actions, Properties, GVLs, and DUTs.
- Generates a `_metadata.json` file (CRITICAL: Do not delete this, as it's required for importing).

### 3. `Project_import.py`
Reads the `.st` files in your sync directory and updates the CODESYS project.
- Matches files to CODESYS objects using the metadata.
- **Untracked File Warning**: If you create new `.st` files or folders directly in the file system, the script will skip them and warn you with a popup list after importing.
- **Warning**: This will overwrite the code in your open CODESYS project. Always have a backup!

### 4. `Project_erase_comments.py`
A utility script that removes comments from the files in your sync directory.
- Removes single-line comments (`//`).
- Removes multi-line comments (`(* ... *)`).
- **Preserves Critical Markers**: It will NOT erase markers like `// ---` or `// === IMPLEMENTATION ===`.
- Useful for reducing token count when sharing code with LLMs or for "cleaning" a project.

### 5. `Project_AutoSync.py` ⚠️ **EXPERIMENTAL**
Automatically monitors your exported `.st` files and syncs changes back to CODESYS in real-time.
- **One-way sync**: Folder → IDE only (external edits update CODESYS)
- Runs in the background without blocking the IDE
- Configurable check interval via `TIMEOUT_MS` file (default: 2000ms)
- **Usage**: Run once to START, run again to STOP
- **Workflow**: Create blocks in IDE → Export → Start AutoSync → Edit files externally
- **⚠️ CAUTION**: This is an experimental feature. Monitor the CODESYS Messages view for sync status.

---

## 🔄 Recommended Workflow

1. **Configure**: Run `Project_directory.py` and select your local Git repository folder.
2. **Export**: Run `Project_export.py`.
3. **Commit**: Use Git to track your changes.
4. **Edit**: Open the `.st` files in your favorite editor (VS Code, etc.) and make changes.
   - **Tip**: If you need a new POU/GVL, create it (even as an empty block) in **CODESYS IDE first**, then run Export. This ensures the object has a valid GUID in the metadata.
5. **Review**: Use Git to review your edits.
6. **Import**: Run `Project_import.py` in CODESYS to bring the changes back into the PLC environment.

---

## ⚠️ Important Notes

- **⚠️ BETA STATUS**: This software is in active development. **Always backup your project** before using any script.
- **Metadata**: Never manually edit or delete `_metadata.json`. It is the link between the files and the CODESYS internal GUIDs.
- **Backups**: Always save a `.project` backup before running an import.
- **Markers**: The scripts use specific markers like `// ---` and `// === IMPLEMENTATION ===` to separate declarations from code. These are **preserved** by the comment eraser and should never be removed manually!
- **Creating New Blocks**: The best workflow is to **create the block name in CODESYS IDE first**, export it, and then fill the content externally. Creating files manually in the folder system will trigger a warning during import because they lack metadata.
- **AutoSync Experimental**: The `Project_AutoSync.py` script is experimental. If you experience issues, stop the sync and use manual export/import workflow instead.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
