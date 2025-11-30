"""Tests for enum utilities."""

import pytest

from src.utilities.enums import Environment
from src.utilities.enums import Language
from src.utilities.enums import Platform


class TestEnvironment:
    """Tests for Environment enum."""

    def test_development_value(self):
        """Test DEVELOPMENT enum value."""
        assert Environment.DEVELOPMENT.value == "development"

    def test_testing_value(self):
        """Test TESTING enum value."""
        assert Environment.TESTING.value == "testing"

    def test_staging_value(self):
        """Test STAGING enum value."""
        assert Environment.STAGING.value == "staging"

    def test_production_value(self):
        """Test PRODUCTION enum value."""
        assert Environment.PRODUCTION.value == "production"

    def test_missing_returns_development(self):
        """Test that invalid value returns DEVELOPMENT."""
        assert Environment("invalid") == Environment.DEVELOPMENT

    def test_empty_returns_development(self):
        """Test that empty value returns DEVELOPMENT."""
        assert Environment("") == Environment.DEVELOPMENT


class TestLanguage:
    """Tests for Language enum."""

    def test_all_language_values(self):
        """Test all language enum values."""
        assert Language.AR.value == "ar"
        assert Language.DE.value == "de"
        assert Language.EN.value == "en"
        assert Language.ES.value == "es"
        assert Language.FR.value == "fr"
        assert Language.RU.value == "ru"
        assert Language.IT.value == "it"

    def test_from_code_valid(self):
        """Test from_code with valid codes."""
        assert Language.from_code("en") == Language.EN
        assert Language.from_code("ar") == Language.AR
        assert Language.from_code("de") == Language.DE

    def test_from_code_with_locale(self):
        """Test from_code with locale codes (e.g., en-US)."""
        assert Language.from_code("en-US") == Language.EN
        assert Language.from_code("ar-SA") == Language.AR
        assert Language.from_code("de-DE") == Language.DE

    def test_from_code_uppercase(self):
        """Test from_code handles uppercase."""
        assert Language.from_code("EN") == Language.EN
        assert Language.from_code("AR") == Language.AR

    def test_from_code_invalid(self):
        """Test from_code returns EN for invalid codes."""
        assert Language.from_code("xx") == Language.EN
        assert Language.from_code("invalid") == Language.EN

    def test_from_code_empty(self):
        """Test from_code returns EN for empty string."""
        assert Language.from_code("") == Language.EN

    def test_from_code_none(self):
        """Test from_code returns EN for None."""
        assert Language.from_code(None) == Language.EN

    def test_missing_returns_en(self):
        """Test that invalid direct lookup returns EN."""
        assert Language("invalid") == Language.EN

    def test_display_name(self):
        """Test display_name property returns native names."""
        assert Language.AR.display_name == "العربية"
        assert Language.DE.display_name == "Deutsch"
        assert Language.EN.display_name == "English"
        assert Language.ES.display_name == "Español"
        assert Language.FR.display_name == "Français"
        assert Language.RU.display_name == "Русский"
        assert Language.IT.display_name == "Italiano"

class TestPlatform:
    """Tests for Platform enum."""

    def test_admin_value(self):
        """Test ADMIN enum value."""
        assert Platform.ADMIN.value == "admin"

    def test_customer_value(self):
        """Test CUSTOMER enum value."""
        assert Platform.CUSTOMER.value == "customer"

