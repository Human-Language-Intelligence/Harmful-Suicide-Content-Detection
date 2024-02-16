from typing import Optional, Tuple

from projects.models.gpt.async_request import api_query


async def request_chatgpt(
    model: str,
    system: str,
    user: str,
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 2048,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    assistant: Optional[str] = None,
    assistant_user: Optional[str] = None,
    stop: Optional[str] = None,
    n: int = 1,
) -> Tuple[str, str, str, int, int, int]:
    assert model in [
        "gpt-3.5-turbo-0301",
        "gpt-4-0314",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0613",
        "gpt-4",
        "gpt-4-32k-0613",
        "gpt-4-32k",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4-1106-preview"
    ], "Not in supported ChatGPT models"

    if system == "":
        prompt = [{"role": "user", "content": user}]
    else:
        prompt = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    if assistant is not None and assistant_user is not None:
        prompt.append({"role": "assistant", "content": assistant})
        prompt.append({"role": "user", "content": assistant_user})

    result, final_result, finish_reason, usages, prompt_usages, completion_usages = await api_query(
        model=model,
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        stop=stop,
        n=n,
    )
    return result, final_result, finish_reason, usages, prompt_usages, completion_usages


async def request_instructgpt(
    model: str,
    prompt: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    presence_penalty: float,
    frequency_penalty: float,
) -> Tuple[str, str, str, int, int, int]:
    assert model in [
        "text-davinci-003",
        "text-curie-001",
        "text-babbage-001",
        "text-ada-001",
    ], "Not supported instructGPT"

    result, final_result, finish_reason, usages, prompt_usages, completion_usages = await api_query(
        model=model,
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )
    return result, final_result, finish_reason, usages, prompt_usages, completion_usages
