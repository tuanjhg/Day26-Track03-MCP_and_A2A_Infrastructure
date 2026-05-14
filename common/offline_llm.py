"""Small offline LLM stub for lab verification without API credits.

This is intentionally simple: it is only enabled when LAB_OFFLINE_MODE=1
and lets the exercise scripts prove their tool and graph wiring locally.
"""

from langchain_core.messages import AIMessage, ToolMessage


class OfflineLLM:
    """Deterministic local stand-in for the exercise scripts."""

    def __init__(self, tools=None):
        self.tools = tools or []

    def bind_tools(self, tools):
        return OfflineLLM(tools)

    def invoke(self, messages):
        return AIMessage(content=self._answer(messages))

    async def ainvoke(self, messages):
        tool_names = {tool.name for tool in self.tools}
        prompt = self._last_text(messages).lower()

        if "check_statute_of_limitations" in tool_names and not self._has_tool_result(messages):
            if "thời hiệu" in prompt or "hợp đồng" in prompt or "contract" in prompt:
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "check_statute_of_limitations",
                            "args": {"case_type": "contract"},
                            "id": "offline-statute-call",
                        }
                    ],
                )

        return AIMessage(content=self._answer(messages))

    def _answer(self, messages):
        prompt = self._last_text(messages).lower()
        tool_result = self._tool_result(messages)
        if tool_result:
            return f"Theo kết quả tra cứu, thời hiệu phù hợp là: {tool_result}"

        if "needs_tax" in prompt and "needs_compliance" in prompt:
            needs_tax = any(word in prompt for word in ["tax", "irs", "thuế"])
            needs_compliance = any(
                word in prompt
                for word in ["compliance", "regulatory", "regulation", "sec", "sox", "tuân thủ"]
            )
            return (
                f'{{"needs_tax": {str(needs_tax).lower()}, '
                f'"needs_compliance": {str(needs_compliance).lower()}}}'
            )

        if "## legal analysis" in prompt or "phân tích pháp lý" in prompt:
            return (
                "Báo cáo tổng hợp offline:\n"
                "1. Pháp lý: cần xác định vi phạm hợp đồng, thiệt hại, nghĩa vụ khắc phục và "
                "khả năng bồi thường.\n"
                "2. Thuế: cần rà soát nghĩa vụ kê khai, tiền thuế thiếu, lãi, phạt dân sự và "
                "nguy cơ điều tra nếu có yếu tố cố ý.\n"
                "3. Tuân thủ: cần kiểm tra nghĩa vụ báo cáo, kiểm soát nội bộ, governance và "
                "biện pháp remediation.\n"
                "Nội dung này phục vụ mục đích học tập; trường hợp thực tế cần hỏi luật sư được cấp phép."
            )

        if "gdpr" in prompt or "privacy" in prompt or "dữ liệu" in prompt or "data" in prompt:
            return (
                "Vụ rò rỉ dữ liệu có thể kích hoạt nghĩa vụ thông báo sự cố, đánh giá tác động "
                "bảo vệ dữ liệu, biện pháp khắc phục cho khách hàng, và rủi ro phạt theo GDPR/CCPA "
                "nếu dữ liệu cá nhân được xử lý hoặc chuyển giao trái quy định."
            )

        if "thuế" in prompt or "tax" in prompt or "irs" in prompt:
            return (
                "Khía cạnh thuế cần xem xét gồm chi phí khắc phục, khoản phạt có được khấu trừ hay "
                "không, nghĩa vụ báo cáo, và rủi ro điều tra nếu sự cố liên quan che giấu doanh thu."
            )

        if "compliance" in prompt or "tuân thủ" in prompt or "sec" in prompt:
            return (
                "Doanh nghiệp cần rà soát chương trình tuân thủ, lưu vết xử lý sự cố, thông báo cơ "
                "quan quản lý khi luật yêu cầu, và cập nhật kiểm soát nội bộ để giảm trách nhiệm."
            )

        return (
            "Phân tích pháp lý tổng quát: cần xác định nghĩa vụ theo hợp đồng, luật áp dụng, "
            "thiệt hại thực tế, nghĩa vụ thông báo, và các biện pháp giảm thiểu rủi ro."
        )

    @staticmethod
    def _last_text(messages):
        for message in reversed(messages):
            content = getattr(message, "content", None)
            if content:
                return content
        return ""

    @staticmethod
    def _has_tool_result(messages):
        return any(isinstance(message, ToolMessage) for message in messages)

    @staticmethod
    def _tool_result(messages):
        for message in reversed(messages):
            if isinstance(message, ToolMessage):
                return message.content
        return ""
