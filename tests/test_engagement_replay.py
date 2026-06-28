"""
Replay the engagement with the prototype chain.
Validates harness output against known engagement inputs.
"""

import sys

from loguru import logger

sys.path.insert(0, "..")
from deepvoxel.application.runner import run_engagement

ENGAGEMENT_SLUG = "example"


def test_intake_extraction():
    state = run_engagement(ENGAGEMENT_SLUG)
    assert state.technology_description, "Technology description empty"
    assert len(state.named_personnel) > 0, "No personnel extracted"
    logger.info(f"Technology: {state.technology_description[:200]}")
    logger.info(f"Personnel:  {state.named_personnel}")
    logger.info(f"Objectives: {state.bd_objectives[:200]}")


def test_patent_chain():
    state = run_engagement(ENGAGEMENT_SLUG)
    assert state.patent_entity_raw, "Patent entity sweep empty"
    assert state.patent_analysis_raw, "Patent analysis empty"
    assert len(state.call_log) >= 3, "Expected at least 3 API calls"
    logger.info(f"Entity sweep ({len(state.patent_entity_raw)} chars)")
    logger.info(state.patent_entity_raw[:400])
    logger.info(f"Portfolio analysis ({len(state.patent_analysis_raw)} chars)")
    logger.info(state.patent_analysis_raw[:400])


def test_call_log():
    state = run_engagement(ENGAGEMENT_SLUG)
    nodes = [c["node"] for c in state.call_log]
    assert "node_00_intake" in nodes
    assert "node_01a_patent_identify" in nodes
    assert "node_01b_patent_analyze" in nodes
    total_tokens = sum(
        c["usage"]["input_tokens"] + c["usage"]["output_tokens"] for c in state.call_log
    )
    logger.info(f"Nodes executed: {nodes}")
    logger.info(f"Total tokens:   {total_tokens}")


if __name__ == "__main__":
    test_intake_extraction()
    test_patent_chain()
    test_call_log()
