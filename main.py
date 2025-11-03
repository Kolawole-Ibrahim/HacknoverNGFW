#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NextGen Firewall with EDR and HIPS capabilities
Main entry point for the firewall agent
"""

import os
import sys
import time
import signal
import logging
import argparse
import threading
import setproctitle
from pathlib import Path

# Adding the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importing firewall modules
from modules.dpi import DeepPacketInspector
from modules.edr import LinuxEDR
from modules.hips import HIPS
from modules.management import ManagementClient
from modules.utils import setup_logging, check_privileges, load_config

#  For Web server imports
from flask import Flask, jsonify, render_template

# path to the config.yaml file
DEFAULT_CONFIG_PATH = '/home/cyberkv/HacknoverNGFW/modules/config.yaml'

# Global variables & instance
running = True
threads = []
modules = {}  # now defined at the global level

# Web server global variables
web_app = None
web_thread = None

def create_web_server(config, logger, modules_dict):
    """Create and configure Flask web application"""
    global web_app
    
    try:
        web_config = config.get('web_interface', {})
        
        if not web_config.get('enabled', True):
            logger.info("Web interface disabled in configuration")
            return None
        
        logger.info("Creating web application...")
        
        app = Flask(__name__, 
                   template_folder='templates',
                   static_folder='static')
        
        # Storing references to modules for API access
        app.config['firewall_modules'] = modules_dict
        app.config['logger'] = logger
        
        #  App routes
        @app.route('/')
        def index():
            """Main dashboard page"""
            try:
                return render_template('index.html')
            except Exception as e:
                return f"""
                <html>
                    <head><title>HacknoverNGFW</title></head>
                    <body>
                        <h1> HacknoverNGFW Dashboard</h1>
                        <p>Web interface is running!</p>
                        <p>Template not found, but server is working.</p>
                        <p><a href="/api/status">Check API Status</a></p>
                    </body>
                </html>
                """
        
        @app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            module_status = {}
            for name, module in modules_dict.items():
                try:
                    if hasattr(module, 'get_status'):
                        module_status[name] = module.get_status()
                    else:
                        module_status[name] = {'status': 'running', 'info': 'No status method'}
                except Exception as e:
                    module_status[name] = {'status': 'error', 'error': str(e)}
            
            return jsonify({
                'system': {
                    'running': running,
                    'web_server': 'active',
                    'timestamp': time.time()
                },
                'modules': module_status,
                'active_threads': len(threads)
            })
        
        @app.route('/api/modules')
        def api_modules():
            """API endpoint for module list"""
            return jsonify({
                'modules': list(modules_dict.keys()),
                'total': len(modules_dict)
            })
        
        @app.route('/api/health')
        def api_health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0'
            })
        
        @app.route('/api/config')
        def api_config():
            """Configuration endpoint (read-only)"""
            safe_config = {
                'web_interface': config.get('web_interface', {}),
                'modules_enabled': {
                    'dpi': config.get('dpi', {}).get('enabled', False),
                    'edr': config.get('edr', {}).get('enabled', False),
                    'hips': config.get('hips', {}).get('enabled', False)
                }
            }
            return jsonify(safe_config)
        
        logger.info("Web application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create web application: {e}")
        return None

def start_web_server(config, logger, modules_dict):
    """Start the web server in a separate thread"""
    global web_app, web_thread
    
    web_config = config.get('web_interface', {})
    
    if not web_config.get('enabled', True):
        logger.info("Web interface disabled in configuration")
        return
    
    web_app = create_web_server(config, logger, modules_dict)
    if not web_app:
        return
    
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', False)
    
    def run_server():
        """Run the Flask web server"""
        try:
            logger.info(f"Starting web server on {host}:{port}")
            web_app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Web server error: {e}")
    
    # Start web server in a daemon thread
    web_thread = threading.Thread(target=run_server, daemon=True)
    web_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Test if server is running
    try:
        import requests
        response = requests.get(f'http://localhost:{port}/api/health', timeout=2)
        if response.status_code == 200:
            logger.info(f"Web server started successfully on http://{host}:{port}")
            logger.info(f"Local access: http://localhost:{port}")
        else:
            logger.warning(f"Web server started but health check failed: {response.status_code}")
    except ImportError:
        logger.info("Web server started (requests module not available for health check)")
    except Exception as e:
        logger.warning(f"Web server started but health check failed: {e}")

def signal_handler(sig, frame):
    """Handle termination signals"""
    global running
    print("Received termination signal. Shutting down...")
    running = False
    # Signal all threads to stop
    for thread in threads:
        if hasattr(thread, 'stop') and callable(thread.stop):
            thread.stop()

def main():
    """Main entry point for the firewall agent"""

    # Argument parsing setup
    parser = argparse.ArgumentParser(description='NextGen Firewall with EDR and HIPS')
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_PATH,
                        help='Path to the configuration file')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='Run as a background process')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--no-web', action='store_true',
                        help='Disable web interface')
    args = parser.parse_args()

    # Check for root privileges
    if not check_privileges():
        sys.exit(1)

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Failed to load configuration: {str(e)}")
        sys.exit(1)

    # Debug: Print out the config loaded
    print("Loaded configuration:")
    print(config)

    # Setup logging using the config.yaml logging section
    try:
        # Fetch log level from config, default to INFO if not set
        log_level_str = config.get('logging', {}).get('level', 'INFO').upper()
        
        # Debug: Print the log level before trying to use it
        print(f"Log level from config: {log_level_str}")

        # Map string to logging module level
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        # Debug: Print the resolved log level (integer value)
        print(f"Resolved log level: {log_level}")

        # Optionally fetch log file path
        log_path = config.get('logging', {}).get('log_file', None)
        
        # Initialize logging
        logger = setup_logging(log_level, log_path)
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        print(f"Failed to set up logging: {str(e)}")
        sys.exit(1)

    # Override web interface setting if --no-web flag is used
    if args.no_web:
        config['web_interface'] = config.get('web_interface', {})
        config['web_interface']['enabled'] = False
        logger.info("Web interface disabled via command line flag")

    # Set process title for better identification
    setproctitle.setproctitle("nextgen_firewall")

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # For Windows, just run in the foreground (no daemon)
    if args.daemon and sys.platform != "win32":
        # Run as a daemon process on non-Windows systems
        pass  # You can add your `daemon` logic for Unix-based systems here
    else:
        # Run in the foreground (Windows or no daemon flag)
        run_firewall(config, logger)

def run_firewall(config, logger):
    """Initialize and run all firewall components"""
    global threads, modules, running
    
    try:
        # Initialize the management client
        logger.info("Initializing management client...")
        management_client = ManagementClient(config.get('management', {}))
        threads.append(management_client)
        modules['management'] = management_client

        # Initialize the DPI module
        if config.get('dpi', {}).get('enabled', False):
            logger.info("Initializing Deep Packet Inspection module...")
            dpi = DeepPacketInspector(
                config.get('dpi', {}),
                management_client.queue_alert
            )
            threads.append(dpi)
            modules['dpi'] = dpi

        # Initialize the EDR module
        if config.get('edr', {}).get('enabled', False):
            logger.info("Initializing Endpoint Detection & Response module...")
            edr = LinuxEDR(
                config.get('edr', {}),
                management_client.queue_alert
            )
            threads.append(edr)
            modules['edr'] = edr

        # Initialize the HIPS module
        if config.get('hips', {}).get('enabled', False):
            logger.info("Initializing Host Intrusion Prevention System...")
            hips = HIPS(
                config.get('hips', {}),
                management_client.queue_alert
            )
            threads.append(hips)
            modules['hips'] = hips

        # Start web server (if enabled) - pass the modules dictionary
        web_config = config.get('web_interface', {})
        if web_config.get('enabled', True):
            start_web_server(config, logger, modules)
        else:
            logger.info("Web interface disabled in configuration")

        # Start all threads
        for thread in threads:
            thread.start()
            logger.debug(f"Started thread: {thread.__class__.__name__}")

        # Display startup information
        print("\n" + "="*60)
        print("Hacknover NextGen Firewall Started Successfully!")
        print("="*60)
        
        if web_config.get('enabled', True):
            host = web_config.get('host', '0.0.0.0')
            port = web_config.get('port', 5000)
            print(f"Web Dashboard: http://{host}:{port}")
            print(f"Local Access:  http://localhost:{port}")
        
        print(f"Active Modules: {', '.join(modules.keys())}")
        print(f"Active Threads: {len(threads)}")
        print("⏹Press Ctrl+C to stop")
        print("="*60 + "\n")

        logger.info(" Hacknover NextGen Firewall is running")

        # Main loop - keep the program running until signaled to stop
        while running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in firewall operation: {str(e)}")
    finally:
        # Cleanup
        logger.info("Shutting down NextGen Firewall...")
        running = False
        
        # Stop all threads
        for thread in threads:
            if hasattr(thread, 'stop') and callable(thread.stop):
                thread.stop()

        # Wait for threads to finish
        for thread in threads:
            if hasattr(thread, 'is_alive') and thread.is_alive():
                thread.join(5)  # Wait up to 5 seconds for each thread

        logger.info(" Hacknover NextGen Firewall shutdown complete")

if __name__ == '__main__':
    main()