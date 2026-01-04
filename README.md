# wetwire-core-python

Shared agent infrastructure for wetwire domain packages.

## Overview

wetwire-core provides the AI agent framework used by wetwire domain packages (like wetwire-aws). It includes:

- **agent/personas** - Developer persona definitions (Beginner, Intermediate, Expert, Terse, Verbose)
- **agent/scoring** - 5-dimension evaluation rubric (0-15 scale)
- **agent/results** - Session tracking and RESULTS.md generation
- **agent/orchestrator** - Developer/Runner agent coordination
- **agents** - Anthropic SDK integration and RunnerAgent

## Installation

```bash
pip install wetwire-core
```

## Usage

wetwire-core is typically used as a dependency of domain packages like wetwire-aws.

```python
from wetwire_core.agent.personas import load_persona
from wetwire_core.agent.scoring import calculate_score
from wetwire_core.agent.orchestrator import Orchestrator
```

## License

Apache License 2.0
