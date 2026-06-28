# deepVoxel LLM Harness

Chained Anthropic API harness for generating competitive intelligence reports.
Encodes the CI engagement methodology as explicit, inspectable API calls
with shared state — making it repeatable across engagements without rebuilding.

## Architecture

DDD layer structure with strict import direction:

```
infrastructure  →  application  →  domain
(Anthropic client,   (runner, nodes)   (EngagementState)
 config loader)
```

### Chain

```
configs/engagements/<slug>.yaml
        ↓
  EngagementState (seed)
        ↓
  node_00_intake       → technology_description, named_personnel, ...
        ↓
  node_01_patents (1a) → patent_entity_raw   (blind USPTO sweep)
        ↓
  node_01_patents (1b) → patent_analysis_raw (target entity deep dive)
        ↓
  state.call_log       → full API call history for inspector
```

## Setup

```bash
uv sync --extra dev
cp .env.example .env          # add ANTHROPIC_API_KEY
```

## Running an Engagement

```bash
# Create an engagement config (gitignored):
cp configs/template.yaml configs/engagements/<slug>.yaml
# Fill in technology_description, key_personnel, transcript_path, etc.

uv run poe run-engagement --engagement <slug>

# Or run the example engagement replay (requires example.yaml locally):
uv run poe run-replay
```

## Inspector

Plotly Dash UI that shows node sequence, messages in/out, and token usage per node:

```bash
uv run poe run-inspector      # → http://localhost:8011
```

## Tests

```bash
uv run pytest tests/ -v -s    # requires ANTHROPIC_API_KEY and example.yaml
```

## Tasks

| Command | Action |
|---|---|
| `uv run poe run-engagement` | Run an engagement by slug |
| `uv run poe run-replay` | Run example engagement replay |
| `uv run poe run-inspector` | Launch chain inspector on port 8011 |
| `uv run poe lint-fix` | Lint and fix with ruff |
| `uv run poe format-fix` | Format with ruff |
| `uv run poe test` | Run test suite |

## Project Structure

```
deepvoxel/
  domain/           # EngagementState dataclass — zero external imports
  infrastructure/   # Anthropic client, YAML config loader
  application/
    nodes/          # One file per phase (node_00_intake, node_01_patents, ...)
    prompts/        # Prompt templates as .md files
    runner.py       # Chain orchestrator
configs/
  template.yaml             # Blank engagement template (tracked)
  engagements/<slug>.yaml   # Client configs (gitignored)
inspector/
  harness_inspector.py      # Dash chain inspector
tools/
  run.py                    # CLI entry point
  inspect.py                # Inspector entry point
tests/
  test_engagement_replay.py # example engagement replay validation
```

## Constraints

- No LangChain or frameworks — raw Anthropic SDK only
- Client configs (`configs/engagements/*.yaml`) are gitignored and never committed
- Domain layer has zero external imports
