from urllib.parse import parse_qs

import httpx
import pytest

from youtube_mcp.auth.oauth import DesktopClient, OAuthManager, READ_SCOPE, WRITE_SCOPE
from youtube_mcp.errors import AuthRequiredError


def test_read_then_write_then_revocation_and_memory_only_access():
    def handler(request):
        data = parse_qs(request.content.decode())
        if request.url.path == "/revoke":
            assert data["token"][0].startswith("refresh-")
            return httpx.Response(200)
        client = data["client_id"][0]
        assert data["grant_type"] == ["authorization_code"]
        assert data["code_verifier"] == ["test-verifier"]
        return httpx.Response(200, json={
            "access_token": f"access-{client}", "refresh_token": f"refresh-{client}",
            "scope": WRITE_SCOPE if client == "write" else READ_SCOPE, "expires_in": 3600,
        })

    class Store(dict):
        load = dict.get
        save = dict.__setitem__

        def delete(self, slot):
            self.pop(slot, None)

    def consent(client, scope):
        calls.append((client, scope))
        return "test-code", "test-verifier", "http://127.0.0.1:12345/oauth2redirect"

    calls = []
    store = Store()
    oauth = OAuthManager(DesktopClient("read", "fake"), DesktopClient("write", "fake"), store,
                         http=httpx.Client(transport=httpx.MockTransport(handler)), consent=consent)
    assert oauth.auth_status().state == "needs_authorisation"
    oauth.authorise()
    assert calls == [("read", READ_SCOPE)]
    assert oauth.auth_status().scopes == (READ_SCOPE,)
    oauth.ensure_write_scope()
    assert calls[-1] == ("write", WRITE_SCOPE)
    assert store == {"read": "refresh-read", "write": "refresh-write"}
    oauth.sign_out()
    assert not store and oauth.auth_status().state == "needs_authorisation"


def test_invalid_grant_erases_token_until_explicit_reauthorisation():
    class Store:
        token = "synthetic-invalid-grant"

        def load(self, slot):
            return self.token

        def delete(self, slot):
            self.token = None

    store = Store()
    transport = httpx.MockTransport(lambda _: httpx.Response(400, json={"error": "invalid_grant"}))
    oauth = OAuthManager(DesktopClient("read", "fake"), DesktopClient("write", "fake"), store,
                         http=httpx.Client(transport=transport))
    with pytest.raises(AuthRequiredError):
        oauth.token()
    assert store.token is None
    assert oauth.auth_status().state == "expired"
