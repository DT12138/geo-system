from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
from .schema import Prompt, ScanResult


def compute_weekly_kpi(scans: List[ScanResult], prompts: List[Prompt] | None = None) -> Dict:
    prompts = prompts or []
    prompt_by_id = {p.id: p for p in prompts}

    by_model = defaultdict(list)
    by_bucket = defaultdict(list)

    for s in scans:
        by_model[s.model].append(s)
        bucket = prompt_by_id.get(s.prompt_id).bucket if s.prompt_id in prompt_by_id else "unknown"
        by_bucket[(s.model, bucket)].append(s)

    model_rows = {}
    for m, rows in by_model.items():
        total = len(rows) or 1
        mention = sum(1 for r in rows if r.mentioned)
        citation = sum(1 for r in rows if r.cited)
        rec = sum(1 for r in rows if r.recommended)
        model_rows[m] = {
            "total": total,
            "mention_rate": round(mention / total, 4),
            "citation_rate": round(citation / total, 4),
            "recommendation_rate": round(rec / total, 4),
        }

    bucket_rows = {}
    for (model, bucket), rows in by_bucket.items():
        total = len(rows) or 1
        mention = sum(1 for r in rows if r.mentioned)
        citation = sum(1 for r in rows if r.cited)
        rec = sum(1 for r in rows if r.recommended)
        bucket_rows.setdefault(model, {})[bucket] = {
            "total": total,
            "mention_rate": round(mention / total, 4),
            "citation_rate": round(citation / total, 4),
            "recommendation_rate": round(rec / total, 4),
        }

    return {"models": model_rows, "by_bucket": bucket_rows}


def render_weekly_report(kpi: Dict) -> str:
    lines = ["GEO Weekly Report", "=" * 50, ""]
    for model, row in kpi.get("models", {}).items():
        lines.append(f"Model: {model}")
        lines.append(f"- Total prompts: {row['total']}")
        lines.append(f"- Mention rate: {row['mention_rate']*100:.1f}%")
        lines.append(f"- Citation rate: {row['citation_rate']*100:.1f}%")
        lines.append(f"- Recommendation rate: {row['recommendation_rate']*100:.1f}%")
        lines.append("")

        if model in kpi.get("by_bucket", {}):
            lines.append("  By bucket:")
            for bucket, brow in sorted(kpi["by_bucket"][model].items()):
                lines.append(
                    f"  - {bucket}: mention {brow['mention_rate']*100:.1f}% | "
                    f"citation {brow['citation_rate']*100:.1f}% | "
                    f"recommendation {brow['recommendation_rate']*100:.1f}%"
                )
            lines.append("")
    return "\n".join(lines)
