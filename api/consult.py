"""Vercel serverless function: /api/consult (Python runtime, stdlib only)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import Handler as handler  # noqa: E402,F401  (Vercel looks for 'handler')
