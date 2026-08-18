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
