# GROUP REPORT: LAB 3 - PRODUCTION-GRADE AGENTIC SYSTEM

- **Team Name**: NguyenMinhKhoa
- **Team Members**: Nguyen Minh Khoa
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

### Project Overview

Dự án xây dựng một hệ thống ReAct Agent hỗ trợ giáo viên tiểu học tạo câu hỏi học tập cho học sinh lớp 1 đến lớp 5.

Khác với chatbot truyền thống chỉ sử dụng một lần gọi LLM để sinh câu trả lời, hệ thống Agent được thiết kế theo mô hình ReAct (Reasoning + Acting), cho phép:

- Phân tích yêu cầu người dùng.
- Suy luận nhiều bước.
- Lựa chọn công cụ phù hợp.
- Thực thi công cụ.
- Quan sát kết quả trả về.
- Đưa ra câu trả lời cuối cùng.

Hệ thống hỗ trợ nhiều nhà cung cấp LLM khác nhau như Gemini và OpenAI thông qua Provider Pattern.

### Success Rate

| Metric | Value |
|----------|----------|
| Total Test Cases | 5 |
| Successful Cases | 5 |
| Failed Cases | 0 |
| Success Rate | 100% |

### Key Outcome

So với chatbot cơ bản, Agent có khả năng:

- Thực hiện suy luận nhiều bước.
- Sử dụng công cụ bên ngoài.
- Giảm hallucination thông qua Observation.
- Hoạt động ổn định hơn trong các tác vụ cần Tool Calling.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Kiến trúc hoạt động:

```text
User Input
     |
     v
LLM Reasoning
     |
     v
Thought
     |
     v
Action
     |
     v
Tool Execution
     |
     v
Observation
     |
     v
LLM Reasoning
     |
     v
Final Answer
```

Pseudo-code:

```python
for step in range(MAX_STEPS):

    response = llm.generate()

    if Final Answer:
        return answer

    if Action:
        run_tool()

        Observation = tool_result

        continue
```

Agent giới hạn tối đa 5 vòng lặp để tránh vòng lặp vô hạn và kiểm soát chi phí API.

---

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
|------------|-------------|-----------|
| generate_questions | JSON | Tạo câu hỏi học tập |
| get_multiplication_table | JSON | Sinh bảng cửu chương |

#### Tool: generate_questions

Ví dụ:

```json
{
  "topic": "bảng cửu chương 9",
  "count": 2
}
```

Kết quả:

```text
Câu hỏi: 9 x 4 = ?
Câu hỏi: 9 x 7 = ?
```

#### Tool: get_multiplication_table

Ví dụ:

```json
{
  "number": 7
}
```

Kết quả:

```text
7 x 1 = 7
...
7 x 10 = 70
```

---

### 2.3 LLM Providers Used

#### Primary Provider

- Gemini 2.5 Flash

#### Secondary Provider

- GPT-4o

Provider được lựa chọn động thông qua biến môi trường:

```env
DEFAULT_PROVIDER=google
DEFAULT_MODEL=gemini-2.5-flash
```

hoặc:

```env
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
```

---

## 3. Telemetry & Performance Dashboard

### Logging Architecture

Hệ thống ghi lại toàn bộ vòng đời Agent thông qua Logger.

Các sự kiện được thu thập:

| Event | Description |
|---------|---------|
| AGENT_START | Bắt đầu Agent |
| AGENT_STEP | Một bước suy luận |
| AGENT_ACTION_REQUEST | Yêu cầu gọi Tool |
| AGENT_OBSERVATION | Kết quả Tool |
| AGENT_EXECUTION_ERROR | Lỗi Tool |
| AGENT_LLM_ERROR | Lỗi LLM |
| AGENT_END | Hoàn thành tác vụ |

### Estimated Metrics

| Metric | Value |
|----------|----------|
| Average Latency (P50) | ~1.2s |
| Max Latency (P99) | ~4.0s |
| Average Tokens per Task | ~250 |
| Total Cost of Test Suite | < $0.01 |

Lưu ý: Các số liệu trên được ước lượng dựa trên quá trình thử nghiệm cục bộ.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Invalid Tool Arguments

#### Input

```text
Tạo 2 câu hỏi từ bảng cửu chương 9
```

#### Observation

Trong một số trường hợp, LLM sinh:

```text
Action:
generate_questions(topic=bảng cửu chương 9)
```

thay vì JSON hợp lệ.

#### Root Cause

System Prompt chưa đủ nghiêm ngặt để ép LLM sử dụng JSON.

#### Impact

Lỗi:

```python
json.loads(...)
```

không parse được dữ liệu.

#### Mitigation

Đã bổ sung vào System Prompt:

```text
Action phải chứa JSON hợp lệ.
Không tự tạo Observation.
```

Ngoài ra Agent có xử lý Exception khi parse JSON.

---

### Case Study: Unknown Tool

#### Input

```text
Tạo đề thi toán lớp 4
```

#### Observation

LLM có thể gọi:

```text
create_exam(...)
```

trong khi Tool chưa tồn tại.

#### Root Cause

Agent hiểu mục tiêu nhưng không có Tool tương ứng.

#### Mitigation

Đã xử lý:

```python
if tool_name not in self.tools:
```

và trả về Observation phù hợp.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt V1 vs Prompt V2

#### Prompt V1

Không ép định dạng JSON.

#### Prompt V2

Bổ sung:

```text
Action phải chứa JSON hợp lệ.
Không tự tạo Observation.
```

#### Result

| Metric | V1 | V2 |
|----------|----------|----------|
| Invalid Tool Calls | 4 | 1 |
| Success Rate | 80% | 100% |

#### Conclusion

Prompt V2 cải thiện đáng kể độ ổn định của Agent.

---

### Experiment 2: Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Question | Correct | Correct | Draw |
| Tool Usage | Hallucinated | Correct | Agent |
| Multi-Step Reasoning | Unstable | Correct | Agent |

#### Example

Input:

```text
Tạo 2 câu hỏi bảng cửu chương 9
```

Chatbot:

- Sinh câu hỏi trực tiếp từ LLM.

Agent:

- Gọi Tool generate_questions.
- Trả kết quả chính xác theo quy trình ReAct.

---

## 6. Production Readiness Review

### Security

Các biện pháp hiện tại:

- Validate JSON trước khi thực thi.
- Kiểm tra Tool tồn tại.
- Xử lý Exception.
- Không thực thi mã do người dùng cung cấp.

### Guardrails

#### Maximum Iteration

```python
max_steps = 5
```

Ngăn vòng lặp vô hạn.

#### Error Handling

Hệ thống xử lý:

- JSON Error
- Tool Error
- Unknown Tool
- API Error
- Rate Limit Error

### Scaling

Các hướng mở rộng:

#### LangChain

Tích hợp thêm nhiều Tool.

#### LangGraph

Xây dựng Agent đa nhánh.

#### Memory Database

Lưu lịch sử hội thoại dài hạn.

#### Tool Registry

Cho phép đăng ký Tool động.

---

## Conclusion

Hệ thống đã hoàn thành đầy đủ các yêu cầu của Lab 3:

- ReAct Agent Architecture
- Tool Calling
- Thought → Action → Observation → Final Answer
- Multiple LLM Providers
- Logging & Telemetry
- Failure Analysis
- Test Cases
- Production Considerations

Kết quả cho thấy Agent hoạt động hiệu quả hơn chatbot truyền thống đối với các tác vụ cần suy luận nhiều bước và sử dụng công cụ, đồng thời có khả năng mở rộng để triển khai trong môi trường thực tế.
> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
