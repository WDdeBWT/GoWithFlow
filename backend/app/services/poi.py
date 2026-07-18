import json
from pathlib import Path
from app.models import POI, Intent

DATA_PATH = Path(__file__).parent.parent / "data" / "beijing_pois.json"


with open(DATA_PATH, "r", encoding="utf-8") as f:
    _POIS = [POI(**item) for item in json.load(f)]


def load_pois() -> list[POI]:
    return _POIS.copy()


ACTION_MAP = {
    "咖啡": ["咖啡馆"],
    "喝": ["咖啡馆", "茶室"],
    "茶": ["茶室"],
    "工作": ["有电源"],
    "写代码": ["有电源"],
    "徒步": ["自然景观"],
    "爬山": ["自然景观"],
    "走": ["自然景观"],
    "户外": ["自然景观"],
    "散步": ["自然景观"],
    "看书": ["书店"],
    "阅读": ["书店"],
    "发呆": ["安静"],
    "独特": ["独特"],
}


def filter_pois(pois: list[POI], intent: Intent) -> list[POI]:
    keywords = set()
    for w in [intent.core_action, intent.extra_action or ""] + intent.soft_preferences + intent.hard_constraints:
        keywords.update(w.split())

    matched = []
    for poi in pois:
        if "有电源" in keywords and not poi.has_power:
            continue
        if "宠物" in keywords and not poi.pet_friendly:
            continue
        if "非露天" in keywords and not poi.indoor:
            continue

        score = 0
        for kw, tags in ACTION_MAP.items():
            if kw in keywords and any(t in poi.tags for t in tags):
                score += 1
        if score > 0 or not keywords:
            matched.append(poi)

    return matched or pois
