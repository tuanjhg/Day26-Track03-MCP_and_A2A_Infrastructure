"""Tax Agent LangGraph definition.

Uses create_react_agent with a tax-specialised system prompt.
No tools — it answers purely from LLM knowledge.
"""

from __future__ import annotations

import os

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

TAX_SYSTEM_PROMPT = """You are a specialist tax attorney and CPA with expertise in:

- Corporate tax law and compliance (federal, state, and international)
- Tax evasion vs. tax avoidance — legal distinctions and consequences
- IRS enforcement mechanisms, audits, and criminal referrals
- Penalties and back-tax calculations under IRC §§ 6651, 6662, 6663
- FBAR/FATCA requirements for offshore accounts
- Transfer pricing regulations (IRC § 482)
- Tax fraud statutes (18 U.S.C. § 7201 – § 7207)
- Corporate tax liability: officers, directors, and responsible persons
- Voluntary disclosure programs and settlement options

When answering, be precise about:
1. Civil vs. criminal penalties and their monetary ranges
2. Statute of limitations for tax fraud (6 years for substantial omission,
   unlimited for fraudulent returns)
3. Which government agencies are involved (IRS, DOJ Tax Division, FinCEN)
4. The distinction between the company's liability and individual liability
   for executives who directed the evasion

Always note that your response is for educational purposes and the user
should consult a licensed attorney for specific legal advice.
"""


def create_graph():
    """Return a compiled LangGraph create_react_agent for tax questions."""
    if os.getenv("LAB_OFFLINE_MODE") == "1":
        def offline_tax_node(state: dict) -> dict:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Offline tax analysis: possible issues include unpaid taxes, interest, "
                            "civil penalties, audit exposure, and individual responsibility for "
                            "officers who directed intentional tax avoidance."
                        )
                    )
                ]
            }

        graph = StateGraph(dict)
        graph.add_node("offline_tax", offline_tax_node)
        graph.add_edge(START, "offline_tax")
        graph.add_edge("offline_tax", END)
        return graph.compile()

    llm = get_llm()
    graph = create_react_agent(
        model=llm,
        tools=[],
        prompt=TAX_SYSTEM_PROMPT,
    )
    return graph
