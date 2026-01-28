"""
Translation Comparison Tool for PlayAural.

Compares English (.ftl) source files with a target locale to identify missing files
and missing translation keys.
"""

import os
import re
import sys
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
SERVER_DIR = SCRIPT_DIR.parent
LOCALES_DIR = SERVER_DIR / "locales"
ENGLISH_DIR = LOCALES_DIR / "en"

def get_message_keys(file_path: Path) -> set[str]:
    """
    Extract message IDs from a Fluent (.ftl) file.
    Matches lines starting with 'key-name ='.
    """
    keys = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Fluent keys start at the beginning of the line
                # Format: key-name = value
                # We also handle terms: -term-name = value
                match = re.match(r"^([a-zA-Z0-9_-]+)\s*=", line)
                if match:
                    keys.add(match.group(1))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return keys

def main():
    print(f"PlayAural Translation Comparison Tool")
    print(f"Source Directory: {ENGLISH_DIR}")
    
    if not ENGLISH_DIR.exists():
        print(f"Error: English locales directory not found at {ENGLISH_DIR}")
        return

    # Prompt for target locale
    target_locale = input("Enter target locale code (e.g., vi, zh): ").strip()
    if not target_locale:
        print("No locale entered. Exiting.")
        return

    target_dir = LOCALES_DIR / target_locale
    print(f"Target Directory: {target_dir}")
    print("-" * 50)

    if not target_dir.exists():
        print(f"Warning: Target directory {target_dir} does not exist.")
        print(f"All files confirm missing.")
        # Proceeding to list all files as missing is one option, 
        # but the user might want to know the directory is missing first.
        # We will treat it as if all files are missing.
    
    # Get all .ftl files in English directory
    en_files = list(ENGLISH_DIR.glob("**/*.ftl"))
    if not en_files:
        print("No .ftl files found in English directory.")
        return

    missing_files = []
    issues_found = False

    for en_file_path in en_files:
        # Calculate relative path to handle subdirectories if any (though usually flat)
        rel_path = en_file_path.relative_to(ENGLISH_DIR)
        target_file_path = target_dir / rel_path

        if not target_file_path.exists():
            missing_files.append(str(rel_path))
            issues_found = True
            continue

        # File exists, compare keys
        en_keys = get_message_keys(en_file_path)
        target_keys = get_message_keys(target_file_path)

        missing_keys = en_keys - target_keys
        
        if missing_keys:
            issues_found = True
            print(f"\n[!] Missing keys in {rel_path}:")
            for key in sorted(missing_keys):
                print(f"  - {key}")

    if missing_files:
        print(f"\n[!] Missing Files ({len(missing_files)}):")
        for f in missing_files:
            print(f"  - {f}")

    print("-" * 50)
    if not issues_found:
        print("Good news! No missing translations found.")
    else:
        print("Analysis complete. Please verify the missing items above.")

if __name__ == "__main__":
    main()
