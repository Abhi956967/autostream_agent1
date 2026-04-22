"""
agent/rag_pipeline.py
Simple RAG pipeline using local JSON knowledge base + Groq embeddings/LLM.
No vector DB required — uses keyword + semantic matching for small KB.
"""

import json
import os
from pathlib import Path


def load_knowledge_base() -> dict:
    """Load the AutoStream knowledge base from JSON."""
    kb_path = Path(__file__).parent.parent / "knowledge_base" / "autostream_kb.json"
    with open(kb_path, "r") as f:
        return json.load(f)


def build_kb_context(kb: dict) -> str:
    """
    Convert the knowledge base dict into a clean text context
    that can be injected into the LLM system prompt.
    """
    ctx = []
    ctx.append(f"=== AUTOSTREAM KNOWLEDGE BASE ===\n")
    ctx.append(f"Company: {kb['company']}")
    ctx.append(f"Description: {kb['product_description']}\n")

    ctx.append("--- PRICING PLANS ---")
    for plan_key, plan in kb["plans"].items():
        ctx.append(f"\n{plan['name']} — {plan['price']}")
        ctx.append(f"  Ideal for: {plan['ideal_for']}")
        ctx.append(f"  Features:")
        for feat in plan["features"]:
            ctx.append(f"    • {feat}")

    ctx.append("\n--- POLICIES ---")
    for policy_name, policy_text in kb["policies"].items():
        ctx.append(f"  {policy_name.replace('_', ' ').title()}: {policy_text}")

    ctx.append("\n--- FAQs ---")
    for faq in kb["faqs"]:
        ctx.append(f"  Q: {faq['question']}")
        ctx.append(f"  A: {faq['answer']}\n")

    return "\n".join(ctx)


# Pre-load once at import time
_KB = load_knowledge_base()
KB_CONTEXT = build_kb_context(_KB)
