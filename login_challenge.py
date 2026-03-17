import requests
import secrets
import hashlib
import base64
import re
import os


def generate_pkce():
    # Generate a random verifier
    verifier = secrets.token_urlsafe(32)
    # Create SHA256 hash
    sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
    # Base64URL encode the hash
    challenge = base64.urlsafe_b64encode(sha256).decode('utf-8').replace('=', '')
    return verifier, challenge

def generate_state():
    return secrets.token_urlsafe(16)

# --- Configuration ---
BASE_URL = os.getenv("BASE_URL")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def perform_full_auth(username, encrypted_password):
 
    verifier, challenge = generate_pkce()
    resp_config = session.get(f"{BASE_URL}/uas/v1/session-config").json()
    access_id = resp_config['accessId']
    
    state = secrets.token_urlsafe(16)
    auth_params = {
        "response_type": "code",
        "client_id": "greythr-coral",
        "state": state,
        "redirect_uri": "https://idp-coral.greythr.com/uas/portal/auth/callback",
        "scope": "openid offline",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "nonce": state,
        "access_id": access_id
    }
    # We follow redirects until we land on the login page URL
    res = session.get("https://goth-coral.greythr.com/oauth2/auth", params=auth_params)
    login_challenge = re.search(r'login_challenge=([^&]+)', res.url).group(1)

    # 4. Submit Credentials
    login_payload = {"userName": username, "password": encrypted_password}
    login_headers = {"X-OAUTH-CHALLENGE": login_challenge}
    login_res = session.post(f"{BASE_URL}/uas/v1/login", json=login_payload, headers=login_headers).json()
    callback_res = session.get(login_res['redirectUrl'])
    
    auth_code = re.search(r'code=([^&]+)', callback_res.url).group(1)

    token_headers = {
        "CODE": auth_code,
        "PKCE-verifier": verifier,
        "Referer": callback_res.url,
        "Content-Type": "application/json"
    }

    token_res = session.post(
        f"{BASE_URL}/uas/v1/initiate/token-request",
        headers=token_headers,
        json={}
    )

    if token_res.status_code == 200:
        return session.cookies.get_dict().get("access_token")
    else:
        return None

