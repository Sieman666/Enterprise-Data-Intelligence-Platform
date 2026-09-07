import logging
import sys
from pathlib import Path

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    pass


def generate_text(prompt: str, system_prompt: str | None = None) -> str:
    if not settings.llm_api_key:
        raise LLMClientError("LLM_API_KEY is not configured")

    if not settings.llm_model:
        raise LLMClientError("LLM_MODEL is not configured")

    try:
        client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    or "You are a helpful enterprise analytics assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        logger.info("Generated text with LLM model %s", settings.llm_model)
        return content.strip()
    except Exception as exc:
        logger.exception("LLM text generation failed")
        raise LLMClientError(str(exc)) from exc
