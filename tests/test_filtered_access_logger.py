from typing import List

import pytest

from sag_py_web_common.filtered_access_logger import \
    FilteredAccessLoggerMiddleware


@pytest.mark.parametrize("path,expected", [
    ("/api/maintain/serviceStatus", True),
    ("/api/maintain/serviceStatusKubernetes", True),
    ("/api/maintain/serviceStatusPrtg", True),
    ("/maintain/serviceStatus", True),
    ("/maintain/serviceStatusKubernetes", True),
    ("/maintain/serviceStatusPrtg", True),
    ("/health/serviceStatus", True),
    ("/health/serviceStatusKubernetes", True),
    ("/health/serviceStatusPrtg", True),
    ("/otherEndpoint/serviceStatus", False),
    ("/serviceStatus", False),
    ("/my/other/endpoint", False),
    ("/", False)
])
def test_is_excluded_path_with_ignore_list(path: str, expected: bool) -> None:
    # Arrange
    excluded_pathes = ["maintain/serviceStatus", "health/serviceStatus"]
    scope = {"path": path}

    # Act
    actual = FilteredAccessLoggerMiddleware._is_excluded_path(scope, excluded_pathes)  # type: ignore

    # Assert
    assert actual == expected


@pytest.mark.parametrize("path,expected", [
    ("/serviceStatus", False),
    ("/my/other/endpoint", False),
    ("/", False)
])
def test_is_excluded_path_without_ignore_list(path: str, expected: bool) -> None:
    # Arrange
    excluded_pathes = None
    scope = {"path": path}

    # Act
    actual = FilteredAccessLoggerMiddleware._is_excluded_path(scope, excluded_pathes)  # type: ignore

    # Assert
    assert actual == expected


@pytest.mark.parametrize("path,expected", [
    ("/serviceStatus", False),
    ("/my/other/endpoint", False),
    ("/", False)
])
def test_is_excluded_path_with_empty_ignore_list(path: str, expected: bool) -> None:
    # Arrange
    excluded_pathes: List[str] = []
    scope = {"path": path}

    # Act
    actual = FilteredAccessLoggerMiddleware._is_excluded_path(scope, excluded_pathes)  # type: ignore

    # Assert
    assert actual == expected
