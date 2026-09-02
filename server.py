"""
Duty roster backend — FastAPI version.

Install once:
    pip install fastapi uvicorn --break-system-packages

Run:
    python3 server.py
    (or: uvicorn server:app --reload)

Then open http://localhost:8000 in a browser.

Routes:
  GET  /              -> sends the frontend (duty-roster.html)
  GET  /api/roster     -> reads roster-data.json and returns it
  POST /api/roster     -> overwrites roster-data.json with whatever JSON is sent
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "roster-data.json"
FRONTEND_FILE = BASE_DIR / "duty-roster.html"

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if not FRONTEND_FILE.exists():
        raise HTTPException(status_code=404, detail="duty-roster.html not found next to server.py")
    return FRONTEND_FILE.read_text(encoding="utf-8")


@app.get("/api/roster")
def get_roster():
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="roster-data.json not found next to server.py")
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise HTTPException(status_code=500, detail=f"roster-data.json is not valid JSON: {err}")


@app.post("/api/roster")
async def save_roster(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body is not valid JSON")

    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return JSONResponse({"status": "saved"})


if __name__ == "__main__":
    import uvicorn

    print("Duty roster running at http://localhost:8000")
    print(f"Reading and saving data at {DATA_FILE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
