# HacknoverNGFW - User Guide for Non-Technical Users

## 🎯 Quick Start Guide

### For First-Time Users:

#### Step 1: Install the Firewall

**Option A - Easy GUI Installer (Recommended):**
1. Double-click `installer_gui.py`
2. Click "🚀 Install HacknoverNGFW"
3. Wait for installation to complete
4. Done! ✅

**Option B - Command Line Installer:**
1. Double-click `scripts\install.bat`
2. Follow the on-screen instructions
3. Installation will complete automatically

**Important:** If Windows asks for Administrator permission, click "Yes"

---

#### Step 2: Start the Firewall

**Option A - Using GUI Launcher (Recommended):**
1. Double-click `START_FIREWALL.bat` (or `gui_launcher.py`)
2. Click the green "▶ Start Firewall" button
3. The firewall will start protecting your computer

**Option B - Using Desktop Shortcut:**
- After installation, a shortcut should appear on your desktop
- Double-click it to launch

---

## 📋 What Each Button Does

### In the GUI Launcher:

- **▶ Start Firewall**: Begins protecting your computer
- **⏹ Stop Firewall**: Stops the firewall protection
- **⚙️ Check Installation**: Verifies everything is installed correctly
- **📋 View Logs**: Opens the log file to see what the firewall detected

---

## 🛡️ What the Firewall Does

The HacknoverNGFW protects your computer in 3 ways:

1. **DPI (Deep Packet Inspection)**: Monitors network traffic for threats
2. **EDR (Endpoint Detection)**: Watches running programs for suspicious behavior
3. **HIPS (Host Intrusion Prevention)**: Protects system directories from unauthorized changes

---

## ❓ Troubleshooting

### "Python not found" Error
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "Administrator Required" Message
- Right-click the file
- Select "Run as Administrator"
- Click "Yes" when Windows asks

### Firewall Won't Start
1. Click "⚙️ Check Installation"
2. If there are errors, run the installer again
3. Make sure you're running as Administrator

### Can't See the GUI
- Make sure Python is installed
- Try running: `python gui_launcher.py`

---

## 📞 Getting Help

- Check the log file: `hacknover_ngfw.log`
- View logs in the GUI by clicking "📋 View Logs"
- Visit: https://github.com/Kolawole-Ibrahim/HacknoverNGFW

---

## 🔄 Updating

To update the firewall:
1. Download the latest version
2. Run the installer again (it will update automatically)
3. Your settings will be preserved

---

## 💡 Tips

- **Always run as Administrator** for full protection
- **Keep the GUI window open** while the firewall is running
- **Check logs regularly** to see what threats were detected
- **Don't close the window** while the firewall is active (it's protecting you!)

---

## 🎓 Understanding the Status Display

- **🟢 Green = Active**: Module is running and protecting you
- **🔴 Red = Inactive**: Module is stopped
- **🟡 Yellow = Warning**: Something needs attention

---

Enjoy your enhanced security! 🛡️

