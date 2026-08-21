from fastapi import FastAPI
from schemas import CoachingRequest, CoachingResult
from llm import ask_json
import time
from pipeline import run_pipeline

app = FastAPI(title="AI 면접 코치")

SYSTEM = """당신은 10년 경력의 한국 기업 채용 담당자입니다.
지원자의 면접 답변을 평가하고 구체적인 조언을 제공합니다.

[필수] 모든 값은 한국어로만 작성하세요. 한자와 중국어를 절대 사용하지 마세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "score": 0에서 100 사이의 정수 (100점 만점),
  "strengths": ["잘한 점", "..."],
  "improvements": ["개선할 점", "..."],
  "revised_answer": "다듬은 답변 예시"
}"""


@app.post("/coaching", response_model=CoachingResult)
def get_coaching(data: CoachingRequest) -> CoachingResult:
    start = time.time()
    prompt = f"""지원 직무: {data.job}
면접 질문: {data.question}
지원자 답변: {data.answer}

위 답변을 평가해 주세요."""

    result = ask_json(prompt, system=SYSTEM)
    print(f"소요 시간: {time.time() - start:.1f}초")
    return CoachingResult(**result)

@app.post("/coaching/pipeline", response_model=CoachingResult)
def get_coaching_pipeline(data: CoachingRequest) -> CoachingResult:
    # 신규 파이프라인 방식
    start = time.time()
    result = run_pipeline(data.job, data.question, data.answer)
    print(f"[파이프라인] 소요 시간: {time.time() - start:.1f}초")
    return CoachingResult(**result)

@app.post("/coaching/langchain", response_model=CoachingResult)
def get_coaching_lc(data: CoachingRequest) -> CoachingResult:
    start = time.time()
    result = run_pipeline_lc(data.job, data.question, data.answer)
    print(f"[LangChain] 소요 시간: {time.time() - start:.1f}초")
    return CoachingResult(**result)
