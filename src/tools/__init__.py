from .topics import list_topics
from .questions import generate_questions, review_questions, format_output

TOOLS = [
    {
        "name": "list_topics",
        "description": "Liệt kê các chủ đề môn học theo lớp (1-5). Tham số: grade (int, optional).",
        "func": list_topics,
    },
    {
        "name": "generate_questions",
        "description": (
            "Tạo câu hỏi. Tham số: topic (str), grade (int), type (str: "
            "'multiple_choice', 'fill_in_blank', 'true_false'), difficulty (str), count (int)."
        ),
        "func": generate_questions,
    },
    {
        "name": "review_questions",
        "description": "Kiểm tra chất lượng danh sách câu hỏi. Tham số: questions (list các dict).",
        "func": review_questions,
    },
    {
        "name": "format_output",
        "description": "Định dạng danh sách câu hỏi. Tham số: questions (list), format (str: 'text').",
        "func": format_output,
    },
]

__all__ = [
    "TOOLS",
    "list_topics",
    "generate_questions",
    "review_questions",
    "format_output",
]
