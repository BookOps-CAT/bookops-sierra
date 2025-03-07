# -*- coding: utf-8 -*-

"""
bookops_sierra.session
=============================
This module provides a session functionality used for making requests
to Sierra API
"""
import json
from typing import Tuple, Union, Optional

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
            5,
            5,
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

    def _prep_multi_keywords(
        self, keywords: Union[str, list[str], None]
    ) -> Optional[str]:
        """
        Verifies or converts passed keywords into a comma separated string.

        Args:
            keywords:       a comma separated string of keywords or a list
                            of strings or integers

        Returns:
            keywords:       a comma separated string of keywords
        """
        if isinstance(keywords, str):
            keywords = keywords.strip()
        elif isinstance(keywords, list):
            keywords = ",".join([str(k) for k in keywords])
        if not keywords:
            return None
        return keywords

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

    def _prep_sierra_numbers(self, sids: Union[str, list[str], list[int], None]) -> str:
        """
        Verifies or converts passed Sierra bib numbers into a comma separated string.

        Args:
            sids:           a comma separated string of Sierra bib numbers

        Returns:
            verified_nos:   a comma separated string of Sierra bib numbers
        """
        verified_nos = []

        if isinstance(sids, list):
            for sid in sids:
                vsid = self._prep_sierra_number(sid)
                verified_nos.append(vsid)
        elif isinstance(sids, str):
            for sid in sids.split(","):
                vsid = self._prep_sierra_number(sid)
                verified_nos.append(vsid)

        return ",".join(verified_nos)

    def _update_authorization(self):
        """
        Updates Bearer token in SierraSession headers
        """
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def bib_get(
        self,
        sid: Union[str, int],
        fields: Optional[Union[str, list]] = None,
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
        prepped_sid = self._prep_sierra_number(sid)
        url = self._bib_endpoint(prepped_sid)
        header = {"Accept": "application/json"}
        payload = {"fields": fields}

        # prep request
        req = requests.Request("GET", url, params=payload, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def bib_get_marc(
        self, sid: Union[str, int], response_type: str = "application/marc-xml"
    ) -> requests.Response:
        """
        Get MARC data for a single bib.
        Uses GET /bibs/{id}/marc endpoint.
        Args:
            sid:            Sierra bib number
            response_type:  choice of marc-json, marc-xml, mar-in-json

        Returns:
            requests.Response instance
        """
        prepped_sid = self._prep_sierra_number(sid)
        url = f"{self._bib_endpoint(prepped_sid)}/marc"
        header = {"Accept": response_type}

        # prep request
        req = requests.Request("GET", url, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

    def bib_create(self):
        # POST /bibs/
        pass

    def bib_delete(self):
        # DELETE /bibs/{id}
        pass

    def bib_update(
        self,
        sid: Union[str, int],
        data: Union[str, dict],
        data_format: str = "application/json",
        response_type: str = "application/json",
    ):
        """
        Update a Sierra bib. Please note, to avoid loosing data, provide the entire bib
        with modified elements in the `data` argument.
        Uses PUT /bibs/{id} endpoint

        Args:
            sid:            Sierra bibliographic record number
            data:           data to be updated
            data_format:    choice of application/json or application/xml
            response_type:  choice of application/json or application/xml

        Returns:
            `requests.Response` instance
        """
        prepped_sid = self._prep_sierra_number(sid)
        url = f"{self._bib_endpoint(prepped_sid)}"
        header = {"Accept": response_type, "content-type": data_format}
        if isinstance(data, dict):
            body = json.dumps(data)
        elif isinstance(data, str) or isinstance(data, bytes):
            body = data
        else:
            raise BookopsSierraError(
                "Error. Given `data` argument is of a wrong type. "
                "Must be a str or dict."
            )

        # prep request
        req = requests.Request("PUT", url, data=body, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

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

    def item_get(
        self,
        sid: Union[str, int],
        fields: Optional[Union[str, list]] = None,
        response_type: str = "application/json",
    ) -> requests.Response:
        """
        Get MARC data for a single bib.
        Uses GET /items/{id} endpoint.
        Args:
            sid:            Sierra bib number
            fields:         a comma-delimited list of fields to retrieve
            response_type:  choice of marc-json, marc-xml, mar-in-json

        Returns:
            requests.Response instance
        """
        prepped_sid = self._prep_sierra_number(sid)
        url = f"{self._item_endpoint(prepped_sid)}"
        header = {"Accept": response_type}
        payload = {"fields": fields}

        # prep request
        req = requests.Request("GET", url, params=payload, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

    def item_delete(self):
        # DELETE /items/{id}
        pass

    def item_update(
        self,
        sid: Union[str, int],
        data: Union[str, dict],
        data_format: str = "application/json",
        response_type: str = "application/json",
    ) -> requests.Response:
        """
        Updates an item record.
        Uses PUT /items/{id} endpoint.
        Args:
            sid:            Sierra bib number
            data:           item record data
            data_format:    choice of application/json or application/xml
            response_type:  choice of application/json or application/xml

        Returns:
            requests.Response instance
        """
        prepped_sid = self._prep_sierra_number(sid)
        url = f"{self._item_endpoint(prepped_sid)}"
        header = {"Accept": response_type, "content-type": data_format}
        if isinstance(data, dict):
            body = json.dumps(data)
        elif isinstance(data, str):
            body = data
        else:
            raise BookopsSierraError(
                "Error. Given `data` argument is of a wrong type. "
                "Must be a str or dict."
            )

        # prep request
        req = requests.Request("PUT", url, data=body, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)
        return query.response

    def item_create(self):
        # POST /items/
        pass

    def item_get_checkouts(self):
        # GET /items/{id}/checkouts
        pass

    def items_get(
        self,
        sids: Union[str, list[str], list[int], None] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        fields: Optional[Union[str, list[str]]] = None,
        createdDate: Optional[str] = None,
        updatedDate: Optional[str] = None,
        deletedDate: Optional[str] = None,
        deleted: Optional[bool] = False,
        bibIds: Optional[Union[str, list[str], list[int]]] = None,
        status: Optional[str] = None,
        duedate: Optional[str] = None,
        suppressed: Optional[str] = None,
        locations: Optional[str] = None,
        response_type="application/json",
    ):
        """
        Retrieves a list of Sierra items of given item numbers.
        Uses GET /items/ endpoint.

        Args:
            sids:           Sierra item numbers as a comma separated string, or
                            list of string or integers.
            limit:          maximum number of results
            offset:         the beginning record (zero-indexed) of the result set
            fields:         a list or comma delimited string of fields to retrieve
            createdDate:    the creation date of items to retrieve (can be a range)
            updatedDate:    the modification date of times to retrieve (can be a range)
            deletedDate:    the deletion date of items to retrieve (can be a range)
            deleted:        retrieve only deleted (true) or non-deleted items (false)
            bibIds:         list of bib IDs for which to retrieve associated items
            status:         the status code of items to retrieve
            duedate:        the due date of items to retrieve
            suppressed:     the suppressed flag value of items to retrieve
            locations:      a list of location codes (can include a single
                            wildcard * to represent one or more final characters)
            response_type:  response content format, application/json or application/xml

        Returns:
            requests.Response instance
        """
        prepped_sids = self._prep_sierra_numbers(sids)
        url = self._items_endpoint
        header = {"Accept": response_type}
        payload = {
            "id": prepped_sids,
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "createdDate": createdDate,
            "updateDate": updatedDate,
            "deletedDate": deletedDate,
            "deleted": deleted,
            "bibIds": bibIds,
            "status": status,
            "duedate": duedate,
            "suppressed": suppressed,
            "locations": locations,
        }

        # prep request
        req = requests.Request("GET", url, params=payload, headers=header)
        prepared_request = self.prepare_request(req)

        # send request
        query = Query(self, prepared_request, timeout=self.timeout)

        return query.response

    def items_get_checkouts(self):
        # GET /items/checkouts
        pass

    def items_checkin(self):
        # DELETE /items/checkouts/{barcode}
        pass

    def items_query(self):
        # POST /items/query
        pass
