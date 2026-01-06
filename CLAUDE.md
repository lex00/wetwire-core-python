# wetwire-core-python

Shared agent infrastructure for wetwire domain packages (Python).

## Package Structure

```
wetwire_core/
├── agent/
│   ├── personas.py      # 5 built-in developer personas
│   ├── scoring.py       # 5-dimension evaluation rubric
│   ├── orchestrator.py  # Developer/Runner coordination
│   └── results.py       # Session tracking, RESULTS.md generation
├── agents.py            # DeveloperAgent, RunnerAgent
└── runner.py            # Runtime utilities
```

## Core Components

### Personas

Five built-in personas for testing AI-human collaboration:

- **Beginner** — Uncertain, asks many questions, needs guidance
- **Intermediate** — Some knowledge, specifies requirements but may miss details
- **Expert** — Deep knowledge, precise requirements, minimal hand-holding
- **Terse** — Minimal information, expects system to infer defaults
- **Verbose** — Over-explains, buries requirements in prose

```python
from wetwire_core.agent.personas import load_persona, PERSONAS

persona = load_persona("beginner")
print(persona.name, persona.description)
```

### Scoring

5-dimension evaluation rubric (0-15 scale):

| Dimension | Points | Description |
|-----------|--------|-------------|
| Completeness | 0-3 | Were all required resources generated? |
| Lint Quality | 0-3 | How many lint cycles needed? |
| Code Quality | 0-3 | Does code follow idiomatic patterns? |
| Output Validity | 0-3 | Does generated output validate? |
| Question Efficiency | 0-3 | Appropriate number of clarifying questions? |

```python
from wetwire_core.agent.scoring import calculate_score, Score

score = calculate_score(
    completeness=3,
    lint_quality=2,
    code_quality=3,
    output_validity=3,
    question_efficiency=2
)
print(f"Total: {score.total}/15 - {score.grade}")
```

### Orchestrator

Coordinates DeveloperAgent and RunnerAgent conversation:

```python
from wetwire_core.agent.orchestrator import Orchestrator

orchestrator = Orchestrator(
    domain="aws",
    developer=developer_agent,
    runner=runner_agent,
)
result = await orchestrator.run(initial_prompt)
```

### Results

Session tracking and RESULTS.md generation:

```python
from wetwire_core.agent.results import Session, ResultsWriter

session = Session(domain="aws", name="my_stack", prompt="Create S3 bucket")
# ... run agent workflow ...
session.complete()

writer = ResultsWriter()
writer.write(session, "./output/RESULTS.md")
```

## Integration Pattern

Domain packages (wetwire-aws, etc.) integrate wetwire-core via:

1. Import agents and orchestrator
2. Define domain-specific tools (init_package, write_file, run_lint, run_build)
3. Configure RunnerAgent with domain tools
4. Use orchestrator for design/test commands

## Key Principles

1. **Two-agent model** — Developer asks, Runner generates
2. **Lint enforcement** — RunnerAgent must lint after every write
3. **Pass before done** — Code must pass linting before completion
4. **Persona-based testing** — Test across all 5 developer styles

## Running Tests

```bash
pytest tests/
```
