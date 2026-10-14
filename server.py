"""
HeatGuard Atlas - JSON API + static host for the React UI (standard library only).

    python server.py            # http://localhost:8000
    python server.py 9000       # custom port

Endpoints
    POST /api/consult    {facts}  -> conclusions, advice, trace, HOW trees
    GET  /api/kb                  -> rules + sources
    GET  /api/scenarios           -> preset test scenarios
Everything else is served from frontend/dist (the built React app).
"""

from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from heatwave_es import build_engine
from heatwave_es.knowledge_base import ALERT_MEANING, RULES, SOURCES
from heatwave_es.scenarios import SCENARIOS

DIST = Path(__file__).resolve().parent / "frontend" / "dist"
ENGINE = build_engine()

# facts the UI may send, with expected types
NUMERIC = {"tmax", "tmax_normal", "heat_days", "rh", "tmin", "tmin_normal"}
CHOICE = {"role", "region", "farm"}
LISTS = {"vulnerable", "symptoms"}


def clean_facts(raw: dict) -> dict:
    facts = {}
    for k, v in (raw or {}).items():
        if v in (None, ""):
            continue
        if k in NUMERIC:
            try:
                v = float(v)
            except (TypeError, ValueError):
                pass  # leave as-is: the engine reports it as an input error
            if k == "heat_days" and isinstance(v, float) and v.is_integer():
                v = int(v)
            facts[k] = v
        elif k in CHOICE:
            facts[k] = str(v)
        elif k in LISTS and isinstance(v, list):
            facts[k] = [str(x) for x in v]
    return facts


def _jsonable(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple, set)):
        return [_jsonable(x) for x in v]
    return str(v)


def consult(raw: dict) -> dict:
    facts = clean_facts(raw)
    res = ENGINE.run(facts)
    alert = res.facts.get("alert")
    how = {}
    for f in ("alert", "hw_category", "night", "hi_level", "hri"):
        if f in res.facts:
            how[f] = ENGINE.how(res, f)
    return {
        "input": facts,
        "facts": {k: _jsonable(v) for k, v in res.facts.items()},
        "alert": alert,
        "alert_meaning": ALERT_MEANING.get(alert),
        "halted_by": res.halted_by,
        "advice": [{"audience": a, "text": t, "rule": r} for a, t, r in res.advice],
        "trace": [{
            "cycle": t.cycle, "id": t.rule.id, "name": t.rule.name, "group": t.rule.group,
            "salience": t.rule.salience, "source": t.rule.source, "because": t.rule.because,
            "matched": t.matched, "asserted": {k: _jsonable(v) for k, v in t.asserted.items()},
            "beaten": t.beaten,
        } for t in res.trace],
        "how": how,
        "sources": {s: SOURCES[s] for s in sorted({t.rule.source for t in res.trace})},
    }


def kb() -> dict:
    return {
        "rules": [{"id": r.id, "name": r.name, "group": r.group, "if": r.if_text(),
                   "then": r.then_text(), "salience": r.salience, "source": r.source,
                   "because": r.because} for r in RULES],
        "sources": SOURCES,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "HeatGuard/1.0"

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200) -> None:
        self._send(code, json.dumps(obj).encode(), "application/json")

    def do_OPTIONS(self):  # CORS pre-flight for the Vite dev server
        self._send(204, b"", "text/plain")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/kb":
            return self._json(kb())
        if path == "/api/scenarios":
            return self._json(SCENARIOS)
        if path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        file = (DIST / path.lstrip("/")).resolve()
        if not file.is_file() or DIST.resolve() not in file.parents:
            file = DIST / "index.html"          # single-page app fallback
        if not file.is_file():
            msg = b"UI not built: run 'npm install && npm run build' in frontend/"
            return self._send(503, msg, "text/plain")
        ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        self._send(200, file.read_bytes(), ctype)

    def do_POST(self):
        if self.path.split("?")[0] != "/api/consult":
            return self._json({"error": "not found"}, 404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(raw, dict):
                raise ValueError("body must be a JSON object")
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json({"error": f"bad request: {exc}"}, 400)
        self._json(consult(raw))

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            sys.stderr.write("  %s\n" % (fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"HeatGuard Atlas running on http://localhost:{port}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
