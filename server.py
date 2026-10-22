"""Tiny local HTTP server for the login form. Serves the page and accepts the POST,
then returns a success or error message. It does NOT store anything — the point of the
demo is that the credentials travel over the wire (plaintext on HTTP), which Wireshark
captures the moment the request is sent, regardless of what the server does with it.
Run:  python server.py   then open  http://localhost:8000
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs


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
            user = data.get("username", [""])[0]
            pw = data.get("password", [""])[0]
            if not user or not pw:
                raise ValueError("username and password are both required")
            body = f"<h2>Success</h2><p>Login received for {user}.</p><a href='/'>Back</a>"
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
