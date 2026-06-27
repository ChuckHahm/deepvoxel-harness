from loguru import logger

from deepvoxel.application.nodes import node_00_intake, node_01_patents
from deepvoxel.domain.engagement import EngagementState
from deepvoxel.infrastructure.anthropic_client import get_client
from deepvoxel.infrastructure.config_loader import seed_state


def run_engagement(engagement_slug: str) -> EngagementState:
    """
    Run the CI engagement chain for a given engagement slug.
    Loads all client-specific inputs from configs/engagements/<slug>.yaml.
    """
    client = get_client()
    state, cfg = seed_state(engagement_slug)

    logger.info(f"Engagement: {state.engagement_id} | {state.client_name}")
    logger.info(f"Vertical:   {cfg.get('vertical', 'unknown')}")

    logger.info("Phase 0 — Intake")
    if state.intake_raw:
        state = node_00_intake.run(state, state.intake_raw, client)
    else:
        logger.warning("No transcript found — seeding from config fields only")

    logger.info("Phase 1 — Patent analysis")
    state = node_01_patents.run(state, client)

    total_tokens = sum(
        c["usage"]["input_tokens"] + c["usage"]["output_tokens"] for c in state.call_log
    )
    logger.success(f"Chain complete — {len(state.call_log)} API calls | {total_tokens} tokens")
    return state
