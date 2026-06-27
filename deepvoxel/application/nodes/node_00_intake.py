from pathlib import Path

import anthropic
from loguru import logger

from deepvoxel.domain.engagement import EngagementState

PROMPT = (Path(__file__).parent.parent / "prompts" / "intake.md").read_text

_HEADERS = [
    "TECHNOLOGY:",
    "BD_OBJECTIVES:",
    "NAMED_COMPETITORS:",
    "NAMED_PERSONNEL:",
    "FUNDING_SIGNALS:",
    "ANOMALIES:",
]


def run(state: EngagementState, transcript: str, client: anthropic.Anthropic) -> EngagementState:
    """Phase 0: Parse intake transcript into structured seed state."""
    prompt = PROMPT().replace("{transcript}", transcript)
    messages = [{"role": "user", "content": prompt}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=messages,
    )
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    state.log_call("node_00_intake", messages, text, usage)
    state.intake_raw = text

    state.technology_description = _section(text, "TECHNOLOGY")
    state.bd_objectives = _section(text, "BD_OBJECTIVES")
    state.funding_signals = _section(text, "FUNDING_SIGNALS")

    raw_competitors = _section(text, "NAMED_COMPETITORS")
    state.named_competitors = [
        c.strip("- ").strip() for c in raw_competitors.splitlines() if c.strip()
    ]
    raw_personnel = _section(text, "NAMED_PERSONNEL")
    state.named_personnel = [
        p.strip("- ").strip() for p in raw_personnel.splitlines() if p.strip()
    ]

    logger.info(f"Intake complete — personnel: {state.named_personnel}")
    return state


def _section(text: str, name: str) -> str:
    lines = text.splitlines()
    collecting, result = False, []
    for line in lines:
        if name in line and ":" in line:
            collecting = True
            continue
        if collecting:
            if any(h in line for h in _HEADERS):
                break
            result.append(line)
    return "\n".join(result).strip()
