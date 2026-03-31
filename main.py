from dotenv import load_dotenv

load_dotenv()

import requests
from flask import Flask, jsonify
import os
from login_challenge import perform_full_auth
from encrypt import encrypt


BASE_URL = os.getenv("BASE_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def mark_attendance(action: str):
    access_token = perform_full_auth(username, encrypt(password))
    if not access_token:
        return {"error": "Unable to login"}, 400

    url = f"{BASE_URL}/v3/api/attendance/mark-attendance?action={action}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    session = requests.Session()
    session.cookies.set("access_token", access_token)
    resp = session.post(url, json={}, headers=headers)
    try:
        return resp.json()
    except Exception as e:
        return {"error": "Failed to parse response"}, 500

app = Flask(__name__)

@app.route("/wakeup", methods=['GET'])
def wakeup():
    return jsonify({"success": True})

@app.route("/signin", methods=['GET'])
def signin():
    result = mark_attendance("Signin")
    if isinstance(result, tuple):  # error case
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route("/signout", methods=['GET'])
def signout():
    result = mark_attendance("Signout")
    if isinstance(result, tuple):  # error case
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route("/auth_token", methods=['GET'])
def auth_token():
    token = perform_full_auth(username, encrypt(password))
    if not token:
        return {"error": "Failed to get access token"}, 500
    return {"access_token": token}

# if __name__ == '__main__':
#     app.run(debug=True)
