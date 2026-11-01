import os
import sys
from pathlib import Path

# Add project root to python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.yojnasetu_api import app

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"🚀 Serving YojnaSetu Production Server with Waitress on http://{host}:{port}")
    serve(app, host=host, port=port, threads=8)
