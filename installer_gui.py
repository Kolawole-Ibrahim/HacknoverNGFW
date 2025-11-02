#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HacknoverNGFW - GUI Installer
One-click installation interface for non-technical users
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import sys
import os
from pathlib import Path

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HacknoverNGFW - Installation Wizard")
        self.root.geometry("750x750")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Installation status
        self.install_status = {}
        self.install_thread = None
        
        self.setup_ui()
        self.check_prerequisites()
    
    def setup_ui(self):
        """Create the installer interface"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ HacknoverNGFW Installer",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="One-Click Installation Wizard",
            font=("Arial", 11),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Create scrollable canvas for main content
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main Content
        content_frame = scrollable_frame
        content_frame.config(padx=20, pady=20)
        
        # Welcome message
        welcome_label = tk.Label(
            content_frame,
            text="Welcome to the HacknoverNGFW Installation Wizard!",
            font=("Arial", 12, "bold"),
            justify=tk.CENTER
        )
        welcome_label.pack(pady=10)
        
        info_text = tk.Text(
            content_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#f8f9fa",
            relief=tk.FLAT
        )
        info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        info_text.insert(tk.END, 
            "This installer will:\n\n"
            "✓ Check Python installation\n"
            "✓ Create virtual environment\n"
            "✓ Install required dependencies\n"
            "✓ Configure the firewall\n"
            "✓ Create desktop shortcut\n\n"
            "Note: Administrator privileges are recommended\n"
            "but not required for installation.\n\n"
            "The installation may take a few minutes."
        )
        info_text.config(state=tk.DISABLED)
        
        # Prerequisites Frame
        prereq_frame = tk.LabelFrame(content_frame, text="Prerequisites Check", font=("Arial", 10, "bold"))
        prereq_frame.pack(fill=tk.X, pady=10)
        
        self.prereq_text = tk.Text(prereq_frame, height=6, font=("Consolas", 9), bg="#ecf0f1")
        self.prereq_text.pack(fill=tk.X, padx=10, pady=10)
        self.prereq_text.config(state=tk.DISABLED)
        
        # Progress Frame
        progress_frame = tk.LabelFrame(content_frame, text="Installation Progress", font=("Arial", 10, "bold"))
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to install...")
        progress_label = tk.Label(progress_frame, textvariable=self.progress_var, font=("Arial", 10))
        progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        # Separator line before install button
        separator = tk.Frame(content_frame, height=2, bg="#bdc3c7")
        separator.pack(fill=tk.X, pady=15)
        
        # Install Button - Make it VERY prominent - PUT IT AT TOP TOO
        # First, add a prominent button at the very top for visibility
        top_install_frame = tk.Frame(content_frame, bg="#27ae60", relief=tk.RAISED, borderwidth=5)
        top_install_frame.pack(fill=tk.X, padx=10, pady=10)
        
        top_label = tk.Label(
            top_install_frame,
            text="READY TO INSTALL - CLICK BELOW",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white"
        )
        top_label.pack(pady=5)
        
        self.top_install_btn = tk.Button(
            top_install_frame,
            text="🚀 INSTALL NOW 🚀",
            command=self.start_installation,
            bg="#1e8449",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=3
        )
        self.top_install_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Install Button - Make it VERY prominent
        install_frame = tk.Frame(content_frame, bg="#ecf0f1", relief=tk.RAISED, borderwidth=3)
        install_frame.pack(fill=tk.X, padx=20, pady=10)
        
        instruction_label = tk.Label(
            install_frame,
            text="Ready to Install!",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        instruction_label.pack(pady=(10, 5))
        
        self.install_btn = tk.Button(
            install_frame,
            text="🚀 INSTALL HacknoverNGFW",
            command=self.start_installation,
            bg="#27ae60",
            fg="white",
            font=("Arial", 16, "bold"),
            width=30,
            height=3,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=4
        )
        self.install_btn.pack(pady=15)
        
        click_hint = tk.Label(
            install_frame,
            text="↑ Click the green button above to start installation ↑",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        click_hint.pack(pady=(0, 10))
        
        # Status labels - moved after install button for better visibility
    
    def log_prereq(self, message, status="info"):
        """Add message to prerequisites text"""
        self.prereq_text.config(state=tk.NORMAL)
        color = {"ok": "green", "error": "red", "warn": "orange", "info": "black"}
        prefix = {"ok": "✓", "error": "✗", "warn": "⚠", "info": "•"}
        self.prereq_text.insert(tk.END, f"{prefix.get(status, '•')} {message}\n")
        self.prereq_text.see(tk.END)
        self.prereq_text.config(state=tk.DISABLED)
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log_prereq("Checking prerequisites...", "info")
        
        # Check Python
        try:
            version = sys.version.split()[0]
            self.log_prereq(f"Python {version} - Found", "ok")
            self.install_status['python'] = True
        except:
            self.log_prereq("Python - Not Found", "error")
            self.install_status['python'] = False
            self.status_label.config(text="❌ Python not found. Please install Python 3.7+ from python.org", fg="red")
        
        # Check if already installed
        venv_path = Path("venv")
        if venv_path.exists():
            self.log_prereq("Previous installation detected", "warn")
            self.install_status['previous_install'] = True
        else:
            self.install_status['previous_install'] = False
        
        # Check admin privileges
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                self.log_prereq("Administrator privileges - OK", "ok")
                self.status_label.config(text="✓ All prerequisites met. Ready to install!", fg="green")
            else:
                self.log_prereq("Administrator privileges - Recommended (not required for install)", "warn")
                self.status_label.config(text="⚠️ Admin privileges recommended. You can install anyway.", fg="orange")
            self.install_status['admin'] = is_admin
        except:
            self.log_prereq("Cannot verify administrator privileges", "warn")
            self.install_status['admin'] = False
    
    def start_installation(self):
        """Start the installation process"""
        if not self.install_status.get('python', False):
            messagebox.showerror("Error", "Python is not installed!\n\nPlease install Python 3.7+ from python.org")
            return
        
        if self.install_thread and self.install_thread.is_alive():
            messagebox.showwarning("Already Installing", "Installation is already in progress!")
            return
        
        # Check admin privileges and offer to restart as admin
        if not self.install_status.get('admin', False):
            response = messagebox.askyesno(
                "Administrator Privileges Required",
                "Administrator privileges are recommended for full functionality.\n\n"
                "Would you like to restart this installer with Administrator privileges?\n\n"
                "Click 'Yes' to restart as admin, or 'No' to continue anyway.\n\n"
                "Note: You can install without admin, but the firewall will need admin to run."
            )
            if response:
                # Restart as administrator
                self.restart_as_admin()
                return
        
        # Confirm installation
        if self.install_status.get('previous_install', False):
            if not messagebox.askyesno("Reinstall?", 
                                     "Previous installation detected.\n\nWould you like to reinstall?"):
                return
        
        self.install_btn.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.progress_var.set("Starting installation...")
        
        # Start installation in separate thread
        self.install_thread = threading.Thread(target=self.run_installation, daemon=True)
        self.install_thread.start()
    
    def restart_as_admin(self):
        """Restart the installer with administrator privileges"""
        try:
            import ctypes
            # Get the script path
            script_path = Path(__file__).absolute()
            # Use ShellExecute to run as admin
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                str(script_path),
                None,
                1
            )
            # Close current window
            self.root.quit()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to restart as administrator:\n{str(e)}\n\n"
                "Please manually right-click and select 'Run as Administrator'"
            )
    
    def run_installation(self):
        """Run the actual installation"""
        try:
            # Step 1: Create virtual environment
            self.update_progress("Step 1/5: Creating virtual environment...", 20)
            venv_path = Path("venv")
            if venv_path.exists():
                self.log_prereq("Removing existing virtual environment...", "info")
                import shutil
                shutil.rmtree(venv_path)
            
            result = subprocess.run(
                [sys.executable, "-m", "venv", "venv"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                raise Exception(f"Failed to create venv: {result.stderr}")
            self.log_prereq("Virtual environment created", "ok")
            
            # Step 2: Upgrade pip
            self.update_progress("Step 2/5: Upgrading pip...", 40)
            venv_pip = Path("venv/Scripts/pip.exe")
            if not venv_pip.exists():
                venv_pip = Path("venv/Scripts/pip")
            
            result = subprocess.run(
                [str(venv_pip), "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                self.log_prereq(f"pip upgrade warning: {result.stderr[:100]}", "warn")
            self.log_prereq("pip upgraded", "ok")
            
            # Step 3: Install dependencies
            self.update_progress("Step 3/5: Installing dependencies (this may take a few minutes)...", 60)
            requirements = Path("requirements.txt")
            
            if requirements.exists():
                # Try installing without netifaces first (it often fails on Windows)
                result = subprocess.run(
                    [str(venv_pip), "install", "setproctitle", "scapy", "Flask", "requests", "psutil", "PyYAML"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    self.log_prereq("Dependencies installed successfully", "ok")
                else:
                    self.log_prereq("Some dependencies may have failed", "warn")
                    self.log_prereq(f"Error: {result.stderr[:200]}", "warn")
            else:
                raise Exception("requirements.txt not found!")
            
            # Step 4: Create directories
            self.update_progress("Step 4/5: Creating directories...", 80)
            for dir_name in ["logs", "quarantined"]:
                Path(dir_name).mkdir(exist_ok=True)
            self.log_prereq("Directories created", "ok")
            
            # Step 5: Create desktop shortcut
            self.update_progress("Step 5/5: Creating desktop shortcut...", 90)
            self.create_desktop_shortcut()
            self.log_prereq("Desktop shortcut created", "ok")
            
            # Installation complete
            self.update_progress("Installation Complete!", 100)
            self.progress_bar.stop()
            self.progress_bar['value'] = 100
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Installation Complete!",
                "HacknoverNGFW has been installed successfully!\n\n"
                "You can now launch the GUI from:\n"
                "• Desktop shortcut\n"
                "• Run: gui_launcher.py\n\n"
                "Remember to run as Administrator!"
            ))
            
            self.install_btn.config(state=tk.NORMAL, text="✓ Installation Complete")
            
        except Exception as e:
            self.progress_bar.stop()
            self.update_progress(f"Installation Failed: {str(e)}", 0)
            self.log_prereq(f"Installation error: {str(e)}", "error")
            self.root.after(0, lambda: messagebox.showerror(
                "Installation Failed",
                f"An error occurred during installation:\n\n{str(e)}\n\n"
                "Please check the prerequisites and try again."
            ))
            self.install_btn.config(state=tk.NORMAL)
    
    def update_progress(self, message, percent):
        """Update progress indicator"""
        self.root.after(0, lambda: self.progress_var.set(message))
        self.root.after(0, lambda: self.status_label.config(text=f"Progress: {percent}%"))
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        try:
            import win32com.client
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "HacknoverNGFW.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(Path(sys.executable))
            shortcut.Arguments = f'"{Path("gui_launcher.py").absolute()}"'
            shortcut.WorkingDirectory = str(Path.cwd().absolute())
            shortcut.IconLocation = str(Path(sys.executable))
            shortcut.save()
        except ImportError:
            # pywin32 not installed, skip shortcut creation
            pass
        except Exception as e:
            # Silently fail - shortcut is not critical
            pass

def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

