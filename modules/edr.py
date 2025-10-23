import logging
import psutil
import time
import os
import fnmatch
import threading
from modules.utils import setup_logging
from modules.utils import is_path_trusted

class LinuxEDR(threading.Thread):
    def __init__(self, config, alert_callback):
        super().__init__()
        self.config = config
        self.alert_callback = alert_callback
        self._stop_event = threading.Event()

        # Extract configuration values for EDR
        edr_config = config.get("edr", {})
        self.cpu_threshold = edr_config.get("cpu_threshold", 50.0)
        self.mem_threshold = edr_config.get("memory_threshold", 200 * 1024 * 1024)

        self.trusted_apps = [app.lower() for app in edr_config.get("trusted_applications", [])]
        self.trusted_paths = [path.lower() for path in edr_config.get("trusted_paths", [])]

        # Set up logging based on the log level from config.yaml
        log_level = edr_config.get("log_level", "INFO")
        self.logger = setup_logging(log_level)
        self.logger.name = "EDR"

def run(self):
    """Main EDR monitoring loop"""
    self.logger.info("EDR module started")
    
    while self.running:
        try:
            self.detect_anomalies()
            time.sleep(self.scan_interval)
        except Exception as e:
            self.logger.error(f"EDR thread error: {str(e)}")
            # Wait before retrying to prevent rapid error loops
            time.sleep(5)

def detect_anomalies(self):
    """Detect system anomalies and suspicious processes with comprehensive error handling"""
    try:
        suspicious_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cpu_percent', 'memory_info', 'create_time', 'username']):
            proc_info = None
            try:
                proc_info = proc.as_dict(attrs=['pid', 'name', 'ppid', 'cpu_percent', 'memory_info', 'create_time', 'username'])
                
                # Validate required fields
                if not all(key in proc_info for key in ['pid', 'name', 'ppid']):
                    continue
                
                # Skip if ppid is None or 0 (kernel processes)
                if proc_info['ppid'] in [None, 0]:
                    continue
                
                pid = proc_info['pid']
                name = proc_info['name']
                ppid = proc_info['ppid']
                
                # Your existing detection logic
                if self.is_suspicious_process(proc_info):
                    suspicious_count += 1
                    self.logger.warning(f"Suspicious process detected: {name} (PID: {pid}, PPID: {ppid})")
                    self.alert_manager.add_alert({
                        'type': 'suspicious_process',
                        'process_name': name,
                        'pid': pid,
                        'ppid': ppid,
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'high'
                    })
                    
            except psutil.NoSuchProcess:
                # Process no longer exists
                continue
            except psutil.AccessDenied:
                # No permission to access this process
                self.logger.debug(f"Access denied to process: {proc_info.get('pid', 'unknown') if proc_info else 'unknown'}")
                continue
            except KeyError as e:
                self.logger.debug(f"Missing key {e} in process info: {proc_info}")
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error processing PID {proc_info.get('pid', 'unknown') if proc_info else 'unknown'}: {str(e)}")
                continue
                
        if suspicious_count > 0:
            self.logger.info(f"Anomaly detection completed. Found {suspicious_count} suspicious processes.")
            
    except Exception as e:
        self.logger.error(f"Critical error in anomaly detection thread: {str(e)}")
        # Don't let the thread die - log error and continue

    def is_whitelisted(self, process_name, exe_path):
        process_name = process_name.lower()
        exe_path = exe_path.lower()

        # Check trusted applications
        if process_name in self.trusted_apps:
            return True

        # Check trusted paths with wildcard support
        for trusted_path in self.trusted_paths:
            if "*" in trusted_path:
                base = trusted_path.replace("\\", "/").lower()
                exe_path_norm = exe_path.replace("\\", "/").lower()
                if fnmatch.fnmatch(exe_path_norm, base):
                    return True
            else:
                if exe_path.startswith(trusted_path):
                    return True
        return False

    def alert(self, anomaly_type, proc_name, details):
        self.logger.warning(f"[{anomaly_type}] Detected in process: {proc_name} - Details: {details}")
        self.alert_callback({
            "module": "EDR",
            "event": "process_anomaly_detected",
            "type": anomaly_type,
            "process": proc_name,
            "details": str(details)
        })

    def stop(self):
        self._stop_event.set()
        self.logger.info("EDR module stopping.")

