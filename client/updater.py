import os
import sys
import time
import zipfile
import subprocess
import argparse
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import psutil

class UpdaterApp:
    def __init__(self, zip_path, target_dir, exe_name, wait_pid=None):
        self.zip_path = zip_path
        self.target_dir = target_dir
        self.exe_name = exe_name
        self.wait_pid = wait_pid
        
        # Setup Window
        self.root = tk.Tk()
        self.root.title("PlayAural Updater")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Labels and Progress
        self.status_var = tk.StringVar(value="Initializing...")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, wraplength=380)
        self.lbl_status.pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress.pack(pady=10, fill=tk.X, padx=20)
        
        # Determine accessible name/description handling if needed
        # Standard tkinter is usually accessible enough for simple progress

        # Start update thread
        self.thread = threading.Thread(target=self.run_update, daemon=True)
        self.thread.start()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def log(self, text):
        self.status_var.set(text)
        self.root.update()

    def run_update(self):
        try:
            # 1. Wait for Parent Process to Exit
            if self.wait_pid:
                self.log(f"Waiting for PlayAural (PID {self.wait_pid}) to close...")
                try:
                    proc = psutil.Process(self.wait_pid)
                    proc.wait(timeout=10) # Wait up to 10 seconds
                except psutil.NoSuchProcess:
                    pass # Already gone
                except psutil.TimeoutExpired:
                    self.log("Error: Game process did not close.")
                    messagebox.showerror("Error", "Game process did not close. Please close it manually.")
                    self.root.destroy()
                    return

            # Double check via file access
            # Try to rename the main exe to check if it's locked
            main_exe = os.path.join(self.target_dir, self.exe_name)
            retry_count = 0
            while retry_count < 10:
                try:
                    if os.path.exists(main_exe):
                        # Attempt to open for append to check lock
                        with open(main_exe, 'a+'):
                            pass
                    break
                except IOError:
                    time.sleep(1)
                    retry_count += 1
                    self.log(f"Waiting for file release... ({retry_count}/10)")
            
            if retry_count == 10:
                 messagebox.showerror("Error", "Cannot update: Files are still in use.")
                 self.root.destroy()
                 return

            # 2. Extract Zip
            if not os.path.exists(self.zip_path):
                messagebox.showerror("Error", f"Update file not found:\n{self.zip_path}")
                self.root.destroy()
                return

            self.log("Extracting update...")
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                
                for i, file in enumerate(file_list):
                    zip_ref.extract(file, self.target_dir)
                    percent = ((i + 1) / total_files) * 100
                    self.progress_var.set(percent)
                    # Update status occasionally to not spam UI
                    if i % 10 == 0:
                        self.log(f"Extracting: {int(percent)}%")
            
            self.log("Update complete!")
            time.sleep(1) # Show 100% briefly

            # 3. Cleanup
            try:
                os.remove(self.zip_path)
            except:
                pass # Not critical

            # 4. Launch Game
            self.log(f"Launching {self.exe_name}...")
            main_exe_path = os.path.join(self.target_dir, self.exe_name)
            if os.path.exists(main_exe_path):
                subprocess.Popen([main_exe_path], cwd=self.target_dir)
            else:
                messagebox.showerror("Error", f"Executable not found:\n{main_exe_path}")

        except Exception as e:
            messagebox.showerror("Update Failed", f"An error occurred:\n{str(e)}")
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlayAural Auto-Updater")
    parser.add_argument("--zip", required=True, help="Path to the update zip file")
    parser.add_argument("--target", required=True, help="Target directory to extract to")
    parser.add_argument("--exe", required=True, help="Name of the executable to launch")
    parser.add_argument("--pid", type=int, help="Process ID to wait for shutdown")
    
    args = parser.parse_args()
    
    # Needs psutil
    try:
        import psutil
    except ImportError:
        # Fallback if psutil missing (though it should be in _internal)
        # We can just rely on file lock retry loop
        pass

    app = UpdaterApp(args.zip, args.target, args.exe, args.pid)
    app.run()
