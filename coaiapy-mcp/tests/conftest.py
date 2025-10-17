"""
Pytest configuration for coaiapy-mcp tests
"""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (may require external services)"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests (no external dependencies)"
    )
