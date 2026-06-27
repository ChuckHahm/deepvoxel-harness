# deepVoxel LLM Harness — Consolidated Build Plan
**Version:** 1.0
**Date:** 2026-06-27
**Status:** Ready for Claude Code handoff

---

## Context and Motivation

This plan productionalizes the LipoNexus CI engagement methodology as a
chained LLM harness. The LipoNexus report was produced manually via the
claude.ai chat interface and validated the core approach: structured
multi-step OSINT research with LLM synthesis at each layer produces
unexpected, high-value findings that justify $8K–$25K report pricing.

The harness encodes that methodology as explicit chained API calls with
a shared state object, making it repeatable across engagements without
rebuilding from scratch each time.

### Design Principles
- No LangChain or similar frameworks — raw Anthropic SDK only
- Transparent data flow — every API call inspectable via message inspector
- Domain-Driven Design structure — borrowed from LLM Engineer's Handbook
- uv for package management — current standard, no conda friction
- Client data never in git — engagement configs are gitignored YAML files
- Exploratory phases (patents, founding team) preserve loose prompt structure
  to allow unexpected findings to surface

---

## Architecture Overview

### DDD Layer Structure
```
deepvoxel/infrastructure/  →  deepvoxel/application/  →  deepvoxel/domain/
(Anthropic client,             (runner, nodes)             (EngagementState,
 config loader, .env)                                       domain entities)
```

**Import direction is strict:** domain has zero external imports.
application imports from domain + infrastructure.
infrastructure wraps all external dependencies.

### Chain Mechanics
```
Engagement YAML config
        ↓
  EngagementState (seed)
        ↓
  node_00_intake      → state.technology_description, named_personnel, ...
        ↓
  node_01a_patents    → state.patent_entity_raw
        ↓
  node_01b_patents    → state.patent_analysis_raw  (feeds from 1a)
        ↓
  node_02_founding    → state.founding_team_risks  (stub in prototype)
        ↓
  [phases 3-6 future] → competitive landscape, grants, investors, deliverables
        ↓
  state.call_log      → full API call history for inspector
```

---

## Project Structure

```
~/GitClones/deepvoxel-harness/
│
├── CLAUDE.md                        ← harness context for Claude Code
├── .python-version                  ← contains: 3.11
├── .env.example                     ← tracked: shows required keys, no values
├── .env                             ← gitignored: actual API keys
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                   ← uv + Poe tasks + ruff config
├── uv.lock                          ← replaces poetry.lock
├── ruff.toml
│
├── deepvoxel/                       ← main package
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── engagement.py            ← EngagementState dataclass
│   ├── application/
│   │   ├── __init__.py
│   │   ├── runner.py                ← chain orchestrator
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── node_00_intake.py
│   │       ├── node_01_patents.py
│   │       └── node_02_founding_team.py   ← stub only in prototype
│   └── infrastructure/
│       ├── __init__.py
│       ├── anthropic_client.py
│       └── config_loader.py
│
├── configs/
│   ├── template.yaml                ← tracked: blank engagement template
│   └── engagements/
│       └── .gitkeep                 ← dir tracked, *.yaml gitignored
│
├── pipelines/
│   └── ci_report_pipeline.py        ← pipeline entry point
│
├── steps/
│   ├── __init__.py
│   ├── intake_step.py
│   └── patent_step.py
│
├── tools/
│   ├── run.py                       ← CLI entry point
│   └── inspect.py                   ← launches inspector on port 8011
│
├── inspector/
│   └── harness_inspector.py         ← Plotly Dash chain inspector
│
├── tests/
│   └── test_engagement_replay.py    ← LipoNexus replay validation
│
└── outputs/
    └── .gitkeep
```

---

## Build Sequence

Hand these to Claude Code as three separate files in order.

---

### FILE 1 — BOOTSTRAP.md
*Steps 1–5: Project init, structure, config files. No Python logic.*

#### Step 1 — Prerequisites and Init

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version

# Initialize project
cd ~/GitClones
uv init deepvoxel-harness
cd deepvoxel-harness
uv python pin 3.11
uv venv
source .venv/bin/activate
```

#### Step 2 — Directory Structure

```bash
mkdir -p deepvoxel/domain
mkdir -p deepvoxel/application/nodes
mkdir -p deepvoxel/infrastructure
mkdir -p configs/engagements
mkdir -p pipelines steps tools inspector tests outputs

touch deepvoxel/__init__.py
touch deepvoxel/domain/__init__.py
touch deepvoxel/application/__init__.py
touch deepvoxel/application/nodes/__init__.py
touch deepvoxel/infrastructure/__init__.py
touch steps/__init__.py
touch configs/engagements/.gitkeep
touch outputs/.gitkeep
```

#### Step 3 — `pyproject.toml`

```toml
[project]
name = "deepvoxel-harness"
version = "0.1.0"
description = "deepVoxel CI Report Generation Harness"
authors = [{ name = "Chuck Hahm" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = "~=3.11"
dependencies = [
    "anthropic>=0.25.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "loguru>=0.7.2",
    "poethepoet>=0.29.0",
    "dash>=2.17.0",
    "dash-bootstrap-components>=1.6.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.4.9",
    "pre-commit>=3.7.1",
    "pytest>=8.2.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["deepvoxel"]

[tool.poe]
executor = { type = "uv" }

[tool.poe.tasks]
run-engagement = "uv run python -m tools.run --engagement"
run-replay     = "uv run python -m tools.run --replay"
run-inspector  = "uv run python -m tools.inspect"
lint-check     = "uv run ruff check ."
format-check   = "uv run ruff format --check ."
lint-fix       = "uv run ruff check --fix ."
format-fix     = "uv run ruff format ."
gitleaks-check = "docker run -v .:/src zricethezav/gitleaks:latest dir /src/deepvoxel"

[tool.poe.tasks.test]
cmd = "uv run pytest tests/"
env = { ENV_FILE = ".env.testing" }
```

Install:
```bash
uv sync
uv sync --extra dev
```

#### Step 4 — `ruff.toml`

```toml
line-length = 99
target-version = "py311"

[lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]
```

#### Step 5 — Supporting Config Files

**`.pre-commit-config.yaml`**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
```

```bash
uv run pre-commit install
```

**`.gitignore`**
```
.env
.venv/
configs/engagements/*.yaml
configs/engagements/*.txt
outputs/
__pycache__/
*.py[cod]
*.egg-info/
dist/
.pytest_cache/
```

**`.env.example`**
```bash
# Copy to .env and fill in values. Never commit .env.
ANTHROPIC_API_KEY=your_key_here
BRAVE_API_KEY=your_key_here
```

**Validate bootstrap:**
```bash
uv run python --version   # should show 3.11.x
uv run poe lint-check     # should pass on empty project
git init && git add . && git commit -m "chore: bootstrap project structure"
```

---

### FILE 2 — BUILD.md
*Steps 6–9: Python source files in DDD order.*

#### Step 6 — `CLAUDE.md`

```markdown
# deepVoxel LLM Harness — Claude Code Context

## Purpose
Prototype implementation of the deepVoxel CI report generation harness.
Productionalizes the LipoNexus engagement methodology as chained LLM calls.

## Tooling
- Python 3.11, uv for package management
- uv sync to install; uv run to execute
- Poe the Poet for task runner: uv run poe <task>
- ruff for linting and formatting

## Architecture — DDD Layers
Import direction: infrastructure → application → domain

- domain/         Core entities. Zero external imports. EngagementState lives here.
- application/    Business logic. Runner and nodes. Imports from domain + infrastructure.
- infrastructure/ External integrations. Anthropic client, config loader, .env loading.

## Active Prototype Scope
Phase 0: Intake (transcript → structured seed state)
Phase 1a: Patent entity identification (blind USPTO sweep)
Phase 1b: Patent portfolio analysis (target entity deep dive)
Phase 2: Founding team stub (structure only, not yet wired)

## Key Files
- deepvoxel/domain/engagement.py        → EngagementState dataclass
- deepvoxel/application/runner.py       → chain orchestrator
- deepvoxel/application/nodes/          → one file per phase
- deepvoxel/infrastructure/             → Anthropic client, config loader
- configs/engagements/                  → client YAML files (gitignored)
- inspector/harness_inspector.py        → Dash chain inspector, port 8011

## Engagement Config Pattern
Each engagement is a gitignored YAML in configs/engagements/<slug>.yaml.
Run: uv run poe run-replay              (liponexus replay)
     uv run poe run-engagement --engagement <slug>

## Do Not
- Do not add LangChain or similar frameworks
- Do not hardcode client names in source code or prompts
- Do not commit configs/engagements/*.yaml to git
- Do not break DDD import direction (domain has zero external imports)
```

#### Step 7 — `deepvoxel/domain/engagement.py`

```python
# deepvoxel/domain/engagement.py
# Domain layer — zero external imports
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

    def log_call(self, node: str, messages_in: list,
                 response_text: str, usage: dict):
        """Record every API call for inspection."""
        self.call_log.append({
            "node": node,
            "timestamp": datetime.now().isoformat(),
            "messages_in": messages_in,
            "response_text": response_text,
            "usage": usage,
        })
```

**Validate:**
```bash
uv run python -c "from deepvoxel.domain.engagement import EngagementState; \
    s = EngagementState(engagement_id='test'); print('OK:', s.engagement_id)"
```

#### Step 8 — Infrastructure Layer

**`deepvoxel/infrastructure/anthropic_client.py`**
```python
import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def get_client() -> anthropic.Anthropic:
    client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env
    logger.debug("Anthropic client initialized")
    return client
```

**`deepvoxel/infrastructure/config_loader.py`**
```python
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
```

**Validate:**
```bash
uv run python -c "from deepvoxel.infrastructure.anthropic_client import get_client; \
    print('OK')"
```

#### Step 9 — Prompt Templates

Create `deepvoxel/application/prompts/` directory and four `.md` files.

**`deepvoxel/application/prompts/intake.md`**
```markdown
You are a competitive intelligence analyst. A client has shared a call transcript.

Extract the following and return as structured text with clear section headers:

1. TECHNOLOGY: What is the core technology or product? One paragraph.
2. BD_OBJECTIVES: What does the client want to achieve?
3. NAMED_COMPETITORS: List any competitors the client mentioned by name.
4. NAMED_PERSONNEL: List any people named (founders, advisors, executives).
5. FUNDING_SIGNALS: Any mentions of fundraising stage, timeline, or amount.
6. ANOMALIES: Anything unusual, contradictory, or strategically sensitive.

Be precise. Do not invent information not present in the transcript.

TRANSCRIPT:
{transcript}
```

**`deepvoxel/application/prompts/patents_identify.md`**
```markdown
You are a patent intelligence analyst conducting a blind competitive sweep.

Using only the technology description below, identify companies and inventors
who hold USPTO patents in this space. Do not assume or use the client's
company name.

For each entity found, provide:
- Assignee name (company or institution)
- Inventor names
- Representative patent numbers
- One-sentence claim summary
- Filing date range

Flag any academic institutions, government labs, or individual inventors
(not corporate assignees) as these represent different competitive dynamics.

TECHNOLOGY DESCRIPTION:
{technology_description}
```

**`deepvoxel/application/prompts/patents_analyze.md`**
```markdown
You are a patent intelligence analyst conducting a deep portfolio analysis.

Target entity: {target_entity}

For this entity's complete patent portfolio:

1. ISSUED PATENTS: List all issued patents. For each: number, title,
   filing date, broadest independent claim, co-inventors.

2. PROVISIONAL APPLICATIONS: List any provisionals not yet converted.
   Flag if provisionals cover claims NOT protected by issued patents.

3. CLAIM GAPS: Identify commercially significant claims the company makes
   (from website, press, or technology description) NOT yet protected by
   issued patents. This is the most important finding.

4. CO-INVENTOR FLAGS: For each co-inventor, note primary affiliation.
   Flag any co-inventor with roles at competing or adjacent organizations.

PRIOR RESEARCH CONTEXT:
{patent_entity_raw}

TECHNOLOGY DESCRIPTION:
{technology_description}
```

**`deepvoxel/application/prompts/founding_team.md`**
```markdown
You are a competitive intelligence analyst conducting founding team due diligence.

For each person listed below, research and report:

1. IDENTITY & CREDENTIALS: Current role, institutional affiliation,
   prior ventures, academic credentials.

2. IP & PATENT ATTRIBUTION: USPTO inventor records. Flag any employer
   assignment conflicts or prior IP claims.

3. GRANT & FEDERAL FUNDING: NIH/SBIR PI record. Flag any ORI misconduct
   findings or debarment status.

4. DUAL ROLE FLAGS: Any current advisory, board, or equity positions at
   competing or adjacent organizations. This is the most important finding.

5. NETWORK & AFFILIATION MAP: Co-founder history, investor loyalties,
   known competitor affiliations.

FOUNDING TEAM:
{named_personnel}

PRIOR PATENT RESEARCH:
{patent_analysis_raw}
```

#### Step 10 — Application Layer (Nodes)

**`deepvoxel/application/nodes/node_00_intake.py`**
```python
from pathlib import Path
import anthropic
from loguru import logger
from deepvoxel.domain.engagement import EngagementState

PROMPT = (Path(__file__).parent.parent / "prompts" / "intake.md").read_text


def run(state: EngagementState, transcript: str,
        client: anthropic.Anthropic) -> EngagementState:
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


_HEADERS = [
    "TECHNOLOGY:", "BD_OBJECTIVES:", "NAMED_COMPETITORS:",
    "NAMED_PERSONNEL:", "FUNDING_SIGNALS:", "ANOMALIES:",
]


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
```

**`deepvoxel/application/nodes/node_01_patents.py`**
```python
from pathlib import Path
import anthropic
from loguru import logger
from deepvoxel.domain.engagement import EngagementState

PROMPTS = Path(__file__).parent.parent / "prompts"


def run(state: EngagementState,
        client: anthropic.Anthropic) -> EngagementState:
    """Phase 1: Two-step patent analysis."""
    state = _step_1a(state, client)
    state = _step_1b(state, client)
    return state


def _step_1a(state: EngagementState,
             client: anthropic.Anthropic) -> EngagementState:
    """Blind entity identification from technology description only."""
    template = (PROMPTS / "patents_identify.md").read_text()
    prompt = template.replace("{technology_description}",
                              state.technology_description)
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


def _step_1b(state: EngagementState,
             client: anthropic.Anthropic) -> EngagementState:
    """Deep portfolio analysis — 1a output feeds 1b input."""
    template = (PROMPTS / "patents_analyze.md").read_text()
    prompt = (
        template
        .replace("{target_entity}", state.target_entity or "[entity from step 1a]")
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
```

#### Step 11 — Runner and CLI

**`deepvoxel/application/runner.py`**
```python
from loguru import logger
from deepvoxel.domain.engagement import EngagementState
from deepvoxel.infrastructure.anthropic_client import get_client
from deepvoxel.infrastructure.config_loader import seed_state
from deepvoxel.application.nodes import node_00_intake, node_01_patents


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
        c["usage"]["input_tokens"] + c["usage"]["output_tokens"]
        for c in state.call_log
    )
    logger.success(
        f"Chain complete — {len(state.call_log)} API calls | {total_tokens} tokens"
    )
    return state
```

**`tools/run.py`**
```python
import click
from loguru import logger
from deepvoxel.application.runner import run_engagement


@click.command()
@click.option("--engagement", default=None, help="Engagement slug to run")
@click.option("--replay", is_flag=True, default=False,
              help="Run LipoNexus replay")
def main(engagement: str, replay: bool):
    if replay:
        logger.info("Running engagement replay...")
        run_engagement("liponexus")
    elif engagement:
        run_engagement(engagement)
    else:
        logger.error("Provide --engagement <slug> or --replay")


if __name__ == "__main__":
    main()
```

---

### FILE 3 — VALIDATE.md
*Steps 12–14: Config files, inspector, test replay.*

#### Step 12 — Engagement Config Files

**`configs/template.yaml`** (tracked in git)
```yaml
# Copy → configs/engagements/<slug>.yaml and fill in.
# Populated copies are gitignored and never committed.

engagement_id: ""
client_name: ""
vertical: ""          # medical_diagnostics | defense_govcon | energy_storage

technology_description: >
  [Describe the core technology or product in 2-4 sentences]

bd_objectives: >
  [What does the client want to achieve?]

key_personnel:
  - name: ""
    role: ""

target_entity_hint: ""   # leave blank for blind patent sweep
transcript_path: ""      # path to raw transcript file, relative to repo root
```

**`configs/engagements/liponexus.yaml`** (gitignored — create locally)
```yaml
engagement_id: "liponexus-001"
client_name: "[CLIENT NAME REDACTED]"
vertical: "medical_diagnostics"

technology_description: >
  Mass spectrometry-based eicosanoid lipidomics platform with proprietary
  algorithm for early detection of metabolic liver disease using a blood test.
  Targets detection before fibrosis onset as primary commercial claim.

bd_objectives: >
  Series A investor introductions, clinical study partners,
  advisory board candidates. VC requires 50-100 competitor identification.

key_personnel:
  - name: "[FOUNDER 1 NAME REDACTED]"
    role: "Co-founder, UCSD Biochemistry professor"
  - name: "[FOUNDER 2 NAME REDACTED]"
    role: "Co-founder, UCSD Medical Center director"

target_entity_hint: ""
transcript_path: "configs/engagements/liponexus_transcript.txt"
```

#### Step 13 — Harness Inspector

**`inspector/harness_inspector.py`**
```python
"""
Harness Inspector — chain-aware extension of message_inspector.py
Port: 8011 (leave 8010 for original single-turn inspector)
Shows: node sequence, state delta per node, token consumption per node.
"""
import json
import sys
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State

sys.path.insert(0, "..")
from deepvoxel.application.runner import run_engagement

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container([
    html.H3("deepVoxel Harness Inspector", className="mt-3 mb-3"),
    dbc.Row([
        dbc.Col([
            html.Label("Engagement Slug"),
            dcc.Input(id="slug-input", value="liponexus",
                      style={"width": "100%"}),
            dbc.Button("Run Chain", id="run-btn",
                       color="primary", className="mt-2"),
        ], width=3),
        dbc.Col([
            html.Label("Chain Summary"),
            html.Div(id="chain-summary",
                     style={"background": "#2a2a2a", "padding": "10px",
                            "height": "150px", "overflow": "auto",
                            "fontFamily": "monospace", "fontSize": "12px"}),
        ], width=9),
    ]),
    html.Hr(),
    html.H5("Node Detail"),
    dcc.Dropdown(id="node-selector",
                 placeholder="Select node to inspect..."),
    dbc.Row([
        dbc.Col([
            html.Label("Messages In"),
            dcc.Textarea(id="messages-in",
                         style={"width": "100%", "height": "350px",
                                "fontFamily": "monospace", "fontSize": "11px"}),
        ], width=6),
        dbc.Col([
            html.Label("Response Out"),
            dcc.Textarea(id="response-out",
                         style={"width": "100%", "height": "350px",
                                "fontFamily": "monospace", "fontSize": "11px"}),
        ], width=6),
    ]),
    dcc.Store(id="state-store"),
], fluid=True)


@app.callback(
    Output("state-store", "data"),
    Output("chain-summary", "children"),
    Output("node-selector", "options"),
    Input("run-btn", "n_clicks"),
    State("slug-input", "value"),
    prevent_initial_call=True,
)
def run_chain(n_clicks, slug):
    if not slug:
        return {}, "No slug provided.", []
    state = run_engagement(slug)
    state_dict = state.__dict__
    lines = [
        f"Engagement: {state.engagement_id}",
        f"API calls:  {len(state.call_log)}",
        f"Technology: {state.technology_description[:120]}",
        f"Personnel:  {state.named_personnel}",
        "",
    ] + [
        f"  [{c['node']}]  "
        f"in={c['usage']['input_tokens']}  "
        f"out={c['usage']['output_tokens']}"
        for c in state.call_log
    ]
    options = [
        {"label": c["node"], "value": i}
        for i, c in enumerate(state.call_log)
    ]
    return state_dict, html.Pre("\n".join(lines)), options


@app.callback(
    Output("messages-in", "value"),
    Output("response-out", "value"),
    Input("node-selector", "value"),
    State("state-store", "data"),
    prevent_initial_call=True,
)
def show_node(node_idx, state_data):
    if node_idx is None or not state_data:
        return "", ""
    call = state_data["call_log"][node_idx]
    return json.dumps(call["messages_in"], indent=2), call["response_text"]


if __name__ == "__main__":
    app.run(debug=True, port=8011)
```

**`tools/inspect.py`**
```python
from inspector.harness_inspector import app

if __name__ == "__main__":
    app.run(debug=True, port=8011)
```

#### Step 14 — Test Replay

**`tests/test_engagement_replay.py`**
```python
"""
Replay the engagement with the prototype chain.
Validates harness output against known engagement inputs.
"""
import sys
sys.path.insert(0, "..")
from deepvoxel.application.runner import run_engagement

ENGAGEMENT_SLUG = "liponexus"


def test_intake_extraction():
    state = run_engagement(ENGAGEMENT_SLUG)
    assert state.technology_description, "Technology description empty"
    assert len(state.named_personnel) > 0, "No personnel extracted"
    print(f"\nTechnology: {state.technology_description[:200]}")
    print(f"Personnel:  {state.named_personnel}")
    print(f"Objectives: {state.bd_objectives[:200]}")


def test_patent_chain():
    state = run_engagement(ENGAGEMENT_SLUG)
    assert state.patent_entity_raw, "Patent entity sweep empty"
    assert state.patent_analysis_raw, "Patent analysis empty"
    assert len(state.call_log) >= 3, "Expected at least 3 API calls"
    print(f"\nEntity sweep ({len(state.patent_entity_raw)} chars)")
    print(state.patent_entity_raw[:400])
    print(f"\nPortfolio analysis ({len(state.patent_analysis_raw)} chars)")
    print(state.patent_analysis_raw[:400])


def test_call_log():
    state = run_engagement(ENGAGEMENT_SLUG)
    nodes = [c["node"] for c in state.call_log]
    assert "node_00_intake" in nodes
    assert "node_01a_patent_identify" in nodes
    assert "node_01b_patent_analyze" in nodes
    total_tokens = sum(
        c["usage"]["input_tokens"] + c["usage"]["output_tokens"]
        for c in state.call_log
    )
    print(f"\nNodes executed: {nodes}")
    print(f"Total tokens:   {total_tokens}")


if __name__ == "__main__":
    test_intake_extraction()
    test_patent_chain()
    test_call_log()
```

**Run:**
```bash
uv run poe test
# or with output:
uv run pytest tests/ -v -s
```

---

## gstack Integration (Optional)

Install gstack skills for harness development discipline:

```bash
git clone https://github.com/garrytan/gstack /tmp/gstack
mkdir -p .claude/commands
cp /tmp/gstack/office-hours/SKILL.md    .claude/commands/office-hours.md
cp /tmp/gstack/plan/SKILL.md            .claude/commands/plan-eng-review.md
cp /tmp/gstack/review/SKILL.md          .claude/commands/review.md
cp /tmp/gstack/document/SKILL.md        .claude/commands/document-release.md
```

**When to invoke each skill:**

| Skill | When |
|---|---|
| `/office-hours` | Before designing each new phase node |
| `/plan-eng-review` | Before implementing the runner or any new DDD layer |
| `/review` | Before each git commit |
| `/document-release` | After LipoNexus replay validates successfully |

Skip: CEO, Designer, Release Manager, QA browser automation — not applicable at this stage.

---

## uv Command Reference

| Action | Command |
|---|---|
| Install all deps | `uv sync` |
| Install with dev | `uv sync --extra dev` |
| Add a package | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Run a script | `uv run python <script>` |
| Run a module | `uv run python -m <module>` |
| Run poe task | `uv run poe <task>` |
| Run tests | `uv run pytest tests/ -v -s` |
| Lint fix | `uv run poe lint-fix` |
| Format fix | `uv run poe format-fix` |
| Activate venv | `source .venv/bin/activate` |

---

## Complete Build Sequence (summary)

```bash
# FILE 1 — Bootstrap
uv init deepvoxel-harness && cd deepvoxel-harness
uv python pin 3.11 && uv venv
# → write pyproject.toml, ruff.toml, .pre-commit-config.yaml, .gitignore, .env.example
uv sync && uv sync --extra dev
uv run pre-commit install
git init && git add . && git commit -m "chore: bootstrap"

# FILE 2 — Build
# → write CLAUDE.md
# → write deepvoxel/domain/engagement.py
uv run python -c "from deepvoxel.domain.engagement import EngagementState; print('OK')"
# → write deepvoxel/infrastructure/anthropic_client.py + config_loader.py
uv run python -c "from deepvoxel.infrastructure.anthropic_client import get_client; print('OK')"
# → write prompts/*.md
# → write application/nodes/node_00_intake.py
# → write application/nodes/node_01_patents.py
# → write application/runner.py + tools/run.py
git add . && git commit -m "feat: Phase 0+1 harness nodes"

# FILE 3 — Validate
# → write configs/template.yaml (tracked)
# → create configs/engagements/liponexus.yaml (local only, gitignored)
# → write inspector/harness_inspector.py + tools/inspect.py
# → write tests/test_engagement_replay.py
uv run poe run-replay       # validate Phase 0 + 1
uv run poe run-inspector    # confirm port 8011
uv run poe test             # full test suite
uv run poe lint-fix && uv run poe format-fix
git add . && git commit -m "feat: inspector + replay validation"
```

---

## What You Will Learn from Running This

**After Phase 0 node alone:** A single focused LLM call produces cleaner
structured output than a broad prompt trying to do everything. The section
extraction in `node_00_intake.py` will show you immediately where prompt
structure affects parseability.

**After Phase 1 chain:** The `messages_in` panel in the inspector will show
Phase 1b receiving Phase 1a's output as context — the core chain mechanic
made visible. Token counts will show how context accumulation grows costs
across nodes.

**After inspector is running:** Token consumption per node reveals where the
chain is expensive and where prompt length can be optimized.

**After LipoNexus replay:** Comparing harness output against the original
manual engagement findings tells you what the prototype gets right and where
prompt templates need refinement before Phase 3 nodes are built.

---

## Future Phases (not in prototype scope)

| Phase | Content |
|---|---|
| Phase 3 | Competitive landscape (3-layer expansion, 57-entity matrix pattern) |
| Phase 4 | NIH/SBIR grant mapping |
| Phase 5 | Investor intelligence |
| Phase 6 | Structured deliverables (teaser + paid report generation) |
| Phase 7 | Tool use integration (live USPTO API, NIH Reporter calls) |
