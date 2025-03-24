# backend/app/utils/bank_auth/gocardless_api.py
# Sourced from: https://github.com/gocardless/gocardless-pro-python/blob/master/gocardless_pro/

from functools import wraps

import sys
import platform
import urllib.parse as urlparse
import json
import requests
from typing import List
import webbrowser


class GoCardlessProError(Exception):
    """Base exception class for gocardless_pro errors."""


class ApiError(GoCardlessProError):
    """Base exception class for GoCardless API errors. API errors will result
    in one of this class' subclasses being raised.
    """

    def __init__(self, error):
        self.error = error

    def __str__(self):
        messages = [
            error["message"]
            for error in (self.errors or [])
            if error["message"] != self.message
        ]
        if messages:
            return "{} ({})".format(self.message, ", ".join(messages))
        else:
            return self.message

    @property
    def type(self):
        return self.error.get("type")

    @property
    def code(self):
        return self.error.get("code")

    @property
    def errors(self):
        return self.error.get("errors")

    @property
    def documentation_url(self):
        return self.error.get("documentation_url")

    @property
    def message(self):
        return self.error.get("message")

    @property
    def request_pointer(self):
        return self.error.get("request_pointer")

    @property
    def request_id(self):
        return self.error.get("request_id")

    @classmethod
    def _exception_for_status(cls, status):
        if status == 401:
            return AuthenticationError
        elif status == 403:
            return PermissionsError
        elif status == 429:
            return RateLimitError
        else:
            return None

    @classmethod
    def _exception_for_error_type(cls, error_type, errors=[]):
        if error_type == "validation_failed":
            return ValidationFailedError
        elif error_type == "invalid_api_usage":
            return InvalidApiUsageError
        elif error_type == "invalid_state":
            for error in errors:
                if error["reason"] == "idempotent_creation_conflict":
                    return IdempotentCreationConflictError
            return InvalidStateError
        elif error_type == "gocardless":
            return GoCardlessInternalError
        else:
            return None

    @classmethod
    def exception_for(cls, status, error_type, errors=[]):
        exception = cls._exception_for_status(status) or cls._exception_for_error_type(
            error_type, errors
        )
        if exception is not None:
            return exception
        raise GoCardlessProError('Invalid error type "{}"'.format(error_type))


class ValidationFailedError(ApiError):
    def __str__(self):
        if self.errors and "field" in self.errors[0]:
            errors = [
                "{field} {message} {request_pointer}".format(**error)
                for error in self.errors
            ]
            return "{} ({})".format(self.message, ", ".join(errors))
        return super(ValidationFailedError, self).__str__()


class IdempotentCreationConflictError(ApiError):
    @property
    def conflicting_resource_id(self):
        for error in self.error["errors"]:
            if "conflicting_resource_id" in error.get("links", {}) and bool(
                error["links"]["conflicting_resource_id"]
            ):  # Neither None nor ""
                return error["links"]["conflicting_resource_id"]
        else:
            raise ApiError(
                "Idempotent Creation Conflict Error missing conflicting_resource_id"
            )


class InvalidApiUsageError(ApiError):
    pass


class InvalidStateError(ApiError):
    pass


class GoCardlessInternalError(ApiError):
    pass


class AuthenticationError(ApiError):
    pass


class PermissionsError(ApiError):
    pass


class RateLimitError(ApiError):
    pass


class MalformedResponseError(GoCardlessProError):
    def __init__(self, message, response):
        super(MalformedResponseError, self).__init__(message)
        self.response = response


class InvalidSignatureError(GoCardlessProError):
    pass


def update_rate_limit(method):
    """Wrap all fetch methods in this decorator to update the client's
    ratelimit object with remaining requests available.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        response = method(self, *args, **kwargs)
        self.rate_limit.update_from_response(response)
        return response

    return wrapper


class RateLimit:
    def __init__(self):
        self.limit = None
        self.remaining = None
        self.reset = None

    def update_from_response(self, response):
        """Reads the remaining ratelimit from the response and updates
        the remaining attribute.
        Args:
          response (requests.Response): A requests ``Response`` object.
        """
        remaining = response.headers.get("ratelimit-remaining")
        if remaining:
            self.remaining = int(remaining)

        limit = response.headers.get("ratelimit-limit")
        if limit:
            self.limit = int(limit)

        self.reset = response.headers.get("ratelimit-reset")


class Paginator(object):
    """Iterates through all records in a paginated collection, automatically
    loading each page until the last.
    """

    def __init__(self, service, params):
        self._service = service
        self._params = params

    def __iter__(self):
        return self._iterate()

    def _iterate(self):
        page = self._fetch_page(None)
        while True:
            for record in page.records:
                yield record

            if page.after is None:
                break

            page = self._fetch_page(page.after)

    def _fetch_page(self, after):
        params = self._params.copy()
        if after is not None:
            params.update({"after": after})
        return self._service.list(params=params)


class ApiClient(object):
    """Client for interacting with a JSON HTTP API, using OAuth2-style auth.

    Args:
      base_url (string): The prefix that's prepended to all request paths.
      access_token (string): Token used in the Authorization header.
    """

    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.access_token = access_token
        self.rate_limit = RateLimit()

    @update_rate_limit
    def get(self, path, params=None, headers=None):
        """Perform a GET request, optionally providing query-string params.

        Args:
          path (str): A path that gets appended to ``base_url``.
          params (dict, optional): Dictionary of param names to values.

        Example:
          api_client.get('/users', params={'active': True})

        Returns:
          A requests ``Response`` object.
        """
        print(self._url_for(path))
        print(json.dumps(self._headers(headers), indent=2))
        response = requests.get(
            self._url_for(path), params=params, headers=self._headers(headers)
        )
        # self._handle_errors(response)
        return response

    @update_rate_limit
    def post(self, path, body, headers=None):
        """Perform a POST request, providing a body, which will be JSON-encoded.

        Args:
          path (str): A path that gets appended to ``base_url``.
          body (dict): Dictionary that will be JSON-encoded and sent as the body.

        Example:
          api_client.post('/users', body={'name': 'Billy Jean'})

        Returns:
          A requests ``Response`` object.
        """
        print(self._url_for(path))
        print(json.dumps(self._headers(headers), indent=2))
        response = requests.post(
            self._url_for(path), data=json.dumps(body), headers=self._headers(headers)
        )
        # self._handle_errors(response)
        return response

    @update_rate_limit
    def put(self, path, body, headers=None):
        """Perform a PUT request, providing a body, which will be JSON-encoded.

        Args:
          path (str): A path that gets appended to ``base_url``.
          body (dict): Dictionary that will be JSON-encoded and sent as the body.

        Example:
          api_client.put('/users', body={'name': 'Billy Jean'})

        Returns:
          A requests ``Response`` object.
        """
        print(self._url_for(path))
        print(json.dumps(self._headers(headers), indent=2))
        response = requests.put(
            self._url_for(path), data=json.dumps(body), headers=self._headers(headers)
        )
        self._handle_errors(response)
        return response

    @update_rate_limit
    def delete(self, path, body, headers=None):
        """Perform a DELETE request, providing a body, which will be JSON-encoded.

        Args:
          path (str): A path that gets appended to ``base_url``.
          body (dict): Dictionary that will be JSON-encoded and sent as the body.

        Example:
          api_client.delete('/users', body={'name': 'Billy Jean'})

        Returns:
          A requests ``Response`` object.
        """
        print(self._url_for(path))
        print(json.dumps(self._headers(headers), indent=2))
        response = requests.delete(
            self._url_for(path), data=json.dumps(body), headers=self._headers(headers)
        )
        self._handle_errors(response)
        return response

    def _handle_errors(self, response):
        if response.status_code == 204:
            return

        try:
            response_body = response.json()
        except ValueError:
            msg = "Malformed response received from server"
            raise MalformedResponseError(msg, response.text)

        if response.status_code < 400:
            return

        error = response.json()["error"]
        exception_class = ApiError.exception_for(
            response.status_code, error["type"], error.get("errors")
        )
        raise exception_class(error)

    def _url_for(self, path):
        return urlparse.urljoin(self.base_url, path)

    def _headers(self, custom_headers):
        headers = self._default_headers()
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _default_headers(self):
        return {
            "Accept": "application/json",
            "Authorization": "Bearer {0}".format(self.access_token),
            "Content-Type": "application/json",
            # "GoCardless-Client-Library": "gocardless-pro-python",
            # "GoCardless-Client-Version": "2.1.0",
            # "User-Agent": self._user_agent(),
            # "GoCardless-Version": "2015-07-06",
        }

    def _user_agent(self):
        python_version = ".".join(platform.python_version_tuple()[0:2])
        vm_version = "{}.{}.{}-{}{}".format(*sys.version_info)
        return " ".join(
            [
                "gocardless-pro-python/2.1.0",
                "python/{0}".format(python_version),
                "{0}/{1}".format(platform.python_implementation(), vm_version),
                "{0}/{1}".format(platform.system(), platform.release()),
                "requests/{0}".format(requests.__version__),
            ]
        )

    # End-user Agreement
    def create_end_user_agreement(
        self,
        path: str = "agreements/enduser/",
        institution_id: str = "ING_INGBNL2A",
        max_historical_days: str = 90,
        access_valid_for_days: str = 180,
        access_scope: List[str] = ["balances", "transactions", "details"],
    ):
        """Generates and end-user-agreement for linking bank account

        Args:
            path (str, optional): _description_. Defaults to "agreements/enduser/".
            institution_id (str, optional): _description_. Defaults to "ING_INGBNL2A".
            max_historical_days (str, optional): _description_. Defaults to 90.
            access_valid_for_days (str, optional): _description_. Defaults to 180.
            access_scope (List[str], optional): _description_. Defaults to ["balances", "transactions", "details"].

        Return Example:
            {
                "id":"2dea1b84-97b0-4cb4-8805-302c227587c8",
                "created":"2021-10-25T16:41:09.753Z",
                "max_historical_days":180,
                "access_valid_for_days":30,
                "access_scope":[
                    "balances",
                    "details",
                    "transactions"
                ],
                "accepted":"",
                "institution_id":"REVOLUT_REVOGB21"
            }
        """
        end_user_agreement = {
            "institution_id": institution_id,
            "max_historical_days": max_historical_days,
            "access_valid_for_days": access_valid_for_days,
            "access_scope": access_scope,
        }

        self.end_user_agreement = self.post(path, body=end_user_agreement).json()

        return self.end_user_agreement

    def link_bank_account(
        self,
        path: str = "requisitions/",
        redirect_url: str = "http://localhost:8000/callback",
        institution_id: str = None,
        reference: str = None,
        user_language: str = "EN",
        user_agreement: dict = None,
        open_browser: bool = True,
    ):
        user_agreement = user_agreement if user_agreement else self.end_user_agreement
        linking_info = {
            "redirect": redirect_url,
            "institution_id": institution_id or user_agreement.get("institution_id"),
            "agreement": user_agreement.get("id"),
            "user_language": user_language,
        }
        if reference is not None:
            linking_info["reference"] = reference

        self.linked_account = self.post(path, body=linking_info).json()

        # Automatically open browser window
        if open_browser:
            webbrowser.open(self.linked_account["link"])

        return self.linked_account

    def list_accounts(
        self,
        path: str = "requisitions/",
        requisition_id: str = None,
    ):
        account_path = urlparse.urljoin(path, requisition_id)
        self.accounts_list = self.get(account_path).json()

        return self.accounts_list

    def get_transactions(
        self,
        account_id: str,
        date_from: str = None,
        date_to: str = None,
    ):
        url = f"accounts/{account_id}/transactions"
        if date_from is not None and date_to is not None:
            params = {"date_from": date_from, "date_to": date_to}
        else:
            params = None
        self.transactions = self.get(url, params).json()

        return self.transactions

    def get_agreement(
        self,
        path: str,
        agreement_id: str,
    ):
        url = f"{path}/{agreement_id}/"
        self.end_user_agreement = self.get(url).json()

        return self.end_user_agreement


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    bank_institutions_path = "institutions/?country=nl"
    end_user_agreement_path = "agreements/enduser/"
    requisition_path = "requisitions/"
    redirect_url = "http://localhost:8000/callback"

    load_dotenv()
    client = ApiClient(
        base_url=os.environ["GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL"],
        access_token=os.environ["GOCARDLESS_ACCESS_TOKEN"],
    )

    # banks = client.get(bank_institutions_path)

    # end_user_params = {
    #     "path": end_user_agreement_path,
    #     "institution_id": "ING_INGBNL2A",
    #     "max_historical_days": 540,
    #     "access_valid_for_days": 180,
    # }
    # client.create_end_user_agreement(**end_user_params)

    # bank_account_params = {
    #     "path": requisition_path,
    #     "open_browser": True,
    # }
    # client.link_bank_account(**bank_account_params)

    # client.get_agreement(
    #     path=end_user_agreement_path,
    #     agreement_id="7154e6cc-08de-402a-b1ab-65a4b8ae240a",
    # )

    # client.list_accounts(
    #     path=requisition_path, requisition_id="c4b238d7-f5cc-47e9-bc79-0af986aba95e"
    # )
    client.get_transactions(
        "54b67147-2720-4e21-b4d2-8302dd8f59dd", "2025-03-01", "2025-03-04"
    )
    local_data_path = "/Users/dizzydwarfus/Dev/expense-tracker/local_data"

    # with open(
    #     f"{local_data_path}/end_user_agreement.json", "w", encoding="utf-8"
    # ) as file:
    #     json.dump(client.end_user_agreement, file, indent=2)

    # with open(f"{local_data_path}/account_list.json", "w", encoding="utf-8") as file:
    #     json.dump(client.accounts_list, file, indent=2)

    with open(f"{local_data_path}/transactions.json", "w", encoding="utf-8") as file:
        json.dump(client.transactions, file, indent=2)
