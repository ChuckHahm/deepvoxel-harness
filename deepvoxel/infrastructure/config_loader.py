from pathlib import Path

import yaml
from loguru import logger

from deepvoxel.domain.engagement import EngagementState

CONFIG_DIR = Path(__file__).parent.parent.parent / "configs" / "engagements"


def load_engagement(slug: str) -> dict:
    config_path = CONFIG_DIR / f"{slug}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"No engagement config at {config_path}\n"
            f"Copy configs/template.yaml → configs/engagements/{slug}.yaml"
        )
    with open(config_path) as f:
        return yaml.safe_load(f)


def seed_state(slug: str) -> tuple[EngagementState, dict]:
    cfg = load_engagement(slug)
    state = EngagementState(
        engagement_id=cfg.get("engagement_id", slug),
        client_name=cfg.get("client_name", ""),
        technology_description=cfg.get("technology_description", ""),
        bd_objectives=cfg.get("bd_objectives", ""),
        named_personnel=[p["name"] for p in cfg.get("key_personnel", [])],
        target_entity=cfg.get("target_entity_hint", ""),
    )
    transcript_path = cfg.get("transcript_path")
    if transcript_path:
        t_path = Path(transcript_path)
        if t_path.exists():
            state.intake_raw = t_path.read_text()
            logger.info(f"Transcript loaded: {t_path}")
        else:
            logger.warning(f"Transcript path not found: {t_path}")
    return state, cfg
