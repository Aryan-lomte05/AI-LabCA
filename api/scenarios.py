"""Vercel serverless function: /api/scenarios (Python runtime, stdlib only)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import Handler  # noqa: E402


class handler(Handler):  # Vercel's Python builder statically scans for a literal
    pass                  # 'class handler(...)' definition; an import alias doesn't match.
