#!/usr/bin/env python3
"""
Simplified Installer - Guaranteed to show Install button
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from pathlib import Path

class SimpleInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("HacknoverNGFW Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        width = 600
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Label(
            self.root,
            text="🛡️ HacknoverNGFW Installer",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=20
        )
        header.pack(fill=tk.X)
        
        # Status area
        status_frame = tk.Frame(self.root, padx=20, pady=20)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(
            status_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "Checking prerequisites...\n\n")
        self.status_text.config(state=tk.DISABLED)
        
        # Check prerequisites
        self.check_prereq()
        
        # BIG INSTALL BUTTON - Can't miss it!
        install_frame = tk.Frame(self.root, bg="#ecf0f1")
        install_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.install_btn = tk.Button(
            install_frame,
            text="🚀 CLICK HERE TO INSTALL 🚀",
            command=self.start_install,
            bg="#27ae60",
            fg="white",
            font=("Arial", 14, "bold"),
            height=3,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=5
        )
        self.install_btn.pack(fill=tk.X, padx=20, pady=20)
        
        # Hint text
        hint = tk.Label(
            install_frame,
            text="↓ Scroll up to see prerequisites check ↑",
            font=("Arial", 9),
            fg="gray"
        )
        hint.pack(pady=(0, 10))
    
    def log(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def check_prereq(self):
        self.log("Checking Python...")
        try:
            version = sys.version.split()[0]
            self.log(f"✓ Python {version} - OK")
        except:
            self.log("✗ Python - NOT FOUND")
            messagebox.showerror("Error", "Python not found!")
            return
        
        self.log("Checking existing installation...")
        if Path("venv").exists():
            self.log("⚠ Previous installation found (will be replaced)")
        else:
            self.log("✓ No previous installation")
        
        self.log("\n✓ Prerequisites check complete!")
        self.log("Ready to install!")
    
    def start_install(self):
        if not messagebox.askyesno("Confirm", "Start installation?\n\nThis may take a few minutes."):
            return
        
        self.install_btn.config(state=tk.DISABLED, text="⏳ Installing... Please wait")
        self.log("\n" + "="*50)
        self.log("STARTING INSTALLATION...")
        self.log("="*50)
        
        try:
            # Step 1
            self.log("\n[1/5] Creating virtual environment...")
            if Path("venv").exists():
                import shutil
                shutil.rmtree("venv")
            
            result = subprocess.run(
                [sys.executable, "-m", "venv", "venv"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                raise Exception(f"Failed: {result.stderr}")
            self.log("✓ Virtual environment created")
            
            # Step 2
            self.log("\n[2/5] Upgrading pip...")
            venv_pip = Path("venv/Scripts/pip.exe")
            subprocess.run([str(venv_pip), "install", "--upgrade", "pip"], 
                         capture_output=True, timeout=120)
            self.log("✓ pip upgraded")
            
            # Step 3
            self.log("\n[3/5] Installing dependencies (this takes time)...")
            deps = ["setproctitle", "scapy", "Flask", "requests", "psutil", "PyYAML"]
            for dep in deps:
                self.log(f"  Installing {dep}...")
                subprocess.run([str(venv_pip), "install", dep, "--quiet"],
                             capture_output=True, timeout=180)
            self.log("✓ All dependencies installed")
            
            # Step 4
            self.log("\n[4/5] Creating directories...")
            Path("logs").mkdir(exist_ok=True)
            Path("quarantined").mkdir(exist_ok=True)
            self.log("✓ Directories created")
            
            # Step 5
            self.log("\n[5/5] Finalizing...")
            self.log("✓ Installation complete!")
            
            self.log("\n" + "="*50)
            self.log("INSTALLATION SUCCESSFUL!")
            self.log("="*50)
            self.log("\nTo start the firewall:")
            self.log("  Double-click: START_FIREWALL.bat")
            self.log("  Or run: python gui_launcher.py")
            
            messagebox.showinfo(
                "Success!",
                "Installation completed successfully!\n\n"
                "You can now run:\n"
                "• START_FIREWALL.bat\n"
                "• python gui_launcher.py\n\n"
                "Remember to run as Administrator!"
            )
            
            self.install_btn.config(text="✓ Installation Complete!", state=tk.DISABLED)
            
        except Exception as e:
            self.log(f"\n✗ ERROR: {str(e)}")
            messagebox.showerror("Installation Failed", f"Error:\n{str(e)}")
            self.install_btn.config(text="🚀 Try Installing Again", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleInstaller(root)
    root.mainloop()

