"""MSAL login with OS credential-store persistence; no plaintext fallback."""

import json
import threading

import keyring
import msal
import requests

from cap_runtime.config import Account
from cap_runtime.models import CAPError


def scopes(account: Account) -> list[str]:
    result = ["User.Read"]
    if "comms" in account.shelves:
        result.append("Mail.Read")
    if "calendar" in account.shelves:
        result.append("Calendars.Read")
    return result


class TimeoutSession(requests.Session):
    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", 20)
        return super().request(method, url, **kwargs)


class MicrosoftAuth:
    def __init__(self, account: Account):
        self.account = account
        self.key = f"{account.tenant}:{account.client_id}:{account.name}"
        self.lock = threading.Lock()
        self._principal: str | None = None

    @staticmethod
    def _store():
        backend = keyring.get_keyring()
        # Explicitly accept only OS-backed storage, never keyrings.alt plaintext files.
        allowed = (
            "keyring.backends.macOS",
            "keyring.backends.Windows",
            "keyring.backends.SecretService",
            "keyring.backends.kwallet",
        )
        if not type(backend).__module__.startswith(allowed):
            raise CAPError(
                "credential_store_unavailable",
                "Configure an OS keyring (Keychain, Credential Manager, or Secret Service).",
            )
        return backend

    def _load(self):
        try:
            backend = self._store()
            saved = backend.get_password("claw-agent-protocol", self.key)
            payload = json.loads(saved) if saved else {}
            cache = msal.SerializableTokenCache()
            if payload.get("cache"):
                cache.deserialize(payload["cache"])
            app = msal.PublicClientApplication(
                self.account.client_id,
                authority=f"https://login.microsoftonline.com/{self.account.tenant}",
                token_cache=cache,
                http_client=TimeoutSession(),
            )
            return backend, payload, cache, app
        except CAPError:
            raise
        except Exception as exc:
            raise CAPError(
                "authentication_unavailable",
                "Cannot load credentials or reach Microsoft login. Run cap auth login.",
            ) from exc

    def _save(self, backend, payload, cache):
        try:
            backend.set_password(
                "claw-agent-protocol", self.key, json.dumps({**payload, "cache": cache.serialize()})
            )
        except Exception as exc:
            raise CAPError(
                "credential_store_unavailable", "Could not save credentials to OS keyring."
            ) from exc

    def login(self, display):
        with self.lock:
            backend, payload, cache, app = self._load()
            try:
                flow = app.initiate_device_flow(scopes=scopes(self.account))
            except Exception as exc:
                raise CAPError("login_failed", "Cannot reach Microsoft to start login.") from exc
            if "user_code" not in flow:
                raise CAPError(
                    "login_failed", "Cannot start Microsoft device login. Check app registration."
                )
            display(flow["message"])
            try:
                result = app.acquire_token_by_device_flow(flow)
            except Exception as exc:
                raise CAPError("login_failed", "Microsoft login could not be completed.") from exc
            if "access_token" not in result:
                raise CAPError("login_failed", "Microsoft login was denied or expired; try again.")
            # Bind alias to the exact signed-in principal, even when the cache has several users.
            claims = result.get("id_token_claims", {})
            principal = f"{claims.get('tid', '')}:{claims.get('oid', '')}"
            if not claims.get("tid") or not claims.get("oid"):
                raise CAPError(
                    "login_failed", "Microsoft did not provide a stable account identity."
                )
            candidates = [
                a
                for a in app.get_accounts()
                if a.get("local_account_id") == claims["oid"] and a.get("realm") == claims["tid"]
            ]
            if len(candidates) != 1:
                raise CAPError("login_failed", "Cannot uniquely bind the signed-in account.")
            payload = {"principal": principal, "home_account_id": candidates[0]["home_account_id"]}
            self._save(backend, payload, cache)
            self._principal = principal

    def token(self) -> str:
        with self.lock:
            backend, payload, cache, app = self._load()
            accounts = [
                a
                for a in app.get_accounts()
                if a["home_account_id"] == payload.get("home_account_id")
            ]
            if len(accounts) != 1 or not payload.get("principal"):
                raise CAPError("not_connected", "Run cap auth login for this account.")
            if self._principal is not None and self._principal != payload["principal"]:
                raise CAPError(
                    "account_changed", "The signed-in identity changed. Restart the CAP server."
                )
            try:
                result = app.acquire_token_silent(scopes(self.account), account=accounts[0])
            except Exception as exc:
                raise CAPError(
                    "authentication_unavailable", "Microsoft login is unavailable.", True
                ) from exc
            if not result or "access_token" not in result:
                raise CAPError(
                    "authentication_required",
                    "Login expired or permissions changed. Run cap auth login.",
                )
            self._principal = payload["principal"]
            if cache.has_state_changed:
                self._save(backend, payload, cache)
            return result["access_token"]

    def principal(self) -> str:
        self.token()
        return self._principal

    def logout(self):
        try:
            self._store().delete_password("claw-agent-protocol", self.key)
        except keyring.errors.PasswordDeleteError:
            pass
        except CAPError:
            raise
        except Exception as exc:
            raise CAPError(
                "credential_store_unavailable", "Could not remove credentials from OS keyring."
            ) from exc
        self._principal = None
