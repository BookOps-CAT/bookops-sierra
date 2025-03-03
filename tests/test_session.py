# -*- coding: utf-8 -*-

"""
bookops_sierra.session testing
"""
from contextlib import nullcontext as does_not_raise
import datetime
import pytest

from bookops_sierra import __title__, __version__

from bookops_sierra.errors import BookopsSierraError
from bookops_sierra.session import SierraSession


class TestSierraSession:
    """
    Test of the SierraSession
    """

    def test_authorization_invalid_argument(self):
        err_msg = "Invalid authorization. Argument must be an instance of `SierraToken` object."  # noqa:E501
        with pytest.raises(BookopsSierraError) as exc:
            SierraSession("my_token")
        assert err_msg in str(exc.value)

    def test_default_agent_parameter(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session.headers["User-Agent"] == f"{__title__}/{__version__}"

    def test_default_timeout_parameter(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session.timeout == (5, 5)

    def test_custom_timeout_parameter(self, mock_token):
        with SierraSession(authorization=mock_token, timeout=1.5) as session:
            assert session.timeout == 1.5

    def test_bibs_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_endpoint
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/"
            )

    def test_items_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._items_endpoint
                == "https://sierra_url.org/iii/sierra-api/v6/items/"
            )

    def test_bibs_endpoint_custom_api_version(self, mock_token):
        mock_token.api_version = "v4"
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_endpoint
                == "https://sierra_url.org/iii/sierra-api/v4/bibs/"
            )

    def test_bibs_marc_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_marc_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/marc"
            )

    def test_bibs_metadata_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_metadata_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/metadata"
            )

    def test_bibs_query_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_query_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/query"
            )

    def test_bibs_search_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_search_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/search"
            )

    def test_bib_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bib_endpoint("123")
                == "https://sierra_url.org/iii/sierra-api/v6/bibs/123"
            )

    def test_items_checkouts_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._items_checkouts_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/items/checkouts"
            )

    def test_items_query_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._items_query_endpoint()
                == "https://sierra_url.org/iii/sierra-api/v6/items/query"
            )

    def test_item_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._item_endpoint("123")
                == "https://sierra_url.org/iii/sierra-api/v6/items/123"
            )

    def test_fetch_new_token(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session.authorization.is_expired() is False
            # force stale token
            session.authorization.expires_on = datetime.datetime.now(
                datetime.timezone.utc
            ) - datetime.timedelta(seconds=1)
            # verify token is expired
            assert session.authorization.is_expired() is True

            # fetch new one and retests
            session._fetch_new_token()
            assert session.authorization.is_expired() is False

    def test_fetch_new_token_exceptions(self, mock_token, mock_timeout):
        with SierraSession(authorization=mock_token) as session:
            with pytest.raises(BookopsSierraError):
                session._fetch_new_token()

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            (12345678, "12345678"),
            (123456789, "12345678"),
            ("12345678", "12345678"),
            ("123456789", "12345678"),
            ("b12345678", "12345678"),
            ("b123456789", "12345678"),
            ("i21234567x", "21234567"),
            ("i21234567", "21234567"),
        ],
    )
    def test_prep_sierra_number(self, mock_token, arg, expectation):
        with SierraSession(authorization=mock_token) as session:
            assert session._prep_sierra_number(arg) == expectation

    @pytest.mark.parametrize(
        "arg",
        [12345, 1234567890, "12345", "bl1234567", "a12345678", None],
    )
    def test_prep_sierra_number_exceptions(self, mock_token, arg):
        err_msg = "Invalid Sierra number passed."
        with SierraSession(authorization=mock_token) as session:
            with pytest.raises(BookopsSierraError) as exc:
                session._prep_sierra_number(arg)
            assert err_msg in str(exc.value)

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            ("12345678", "12345678"),
            ("12345678,12345679", "12345678,12345679"),
            ("b12345678a", "12345678"),
            ("b12345678a,b12345679a", "12345678,12345679"),
            ("12345678a,12345679a", "12345678,12345679"),
            (" 12345678, 12345679 ", "12345678,12345679"),
            ("i389995009", "38999500"),
            (["12345678", "12345678"], "12345678,12345678"),
            ([12345678, 12345678], "12345678,12345678"),
            (["b12345678a", "12345678"], "12345678,12345678"),
        ],
    )
    def test_prep_sierra_numbers(self, mock_token, arg, expectation):
        with SierraSession(authorization=mock_token) as session:
            assert session._prep_sierra_numbers(arg) == expectation

    @pytest.mark.http_code(200)
    def test_bib_get_success_default_fields(self, mock_session, mock_session_response):
        assert mock_session.bib_get("12345678").status_code == 200

    @pytest.mark.http_code(200)
    def test_bib_get_marc(self, mock_session, mock_session_response):
        assert mock_session.bib_get("123345678").status_code == 200

    @pytest.mark.http_code(200)
    def test_item_get_success_default_fields(self, mock_session, mock_session_response):
        assert mock_session.item_get("12345678").status_code == 200

    @pytest.mark.http_code(204)
    def test_item_update_success_data_as_dict(
        self, mock_session, mock_session_response
    ):
        assert (
            mock_session.item_update("12345678", data={"status": "m"}).status_code
            == 204
        )

    @pytest.mark.http_code(204)
    def test_item_update_success_data_as_str(self, mock_session, mock_session_response):
        assert (
            mock_session.item_update("12345678", data='{"status": "m"}').status_code
            == 204
        )

    def test_item_update_invalid_body_type(self, mock_session):
        with pytest.raises(BookopsSierraError) as exc:
            mock_session.item_update("12345678", data=["foo", "bar"])
        assert (
            "Error. Given `data` argument is of a wrong type. Must be a str or dict."
            in str(exc.value)
        )

    @pytest.mark.http_code(204)
    def test_bib_update_success_data_as_dict(self, mock_session, mock_session_response):
        data = {
            "varFields": [
                {
                    "fieldTag": "y",
                    "marcTag": "901",
                    "ind1": " ",
                    "ind2": "1",
                    "subfields": [
                        {"tag": "a", "content": "TEST"},
                    ],
                },
            ],
        }
        assert mock_session.bib_update("12345678", data=data).status_code == 204
