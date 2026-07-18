import re
import jieba
from app.models import Intent


TRANSPORT_KEYWORDS = {
    "开车": ["开车", "自驾", "驾车"],
    "骑行": ["骑车", "骑行", "单车"],
    "步行": ["步行", "走路", "散步"],
    "公共交通": ["地铁", "公交", "地铁/公交"],
}

HARD_CONSTRAINTS = {
    "有电源": ["有电源", "有插座", "可充电", "插座"],
    "非露天": ["非露天", "室内", "不露天"],
    "宠物可进": ["宠物", "宠物友好", "带狗", "带猫"],
}

SOFT_PREFERENCES = {
    "凉快": ["凉快", "凉爽", "冷", "不热"],
    "安静": ["安静", "人少", "不吵", "宁静"],
    "松弛": ["松弛", "chill", "放松", "放空"],
    "专注": ["专注", "工作", "办公", "写代码"],
    "独特": ["独特", "小众", "不网红", "反网红"],
}

ACTION_KEYWORDS = {
    "喝咖啡": ["喝咖啡", "咖啡"],
    "工作": ["工作", "办公", "写代码"],
    "看书": ["看书", "阅读"],
    "徒步": ["徒步", "爬山", "登山"],
    "散步": ["散步", "走走", "户外走两步"],
    "喝茶": ["喝茶", "品茶", "茶"],
    "发呆": ["发呆", "放空"],
}


_TIME_PATTERNS = [
    (re.compile(r"(\d+(?:\.\d+)?)\s*小时"), 60),
    (re.compile(r"(\d+(?:\.\d+)?)\s*小時"), 60),
    (re.compile(r"(\d+(?:\.\d+)?)\s*h"), 60),
    (re.compile(r"半\s*小时"), 30),
    (re.compile(r"一个?半小时"), 90),
    (re.compile(r"半天"), 240),
    (re.compile(r"一天"), 480),
]


_DEFAULT_INTENT = Intent(
    transport="开车",
    time_minutes=90,
    hard_constraints=[],
    soft_preferences=[],
    core_action="",
    extra_action="",
)


def _extract_time(text: str) -> int:
    for pat, multiplier in _TIME_PATTERNS:
        m = pat.search(text)
        if m:
            if len(m.groups()) > 0:
                return int(float(m.group(1)) * multiplier)
            return multiplier
    return 90


def _extract_by_keywords(text: str, keyword_map: dict) -> list[str]:
    found = []
    for label, variants in keyword_map.items():
        for variant in variants:
            if variant in text:
                found.append(label)
                break
    return found


def _extract_core_action(text: str) -> tuple[str, str]:
    # 优先匹配包含“顺便”或“再”/“还”的附加动作
    # 简单做法：第一个匹配到的动作是核心，其余是附加
    matched = []
    for label, variants in ACTION_KEYWORDS.items():
        for variant in variants:
            if variant in text:
                matched.append(label)
                break

    if not matched:
        return "", ""

    core = matched[0]
    extra = matched[1] if len(matched) > 1 else ""
    return core, extra


def parse_intent_rule(text: str) -> tuple[Intent, str | None]:
    """基于规则快速解析意图，返回 Intent 和可能的追问。"""
    if not text or not text.strip():
        return _DEFAULT_INTENT, "你想去哪种类型的周末地点？"

    text = text.strip()

    transport = "开车"
    for tmode, variants in TRANSPORT_KEYWORDS.items():
        if any(v in text for v in variants):
            transport = tmode
            break

    time_minutes = _extract_time(text)
    hard_constraints = _extract_by_keywords(text, HARD_CONSTRAINTS)
    soft_preferences = _extract_by_keywords(text, SOFT_PREFERENCES)
    core_action, extra_action = _extract_core_action(text)

    # 如果是“山里/郊区”等远地，默认车程映射到 1~2 小时
    if any(w in text for w in ["山里", "郊区", "远点", "远一点"]):
        time_minutes = max(time_minutes, 90)

    intent = Intent(
        transport=transport,
        time_minutes=time_minutes,
        hard_constraints=hard_constraints,
        soft_preferences=soft_preferences,
        core_action=core_action,
        extra_action=extra_action,
    )

    follow_up = None
    if not core_action:
        follow_up = "你主要想在那里做什么？比如工作、喝咖啡、徒步还是发呆？"

    return intent, follow_up
