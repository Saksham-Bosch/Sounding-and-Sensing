from __future__ import annotations

import pytest

from tests.helpers.configuration import get_test_settings


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip live API tests unless explicitly enabled."""
    settings = get_test_settings()
    if settings.api_test_allow_live_calls:
        return

    skip_live = pytest.mark.skip(reason="live API tests are disabled; set API_TEST_ALLOW_LIVE_CALLS=true")
    for item in items:
        if "live_api" in item.keywords:
            item.add_marker(skip_live)
