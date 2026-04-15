import asyncio

from contextlib import asynccontextmanager
from llama_cpp import Llama
from openai import AsyncOpenAI
from fastapi import FastAPI, Body, Request, Depends
from fastapi.responses import StreamingResponse

from config import settings
from schema import OpenAIReponse


# 언어 모델에게 규칙을 지정하는 최상위 지시문
SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.llm = Llama(
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=2,
        verbose=False,
        chat_format="llama-3",
    )
    app.state.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    yield

app = FastAPI(lifespan=lifespan)

# 요청 객체(request)에서 llm 객체를 접근할 수 있게 도와주는 의존성 함수
def get_llm(request: Request):
    return request.app.state.llm

def get_openai_client(request: Request):
    return request.app.state.openai_client

@app.post("/chats")
async def generate_chat_handler(
    user_input: str = Body(..., embed=True), # 사용자 인풋
        # request:Request,
    llm = Depends(get_llm),
):
    #RAG(=Retrieval Augmented Generation)
    # 질문 생성
    async def event_generator():
        result = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=256,
            temperature=0.7,
            stream=True # 응답을 토큰 단위로    
        )
        for chunk in result:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                yield token
                await asyncio.sleep(0.1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )

#   curl -N -X 'POST' \ 
#   'http://127.0.0.1:8000/chats' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "user_input": "Python이 뭐야?"
# }'

# >>> def factorial(n):
# ...     ans =1
# ...     for i in range(1,n+1):
# ...         ans *= i
# ...     return ans
# 제너레이터 
# >>> def factorial(n):
# ...     ans = 1
# ...     i = 1
# ...     while i <= n:
# ...         ans *= i
# ...         yield ans
# ...         i += 1

# >>> def factorial(n):
# ...     ans = 1
# ...     for i in range(1, n+1):
# ...         ans *= i
# ...         yield ans
# >>> factorial(10)
# <generator object factorial at 0x102f7ac00>
# >>>gen = fafactorial(10)
# >>> next(gen)

# @app.post("/openai")
# def openai_handler(
#     user_input: str = Body(..., embed=True),
#     openai_client = Depends(get_openai_client),
# ):
#     response = openai_client.responses.parse(
#         model="gpt-4.1-mini",
#         input = user_input,
#         text_format=OpenAIReponse,
#     )
#     # if response.output_parsed.confidence <= 0.95: # 0.5
#     #     return  # 재시도

#     # return response.output_parsed # 동기 쓰레드풀이니까 상관안씀

@app.post("/openai")
async def openai_handler(
    user_input: str = Body(..., embed=True),
    openai_client = Depends(get_openai_client),
):
    async def event_generator():
        async with openai_client.responses.stream(
            model="gpt-4.1-mini",
            input = user_input,
            text_format=OpenAIReponse,
        ) as stream:
            async for event in stream:
                # 텍스트 토큰
                if event.type =="response.output_text.delta":
                    yield event.dalta
                # 연결 종료
                elif event.type =="response.completed":
                    break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
