from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EngagementState:
    """
    Single source of truth for a CI engagement.
    Grows as each node completes. Fed forward into every subsequent node.
    call_log preserves every API call for inspection via harness_inspector.
    """

    # Engagement identity
    engagement_id: str = ""
    client_name: str = ""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Phase 0 — Intake outputs
    technology_description: str = ""
    bd_objectives: str = ""
    named_competitors: list = field(default_factory=list)
    named_personnel: list = field(default_factory=list)
    funding_signals: str = ""
    intake_raw: str = ""

    # Phase 1a — Patent entity identification outputs
    identified_entities: list = field(default_factory=list)
    patent_entity_raw: str = ""

    # Phase 1b — Patent portfolio analysis outputs
    target_entity: str = ""
    issued_patents: list = field(default_factory=list)
    provisional_patents: list = field(default_factory=list)
    patent_gaps: list = field(default_factory=list)
    co_inventors: list = field(default_factory=list)
    patent_analysis_raw: str = ""

    # Phase 2 — Founding team outputs (stub)
    founding_team_risks: list = field(default_factory=list)
    dual_role_flags: list = field(default_factory=list)
    founding_team_raw: str = ""

    # Node call log — every API call recorded here
    call_log: list = field(default_factory=list)

    def log_call(self, node: str, messages_in: list, response_text: str, usage: dict):
        """Record every API call for inspection."""
        self.call_log.append(
            {
                "node": node,
                "timestamp": datetime.now().isoformat(),
                "messages_in": messages_in,
                "response_text": response_text,
                "usage": usage,
            }
        )
