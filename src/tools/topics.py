from typing import List

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
    return TOPICS_DB.get(int(grade), [])
