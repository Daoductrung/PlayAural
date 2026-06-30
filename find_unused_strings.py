import os
import re
import glob
import json

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER_LOCALES_DIR = os.path.join(PROJECT_ROOT, "server", "locales", "en")
CLIENT_LOCALES_DIR = os.path.join(PROJECT_ROOT, "client", "locales", "en")
WEB_CLIENT_LOCALES_DIR = os.path.join(PROJECT_ROOT, "web_client", "locales")
MOBILE_CLIENT_LOCALES_FILE = os.path.join(PROJECT_ROOT, "mobile_client", "locales", "en", "client.json")

SCAN_DIRS = [
    os.path.join(PROJECT_ROOT, "server"),
    os.path.join(PROJECT_ROOT, "client"),
    os.path.join(PROJECT_ROOT, "web_client"),
    os.path.join(PROJECT_ROOT, "mobile_client"),
]

SKIP_DIRS = [
    "__pycache__",
    ".git",
    ".idea",
    "venv",
    "env",
    "locales", # Skip scanning definition files for usage
    "generated", # Skip generated manifests
]

SKIP_FILES = [
    "en.js", # Skip scanning definition files for usage
    "vi.js", # Skip scanning definition files for usage
    "manifest.js", # Skip locale metadata
    "localeCatalogs.ts", # Skip generated locale registry
    "find_unused_strings.py", # Skip self
    "architecture_overview.md", # Skip documentation
    "development_guidelines.md", # Skip documentation
    "task.md", # Skip documentation
    "implementation_plan.md" # Skip documentation
]

EXTENSIONS = [".py", ".js", ".html", ".css", ".ts", ".tsx"]

def parse_ftl(file_path):
    """Extract keys from an FTL file."""
    keys = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # FTL key format: key-name = value
                # Using simple regex to capture key at start of line
                match = re.match(r"^([a-zA-Z0-9_-]+)\s*=", line)
                if match:
                    keys.append(match.group(1))
    except Exception as e:
        print(f"Error parsing FTL {file_path}: {e}")
    return keys

def parse_js_locale_file(file_path):
    """Extract keys from a web locale catalog file."""
    keys = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(r'"([a-zA-Z0-9_-]+)":\s*["{]', content)
            keys.extend(matches)
    except Exception as e:
        print(f"Error parsing JS locale file {file_path}: {e}")
    return keys

def parse_json_locale_file(file_path):
    """Extract keys from a JSON locale catalog file."""
    keys = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                keys.extend(str(key) for key in data.keys())
    except Exception as e:
        print(f"Error parsing JSON locale file {file_path}: {e}")
    return keys

def get_all_source_files():
    """Get all source files to scan."""
    files = []
    for scan_dir in SCAN_DIRS:
        for root, dirs, filenames in os.walk(scan_dir):
            # Modify dirs in-place to skip
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for filename in filenames:
                if filename in SKIP_FILES:
                    continue
                if any(filename.lower().endswith(ext) for ext in EXTENSIONS):
                    files.append(os.path.join(root, filename))
    return files

def check_usage(keys, source_files):
    """Check if keys are used in source files."""
    unused_keys = set(keys)
    used_keys = set()
    
    total_files = len(source_files)
    print(f"Scanning {total_files} files...")

    for i, file_path in enumerate(source_files):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
                # Check for each remaining unused key
                # We iterate a copy because we modify the set
                for key in list(unused_keys):
                    if key in content:
                        unused_keys.remove(key)
                        used_keys.add(key)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return unused_keys, used_keys

def main():
    print("Starting unused strings analysis...")
    
    # 1. Collect all defined keys
    all_keys = {} # {"filename": [keys]}
    
    # Server FTL
    if os.path.exists(SERVER_LOCALES_DIR):
        ftl_files = glob.glob(os.path.join(SERVER_LOCALES_DIR, "*.ftl"))
        for ftl in ftl_files:
            filename = os.path.basename(ftl)
            keys = parse_ftl(ftl)
            all_keys[f"server/locales/en/{filename}"] = keys
            print(f"Found {len(keys)} keys in {filename}")

    # Client FTL (if exists)
    if os.path.exists(CLIENT_LOCALES_DIR):
        ftl_files = glob.glob(os.path.join(CLIENT_LOCALES_DIR, "*.ftl"))
        for ftl in ftl_files:
            filename = os.path.basename(ftl)
            keys = parse_ftl(ftl)
            all_keys[f"client/locales/en/{filename}"] = keys
            print(f"Found {len(keys)} keys in client/{filename}")

    # Web JS source catalog
    web_source_file = os.path.join(WEB_CLIENT_LOCALES_DIR, "en.js")
    if os.path.exists(web_source_file):
        keys = parse_js_locale_file(web_source_file)
        all_keys["web_client/locales/en.js"] = keys
        print(f"Found {len(keys)} keys in web_client/locales/en.js")

    # Mobile JSON source catalog
    if os.path.exists(MOBILE_CLIENT_LOCALES_FILE):
        keys = parse_json_locale_file(MOBILE_CLIENT_LOCALES_FILE)
        all_keys["mobile_client/locales/en/client.json"] = keys
        print(f"Found {len(keys)} keys in mobile_client/locales/en/client.json")

    # Flatten keys for checking
    flat_keys = []
    for k_list in all_keys.values():
        flat_keys.extend(k_list)
    
    unique_keys = set(flat_keys)
    print(f"Total unique keys to check: {len(unique_keys)}")

    # 2. Collect source files
    source_files = get_all_source_files()
    
    # 3. Check usage
    unused, used = check_usage(unique_keys, source_files)
    
    # 4. Generate Report
    report_lines = []
    report_lines.append(f"Unused Strings Report")
    report_lines.append(f"=====================")
    report_lines.append(f"Generated on: {os.environ.get('USERNAME', 'User')}")
    report_lines.append(f"Total Keys: {len(unique_keys)}")
    report_lines.append(f"Unused Keys: {len(unused)}")
    report_lines.append(f"Used Keys: {len(used)}")
    report_lines.append("")
    report_lines.append("IMPORTANT: This script only checks for literal string text matches.")
    report_lines.append("Keys constructed dynamically (e.g. f'game-name-{type}') will appear as UNUSED.")
    report_lines.append("Please verify manually before deleting.")
    report_lines.append("")

    for source, keys in all_keys.items():
        file_unused = [k for k in keys if k in unused]
        if file_unused:
            report_lines.append(f"File: {source}")
            report_lines.append(f"Found {len(file_unused)} unused keys:")
            for k in sorted(file_unused):
                report_lines.append(f"  - {k}")
            report_lines.append("")

    report_path = os.path.join(PROJECT_ROOT, "unused_strings_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Analysis complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
