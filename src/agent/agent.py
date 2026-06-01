import re
import json
from typing import List, Dict, Any

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class MaxStepsExceededError(Exception):
    pass


class ReActAgent:
    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Dict[str, Any]],
        max_steps: int = 5,
        system_prompt: str = None,
    ):
        self.llm = llm
        self.tools = {tool["name"]: tool for tool in tools}
        self.max_steps = max_steps
        self.history = []
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        tool_desc = "\n".join(
            [
                f"- {name}: {tool['description']}"
                for name, tool in self.tools.items()
            ]
        )

        return f"""
Bạn là trợ lý AI hỗ trợ giáo viên tiểu học tạo câu hỏi cho học sinh lớp 1-5.

Bạn có các công cụ sau:
{tool_desc}

Định dạng bắt buộc:

Thought: suy nghĩ của bạn
Action: tên_hàm(json)

Khi hoàn thành:

Final Answer: nội dung trả lời

Lưu ý:
- Action phải chứa JSON hợp lệ.
- Không tự tạo Observation.
- Hệ thống sẽ tự thêm Observation sau khi tool chạy.
"""

    def run(self, user_input: str) -> str:
        logger.log_event(
            "AGENT_START",
            {
                "input": user_input,
                "model": self.llm.model_name,
            },
        )

        conversation = f"Người dùng: {user_input}\n"

        for step in range(self.max_steps):

            try:
                response = self.llm.generate(
                    conversation
                    + "\nHãy tiếp tục. Nếu hoàn thành thì trả về Final Answer.",
                    system_prompt=self.system_prompt,
                )

            except Exception as e:
                logger.log_event(
                    "AGENT_LLM_ERROR",
                    {
                        "step": step + 1,
                        "error": str(e),
                    },
                )

                if "429" in str(e):
                    return (
                        "Hệ thống Gemini hiện đã hết quota hoặc bị giới hạn tốc độ.\n"
                        "Vui lòng thử lại sau vài phút hoặc đổi API Key."
                    )

                raise

            content = response.get("content", "").strip()

            logger.log_event(
                "AGENT_STEP",
                {
                    "step": step + 1,
                    "raw_output": content,
                },
            )

            self.history.append(
                {
                    "step": step + 1,
                    "raw": content,
                }
            )

            # ==========================
            # Final Answer
            # ==========================
            if "Final Answer:" in content:
                final_answer = content.split(
                    "Final Answer:",
                    1
                )[1].strip()

                logger.log_event(
                    "AGENT_END",
                    {
                        "steps": step + 1,
                        "final_answer": final_answer,
                    },
                )

                return final_answer

            # ==========================
            # Action
            # ==========================
            action_match = re.search(
                r"Action:\s*(\w+)\((.*)\)",
                content,
                re.DOTALL,
            )

            if not action_match:
                conversation += content + "\n"

                logger.log_event(
                    "AGENT_NO_ACTION",
                    {
                        "step": step + 1,
                    },
                )

                continue

            tool_name = action_match.group(1)
            args_str = action_match.group(2).strip()

            logger.log_event(
                "AGENT_ACTION_REQUEST",
                {
                    "tool": tool_name,
                    "args_str": args_str,
                },
            )

            # ==========================
            # Tool không tồn tại
            # ==========================
            if tool_name not in self.tools:

                observation = (
                    f"Lỗi: không tồn tại công cụ '{tool_name}'"
                )

            else:
                try:
                    args = json.loads(args_str)

                    func = self.tools[tool_name]["func"]

                    if isinstance(args, dict):
                        result = func(**args)

                    elif isinstance(args, list):
                        result = func(*args)

                    else:
                        result = func(args)

                    observation = str(result)

                    logger.log_event(
                        "AGENT_OBSERVATION",
                        {
                            "tool": tool_name,
                            "result": observation,
                        },
                    )

                    # ==================================
                    # TRẢ KẾT QUẢ NGAY CHO TOOL TẠO CÂU HỎI
                    # ==================================
                    if tool_name == "generate_questions":

                        logger.log_event(
                            "AGENT_END",
                            {
                                "steps": step + 1,
                                "final_answer": observation,
                            },
                        )

                        return observation

                except Exception as e:

                    observation = f"Lỗi thực thi: {e}"

                    logger.log_event(
                        "AGENT_EXECUTION_ERROR",
                        {
                            "tool": tool_name,
                            "error": str(e),
                        },
                    )

            content_clean = re.sub(
                r"^Observation:.*$",
                "",
                content,
                flags=re.MULTILINE | re.IGNORECASE,
            )

            conversation += (
                content_clean.strip()
                + f"\nObservation: {observation}\n"
            )

        raise MaxStepsExceededError(
            f"Đã vượt quá {self.max_steps} bước suy luận."
        )