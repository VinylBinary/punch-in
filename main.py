import httpx
from fastapi import FastAPI, HTTPException
import os
from login_challenge import  perform_full_auth
from encrypt import encrypt
from dotenv import load_dotenv

load_dotenv()



BASE_URL = os.getenv("BASE_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


async def mark_attendance(action: str):
    access_token = perform_full_auth(username, encrypt(password))
    if not access_token:
        raise HTTPException(status_code=400, detail="Unable to login")

    url = f"{BASE_URL}/v3/api/attendance/mark-attendance?action={action}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with httpx.AsyncClient(cookies={"access_token": access_token}, headers=headers) as client:
        resp = await client.post(url, json={})
        try:
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse response")


app = FastAPI()


@app.get("/signin")
async def signin():
    return await mark_attendance("Signin")

@app.get("/signout")
async def signout():
    return await mark_attendance("Signout")

@app.get("/auth_token")
async def auth_token():
    token = perform_full_auth(username, encrypt(password))
    if not token:
        raise HTTPException(status_code=500, detail="Failed to get access token")
    return {"access_token": token}
