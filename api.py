from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_system import CareerAI
from career_data import CAREER_TIPS

# 1. 앱 초기화
app = FastAPI()

# 2. CORS 설정 (Next.js인 localhost:3000 접속 허용 필수!)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 개발 중엔 모든 곳 허용 (배포 시 origins로 변경 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. AI 로드
ai_system = CareerAI()
ai_system.load_data(CAREER_TIPS)

class ChatRequest(BaseModel):
    user_input: str

@app.post("/api/coach")
async def chat(request: ChatRequest):
    try:
        response_text, sources, draft = ai_system.get_coaching(request.user_input)
        return {"answer": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 실행 명령어: uvicorn api:app --reload --port 8000