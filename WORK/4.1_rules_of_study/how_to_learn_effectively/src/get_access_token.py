from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv


WORK_DIR = Path(__file__).resolve().parent
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    load_dotenv(WORK_DIR / ".env")

    credentials = (os.getenv("GIGACHAT_CREDENTIALS") or "").strip()
    verify_ssl = parse_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS"), default=True)
    scope = (os.getenv("GIGACHAT_SCOPE") or "GIGACHAT_API_PERS").strip()
    request_id = str(uuid.uuid4())

    if not credentials:
        print(
            "Missing GIGACHAT_CREDENTIALS in WORK/4.1/how_to_learn_effectively/.env",
            file=sys.stderr,
        )
        return 1

    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": request_id,
        "Authorization": f"Basic {credentials}",
    }
    payload = {"scope": scope}

    try:
        response = requests.post(
            TOKEN_URL,
            headers=headers,
            data=payload,
            verify=verify_ssl,
            timeout=60,
        )
    except requests.exceptions.SSLError as exc:
        print("SSL error while requesting GigaChat token.", file=sys.stderr)
        print(
            "Your VPN, proxy, antivirus, or local network is likely replacing certificates.",
            file=sys.stderr,
        )
        print(
            "Set GIGACHAT_VERIFY_SSL_CERTS=false in .env for this environment.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 2
    except requests.RequestException as exc:
        print(f"Network error while requesting GigaChat token: {exc}", file=sys.stderr)
        return 3

    print(f"HTTP {response.status_code}")
    print(response.text)

    return 0 if response.ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
