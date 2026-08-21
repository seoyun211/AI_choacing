from llm import ask_json
from rag import search, format_context
from pipeline import analyze, ANALYZE_SYSTEM


# ============================================================
# 2단계 · 평가 (공고 참고)
# ============================================================
EVALUATE_RAG_SYSTEM = """당신은 10년 경력의 한국 기업 채용 담당자입니다.
분석 결과와 실제 채용공고를 근거로 답변을 평가합니다.

[필수] 모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.
[필수] 반드시 분석 결과에 근거해서 평가하세요.
[필수] 채용공고의 자격요건·우대사항·전형절차를 참고하여
       "어느 공고에서 무엇을 요구하는지"를 구체적으로 언급하세요.
       예: "델타모바일 공고의 우대사항인 대용량 로그 처리 경험을 강조하세요"
[필수] 비현실적 주장이 있다면 반드시 개선점에 포함하세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "score": 0에서 100 사이의 정수 (100점 만점),
  "strengths": ["잘한 점", "..."],
  "improvements": ["개선할 점", "..."]
}"""


def evaluate_rag(job, question, answer, analysis, context):
    prompt = f"""지원 직무: {job}
면접 질문: {question}
지원자 답변: {answer}

[분석 결과]
수치 언급: {analysis.get('has_number')} {analysis.get('numbers')}
기술 언급: {analysis.get('has_tech')} {analysis.get('techs')}
본인 역할: {analysis.get('has_role')} {analysis.get('role')}
어려움 언급: {analysis.get('has_difficulty')}
어조: {analysis.get('tone')}
비현실적 주장: {analysis.get('unrealistic_claims')}
분량: {analysis.get('length_issue')}

[실제 채용공고]
{context}

위 분석과 채용공고를 근거로 평가해 주세요."""
    return ask_json(prompt, system=EVALUATE_RAG_SYSTEM)


# ============================================================
# 3단계 · 재작성 (공고 참고)
# ============================================================
REWRITE_RAG_SYSTEM = """당신은 면접 답변을 다듬는 전문가입니다.

[필수] 모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.
[필수] 반드시 3~5문장의 완성된 답변을 작성하세요. 빈 값은 허용되지 않습니다.
[필수] 원래 답변에 없는 경험이나 수치를 지어내지 마세요.
[필수] 채용공고가 요구하는 역량과 지원자의 경험이 연결되도록 다듬으세요.
[필수] 존댓말과 격식체로 바꾸되, 지원자의 열정과 개성은 살리세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "revised_answer": "다시 작성한 답변 (3~5문장)"
}"""


def rewrite_rag(job, question, answer, analysis, evaluation, context):
    improvements = "\n".join(
        "- " + s for s in evaluation.get("improvements", [])
    )
    prompt = f"""지원 직무: {job}
면접 질문: {question}
원래 답변: {answer}

[개선할 점]
{improvements}

[실제 채용공고]
{context}

위 내용을 반영해 답변을 다시 작성해 주세요."""
    return ask_json(prompt, system=REWRITE_RAG_SYSTEM)


# ============================================================
# 전체 실행
# ============================================================
def run_pipeline_rag(job: str, question: str, answer: str) -> dict:
    # 0단계 — 관련 공고 검색
    docs = search(job, answer, k=3)
    context = format_context(docs)
    sources = [d.metadata.get("company", "?") for d in docs]

    # 1단계 — 분석 (공고 불필요)
    analysis = analyze(job, question, answer)

    # 2단계 — 평가 (공고 참고)
    evaluation = evaluate_rag(job, question, answer, analysis, context)

    # 3단계 — 재작성 (공고 참고)
    revision = rewrite_rag(job, question, answer, analysis, evaluation, context)

    return {
        "score": evaluation["score"],
        "strengths": evaluation["strengths"],
        "improvements": evaluation["improvements"],
        "revised_answer": revision["revised_answer"],
        "_sources": sources,
    }
