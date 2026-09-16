import json
from unittest.mock import Mock

import pytest

from cap_runtime.auth import MicrosoftAuth, scopes
from cap_runtime.config import Account
from cap_runtime.models import CAPError


def auth():
    return MicrosoftAuth(Account(name="work", provider="microsoft365", client_id="app"))


def test_no_write_scopes():
    assert scopes(auth().account) == ["User.Read", "Mail.Read", "Calendars.Read"]
    account = auth().account
    account.shelves = ["calendar"]
    assert scopes(account) == ["User.Read", "Calendars.Read"]


def test_plaintext_keyring_rejected(monkeypatch):
    backend = type("Plaintext", (), {"__module__": "keyrings.alt.file"})()
    monkeypatch.setattr("keyring.get_keyring", lambda: backend)
    with pytest.raises(CAPError, match="OS keyring"):
        auth()._store()


def test_silent_login_selects_bound_account_and_saves_refresh(monkeypatch):
    client = auth()
    backend = Mock()
    cache = Mock(has_state_changed=True, serialize=lambda: "new-cache")
    wrong = {"home_account_id": "wrong"}
    selected = {"home_account_id": "selected"}
    app = Mock()
    app.get_accounts.return_value = [wrong, selected]
    app.acquire_token_silent.return_value = {"access_token": "secret-not-logged"}
    payload = {"home_account_id": "selected", "principal": "tenant:person"}
    monkeypatch.setattr(client, "_load", lambda: (backend, payload, cache, app))
    assert client.token() == "secret-not-logged"
    app.acquire_token_silent.assert_called_once_with(scopes(client.account), account=selected)
    assert json.loads(backend.set_password.call_args.args[2])["cache"] == "new-cache"


def test_missing_cached_account_never_falls_back_to_other_user(monkeypatch):
    client = auth()
    app = Mock()
    app.get_accounts.return_value = [{"home_account_id": "someone-else"}]
    monkeypatch.setattr(
        client, "_load", lambda: (Mock(), {"home_account_id": "missing"}, Mock(), app)
    )
    with pytest.raises(CAPError) as caught:
        client.token()
    assert caught.value.problem.code == "not_connected"
    app.acquire_token_silent.assert_not_called()


def test_reauthentication_to_different_person_requires_restart(monkeypatch):
    client = auth()
    client._principal = "tenant:original"
    app = Mock()
    app.get_accounts.return_value = [{"home_account_id": "new"}]
    monkeypatch.setattr(
        client,
        "_load",
        lambda: (Mock(), {"home_account_id": "new", "principal": "tenant:new"}, Mock(), app),
    )
    with pytest.raises(CAPError) as caught:
        client.token()
    assert caught.value.problem.code == "account_changed"
    app.acquire_token_silent.assert_not_called()
