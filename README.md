# HacknoverNGFW
 This is a Python-based Next Generation Firewall (NGFW) that provides network security features including packet filtering, intrusion detection, and traffic monitoring.

 Project Features
Deep Packet Inspection: Real-time network packet inspection and filtering

Host Intrusion and Prevention System: Basic pattern-based intrusion detection system

Traffic Monitoring: Live network traffic analysis and logging

Custom Rules: Configurable firewall rules for different security policies

Logging: Comprehensive logging of network events and security incidents

Main.py Module Explanation

This is the main entry point for HacknoverNGFW which combines Deep Packet Inspection (DPI), Endpoint Detection & Response (EDR), and Host Intrusion Prevention System (HIPS) capabilities.

Key Imports:

setproctitle: For renaming the process for better identification

Custom modules: DeepPacketInspector, LinuxEDR, HIPS, ManagementClient

Utility functions: setup_logging, check_privileges, load_config

def signal_handler(sig, frame): handles termination signals (Ctrl+C, kill commands)

Setup guide.
1. Clone the repository: git clone https://github.com/Kolawole-Ibrahim/HacknoverNGFW.git

Change into the directory:cd HacknoverNGFW

2. Set up Python Virtual enviroment(Venv)
python -m venv venv
Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure the App
Check config.yaml for the configuration details and set up any neccesary network settings 

5. Run the App
in your venv: python main.py
on your terminal:Python3 main.py

6. Installation 
Install.sh still a little bit shaky, 
to install, make it executable chmod +x install.sh 
run with sudo ./install.sh

still working on modification,
the script is excpected to:

Check for Python 3 and verify version compatibility

Install system packages like python3-pip, venv, etc.

Create virtual environment in a venv or .venv directory

Install Python dependencies from requirements.txt

Set up configuration files and directories

Set proper permissions for the application

## 🖥️ Windows Installation (User-Friendly)

### For Non-Technical Users - Easy GUI Installation:

1. **Double-click `installer_gui.py`** (or `scripts\install.bat`)
2. Click "🚀 Install HacknoverNGFW"
3. Wait for installation to complete
4. Done! ✅

### Running the Firewall:

**Option 1 - GUI Launcher (Recommended):**
- Double-click `START_FIREWALL.bat` or `gui_launcher.py`
- Click "▶ Start Firewall" button
- Easy-to-use interface with Start/Stop buttons!

**Option 2 - Command Line:**
- Run `scripts\install.bat` to install
- Activate: `venv\Scripts\activate`
- Run: `python main.py`

### Features for Non-Technical Users:
- ✅ One-click GUI installer
- ✅ Visual GUI launcher with Start/Stop buttons
- ✅ Real-time status display
- ✅ Easy log viewing
- ✅ Desktop shortcut creation
- ✅ Automatic dependency checking
- ✅ Progress indicators

See **USER_GUIDE.md** for detailed step-by-step instructions!

### Advanced Windows Installation:

If the GUI installer doesn't work, use:
- `install.bat` - Improved command-line installer
- `install.ps1` - PowerShell installer

For PowerShell, you may need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\install.ps1
```

---

## 📚 Documentation

- **USER_GUIDE.md** - Complete guide for non-technical users
- **RUN_WINDOWS.md** - Technical details for Windows

---

Work in progress for interfaces and additional features!
