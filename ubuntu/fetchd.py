import sys, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.sync_api import sync_playwright

CDP = "http://localhost:9222"
JS = """async (path) => {
  const tok = JSON.parse(localStorage.getItem('sofa.captcha.token') || 'null')
           || (document.cookie.match(/(?:^|; )sofa_captcha=([^;]+)/) || [])[1];
  const r = await fetch(path, { headers: tok ? { 'X-Captcha': tok } : {} });
  return { status: r.status, body: await r.text() };
}"""

pw = sync_playwright().start()
browser = None

def sofa_tab():
    global browser
    if browser is None or not browser.is_connected():
        browser = pw.chromium.connect_over_cdp(CDP)
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if pg.url.startswith("https://www.sofascore.com"):
                return pg
    raise RuntimeError("no www.sofascore.com tab open in the Mac's Chrome")

def fetch(path):
    global browser
    for attempt in (1, 2):          # if the bridge was restarted, reconnect once
        try:
            return sofa_tab().evaluate(JS, path)
        except Exception:
            browser = None
            if attempt == 2:
                raise

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.urlparse(self.path)
        if q.path != "/fetch":
            self.send_error(404); return
        url = urllib.parse.parse_qs(q.query).get("url", [""])[0]
        path = url.split("sofascore.com", 1)[1] if "sofascore.com" in url else url
        try:
            res = fetch(path)
            status, body = res["status"], res["body"].encode()
        except Exception as e:
            status, body = 502, ("fetchd: %s\n" % e).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write(fmt % args + "\n")

HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
