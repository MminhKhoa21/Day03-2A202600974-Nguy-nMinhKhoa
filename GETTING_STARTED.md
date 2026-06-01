# 🚀 ReAct Agent for Elementary School Question Generation

## Project Overview

This project implements a **ReAct (Reasoning + Acting) Agent** that helps teachers create questions for elementary school students (grades 1-5) in Vietnamese. The agent uses **multi-step reasoning** with structured tools for:

- 📚 Getting curriculum topics by subject and grade
- ❓ Generating questions with customizable difficulty and format
- ✅ Evaluating student answers
- 💡 Providing teaching tips

## ✨ Key Features

- **ReAct Loop Implementation**: Thought → Action → Observation pattern
- **Multi-Provider Support**: OpenAI, Google Gemini, Local Models (via llama-cpp)
- **Industry-Grade Telemetry**: JSON-formatted event logging for analysis
- **Vietnamese Language Support**: Native support for Vietnamese prompts and responses
- **Tool Integration**: Flexible tool framework for extending functionality
- **Error Handling**: Robust fallbacks and error logging

## 📋 Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py              # ReActAgent implementation
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm_provider.py        # Base LLM provider interface
│   │   ├── openai_provider.py     # OpenAI implementation
│   │   ├── gemini_provider.py     # Google Gemini implementation
│   │   └── local_provider.py      # Local model support (Phi-3)
│   └── telemetry/
│       ├── __init__.py
│       ├── logger.py              # Structured JSON logging
│       └── metrics.py             # Performance metrics
├── agent.py                        # Wrapper for ReActAgent imports
├── tools.py                        # Tools for the agent (get_topics, generate_question, etc.)
├── chatbot.py                      # Interactive CLI chatbot
├── requirements.txt
├── .env                            # Configuration (API keys, model settings)
├── test_cases.md                   # Test cases and results
├── trace.md                        # Detailed execution traces
└── logs/                           # JSON event logs (auto-created)
```

## 🔧 Setup & Installation

### 1. Clone and Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env`:

```env
# For Google Gemini
GEMINI_API_KEY='your-gemini-api-key'
DEFAULT_PROVIDER=google
DEFAULT_MODEL=gemini-1.5-flash

# OR for OpenAI
OPENAI_API_KEY='your-openai-key'
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o

# OR for Local Model (Phi-3)
DEFAULT_PROVIDER=local
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
```

### 3. Run the Chatbot

```bash
python chatbot.py
```

**Example Interactions:**

```
🤖 CHATBOT TẠO CÂU HỎI TIỂU HỌC (ReAct Agent)
VD: 'Tạo 2 câu hỏi trắc nghiệm toán lớp 2 về phép cộng'
Hoặc: 'Lấy danh sách chủ đề tiếng việt lớp 3'

Bạn: Tạo một câu hỏi trắc nghiệm toán lớp 1 về phép cộng
Agent đang suy nghĩ...
📚 Agent: Câu hỏi trắc nghiệm: 5 + 3 = ? A. 7 B. 8 C. 9
```

## 🛠️ Available Tools

### 1. `get_topics(subject: str, grade: str) -> str`
Get available topics for a subject and grade.

**Supported subjects:** toán, tiếng việt, khoa học  
**Supported grades:** lớp 1-5

**Example:**
```
User: "Lấy danh sách chủ đề tiếng việt lớp 3"
→ Action: get_topics(tiếng việt, lớp 3)
→ Topics: So sánh, Nhân hóa, Chính tả phân biệt l/n
```

### 2. `generate_question(topic: str, difficulty: str, question_type: str) -> str`
Generate a question based on topic, difficulty level, and format.

**Difficulties:** dễ (easy), trung bình (medium), khó (hard)  
**Types:** trắc nghiệm (multiple choice), tự luận (essay)

**Example:**
```
Action: generate_question(phép cộng trong phạm vi 10, dễ, trắc nghiệm)
→ Result: 5 + 3 = ? A. 7 B. 8 C. 9
```

### 3. `evaluate_answer(question: str, student_answer: str, expected_answer: str) -> str`
Evaluate a student's answer.

**Example:**
```
Action: evaluate_answer(2+3=?, 6, 5)
→ Result: Sai. Đáp án đúng là: 5
```

### 4. `get_teaching_tip(topic: str) -> str`
Get teaching strategies for a specific topic.

**Example:**
```
Action: get_teaching_tip(phép cộng)
→ Result: Dùng que tính hoặc ngón tay để minh họa phép cộng.
```

## 📊 Performance & Metrics

The agent includes comprehensive telemetry:

```json
{
  "timestamp": "2026-06-01T09:34:24.988200",
  "event": "AGENT_START",
  "data": {"input": "...", "model": "gemini-1.5-flash"}
}

{
  "timestamp": "2026-06-01T09:34:24.991700",
  "event": "AGENT_END",
  "data": {"steps": 3, "final_answer": "..."}
}
```

### Key Metrics:
- **Latency:** ~50-100ms per step
- **Token Efficiency:** ~250 prompt tokens, ~150 completion tokens per query
- **Success Rate:** 100% (in test cases)
- **Loop Count:** Typically 1-3 steps

## 📝 System Prompt

The agent uses this Vietnamese system prompt:

```
Bạn là trợ lý AI chuyên tạo câu hỏi cho học sinh tiểu học (lớp 1-5).

Hãy luôn tuân theo khuôn mẫu:
Thought: (suy nghĩ của bạn)
Action: tên_công_cụ(đối số)
Observation: kết quả trả về từ công cụ
... (lặp lại nếu cần)
Final Answer: câu trả lời cuối cùng cho người dùng
```

## 🧪 Testing

### Run All Test Cases
```bash
python test_agent.py
```

### Expected Test Results
- ✅ Test 1: Multiple choice question generation (2 steps)
- ✅ Test 2: Multi-step reasoning with topic selection (3 steps)
- ✅ Test 3: Answer evaluation with multiple arguments (2 steps)
- ✅ Test 4: Teaching tips retrieval (1 step)
- ✅ Test 5: Complex scenarios with multiple tools

### Check Logs
```bash
# View today's logs in JSON format
cat logs/2026-06-01.log | python -m json.tool
```

## 🔍 Troubleshooting

### ImportError: No module named 'src'
```bash
# Make sure you're running from the project root
cd Day-3-Lab-Chatbot-vs-react-agent-main
python chatbot.py
```

### API Key Issues
```bash
# Check .env file exists and has correct keys
cat .env | grep API_KEY
```

### Model Not Found (Local Provider)
```bash
# Download from Hugging Face
mkdir -p models
# Download Phi-3-mini-4k-instruct-q4.gguf and place in models/
```

## 📚 Advanced Features

### Custom Tools
Add new tools by modifying `tools.py`:

```python
TOOLS = [
    {
        "name": "your_tool_name",
        "description": "Tool description for the agent",
        "func": your_function
    },
    # ... existing tools
]
```

### Custom LLM Providers
Extend `LLMProvider` base class to add new providers:

```python
from src.core.llm_provider import LLMProvider

class MyProvider(LLMProvider):
    def generate(self, prompt, system_prompt=None):
        # Implementation
        pass
    
    def stream(self, prompt, system_prompt=None):
        # Implementation
        pass
```

## 📖 Documentation

- **test_cases.md**: Comprehensive test cases and results
- **trace.md**: Detailed execution traces with JSON events
- **EVALUATION.md**: Metrics and evaluation criteria
- **INSTRUCTOR_GUIDE.md**: Guide for instructors
- **SCORING.md**: Grading rubric

## 🎯 Use Cases

1. **Question Generation**: Create questions automatically for different topics/levels
2. **Answer Evaluation**: Check student answers with explanations
3. **Teaching Support**: Get tips and strategies for each topic
4. **Curriculum Planning**: Explore available topics per grade level
5. **Adaptive Learning**: Generate questions matching student proficiency

## 🔗 Architecture

```
User Input
    ↓
Chatbot.py (CLI Interface)
    ↓
ReActAgent (Reasoning Loop)
    ├→ LLM Provider (Gemini/OpenAI/Local)
    ├→ Tool Execution (get_topics, generate_question, etc.)
    └→ Telemetry Logger (JSON Events)
    ↓
Final Answer
```

## 📄 License

This project is part of the Agentic AI course.

## 🤝 Contributing

To extend the agent:
1. Add new tools to `tools.py`
2. Update system prompt in `src/agent/agent.py` if needed
3. Add test cases to `test_cases.md`
4. Run tests and verify performance

---

**Happy Teaching! 🎓**
