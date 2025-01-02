# -*- coding: utf-8 -*-
from contextlib import nullcontext as does_not_raise
import datetime

import pytest

from requests import Request

from bookops_sierra.errors import BookopsSierraError
from bookops_sierra.query import Query


def test_query_not_prepared_request(mock_session):
    with pytest.raises(TypeError) as exc:
        req = Request("GET", "https://foo.org")
        Query(mock_session, req, timeout=2)
    assert "Invalid type for argument 'prepared_request'." in str(exc.value)


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


# Most likely not needed, check server response codes
# @pytest.mark.http_code(201)
# def test_query_http_201_response(mock_session, mock_session_response):
#     with does_not_raise():
#         req = Request("GET", "https://foo.org")
#         prepped = mock_session.prepare_request(req)
#         query = Query(mock_session, prepped)
#         assert query.response.status_code == 201


# @pytest.mark.http_code(404)
# def test_query_http_404_response(mock_session, mock_session_response):
#     header = {"Accept": "application/json"}
#     url = "https://metadata.api.oclc.org/worldcat/search/brief-bibs/41266045"
#     req = Request("GET", url, headers=header, hooks=None)
#     prepped = mock_session.prepare_request(req)

#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert (
#         "404 Client Error: 'foo' for url: https://foo.bar?query. Server response: spam"
#         in str(exc.value)
#     )


# @pytest.mark.http_code(500)
# def test_query_http_500_response(mock_session, mock_session_response):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert (
#         "500 Server Error: 'foo' for url: https://foo.bar?query. Server response: spam"
#         in str(exc.value)
#     )


# def test_query_timeout_exception(mock_session, mock_timeout):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert "Connection Error: <class 'requests.exceptions.Timeout'>" in str(exc.value)


# def test_query_connection_exception(mock_session, mock_connection_error):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert "Connection Error: <class 'requests.exceptions.ConnectionError'>" in str(
#         exc.value
#     )


# def test_query_retry_exception(mock_session, mock_retry_error):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert "Connection Error: <class 'requests.exceptions.RetryError'>" in str(
#         exc.value
#     )


# def test_query_unexpected_exception(mock_session, mock_unexpected_error):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError) as exc:
#         Query(mock_session, prepped)

#     assert "Unexpected request error: <class 'Exception'>" in str(exc.value)


# def test_query_timeout_retry(stub_retry_session, caplog):
#     req = Request("GET", "https://foo.org")
#     prepped = stub_retry_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError):
#         Query(stub_retry_session, prepped)

#     assert "Retry(total=0, " in caplog.records[2].message
#     assert "Retry(total=1, " in caplog.records[1].message
#     assert "Retry(total=2, " in caplog.records[0].message


# def test_query_timeout_no_retry(mock_session, caplog):
#     req = Request("GET", "https://foo.org")
#     prepped = mock_session.prepare_request(req)
#     with pytest.raises(WorldcatRequestError):
#         Query(mock_session, prepped)

#     assert "Retry" not in caplog.records
