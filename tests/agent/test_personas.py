"""Tests for agent.personas module."""

import pytest

from wetwire_core.agent.personas import (
    BEGINNER,
    EXPERT,
    INTERMEDIATE,
    PERSONAS,
    TERSE,
    VERBOSE,
    Persona,
    load_persona,
)


class TestPersona:
    """Tests for Persona dataclass."""

    def test_persona_creation(self):
        """Test that Persona can be created with all fields."""
        persona = Persona(
            name="test",
            description="Test persona",
            system_prompt="You are a test persona.",
            traits=["trait1", "trait2"],
        )
        assert persona.name == "test"
        assert persona.description == "Test persona"
        assert persona.system_prompt == "You are a test persona."
        assert persona.traits == ["trait1", "trait2"]


class TestLoadPersona:
    """Tests for load_persona function."""

    def test_load_beginner(self):
        """Test loading BEGINNER persona."""
        persona = load_persona("beginner")
        assert persona.name == "beginner"
        assert persona.description == "Vague requirements, defers to suggestions"
        assert "beginner user" in persona.system_prompt.lower()
        assert "vague" in persona.traits

    def test_load_intermediate(self):
        """Test loading INTERMEDIATE persona."""
        persona = load_persona("intermediate")
        assert persona.name == "intermediate"
        assert persona.description == "Mixed clarity, asks clarifying questions"
        assert "intermediate user" in persona.system_prompt.lower()
        assert "generally_clear" in persona.traits

    def test_load_expert(self):
        """Test loading EXPERT persona."""
        persona = load_persona("expert")
        assert persona.name == "expert"
        assert persona.description == "Precise requirements, corrects mistakes"
        assert "expert user" in persona.system_prompt.lower()
        assert "precise" in persona.traits

    def test_load_terse(self):
        """Test loading TERSE persona."""
        persona = load_persona("terse")
        assert persona.name == "terse"
        assert persona.description == "Minimal responses"
        assert "terse user" in persona.system_prompt.lower()
        assert "minimal" in persona.traits

    def test_load_verbose(self):
        """Test loading VERBOSE persona."""
        persona = load_persona("verbose")
        assert persona.name == "verbose"
        assert persona.description == "Over-explains, adds tangents"
        assert "verbose user" in persona.system_prompt.lower()
        assert "wordy" in persona.traits

    def test_load_invalid_persona_raises_error(self):
        """Test that loading an invalid persona raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            load_persona("nonexistent")
        assert "Unknown persona 'nonexistent'" in str(exc_info.value)
        assert "beginner" in str(exc_info.value)


class TestBuiltInPersonas:
    """Tests for built-in persona constants."""

    def test_beginner_attributes(self):
        """Test BEGINNER persona has correct attributes."""
        assert BEGINNER.name == "beginner"
        assert BEGINNER.description == "Vague requirements, defers to suggestions"
        assert len(BEGINNER.system_prompt) > 0
        assert len(BEGINNER.traits) == 3
        assert all(isinstance(trait, str) for trait in BEGINNER.traits)

    def test_intermediate_attributes(self):
        """Test INTERMEDIATE persona has correct attributes."""
        assert INTERMEDIATE.name == "intermediate"
        assert INTERMEDIATE.description == "Mixed clarity, asks clarifying questions"
        assert len(INTERMEDIATE.system_prompt) > 0
        assert len(INTERMEDIATE.traits) == 3
        assert all(isinstance(trait, str) for trait in INTERMEDIATE.traits)

    def test_expert_attributes(self):
        """Test EXPERT persona has correct attributes."""
        assert EXPERT.name == "expert"
        assert EXPERT.description == "Precise requirements, corrects mistakes"
        assert len(EXPERT.system_prompt) > 0
        assert len(EXPERT.traits) == 3
        assert all(isinstance(trait, str) for trait in EXPERT.traits)

    def test_terse_attributes(self):
        """Test TERSE persona has correct attributes."""
        assert TERSE.name == "terse"
        assert TERSE.description == "Minimal responses"
        assert len(TERSE.system_prompt) > 0
        assert len(TERSE.traits) == 3
        assert all(isinstance(trait, str) for trait in TERSE.traits)

    def test_verbose_attributes(self):
        """Test VERBOSE persona has correct attributes."""
        assert VERBOSE.name == "verbose"
        assert VERBOSE.description == "Over-explains, adds tangents"
        assert len(VERBOSE.system_prompt) > 0
        assert len(VERBOSE.traits) == 3
        assert all(isinstance(trait, str) for trait in VERBOSE.traits)

    def test_all_personas_in_registry(self):
        """Test that all built-in personas are in the PERSONAS registry."""
        assert "beginner" in PERSONAS
        assert "intermediate" in PERSONAS
        assert "expert" in PERSONAS
        assert "terse" in PERSONAS
        assert "verbose" in PERSONAS
        assert len(PERSONAS) == 5

    def test_personas_registry_values(self):
        """Test that PERSONAS registry contains correct persona objects."""
        assert PERSONAS["beginner"] is BEGINNER
        assert PERSONAS["intermediate"] is INTERMEDIATE
        assert PERSONAS["expert"] is EXPERT
        assert PERSONAS["terse"] is TERSE
        assert PERSONAS["verbose"] is VERBOSE
