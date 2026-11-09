"""Restricted Deepline metadata and Play-run HTTP interface."""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE_URL = "https://code.deepline.com"
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_REQUEST_BYTES = 1024 * 1024
MAX_POLLS = 20
MAX_DEADLINE_SECONDS = 120.0
NONTERMINAL = frozenset({"queued", "running", "waiting"})
TERMINAL = frozenset({"completed", "failed", "cancelled"})
Transport = Callable[[Request, float], tuple[int, bytes]]


class DeeplineError(RuntimeError):
    pass


class ResponseFormatError(DeeplineError):
    pass


class RunLimitError(DeeplineError):
    pass


@dataclass(frozen=True)
class PreparedPlay:
    name: str
    body: bytes


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def urllib_transport(request: Request, timeout: float) -> tuple[int, bytes]:
    try:
        with build_opener(_NoRedirect).open(request, timeout=timeout) as response:
            return response.status, response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        error.close()
        return error.code, b""


def _identifier(value: str, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 2048
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError(f"Invalid {label}")
    return value


def _positive_number(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"Invalid {label}")
    return float(value)


def _invalid_constant(value: str) -> None:
    raise ValueError("Non-finite JSON value")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON value")
    return number


def prepare_play(name: str, input: Mapping[str, Any]) -> PreparedPlay:
    """Build a Play request without reading credentials or contacting Deepline."""
    _identifier(name, "Play name")
    if not isinstance(input, Mapping):
        raise ValueError("Play input must be an object")
    try:
        body = json.dumps({"name": name, "input": input}, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError):
        raise ValueError("Play input must be finite JSON data") from None
    if len(body) > MAX_REQUEST_BYTES:
        raise ValueError("Play request exceeds size limit")
    return PreparedPlay(name, body)


class DeeplineClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
        transport: Transport = urllib_transport,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.api_key = api_key
        self.timeout_seconds = _positive_number(timeout_seconds, "request timeout")
        self.transport = transport
        self.clock = clock
        self.sleep = sleep

    def _request(self, method: str, path: str, *, body: bytes | None = None, timeout: float | None = None) -> dict[str, Any]:
        key = self.api_key if self.api_key is not None else os.getenv("DEEPLINE_API_KEY")
        if not key or not isinstance(key, str) or any(ord(char) < 33 or ord(char) == 127 for char in key):
            raise DeeplineError("DEEPLINE_API_KEY is not safely bound")
        headers = {"Authorization": f"Bearer {key}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(BASE_URL + path, data=body, headers=headers, method=method)
        try:
            status, response = self.transport(request, self.timeout_seconds if timeout is None else timeout)
        except Exception:
            raise DeeplineError("Deepline transport failed; outcome may be unknown") from None
        if not isinstance(status, int) or isinstance(status, bool) or not 200 <= status < 300:
            raise DeeplineError("Deepline request did not succeed; outcome may be unknown")
        if not isinstance(response, bytes) or len(response) > MAX_RESPONSE_BYTES:
            raise ResponseFormatError("Deepline response exceeded limits or was not bytes")
        try:
            package = json.loads(response, parse_constant=_invalid_constant, parse_float=_finite_float)
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise ResponseFormatError("Deepline response was not valid JSON") from None
        if not isinstance(package, dict):
            raise ResponseFormatError("Deepline response was not an object")
        return package

    def inspect_tool(self, tool_id: str) -> dict[str, Any]:
        """Read a tool's non-executing metadata; do not infer approval from it."""
        _identifier(tool_id, "tool ID")
        metadata = self._request("GET", f"/api/v2/integrations/{quote(tool_id, safe='')}/get")
        if not isinstance(metadata.get("inputSchema"), dict):
            raise ResponseFormatError("Deepline tool metadata lacks an input schema")
        return metadata

    def run_play(self, prepared: PreparedPlay, *, live: bool = False) -> dict[str, Any]:
        """Start one paid Play only after an explicit live confirmation."""
        if not isinstance(prepared, PreparedPlay):
            raise ValueError("Expected a prepared Play")
        if not isinstance(prepared.body, bytes) or len(prepared.body) > MAX_REQUEST_BYTES:
            raise ValueError("Invalid prepared Play body")
        try:
            payload = json.loads(prepared.body, parse_constant=_invalid_constant, parse_float=_finite_float)
            if not isinstance(payload, dict) or set(payload) != {"name", "input"}:
                raise ValueError
            validated = prepare_play(payload["name"], payload["input"])
            if validated.name != prepared.name:
                raise ValueError
        except (ValueError, TypeError, UnicodeDecodeError, RecursionError):
            raise ValueError("Invalid prepared Play body") from None
        if live is not True or os.getenv("CONFIRM") != "send":
            raise DeeplineError("Paid Play requires live=True and current CONFIRM=send")
        package = self._request("POST", "/api/v2/plays/run", body=validated.body)
        self._run(package)
        return package

    @staticmethod
    def _run(package: Mapping[str, Any], expected_id: str | None = None) -> str:
        if type(package.get("schemaVersion")) is not int or package["schemaVersion"] != 1 or package.get("kind") != "play_run":
            raise ResponseFormatError("Deepline response is not a version 1 play_run package")
        run = package.get("run")
        if not isinstance(run, dict):
            raise ResponseFormatError("Deepline response lacks a run")
        try:
            run_id = _identifier(run.get("id"), "run ID")
        except ValueError:
            raise ResponseFormatError("Deepline response has an invalid run ID") from None
        if expected_id is not None and run_id != expected_id:
            raise ResponseFormatError("Deepline response has a different run ID")
        status = run.get("status")
        if not isinstance(status, str) or status not in NONTERMINAL | TERMINAL:
            raise ResponseFormatError("Deepline response has an unknown run status")
        return status

    def get_run(self, run_id: str, *, timeout: float | None = None) -> dict[str, Any]:
        """Read one full package for an existing run, preserving outputs for review."""
        _identifier(run_id, "run ID")
        if timeout is not None:
            _positive_number(timeout, "request timeout")
        package = self._request("GET", f"/api/v2/runs/{quote(run_id, safe='')}?full=true", timeout=timeout)
        self._run(package, run_id)
        return package

    def poll_run(
        self,
        run_id: str,
        *,
        max_polls: int = 10,
        deadline_seconds: float = 60.0,
        interval_seconds: float = 1.0,
    ) -> dict[str, Any]:
        """Poll an existing run within both a hard call cap and a total deadline."""
        _identifier(run_id, "run ID")
        if isinstance(max_polls, bool) or not isinstance(max_polls, int) or not 1 <= max_polls <= MAX_POLLS:
            raise ValueError("Invalid poll count")
        deadline_seconds = _positive_number(deadline_seconds, "poll deadline")
        if deadline_seconds > MAX_DEADLINE_SECONDS:
            raise ValueError("Poll deadline exceeds hard limit")
        if isinstance(interval_seconds, bool) or not isinstance(interval_seconds, (int, float)) or not math.isfinite(interval_seconds) or interval_seconds < 0:
            raise ValueError("Invalid poll interval")
        deadline = self.clock() + deadline_seconds
        for attempt in range(max_polls):
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise RunLimitError("Deepline poll deadline reached")
            package = self.get_run(run_id, timeout=min(self.timeout_seconds, remaining))
            if self.clock() >= deadline:
                raise RunLimitError("Deepline poll deadline reached")
            if self._run(package) in TERMINAL:
                return package
            if attempt + 1 < max_polls:
                remaining = deadline - self.clock()
                if remaining <= 0:
                    raise RunLimitError("Deepline poll deadline reached")
                self.sleep(min(interval_seconds, remaining))
        raise RunLimitError("Deepline poll count reached")
