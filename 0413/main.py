from llama_cpp import Llama
from fastapi import FastAPI, Body

# Llama 모델 로트
llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

# 언어 모델에게 규칙을 지정하는 최상위 지시문
SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

# # 사용자 인풋
# user_input = input("질문을 입력하세요.").strip()
# # 질문 생성
# result = llm.create_chat_completion(
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": user_input},
#     ],
#     max_tokens=256,
#     temperature=0.7,
# )

# print(result["choices"][0]) 터미널에서 가능

# fastapi 로 실행

app = FastAPI()

@app.post("/chats")
def generate_chat_handler(
    # {"user_input" : "python이 뭐야?"}
    user_input: str = Body(..., embed=True), # 사용자 인풋
):
    # 질문 생성
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        max_tokens=256,
        temperature=0.7,
    )
    return {"result": result["choices"][0]["message"]["content"].strip()}
