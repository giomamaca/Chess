import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from db.init_db import init_db

from .routes import online_routes, offline_routes, auth_routes

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(offline_routes.router)
app.include_router(online_routes.router)

BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "client", "build")

app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")
app.mount("/pieces", StaticFiles(directory=os.path.join(BUILD_DIR, "pieces")), name="pieces")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(BUILD_DIR, "index.html"))