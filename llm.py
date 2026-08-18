import json
import ollama

MODEL = "qwen3.5:9b"


def ask(prompt: str, system: str = "") -> str:
    """모델에게 물어보고 텍스트로 답을 받는다."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(model=MODEL, messages=messages)
    return response["message"]["content"]


def ask_json(prompt: str, system: str = "") -> dict:
    """모델에게 물어보고 JSON 형태로 답을 받는다."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        think=False,
        format="json",          
    )
    return json.loads(response["message"]["content"])
