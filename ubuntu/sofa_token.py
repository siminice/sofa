import sys, os, json, base64, time
from playwright.sync_api import sync_playwright

def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)

PAGE = "https://www.sofascore.com/football/tournament/germany/2-bundesliga/44"
out = sys.argv[1]
grab = {}

def on_request(req):
    if "/api/v1/" in req.url:
        if "x-captcha" in req.headers and not grab:
            grab.update(req.headers)
            log("captured token from", req.url)


def on_response(resp):
    if resp.request.resource_type in ("document", "xhr", "fetch", "script"):
        log(resp.status, resp.request.resource_type, resp.url[:110])

log("starting playwright")
with sync_playwright() as p:
    log("launching chromium")
    b = p.chromium.launch(headless=False, timeout=60000,
                          ignore_default_args=["--enable-automation"],
                          args=["--disable-blink-features=AutomationControlled"])
    log("chromium", b.version)
    ctx = b.new_context(locale="en-US")
    page = ctx.new_page()
    page.on("request", on_request)
    page.on("response", on_response)
    log("loading", PAGE)
    page.goto(PAGE, wait_until="domcontentloaded", timeout=45000)
    log("page loaded, title:", page.title())
    for _ in range(45):
        if grab: break
        page.wait_for_timeout(1000)
    ua = page.evaluate("navigator.userAgent")
    cookies = {c["name"]: c["value"] for c in ctx.cookies("https://www.sofascore.com")}
    log("cookies:", ", ".join(sorted(cookies)))
    page.screenshot(path="/out/sofa_page.png", full_page=True)
    with open("/out/sofa_page.html", "w") as f:
        f.write(page.content())
    log("saved sofa_page.png and sofa_page.html")
    b.close()

token = grab.get("x-captcha") or cookies.get("sofa_captcha")
if not token:
    sys.exit("no captcha token found")

lines = [f'user-agent = "{ua}"',
         'referer = "https://www.sofascore.com/"',
         f'header = "x-captcha: {token}"',
         f'cookie = "sofa_captcha={token}"',
         'compressed']
if "x-requested-with" in grab:
    lines.append(f'header = "x-requested-with: {grab["x-requested-with"]}"')

tmp = out + ".tmp"
with open(tmp, "w") as f:
    f.write("\n".join(lines) + "\n")
os.replace(tmp, out)

payload = token.split(".")[1]
exp = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["exp"]
log("token ok, expires", time.strftime("%Y-%m-%d %H:%M", time.localtime(exp)))
