import json
import math
from collections import Counter, defaultdict
import jieba
from app.services.llm import chat
from app.models import POI, Intent, Recommendation


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _estimate_drive_time(distance_km: float) -> float:
    speed = 30 if distance_km < 30 else 50
    return distance_km / speed * 60


_STOP = set(["的", "了", "是", "很", "有", "可以", "但", "不", "非常", "适合", "就是", "而且", "在", "和", "与", "也", "都"])


def _compute_surprise(pois: list[POI]) -> list[float]:
    doc_words = []
    for poi in pois:
        words = []
        for c in poi.comments:
            words.extend([w for w in jieba.cut(c) if len(w) > 1 and w not in _STOP])
        doc_words.append(Counter(words))

    df = defaultdict(int)
    for dw in doc_words:
        for w in set(dw):
            df[w] += 1

    scores = []
    for dw in doc_words:
        score = 0
        for w, cnt in dw.items():
            idf = math.log(len(pois) / (df[w] + 0.5))
            score += cnt * idf
        scores.append(score)
    return scores


def rank_pois(intent: Intent, weather: dict, user_lat: float, user_lon: float, pois: list[POI]) -> list[Recommendation]:
    if not pois:
        return []

    candidate_text = "\n\n".join(
        f"ID: {p.id}\n名称: {p.name}\n类型: {p.type}\n标签: {', '.join(p.tags)}\n描述: {'；'.join(p.comments)}"
        for p in pois
    )
    system = "你是一位周末地点推荐助手，擅长理解用户模糊意图。"
    user = f"""用户意图：{intent.core_action} {intent.extra_action or ''}，{', '.join(intent.soft_preferences)}，交通{intent.transport}，约{intent.time_minutes}分钟。
当前天气：温度{weather['temperature']}℃，降水概率{weather['precipitation_probability']}%。
候选地点：
{candidate_text}

请对每个候选地点给出：氛围匹配分（0-100）、惊喜指数（0-100）、一条语义推荐理由。输出 JSON 数组，每项包含 id, semantic_score, surprise_score, semantic_reason。"""

    try:
        content = chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
        )
        scores_raw = json.loads(content)
    except Exception:
        scores_raw = []

    if isinstance(scores_raw, dict):
        scores_raw = scores_raw.get("scores", []) or scores_raw.get("recommendations", [])

    score_map = {s["id"]: s for s in scores_raw}
    surprise_scores = _compute_surprise(pois)
    results = []

    for i, poi in enumerate(pois):
        dist = _haversine(user_lat, user_lon, poi.lat, poi.lon)
        drive_min = _estimate_drive_time(dist)
        accessibility = max(0, 1 - drive_min / intent.time_minutes)

        s = score_map.get(poi.id, {"semantic_score": 50, "surprise_score": 50, "semantic_reason": ""})
        sem = float(s.get("semantic_score", 50))
        sur = float(s.get("surprise_score", surprise_scores[i] * 10))

        weather_multiplier = 1.0
        if weather["precipitation_probability"] > 70 and not poi.indoor:
            weather_multiplier = 0.2
            weather_reason = f"降水概率高，{'该地点非室内' if not poi.indoor else '地点为室内'}"
        else:
            weather_reason = "当前天气条件适宜"

        if weather["temperature"] > 32 and ("户外" in intent.core_action or "走" in intent.core_action):
            if any(t in poi.tags for t in ["溪流", "林荫道"]):
                weather_multiplier *= 1.2
                weather_reason = "高温天优先推荐有溪流/林荫道的地点"

        final_score = (sem * 0.6 + min(sur, 100) * 0.2) * weather_multiplier * accessibility
        results.append({
            "id": poi.id,
            "name": poi.name,
            "type": poi.type,
            "district": poi.district,
            "lat": poi.lat,
            "lon": poi.lon,
            "drive_time": f"{drive_min:.0f} 分钟",
            "reasons": [
                s.get("semantic_reason", "氛围与用户意图相符"),
                weather_reason,
                f"距你约 {dist:.1f} km，预计车程 {drive_min:.0f} 分钟",
            ],
            "tags": poi.tags,
            "_score": final_score,
        })

    results.sort(key=lambda x: x["_score"], reverse=True)
    for r in results:
        r.pop("_score")
    return [Recommendation(**r) for r in results[:3]]
