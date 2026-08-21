from pydantic import BaseModel, Field


class CoachingRequest(BaseModel):
    job: str = Field(min_length=1, description="관심 직무")
    question: str = Field(min_length=1, description="면접 질문")
    answer: str = Field(min_length=10, description="내 답변")


class CoachingResult(BaseModel):
    score: int = Field(ge=0, le=100, description="답변 점수")
    strengths: list[str] = Field(description="잘한 점")
    improvements: list[str] = Field(description="개선할 점")
    revised_answer: str = Field(description="다듬은 답변 예시")

class Analysis(BaseModel):
    """1단계 분석 결과"""
    has_number: bool = Field(description="수치나 성과가 언급되었는가")
    numbers: list[str] = Field(description="언급된 수치")
    has_tech: bool = Field(description="기술이나 도구가 언급되었는가")
    techs: list[str] = Field(description="언급된 기술")
    has_role: bool = Field(description="본인의 역할이 명시되었는가")
    role: str = Field(description="본인이 맡은 역할")
    has_difficulty: bool = Field(description="겪은 어려움이 언급되었는가")
    structure: str = Field(description="답변의 구조를 한 문장으로")
    tone: str = Field(description="답변의 어조")
    unrealistic_claims: list[str] = Field(description="검증이 필요한 비현실적 주장")
    length_issue: str = Field(description="적절함 또는 너무 짧음 또는 너무 장황함")


class Evaluation(BaseModel):
    """2단계 평가 결과"""
    score: int = Field(ge=0, le=100, description="답변 점수")
    strengths: list[str] = Field(description="잘한 점")
    improvements: list[str] = Field(description="개선할 점")


class Revision(BaseModel):
    """3단계 재작성 결과"""
    revised_answer: str = Field(description="다시 작성한 답변")
