# -*- coding: utf-8 -*-

"""Handles requests to Sierra server."""

from __future__ import annotations
from typing import Union, TYPE_CHECKING
import sys

from requests import PreparedRequest
from requests.exceptions import ConnectionError, HTTPError, Timeout

from .errors import BookopsSierraError

if TYPE_CHECKING:
    from .session import SierraSession  # pragma: no cover


class Query:
    """Sends a request to Sierra server and unifies exceptions.

    Query object handles automatic refresh of expired token before each
    request is made to the web service. `Query.response` attribute is
    [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.PreparedRequest)
    instance that can be parsed to extract information received from the web service.
    """

    def __init__(
        self,
        session: SierraSession,
        prepared_request: PreparedRequest,
        timeout: Union[int, float, tuple[int, int], tuple[float, float], None] = (
            5,
            5,
        ),
    ) -> None:
        """Initializes Query object.

        Args:
            session:
                `session.SierraSession` instance.
            prepared_request:
                `requests.PreparedRequest` instance.
            timeout:
                How long to wait for server to send data before giving up. Accepts
                separate values for connect and read timeouts or a single value.

        Raises:
            BookopsSierraError:
                If the request encounters any errors.
            TypeError:
                If `prepared_request` arg is passed anything other than a
                `requests.PreparedRequest` object.
        """
        if not isinstance(prepared_request, PreparedRequest):
            raise TypeError("Invalid type for argument 'prepared_request'.")

        # make sure access token is still valid and if not request a new one
        if session.authorization.is_expired():
            session._fetch_new_token()

        try:
            self.response = session.send(prepared_request, timeout=timeout)
            self.response.raise_for_status()

        except HTTPError as exc:
            raise BookopsSierraError(
                f"{exc}. Server response: "  # type: ignore
                f"{self.response.content.decode('utf-8')}"
            )
        except (Timeout, ConnectionError):
            raise BookopsSierraError(f"Connection Error: {sys.exc_info()[0]}")

        except Exception:
            raise BookopsSierraError(f"Unexpected request error: {sys.exc_info()[0]}")
