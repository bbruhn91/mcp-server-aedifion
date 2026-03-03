"""HTTP client for the aedifion REST API."""

from __future__ import annotations

import httpx


BASE_URL = "https://api.cloud.aedifion.eu"


class AedifionClient:
    """Thin wrapper around the aedifion HTTP API.

    Handles authentication (HTTP Basic -> bearer token) and provides
    convenience helpers for every HTTP verb the API uses.
    """

    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._credentials: tuple[str, str] | None = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def set_credentials(self, username: str, password: str) -> None:
        self._credentials = (username, password)
        self._token = None

    def set_token(self, token: str) -> None:
        self._token = token

    async def obtain_token(self) -> str:
        """Obtain a bearer token using HTTP Basic credentials."""
        if self._credentials is None:
            raise RuntimeError(
                "No credentials configured. Call set_credentials() first."
            )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v2/user/token",
                auth=self._credentials,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("token") or data.get("access_token")
            if self._token is None:
                raise RuntimeError(f"Unexpected token response: {data}")
            return self._token

    async def _ensure_token(self) -> str:
        if self._token is None:
            return await self.obtain_token()
        return self._token

    # ------------------------------------------------------------------
    # Generic request helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | list | None = None,
        data: dict | None = None,
        files: dict | None = None,
        timeout: float = 60,
    ) -> dict | list | str:
        token = await self._ensure_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                params=params,
                json=json_body,
                data=data,
                files=files,
                timeout=timeout,
            )

            # If we get a 401 try to refresh the token once
            if resp.status_code == 401:
                token = await self.obtain_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.request(
                    method,
                    f"{self.base_url}{path}",
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    files=files,
                    timeout=timeout,
                )

            resp.raise_for_status()

            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return resp.text

    async def get(self, path: str, **kwargs) -> dict | list | str:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict | list | str:
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict | list | str:
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> dict | list | str:
        return await self._request("DELETE", path, **kwargs)
