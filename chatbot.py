# main/chatbot.py
import os
import sys
from dotenv import load_dotenv

# Thêm đường dẫn gốc vào sys.path để import được src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent, MaxStepsExceededError
from src.tools.tools import TOOLS

# ------------------------------------------------------------
# FACTORY: Tạo provider dựa trên biến môi trường
# ------------------------------------------------------------
def build_provider():
    default_provider = os.getenv("DEFAULT_PROVIDER", "google").strip().lower()
    model_name = os.getenv("DEFAULT_MODEL")

    if default_provider == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Thiếu GEMINI_API_KEY trong file .env")
        return GeminiProvider(model_name=model_name or "gemini-1.5-flash", api_key=api_key)

    if default_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Thiếu OPENAI_API_KEY trong file .env")
        return OpenAIProvider(model_name=model_name or "gpt-4o", api_key=api_key)

    if default_provider == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH")
        if not model_path:
            raise ValueError("Thiếu LOCAL_MODEL_PATH trong file .env")
        try:
            from src.core.local_provider import LocalProvider
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Chưa cài đặt llama_cpp. Hãy cài đặt hoặc dùng DEFAULT_PROVIDER=openai|google"
            ) from exc
        return LocalProvider(model_path=model_path)

    raise ValueError(f"Không xác định được nhà cung cấp: {default_provider}")

# ------------------------------------------------------------
# Các chế độ của chatbot
# ------------------------------------------------------------
def run_chatbot(prompt: str) -> str:
    """Chat thông thường (không qua agent)"""
    provider = build_provider()
    result = provider.generate(prompt)
    return result.get("content", "")

def chat_mode():
    """Chế độ trò chuyện tương tác (dùng LLM trực tiếp)"""
    print("\n" + "="*60)
    print("🤖 CHATBOT TIẾNG VIỆT".center(60))
    print("="*60)
    print("\nChào bạn! Tôi là trợ lý AI. Hãy nhập câu hỏi của bạn bên dưới.")
    print("Nhập 'exit' hoặc 'thoát' để kết thúc.\n")
    
    while True:
        try:
            user_input = input("Bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'thoát', 'quit']:
                print("\nTạm biệt! 👋")
                break
            
            print("\nChatbot đang suy nghĩ...")
            print("-" * 50)
            response = run_chatbot(user_input)
            print(f"Chatbot: {response}")
            print("-" * 50 + "\n")
        except KeyboardInterrupt:
            print("\n\nTạm biệt! 👋")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {e}\n")

def teacher_mode():
    """Chế độ hỗ trợ giáo viên, sử dụng ReActAgent"""
    print("\n" + "="*60)
    print("🧑‍🏫 CHẾ ĐỘ HỖ TRỢ GIÁO VIÊN TIỂU HỌC".center(60))
    print("="*60)
    print("\nTôi có thể giúp bạn tạo câu hỏi trắc nghiệm, điền từ, đúng/sai...")
    print("Ví dụ: 'Tạo 3 câu hỏi trắc nghiệm về Bảng nhân 3 cho lớp 2, mức dễ'")
    print("Nhập 'exit' hoặc 'thoát' để quay lại menu chính.\n")

    provider = build_provider()
    agent = ReActAgent(llm=provider, tools=TOOLS, max_steps=5)

    while True:
        try:
            user_input = input("👩‍🏫 Bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'thoát', 'quit']:
                print("\nĐã thoát chế độ giáo viên.\n")
                break

            print("\n🤔 Agent đang suy nghĩ...")
            print("-" * 50)
            final_answer = agent.run(user_input)
            print(f"📋 Kết quả:\n{final_answer}")
            print("-" * 50 + "\n")
        except MaxStepsExceededError:
            print("\n⚠️ Agent đã đạt số bước tối đa mà không hoàn thành. Vui lòng thử lại với yêu cầu khác.\n")
        except KeyboardInterrupt:
            print("\n\nĐã thoát chế độ giáo viên.")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {e}\n")

def run_sample_cases():
    """Chạy các trường hợp mẫu (chatbot thông thường)"""
    vi_examples = [
        {
            "title": "Tính giá sản phẩm sau giảm giá và thuế",
            "prompt": (
                "Một sản phẩm có giá 150 USD. Sản phẩm được giảm giá 15% trước khi tính thuế, "
                "sau đó áp dụng thuế 8.5%, và cộng thêm phí vận chuyển 12 USD. "
                "Hãy tính tổng số tiền cần thanh toán và giải thích từng bước."
            ),
        },
        {
            "title": "Kế hoạch marketing 3 bước",
            "prompt": (
                "Hãy xây dựng một kế hoạch marketing gồm 3 bước cho một startup công nghệ: "
                "nghiên cứu thị trường, tạo nội dung và theo dõi hiệu quả. "
                "Giải thích cần làm gì ở mỗi bước và thời gian thực hiện dự kiến."
            ),
        },
        {
            "title": "Lập lịch họp",
            "prompt": (
                "Hôm nay là ngày 01/06/2026. Bạn cần gặp 3 đồng nghiệp, "
                "mỗi cuộc họp cách nhau 2 ngày và phải hoàn thành trong vòng 2 tuần. "
                "Hỏi sẽ có tổng cộng bao nhiêu cuộc họp và ngày diễn ra cuộc họp cuối cùng là ngày nào?"
            ),
        },
    ]

    for example in vi_examples:
        print(f"\n=== Ví dụ: {example['title']} ===")
        print(f"Câu hỏi: {example['prompt']}")
        print("Kết quả:")
        try:
            output = run_chatbot(example["prompt"])
            print(output)
        except Exception as exc:
            print(f"Lỗi: {exc}")

# ------------------------------------------------------------
# MENU CHÍNH
# ------------------------------------------------------------
def main():
    load_dotenv()
    print("\n🚀 CHATBOT BASELINE + AGENT GIÁO VIÊN")
    print(f"📌 Nhà cung cấp mặc định: {os.getenv('DEFAULT_PROVIDER', 'google')}")

    while True:
        print("\n" + "="*50)
        print("MENU CHÍNH".center(50))
        print("="*50)
        print("1. 💬 Chế độ trò chuyện (Chat Mode)")
        print("2. 🧪 Chạy các trường hợp mẫu (Sample Cases)")
        print("3. 🧑‍🏫 Hỗ trợ giáo viên (Teacher Mode)")
        print("4. ❌ Thoát")
        print("-"*50)

        choice = input("👉 Lựa chọn của bạn (1/2/3/4): ").strip()

        if choice == "1":
            chat_mode()
        elif choice == "2":
            run_sample_cases()
            input("\nNhấn Enter để quay lại menu...")
        elif choice == "3":
            teacher_mode()
        elif choice == "4":
            print("\n👋 Cảm ơn bạn đã sử dụng! Hẹn gặp lại!")
            break
        else:
            print("\n❌ Lựa chọn không hợp lệ. Vui lòng chọn 1-4.")

if __name__ == "__main__":
    main()