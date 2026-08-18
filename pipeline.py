from llm import ask_json

# ============================================================
# 1단계 · 분석 — 답변에 무엇이 있고 없는지만 파악
# ============================================================
ANALYZE_SYSTEM = """당신은 면접 답변을 객관적으로 분석하는 분석가입니다.
평가나 조언은 하지 말고, 답변에 무엇이 있고 무엇이 없는지만 파악하세요.

[필수] 모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "has_number": true 또는 false,
  "numbers": ["언급된 수치나 성과"],
  "has_tech": true 또는 false,
  "techs": ["언급된 기술이나 도구"],
  "has_role": true 또는 false,
  "role": "본인이 맡은 역할 (없으면 빈 문자열)",
  "has_difficulty": true 또는 false,
  "structure": "답변의 구조를 한 문장으로",
  "tone": "답변의 어조 (격식체/구어체/감정적 등)",
  "unrealistic_claims": ["검증이 필요한 비현실적 주장 (없으면 빈 목록)"],
  "length_issue": "적절함 또는 너무 짧음 또는 너무 장황함"
}"""


def analyze(job: str, question: str, answer: str) -> dict:
    prompt = f"""지원 직무: {job}
면접 질문: {question}
지원자 답변: {answer}

위 답변을 분석해 주세요."""
    return ask_json(prompt, system=ANALYZE_SYSTEM)


# ============================================================
# 2단계 · 평가 — 분석 결과를 근거로 점수와 개선점 도출
# ============================================================
EVALUATE_SYSTEM = """당신은 10년 경력의 한국 기업 채용 담당자입니다.
분석 결과를 근거로 답변을 평가합니다.

[필수] 모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.
[필수] 반드시 분석 결과에 근거해서 평가하세요. 추측하지 마세요.
[필수] 비현실적 주장이 있다면 반드시 개선점에 포함하세요.
[필수] 어조가 면접에 부적절하면 반드시 개선점에 포함하세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "score": 0에서 100 사이의 정수 (100점 만점),
  "strengths": ["잘한 점", "..."],
  "improvements": ["개선할 점", "..."]
}"""


def evaluate(job: str, question: str, answer: str, analysis: dict) -> dict:
    prompt = f"""지원 직무: {job}
면접 질문: {question}
지원자 답변: {answer}

[분석 결과]
수치 언급: {analysis.get('has_number')} {analysis.get('numbers')}
기술 언급: {analysis.get('has_tech')} {analysis.get('techs')}
본인 역할: {analysis.get('has_role')} {analysis.get('role')}
어려움 언급: {analysis.get('has_difficulty')}
답변 구조: {analysis.get('structure')}
어조: {analysis.get('tone')}
비현실적 주장: {analysis.get('unrealistic_claims')}
분량: {analysis.get('length_issue')}

위 분석을 근거로 평가해 주세요."""
    return ask_json(prompt, system=EVALUATE_SYSTEM)


# ============================================================
# 3단계 · 재작성 — 분석과 평가를 반영해 답변을 다시 작성
# ============================================================
REWRITE_SYSTEM = """당신은 면접 답변을 다듬는 전문가입니다.
지원자의 원래 답변을 개선점에 맞춰 다시 작성합니다.

[필수] 모든 값은 한국어로만 작성하세요. 한자를 사용하지 마세요.
[필수] 지원자가 말하지 않은 경험을 지어내지 마세요.
[필수] 원래 답변에 없는 수치를 만들어내지 마세요.
       수치가 필요한 자리는 "(구체적 수치)"로 표시하세요.
[필수] 격식 있는 면접 어조로 작성하세요.

반드시 아래 JSON 형식으로만 답하세요.
{
  "revised_answer": "다시 작성한 답변"
}"""


def rewrite(job: str, question: str, answer: str,
            analysis: dict, evaluation: dict) -> dict:
    prompt = f"""지원 직무: {job}
면접 질문: {question}
원래 답변: {answer}

[분석 결과]
부족한 부분: 역할 {analysis.get('has_role')} / 어려움 {analysis.get('has_difficulty')}
분량: {analysis.get('length_issue')}
어조: {analysis.get('tone')}

[개선할 점]
{chr(10).join('- ' + s for s in evaluation.get('improvements', []))}

위 내용을 반영해 답변을 다시 작성해 주세요."""
    return ask_json(prompt, system=REWRITE_SYSTEM)


# ============================================================
# 전체 파이프라인 실행 (오케스트레이션)
# ============================================================
def run_pipeline(job: str, question: str, answer: str) -> dict:
    """분석 → 평가 → 재작성 순서로 실행하고 결과를 합친다."""
    analysis = analyze(job, question, answer)
    evaluation = evaluate(job, question, answer, analysis)
    revision = rewrite(job, question, answer, analysis, evaluation)

    return {
        "score": evaluation["score"],
        "strengths": evaluation["strengths"],
        "improvements": evaluation["improvements"],
        "revised_answer": revision["revised_answer"],
        "_analysis": analysis,      # 중간 결과도 함께 반환
    }
