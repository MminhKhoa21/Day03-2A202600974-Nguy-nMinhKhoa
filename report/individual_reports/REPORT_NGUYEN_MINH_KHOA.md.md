# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Minh Khoa
- **Student ID**: 2A202600974
- **Date**: 2026-06-01

---

# I. Technical Contribution (15 Points)

## Overview

Trong Lab 3, tôi chịu trách nhiệm xây dựng và hoàn thiện hệ thống ReAct Agent hỗ trợ giáo viên tiểu học tạo câu hỏi học tập.

Các công việc chính bao gồm:

- Thiết kế vòng lặp ReAct (Thought → Action → Observation → Final Answer).
- Xây dựng Tool Registry.
- Xây dựng Tool tạo câu hỏi học tập.
- Xây dựng Tool sinh bảng cửu chương.
- Tích hợp Gemini/OpenAI Provider.
- Xây dựng hệ thống Logging và Telemetry.
- Xử lý lỗi Tool Calling và JSON Parsing.

---

## Modules Implemented

### Agent Core

```text
src/agent/agent.py
```

Chức năng:

- ReAct Loop
- Tool Calling
- Observation Handling
- Final Answer Extraction
- Error Handling

---

### Tool Definitions

```text
src/tools/tools.py
```

Bao gồm:

- generate_questions()
- get_multiplication_table()

---

### Provider Layer

```text
src/core/gemini_provider.py
src/core/openai_provider.py
```

Chức năng:

- Kết nối Gemini API
- Kết nối OpenAI API

---

### Logging System

```text
src/telemetry/logger.py
```

Ghi lại:

- AGENT_START
- AGENT_STEP
- AGENT_ACTION_REQUEST
- AGENT_OBSERVATION
- AGENT_EXECUTION_ERROR
- AGENT_END

---

## Code Highlights

### ReAct Loop

```python
for step in range(self.max_steps):
```

Đây là vòng lặp chính cho phép Agent suy luận nhiều bước.

---

### Tool Execution

```python
func = self.tools[tool_name]["func"]

result = func(**args)
```

Cho phép Agent thực thi Tool động dựa trên Action do LLM sinh ra.

---

### Observation Injection

```python
conversation += (
    content_clean.strip()
    + f"\nObservation: {observation}\n"
)
```

Observation được đưa ngược lại vào context để Agent tiếp tục suy luận.

---

## Documentation

Luồng hoạt động của Agent:

```text
User Input
     ↓
Thought
     ↓
Action
     ↓
Tool Execution
     ↓
Observation
     ↓
Thought
     ↓
Final Answer
```

Hệ thống được triển khai theo mô hình ReAct nhằm tăng khả năng reasoning và giảm hallucination.

---

# II. Debugging Case Study (10 Points)

## Problem Description

Trong quá trình thử nghiệm, Agent thường sinh Action không đúng định dạng JSON.

Ví dụ:

```text
Action:
generate_questions(topic=bảng cửu chương 9)
```

thay vì:

```json
{
  "topic": "bảng cửu chương 9",
  "count": 2
}
```

Điều này gây lỗi khi thực hiện:

```python
json.loads(args_str)
```

---

## Log Source

Ví dụ log:

```text
AGENT_ACTION_REQUEST

tool=generate_questions

args_str=topic=bảng cửu chương 9
```

Tiếp theo:

```text
AGENT_EXECUTION_ERROR

JSONDecodeError
```

---

## Diagnosis

Nguyên nhân chính đến từ Prompt.

LLM hiểu cần gọi Tool nhưng không hiểu rằng tham số bắt buộc phải là JSON hợp lệ.

Điều này không phải lỗi của Tool mà là lỗi ở Prompt Engineering.

---

## Solution

Tôi cập nhật System Prompt:

```text
Action phải chứa JSON hợp lệ.

Không tự tạo Observation.
```

Sau khi cập nhật Prompt:

```text
Action:
generate_questions({
  "topic":"bảng cửu chương 9",
  "count":2
})
```

Tỷ lệ lỗi Tool Calling giảm đáng kể.

---

# III. Personal Insights: Chatbot vs ReAct (10 Points)

## 1. Reasoning

Khối Thought giúp Agent phân tích bài toán trước khi hành động.

Ví dụ:

```text
User:
Tạo 2 câu hỏi bảng cửu chương 9
```

Chatbot:

- Trả lời trực tiếp bằng kiến thức mô hình.

Agent:

```text
Thought:
Cần tạo câu hỏi.

Action:
generate_questions(...)
```

Sau đó mới trả lời.

Điều này giúp Agent đưa ra kết quả có cấu trúc và đáng tin cậy hơn.

---

## 2. Reliability

Có một số trường hợp Agent hoạt động kém hơn Chatbot.

Ví dụ:

```text
Hôm nay là ngày mấy?
```

Chatbot:

- Trả lời ngay.

Agent:

- Phân tích.
- Kiểm tra Tool.
- Tăng độ trễ không cần thiết.

Đối với các câu hỏi đơn giản, Chatbot hiệu quả hơn Agent.

---

## 3. Observation

Observation là thành phần quan trọng nhất của ReAct.

Ví dụ:

```text
Action:
get_multiplication_table(7)
```

Tool trả về:

```text
7 x 1 = 7
...
7 x 10 = 70
```

Observation được đưa lại cho LLM:

```text
Observation:
7 x 1 = 7
...
```

Từ đó Agent có thể tiếp tục suy luận thay vì dựa hoàn toàn vào kiến thức nội tại.

Observation giúp Agent giảm hallucination và tăng khả năng sử dụng công cụ.

---

# IV. Future Improvements (5 Points)

## Scalability

Khi số lượng Tool tăng lên, hệ thống có thể mở rộng bằng:

- LangChain Tool Router
- LangGraph Workflow
- Tool Registry động

Ngoài ra có thể sử dụng hàng đợi bất đồng bộ (Async Queue) cho các Tool mất nhiều thời gian.

---

## Safety

Một số cải tiến an toàn:

- Validate Tool Arguments.
- Prompt Injection Detection.
- Tool Permission Layer.
- Supervisor Agent kiểm tra Action trước khi thực thi.

---

## Performance

Để tối ưu hiệu năng:

- Sử dụng Vector Database để tìm Tool phù hợp.
- Cache kết quả Tool.
- Streaming Response.
- Context Compression.

---

# Conclusion

Thông qua Lab 3, tôi đã hiểu rõ sự khác biệt giữa Chatbot truyền thống và ReAct Agent.

Chatbot phù hợp với các câu hỏi đơn giản và phản hồi nhanh.

Trong khi đó, ReAct Agent phù hợp với các tác vụ cần suy luận nhiều bước, sử dụng công cụ và tương tác với môi trường.

Việc triển khai ReAct Agent giúp tôi hiểu rõ hơn về kiến trúc Agentic AI, Tool Calling, Prompt Engineering, Logging và các yêu cầu cần thiết để xây dựng hệ thống AI có khả năng mở rộng trong môi trường thực tế.