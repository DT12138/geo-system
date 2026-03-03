from __future__ import annotations
import re
import uuid
from collections import defaultdict
from typing import Dict, List
from .schema import Prompt


def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def _bucket_for_prompt(text: str) -> str:
    t = text.lower()
    if "vs" in t or "alternative" in t or "compare" in t:
        return "comparison"
    if any(k in t for k in ["best", "which", "top", "recommend"]):
        return "decision"
    if any(k in t for k in ["what is", "how", "why", "guide", "explain"]):
        return "info"
    if any(k in t for k in ["for ", "use case", "workflow"]):
        return "usecase"
    return "info"


def generate_prompts(seed_terms: List[str], count: int = 100) -> List[Prompt]:
    templates = [
        "What is {x}?",
        "How does {x} work?",
        "Why use {x}?",
        "Best tools for {x}",
        "{x} alternatives",
        "{x} vs competitors",
        "Is {x} good for game assets?",
        "Is {x} good for e-commerce?",
        "Which AI can do {x}?",
        "How to choose {x} tools?",
    ]

    prompts: List[Prompt] = []
    i = 0
    while len(prompts) < count:
        term = seed_terms[i % len(seed_terms)].strip()
        tpl = templates[i % len(templates)]
        text = tpl.format(x=term)
        bucket = _bucket_for_prompt(text)
        prompts.append(
            Prompt(
                id=str(uuid.uuid4()),
                prompt=text,
                bucket=bucket,
                intent_type=bucket,
                stage="awareness" if bucket == "info" else "consideration",
                priority="P0" if len(prompts) < 30 else "P1",
            )
        )
        i += 1
    return prompts


def dedupe_prompts(prompts: List[Prompt]) -> List[Prompt]:
    seen = set()
    out: List[Prompt] = []
    for p in prompts:
        key = _normalize(p.prompt)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def cluster_prompts(prompts: List[Prompt]) -> Dict[str, List[Prompt]]:
    clusters: Dict[str, List[Prompt]] = defaultdict(list)
    for p in prompts:
        clusters[p.bucket].append(p)
    return dict(clusters)
