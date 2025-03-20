# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
import datetime
import time

import pytest

from requests import Request

from bookops_sierra.errors import BookopsSierraError
from bookops_sierra.query import Query


def test_query_not_prepared_request(mock_session):
    with pytest.raises(TypeError) as exc:
        req = Request("GET", "https://foo.org")
        Query(mock_session, req, timeout=2)
    assert "Invalid type for argument 'prepared_request'." in str(exc.value)


def test_query_delay(mock_session, mock_session_response):
    mock_session.delay = 3
    req = Request("GET", "https://foo.org")
    prepped = mock_session.prepare_request(req)
    start = time.time()
    Query(mock_session, prepped)
    end = time.time()
    assert end - start >= mock_session.delay


@pytest.mark.http_code(200)
def test_query_with_stale_token(mock_session, mock_session_response):
    mock_session.authorization.expires_on = datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.timedelta(0, 1)
    assert mock_session.authorization.is_expired() is True

    req = Request("GET", "http://foo.org")
    prepped = mock_session.prepare_request(req)
    query = Query(mock_session, prepped)
    assert mock_session.authorization.is_expired() is False
    assert query.response.status_code == 200


@pytest.mark.http_code(200)
def test_query_http_200_response(mock_session, mock_session_response):
    with does_not_raise():
        req = Request("GET", "https://foo.org")
        prepped = mock_session.prepare_request(req)
        query = Query(mock_session, prepped)
        assert query.response.status_code == 200


@pytest.mark.http_code(500)
def test_query_http_500_response(mock_session, mock_session_response):
    req = Request("GET", "https://foo.org")
    prepped = mock_session.prepare_request(req)
    with pytest.raises(BookopsSierraError) as exc:
        Query(mock_session, prepped)

    assert (
        "500 Server Error: 'foo' for url: https://foo.bar?query. Server response: spam"
        in str(exc.value)
    )


def test_query_timeout_exception(mock_session, mock_timeout):
    req = Request("GET", "https://foo.org")
    prepped = mock_session.prepare_request(req)
    with pytest.raises(BookopsSierraError) as exc:
        Query(mock_session, prepped)

    assert "Connection Error: <class 'requests.exceptions.Timeout'>" in str(exc.value)


def test_query_connection_exception(mock_session, mock_connection_error):
    req = Request("GET", "https://foo.org")
    prepped = mock_session.prepare_request(req)
    with pytest.raises(BookopsSierraError) as exc:
        Query(mock_session, prepped)

    assert "Connection Error: <class 'requests.exceptions.ConnectionError'>" in str(
        exc.value
    )


def test_query_unexpected_exception(mock_session, mock_unexpected_error):
    req = Request("GET", "https://foo.org")
    prepped = mock_session.prepare_request(req)
    with pytest.raises(BookopsSierraError) as exc:
        Query(mock_session, prepped)

    assert "Unexpected request error: <class 'Exception'>" in str(exc.value)
