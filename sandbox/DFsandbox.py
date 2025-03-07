"""
A simple script to demonstrate basic Dockerfile concepts.
This script will create a simple web server that displays system information.
"""

import os
import platform
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Gather system information
        system_info = f"""
        <html>
            <body>
                <h1>Docker Container System Information</h1>
                <ul>
                    <li>Hostname: {socket.gethostname()}</li>
                    <li>Platform: {platform.platform()}</li>
                    <li>Python Version: {platform.python_version()}</li>
                    <li>Working Directory: {os.getcwd()}</li>
                    <li>Environment TEST_VAR: {os.getenv('TEST_VAR', 'Not set')}</li>
                </ul>
            </body>
        </html>
        """
        
        self.wfile.write(system_info.encode())

def run_server(port=8000):
    print(f"Starting server on port {port}...")
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
  
    # then go to http://localhost:8000
    
