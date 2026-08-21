from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from schemas import Analysis, Evaluation, Revision

MODEL = "qwen3.5:9b"

llm = ChatOllama(model=MODEL, temperature=0.3)


# ============================================================
# 1단계 · 분석
# ============================================================
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 면접 답변을 객관적으로 분석하는 분석가입니다.\n"
     "평가나 조언은 하지 말고, 답변에 무엇이 있고 무엇이 없는지만 파악하세요.\n"
     "모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요."),
    ("human",
     "지원 직무: {job}\n"
     "면접 질문: {question}\n"
     "지원자 답변: {answer}\n\n"
     "위 답변을 분석해 주세요."),
])

analyze_chain = analyze_prompt | llm.with_structured_output(
    Analysis, method="json_schema"
)


# ============================================================
# 2단계 · 평가
# ============================================================
evaluate_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 10년 경력의 한국 기업 채용 담당자입니다.\n"
     "분석 결과를 근거로 답변을 평가합니다.\n"
     "모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.\n"
     "반드시 분석 결과에 근거해서 평가하세요. 추측하지 마세요.\n"
     "비현실적 주장이 있다면 반드시 개선점에 포함하세요.\n"
     "어조가 면접에 부적절하면 반드시 개선점에 포함하세요.\n"
     "점수는 0에서 100 사이의 정수입니다."),
    ("human",
     "지원 직무: {job}\n"
     "면접 질문: {question}\n"
     "지원자 답변: {answer}\n\n"
     "[분석 결과]\n"
     "수치 언급: {has_number} {numbers}\n"
     "기술 언급: {has_tech} {techs}\n"
     "본인 역할: {has_role} {role}\n"
     "어려움 언급: {has_difficulty}\n"
     "답변 구조: {structure}\n"
     "어조: {tone}\n"
     "비현실적 주장: {unrealistic_claims}\n"
     "분량: {length_issue}\n\n"
     "위 분석을 근거로 평가해 주세요."),
])

evaluate_chain = evaluate_prompt | llm.with_structured_output(
    Evaluation, method="json_schema"
)


# ============================================================
# 3단계 · 재작성
# ============================================================
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 면접 답변을 다듬는 전문가입니다.\n"
     "모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.\n"
     "반드시 3~5문장의 완성된 답변을 작성하세요. 빈 값은 허용되지 않습니다.\n"
     "원래 답변에 없는 경험이나 수치를 지어내지 마세요.\n"
     "존댓말과 격식체로 바꾸되, 지원자의 열정과 개성은 살리세요."),
    ("human",
     "지원 직무: {job}\n"
     "면접 질문: {question}\n"
     "원래 답변: {answer}\n\n"
     "[분석 결과]\n"
     "본인 역할: {has_role} / 어려움: {has_difficulty}\n"
     "분량: {length_issue} / 어조: {tone}\n\n"
     "[개선할 점]\n{improvements}\n\n"
     "위 내용을 반영해 답변을 다시 작성해 주세요."),
])

rewrite_chain = rewrite_prompt | llm.with_structured_output(
    Revision, method="json_schema"
)


# ============================================================
# 전체 실행 (오케스트레이션)
# ============================================================
def run_pipeline_lc(job: str, question: str, answer: str) -> dict:
    base = {"job": job, "question": question, "answer": answer}

    analysis = analyze_chain.invoke(base)

    evaluation = evaluate_chain.invoke({
        **base,
        **analysis.model_dump(),
    })

    revision = rewrite_chain.invoke({
        **base,
        "has_role": analysis.has_role,
        "has_difficulty": analysis.has_difficulty,
        "length_issue": analysis.length_issue,
        "tone": analysis.tone,
        "improvements": "\n".join("- " + s for s in evaluation.improvements),
    })

    return {
        "score": evaluation.score,
        "strengths": evaluation.strengths,
        "improvements": evaluation.improvements,
        "revised_answer": revision.revised_answer,
    }
