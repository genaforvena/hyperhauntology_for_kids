"""One function to talk to a model. stdlib only, no SDKs.

A provider is a URL, a header and a way to dig the text back out. Adding one
should be three lines in PROVIDERS, not a class hierarchy.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from . import __version__


class ProviderError(RuntimeError):
    """The call did not produce an answer. Never confuse this with an empty answer."""


@dataclass(frozen=True)
class Reply:
    text: str
    latency_s: float
    raw_finish: str | None
    # Reasoning models return their chain separately. It is kept on the tape as
    # evidence and NEVER graded as the answer: a model whose whole budget went
    # into thinking returns an empty `text`, and scoring that as an answer turns
    # silence into an observation.
    thinking: str | None = None


def _post(url: str, payload: dict, headers: dict, timeout: float) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    # urllib's default UA is "Python-urllib/3.x", which Cloudflare in front of at
    # least one provider rejects with a 403 (error 1010) while the identical
    # request from curl returns 200. A provider outage and a blocked user agent
    # are not the same fault and must not look alike.
    req.add_header("User-Agent", f"hyperhauntology-for-kids/{__version__} (+python-urllib)")
    for k, v in headers.items():
        req.add_header(k, v)
    # Bypass any configured proxy for LOCAL endpoints only. A machine that
    # exports HTTP(S)_PROXY globally would otherwise send 127.0.0.1 through it;
    # disabling the proxy for every host instead would break a remote API that
    # legitimately needs one.
    host = urllib.parse.urlsplit(url).hostname or ""
    if host in ("127.0.0.1", "localhost", "::1"):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    else:
        opener = urllib.request.build_opener()
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _groq(messages, model, temperature, seed, timeout):
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise ProviderError("GROQ_API_KEY is not set")
    payload = {"model": model, "messages": messages, "temperature": temperature}
    if seed is not None:
        payload["seed"] = seed
    out = _post(
        "https://api.groq.com/openai/v1/chat/completions",
        payload,
        {"Authorization": f"Bearer {key}"},
        timeout,
    )
    choice = out["choices"][0]
    msg = choice["message"]
    return msg["content"] or "", choice.get("finish_reason"), msg.get("reasoning_content")


def _openai_compatible(base_env, key_env):
    def call(messages, model, temperature, seed, timeout):
        base = os.environ.get(base_env, "").strip()
        if not base:
            raise ProviderError(f"{base_env} is not set")
        key = os.environ.get(key_env, "").strip()
        payload = {"model": model, "messages": messages, "temperature": temperature}
        if seed is not None:
            payload["seed"] = seed
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        out = _post(base.rstrip("/") + "/chat/completions", payload, headers, timeout)
        choice = out["choices"][0]
        msg = choice["message"]
        return msg["content"] or "", choice.get("finish_reason"), msg.get("reasoning_content")

    return call


def _ollama(messages, model, temperature, seed, timeout):
    base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
    if not base.startswith("http"):
        base = "http://" + base
    opts = {"temperature": temperature}
    if seed is not None:
        opts["seed"] = seed
    out = _post(
        base.rstrip("/") + "/api/chat",
        {"model": model, "messages": messages, "stream": False, "options": opts},
        {},
        timeout,
    )
    msg = out["message"]
    return msg["content"] or "", out.get("done_reason"), msg.get("thinking")


PROVIDERS = {
    "groq": _groq,
    "ollama": _ollama,
    "openai": _openai_compatible("OPENAI_BASE_URL", "OPENAI_API_KEY"),
}


def chat(
    messages: list[dict],
    model: str,
    provider: str = "ollama",
    temperature: float = 0.0,
    seed: int | None = 7,
    timeout: float = 120.0,
    retries: int = 2,
) -> Reply:
    """Send `messages`, get one Reply back, or raise ProviderError.

    Raising rather than returning "" is deliberate: a failed call and a model
    that answered with nothing are different facts, and every detector
    downstream renders the first as `na` and the second as a real observation.
    """
    fn = PROVIDERS.get(provider)
    if fn is None:
        raise ProviderError(f"unknown provider {provider!r}; have {sorted(PROVIDERS)}")
    last = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            text, finish, thinking = fn(messages, model, temperature, seed, timeout)
            return Reply(
                text=text,
                latency_s=round(time.time() - t0, 3),
                raw_finish=finish,
                thinking=thinking,
            )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:400]
            last = ProviderError(f"HTTP {exc.code} from {provider}: {detail}")
            if exc.code in (400, 401, 403, 404):
                break  # not transient; retrying just burns quota
            if exc.code == 429:
                # Honour the server's own number. Guessing a backoff against a
                # rate limiter turns a delay into a truncated experiment: the
                # first live groq run lost six derail turns to 429 and scored
                # two-turn conversations as derailments.
                wait = exc.headers.get("retry-after") if exc.headers else None
                try:
                    delay = min(float(wait), 60.0)
                except (TypeError, ValueError):
                    delay = 5.0 * (attempt + 1)
                if attempt < retries:
                    time.sleep(delay)
                    continue
        except Exception as exc:  # noqa: BLE001 - surfaced verbatim below
            last = ProviderError(f"{type(exc).__name__}: {exc}")
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise last or ProviderError("no attempt was made")
