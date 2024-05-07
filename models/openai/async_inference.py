from typing import Optional, Tuple, List

from projects.models.gpt.new_async_request import api_query


async def request_chatgpt(
    model: str,
    system: str,
    user: str,
    temperature: float = 0.0,
    seed: int = 42,
    top_p: float = 1.0,
    max_tokens: int = 2048,
    images: List[str] = [],
    image_types: List[str] = [],
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
        "gpt-4-1106-preview",
        "gpt-4-turbo-2024-04-09"
    ], "Not in supported ChatGPT models"

    if system == "":
        prompt = [{"role": "user", "content": user}]
    else:
        prompt = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    
    if images != []:
        user_message = {
            "role": "user",
            "content": [
                {
                    'type': 'text',
                    'text': user,
                }
            ]
        }
        for image, image_type in zip(images, image_types):
            user_message['content'].append({
                'type': 'image_url',
                'image_url': {
                    'url': f"data:{image_type};base64,{image}",
                    'detail': 'high',
                }
            })

        prompt[-1] = user_message

    if assistant is not None and assistant_user is not None:
        prompt.append({"role": "assistant", "content": assistant})
        prompt.append({"role": "user", "content": assistant_user})

    result, final_result, finish_reason, usages, prompt_usages, completion_usages = await api_query(
        model=model,
        prompt=prompt,
        temperature=temperature,
        seed = seed,
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
