#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HacknoverNGFW - Protection Dashboard
Real-time security monitoring and threat display
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import ctypes
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

# Try importing psutil, make it optional
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available. Some features may be limited.")

class ProtectionDashboard:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("🛡️ HacknoverNGFW - Protection Dashboard")
            self.root.geometry("1000x750")
            self.root.resizable(True, True)
            
            # Statistics
            self.stats = {
                'threats_blocked_today': 0,
                'threats_blocked_total': 0,
                'packets_inspected': 0,
                'processes_monitored': 0,
                'files_quarantined': 0,
                'last_threat': None,
                'protection_level': "High"
            }
            
            # Threat history
            self.threat_history = []
            
            # Firewall process
            self.firewall_process = None
            self.is_running = False
            
            # Check admin
            try:
                self.check_admin()
            except Exception as e:
                print(f"Admin check failed: {e}")
            
            # Setup UI
            self.setup_ui()
            
            # Start monitoring (with error handling) - use after() to avoid blocking
            try:
                self.root.after(100, self.monitor_firewall)  # Delay slightly
                self.root.after(200, self.update_dashboard)  # Delay slightly
            except Exception as e:
                print(f"Monitoring setup error: {e}")
                # Try to start anyway
                try:
                    self.root.after(1000, self.monitor_firewall)
                    self.root.after(1000, self.update_dashboard)
                except:
                    pass
            
            # Check if firewall is running
            try:
                self.check_firewall_status()
            except Exception as e:
                print(f"Firewall status check error: {e}")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize dashboard:\n{str(e)}")
            raise
    
    def check_admin(self):
        """Check if running with admin privileges"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                messagebox.showwarning(
                    "Administrator Required",
                    "Administrator privileges are required for full protection.\n\n"
                    "Please restart as Administrator for complete security monitoring."
                )
        except:
            pass
    
    def setup_ui(self):
        """Create the dashboard interface"""
        try:
            # Header with protection status
            header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
        except Exception as e:
            print(f"Error creating header: {e}")
            raise
        
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="🛡️ HacknoverNGFW Protection Dashboard",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Protection status indicator
        self.status_indicator = tk.Label(
            title_frame,
            text="🟢 PROTECTED",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="#2ecc71"
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=20)
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Statistics
        left_panel = tk.Frame(main_frame, bg="#ecf0f1", relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Statistics section
        stats_frame = tk.LabelFrame(left_panel, text="🛡️ Protection Statistics", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create stat items
        self.stat_items = {}
        stat_names = [
            ("Threats Blocked Today", "threats_blocked_today", "🔴"),
            ("Total Threats Blocked", "threats_blocked_total", "🛡️"),
            ("Packets Inspected", "packets_inspected", "📡"),
            ("Processes Monitored", "processes_monitored", "👁️"),
            ("Files Quarantined", "files_quarantined", "📦"),
        ]
        
        for name, key, icon in stat_names:
            item_frame = tk.Frame(stats_frame)
            item_frame.pack(fill=tk.X, pady=5)
            
            label = tk.Label(item_frame, text=f"{icon} {name}:", font=("Arial", 10), anchor=tk.W)
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(item_frame, text="0", font=("Arial", 12, "bold"), 
                                  fg="#27ae60", anchor=tk.E)
            value_label.pack(side=tk.RIGHT, padx=10)
            
            self.stat_items[key] = value_label
        
        # Last threat
        last_threat_frame = tk.LabelFrame(left_panel, text="⚠️ Last Threat Detected", 
                                         font=("Arial", 10, "bold"), padx=10, pady=10)
        last_threat_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.last_threat_label = tk.Label(
            last_threat_frame,
            text="No threats detected",
            font=("Arial", 9),
            fg="gray",
            wraplength=250,
            justify=tk.LEFT
        )
        self.last_threat_label.pack(fill=tk.X, padx=5)
        
        # Protection level
        level_frame = tk.LabelFrame(left_panel, text="🔒 Protection Level", 
                                    font=("Arial", 10, "bold"), padx=10, pady=10)
        level_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.protection_level_label = tk.Label(
            level_frame,
            text="HIGH",
            font=("Arial", 16, "bold"),
            fg="#27ae60"
        )
        self.protection_level_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(left_panel, padx=10, pady=10)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start Protection",
            command=self.start_firewall,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ Stop Protection",
            command=self.stop_firewall,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Right panel - Threat alerts and activity
        right_panel = tk.Frame(main_frame, bg="#ecf0f1", relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Active threats panel
        threats_frame = tk.LabelFrame(right_panel, text="🚨 Active Threats & Alerts", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        threats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Threat list with scrollbar
        threat_scroll = scrolledtext.ScrolledText(
            threats_frame,
            height=15,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        threat_scroll.pack(fill=tk.BOTH, expand=True)
        self.threat_display = threat_scroll
        self.threat_display.config(state=tk.DISABLED)
        
        # Recent activity
        activity_frame = tk.LabelFrame(right_panel, text="📋 Recent Activity", 
                                       font=("Arial", 12, "bold"), padx=10, pady=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        activity_scroll = scrolledtext.ScrolledText(
            activity_frame,
            height=8,
            font=("Consolas", 8),
            bg="#34495e",
            fg="#bdc3c7",
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        activity_scroll.pack(fill=tk.BOTH, expand=True)
        self.activity_display = activity_scroll
        self.activity_display.config(state=tk.DISABLED)
        
        # Initial message (with error handling)
        try:
            self.add_threat_alert("System initialized", "info", "Protection dashboard ready")
            self.add_activity("Dashboard started", "system")
        except Exception as e:
            print(f"Warning: Could not add initial messages: {e}")
    
    def add_threat_alert(self, title, severity, details=""):
        """Add a threat alert to the display"""
        try:
            self.threat_display.config(state=tk.NORMAL)
        except Exception as e:
            print(f"Error accessing threat display: {e}")
            return
        
        colors = {
            "critical": "#e74c3c",
            "high": "#e67e22",
            "medium": "#f39c12",
            "low": "#3498db",
            "info": "#95a5a6"
        }
        
        icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "ℹ️"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = icons.get(severity, "ℹ️")
        
        self.threat_display.insert(tk.END, f"[{timestamp}] {icon} {title}\n", severity)
        if details:
            self.threat_display.insert(tk.END, f"    └─ {details}\n\n", "detail")
        
        self.threat_display.see(tk.END)
        
        # Configure colors
        self.threat_display.tag_config("critical", foreground=colors["critical"])
        self.threat_display.tag_config("high", foreground=colors["high"])
        self.threat_display.tag_config("medium", foreground=colors["medium"])
        self.threat_display.tag_config("low", foreground=colors["low"])
        self.threat_display.tag_config("info", foreground=colors["info"])
        self.threat_display.tag_config("detail", foreground="#95a5a6")
        
        self.threat_display.config(state=tk.DISABLED)
        
        # Store in history
        self.threat_history.append({
            'time': timestamp,
            'severity': severity,
            'title': title,
            'details': details
        })
        
        # Update stats
        if severity in ["critical", "high", "medium", "low"]:
            self.stats['threats_blocked_today'] += 1
            self.stats['threats_blocked_total'] += 1
            self.stats['last_threat'] = title
    
    def add_activity(self, message, category="info"):
        """Add activity log entry"""
        try:
            self.activity_display.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            print(f"Error accessing activity display: {e}")
            return
        
        icons = {
            "system": "⚙️",
            "threat": "🚨",
            "protection": "🛡️",
            "info": "ℹ️"
        }
        
        icon = icons.get(category, "ℹ️")
        self.activity_display.insert(tk.END, f"[{timestamp}] {icon} {message}\n")
        self.activity_display.see(tk.END)
        self.activity_display.config(state=tk.DISABLED)
    
    def update_dashboard(self):
        """Update dashboard statistics and displays"""
        try:
            # Update stat displays
            if hasattr(self, 'stat_items'):
                for key, label in self.stat_items.items():
                    try:
                        value = self.stats.get(key, 0)
                        if isinstance(value, int):
                            label.config(text=f"{value:,}")
                        else:
                            label.config(text=str(value))
                    except Exception as e:
                        print(f"Error updating stat {key}: {e}")
            
            # Update last threat
            if hasattr(self, 'last_threat_label'):
                try:
                    if self.stats.get('last_threat'):
                        self.last_threat_label.config(
                            text=f"{self.stats['last_threat']}\n{datetime.now().strftime('%H:%M:%S')}",
                            fg="#e74c3c"
                        )
                    else:
                        self.last_threat_label.config(text="No threats detected", fg="gray")
                except Exception as e:
                    print(f"Error updating last threat: {e}")
            
            # Update protection level
            if hasattr(self, 'protection_level_label') and hasattr(self, 'status_indicator'):
                try:
                    if self.is_running:
                        self.protection_level_label.config(text="HIGH", fg="#27ae60")
                        self.status_indicator.config(text="🟢 PROTECTED", fg="#2ecc71")
                    else:
                        self.protection_level_label.config(text="OFF", fg="#e74c3c")
                        self.status_indicator.config(text="🔴 UNPROTECTED", fg="#e74c3c")
                except Exception as e:
                    print(f"Error updating protection status: {e}")
            
            # Parse log file for threats
            try:
                self.parse_log_for_threats()
            except Exception as e:
                pass  # Silently ignore log parsing errors
            
            # Schedule next update
            try:
                self.root.after(2000, self.update_dashboard)
            except:
                pass
        except Exception as e:
            print(f"Error in update_dashboard: {e}")
            # Try to schedule next update anyway
            try:
                self.root.after(2000, self.update_dashboard)
            except:
                pass
    
    def parse_log_for_threats(self):
        """Parse log file to detect threats and update stats"""
        log_file = Path("hacknover_ngfw.log")
        if not log_file.exists():
            return
        
        try:
            # Read last 100 lines
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            # Parse for threat indicators
            threat_keywords = {
                'suspicious': ['suspicious', 'anomaly', 'threat', 'malware', 'attack'],
                'blocked': ['blocked', 'dropped', 'denied', 'quarantine'],
                'detected': ['detected', 'alert', 'warning', 'intrusion'],
                'scan': ['scan', 'inspection', 'monitor']
            }
            
            for line in recent_lines:
                line_lower = line.lower()
                
                # Check for threats
                if any(kw in line_lower for kw in threat_keywords['threat']):
                    if 'suspicious' in line_lower or 'threat' in line_lower:
                        # Extract threat info
                        if 'suspicious_command' in line_lower:
                            self.add_threat_alert(
                                "Suspicious Command Detected",
                                "high",
                                "Malicious command pattern detected in process"
                            )
                        elif 'high_cpu' in line_lower:
                            self.add_threat_alert(
                                "High CPU Usage Detected",
                                "medium",
                                "Potential resource exhaustion attack"
                            )
                        elif 'unauthorized' in line_lower:
                            self.add_threat_alert(
                                "Unauthorized Access Attempt",
                                "critical",
                                "Intrusion prevention system blocked unauthorized activity"
                            )
                
                # Count packets inspected
                if 'packet' in line_lower or 'inspect' in line_lower:
                    self.stats['packets_inspected'] += 1
                
                # Count processes
                if 'process' in line_lower and 'monitor' in line_lower:
                    self.stats['processes_monitored'] += 1
                
                # Count quarantined files
                if 'quarantine' in line_lower:
                    self.stats['files_quarantined'] += 1
                    self.add_threat_alert(
                        "File Quarantined",
                        "high",
                        "Potentially malicious file moved to quarantine"
                    )
            
            # Reset counters periodically (keep stats reasonable)
            if self.stats['packets_inspected'] > 1000000:
                self.stats['packets_inspected'] = 0
            
        except Exception as e:
            pass  # Silently ignore log parsing errors
    
    def check_firewall_status(self):
        """Check if firewall is already running"""
        if not HAS_PSUTIL:
            return  # Skip if psutil not available
        
        # Check for running firewall process
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'main.py' in cmdline and 'nextgen_firewall' in cmdline.lower():
                        self.firewall_process = proc
                        self.is_running = True
                        self.start_btn.config(state=tk.DISABLED)
                        self.stop_btn.config(state=tk.NORMAL)
                        self.add_activity("Firewall already running", "system")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass  # Silently fail if psutil has issues
    
    def start_firewall(self):
        """Start the firewall"""
        if self.is_running:
            return
        
        self.add_activity("Starting firewall protection...", "system")
        
        venv_python = Path("venv/Scripts/python.exe")
        if not venv_python.exists():
            venv_python = Path("venv/Scripts/pythonw.exe")
        
        if not venv_python.exists():
            messagebox.showerror("Error", "Virtual environment not found!\n\nPlease run the installer first.")
            return
        
        try:
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
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.add_activity(f"Firewall started (PID: {self.firewall_process.pid})", "protection")
            self.add_threat_alert("Protection Activated", "info", "All security modules are now active")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start firewall:\n{str(e)}")
            self.add_activity(f"Failed to start firewall: {str(e)}", "system")
            self.is_running = False
    
    def stop_firewall(self):
        """Stop the firewall"""
        if not self.is_running:
            return
        
        self.add_activity("Stopping firewall protection...", "system")
        
        try:
            if self.firewall_process:
                self.firewall_process.terminate()
                try:
                    self.firewall_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.firewall_process.kill()
                self.firewall_process = None
            
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            self.add_activity("Firewall stopped", "system")
            self.add_threat_alert("Protection Deactivated", "critical", "Your system is no longer protected")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop firewall:\n{str(e)}")
    
    def monitor_firewall(self):
        """Monitor firewall process status"""
        if self.firewall_process:
            try:
                if self.firewall_process.poll() is not None:
                    # Process terminated
                    self.is_running = False
                    self.start_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    self.add_threat_alert("Firewall Process Terminated", "critical", "Protection is offline")
                    self.firewall_process = None
            except:
                pass
        
        # Schedule next check
        self.root.after(3000, self.monitor_firewall)

def main():
    root = None
    try:
        # Create root window first
        root = tk.Tk()
        root.withdraw()  # Hide initially until ready
        
        # Create app
        app = ProtectionDashboard(root)
        
        # Show window
        root.deiconify()
        
        # Keep window open
        root.mainloop()
        
    except tk.TclError as e:
        # GUI-specific error
        print(f"GUI Error: {str(e)}")
        if root:
            try:
                root.destroy()
            except:
                pass
        input("\nPress Enter to exit...")
        
    except Exception as e:
        # Show error in message box before closing
        error_msg = f"Error: {str(e)}\nType: {type(e).__name__}"
        print(f"FATAL ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        try:
            if root:
                error_window = tk.Tk()
                error_window.withdraw()
                messagebox.showerror(
                    "Dashboard Error",
                    f"An error occurred:\n\n{str(e)}\n\n"
                    f"Error type: {type(e).__name__}\n\n"
                    "Please check:\n"
                    "1. Python is installed correctly\n"
                    "2. All dependencies are installed\n"
                    "3. Run as Administrator if needed\n\n"
                    "Check console for full error details."
                )
                error_window.destroy()
        except:
            pass
        
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

