import os
import sys
import subprocess
import socket
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Auto-setup TLS certs before creating the app ---
hostname = socket.gethostname()
mdns_name = f"{hostname}.local"

cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ssl")
cert_file = os.path.join(cert_dir, "cert.pem")
key_file = os.path.join(cert_dir, "key.pem")

# Run cert setup on every startup (fast, ensures cert matches current hostname/IP)
cert_setup = os.path.join(cert_dir, "setup_certs.bat")
if os.path.exists(cert_setup):
    print("  Setting up TLS certificates...")
    try:
        subprocess.run(
            [cert_setup],
            cwd=cert_dir,
            capture_output=True, text=True, check=True, timeout=30
        )
        print("  Certificates ready.")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  Certificate setup notice: {e}")

# Now create the app
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"

    ssl_context = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)

    # Get current LAN IP
    lan_ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            lan_ip = socket.gethostbyname(hostname)
        except Exception:
            pass

    print("=" * 54)
    print("  SmartTrade Africa Server")
    print("=" * 54)
    if ssl_context:
        print(f"  Local:    https://localhost:{port}")
        if lan_ip:
            print(f"  LAN IP:   https://{lan_ip}:{port}")
        print(f"  LAN DNS:  https://{mdns_name}:{port}")
    else:
        print(f"  HTTP on http://{host}:{port}")
        print(f"  Run ssl\\setup_certs.bat manually to enable HTTPS")
    print("=" * 54)
    print("  Mobile: install ssl/mkcert-rootCA.pem on device")
    print("=" * 54)

    app.run(host=host, port=port, debug=debug, use_reloader=False, ssl_context=ssl_context)
