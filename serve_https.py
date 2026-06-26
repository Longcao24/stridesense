#!/usr/bin/env python3
"""
Local HTTPS static server + upload receiver -- for accessing index.html from a phone.
iOS only prompts for motion sensor permission under HTTPS (a secure context); plain HTTP does not work.
This script auto-generates a self-signed certificate (on first run), serves the current directory at 0.0.0.0:8443,
and additionally receives recording data from the phone via POST /upload, saving it to uploads/ for analysis on the computer side (Claude).

Usage:
    python3 serve_https.py            # default port 8443
    python3 serve_https.py 9000       # specify port

On the phone (connected to the same WiFi), open the printed https://<computer IP>:8443/
On the first prompt that the certificate is untrusted -> choose "Continue / Visit anyway".
"""
import http.server, ssl, sys, os, subprocess, socket

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(HERE, "cert.pem")
KEY  = os.path.join(HERE, "key.pem")
UPLOADS = os.path.join(HERE, "uploads")


def lan_ip():
    """Get this machine's LAN IP (used by the phone to connect)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def ensure_cert():
    if os.path.exists(CERT) and os.path.exists(KEY):
        return
    print("· First run: generating a self-signed certificate with openssl ...")
    ip = lan_ip()
    subprocess.check_call([
        "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-keyout", KEY, "-out", CERT, "-days", "825",
        "-subj", "/CN=phone-motion-tracker",
        "-addext", f"subjectAltName=IP:{ip},IP:127.0.0.1,DNS:localhost",
    ])
    print("  Certificate generated: cert.pem / key.pem")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static files + POST /upload receiver for recordings. Default home page = English index_en.html."""

    def send_head(self):
        # Default homepage (/) = English version; the Chinese version is still at /index.html
        if self.path in ("/", "/index"):
            self.path = "/index_en.html"
        return super().send_head()

    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404, "not found")
            return
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(n)
            os.makedirs(UPLOADS, exist_ok=True)
            idx = len([f for f in os.listdir(UPLOADS) if f.endswith(".json")]) + 1
            fname = f"upload_{idx:03d}.json"
            with open(os.path.join(UPLOADS, fname), "wb") as f:
                f.write(body)
            print(f"· Upload received -> uploads/{fname}  ({n} bytes)")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(fname.encode("utf-8"))
        except Exception as e:
            self.send_error(500, str(e))

    def end_headers(self):
        # Do not cache static resources, so the phone always gets the latest index.html
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        try:
            print("· %s - %s" % (self.address_string(), fmt % args))
        except Exception:
            pass


def main():
    os.chdir(HERE)
    ensure_cert()
    ip = lan_ip()

    httpd = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print("\n" + "=" * 52)
    print("  Phone Motion Tracker · HTTPS started (upload enabled)")
    print("=" * 52)
    print(f"  Local (this computer):  https://localhost:{PORT}/")
    print(f"  Phone (use this one):   https://{ip}:{PORT}/")
    print(f"  Uploads saved to:       {UPLOADS}/")
    print("  (Phone must be on the same WiFi; on the cert warning choose \"Continue\")")
    print("  Ctrl-C to stop")
    print("=" * 52 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
