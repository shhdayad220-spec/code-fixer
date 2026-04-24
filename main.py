from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()
