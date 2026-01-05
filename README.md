# wetwire-core-python

[![CI](https://github.com/lex00/wetwire-core-python/actions/workflows/ci.yml/badge.svg)](https://github.com/lex00/wetwire-core-python/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/wetwire-core.svg)](https://pypi.org/project/wetwire-core/)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

MIT
