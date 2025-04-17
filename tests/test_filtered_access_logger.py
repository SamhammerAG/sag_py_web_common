import logging
from typing import List

import pytest
from asgiref.typing import ASGI3Application
from fastapi import FastAPI
from starlette.testclient import TestClient

from sag_py_web_common.filtered_access_logger import FilteredAccessLoggerMiddleware

app = FastAPI()
app.add_middleware(
    FilteredAccessLoggerMiddleware,
    format="%(client_addr)s - %(request_line)s %(status_code)s",
    logger=logging.getLogger("access"),
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the root URL"}


client = TestClient(app)


@pytest.mark.parametrize(
    "path, ignored_headers, isLogged",
    [
        ("/metrics", [(b"Exclude-Logging", b"")], False),
        ("/maintain/serviceStatusKubernetes", [], False),
        ("/maintain/serviceStatusPrtg", [], False),
        ("/health/serviceStatusKubernetes", [], False),
        ("/health/serviceStatusPrtg", [], False),
        ("/otherEndpoint/serviceStatus", [], True),
        ("/my/other/endpoint", [], True),
        ("/", [], True),
    ],
)
def test_logs_can_be_ignored_via_path_and_header(
    path: str, ignored_headers: list[tuple[bytes, bytes]], isLogged: bool
) -> None:
    exclude_header = "exclude-logging"
    excluded_paths = ["maintain/serviceStatus", "health/serviceStatus"]
    mock_app: ASGI3Application = lambda scope, receive, send: None  # type: ignore
    middleware = FilteredAccessLoggerMiddleware(
        app=mock_app, format=None, logger=None, excluded_paths=excluded_paths, exclude_header=exclude_header
    )

    scope = {"type": "http", "path": path, "headers": ignored_headers}

    actual = middleware._should_log(scope)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == isLogged


@pytest.mark.parametrize(
    "path,pathIsIgnored",
    [
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
        ("/", False),
    ],
)
def test_excluding_log_via_path_is_possible(path: str, pathIsIgnored: bool) -> None:
    excluded_paths = ["maintain/serviceStatus", "health/serviceStatus"]
    scope = {"path": path}

    actual = FilteredAccessLoggerMiddleware._is_excluded_via_path(scope, excluded_paths)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == pathIsIgnored


@pytest.mark.parametrize("path,pathIsIgnored", [("/serviceStatus", False), ("/my/other/endpoint", False), ("/", False)])
def test_not_configured_excluded_paths_does_not_cause_any_logs_to_be_excluded(path: str, pathIsIgnored: bool) -> None:
    excluded_paths = None
    scope = {"path": path}

    actual = FilteredAccessLoggerMiddleware._is_excluded_via_path(scope, excluded_paths)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == pathIsIgnored


@pytest.mark.parametrize("path,pathIsIgnored", [("/serviceStatus", False), ("/my/other/endpoint", False), ("/", False)])
def test_empty_excludes_paths_does_not_cause_any_logs_to_be_excluded(path: str, pathIsIgnored: bool) -> None:
    excluded_paths: List[str] = []
    scope = {"path": path}

    actual = FilteredAccessLoggerMiddleware._is_excluded_via_path(scope, excluded_paths)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == pathIsIgnored


@pytest.mark.parametrize(
    "headers,path_is_ignored",
    [
        ([(b"Exclude-Logging", b"")], True),
        ([(b"exClUDe-loGGing", b"")], True),
        ([(b"Exclude-Logging", b"thisValueIsIrrelevant")], True),
        ([(b"some-incorrect-header", b"")], False),
        ([], False),
    ],
)
def test_excluding_logs_via_header_is_possible(headers: list[tuple[bytes, bytes]], path_is_ignored: bool) -> None:
    exclude_header = "exclude-logging"
    scope = {
        "headers": headers,
    }

    actual = FilteredAccessLoggerMiddleware._is_excluded_via_header(scope, exclude_header)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == path_is_ignored


@pytest.mark.parametrize("headers,path_is_ignored", [([(b"Exclude-Logging", b"")], False), ([], False)])
def test_not_configured_exclude_header_does_not_cause_any_logs_to_be_excluded(
    headers: list[tuple[bytes, bytes]], path_is_ignored: bool
) -> None:
    exclude_header = ""
    scope = {"headers": headers}

    actual = FilteredAccessLoggerMiddleware._is_excluded_via_header(scope, exclude_header)  # type: ignore # pylint: disable=W0212:protected-access

    assert actual == path_is_ignored
