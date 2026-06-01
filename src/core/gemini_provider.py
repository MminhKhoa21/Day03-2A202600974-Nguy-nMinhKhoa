import time
import google.generativeai as genai

from typing import Dict, Any, Optional, Generator

from src.core.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key)

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(
            model_name
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:

        start_time = time.time()

        full_prompt = prompt

        if system_prompt:
            full_prompt = (
                f"System: {system_prompt}\n\n"
                f"User: {prompt}"
            )

        try:

            response = self.model.generate_content(
                full_prompt
            )

            end_time = time.time()

            latency_ms = int(
                (end_time - start_time) * 1000
            )

            content = response.text

            usage = {
                "prompt_tokens":
                    getattr(
                        response.usage_metadata,
                        "prompt_token_count",
                        0
                    ),
                "completion_tokens":
                    getattr(
                        response.usage_metadata,
                        "candidates_token_count",
                        0
                    ),
                "total_tokens":
                    getattr(
                        response.usage_metadata,
                        "total_token_count",
                        0
                    )
            }

            return {
                "content": content,
                "usage": usage,
                "latency_ms": latency_ms,
                "provider": "google"
            }

        except Exception as e:

            error_message = str(e)

            # Gemini quota exceeded
            if "429" in error_message:

                return {
                    "content": (
                        "Final Answer: "
                        "Gemini API đã hết quota miễn phí. "
                        "Vui lòng thử lại sau hoặc thay API key."
                    ),
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    },
                    "latency_ms": 0,
                    "provider": "google"
                }

            # Model không tồn tại
            if "404" in error_message:

                return {
                    "content": (
                        "Final Answer: "
                        "Model Gemini không tồn tại hoặc không được hỗ trợ."
                    ),
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    },
                    "latency_ms": 0,
                    "provider": "google"
                }

            raise

    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:

        full_prompt = prompt

        if system_prompt:
            full_prompt = (
                f"System: {system_prompt}\n\n"
                f"User: {prompt}"
            )

        try:

            response = self.model.generate_content(
                full_prompt,
                stream=True
            )

            for chunk in response:
                if hasattr(chunk, "text"):
                    yield chunk.text

        except Exception as e:

            if "429" in str(e):
                yield (
                    "Gemini API đã hết quota miễn phí. "
                    "Vui lòng thử lại sau."
                )
                return

            raise