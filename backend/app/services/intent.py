import json
from app.services.llm import chat
from app.models import Intent


def parse_intent(text: str) -> tuple[Intent, str | None]:
    system = (
        "你是一个周末出行意图解析器。把用户的自然语言描述解析成结构化 JSON，"
        "包含交通方式、预计车程分钟数、硬约束、软偏好、核心动作、附加动作。"
    )
    user = f"""用户输入：{text}

请返回 JSON：
{{
  "transport": "开车",
  "time_minutes": 90,
  "hard_constraints": [],
  "soft_preferences": [],
  "core_action": "",
  "extra_action": ""
}}
"""
    content = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    data = json.loads(content)
    intent = Intent(**data)
    follow_up = None
    if not intent.core_action:
        follow_up = "你主要想在那里做什么？比如工作、喝咖啡、徒步还是发呆？"
    return intent, follow_up
