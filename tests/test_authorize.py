# -*- coding: utf-8 -*-

import datetime
import os

import pytest


from bookops_sierra.authorize import SierraToken
from bookops_sierra.errors import BookopsSierraError


class TestSierraToken:
    """
    Test SierraToken class
    """

    @pytest.mark.parametrize(
        "args, msg",
        [
            ((None, None, None), "Missing Sierra authentication argument."),
            (("key", None, None), "Missing Sierra authentication argument."),
            ((None, "secret", None), "Missing Sierra authentication argument."),
            ((None, None, "server"), "Missing Sierra authentication argument."),
            (("", "", ""), "Missing Sierra authentication argument."),
            (
                ("key", "secret", "server", ""),
                "Missing Sierra authentication argument.",
            ),
            (("key", "", ""), "Missing Sierra authentication argument."),
            (("", "secret", ""), "Missing Sierra authentication argument."),
            (("", "", "server"), "Missing Sierra authentication argument."),
        ],
    )
    def test_missing_init_arguments(self, args, msg):
        with pytest.raises(BookopsSierraError) as exc:
            SierraToken(*args)
        assert msg in str(exc.value)

    def test_auth(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.auth == ("my_client_id", "my_client_secret")

    def test_host_url(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.host_url == "sierra_url"

    def test_api_version_default(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.api_version == "v6"

    def test_api_version_custom(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url", "v4")
        assert token.api_version == "v4"

    def test_base_url_default_api_version(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.base_url == "sierra_url/iii/sierra-api/v6"

    def test_base_url_custom_api_version(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url", "v4")
        assert token.base_url == "sierra_url/iii/sierra-api/v4"

    def test_default_agent(self, mock_successful_post_token_response):
        from bookops_sierra import __title__, __version__

        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.agent == f"{__title__}/{__version__}"

    def test_default_timeout(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token.timeout == (3, 3)

    def test_custom_agent(self, mock_successful_post_token_response):
        token = SierraToken(
            "my_client_id", "my_client_secret", "sierra_url", agent="my_client/1.0"
        )
        assert token.agent == "my_client/1.0"

    def test_custom_timeout(self, mock_successful_post_token_response):
        token = SierraToken(
            "my_client_id", "my_client_secret", "sierra_url", timeout=1.5
        )
        assert token.timeout == 1.5

    def test_token_url(self, mock_successful_post_token_response):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert token._token_url() == "sierra_url/iii/sierra-api/v6/token"

    def test_parse_access_token_string_success(self, mock_token):
        token = mock_token
        res = {
            "access_token": "token_string_here",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        assert token._parse_access_token_string(res) == "token_string_here"

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            (None, pytest.raises(BookopsSierraError)),
            ({"a": 1}, pytest.raises(BookopsSierraError)),
            ("some_str", pytest.raises(BookopsSierraError)),
        ],
    )
    def test_parse_access_token_string_failure(self, mock_token, arg, expectation):
        token = mock_token
        err_msg = (
            "Missing access_token parameter in the authenticating server's response."
        )
        with expectation as exc:
            token._parse_access_token_string(arg)
        assert err_msg in str(exc.value)

    def test_calculate_expiration_time_success(self, mock_token, mock_datetime_now):
        token = mock_token
        res = {"expires_in": 3600}
        assert token._calculate_expiration_time(res) == datetime.datetime(
            2019, 1, 1, 17, 0, 0, tzinfo=datetime.timezone.utc
        ) + datetime.timedelta(seconds=3599)

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            (None, pytest.raises(BookopsSierraError)),
            ("", pytest.raises(BookopsSierraError)),
            ({}, pytest.raises(BookopsSierraError)),
        ],
    )
    def test_calculate_expiration_time_failure(self, mock_token, arg, expectation):
        token = mock_token
        err_msg = "Missing expires_in parameter in the server's response."
        with expectation as exc:
            token._calculate_expiration_time(arg)
        assert err_msg in str(exc.value)

    def test_get_token_timeout(self, mock_timeout):
        with pytest.raises(BookopsSierraError):
            SierraToken("my_client_id", "my_client_secret", "sierra_url")

    def test_get_token_connection_error(self, mock_connection_error):
        with pytest.raises(BookopsSierraError):
            SierraToken("my_client_id", "my_client_secret", "sierra_url")

    def test_get_token_unexpected_error(self, mock_unexpected_error):
        with pytest.raises(BookopsSierraError):
            SierraToken("my_client_id", "my_client_secret", "sierra_url")

    def test_get_token_http_400_error(self, mock_failed_post_token_response):
        with pytest.raises(BookopsSierraError):
            SierraToken("my_client_id", "my_client_secret", "sierra_url")

    def test_get_token_success(
        self, mock_successful_post_token_response, mock_datetime_now
    ):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        res = {
            "access_token": "token_string_here",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        assert token.server_response.json() == res
        assert token.token_str == "token_string_here"
        assert token.expires_on == datetime.datetime(
            2019, 1, 1, 17, 0, 0, tzinfo=datetime.timezone.utc
        ) + datetime.timedelta(seconds=3599)

    def test_is_expired_false(self, mock_token):
        token = mock_token
        assert token.is_expired() is False

    def test_is_expired_true(self, mock_token):
        token = mock_token
        token.expires_on = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(seconds=1)
        assert token.is_expired() is True

    def test_printing_token(
        self, mock_successful_post_token_response, mock_datetime_now
    ):
        token = SierraToken("my_client_id", "my_client_secret", "sierra_url")
        assert (
            str(token)
            == "<token: token_string_here, expires_on: 2019-01-01 17:59:59, server_response: {'access_token': 'token_string_here', 'token_type': 'bearer', 'expires_in': 3600}>"  # noqa: E501
        )


@pytest.mark.webtest
class TestLiveAuthentication:
    """Runs access token request against live authentication server"""

    def test_access_token(self, live_keys):
        agent = os.getenv("SIERRA_AGENT")
        token = SierraToken(
            client_id=os.getenv("SIERRA_CLIENT"),
            client_secret=os.getenv("SIERRA_SECRET"),
            host_url=os.getenv("SIERRA_SERVER"),
            agent=f"{agent}",
        )

        assert token.server_response.status_code == 200
        assert sorted(token.server_response.json().keys()) == sorted(
            ["access_token", "expires_in", "token_type"]
        )
        assert token.token_str is not None
        assert len(token.token_str) > 0
        assert token.expires_on is not None
        assert token.is_expired() is False
