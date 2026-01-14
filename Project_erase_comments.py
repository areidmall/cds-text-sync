# -*- coding: utf-8 -*-
import os
import codecs
import re

def erase_comments_in_dir(target_dir):
    print("--- Starting Comment Removal ---")
    
    count = 0
    # Regex to find //, but NOT touching lines with --- (our markers)
    comment_pattern = re.compile(r"//(?!\s---).*$", re.MULTILINE)

    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            if not filename.endswith(".st") and not filename.endswith(".txt"):
                continue
                
            file_path = os.path.join(root, filename)
            
            try:
                with codecs.open(file_path, "r", "utf-8") as f:
                    content = f.read()
                
                # Remove comments
                new_content = comment_pattern.sub("", content)
                
                # Remove trailing whitespace from lines
                lines = [line.rstrip() for line in new_content.splitlines()]
                final_text = "\n".join(lines)

                # Write back only if something changed
                if content != final_text:
                    with codecs.open(file_path, "w", "utf-8") as f:
                        f.write(final_text)
                    print("Cleaned: " + filename)
                    count += 1

            except Exception as e:
                print("Error processing " + filename + ": " + str(e))

    print("--- Completed. Total files cleaned: " + str(count) + " ---")

def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BASE_DIR")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            base_dir = f.read().strip()
    else:
        # Show warning if config doesn't exist
        system.ui.warning("Base directory is not set! Please run 'Project_directory.py' first.")
        return

    # Confirmation dialog
    message = "This operation will PERMANENTLY erase all comments in:\n" + base_dir + "\n\nAre you sure you want to proceed?"
    options = ["Yes, Erase Comments", "No, Cancel"]
    
    # system.ui.choose returns (index, text)
    result = system.ui.choose(message, options)
    
    # Check if user cancelled or chose "No"
    if result[0] != 0:
        print("Operation cancelled by user.")
        return

    # Use base_dir directly (same as in export/import)
    erase_comments_in_dir(base_dir)

if __name__ == "__main__":
    main()
