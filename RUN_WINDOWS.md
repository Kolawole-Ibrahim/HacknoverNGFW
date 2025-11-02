# Running HacknoverNGFW on Windows

## What We've Done:

1. ✅ Fixed config path in `main.py` to work on Windows
2. ✅ Removed invalid "EOF:" from config.yaml
3. ✅ Installed most dependencies (except netifaces which requires C++ build tools)
4. ✅ Updated config.yaml for Windows paths and interfaces

## Requirements to Run:

1. **Administrator Privileges**: The program MUST run as Administrator

   - Right-click PowerShell → "Run as Administrator"
   - Or use: `Start-Process powershell -Verb RunAs`

2. **Npcap or WinPcap** (for packet capture):

   - Scapy needs a packet capture library on Windows
   - Download and install Npcap: https://npcap.com/download/
   - Or WinPcap: https://www.winpcap.org/ (older, less secure)

3. **Optional - Visual C++ Build Tools** (for netifaces):
   - Only needed if you want full network interface detection
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Current program runs without it

## How to Run:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run as Administrator (in elevated PowerShell)
python main.py

# Or with verbose output:
python main.py -v
```

## Windows-Specific Notes:

- Network interfaces use Windows names (e.g., "Ethernet 3" instead of "eth0")
- HIPS monitors Windows system directories (C:\Windows\System32, etc.)
- EDR works with Windows processes
- DPI requires Npcap/WinPcap for packet capture
- Some Linux-specific features may not work on Windows

## Current Status:

- ✅ Program structure is ready
- ✅ Dependencies installed (except netifaces - optional)
- ✅ Config updated for Windows
- ⚠️ Requires Administrator privileges
- ⚠️ Needs Npcap/WinPcap for full packet capture functionality

## If You Get Errors:

1. **"No libpcap provider available"**: Install Npcap/WinPcap
2. **"Permission denied"**: Run PowerShell as Administrator
3. **Module import errors**: Check that all dependencies installed correctly
4. **Config errors**: Verify config.yaml syntax is correct
