"""Stdlib-only HTTP client for the TypeSafe System One endpoint."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .constraints import Budget
from .questions import validate_questions

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
Transport = Callable[[Request, float], tuple[int, bytes]]


class TypeSafeError(RuntimeError):
    pass


class ProviderError(TypeSafeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"TypeSafe returned HTTP {status}: {body}")
        self.status = status
        self.body = body


class ResponseFormatError(TypeSafeError):
    pass


class BudgetRefused(TypeSafeError):
    pass


@dataclass(frozen=True)
class SystemOneResponse:
    model: str
    answers: Mapping[str, Mapping[str, Any]]
    usage: Mapping[str, Any]


def urllib_transport(request: Request, timeout: float) -> tuple[int, bytes]:
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        return error.code, error.read(MAX_RESPONSE_BYTES + 1)
    except URLError as error:
        raise TypeSafeError(f"TypeSafe connection failed: {error.reason}") from error


class TypeSafeClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "jev-latest",
        timeout_seconds: float = 60.0,
        max_attempts: int = 3,
        transport: Transport = urllib_transport,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("TYPESAFE_API_KEY")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.transport = transport
        self.sleep = sleep
        self.clock = clock

    def system_one(
        self, state: Any, questions: Mapping[str, Mapping[str, Any]], budget: Budget
    ) -> SystemOneResponse:
        if not self.api_key:
            raise TypeSafeError("TYPESAFE_API_KEY is not bound")
        payload = json.dumps(
            {"state": state, "questions": validate_questions(questions), "model": self.model}
        ).encode("utf-8")
        request = Request(
            ENDPOINT,
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        started = self.clock()
        response: SystemOneResponse | None = None
        try:
            for attempt in range(self.max_attempts):
                remaining_ms = budget.max_latency_ms - budget.latency_ms - (self.clock() - started) * 1000
                if remaining_ms <= 0:
                    raise BudgetRefused("TypeSafe latency ceiling reached before transport")
                if not budget.reserve_call():
                    raise BudgetRefused("TypeSafe call ceiling reached before transport")
                status, body = self.transport(request, min(self.timeout_seconds, remaining_ms / 1000))
                if status in {429, 529} and attempt + 1 < self.max_attempts:
                    if budget.calls >= budget.max_calls:
                        raise BudgetRefused("TypeSafe call ceiling reached; refusing transport retry")
                    remaining_ms = budget.max_latency_ms - budget.latency_ms - (self.clock() - started) * 1000
                    if remaining_ms <= 0:
                        raise BudgetRefused("TypeSafe latency ceiling reached before retry")
                    self.sleep(min(2**attempt, remaining_ms / 1000))
                    continue
                if not 200 <= status < 300:
                    raise ProviderError(status, body.decode("utf-8", errors="replace"))
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ResponseFormatError("TypeSafe response exceeded 16 MiB")
                try:
                    decoded = json.loads(body)
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise ResponseFormatError("TypeSafe response was not valid JSON") from error
                if not isinstance(decoded, dict) or not isinstance(decoded.get("answers"), dict):
                    raise ResponseFormatError("TypeSafe response lacks an answers map")
                response = SystemOneResponse(
                    model=str(decoded.get("model", self.model)),
                    answers=decoded["answers"],
                    usage=decoded.get("usage", {}),
                )
                break
        finally:
            elapsed_ms = round((self.clock() - started) * 1000)
            within_budget = budget.record_latency(elapsed_ms)
        if not within_budget:
            raise BudgetRefused("TypeSafe latency ceiling reached")
        if response is not None:
            return response
        raise TypeSafeError("TypeSafe request ended without a response")
