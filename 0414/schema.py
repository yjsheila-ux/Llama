from pydantic import BaseModel, Field

class OpenAIReponse(BaseModel):
    result: str = Field(description="최종 답변")
    confidence: float = Field(description="0~1 사이의 신뢰도")
