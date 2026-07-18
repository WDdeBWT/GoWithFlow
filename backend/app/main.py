from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import DEFAULT_CITY_CENTER
from app.models import UserQuery
from app.services.intent_rule import parse_intent_rule
from app.services.weather import get_weather
from app.services.poi import load_pois, filter_pois
from app.services.ranking import rank_pois
from app.services.feedback import adjust_intent

app = FastAPI(title="GoWithFlow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend")
async def recommend(
    query: UserQuery,
    lat: float = Query(DEFAULT_CITY_CENTER[0]),
    lon: float = Query(DEFAULT_CITY_CENTER[1]),
):
    intent, follow_up = parse_intent_rule(query.text)
    weather = await get_weather(lat, lon)
    candidates = filter_pois(load_pois(), intent)
    recommendations = rank_pois(intent, weather, lat, lon, candidates)
    return {"follow_up": follow_up, "recommendations": recommendations}


@app.post("/feedback")
async def feedback(
    query: UserQuery,
    feedback_type: str,
    lat: float = Query(DEFAULT_CITY_CENTER[0]),
    lon: float = Query(DEFAULT_CITY_CENTER[1]),
):
    intent, _ = parse_intent_rule(query.text)
    adjusted = adjust_intent(intent, feedback_type)
    weather = await get_weather(lat, lon)
    candidates = filter_pois(load_pois(), adjusted)
    recommendations = rank_pois(adjusted, weather, lat, lon, candidates)
    return {"recommendations": recommendations}
