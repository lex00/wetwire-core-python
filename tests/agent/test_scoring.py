"""Tests for agent.scoring module."""

from wetwire_core.agent.scoring import (
    Rating,
    Score,
    calculate_score,
    score_code_quality,
    score_completeness,
    score_lint_quality,
    score_output_validity,
    score_question_efficiency,
)


class TestRating:
    """Tests for Rating enum."""

    def test_rating_values(self):
        """Test that Rating enum has correct values."""
        assert Rating.NONE == 0
        assert Rating.POOR == 1
        assert Rating.GOOD == 2
        assert Rating.EXCELLENT == 3

    def test_rating_is_int_enum(self):
        """Test that Rating values can be used as integers."""
        assert int(Rating.NONE) == 0
        assert int(Rating.POOR) == 1
        assert int(Rating.GOOD) == 2
        assert int(Rating.EXCELLENT) == 3


class TestScore:
    """Tests for Score dataclass."""

    def test_score_creation(self):
        """Test that Score can be created with all ratings."""
        score = Score(
            completeness=Rating.EXCELLENT,
            lint_quality=Rating.GOOD,
            code_quality=Rating.GOOD,
            output_validity=Rating.EXCELLENT,
            question_efficiency=Rating.POOR,
        )
        assert score.completeness == Rating.EXCELLENT
        assert score.lint_quality == Rating.GOOD
        assert score.code_quality == Rating.GOOD
        assert score.output_validity == Rating.EXCELLENT
        assert score.question_efficiency == Rating.POOR

    def test_total_calculation(self):
        """Test that Score.total calculates correctly."""
        score = Score(
            completeness=Rating.EXCELLENT,  # 3
            lint_quality=Rating.GOOD,  # 2
            code_quality=Rating.GOOD,  # 2
            output_validity=Rating.EXCELLENT,  # 3
            question_efficiency=Rating.POOR,  # 1
        )
        assert score.total == 11

    def test_total_range(self):
        """Test that total scores are in 0-15 range."""
        min_score = Score(
            completeness=Rating.NONE,
            lint_quality=Rating.NONE,
            code_quality=Rating.NONE,
            output_validity=Rating.NONE,
            question_efficiency=Rating.NONE,
        )
        assert min_score.total == 0

        max_score = Score(
            completeness=Rating.EXCELLENT,
            lint_quality=Rating.EXCELLENT,
            code_quality=Rating.EXCELLENT,
            output_validity=Rating.EXCELLENT,
            question_efficiency=Rating.EXCELLENT,
        )
        assert max_score.total == 15

    def test_grade_failure(self):
        """Test that scores 0-5 get 'Failure' grade."""
        score = Score(
            completeness=Rating.POOR,  # 1
            lint_quality=Rating.POOR,  # 1
            code_quality=Rating.POOR,  # 1
            output_validity=Rating.POOR,  # 1
            question_efficiency=Rating.POOR,  # 1
        )
        assert score.total == 5
        assert score.grade == "Failure"

    def test_grade_partial(self):
        """Test that scores 6-9 get 'Partial' grade."""
        score = Score(
            completeness=Rating.GOOD,  # 2
            lint_quality=Rating.GOOD,  # 2
            code_quality=Rating.POOR,  # 1
            output_validity=Rating.POOR,  # 1
            question_efficiency=Rating.NONE,  # 0
        )
        assert score.total == 6
        assert score.grade == "Partial"

        score2 = Score(
            completeness=Rating.EXCELLENT,  # 3
            lint_quality=Rating.POOR,  # 1
            code_quality=Rating.POOR,  # 1
            output_validity=Rating.GOOD,  # 2
            question_efficiency=Rating.NONE,  # 0
        )
        assert score2.total == 7

    def test_grade_success(self):
        """Test that scores 10-12 get 'Success' grade."""
        score = Score(
            completeness=Rating.GOOD,  # 2
            lint_quality=Rating.GOOD,  # 2
            code_quality=Rating.GOOD,  # 2
            output_validity=Rating.GOOD,  # 2
            question_efficiency=Rating.GOOD,  # 2
        )
        assert score.total == 10
        assert score.grade == "Success"

    def test_grade_excellent(self):
        """Test that scores 13-15 get 'Excellent' grade."""
        score = Score(
            completeness=Rating.EXCELLENT,  # 3
            lint_quality=Rating.EXCELLENT,  # 3
            code_quality=Rating.EXCELLENT,  # 3
            output_validity=Rating.GOOD,  # 2
            question_efficiency=Rating.GOOD,  # 2
        )
        assert score.total == 13
        assert score.grade == "Excellent"

    def test_passed_returns_true_when_total_gte_6(self):
        """Test that Score.passed returns True when total >= 6."""
        score = Score(
            completeness=Rating.GOOD,
            lint_quality=Rating.GOOD,
            code_quality=Rating.GOOD,
            output_validity=Rating.NONE,
            question_efficiency=Rating.NONE,
        )
        assert score.total == 6
        assert score.passed is True

    def test_passed_returns_false_when_total_lt_6(self):
        """Test that Score.passed returns False when total < 6."""
        score = Score(
            completeness=Rating.POOR,
            lint_quality=Rating.POOR,
            code_quality=Rating.POOR,
            output_validity=Rating.POOR,
            question_efficiency=Rating.POOR,
        )
        assert score.total == 5
        assert score.passed is False


class TestScoreCompleteness:
    """Tests for score_completeness function."""

    def test_no_package_produced(self):
        """Test that NONE is returned when no package is produced."""
        rating = score_completeness(produced_package=False, missing_resources=0, total_resources=5)
        assert rating == Rating.NONE

    def test_all_resources_present(self):
        """Test that EXCELLENT is returned when all resources are present."""
        rating = score_completeness(produced_package=True, missing_resources=0, total_resources=5)
        assert rating == Rating.EXCELLENT

    def test_most_resources_present(self):
        """Test that GOOD is returned when most resources are present."""
        rating = score_completeness(produced_package=True, missing_resources=1, total_resources=5)
        assert rating == Rating.GOOD

    def test_many_resources_missing(self):
        """Test that POOR is returned when many resources are missing."""
        rating = score_completeness(produced_package=True, missing_resources=3, total_resources=5)
        assert rating == Rating.POOR


class TestScoreLintQuality:
    """Tests for score_lint_quality function."""

    def test_lint_never_passed(self):
        """Test that NONE is returned when lint never passed."""
        rating = score_lint_quality(cycles=3, passed=False)
        assert rating == Rating.NONE

    def test_lint_passed_first_try(self):
        """Test that EXCELLENT is returned when lint passed on first try."""
        rating = score_lint_quality(cycles=0, passed=True)
        assert rating == Rating.EXCELLENT

    def test_lint_passed_after_1_cycle(self):
        """Test that GOOD is returned when lint passed after 1 cycle."""
        rating = score_lint_quality(cycles=1, passed=True)
        assert rating == Rating.GOOD

    def test_lint_passed_after_2_cycles(self):
        """Test that GOOD is returned when lint passed after 2 cycles."""
        rating = score_lint_quality(cycles=2, passed=True)
        assert rating == Rating.GOOD

    def test_lint_passed_after_3_cycles(self):
        """Test that POOR is returned when lint passed after 3+ cycles."""
        rating = score_lint_quality(cycles=3, passed=True)
        assert rating == Rating.POOR


class TestScoreCodeQuality:
    """Tests for score_code_quality function."""

    def test_invalid_syntax(self):
        """Test that NONE is returned when syntax is invalid."""
        rating = score_code_quality(syntax_valid=False, pattern_issues=0)
        assert rating == Rating.NONE

    def test_no_pattern_issues(self):
        """Test that EXCELLENT is returned when there are no pattern issues."""
        rating = score_code_quality(syntax_valid=True, pattern_issues=0)
        assert rating == Rating.EXCELLENT

    def test_few_pattern_issues(self):
        """Test that GOOD is returned when there are few pattern issues."""
        rating = score_code_quality(syntax_valid=True, pattern_issues=1)
        assert rating == Rating.GOOD

        rating = score_code_quality(syntax_valid=True, pattern_issues=2)
        assert rating == Rating.GOOD

    def test_many_pattern_issues(self):
        """Test that POOR is returned when there are many pattern issues."""
        rating = score_code_quality(syntax_valid=True, pattern_issues=3)
        assert rating == Rating.POOR


class TestScoreOutputValidity:
    """Tests for score_output_validity function."""

    def test_invalid_output(self):
        """Test that NONE is returned when output is invalid."""
        rating = score_output_validity(valid=False, errors=5, warnings=2)
        assert rating == Rating.NONE

    def test_valid_with_no_errors_or_warnings(self):
        """Test that EXCELLENT is returned when valid with no errors or warnings."""
        rating = score_output_validity(valid=True, errors=0, warnings=0)
        assert rating == Rating.EXCELLENT

    def test_valid_with_warnings_only(self):
        """Test that GOOD is returned when valid with warnings but no errors."""
        rating = score_output_validity(valid=True, errors=0, warnings=3)
        assert rating == Rating.GOOD

    def test_valid_with_errors(self):
        """Test that POOR is returned when valid but has errors."""
        rating = score_output_validity(valid=True, errors=1, warnings=0)
        assert rating == Rating.POOR


class TestScoreQuestionEfficiency:
    """Tests for score_question_efficiency function."""

    def test_no_questions_when_none_needed(self):
        """Test that EXCELLENT is returned when no questions asked and none needed."""
        rating = score_question_efficiency(questions=0, appropriate_questions=0)
        assert rating == Rating.EXCELLENT

    def test_1_question(self):
        """Test that GOOD is returned for 1-2 questions."""
        rating = score_question_efficiency(questions=1, appropriate_questions=1)
        assert rating == Rating.GOOD

    def test_2_questions(self):
        """Test that GOOD is returned for 1-2 questions."""
        rating = score_question_efficiency(questions=2, appropriate_questions=2)
        assert rating == Rating.GOOD

    def test_3_questions(self):
        """Test that POOR is returned for 3-4 questions."""
        rating = score_question_efficiency(questions=3, appropriate_questions=2)
        assert rating == Rating.POOR

    def test_4_questions(self):
        """Test that POOR is returned for 3-4 questions."""
        rating = score_question_efficiency(questions=4, appropriate_questions=3)
        assert rating == Rating.POOR

    def test_5_plus_questions(self):
        """Test that NONE is returned for 5+ questions."""
        rating = score_question_efficiency(questions=5, appropriate_questions=4)
        assert rating == Rating.NONE


class TestCalculateScore:
    """Tests for calculate_score integration function."""

    def test_perfect_score(self):
        """Test calculation of a perfect score."""
        score = calculate_score(
            produced_package=True,
            missing_resources=0,
            total_resources=5,
            lint_cycles=0,
            lint_passed=True,
            syntax_valid=True,
            pattern_issues=0,
            output_valid=True,
            validation_errors=0,
            validation_warnings=0,
            questions_asked=0,
            appropriate_questions=0,
        )
        assert score.total == 15
        assert score.grade == "Excellent"
        assert score.passed is True

    def test_failing_score(self):
        """Test calculation of a failing score."""
        score = calculate_score(
            produced_package=False,
            missing_resources=5,
            total_resources=5,
            lint_cycles=5,
            lint_passed=False,
            syntax_valid=False,
            pattern_issues=10,
            output_valid=False,
            validation_errors=5,
            validation_warnings=3,
            questions_asked=10,
            appropriate_questions=2,
        )
        assert score.total == 0
        assert score.grade == "Failure"
        assert score.passed is False

    def test_partial_score(self):
        """Test calculation of a partial success score."""
        score = calculate_score(
            produced_package=True,
            missing_resources=1,
            total_resources=5,
            lint_cycles=2,
            lint_passed=True,
            syntax_valid=True,
            pattern_issues=1,
            output_valid=True,
            validation_errors=1,
            validation_warnings=0,
            questions_asked=3,
            appropriate_questions=2,
        )
        assert score.completeness == Rating.GOOD
        assert score.lint_quality == Rating.GOOD
        assert score.code_quality == Rating.GOOD
        assert score.output_validity == Rating.POOR
        assert score.question_efficiency == Rating.POOR
        assert score.total == 8
        assert score.grade == "Partial"
        assert score.passed is True
