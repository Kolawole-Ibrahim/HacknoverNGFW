#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HacknoverNGFW - GUI Launcher
User-friendly interface for non-technical users
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import ctypes
import psutil
from pathlib import Path

class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HacknoverNGFW - NextGen Firewall")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Firewall process
        self.firewall_process = None
        self.is_running = False
        
        # Check admin privileges
        self.check_admin()
        
        # Setup UI
        self.setup_ui()
        
        # Check installation status
        self.check_installation()
        
        # Start monitoring
        self.monitor_status()
    
    def check_admin(self):
        """Check if running with admin privileges"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                messagebox.showwarning(
                    "Administrator Required",
                    "This application requires Administrator privileges.\n\n"
                    "Please right-click and select 'Run as Administrator'"
                )
        except:
            pass
    
    def setup_ui(self):
        """Create the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛡️ HacknoverNGFW",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="NextGen Firewall with EDR & HIPS Protection",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="Status", font=("Arial", 12, "bold"), padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="⏸️ Not Running",
            font=("Arial", 14),
            fg="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Control Buttons Frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start Firewall",
            command=self.start_firewall,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ Stop Firewall",
            command=self.stop_firewall,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.install_btn = tk.Button(
            control_frame,
            text="⚙️ Check Installation",
            command=self.check_installation,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            cursor="hand2"
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_logs_btn = tk.Button(
            control_frame,
            text="📋 View Logs",
            command=self.view_logs,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            cursor="hand2"
        )
        self.view_logs_btn.pack(side=tk.LEFT, padx=5)
        
        # Module Status Frame
        modules_frame = tk.LabelFrame(self.root, text="Module Status", font=("Arial", 12, "bold"), padx=10, pady=10)
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.modules_text = scrolledtext.ScrolledText(
            modules_frame,
            height=12,
            font=("Consolas", 10),
            bg="#ecf0f1",
            wrap=tk.WORD
        )
        self.modules_text.pack(fill=tk.BOTH, expand=True)
        self.modules_text.config(state=tk.DISABLED)
        
        # Info/Logs Frame
        info_frame = tk.LabelFrame(self.root, text="Information & Alerts", font=("Arial", 12, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            height=8,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            wrap=tk.WORD
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#34495e", height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="For support, visit: https://github.com/Kolawole-Ibrahim/HacknoverNGFW",
            font=("Arial", 8),
            bg="#34495e",
            fg="#bdc3c7"
        )
        footer_label.pack(pady=5)
    
    def log_info(self, message):
        """Add message to info text area"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def update_modules_status(self):
        """Update module status display"""
        self.modules_text.config(state=tk.NORMAL)
        self.modules_text.delete(1.0, tk.END)
        
        if self.is_running:
            self.modules_text.insert(tk.END, "🟢 DPI (Deep Packet Inspection): Active\n")
            self.modules_text.insert(tk.END, "🟢 EDR (Endpoint Detection & Response): Active\n")
            self.modules_text.insert(tk.END, "🟢 HIPS (Host Intrusion Prevention): Active\n")
            self.modules_text.insert(tk.END, "🟢 Management Client: Active\n\n")
            self.modules_text.insert(tk.END, f"Process ID: {self.firewall_process.pid if self.firewall_process else 'N/A'}\n")
            self.modules_text.insert(tk.END, f"Status: Running\n")
        else:
            self.modules_text.insert(tk.END, "🔴 All Modules: Inactive\n\n")
            self.modules_text.insert(tk.END, "Click 'Start Firewall' to begin protection.\n")
        
        self.modules_text.config(state=tk.DISABLED)
    
    def check_installation(self):
        """Check if installation is complete"""
        self.log_info("Checking installation status...")
        
        issues = []
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            self.log_info(f"✓ Python {python_version} detected")
        except:
            issues.append("Python not found")
            self.log_info("✗ Python not found")
        
        # Check virtual environment
        venv_path = Path("venv")
        if venv_path.exists():
            self.log_info("✓ Virtual environment found")
        else:
            issues.append("Virtual environment not found")
            self.log_info("✗ Virtual environment not found - Run installer first")
        
        # Check dependencies
        try:
            import scapy
            import flask
            import psutil
            import yaml
            self.log_info("✓ Required dependencies installed")
        except ImportError as e:
            issues.append(f"Missing dependency: {e.name}")
            self.log_info(f"✗ Missing dependency: {e.name}")
        
        # Check config file
        config_path = Path("modules/config.yaml")
        if config_path.exists():
            self.log_info("✓ Configuration file found")
        else:
            issues.append("Config file not found")
            self.log_info("✗ Configuration file not found")
        
        if issues:
            self.log_info(f"\n⚠️ Installation incomplete. {len(issues)} issue(s) found.")
            if messagebox.askyesno("Installation Issues", 
                                 "Some components are missing.\n\nWould you like to run the installer?"):
                self.run_installer()
        else:
            self.log_info("\n✓ Installation complete! Ready to start.")
            messagebox.showinfo("Installation Check", "All components are installed and ready!")
    
    def run_installer(self):
        """Run the installer script"""
        self.log_info("Launching installer...")
        try:
            installer_path = Path("scripts/install.bat")
            if installer_path.exists():
                subprocess.Popen(["cmd", "/c", str(installer_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Try PowerShell installer
                installer_ps1 = Path("scripts/install.ps1")
                if installer_ps1.exists():
                    subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(installer_ps1)])
                else:
                    messagebox.showerror("Error", "Installer not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run installer: {str(e)}")
            self.log_info(f"✗ Installer error: {str(e)}")
    
    def start_firewall(self):
        """Start the firewall"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Firewall is already running!")
            return
        
        self.log_info("Starting NextGen Firewall...")
        
        # Check for venv
        venv_python = Path("venv/Scripts/python.exe")
        if not venv_python.exists():
            venv_python = Path("venv/Scripts/pythonw.exe")
        
        if not venv_python.exists():
            messagebox.showerror("Error", 
                               "Virtual environment not found!\n\nPlease run the installer first.")
            self.run_installer()
            return
        
        try:
            # Start firewall process
            main_py = Path("main.py")
            if not main_py.exists():
                messagebox.showerror("Error", "main.py not found!")
                return
            
            self.firewall_process = subprocess.Popen(
                [str(venv_python), str(main_py), "-v"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.is_running = True
            self.status_label.config(text="▶️ Running", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_modules_status()
            self.log_info("✓ Firewall started successfully!")
            self.log_info(f"Process ID: {self.firewall_process.pid}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start firewall:\n{str(e)}")
            self.log_info(f"✗ Failed to start: {str(e)}")
            self.is_running = False
    
    def stop_firewall(self):
        """Stop the firewall"""
        if not self.is_running:
            return
        
        self.log_info("Stopping firewall...")
        
        try:
            if self.firewall_process:
                # Try graceful termination
                self.firewall_process.terminate()
                
                # Wait up to 5 seconds
                try:
                    self.firewall_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.firewall_process.kill()
                
                self.firewall_process = None
            
            # Also check for any remaining firewall processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'main.py' in cmdline and 'nextgen_firewall' in cmdline.lower():
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.is_running = False
            self.status_label.config(text="⏸️ Not Running", fg="red")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.update_modules_status()
            self.log_info("✓ Firewall stopped successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop firewall:\n{str(e)}")
            self.log_info(f"✗ Failed to stop: {str(e)}")
    
    def view_logs(self):
        """Open log file in notepad"""
        log_file = Path("hacknover_ngfw.log")
        if log_file.exists():
            try:
                os.startfile(str(log_file))
                self.log_info("Opening log file...")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open log file:\n{str(e)}")
        else:
            messagebox.showinfo("No Logs", "Log file not found.\nThe firewall needs to run first to generate logs.")
    
    def monitor_status(self):
        """Monitor firewall status periodically"""
        if self.firewall_process:
            # Check if process is still running
            try:
                if self.firewall_process.poll() is not None:
                    # Process has terminated
                    self.is_running = False
                    self.status_label.config(text="⏸️ Stopped", fg="orange")
                    self.start_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    self.update_modules_status()
                    self.log_info("⚠️ Firewall process terminated unexpectedly")
                    self.firewall_process = None
            except:
                pass
        
        self.update_modules_status()
        # Schedule next check
        self.root.after(2000, self.monitor_status)
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Firewall is running. Do you want to stop it and exit?"):
                self.stop_firewall()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = FirewallGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

