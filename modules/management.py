import threading
import queue
import yaml
from modules.hips import HIPS
from modules.edr import LinuxEDR
from modules.dpi import DeepPacketInspector
from modules.utils import setup_logging  # Assuming you have a logging function in utils.py

class ManagementClient(threading.Thread):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.alert_queue = queue.Queue()
        self._stop_event = threading.Event()
        self.alert_history = []  # Store alerts for dashboard

        # Setup logging
        try:
            log_level = config.get("logging", {}).get("level", "INFO")
            log_file = config.get("logging", {}).get("log_file", None)
            self.logger = setup_logging(log_level, log_file)
            self.logger.info("ManagementClient initialized.")
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Don't raise - continue without file logging
            import logging
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)

    def run(self):
        """Process alerts from the queue"""
        while not self._stop_event.is_set():
            try:
                alert = self.alert_queue.get(timeout=1)
                self.handle_alert(alert)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing alert: {e}")

    def queue_alert(self, alert):
        """Put the alert in the queue to be processed"""
        self.alert_queue.put(alert)

    def handle_alert(self, alert):
        """Handle the received alert"""
        # Add timestamp and store in history
        import time
        from datetime import datetime
        alert['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert['time'] = time.time()
        
        # Store in history (keep last 1000 alerts)
        self.alert_history.append(alert)
        if len(self.alert_history) > 1000:
            self.alert_history.pop(0)
        
        # Log the alert
        self.logger.warning(f"[ManagementClient] Alert received: {alert}")

    def stop(self):
        """Stop all the modules and the thread"""
        self._stop_event.set()

        # Attempt to stop modules gracefully if they have stop() methods
        try:
            if hasattr(self.hips, 'stop'):
                self.hips.stop()
            if hasattr(self.edr, 'stop'):
                self.edr.stop()
            if hasattr(self.dpi, 'stop'):
                self.dpi.stop()
        except Exception as e:
            self.logger.error(f"Error stopping modules: {e}")

def load_config(path='config.yaml'):
    """Load the configuration from config.yaml"""
    try:
        with open(path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Configuration file {path} not found.")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing the configuration file: {e}")
        raise

if __name__ == "__main__":
    # Load config
    config_path = 'config.yaml'  # Adjust path if needed
    config = load_config(config_path)

    # Initialize and start the management client
    try:
        management_client = ManagementClient(config=config)
        management_client.start()
    except Exception as e:
        print(f"Error starting ManagementClient: {e}")
        sys.exit(1)
