"""Offline request construction and explicitly authorized Answers calls."""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT = "https://api.context.dev/v1/web/answers"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
Transport = Callable[[Request, float], tuple[int, Mapping[str, str], bytes]]


class AnswersError(RuntimeError):
    pass


class AnswersResponseError(AnswersError):
    pass


@dataclass(frozen=True)
class Answer:
    json_content: dict[str, Any]
    sources: list[str]
    partial: bool | None
    credits_consumed: int | None
    credits_remaining: int | None
    credits_used_header: int | None


def _example(value: Any, depth: int, seen: set[int], count: list[int]) -> None:
    if depth > 8:
        raise ValueError("json_format exceeds 8 levels")
    count[0] += 1
    if count[0] > 500:
        raise ValueError("json_format exceeds 500 values")
    if isinstance(value, (dict, list)):
        if id(value) in seen:
            raise ValueError("json_format contains a cycle")
        seen.add(id(value))
        if isinstance(value, dict):
            if any(not isinstance(key, str) for key in value):
                raise ValueError("json_format keys must be strings")
            for child in value.values():
                _example(child, depth + 1, seen, count)
        else:
            for child in value:
                _example(child, depth + 1, seen, count)
        seen.remove(id(value))
    elif value is None or isinstance(value, (str, bool)):
        return
    elif type(value) is int or isinstance(value, float) and math.isfinite(value):
        return
    else:
        raise ValueError("json_format must contain finite JSON values")


def build_request(
    task: str,
    *,
    json_format: dict[str, Any] | None = None,
    mode: str = "fast",
    timeout_opts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate and return an offline JSON-ready payload; this never reads a key."""
    if not isinstance(task, str) or not task.strip() or not 1 <= len(task) <= 2000:
        raise ValueError("task must have 1 to 2000 characters")
    if mode not in ("fast", "ultra"):
        raise ValueError("mode must be fast or ultra")
    payload: dict[str, Any] = {"task": task, "mode": mode}
    if json_format is not None:
        if not isinstance(json_format, dict):
            raise ValueError("json_format must be an example object")
        _example(json_format, 1, set(), [0])
        if len(json.dumps(json_format, ensure_ascii=False, allow_nan=False)) > 16000:
            raise ValueError("json_format exceeds 16000 characters")
        payload["json_format"] = json.loads(json.dumps(json_format, allow_nan=False))
    if timeout_opts is not None:
        if not isinstance(timeout_opts, Mapping) or set(timeout_opts) - {"milliseconds", "behavior"}:
            raise ValueError("timeout_opts must contain only milliseconds and behavior")
        ms = timeout_opts.get("milliseconds")
        behavior = timeout_opts.get("behavior", "fail")
        if type(ms) is not int or not 1000 <= ms <= 300000:
            raise ValueError("timeout_opts milliseconds must be an integer from 1000 to 300000")
        if behavior not in ("fail", "return-partial") or not isinstance(behavior, str):
            raise ValueError("timeout_opts behavior must be fail or return-partial")
        payload["timeoutOpts"] = {"milliseconds": ms, "behavior": behavior}
    return payload


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request: Request, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


def urllib_transport(request: Request, timeout: float) -> tuple[int, Mapping[str, str], bytes]:
    try:
        with build_opener(_NoRedirect()).open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        error.close()
        return error.code, dict(error.headers.items()) if error.headers else {}, b""


def _credit(value: Any) -> int:
    if type(value) is not int or value < 0:
        raise AnswersResponseError("Answers returned invalid credit metadata")
    return value


def _invalid_constant(value: str) -> None:
    raise ValueError("Non-finite JSON value")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON value")
    return number


class ContextAnswers:
    def __init__(self, *, transport: Transport = urllib_transport) -> None:
        self.transport = transport

    def answer(
        self,
        task: str,
        *,
        json_format: dict[str, Any] | None = None,
        mode: str = "fast",
        timeout_opts: Mapping[str, Any] | None = None,
        live: bool = False,
    ) -> Answer:
        payload = build_request(task, json_format=json_format, mode=mode, timeout_opts=timeout_opts)
        if live is not True or os.getenv("CONFIRM") != "send":
            raise AnswersError("Live Answers call requires live=True and current CONFIRM=send")
        key = os.getenv("CONTEXT_DEV_API_KEY")
        if not key or any(ord(char) < 33 or ord(char) == 127 for char in key):
            raise AnswersError("CONTEXT_DEV_API_KEY is not bound or is invalid")
        request = Request(
            ENDPOINT,
            data=json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        research_seconds = 30 if mode == "fast" else 50
        deadline = min(payload["timeoutOpts"]["milliseconds"] / 1000, research_seconds) if "timeoutOpts" in payload else research_seconds
        try:
            status, headers, body = self.transport(request, deadline + 15)
        except Exception:
            raise AnswersError("Answers transport failed; billing status unknown, no retry") from None
        if type(status) is not int or not 200 <= status < 300:
            safe_status = status if type(status) is int and 100 <= status <= 599 else "unknown"
            raise AnswersError(f"Answers HTTP {safe_status}; billing status unknown, no retry")
        if not isinstance(body, bytes) or len(body) > MAX_RESPONSE_BYTES:
            raise AnswersResponseError("Answers response exceeds limit or is not bytes")
        try:
            decoded = json.loads(body, parse_constant=_invalid_constant, parse_float=_finite_float)
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise AnswersResponseError("Answers response is not valid JSON") from None
        if not isinstance(decoded, dict) or not isinstance(decoded.get("json_content"), dict):
            raise AnswersResponseError("Answers response lacks json_content object")
        sources = decoded.get("sources")
        if not isinstance(sources, list):
            raise AnswersResponseError("Answers response has invalid sources")
        for source in sources:
            try:
                if not isinstance(source, str) or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in source):
                    raise ValueError
                url = urlsplit(source)
                if url.scheme not in ("http", "https") or not url.hostname or url.username is not None or url.password is not None:
                    raise ValueError
                if url.port is not None and not 1 <= url.port <= 65535:
                    raise ValueError
            except ValueError:
                raise AnswersResponseError("Answers response has invalid sources") from None
        partial = decoded.get("partial")
        if "partial" in decoded and type(partial) is not bool:
            raise AnswersResponseError("Answers response has invalid partial marker")
        metadata = decoded.get("key_metadata")
        if "key_metadata" in decoded and not isinstance(metadata, dict):
            raise AnswersResponseError("Answers returned invalid credit metadata")
        metadata = metadata or {}
        consumed = _credit(metadata["credits_consumed"]) if "credits_consumed" in metadata else None
        remaining = _credit(metadata["credits_remaining"]) if "credits_remaining" in metadata else None
        if not isinstance(headers, Mapping) or any(not isinstance(name, str) for name in headers):
            raise AnswersResponseError("Answers returned invalid headers")
        header = next((value for name, value in headers.items() if name.lower() == "x-credits-used"), None)
        if header is not None and (not isinstance(header, str) or not header.isascii() or not header.isdecimal() or len(header) > 20):
            raise AnswersResponseError("Answers returned invalid credit header")
        return Answer(decoded["json_content"], sources, partial, consumed, remaining,
                      int(header) if header is not None else None)
