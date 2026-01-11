# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- CLI utility functions module (`wetwire_core.cli`)
- MCP server abstraction module (`wetwire_core.mcp`)
- Provider abstraction layer (`wetwire_core.providers`)
- Kiro CLI integration module (`wetwire_core.kiro`)
- Persona helper functions: `get_persona()`, `all_personas()`, `persona_names()`

## [1.0.1] - 2026-01-05

### Changed
- Replace mypy with ty for type checking
- Add MIT license file

## [1.0.0] - 2026-01-03

### Changed
- Stabilize API for production use
- License clarification (MIT)

## [0.1.2] - 2026-01-03

### Added
- Comprehensive test suite for agents, personas, scoring, and results
- PyPI publish workflow
- CodeBot workflow for automated responses

## [0.1.1] - 2026-01-03

### Added
- CI workflow for testing
- Initial test coverage

### Fixed
- Ruff linting errors resolved

## [0.1.0] - 2026-01-03

### Added
- Initial release
- Core agent infrastructure (DeveloperAgent, RunnerAgent)
- Persona system with 5 built-in personas
- Scoring rubric with 5 dimensions (0-15 scale)
- Orchestrator for Developer/Runner coordination
- ResultsWriter for session documentation

[Unreleased]: https://github.com/lex00/wetwire-core-python/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/lex00/wetwire-core-python/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/lex00/wetwire-core-python/compare/v0.1.2...v1.0.0
[0.1.2]: https://github.com/lex00/wetwire-core-python/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/lex00/wetwire-core-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/lex00/wetwire-core-python/releases/tag/v0.1.0
