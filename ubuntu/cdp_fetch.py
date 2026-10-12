import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
path = url.split("sofascore.com", 1)[1] if "sofascore.com" in url else url
JS = """async (path) => {
  const tok = JSON.parse(localStorage.getItem('sofa.captcha.token') || 'null')
           || (document.cookie.match(/(?:^|; )sofa_captcha=([^;]+)/) || [])[1];
  const r = await fetch(path, { headers: tok ? { 'X-Captcha': tok } : {} });
  return { status: r.status, body: await r.text() };
}"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://localhost:9222")
    tabs = [pg for c in b.contexts for pg in c.pages
            if pg.url.startswith("https://www.sofascore.com")]
    if not tabs:
        sys.exit("sofacurl: no www.sofascore.com tab open in the Mac's Chrome")
    res = tabs[0].evaluate(JS, path)
    # no b.close(): leave the Mac's Chrome running

if res["status"] != 200:
    sys.stderr.write("sofacurl: HTTP %d for %s\n" % (res["status"], path))
    sys.exit(22)
sys.stdout.write(res["body"])
