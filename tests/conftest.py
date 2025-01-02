# -*- coding: utf-8 -*-

import datetime
import os
import json
from typing import Generator

import pytest
import requests


from bookops_sierra import SierraToken, SierraSession
from bookops_sierra.errors import BookopsSierraError


class FakeDate(datetime.datetime):
    @classmethod
    def now(cls, tzinfo=datetime.timezone.utc) -> "FakeUtcNow":
        return cls(2019, 1, 1, 17, 0, 0, tzinfo=datetime.timezone.utc)


class MockUnexpectedException:
    def __init__(self, *args, **kwargs):
        raise Exception


class MockTimeout:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.Timeout


class MockConnectionError:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.ConnectionError


class MockBookopsSierraError:
    def __init__(self, *args, **kwargs):
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


# class MockSuccessfulHTTP200SessionResponse:
#     def __init__(self):
#         self.status_code = 200


class MockAuthServerResponseFailure:
    """Simulates oauth server response to successful token request"""

    def __init__(self):
        self.status_code = 400

    def json(self):
        return {"error": "No grant_type specified", "error_description": None}


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


# @pytest.fixture
# def mock_successful_session_get_response(monkeypatch):
#     def mock_api_response(*args, **kwargs):
#         return MockSuccessfulHTTP200SessionResponse()

#     monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def mock_token(mock_successful_post_token_response):
    return SierraToken("my_client", "my_secret", "sierra_url")


@pytest.fixture
def mock_unexpected_error(monkeypatch):
    monkeypatch.setattr("requests.post", MockUnexpectedException)
    monkeypatch.setattr("requests.Session.get", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.post", MockTimeout)
    monkeypatch.setattr("requests.Session.get", MockTimeout)


@pytest.fixture
def mock_connectionerror(monkeypatch):
    monkeypatch.setattr("requests.post", MockConnectionError)
    monkeypatch.setattr("requests.Session.get", MockConnectionError)


@pytest.fixture
def mock_bookopssierraerror(monkeypatch):
    monkeypatch.setattr("requests.Session.get", MockBookopsSierraError)


@pytest.fixture
def mock_datetime_now(monkeypatch):
    monkeypatch.setattr(datetime, "datetime", FakeDate)


@pytest.fixture
def mock_session(mock_token) -> Generator[SierraSession, None, None]:
    with SierraSession(authorization=mock_token) as session:
        yield session


@pytest.fixture
def live_keys():
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
