import os
import zipfile
import subprocess
import shutil

# Mock the tkinter part of the script for the test to succeed in a headless environment
with open('client/updater.py', 'r') as f:
    content = f.read()

# Replace UI methods with basic prints
content = content.replace('def log(self, text):', 'def log(self, text):\n        print(text)\n        return\n    def x_log(self, text):')
content = content.replace('self.progress_var.set(percent)', 'pass')
content = content.replace('messagebox.showerror', 'print')
content = content.replace('self.root.destroy()', 'pass')

# Avoid tkinter init
content = content.replace('self.root = tk.Tk()', 'self.root = None\n        return')
content = content.replace('self.root.mainloop()', 'self.run_update()')


with open('test_updater_mock.py', 'w') as f:
    f.write(content)

# 1. Setup mock directories
target_dir = os.path.abspath("test_game")
sounds_dir = os.path.join(target_dir, "sounds")
os.makedirs(sounds_dir, exist_ok=True)
os.makedirs(target_dir, exist_ok=True)

# Mock executable
exe_path = os.path.join(target_dir, "test_game.exe")
with open(exe_path, "w") as f:
    f.write("mock executable")

# Mock old sound
old_sound = os.path.join(sounds_dir, "old.ogg")
with open(old_sound, "w") as f:
    f.write("old data")

# 2. Create mock sounds.zip
zip_path = os.path.abspath("mock_sounds.zip")
with zipfile.ZipFile(zip_path, 'w') as z:
    z.writestr("sounds/new.ogg", "new data")

print(f"Created zip at {zip_path}")
print(f"Target dir: {target_dir}")
print(f"Extract dir: {sounds_dir}")

# 3. Call modified updater
cmd = [
    "python", "test_updater_mock.py",
    "--zip", zip_path,
    "--target", target_dir,
    "--exe", "test_game.exe",
    "--extract-dir", sounds_dir
]
print(f"Running command: {' '.join(cmd)}")
subprocess.run(cmd)

# 4. Verify results
assert not os.path.exists(zip_path), "Zip file was not deleted"
assert os.path.exists(os.path.join(sounds_dir, "new.ogg")), "New file not extracted"

print("All tests passed! Cleaning up...")
shutil.rmtree(target_dir)
os.remove('test_updater_mock.py')
