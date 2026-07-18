from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import UserQuery, Recommendation

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


@app.post("/recommend", response_model=list[Recommendation])
def recommend(query: UserQuery):
    # TODO: 接入意图解析、天气、POI 排序
    return []


@app.post("/feedback")
def feedback(type: str):
    # TODO: 基于失败维度替换全部 3 个推荐
    return {"type": type, "recommendations": []}
