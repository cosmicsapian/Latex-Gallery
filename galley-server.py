#!/usr/bin/env python3
"""Galley compile server: your own LaTeX compiler for the Galley app.

Speaks the same API as latex.ytotech.com (POST /builds/sync), so Galley can
use it as its compile server. Needs Python 3.8+ and TeX Live with latexmk.

  python3 galley-server.py              # for this computer: http://localhost:8080
  python3 galley-server.py --tunnel     # also for your phone, via a free Cloudflare quick tunnel

Safety: TeX may only read files inside the project and TeX Live (openin_any=p),
latexmk ignores rc files (-norc), shell escape stays restricted, and every
compile has a time limit. With --tunnel a secret key is added to the address,
so only someone who has the full address can compile.
"""
import argparse
import base64
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import PurePosixPath

ENGINES = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}
MAX_BODY = 60 * 1024 * 1024        # bytes of JSON accepted per request
MAX_FILES = 500
LOG_LIMIT = 400_000                # characters of log sent back
BLOCKED_NAMES = {"latexmkrc", ".latexmkrc", "texmf.cnf"}

OPTS = None
KEY = ""
SLOTS = None
TEXLIVE = ""


def bool_opt(value, default):
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def safe_path(path):
    """Return a clean relative path, or None if it could escape the project."""
    if not isinstance(path, str) or not path.strip():
        return None
    p = PurePosixPath(path.replace("\\", "/"))
    if p.is_absolute() or not p.parts:
        return None
    for part in p.parts:
        if part in ("", ".", "..") or part.startswith(".") or "\0" in part:
            return None
    if p.name.lower() in BLOCKED_NAMES:
        return None
    return str(p)


def texlive_version():
    try:
        out = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True, timeout=10).stdout
        m = re.search(r"\(TeX Live (\d{4})", out)
        return m.group(1) if m else out.splitlines()[0]
    except Exception:
        return "unknown"


def read_text(path, limit=LOG_LIMIT):
    try:
        with open(path, "rb") as f:
            data = f.read()
        text = data.decode("utf-8", errors="replace")
        return text[-limit:]
    except OSError:
        return ""


def compile_project(spec):
    """Returns (status, content_type, body_bytes)."""
    compiler = spec.get("compiler", "pdflatex")
    if compiler not in ENGINES:
        return json_reply(400, {"error": "INVALID_COMPILER", "message": f"Use one of: {', '.join(ENGINES)}"})
    resources = spec.get("resources")
    if not isinstance(resources, list) or not resources:
        return json_reply(400, {"error": "MISSING_RESOURCES", "message": "Send at least one file in resources."})
    if len(resources) > MAX_FILES:
        return json_reply(400, {"error": "TOO_MANY_FILES", "message": f"At most {MAX_FILES} files per compile."})
    options = spec.get("options") or {}
    copts = options.get("compiler") or {}
    halt = bool_opt(copts.get("halt_on_error"), False)
    force = bool_opt(copts.get("force"), not halt)
    bib = bool_opt(copts.get("bibliography"), True)

    work = tempfile.mkdtemp(prefix="galley-")
    try:
        main = None
        for i, res in enumerate(resources):
            if not isinstance(res, dict):
                return json_reply(400, {"error": "INVALID_RESOURCE", "resource_index": i})
            sources = [k for k in ("content", "file") if k in res]
            if len(sources) != 1:
                return json_reply(400, {"error": "INVALID_RESOURCE", "resource_index": i,
                                        "message": "Each file needs exactly one of content (text) or file (base64)."})
            path = res.get("path") or ("main.tex" if res.get("main") else None)
            rel = safe_path(path)
            if not rel:
                return json_reply(400, {"error": "INVALID_PATH", "resource_index": i, "path": path})
            if "content" in res:
                if not isinstance(res["content"], str):
                    return json_reply(400, {"error": "INVALID_STRING_CONTENT", "resource_index": i})
                data = res["content"].encode("utf-8")
            else:
                try:
                    data = base64.b64decode(res["file"], validate=True)
                except Exception:
                    return json_reply(400, {"error": "INVALID_BASE64_CONTENT", "resource_index": i, "path": rel})
            full = os.path.join(work, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(data)
            if res.get("main"):
                if main:
                    return json_reply(400, {"error": "MORE_THAN_ONE_MAIN_DOCUMENT"})
                main = rel
        if not main:
            return json_reply(400, {"error": "MUST_SPECIFY_MAIN_DOCUMENT"})

        cmd = ["latexmk", "-norc", ENGINES[compiler], "-interaction=nonstopmode", "-file-line-error"]
        cmd.append("-halt-on-error" if halt else "-f")
        if not bib:
            cmd.append("-bibtex-")
        cmd.append(main)
        env = dict(os.environ, openin_any="p", openout_any="p", shell_escape="p", TEXMFOUTPUT="")
        started = time.time()
        proc = subprocess.Popen(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            out, _ = proc.communicate(timeout=OPTS.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            out, _ = proc.communicate()
        stdout = out.decode("utf-8", errors="replace")[-LOG_LIMIT:]
        stem = os.path.splitext(main)[0]
        pdf_path = os.path.join(work, stem + ".pdf")
        log = read_text(os.path.join(work, stem + ".log"))
        took = time.time() - started

        if not timed_out and os.path.isfile(pdf_path) and (proc.returncode == 0 or force):
            with open(pdf_path, "rb") as f:
                pdf = f.read()
            print(f"  compiled {main} with {compiler} in {took:.1f} s ({len(pdf) // 1024} KB)", flush=True)
            return 201, "application/pdf", pdf
        error = "COMPILATION_TIMEOUT" if timed_out else "COMPILATION_ERROR"
        print(f"  {error.lower().replace('_', ' ')}: {main} after {took:.1f} s", flush=True)
        return json_reply(400, {"error": error, "duration": round(took, 2), "logs": stdout,
                                "log_files": {"__main_document__.log": log}})
    finally:
        shutil.rmtree(work, ignore_errors=True)


def json_reply(status, obj):
    return status, "application/json", json.dumps(obj).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "GalleyServer/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # one line per compile is printed instead

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "86400")

    def reply(self, status, ctype, body):
        self.send_response(status)
        self.cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def route(self):
        """Strip the secret key from the path; None if the key is missing or wrong."""
        path = self.path.split("?", 1)[0]
        if KEY:
            prefix = "/" + KEY
            if path != prefix and not path.startswith(prefix + "/"):
                return None
            path = path[len(prefix):] or "/"
        return path.rstrip("/") or "/"

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = self.route()
        if path is None:
            return self.reply(*json_reply(404, {"error": "NOT_FOUND"}))
        if path == "/":
            return self.reply(*json_reply(200, {"message": "Galley compile server", "service": "galley-server",
                                                "texlive_version": TEXLIVE, "engines": list(ENGINES)}))
        return self.reply(*json_reply(404, {"error": "NOT_FOUND"}))

    def do_POST(self):
        path = self.route()
        if path is None or path != "/builds/sync":
            self.close_connection = True
            return self.reply(*json_reply(404, {"error": "NOT_FOUND"}))
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return self.reply(*json_reply(411, {"error": "LENGTH_REQUIRED"}))
        if length > MAX_BODY:
            self.close_connection = True
            return self.reply(*json_reply(413, {"error": "TOO_LARGE",
                                                "message": f"Projects up to {MAX_BODY // 1048576} MB can be compiled. Shrink large images."}))
        try:
            spec = json.loads(self.rfile.read(length))
            if not isinstance(spec, dict):
                raise ValueError
        except Exception:
            return self.reply(*json_reply(400, {"error": "INVALID_JSON"}))
        if not SLOTS.acquire(timeout=90):
            return self.reply(*json_reply(503, {"error": "BUSY", "message": "Too many compiles at once. Try again."}))
        try:
            result = compile_project(spec)
        except Exception as e:  # keep serving after an unexpected error
            result = json_reply(500, {"error": "SERVER_ERROR", "message": str(e)})
        finally:
            SLOTS.release()
        self.reply(*result)


def start_tunnel(port):
    exe = shutil.which("cloudflared")
    if not exe:
        print("\n  cloudflared isn't installed, so there is no phone address yet.")
        print("  Install it: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/")
        return None
    proc = subprocess.Popen([exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    def watch():
        found = False
        for line in proc.stderr:
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
            if m and not found:
                found = True
                print("\n  Phone, tablet or any other device: paste this into Galley → Settings → Compile server")
                print(f"     {m.group(0)}/{KEY}\n", flush=True)
        if not found:
            print("  The tunnel stopped before it gave an address. Check your internet connection.", flush=True)

    threading.Thread(target=watch, daemon=True).start()
    return proc


def main():
    global OPTS, KEY, SLOTS, TEXLIVE
    ap = argparse.ArgumentParser(description="Your own LaTeX compile server for Galley.")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1", help="127.0.0.1 keeps it on this computer (default)")
    ap.add_argument("--tunnel", action="store_true", help="also give it a public https address with cloudflared")
    ap.add_argument("--key", default=None, help="secret part of the address; 'auto' makes one (automatic with --tunnel)")
    ap.add_argument("--timeout", type=int, default=120, help="seconds a compile may take (default 120)")
    ap.add_argument("--jobs", type=int, default=2, help="compiles that may run at the same time (default 2)")
    OPTS = ap.parse_args()

    if not shutil.which("latexmk"):
        sys.exit("latexmk isn't installed. On Ubuntu: sudo apt install texlive-full latexmk")
    KEY = OPTS.key or ""
    if KEY == "auto" or (OPTS.tunnel and not KEY):
        KEY = secrets.token_urlsafe(12)
    if KEY and not re.fullmatch(r"[A-Za-z0-9_-]{8,}", KEY):
        sys.exit("--key must be at least 8 letters, digits, - or _")
    SLOTS = threading.BoundedSemaphore(max(1, OPTS.jobs))
    TEXLIVE = texlive_version()

    httpd = ThreadingHTTPServer((OPTS.host, OPTS.port), Handler)
    httpd.daemon_threads = True
    local = f"http://localhost:{OPTS.port}" + (f"/{KEY}" if KEY else "")
    print(f"Galley compile server · TeX Live {TEXLIVE}")
    print("\n  This computer: paste this into Galley → Settings → Compile server")
    print(f"     {local}")
    tunnel = start_tunnel(OPTS.port) if OPTS.tunnel else None
    print("\n  Press Ctrl+C to stop.\n", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if tunnel:
            tunnel.terminate()


if __name__ == "__main__":
    main()
