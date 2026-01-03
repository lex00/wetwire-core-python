"""Tests for agent.results module."""

import tempfile
from datetime import datetime
from pathlib import Path

from wetwire_core.agent.results import LintCycle, Question, ResultsWriter, SessionResults
from wetwire_core.agent.scoring import Rating, Score


class TestLintCycle:
    """Tests for LintCycle dataclass."""

    def test_lint_cycle_creation(self):
        """Test that LintCycle can be created with all fields."""
        cycle = LintCycle(
            cycle_number=1,
            issues_found=3,
            issues=["issue1", "issue2", "issue3"],
            actions_taken=["fix1", "fix2"],
        )
        assert cycle.cycle_number == 1
        assert cycle.issues_found == 3
        assert cycle.issues == ["issue1", "issue2", "issue3"]
        assert cycle.actions_taken == ["fix1", "fix2"]


class TestQuestion:
    """Tests for Question dataclass."""

    def test_question_creation(self):
        """Test that Question can be created with all fields."""
        question = Question(
            runner_question="What region should I use?",
            developer_response="us-east-1",
        )
        assert question.runner_question == "What region should I use?"
        assert question.developer_response == "us-east-1"


class TestSessionResults:
    """Tests for SessionResults dataclass."""

    def test_minimal_creation(self):
        """Test that SessionResults can be created with minimal fields."""
        results = SessionResults(
            prompt="Create a VPC",
            package_name="my_vpc",
            domain="aws",
        )
        assert results.prompt == "Create a VPC"
        assert results.package_name == "my_vpc"
        assert results.domain == "aws"
        assert results.persona is None
        assert results.summary == ""
        assert results.lint_cycles == []
        assert results.questions == []
        assert results.suggestions == []
        assert results.score is None
        assert isinstance(results.started_at, datetime)
        assert results.completed_at is None

    def test_full_creation(self):
        """Test that SessionResults can be created with all fields."""
        score = Score(
            completeness=Rating.EXCELLENT,
            lint_quality=Rating.GOOD,
            code_quality=Rating.GOOD,
            output_validity=Rating.EXCELLENT,
            question_efficiency=Rating.EXCELLENT,
        )
        started = datetime.now()
        completed = datetime.now()

        results = SessionResults(
            prompt="Create a VPC",
            package_name="my_vpc",
            domain="aws",
            persona="expert",
            summary="Created a VPC with public and private subnets",
            lint_cycles=[
                LintCycle(
                    cycle_number=1,
                    issues_found=2,
                    issues=["missing import", "unused variable"],
                    actions_taken=["added import", "removed variable"],
                )
            ],
            questions=[
                Question(
                    runner_question="What CIDR block?",
                    developer_response="10.0.0.0/16",
                )
            ],
            suggestions=["Add better error handling"],
            score=score,
            started_at=started,
            completed_at=completed,
        )
        assert results.prompt == "Create a VPC"
        assert results.package_name == "my_vpc"
        assert results.domain == "aws"
        assert results.persona == "expert"
        assert results.summary == "Created a VPC with public and private subnets"
        assert len(results.lint_cycles) == 1
        assert len(results.questions) == 1
        assert len(results.suggestions) == 1
        assert results.score == score
        assert results.started_at == started
        assert results.completed_at == completed


class TestResultsWriter:
    """Tests for ResultsWriter class."""

    def test_format_minimal_results(self):
        """Test formatting of minimal SessionResults."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            started_at=datetime(2024, 1, 15, 10, 30),
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "# Package Generation Results" in markdown
        assert '**Prompt:** "Create a bucket"' in markdown
        assert "**Package:** my_bucket" in markdown
        assert "**Domain:** aws" in markdown
        assert "**Date:** 2024-01-15" in markdown
        assert "## Summary" in markdown
        assert "_No summary provided_" in markdown
        assert "## Lint Cycles" in markdown
        assert "_No lint cycles needed_" in markdown
        assert "## Questions Asked" in markdown
        assert "_No questions asked_" in markdown
        assert "## Score" not in markdown

    def test_format_with_persona(self):
        """Test that persona is included when present."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            persona="beginner",
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "**Persona:** beginner" in markdown

    def test_format_with_summary(self):
        """Test that summary is included correctly."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            summary="Created an encrypted S3 bucket with versioning enabled.",
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "Created an encrypted S3 bucket with versioning enabled." in markdown
        assert "_No summary provided_" not in markdown

    def test_format_with_lint_cycles(self):
        """Test that lint cycles are formatted correctly."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            lint_cycles=[
                LintCycle(
                    cycle_number=1,
                    issues_found=2,
                    issues=["Missing import", "Unused variable x"],
                    actions_taken=["Added import", "Removed variable x"],
                ),
                LintCycle(
                    cycle_number=2,
                    issues_found=0,
                    issues=[],
                    actions_taken=[],
                ),
            ],
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "### Cycle 1" in markdown
        assert "**Issues Found:** 2" in markdown
        assert "- Missing import" in markdown
        assert "- Unused variable x" in markdown
        assert "**Actions Taken:**" in markdown
        assert "- Added import" in markdown
        assert "- Removed variable x" in markdown
        assert "### Cycle 2" in markdown
        assert "_No lint cycles needed_" not in markdown

    def test_format_with_questions(self):
        """Test that questions are formatted correctly."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            questions=[
                Question(
                    runner_question="What region should I use?",
                    developer_response="us-west-2",
                ),
                Question(
                    runner_question="Enable versioning?",
                    developer_response="Yes",
                ),
            ],
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert '1. **Runner:** "What region should I use?"' in markdown
        assert '**Developer:** "us-west-2"' in markdown
        assert '2. **Runner:** "Enable versioning?"' in markdown
        assert '**Developer:** "Yes"' in markdown
        assert "_No questions asked_" not in markdown

    def test_format_with_suggestions(self):
        """Test that suggestions are formatted correctly."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            suggestions=[
                "Add better error messages for validation failures",
                "Support for custom encryption keys",
            ],
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "## Framework Improvement Suggestions" in markdown
        assert "1. Add better error messages for validation failures" in markdown
        assert "2. Support for custom encryption keys" in markdown

    def test_format_with_score(self):
        """Test that score is formatted correctly."""
        score = Score(
            completeness=Rating.EXCELLENT,
            lint_quality=Rating.GOOD,
            code_quality=Rating.GOOD,
            output_validity=Rating.EXCELLENT,
            question_efficiency=Rating.POOR,
        )
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            score=score,
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "## Score" in markdown
        assert "| Dimension | Score |" in markdown
        assert "| Completeness | 3/3 |" in markdown
        assert "| Lint Quality | 2/3 |" in markdown
        assert "| Code Quality | 2/3 |" in markdown
        assert "| Output Validity | 3/3 |" in markdown
        assert "| Question Efficiency | 1/3 |" in markdown
        assert "| **Total** | **11/15** |" in markdown
        assert "**Grade:** Success" in markdown

    def test_write_to_file(self):
        """Test that write() writes markdown to a file."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            summary="Test summary",
        )
        writer = ResultsWriter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "RESULTS.md"
            writer.write(results, output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "# Package Generation Results" in content
            assert "Test summary" in content

    def test_empty_lists_handled_correctly(self):
        """Test that empty lists don't cause formatting issues."""
        results = SessionResults(
            prompt="Create a bucket",
            package_name="my_bucket",
            domain="aws",
            lint_cycles=[],
            questions=[],
            suggestions=[],
        )
        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "_No lint cycles needed_" in markdown
        assert "_No questions asked_" in markdown
        assert "## Framework Improvement Suggestions" not in markdown
