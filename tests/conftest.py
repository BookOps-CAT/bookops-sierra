# -*- coding: utf-8 -*-

import datetime
import os
import json
from typing import Generator

import pytest
import requests


from bookops_sierra import SierraToken, SierraSession
from bookops_sierra.errors import BookopsSierraError


class FakeUtcNow(datetime.datetime):
    @classmethod
    def now(cls, tzinfo=datetime.timezone.utc) -> "FakeUtcNow":
        return cls(2019, 1, 1, 17, 0, 0, tzinfo=datetime.timezone.utc)


class MockUnexpectedException:
    def __init__(self, *args, **kwargs) -> None:
        raise Exception


class MockTimeout:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.Timeout


class MockConnectionError:
    def __init__(self, *args, **kwargs) -> None:
        raise requests.exceptions.ConnectionError


class MockBookopsSierraError:
    def __init__(self, *args, **kwargs) -> None:
        raise BookopsSierraError


class MockAuthServerResponseSuccess:
    """Simulates oauth server response to successful token request"""

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "access_token": "token_string_here",
            "token_type": "bearer",
            "expires_in": 3600,
        }


class MockAuthServerResponseFailure:
    """Simulates oauth server response to successful token request"""

    def __init__(self):
        self.status_code = 400

    def json(self):
        return {"error": "No grant_type specified", "error_description": None}


class MockHTTPSessionResponse(requests.Response):
    def __init__(self, http_code) -> None:
        self.status_code = http_code
        self.reason = "'foo'"
        self.url = "https://foo.bar?query"
        self._content = b"spam"


@pytest.fixture
def mock_successful_post_token_response(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseSuccess()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_failed_post_token_response(monkeypatch):
    def mock_oauth_server_response(*args, **kwargs):
        return MockAuthServerResponseFailure()

    monkeypatch.setattr(requests, "post", mock_oauth_server_response)


@pytest.fixture
def mock_session_response(request, monkeypatch) -> None:
    """
    Use together with `pytest.mark.http_code` decorator to pass
    specific HTTP code to be returned to simulate various
    responses from different endpoints
    """
    marker = request.node.get_closest_marker("http_code")
    if marker is None:
        http_code = 200
    else:
        http_code = marker.args[0]

    def mock_api_response(*args, http_code=http_code, **kwargs):
        return MockHTTPSessionResponse(http_code=http_code)

    monkeypatch.setattr(requests.Session, "send", mock_api_response)
    monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def mock_token(mock_successful_post_token_response):
    return SierraToken("my_client", "my_secret", "https://sierra_url.org")


@pytest.fixture
def mock_unexpected_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockUnexpectedException)
    monkeypatch.setattr("requests.Session.get", MockUnexpectedException)
    monkeypatch.setattr("requests.Session.send", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.post", MockTimeout)
    monkeypatch.setattr("requests.get", MockTimeout)
    monkeypatch.setattr("requests.Session.get", MockTimeout)
    monkeypatch.setattr("requests.Session.send", MockTimeout)


@pytest.fixture
def mock_connection_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockConnectionError)
    monkeypatch.setattr("requests.Session.get", MockConnectionError)


@pytest.fixture
def mock_bookopssierra_error(monkeypatch):
    monkeypatch.setattr("requests.Session.get", MockBookopsSierraError)


@pytest.fixture
def mock_datetime_now(monkeypatch):
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


@pytest.fixture
def mock_session(mock_token) -> Generator[SierraSession, None, None]:
    with SierraSession(authorization=mock_token, delay=None) as session:
        yield session


@pytest.fixture(scope="module")
def live_keys():
    # the credentials must be for Sierra TEST/TRAINING server
    # NEVER USE for the production server!
    if os.name == "nt":
        fh = os.path.join(os.environ["USERPROFILE"], ".cred/.sierra/sierra-dev.json")
        with open(fh, "r") as file:
            data = json.load(file)
            os.environ["SIERRA_CLIENT"] = data["client_id"]
            os.environ["SIERRA_SECRET"] = data["client_secret"]
            os.environ["SIERRA_SERVER"] = data["host_url"]
            os.environ["SIERRA_AGENT"] = data["agent"]

    else:
        # Github Actions env variables defined in the repository settings
        pass


@pytest.fixture(scope="module")
def live_session(live_keys):
    # live session on the TEST server
    token = SierraToken(
        client_id=os.environ["SIERRA_CLIENT"],
        client_secret=os.environ["SIERRA_SECRET"],
        host_url=os.environ["SIERRA_SERVER"],
        agent="Tests",
    )
    with SierraSession(authorization=token) as session:
        yield session
