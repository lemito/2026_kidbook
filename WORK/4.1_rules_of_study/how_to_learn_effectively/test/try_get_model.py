from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv


WORK_DIR = Path(__file__).resolve().parent
MODELS_URL = "https://gigachat.devices.sberbank.ru/api/v1/models"


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    load_dotenv(WORK_DIR / ".env")

    access_token = (os.getenv("GIGACHAT_ACCESS_TOKEN") or "").strip()
    verify_ssl = parse_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS"), default=True)

    if not access_token:
        print(
            "Missing GIGACHAT_ACCESS_TOKEN in WORK/4.1/how_to_learn_effectively/.env",
            file=sys.stderr,
        )
        return 1

    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = requests.get(
            MODELS_URL,
            headers=headers,
            verify=verify_ssl,
            timeout=60,
        )
    except requests.exceptions.SSLError as exc:
        print("SSL error while requesting GigaChat models.", file=sys.stderr)
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
        print(f"Network error while requesting GigaChat models: {exc}", file=sys.stderr)
        return 3

    print(f"HTTP {response.status_code}")
    print(response.text)

    return 0 if response.ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
