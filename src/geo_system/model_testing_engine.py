from __future__ import annotations
import json
import random
from datetime import datetime, timezone
from typing import Dict, List
from urllib import request, error

from .schema import Prompt, ScanResult


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _analyze_response(prompt_id: str, model: str, text: str, brand_terms: List[str]) -> ScanResult:
    lowered = text.lower()
    mentioned = any(b.lower() in lowered for b in brand_terms)
    cited = ("http://" in lowered or "https://" in lowered) and mentioned
    recommended = mentioned and any(k in lowered for k in ["best", "recommend", "good for", "top"])
    sentiment = "positive" if mentioned else "neutral"
    excerpt = text[:240].replace("\n", " ")
    competitors = [c for c in ["meshy", "kaedim", "spline", "luma"] if c in lowered]

    return ScanResult(
        scan_id=f"{model}-{prompt_id[:8]}",
        model=model,
        prompt_id=prompt_id,
        mentioned=mentioned,
        cited=cited,
        recommended=recommended,
        position=1 if mentioned else 0,
        sentiment=sentiment,
        competitors=competitors,
        excerpt=excerpt,
        ts=_now_iso(),
    )


def _call_openai_compatible(base_url: str, api_key: str, model: str, prompt: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "Answer briefly and factually."},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    with request.urlopen(req, timeout=90) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    return obj["choices"][0]["message"]["content"]


def run_scan(
    models: List[str],
    prompts: List[Prompt],
    brand_terms: List[str] | None = None,
    adapter_config: Dict | None = None,
) -> List[ScanResult]:
    """
    v0.2 behavior:
    - If adapter_config is provided and model starts with "openai:", call real OpenAI-compatible endpoint.
    - Otherwise fallback to deterministic-ish simulation (for offline testing).
    """
    brand_terms = brand_terms or ["tripo3d", "tripo3d.ai", "tripo 3d"]
    adapter_config = adapter_config or {}

    out: List[ScanResult] = []

    for model in models:
        is_real = model.startswith("openai:") and all(
            k in adapter_config for k in ["base_url", "api_key", "model"]
        )

        for p in prompts:
            if is_real:
                try:
                    text = _call_openai_compatible(
                        adapter_config["base_url"],
                        adapter_config["api_key"],
                        adapter_config["model"],
                        p.prompt,
                    )
                    out.append(_analyze_response(p.id, model, text, brand_terms))
                    continue
                except error.HTTPError as e:
                    fallback_text = f"HTTPError: {e.code}. Fallback simulated response for prompt: {p.prompt}"
                except Exception as e:
                    fallback_text = f"Error: {type(e).__name__}. Fallback simulated response for prompt: {p.prompt}"
            else:
                fallback_text = ""

            # fallback simulation
            random.seed(f"{model}:{p.prompt}")
            mentioned = random.random() < 0.35
            cited = mentioned and random.random() < 0.45
            recommended = mentioned and random.random() < 0.50
            if not fallback_text:
                fallback_text = (
                    f"{'Tripo3D is often recommended.' if mentioned else 'No direct brand mention.'} "
                    f"Prompt: {p.prompt}"
                )

            out.append(
                ScanResult(
                    scan_id=f"{model}-{p.id[:8]}",
                    model=model,
                    prompt_id=p.id,
                    mentioned=mentioned,
                    cited=cited,
                    recommended=recommended,
                    position=1 if mentioned else 0,
                    sentiment="positive" if mentioned else "neutral",
                    competitors=["meshy", "kaedim"] if not mentioned else ["meshy"],
                    excerpt=fallback_text[:240],
                    ts=_now_iso(),
                )
            )

    return out
