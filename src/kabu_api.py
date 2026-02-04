from __future__ import annotations

import requests


class KabuApiClient:
    def __init__(self, base_url: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.password = password

    def get_token(self) -> str:
        url = f"{self.base_url}/token"
        response = requests.post(url, json={"APIPassword": self.password}, timeout=10)
        response.raise_for_status()
        data = response.json()
        token = data.get("Token")
        if not token:
            raise ValueError("Token not found in response")
        return token
