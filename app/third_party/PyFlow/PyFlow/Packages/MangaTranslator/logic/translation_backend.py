from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .base import NodeLogicError

DEFAULT_API_KEYS_PATH = Path("app/config/api_keys.yaml")


def _load_api_key(api_keys_path: Path, key_name: str) -> str:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise NodeLogicError("Install `pyyaml` to load API keys.") from exc

    if not api_keys_path.exists():
        raise NodeLogicError(f"Missing API keys file: {api_keys_path}")
    try:
        content = api_keys_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        key = (data.get("api_keys") or {}).get(key_name)
    except Exception as exc:
        raise NodeLogicError(f"Failed to read API keys: {exc}") from exc
    if not key:
        raise NodeLogicError(f"API key '{key_name}' not found in {api_keys_path}")
    return key


class TranslationBackend:
    """Together-powered translator without stub fallbacks."""

    def __init__(self, api_keys_path: Path = DEFAULT_API_KEYS_PATH) -> None:
        self.api_keys_path = api_keys_path
        self.system_prompt = (
            "You are a professional manga translator. Translate Japanese text into fluent, natural "
            "English while preserving tone, context, and flow. Return the same JSON array structure "
            "with an added 'translation' field and no extra commentary."
        )

    def translate(self, texts: Iterable[str]) -> List[str]:
        text_list = list(texts)
        if not text_list:
            return []

        api_key = _load_api_key(self.api_keys_path, "together_api_key")
        try:
            from together import Together  # type: ignore
        except Exception as exc:
            raise NodeLogicError("Install `together` to enable translation.") from exc

        try:
            client = Together(api_key=api_key)
        except Exception as exc:
            raise NodeLogicError(f"Together client initialization failed: {exc}") from exc

        batch = self._prepare_batch(text_list)
        user_prompt = json.dumps(batch, ensure_ascii=False, indent=2)

        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_response_text = response.choices[0].message.content
            translated_batch = json.loads(raw_response_text)
            return self._batch_to_list(translated_batch, len(text_list))
        except Exception as exc:
            raise NodeLogicError(f"Translation failed: {exc}") from exc

    # Helpers ------------------------------------------------------------------
    @staticmethod
    def _prepare_batch(text_list: List[str]) -> List[dict]:
        return [{"id": idx, "original": entry} for idx, entry in enumerate(text_list) if str(entry).strip()]

    @staticmethod
    def _batch_to_list(translated_batch: List[dict], desired_size: int) -> List[str]:
        new_list = ["" for _ in range(desired_size)]
        for entry in translated_batch:
            try:
                index = int(entry.get("id", -1))
            except Exception:
                continue
            if 0 <= index < len(new_list):
                new_list[index] = str(entry.get("translation", ""))
        return new_list


class OpenAITranslationBackend:
    """OpenAI-powered translator without stub fallbacks."""

    def __init__(self, api_keys_path: Path = DEFAULT_API_KEYS_PATH) -> None:
        self.api_keys_path = api_keys_path
        self.system_prompt = (
            "You are a professional manga translator. Translate Japanese text into fluent, natural "
            "English while preserving tone, context, and flow. Return the same JSON array structure "
            "with an added 'translation' field and no extra commentary."
        )

    def translate(self, texts: Iterable[str]) -> List[str]:
        text_list = list(texts)
        if not text_list:
            return []

        api_key = _load_api_key(self.api_keys_path, "openai_api_key")
        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:
            raise NodeLogicError("Install `openai` to enable translation.") from exc

        try:
            client = OpenAI(api_key=api_key)
        except Exception as exc:
            raise NodeLogicError(f"OpenAI client initialization failed: {exc}") from exc

        batch = self._prepare_batch(text_list)
        user_prompt = json.dumps(batch, ensure_ascii=False, indent=2)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_response_text = response.choices[0].message.content
            translated_batch = json.loads(raw_response_text)
            return self._batch_to_list(translated_batch, len(text_list))
        except Exception as exc:
            raise NodeLogicError(f"Translation failed: {exc}") from exc

    # Helpers ------------------------------------------------------------------
    @staticmethod
    def _prepare_batch(text_list: List[str]) -> List[dict]:
        return [{"id": idx, "original": entry} for idx, entry in enumerate(text_list) if str(entry).strip()]

    @staticmethod
    def _batch_to_list(translated_batch: List[dict], desired_size: int) -> List[str]:
        new_list = ["" for _ in range(desired_size)]
        for entry in translated_batch:
            try:
                index = int(entry.get("id", -1))
            except Exception:
                continue
            if 0 <= index < len(new_list):
                new_list[index] = str(entry.get("translation", ""))
        return new_list
