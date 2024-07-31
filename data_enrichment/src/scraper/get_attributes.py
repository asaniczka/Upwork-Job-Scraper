"""
This module constains the worker responsible for gather client data.
"""

# pylint:disable=wrong-import-position

import sys
import os
from datetime import datetime
import re

from pydantic import ValidationError
import httpx
from rich import print
from wrapworks import timeit, cwdtoenv
from dotenv import load_dotenv
import chompjs

cwdtoenv()
load_dotenv()

from src.scraper.zyte import zyte_worker
from src.scraper.browser_worker import get_page
from src.models.upwork_models import PostingAttributes, OPENAPI_SCHEMA
from src.models.genai_models import (
    ValidLLMModels,
    LLM_COST_PER_TOKEN,
    LLMMessage,
    LLMMessageLog,
    AIResponse,
    LLMRoles,
)

# ----------------------------------------
#               WORKERS
# ----------------------------------------


def invoke_openai(
    model: ValidLLMModels | str, messages: LLMMessageLog, api_key: str
) -> AIResponse:
    """"""

    if not isinstance(model, str):
        model = model.value

    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [x.model_dump() for x in messages.messages],
        "max_tokens": 1500,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers, timeout=120)

    try:
        data = response.json()
        if data.get("error"):
            print(payload)
            raise RuntimeError(data["error"]["message"])
        return AIResponse(**data)
    except RuntimeError:
        raise
    except Exception as e:
        print(f"Error parsing {response.text}: {type(e).__name__}: {e}")
        raise


def handler_generate_response(
    messages: LLMMessageLog, model: ValidLLMModels, api_key: str
) -> AIResponse:
    """"""

    response = invoke_openai(model, messages, api_key)
    response.calculate_cost(model.value, LLM_COST_PER_TOKEN)

    return response


def convert_response_to_schema(res: str) -> PostingAttributes:
    """"""

    data = chompjs.parse_js_object(res)
    schemed_product = PostingAttributes(**data)
    return schemed_product


def entry_convert_to_schema(
    page: str, api_key: str
) -> tuple[AIResponse, PostingAttributes]:
    """"""

    messages = LLMMessageLog(
        messages=[
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content="""You are a webpage parser. User will provide you with the getTExt of a webpage. 
                Extract all the data to match the schema. Job description must be the full description. Don't truncate.
                Reply in valid JSON.
                """,
            ),
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content=f"""Below is the OpenAPI JSON schema:

                {OPENAPI_SCHEMA}
                """,
            ),
        ]
    )

    messages.messages.append(LLMMessage(role=LLMRoles.USER, content=page))

    running_cost = 0
    retries = 0
    while retries < 5:
        try:
            response = handler_generate_response(
                messages, ValidLLMModels.OPENAI_GPT4o, api_key
            )
            # add current cost to checkpoint incase validation fails
            if response:
                running_cost += response.cost

            parsed_product = convert_response_to_schema(response.text)
            response.cost = running_cost  # combine cost of failed previous runs
            return response, parsed_product
        except ValidationError:
            retries += 1
            print(f"Error extracting metadata with OpenAI. Retrying...")
        except Exception as e:
            retries += 1
            print(
                f"Error extracting metadata with OpenAI: {type(e).__name__}: {e}. Retrying..."
            )


if __name__ == "__main__":
    pass
