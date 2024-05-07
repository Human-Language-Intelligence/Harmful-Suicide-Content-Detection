import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union

from loguru import logger
import openai
from openai import AsyncOpenAI


def read_json(filepath: str) -> Dict[Any, Any]:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


config = read_json(os.path.join(os.path.dirname(__file__), "openai_config.json"))
#openai.api_key = config["api_key"]
client = AsyncOpenAI(api_key = config["api_key"])

async def api_query(
    model: str,
    prompt: Union[str, List[Dict[str, str]]],
    temperature: float = 0.0,
    seed: int = 42,
    top_p: float = 1.0,
    max_tokens: int = 512,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    stop: Optional[str] = None,
    return_text: str = "",
    return_texts: str = "",
    finish_reason: str = "",
    return_usages: int = 0,
    return_prompt_usages: int = 0,
    return_completion_usages: int = 0,
    n: int = 1,
) -> Any:
    try:
        if model in [
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
        ]:
            #response = await openai.ChatCompletion.acreate(
            response = await client.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                n=n,
            )
            # from functools import reduce
            # return_text = reduce(lambda x, y: x + y, [choice["message"]["content"] for choice in response["choices"]], '')
            response = response.model_dump_json(indent=2)
            response = json.loads(response)
            
            return_text = response["choices"][0]["message"]["content"]
            return_texts += return_text
            finish_reason = response["choices"][0]["finish_reason"]
            return_usages += response["usage"]["total_tokens"]
            return_prompt_usages += response["usage"]["prompt_tokens"]
            return_completion_usages += response["usage"]["completion_tokens"]
        elif model in [
            "text-davinci-003",
            "text-curie-001",
            "text-babbage-001",
            "text-ada-001",
        ]:
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stop=stop,
                n=n,
            )
            return_text = response["choices"][0]["text"]
            return_texts += return_text
            finish_reason = response["choices"][0]["finish_reason"]
            return_usages += response["usage"]["total_tokens"]
            return_prompt_usages += response["usage"]["prompt_tokens"]
            return_completion_usages += response["usage"]["completion_tokens"]
        else:
            raise ValueError("Not supported model.")

    except openai.error.InvalidRequestError as e:  # number of tokens > 4097
        logger.error(e)
        logger.error("Number of tokens > 4097")
        return (
            return_text,
            return_texts,
            finish_reason,
            return_usages,
            return_prompt_usages,
            return_completion_usages,
        )
    except (
        openai.error.ServiceUnavailableError,
        openai.error.RateLimitError,
        openai.error.APIError,
        openai.error.Timeout,
    ) as e:
        logger.warning(e)
        logger.warning("Try again in 30 seconds.")
        await asyncio.sleep(30)
        (
            return_text,
            return_texts,
            finish_reason,
            return_usages,
            return_prompt_usages,
            return_completion_usages,
        ) = await api_query(
            model,
            prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stop=stop,
            return_text=return_text,
            return_texts=return_texts,
            finish_reason=finish_reason,
            return_usages=return_usages,
            return_prompt_usages=return_prompt_usages,
            return_completion_usages=return_completion_usages,
            n=n,
        )

    if finish_reason == "stop":
        return (
            return_text,
            return_texts,
            finish_reason,
            return_usages,
            return_prompt_usages,
            return_completion_usages,
        )
    elif model in [
        "text-davinci-003",
        "text-curie-001",
        "text-babbage-001",
        "text-ada-001",
    ]:
        return (
            return_text,
            return_texts,
            finish_reason,
            return_usages,
            return_prompt_usages,
            return_completion_usages,
        )
    else:
        logger.warning("finish_reason is not stop.")
        prompt.append({"role": "user", "content": return_text})
        return await api_query(
            model,
            prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=1024,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stop=stop,
            return_text=return_text,
            return_texts=return_texts,
            finish_reason=finish_reason,
            return_usages=return_usages,
            return_prompt_usages=return_prompt_usages,
            return_completion_usages=return_completion_usages,
            n=n,
        )
