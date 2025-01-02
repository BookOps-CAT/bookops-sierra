# -*- coding: utf-8 -*-

"""
bookops_sierra.session testing
"""
from contextlib import nullcontext as does_not_raise
import datetime
import os
import pytest

from bookops_sierra import __title__, __version__

from bookops_sierra.errors import BookopsSierraError
from bookops_sierra.session import SierraSession


class TestSierraSession:
    """
    Test of the SierraSession
    """

    def test_authorization_invalid_argument(self):
        err_msg = "Invalid authorization. Argument must be an instance of `SierraToken` object."
        with pytest.raises(BookopsSierraError) as exc:
            SierraSession("my_token")
        assert err_msg in str(exc.value)

    def test_default_agent_parameter(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session.headers["User-Agent"] == f"{__title__}/{__version__}"

    def test_default_timeout_parameter(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session.timeout == (3, 3)

    def test_custom_timeout_parameter(self, mock_token):
        with SierraSession(authorization=mock_token, timeout=1.5) as session:
            assert session.timeout == 1.5

    def test_bibs_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session._bibs_endpoint == "sierra_url/iii/sierra-api/v6/bibs/"

    def test_items_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert session._items_endpoint == "sierra_url/iii/sierra-api/v6/items/"

    def test_bibs_endpoint_custom_api_version(self, mock_token):
        mock_token.api_version = "v4"
        with SierraSession(authorization=mock_token) as session:
            assert session._bibs_endpoint == "sierra_url/iii/sierra-api/v4/bibs/"

    def test_bibs_marc_endpoint(self, mock_token):
        with SierraSession(authorization=mock_token) as session:
            assert (
                session._bibs_marc_endpoint()
                == "sierra_url/iii/sierra-api/v6/bibs/marc"
            )
