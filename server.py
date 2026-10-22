"""Tiny local server for the login form: serves the page, receives the POST,
stores each submission to submissions.jsonl, and returns a success or error message.
Run:  python server.py   then open  http://localhost:8000
"""
import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

STORE = Path(__file__).parent / "submissions.jsonl"


def page(body):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{{font-family:Arial;background:#f2f2f2;display:flex;justify-content:center;
align-items:center;height:100vh;margin:0}}.box{{background:pink;padding:30px;border-radius:8px;
box-shadow:0 2px 8px rgba(0,0,0,.15);width:280px;text-align:center}}
a{{color:#0078d4}}</style></head><body><div class="box">{body}</div></body></html>""".encode()


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/login":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = parse_qs(self.rfile.read(length).decode())
            record = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "username": data.get("username", [""])[0],
                "password": data.get("password", [""])[0],
            }
            if not record["username"] or not record["password"]:
                raise ValueError("username and password are both required")
            with STORE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            body = f"<h2>Success</h2><p>Saved. Welcome, {record['username']}.</p><a href='/'>Back</a>"
            self.respond(200, body)
        except Exception as e:
            self.respond(400, f"<h2>Something went wrong</h2><p>{e}</p><a href='/'>Try again</a>")

    def respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(page(body))


if __name__ == "__main__":
    print("running on http://localhost:8000  (Ctrl+C to stop)")
    HTTPServer(("localhost", 8000), Handler).serve_forever()
