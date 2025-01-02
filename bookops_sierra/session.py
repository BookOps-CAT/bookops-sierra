# -*- coding: utf-8 -*-

"""
bookops_sierra.session
=============================
This module provides a session functionality used for making requests
to Sierra API
"""

from typing import Tuple, Union

import requests

from .authorize import SierraToken
from .errors import BookopsSierraError
from .query import Query


class SierraSession(requests.Session):
    """
    Opens a session with Sierra API server and provides methods
    to send requests to it.

    Args:
        authorization:          authorization in form of the `SierraToken` instance
        timeout:                how long to wait for server to send data before
                                giving up; default value is 3 seconds
    Example:

    >>> from bookops_sierra import SierraSession
    >>> with SierraSession(authorization=token, agent="my_client") as session:
            # needs tailored example
            # response = session.search_standardNos(
            #     keywords=["9780316230032", "0674976002"])
            print(response.json())
    """

    def __init__(
        self,
        authorization: SierraToken,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            3,
            3,
        ),
    ):
        requests.Session.__init__(self)

        self.authorization = authorization
        if not isinstance(self.authorization, SierraToken):
            raise BookopsSierraError(
                "Invalid authorization. Argument must be an instance of "
                "`SierraToken` object."
            )

        self._bibs_endpoint = f"{self.authorization.base_url}/bibs/"
        self._items_endpoint = f"{self.authorization.base_url}/items/"

        # set agent for requests
        self.headers.update({"User-Agent": self.authorization.agent})

        # set timeout
        self.timeout = timeout

        # set session wide response content type
        self.headers.update({"Accept": "application/json"})

        # set token bearer for the session
        self._update_authorization()

    def _fetch_new_token(self):
        """
        Requests new access token from the oauth server and updates
        session headers with new authorization
        """
        try:
            self.authorization._get_token()
            self._update_authorization()
        except BookopsSierraError:
            raise

    def _bibs_marc_endpoint(self) -> str:
        return f"{self._bibs_endpoint}marc"

    def _bibs_metadata_endpoint(self) -> str:
        return f"{self._bibs_endpoint}metadata"

    def _bibs_query_endpoint(self) -> str:
        return f"{self._bibs_endpoint}query"

    def _bibs_search_endpoint(self) -> str:
        return f"{self._bibs_endpoint}search"

    def _bib_endpoint(self, sid: Union[str, int]) -> str:
        return f"{self._bibs_endpoint}{sid}"

    def _items_checkouts_endpoint(self) -> str:
        return f"{self._items_endpoint}checkouts"

    def _items_query_endpoint(self) -> str:
        return f"{self._items_endpoint}query"

    def _item_endpoint(self, sid: Union[str, int]) -> str:
        return f"{self._items_endpoint}{sid}"

    # def _prep_multi_keywords(
    #     self, keywords: Union[str, List[str], List[int], None]
    # ) -> Optional[str]:
    #     """
    #     Verifies or converts passed keywords into a comma separated string.

    #     Args:
    #         keywords:       a comma separated string of keywords or a list
    #                         of strings or integers

    #     Returns:
    #         keywords:       a comma separated string of keywords
    #     """
    #     if isinstance(keywords, str):
    #         keywords = keywords.strip()
    #     elif isinstance(keywords, int):
    #         keywords = str(keywords)
    #     elif isinstance(keywords, list):
    #         keywords = ",".join([str(k) for k in keywords])
    #     if not keywords:
    #         return None
    #     return keywords

    def _prep_sierra_number(self, sid: Union[str, int]) -> str:
        """
        Verifies and formats Sierra bib numbers

        Args:
            sid:            Sierra bib or item number as string or int

        Returns:
            sid
        """
        err_msg = "Invalid Sierra number passed."

        if isinstance(sid, int):
            sid = str(sid)
        elif isinstance(sid, str):
            sid = sid.strip()
        else:
            raise BookopsSierraError(err_msg)

        if sid.lower()[0] in ("b", "i"):
            sid = sid[1:]
        if len(sid) == 8:
            if not sid.isdigit():
                raise BookopsSierraError(err_msg)
        elif len(sid) == 9:
            sid = sid[:8]
            if not sid.isdigit():
                raise BookopsSierraError(err_msg)
        else:
            raise BookopsSierraError(err_msg)

        return sid

    def _prep_sierra_numbers(self, sids: str) -> str:
        """
        Verifies or converts passed Sierra bib numbers into a comma separated string.

        Args:
            sids:           a comma separated string of Sierra bib numbers

        Returns:
            verified_nos:   a comma separated string of Sierra bib numbers
        """
        verified_nos = []

        for bid in sids.split(","):
            bid = self._prep_sierra_number(bid)
            verified_nos.append(bid)

        return ",".join(verified_nos)

    def _update_authorization(self):
        """
        Updates Bearer token in SierraSession headers
        """
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def bib_get(
        self,
        sid: Union[str, int],
        fields: Union[str, list] = "id,createdDate,normTitle",
    ) -> requests.Response:
        """
        Retrieves specified fields of a Sierra bib.
        Uses GET /bibs/{id} endpoint.

        Args:
            sid:        Sierra bib number
            fields:     a list or comma delimited string of fields to retrieve

        Returns:
            requests.Response instance
        """
        url = self._bib_endpoint(sid)
        header = {"Accept": "application/json"}
        payload = {"fields": fields}

        # prep request
        req = requests.Request("GET", url, params=payload, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def bib_get_marc(self):
        # GET /bibs/{id}/marc
        pass

    def bib_create(self):
        # POST /bibs/
        pass

    def bib_delete(self):
        # DELETE /bibs/{id}
        pass

    def bib_update(self):
        # PUT /bibs/{id}
        pass

    def bibs_get(self):
        # GET /bibs/
        pass

    def bibs_get_marc(self):
        # GET /bibs/marc
        pass

    def bibs_get_metadata(self):
        # GET /bibs/metadata
        pass

    def bibs_delete_marc_files(self):
        # DELETE /bibs/marc
        pass

    def bibs_query(self):
        # POST /bibs/query
        pass

    def bibs_search(self):
        # GET /bibs/search
        pass

    def item_get(self):
        pass

    def item_delete(self):
        # DELETE /items/{id}
        pass

    def item_update(self):
        # PUT /items/{id}
        pass

    def item_create(self):
        # POST /items/
        pass

    def item_get_checkouts(self):
        # GET /items/{id}/checkouts
        pass

    def items_get(self):
        # GET /items/
        pass

    def items_get_checkouts(self):
        # GET /items/checkouts
        pass

    def items_checkin(self):
        # DELETE /items/checkouts/{barcode}
        pass

    def items_query(self):
        # POST /items/query
        pass
