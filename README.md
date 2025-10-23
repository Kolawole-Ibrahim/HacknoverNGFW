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
1. Clone the repository: it clone https://github.com/Kolawole-Ibrahim/HacknoverNGFW.git

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

still working on modifications 
the script is excpected to:

Check for Python 3 and verify version compatibility

Install system packages like python3-pip, venv, etc.

Create virtual environment in a venv or .venv directory

Install Python dependencies from requirements.txt

Set up configuration files and directories

Set proper permissions for the application

TO install for windows, Use:
install.bat or install.ps1

run install.bat to install

if it didnt work 

Try install.ps1

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser #on windows terminal

&

.\install.ps1


Work in progress to for interfaces 

project documentation coming soon!!!!