"""One-time interactive OAuth bootstrap; run on your own PC, not Actions.
No dependencies beyond Python 3.12. Does not call advertising tools.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

MCP = 'https://ads-mcp.kr.karrotmarket.com/mcp'
ISSUER = 'https://accounts.daangn.com/internal-oidc'
META = 'https://accounts.daangn.com/.well-known/oauth-authorization-server/internal-oidc'
CLIENT_ID = 'https://raw.githubusercontent.com/hyeonchangleeremakedigital-cloud/claude_test/karrot-oauth-setup/karrot-client.json'
REDIRECT = 'http://127.0.0.1:8765/callback'
SCOPE = 'ads:read offline_access'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def request_json(url, form=None):
    data = urllib.parse.urlencode(form).encode() if form is not None else None
    headers = {'Accept': 'application/json'}
    if data is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = urllib.request.Request(url, data=data, headers=headers)
    # Do not forward authorization codes/tokens to redirected endpoints.
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as response:
        return json.load(response)


def challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')


def validate_metadata(metadata, client):
    if metadata.get('issuer') != ISSUER:
        raise ValueError('Unexpected issuer')
    if metadata.get('client_id_metadata_document_supported') is not True:
        raise ValueError('Client metadata URL unsupported')
    if 'S256' not in metadata.get('code_challenge_methods_supported', []):
        raise ValueError('PKCE S256 unsupported')
    for field in ('authorization_endpoint', 'token_endpoint'):
        parsed = urllib.parse.urlsplit(metadata[field])
        if parsed.scheme != 'https' or parsed.netloc != 'accounts.daangn.com':
            raise ValueError('Unexpected authorization endpoint')
    if client.get('client_id') != CLIENT_ID or client.get('redirect_uris') != [REDIRECT]:
        raise ValueError('Published client metadata mismatch')
    if not set(SCOPE.split()).issubset(metadata.get('scopes_supported', [])):
        raise ValueError('Required scopes unavailable')


def parse_callback(path, expected_state):
    parsed = urllib.parse.urlsplit(path)
    if parsed.path != '/callback':
        raise ValueError('Unexpected callback path')
    query = urllib.parse.parse_qs(parsed.query)
    states = query.get('state', [])
    if len(states) != 1 or not secrets.compare_digest(states[0], expected_state):
        raise ValueError('State mismatch')
    if query.get('iss') != [ISSUER]:
        raise ValueError('Issuer missing or mismatch')
    if 'error' in query:
        raise ValueError('Authorization denied')
    codes = query.get('code', [])
    if len(codes) != 1 or not codes[0]:
        raise ValueError('Missing code')
    return codes[0]


def save_tokens(token, destination):
    if not token.get('access_token') or str(token.get('token_type', '')).lower() != 'bearer':
        raise ValueError('Invalid token response')
    # Stored outside repository. New unique file, owner-only on Unix.
    # Windows inherits the user's profile-folder ACL.
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    record = {'client_id': CLIENT_ID, 'resource': MCP, 'issuer': ISSUER,
              'obtained_at': int(time.time()), 'tokens': token}
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(record, handle, ensure_ascii=False)


def main():
    print('Checking public OAuth metadata...')
    metadata = request_json(META)
    validate_metadata(metadata, request_json(CLIENT_ID))
    # This bootstrap requires RFC 9207 issuer validation in callback.
    if metadata.get('authorization_response_iss_parameter_supported') is not True:
        raise ValueError('Authorization response issuer validation unsupported')
    verifier = secrets.token_urlsafe(48)
    state = secrets.token_urlsafe(32)
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Never log the callback URL containing the authorization code.

        def do_GET(self):
            try:
                result['code'] = parse_callback(self.path, state)
                status, message = 200, b'Login received. Return to your terminal.'
            except ValueError:
                status, message = 400, b'Invalid or denied callback. Return to your terminal.'
                # Ignore unrelated paths; a real callback error ends this attempt.
                if urllib.parse.urlsplit(self.path).path == '/callback':
                    result['error'] = True
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers()
            self.wfile.write(message)

    params = {'response_type': 'code', 'client_id': CLIENT_ID,
              'redirect_uri': REDIRECT, 'scope': SCOPE, 'resource': MCP,
              'state': state, 'code_challenge': challenge(verifier),
              'code_challenge_method': 'S256'}
    authorize = metadata['authorization_endpoint'] + '?' + urllib.parse.urlencode(params)
    with HTTPServer(('127.0.0.1', 8765), Handler) as server:
        server.timeout = 1
        print('Opening Daangn login. Approve only this monitoring app and read access.')
        if not webbrowser.open(authorize):
            print('Open this login URL in the browser on THIS PC (do not share it):')
            print(authorize)
        deadline = time.monotonic() + 300
        while not result and time.monotonic() < deadline:
            server.handle_request()
    if not result.get('code'):
        raise ValueError('Login cancelled or timed out')
    token = request_json(metadata['token_endpoint'], {
        'grant_type': 'authorization_code', 'code': result['code'],
        'client_id': CLIENT_ID, 'redirect_uri': REDIRECT,
        'code_verifier': verifier, 'resource': MCP})
    destination = Path.home() / ('karrot-monitor-auth-' + secrets.token_hex(6) + '.json')
    save_tokens(token, destination)
    print('OAuth login succeeded. Private credentials saved locally:')
    print(destination)
    print('Refresh token present:', bool(token.get('refresh_token')))
    print('Do NOT upload this JSON to GitHub or paste its contents into chat.')
    print('Next: verify tool schemas and design persistent token rotation before scheduling.')


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as exc:
        print(f'HTTP {exc.code}: OAuth setup failed. No response body or credentials printed.')
        raise SystemExit(1)
    except Exception as exc:
        print(f'Setup failed ({type(exc).__name__}). No credentials printed.')
        raise SystemExit(1)
