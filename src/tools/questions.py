from typing import List, Dict, Any


def generate_questions(
    topic: str,
    grade: int,
    type: str = "multiple_choice",
    difficulty: str = "easy",
    count: int = 1,
) -> List[Dict[str, Any]]:
    """Sinh danh sách câu hỏi mẫu."""
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
            q["question"] = (
                f"Kết quả của phép tính phù hợp với chủ đề '{topic}' (lớp {grade}) là gì?"
            )
            q["options"] = {"A": "10", "B": "12", "C": "14", "D": "16"}
            q["correct"] = "B"
        elif type == "fill_in_blank":
            q["sentence"] = f"Trong bài học '{topic}', chúng ta đã học về ____."
            q["correct_answer"] = "phép cộng"
        elif type == "true_false":
            q["statement"] = "2 + 2 = 5 là đúng."
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
                for key, val in q["options"].items():
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
    return (
        f"Định dạng '{format}' chưa được hỗ trợ. Tạm trả về dạng text:\n\n"
        f"{format_output(questions, 'text')}"
    )
