import base64, json, re, requests, user_agents

def get_native_build() -> int:
    return str(requests.get(
        "https://updates.discord.com/distributions/app/manifests/latest",
        params = {
            "install_id":'0',
            "channel":"stable",
            "platform":"win",
            "arch":"x86"
        },
        headers = {
            "user-agent": "Discord-Updater/1",
            "accept-encoding": "gzip"
    }).json()["metadata_version"])

def get_client_build():
    r = requests.get("https://discord.com/login")
    regex = r"assets\/(sentry\.\w+)\.js"
    match = re.search(regex, r.text)
    r = requests.get(f"https://discord.com/assets/{match[1]}.js", headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
    })
    regex = r"buildNumber\D+(\d+)"
    build_number = re.search(regex, r.text).group(1)
    return build_number

def get_main_ver() -> str:
    app = requests.get(
        "https://discord.com/api/downloads/distributions/app/installers/latest",
        params = {
            "channel":"stable",
            "platform":"win",
            "arch":"x86"
        },
        allow_redirects = False
    ).text
    return re.search(r'x86/(.*?)/', app).group(1)

def get_useragent_infos(build_number : int, user_agent: str):

    parsed_ua = user_agents.parse(user_agent)

    xtrack = json.dumps({
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": user_agent,
        "browser_version": parsed_ua.browser.version_string,
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": build_number,
        "client_event_source": None
    })

    while ": " in xtrack:
        xtrack = xtrack.replace(": ", ":")

    track = base64.b64encode(xtrack.encode()).decode()

    return {
        "xtrack": track,
        "browser": {
            "name": parsed_ua.browser.family,
            "version": parsed_ua.browser.version_string
        },
        "os": {
            "name": parsed_ua.os.family,
            "version": parsed_ua.os.version_string
        },
        "device": {
            "family": parsed_ua.device.family,
            "brand": parsed_ua.device.brand,
            "model": parsed_ua.device.model
        }
    }
