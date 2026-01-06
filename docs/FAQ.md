# wetwire-core-python FAQ

This FAQ covers questions specific to the Python agent infrastructure. For general wetwire questions, see the [central FAQ](https://github.com/lex00/wetwire/blob/main/docs/FAQ.md).

---

## General

### What is wetwire-core?

wetwire-core provides the agent infrastructure for AI-assisted infrastructure generation:
- Developer and Runner agent implementations
- Personas for testing
- Scoring and evaluation
- Session tracking and results

### How do I install it?

```bash
pip install wetwire-core
```

### How does it relate to domain packages?

Domain packages (like wetwire-aws) use wetwire-core for `design` and `test` commands. The core package provides the agent orchestration; domain packages provide the tools and resources.

---

## Agents

### What is the two-agent model?

1. **DeveloperAgent** — Represents the human (or simulates via persona)
2. **RunnerAgent** — Generates infrastructure code using domain CLI tools

### What agents are available?

```python
from wetwire_core.agents import DeveloperAgent, RunnerAgent
from wetwire_core.agents import AIConversationHandler, InteractiveConversationHandler
```

### What's the difference between handlers?

| Handler | Use Case |
|---------|----------|
| `AIConversationHandler` | Autonomous AI-to-AI testing |
| `InteractiveConversationHandler` | Human + AI collaboration |

---

## Personas

### What personas are available?

| Name | Behavior |
|------|----------|
| **Beginner** | Uncertain, asks many questions |
| **Intermediate** | Some knowledge, may miss details |
| **Expert** | Precise requirements, minimal hand-holding |
| **Terse** | Minimal information, expects inference |
| **Verbose** | Over-explains, buries requirements |

### How do I load a persona?

```python
from wetwire_core.agent.personas import load_persona

persona = load_persona("beginner")
```

### Can I create custom personas?

Yes. Create a `Persona` with name, description, system_prompt, and traits.

---

## Scoring

### How is scoring calculated?

5 dimensions, 0-3 points each (15 total):

| Dimension | Measures |
|-----------|----------|
| Completeness | Were all resources generated? |
| Lint Quality | How many lint cycles needed? |
| Code Quality | Is the code idiomatic? |
| Output Validity | Does output validate? |
| Question Efficiency | Appropriate question count? |

### How do I access scoring functions?

```python
from wetwire_core.agent.scoring import Score, Rating
```

### What scores are passing?

| Score | Grade |
|-------|-------|
| 0-5 | Failure |
| 6-9 | Partial |
| 10-12 | Success |
| 13-15 | Excellent |

Minimum passing score is 6.

---

## Results

### How do I generate results?

```python
from pathlib import Path
from wetwire_core.agent.results import SessionResults, ResultsWriter

results = SessionResults(
    prompt="Create a VPC",
    package_name="my_vpc",
    domain="aws",
)
writer = ResultsWriter()
writer.write(results, Path("output/RESULTS.md"))
```

### What output files are generated?

| File | Content |
|------|---------|
| `RESULTS.md` | Human-readable summary |
| `session.json` | Complete session data |

---

## Streaming

### Does wetwire-core support streaming?

Yes. The `RunnerAgent` supports streaming output:

```python
runner.run_turn_streaming(
    on_text=lambda chunk: print(chunk, end=""),
    on_tool_start=lambda name: print(f"Starting {name}..."),
    on_tool_end=lambda name, result: print(f"Done {name}: {result.output[:50]}...")
)
```

---

## Integration

### How do domain packages integrate?

Domain packages use `InteractiveConversationHandler` which internally creates a `RunnerAgent`:

```python
# In domain package
from pathlib import Path
from wetwire_core.agents import InteractiveConversationHandler

handler = InteractiveConversationHandler(output_dir=Path("./output"))
package_path, messages = handler.run(initial_prompt)
```

The handler creates its own `RunnerAgent` internally, which calls domain CLI tools (`wetwire-aws lint`, `wetwire-aws build`, etc.) via subprocess.

---

## Troubleshooting

### ANTHROPIC_API_KEY not set

Design mode requires the Anthropic API:

```bash
export ANTHROPIC_API_KEY=your-key
```

### Agent not completing

Check enforcement rules:
1. Agent must call `run_lint` after `write_file`
2. Lint must pass before completion

---

## Resources

- [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md)
- [wetwire-aws-python](https://github.com/lex00/wetwire-aws-python) (example integration)
