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
