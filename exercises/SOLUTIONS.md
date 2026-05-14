# Solutions

## Exercise 2: Tools and Knowledge Base

### 2.1 Add Labor Law Knowledge

Added a `labor_law` entry to `LEGAL_KNOWLEDGE` with Vietnamese and English keywords:

```python
{
    "id": "labor_law",
    "keywords": ["lao động", "sa thải", "hợp đồng lao động", "labor", "termination"],
    "text": (
        "Theo Bộ luật Lao động Việt Nam 2019, người sử dụng lao động có thể "
        "đơn phương chấm dứt hợp đồng ..."
    ),
}
```

The original contract/UCC entry was also expanded with Vietnamese keywords such as `hợp đồng`, `vi phạm hợp đồng`, and `thời hiệu`.

### 2.2 Add Statute of Limitations Tool

Implemented:

```python
@tool
def check_statute_of_limitations(case_type: str) -> str:
    limits = {
        "contract": "4 năm (UCC § 2-725)",
        "tort": "2-3 năm tùy bang",
        "property": "5 năm",
    }
    return limits.get(case_type.lower(), "Không xác định")
```

Then added it to:

```python
tools = [search_legal_knowledge, check_statute_of_limitations]
```

The tool loop now dispatches by tool name through `tool_map`, so new tools can be added without duplicating conditional branches.

## Exercise 4: Multi-Agent Privacy Agent

### 4.1 Add Privacy Agent

Implemented `privacy_agent(state)` using the same pattern as `tax_agent` and `compliance_agent`. The prompt focuses on:

- GDPR
- data protection
- privacy rights
- data breach

It returns:

```python
{"privacy_analysis": response.content}
```

### 4.2 Add Conditional Routing

Routing now sends work to agents based on keyword groups:

```python
if any(kw in question_lower for kw in ["tax", "irs", "thuế"]):
    tasks.append(Send("tax_agent", state))

if any(kw in question_lower for kw in ["compliance", "sec", "regulation", "tuân thủ"]):
    tasks.append(Send("compliance_agent", state))

if any(kw in question_lower for kw in ["data", "privacy", "gdpr", "dữ liệu"]):
    tasks.append(Send("privacy_agent", state))
```

The graph registers `privacy_agent` as a node and adds the edge:

```python
graph.add_edge("privacy_agent", "aggregate_results")
```

### Aggregation

`aggregate_results` now includes `privacy_analysis` when present:

```python
if state.get("privacy_analysis"):
    sections.append(f"PHÂN TÍCH PRIVACY/GDPR:\n{state['privacy_analysis']}")
```

## Review Questions

### 1. Khi nào dùng single agent thay vì multi-agent?

Dùng single agent khi bài toán hẹp, ít domain chuyên môn, không cần song song hóa, và chi phí vận hành cần thấp. Dùng multi-agent khi câu hỏi cần nhiều chuyên gia, có thể phân nhánh độc lập, hoặc cần tách trách nhiệm để dễ mở rộng.

### 2. A2A khác gì REST/gRPC thường?

A2A chuẩn hóa cách agent công bố năng lực, nhận task, trả artifact, quản lý trạng thái task, và truyền metadata như `trace_id`/`context_id`. REST/gRPC chỉ là cơ chế transport/API chung, còn A2A thêm ngữ nghĩa dành riêng cho agent collaboration.

### 3. Làm sao tránh infinite delegation loop?

Dùng `delegation_depth`, giới hạn `MAX_DELEGATION_DEPTH`, timeout, retry có giới hạn, và có thể thêm visited-agent tracking để một request không quay vòng giữa cùng các agents.

### 4. Tại sao cần Registry?

Registry giúp dynamic discovery: agent không cần hardcode URL của nhau. Khi thay endpoint, scale service, hoặc thêm agent mới, các agent khác vẫn discover theo task capability như `legal_question`, `tax_question`, `compliance_question`.
