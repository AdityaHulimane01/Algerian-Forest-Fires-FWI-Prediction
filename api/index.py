import os
import sys

# Ensure root project directory is in sys.path so application and models are resolved
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from application import app

# Vercel's Python runtime requires an 'app' WSGI/ASGI callable
if __name__ == "__main__":
    app.run(debug=True)
