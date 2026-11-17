"""
Curd Rice Business Studio · Frontend Server & Development Proxy
Serves static frontend files and seamlessly proxies API calls to FastAPI backend on http://127.0.0.1:8000
Requires NO external packages (runs on standard Python library).
"""

import http.server
import os
import socketserver
import sys
import urllib.error
import urllib.request

PORT = 3000
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))

API_ROUTES = ["/analyse", "/enquiries", "/upload-csv", "/health"]


class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if any(self.path.startswith(route) for route in API_ROUTES):
            self.proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if any(self.path.startswith(route) for route in API_ROUTES):
            self.proxy_request("POST")
        else:
            self.send_error(404, "Not Found")

    def proxy_request(self, method):
        target_url = f"{BACKEND_URL}{self.path}"
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None

        req_headers = {}
        for key in ["Content-Type", "Accept", "User-Agent"]:
            if key in self.headers:
                req_headers[key] = self.headers[key]

        try:
            req = urllib.request.Request(
                target_url,
                data=post_data,
                headers=req_headers,
                method=method
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for header, value in resp.getheaders():
                    # Strip hop-by-hop headers
                    if header.lower() not in ["transfer-encoding", "connection"]:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                f'{{"error": "Backend at {BACKEND_URL} not reachable", "details": "{str(e)}"}}'.encode("utf-8")
            )


if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print("=" * 65)
        print("  Curd Rice Business Studio · Frontend Server")
        print(f"  Local URL : http://localhost:{PORT}")
        print(f"  Backend   : {BACKEND_URL} (proxied for zero-CORS)")
        print("=" * 65)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down frontend server.")
            sys.exit(0)

