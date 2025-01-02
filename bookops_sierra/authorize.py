# -*- coding: utf-8 -*-

"""
bookops_nypl_platform.authorize
===============================
This module provides method to authenticate subsequent requests to NYPL Platform
by obtaining an access token used for authorization.
"""
import datetime
import sys
from typing import Any, Dict, Optional, Tuple, Union

import requests


from . import __title__, __version__
from .errors import BookopsSierraError


class SierraToken:
    """
    Authenticates access to III Sierra REST API and returns an access token.

    Args:
        client_id:      client id
        client_secret:  client secret
        host_url:       host's URL
        api_version:    version of Sierra API in the following format: 'v6'
        agent:          "User-Agent" parameter to be passed in the request
                        header
        timeout:        how long to wait for server to respond before
                        giving up; default value is 3 seconds

    Example:


    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        host_url: str,
        api_version: str = "v6",
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            3,
            3,
        ),
    ):
        """Constructor"""

        if not all([client_id, client_secret, host_url, api_version]):
            raise BookopsSierraError("Missing Sierra authentication argument.")

        self.token_str = None
        self.expires_on = None
        self.server_response = None
        self.auth = (client_id, client_secret)
        self.host_url = host_url
        self.api_version = api_version
        self.timeout = timeout

        if agent is None:
            self.agent = f"{__title__}/{__version__}"
        else:
            self.agent = agent

        # make access token request
        self._get_token()

    @property
    def base_url(self) -> str:
        return f"{self.host_url}/iii/sierra-api/{self.api_version}"

    def _token_url(self) -> str:
        return f"{self.base_url}/token"

    def _parse_access_token_string(self, server_response: Dict[str, Any]) -> str:
        """
        Parsers access token string from auth_server response

        Args:
            server_response:    server's response in dictionary format

        Returns:
            access_token
        """
        try:
            return server_response["access_token"]
        except (KeyError, TypeError):
            raise BookopsSierraError(
                "Missing access_token parameter in the authenticating server's response."
            )

    def _calculate_expiration_time(
        self, server_response: Dict[str, Any]
    ) -> datetime.datetime:
        """
        Calculates access token expiration time based on it's life length
        indicated in the server's response

        Args:
            server_response:    host_url response in dict format

        Returns:
            expires_on:         datetime object
        """
        try:
            expires_on = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=server_response["expires_in"] - 1)
            return expires_on
        except (KeyError, TypeError):
            raise BookopsSierraError(
                "Missing expires_in parameter in the server's response."
            )

    def _get_token(self):
        """
        Fetches Sierra API access token
        """
        token_url = self._token_url()
        header = {"User-Agent": self.agent}
        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(
                token_url,
                auth=self.auth,
                headers=header,
                data=data,
                timeout=self.timeout,
            )
            if response.status_code == requests.codes.ok:
                self.server_response = response
                self.token_str = self._parse_access_token_string(response.json())
                self.expires_on = self._calculate_expiration_time(response.json())
            else:
                raise BookopsSierraError(
                    f"Invalid request. Oauth server returned error: {response.json()}"
                )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise BookopsSierraError(f"Trouble connecting: {sys.exc_info()[0]}")
        except BookopsSierraError:
            raise
        except Exception:
            raise BookopsSierraError(f"Unexpected error occured: {sys.exc_info()[0]}")

    def is_expired(self):
        """
        Checks if the access token is expired

        Returns:
            Boolean

        Example:
        >>> token.is_expired()
        False

        """
        if self.expires_on < datetime.datetime.now(datetime.timezone.utc):
            return True
        else:
            return False

    def __repr__(self):
        return (
            f"<token: {self.token_str}, "
            f"expires_on: {self.expires_on:%Y-%m-%d %H:%M:%S}, "
            f"server_response: {self.server_response.json()}>"
        )
