#!/usr/bin/env python3
"""
Simplified Dashboard - Minimal version that won't crash
"""

import tkinter as tk
from tkinter import messagebox
import sys

def main():
    try:
        root = tk.Tk()
        root.title("HacknoverNGFW - Protection Dashboard")
        root.geometry("800x600")
        
        # Simple header
        header = tk.Label(root, text="🛡️ HacknoverNGFW Protection Dashboard", 
                         font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=20)
        header.pack(fill=tk.X)
        
        # Status
        status_label = tk.Label(root, text="Status: Ready", font=("Arial", 12))
        status_label.pack(pady=20)
        
        # Info
        info_text = tk.Text(root, height=20, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info_text.insert(tk.END, "Dashboard loaded successfully!\n\n")
        info_text.insert(tk.END, "If you see this, the basic GUI is working.\n\n")
        info_text.insert(tk.END, "The full dashboard should now work.\n")
        info_text.config(state=tk.DISABLED)
        
        # Keep window open
        root.mainloop()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

