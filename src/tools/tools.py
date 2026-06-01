# src/tools.py
from typing import List, Dict, Any

# Dữ liệu giả lập (trong thực tế có thể lấy từ CSDL hoặc API)
TOPICS_DB = {
    1: ["Phép cộng trừ phạm vi 10", "Nhận biết hình vuông, hình tròn", "Bảng chữ cái"],
    2: ["Phép cộng trừ có nhớ", "Bảng nhân 2, 3, 4, 5", "Từ và câu"],
    3: ["Phép nhân chia", "Hình học cơ bản", "Luyện từ và câu"],
    4: ["Phân số", "Số thập phân", "Tập làm văn"],
    5: ["Số thập phân", "Hình học nâng cao", "Viết đoạn văn"],
}

def list_topics(grade: int = None) -> List[str]:
    """Liệt kê chủ đề môn học theo lớp (1-5). Nếu grade None, trả về tất cả."""
    if grade is None:
        all_topics = []
        for g in range(1, 6):
            all_topics.extend(TOPICS_DB.get(g, []))
        return list(set(all_topics))
    else:
        return TOPICS_DB.get(int(grade), [])

def generate_questions(
    topic: str,
    grade: int,
    type: str = "multiple_choice",
    difficulty: str = "easy",
    count: int = 1
) -> List[Dict[str, Any]]:
    """
    Sinh danh sách câu hỏi mẫu.
    Trong triển khai thực, có thể gọi một LLM khác hoặc lấy từ ngân hàng câu hỏi.
    """
    questions = []
    for i in range(count):
        q = {
            "id": i + 1,
            "topic": topic,
            "grade": grade,
            "type": type,
            "difficulty": difficulty,
        }
        if type == "multiple_choice":
            q["question"] = f"Kết quả của phép tính phù hợp với chủ đề '{topic}' (lớp {grade}) là gì?"
            q["options"] = {"A": "10", "B": "12", "C": "14", "D": "16"}
            q["correct"] = "B"
        elif type == "fill_in_blank":
            q["sentence"] = f"Trong bài học '{topic}', chúng ta đã học về ____."
            q["correct_answer"] = "phép cộng"
        elif type == "true_false":
            q["statement"] = f"2 + 2 = 5 là đúng."
            q["correct"] = False
        else:
            q["question"] = f"Câu hỏi mẫu về '{topic}'."
        questions.append(q)
    return questions

def review_questions(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Kiểm tra chất lượng danh sách câu hỏi."""
    warnings = []
    for q in questions:
        if "topic" not in q or "grade" not in q:
            warnings.append(f"Câu hỏi {q.get('id', '?')} thiếu thông tin.")
    if warnings:
        return {"status": "warning", "warnings": warnings}
    return {"status": "ok", "message": "Tất cả câu hỏi đều phù hợp."}

def format_output(questions: List[Dict[str, Any]], format: str = "text") -> str:
    """Định dạng danh sách câu hỏi thành văn bản."""
    if format == "text":
        lines = []
        for q in questions:
            lines.append(f"Câu {q.get('id', '?')}:")
            if q.get("type") == "multiple_choice":
                lines.append(f"  {q['question']}")
                for key, val in q['options'].items():
                    lines.append(f"    {key}. {val}")
                lines.append(f"  Đáp án: {q['correct']}")
            elif q.get("type") == "fill_in_blank":
                lines.append(f"  {q['sentence']}")
                lines.append(f"  Đáp án: {q['correct_answer']}")
            elif q.get("type") == "true_false":
                lines.append(f"  {q['statement']}")
                lines.append(f"  Đáp án: {'Đúng' if q['correct'] else 'Sai'}")
            else:
                lines.append(f"  {q.get('question', 'Nội dung không rõ')}")
            lines.append("")
        return "\n".join(lines)
    else:
        # Các định dạng khác (docx, pdf) có thể mở rộng sau
        return f"Định dạng '{format}' chưa được hỗ trợ. Tạm trả về dạng text:\n\n{format_output(questions, 'text')}"

# Danh sách công cụ mà agent được phép dùng
TOOLS = [
    {
        "name": "list_topics",
        "description": "Liệt kê các chủ đề môn học theo lớp (1-5). Tham số: grade (int, optional).",
        "func": list_topics,
    },
    {
        "name": "generate_questions",
        "description": "Tạo câu hỏi. Tham số: topic (str), grade (int), type (str: 'multiple_choice', 'fill_in_blank', 'true_false'), difficulty (str: 'easy', 'medium', 'hard'), count (int).",
        "func": generate_questions,
    },
    {
        "name": "review_questions",
        "description": "Kiểm tra chất lượng danh sách câu hỏi. Tham số: questions (list các dict).",
        "func": review_questions,
    },
    {
        "name": "format_output",
        "description": "Định dạng danh sách câu hỏi. Tham số: questions (list), format (str: 'text', 'docx', 'pdf').",
        "func": format_output,
    },
]