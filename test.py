import httpx
from playwright.async_api import async_playwright
from fastapi import FastAPI, HTTPException
import os


url = os.getenv("URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

async def get_access_token():
    access_token = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url)

            # fill login form
            await page.fill('#username', username)
            await page.fill('#password', password)

            await page.locator('//form//button[@type="submit"]').click()
            # wait for login to complete
            await page.wait_for_load_state("networkidle")

            # get cookies
            cookies = await context.cookies()
            for cookie in cookies:
                if cookie.get("name", "") == "access_token":
                    access_token = cookie.get("value")
                    break
            
            await browser.close()
    except Exception as e:
        print(e)
    return access_token

async def mark_attendance(action: str):
    access_token = await get_access_token()
    if not access_token:
        raise HTTPException(status_code=400, detail="Unable to login")

    url = f"https://fusion-galaxxy.greythr.com/v3/api/attendance/mark-attendance?action={action}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with httpx.AsyncClient(cookies={"access_token": access_token}, headers=headers) as client:
        resp = await client.post(url, json={})
        try:
            return resp.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to parse response")


app = FastAPI()


@app.get("/signin")
async def signin():
    return await mark_attendance("Signin")

@app.get("/signout")
async def signout():
    return await mark_attendance("Signout")

@app.get("/auth_token")
async def auth_token():
    token = await get_access_token()
    if not token:
        raise HTTPException(status_code=500, detail="Failed to get access token")
    return {"access_token": token}
