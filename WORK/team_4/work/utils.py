"""Утилиты

В этом файле собраны различные функции-утилиты и константы,
которые помогают в рутинной работе с нейросетями и генерацией.
"""

import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Union
from pydantic import BaseModel

from langchain_gigachat import GigaChat
from langchain_google_genai import ChatGoogleGenerativeAI


def setup_env() -> None:
    # Ищем .env и в текущей директории, и уровнем выше.
    cur_dir = Path.cwd()
    env_candidates = [
        cur_dir / '.env',
        cur_dir.parent / '.env',
    ]
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)


setup_env()
credentials_gigachat = os.getenv("AUTHORIZATION_KEY")
gigachat_scope = os.getenv("SCOPE")
ca_bundle_file = os.getenv("CA_BUNDLE_FILE")
google_api_key = os.getenv("GOOGLE_API_KEY")

gemini_model_list = [
    # Подробнее: https://ai.google.dev/gemini-api/docs/pricing?hl=ru
    'gemini-3.1-flash-lite-preview',
    'gemini-3-flash-preview',
    'gemini-2.5-pro',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash-lite-preview-09-2025',
]


class DemoResponse:
    def __init__(self, text: str):
        self.content = text


class DemoLLM:
    """Локальный отладочный фолбэк. Не использовать для финальной генерации статей."""
    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature

    def invoke(self, prompt: str) -> DemoResponse:
        prompt = prompt.strip()

        if "Ответь одним словом: ок" in prompt:
            return DemoResponse("ок")

        if "Напиши введение и содержание для статьи по физике" in prompt:
            concept = _extract_tag(prompt, "CONCEPT") or "Физическое явление"
            return DemoResponse(_build_demo_index_article(concept))

        if "Напиши раздел/подраздел" in prompt:
            concept = _extract_tag(prompt, "CONCEPT") or "Физическое явление"
            part = _extract_tag(prompt, "PART") or "1. Введение"
            return DemoResponse(_build_demo_part_article(concept, part))

        return DemoResponse("Демо-ответ")

    def with_structured_output(self, structured):
        return self


def _extract_tag(text: str, tag: str) -> Optional[str]:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else None


def _slugify(title: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", title.lower(), flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "-", cleaned.strip())
    return cleaned


def _build_demo_index_article(concept: str) -> str:
    section_titles = [
        f"Что такое {concept}",
        f"Главные свойства {concept}",
        f"Где встречается {concept}",
        f"Как изучают {concept}",
        f"Почему {concept} важно",
    ]
    index_lines = [f"{i + 1}. [{title}](#{_slugify(title)})" for i, title in enumerate(section_titles)]
    return (
        f"# {concept}\n\n"
        f"## Введение\n\n"
        f"Почему одни явления кажутся привычными, а на самом деле скрывают важные законы природы?\n\n"
        f"{concept} - это физическое понятие, которое помогает описывать и объяснять процессы в природе и технике. "
        f"Его изучают, чтобы лучше понимать окружающий мир и связи между явлениями.\n\n"
        f"Это понятие важно потому, что через него удобно разбирать реальные примеры из жизни, школьные опыты и работу приборов. "
        f"При этом {concept.lower()} стоит рассматривать аккуратно, чтобы не путать с близкими по смыслу терминами, если они есть.\n\n"
        f"## Содержание\n\n"
        + "\n".join(index_lines)
    )


def _build_demo_part_article(concept: str, part: str) -> str:
    marker, title = part.split(". ", 1)
    heading = "###" if marker.isdigit() else "####"
    return (
        f"{heading} {title}\n\n"
        f"{title} помогает раскрыть понятие **{concept}** с понятной стороны: сначала через наблюдаемые примеры, "
        f"а затем через более точные научные объяснения. Такой подход делает тему связной и удобной для 8 класса, "
        f"потому что новое знание опирается на знакомые ситуации из повседневной жизни, опытов и техники."
    )


def get_llm(name: str,
            temperature: float = 0.7,
            structured: BaseModel = None) -> Optional[Union[GigaChat, ChatGoogleGenerativeAI, DemoLLM]]:
    llm = None
    if name.lower() == "demollm":
        llm = DemoLLM(temperature=temperature)

    elif name.lower() == "gigachat":
        if not credentials_gigachat:
            return None
        llm = GigaChat(
            credentials=credentials_gigachat,
            scope=gigachat_scope,
            model="GigaChat",
            temperature=temperature,
            verify_ssl_certs=False,
            ca_bundle_file=ca_bundle_file,
        )

    elif name in gemini_model_list:
        if not google_api_key:
            return None
        kwargs = dict(
            model=name,
            temperature=temperature,
            retries=1,
            request_timeout=30,
        )
        if google_api_key:
            kwargs["api_key"] = google_api_key
        llm = ChatGoogleGenerativeAI(**kwargs)
    
    if llm is not None and structured is not None:
        llm = llm.with_structured_output(structured)

    return llm


def get_response_text(response) -> str:
    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                chunks.append(item["text"])
            else:
                chunks.append(str(item))
        return "".join(chunks).strip()

    return str(content)


def get_concepts():
    with open(Path.cwd().parent / 'ontology.json', 'r', encoding='utf-8') as file:
        ontology = json.load(file)

    concepts = [
        (id, concept.lower())
        for id, concept in ontology['labels'].items()
        if id[0] == 'Q'
    ]

    return concepts

