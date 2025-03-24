# backend/app/utils/bank_auth/bank_auth.py

import requests

import urllib.parse as urlparse


class BankConnect:
    def __init__(
        self,
        base_url,
        redirect_url,
        secret_key,
        secret_id,
        access_token=None,
        refresh_token=None,
    ):
        self.base_url = base_url
        self.redirect_url = redirect_url
        self.secret_key = secret_key
        self.secret_id = secret_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def generate_access_token(
        self,
    ) -> dict:
        response = requests.post(
            self._url_for("token/new/"),
            json={"secret_id": self.secret_id, "secret_key": self.secret_key},
            headers=self._default_headers,
        )
        response.raise_for_status()
        self.access_token = response.json()["access"]
        self.refresh_token = response.json()["refresh"]
        return response.json()

    def upsert_tokens(self, env_filepath: str, access_token: str, refresh_token: str):
        with open(env_filepath, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith("GOCARDLESS_ACCESS_TOKEN"):
                    lines[i] = f"GOCARDLESS_ACCESS_TOKEN = {access_token}\n"
                if line.startswith("GOCARDLESS_REFRESH_TOKEN"):
                    lines[i] = f"GOCARDLESS_REFRESH_TOKEN = {refresh_token}\n"

        with open(env_filepath, "w") as file:
            file.writelines(lines)
        return 0

    def refresh_access_token(
        self,
    ) -> dict:
        response = requests.post(
            self._url_for("token/refresh/"),
            json={"refresh": self.refresh_token},
            headers=self._default_headers,
        )
        response.raise_for_status()
        self.access_token = response.json()["access"]
        return response.json()

    def _url_for(self, path):
        return urlparse.urljoin(self.base_url, path)

    @property
    def _default_headers(self):
        return {"Accept": "application/json", "Content-Type": "application/json"}


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    env_filepath = "/Users/dizzydwarfus/Dev/expense-tracker/backend/.env"
    load_dotenv()

    client = BankConnect(
        base_url=os.environ["GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL"],
        redirect_url=os.environ["GOCARDLESS_REDIRECT_URL"],
        secret_key=os.environ["GOCARDLESS_SECRET_KEY"],
        secret_id=os.environ["GOCARDLESS_SECRET_ID"],
        access_token=os.environ["GOCARDLESS_ACCESS_TOKEN"],
        refresh_token=os.environ["GOCARDLESS_REFRESH_TOKEN"],
    )

    # access = client.generate_access_token()
    refresh = client.refresh_access_token()
    client.upsert_tokens(env_filepath, client.access_token, client.refresh_token)
