import requests

_session: requests.Session | None = None

_VOYAGER_BASE = "https://www.linkedin.com/voyager/api"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/vnd.linkedin.normalized+json+2.1",
    "Accept-Language": "en-GB,en;q=0.9",
    "x-li-lang": "en_US",
    "x-li-track": (
        '{"clientVersion":"1.13.9184","mpName":"voyager-web","osName":"web",'
        '"timezoneOffset":0,"timezone":"Europe/London","deviceFormFactor":"DESKTOP"}'
    ),
    "x-restli-protocol-version": "2.0.0",
}


def get_session(li_at: str) -> requests.Session:
    global _session
    if _session is not None:
        return _session

    s = requests.Session()
    s.cookies.set("li_at", li_at, domain=".linkedin.com")
    s.headers.update(_HEADERS)

    resp = s.get("https://www.linkedin.com/feed/", allow_redirects=True, timeout=15)
    if "authwall" in resp.url or "login" in resp.url:
        raise RuntimeError("LinkedIn session invalid — check your LINKEDIN_LI_AT_COOKIE value.")

    for cookie in s.cookies:
        if cookie.name == "JSESSIONID":
            s.headers["csrf-token"] = cookie.value.strip('"')
            break

    _session = s
    return _session


def voyager_get(path: str, params: dict = None) -> dict:
    from config import LINKEDIN_LI_AT_COOKIE
    session = get_session(LINKEDIN_LI_AT_COOKIE)
    resp = session.get(
        f"{_VOYAGER_BASE}/{path.lstrip('/')}",
        params=params,
        timeout=15,
    )
    if resp.status_code == 999:
        raise RuntimeError("LinkedIn rate-limited this session (HTTP 999). Wait before retrying.")
    resp.raise_for_status()
    return resp.json()
