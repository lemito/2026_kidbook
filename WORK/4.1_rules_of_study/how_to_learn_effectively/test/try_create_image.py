from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


WORK_DIR = Path(__file__).resolve().parent


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    load_dotenv(WORK_DIR / ".env")

    credentials = (os.getenv("GIGACHAT_CREDENTIALS") or "").strip() or None
    access_token = (os.getenv("GIGACHAT_ACCESS_TOKEN") or "").strip() or None
    verify_ssl = parse_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS"), default=True)
    model = (os.getenv("GIGACHAT_MODEL") or "GigaChat-2-Max").strip()

    if not credentials and not access_token:
        print(
            "Missing GIGACHAT_CREDENTIALS or GIGACHAT_ACCESS_TOKEN in .env",
            file=sys.stderr,
        )
        return 1

    kwargs = {
        "model": model,
        "timeout": 60,
        "verify_ssl_certs": verify_ssl,
    }
    if credentials:
        kwargs["credentials"] = credentials
    if access_token:
        kwargs["access_token"] = access_token

    payload = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content=(
                    "Ты создаёшь безопасные детские иллюстрации без текста, "
                    "без букв и без цифр."
                ),
            ),
            Messages(
                role=MessagesRole.USER,
                content=(
                    "Сгенерируй картинку: розовый кот в стиле Василия Кандинского, "
                    "яркая абстрактная композиция, без текста."
                ),
            ),
        ],
        function_call="auto",
    )

    with GigaChat(**kwargs) as giga:
        response = giga.chat(payload)

    choice = response.choices[0].message
    print(f"attachments={getattr(choice, 'attachments', None)}")
    print(f"content={(getattr(choice, 'content', '') or '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
