#!/usr/bin/env python3
"""
Dharma Lens – Quick Start
Run: python3 run.py
"""
import subprocess, sys, os

print("╔══════════════════════════════════════════╗")
print("║       DHARMA LENS – Legal Platform       ║")
print("╚══════════════════════════════════════════╝")
print()

# Check dependencies
missing = []
for pkg in ["flask","pdfplumber","sklearn"]:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"Installing missing packages: {missing}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages", "-q"])

os.environ.setdefault("PORT", "5050")
from app import app
port = int(os.environ["PORT"])
print(f"✅ Server starting at http://localhost:{port}")
print(f"📖 Open browser: http://localhost:{port}")
print()
app.run(host="0.0.0.0", port=port, debug=False)
