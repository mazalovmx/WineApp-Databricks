"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api.routes import health, auth, users, recommendations, wines, ratings, runs

app = FastAPI(
    title="Guadalajara Wine Finder",
    description="API for wine recommendations in Guadalajara, Jalisco",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(wines.router)
app.include_router(ratings.router)
app.include_router(runs.router)


@app.get("/")
def root():
    return {"app": "Guadalajara Wine Finder", "docs": "/docs"}
