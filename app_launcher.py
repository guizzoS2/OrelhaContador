import webbrowser
import threading
import time
from run import app, init_db
import os
import sys
import signal

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open('http://127.0.0.1:5000')

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nEncerrando o aplicativo...")
    os._exit(0)

def main():
    # Initialize database
    init_db()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start browser in a separate thread
    threading.Thread(target=open_browser).start()
    
    # Run the Flask app
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    main() 