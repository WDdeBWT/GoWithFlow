from typing import List, Optional
from pydantic import BaseModel, Field


class Intent(BaseModel):
    transport: str = "开车"
    time_minutes: int = Field(90, ge=10, le=300)
    hard_constraints: List[str] = []
    soft_preferences: List[str] = []
    core_action: str = ""
    extra_action: Optional[str] = ""


class UserQuery(BaseModel):
    text: str


class POI(BaseModel):
    id: str
    name: str
    type: str
    district: str
    lat: float
    lon: float
    tags: List[str] = []
    comments: List[str] = []
    has_power: bool = False
    pet_friendly: bool = False
    indoor: bool = False


class Recommendation(BaseModel):
    id: str
    name: str
    type: str
    district: str
    lat: float
    lon: float
    drive_time: str
    reasons: List[str]
    tags: List[str] = []
