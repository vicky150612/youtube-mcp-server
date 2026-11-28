import base64
from dataclasses import dataclass
from datetime import timedelta
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
from threading import RLock
import time
from urllib.parse import parse_qs, urlencode, urlsplit
import webbrowser

import httpx

from youtube_mcp.clock import SystemClock
from youtube_mcp.errors import AuthRequiredError, ProviderError
from youtube_mcp.models import AuthStatus

READ_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CONSENT_URL = "https://accounts.google.com/o/oauth2/v2/auth"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"


@dataclass(frozen=True)
class DesktopClient:
    client_id: str
    client_secret: str


def desktop_consent(client_id, scope, *, open_browser=webbrowser.open, timeout=180):
    verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    result = {}

    class Callback(BaseHTTPRequestHandler):
        timeout = 2

        def log_message(self, *_args):
            pass

        def do_GET(self):
            target = urlsplit(self.path)
            query = parse_qs(target.query)
            if (target.path != "/oauth2redirect"
                    or query.get("state") != [state]):
                self.send_error(400, "Invalid callback.")
                return
            result["code"] = query.get("code", [None])[0] if "error" not in query else None
            body = b"Authorization response received. Return to the application."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    with HTTPServer(("127.0.0.1", 0), Callback) as server:
        redirect = f"http://127.0.0.1:{server.server_port}/oauth2redirect"
        link = CONSENT_URL + "?" + urlencode({
            "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
            "scope": scope, "state": state, "code_challenge": challenge,
            "code_challenge_method": "S256", "access_type": "offline", "prompt": "consent",
        })
        if not open_browser(link):
            raise AuthRequiredError("Could not open the browser for YouTube consent.")
        deadline = time.monotonic() + timeout
        while not result and time.monotonic() < deadline:
            server.timeout = max(0, deadline - time.monotonic())
            server.handle_request()
    if not result.get("code"):
        raise AuthRequiredError("YouTube consent was declined or timed out.")
    return result["code"], verifier, redirect


class OAuthManager:
    """Desktop PKCE, independently requested read and write grants."""

    def __init__(self, read_client, write_client, store, *, http=None, clock=None,
                 consent=desktop_consent, write_store=None):
        self.clients = {"read": read_client, "write": write_client}
        self.stores = {"read": store, "write": write_store or store}
        self.scopes = {"read": READ_SCOPE, "write": WRITE_SCOPE}
        self.http = http or httpx.Client(timeout=15)
        self.clock = clock or SystemClock()
        self.consent = consent
        self.access = {}
        self.expired = set()
        self.lock = RLock()

    def _exchange(self, slot, **params):
        client = self.clients[slot]
        try:
            response = self.http.post(TOKEN_URL, data={
                "client_id": client.client_id, "client_secret": client.client_secret, **params,
            })
            data = response.json()
        except (httpx.HTTPError, ValueError):
            raise ProviderError("Google OAuth is temporarily unavailable.") from None
        if not isinstance(data, dict):
            raise ProviderError("Google returned an invalid OAuth response.")
        if data.get("error") == "invalid_grant":
            self.expired.add(slot)
            self.access.pop(slot, None)
            self.stores[slot].delete(slot)
            raise AuthRequiredError("The Google grant expired or was revoked. Re-authorise YouTube.")
        if (response.is_error or not data.get("access_token")
                or self.scopes[slot] not in (data.get("scope") or self.scopes[slot]).split()):
            raise AuthRequiredError("Google did not grant the requested YouTube access.")
        if any(scope not in {READ_SCOPE, WRITE_SCOPE}
               for scope in (data.get("scope") or self.scopes[slot]).split()):
            raise AuthRequiredError("Google returned an unexpected OAuth scope.")
        if slot == "read" and WRITE_SCOPE in (data.get("scope") or "").split():
            raise AuthRequiredError("Authorise read access using the read-only desktop client.")
        if data.get("refresh_token"):
            self.stores[slot].save(slot, data["refresh_token"])
        elif params["grant_type"] == "authorization_code":
            raise AuthRequiredError("Google did not issue a refresh token. Re-authorise YouTube.")
        lifetime = data.get("expires_in")
        if type(lifetime) is not int or lifetime <= 0:
            raise ProviderError("Google returned an invalid access-token lifetime.")
        self.expired.discard(slot)
        self.access[slot] = (data["access_token"], self.clock.now() + timedelta(seconds=lifetime))
        return data["access_token"]

    def authorise(self, *, write=False):
        slot = "write" if write else "read"
        with self.lock:
            code, verifier, redirect = self.consent(self.clients[slot].client_id, self.scopes[slot])
            return self._exchange(slot, grant_type="authorization_code", code=code,
                                  code_verifier=verifier, redirect_uri=redirect)

    def token(self, *, write=False):
        slot = "write" if write else "read"
        with self.lock:
            cached = self.access.get(slot)
            if cached and cached[1] > self.clock.now() + timedelta(seconds=30):
                return cached[0]
            refresh = self.stores[slot].load(slot)
            if not refresh:
                raise AuthRequiredError("Authorise YouTube before using this operation.")
            return self._exchange(slot, grant_type="refresh_token", refresh_token=refresh)

    def ensure_write_scope(self):
        with self.lock:
            self.token()
            try:
                self.token(write=True)
            except AuthRequiredError:
                self.authorise(write=True)

    def auth_status(self):
        with self.lock:
            try:
                self.token()
            except AuthRequiredError:
                return AuthStatus("expired" if "read" in self.expired else "needs_authorisation", ())
            scopes = [READ_SCOPE]
            try:
                self.token(write=True)
            except AuthRequiredError:
                pass
            else:
                scopes.append(WRITE_SCOPE)
            return AuthStatus("ok", tuple(scopes))

    def sign_out(self):
        failed = False
        with self.lock:
            for slot, store in self.stores.items():
                refresh = store.load(slot)
                try:
                    if refresh:
                        response = self.http.post(REVOKE_URL, data={"token": refresh})
                        failed |= response.is_error
                except httpx.HTTPError:
                    failed = True
                finally:
                    self.access.pop(slot, None)
                    self.expired.discard(slot)
                    store.delete(slot)
        if failed:
            raise ProviderError("Local credentials were removed. Revoke access in Google Account settings.")
