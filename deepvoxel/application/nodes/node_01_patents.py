from pathlib import Path

import anthropic
from loguru import logger

from deepvoxel.domain.engagement import EngagementState

PROMPTS = Path(__file__).parent.parent / "prompts"


def run(state: EngagementState, client: anthropic.Anthropic) -> EngagementState:
    """Phase 1: Two-step patent analysis."""
    state = _step_1a(state, client)
    state = _step_1b(state, client)
    return state


def _step_1a(state: EngagementState, client: anthropic.Anthropic) -> EngagementState:
    """Blind entity identification from technology description only."""
    template = (PROMPTS / "patents_identify.md").read_text()
    prompt = template.replace("{technology_description}", state.technology_description)
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2048, messages=messages
    )
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    state.log_call("node_01a_patent_identify", messages, text, usage)
    state.patent_entity_raw = text
    logger.info(f"Patent entity sweep complete ({len(text)} chars)")
    return state


def _step_1b(state: EngagementState, client: anthropic.Anthropic) -> EngagementState:
    """Deep portfolio analysis — 1a output feeds 1b input."""
    template = (PROMPTS / "patents_analyze.md").read_text()
    prompt = (
        template.replace("{target_entity}", state.target_entity or "[entity from step 1a]")
        .replace("{patent_entity_raw}", state.patent_entity_raw)
        .replace("{technology_description}", state.technology_description)
    )
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2048, messages=messages
    )
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    state.log_call("node_01b_patent_analyze", messages, text, usage)
    state.patent_analysis_raw = text
    logger.info(f"Patent analysis complete ({len(text)} chars)")
    return state
