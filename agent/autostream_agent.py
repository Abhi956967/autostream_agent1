"""
agent/autostream_agent.py
Core conversational agent using Groq API with state management.
Handles: intent detection, RAG, lead qualification, tool execution.
"""

import os
import json
import re
from typing import TypedDict, Literal, Optional
from groq import Groq
from agent.rag_pipeline import KB_CONTEXT
from tools.lead_capture import mock_lead_capture


# ─────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    conversation_history: list[dict]
    intent: Literal["greeting", "product_inquiry", "high_intent", "unknown"]
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_platform: Optional[str]
    lead_captured: bool
    collecting_lead: bool


# ─────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are Aria, the friendly and knowledgeable sales assistant for AutoStream — an AI-powered video editing SaaS for content creators.

Your goals:
1. Greet users warmly and understand what they need.
2. Answer product, pricing, and policy questions accurately using ONLY the knowledge base below.
3. Detect when a user shows HIGH INTENT (ready to sign up / try the product).
4. Collect their Name, Email, and Creator Platform (e.g. YouTube, Instagram, TikTok) ONE AT A TIME — never ask for all three at once.
5. Confirm lead capture once all three details are collected.

=== INTENT CLASSIFICATION RULES ===
- GREETING: Simple hi, hello, hey, how are you
- PRODUCT_INQUIRY: Questions about features, pricing, plans, policies, comparisons
- HIGH_INTENT: User says things like "I want to sign up", "I'm ready", "let's do it", "I want to try", "sign me up", "how do I get started", "I'll take the Pro plan", "sounds good, I'm in"

=== LEAD COLLECTION RULES ===
- Only start collecting when intent is HIGH_INTENT.
- Ask for Name first, then Email, then Platform — one per message.
- If you already have Name but not Email, ask only for Email.
- If you have Name and Email but not Platform, ask only for Platform.
- Once you have all three, respond ONLY with this exact JSON block (no other text):

LEAD_READY::{{
  "name": "<name>",
  "email": "<email>",
  "platform": "<platform>"
}}

=== RESPONSE STYLE ===
- Be warm, concise, and professional.
- Never make up information not in the knowledge base.
- Keep responses under 120 words unless explaining plans in detail.
- Use emojis sparingly for a friendly tone.

{KB_CONTEXT}
"""


# ─────────────────────────────────────────────
# Agent Class
# ─────────────────────────────────────────────
class AutoStreamAgent:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast, capable Groq model
        self.state: AgentState = self._init_state()

    def _init_state(self) -> AgentState:
        return {
            "conversation_history": [],
            "intent": "unknown",
            "lead_name": None,
            "lead_email": None,
            "lead_platform": None,
            "lead_captured": False,
            "collecting_lead": False,
        }

    def reset(self):
        """Reset conversation for a new session."""
        self.state = self._init_state()

    def _classify_intent(self, user_message: str) -> str:
        """Quick rule-based intent pre-check before LLM."""
        msg = user_message.lower()
        high_intent_keywords = [
            "sign up", "sign me up", "i want to try", "i'm ready", "let's do it",
            "i'll take", "get started", "subscribe", "buy", "purchase", "i'm in",
            "sounds good", "let me join", "i want the", "ready to start"
        ]
        greeting_keywords = ["hi", "hello", "hey", "howdy", "good morning", "good evening", "what's up"]

        if any(k in msg for k in high_intent_keywords):
            return "high_intent"
        if msg.strip() in greeting_keywords or (len(msg.split()) <= 3 and any(k in msg for k in greeting_keywords)):
            return "greeting"
        return "product_inquiry"

    def _extract_lead_data(self, response_text: str) -> Optional[dict]:
        """Extract lead JSON from LLM response if present."""
        match = re.search(r"LEAD_READY::\{(.+?)\}", response_text, re.DOTALL)
        if match:
            try:
                return json.loads("{" + match.group(1) + "}")
            except json.JSONDecodeError:
                return None
        return None

    def _update_state_from_response(self, response: str, user_msg: str):
        """Update state based on LLM response and user message."""
        # Detect intent
        intent = self._classify_intent(user_msg)
        if intent == "high_intent" or self.state["collecting_lead"]:
            self.state["intent"] = "high_intent"
            self.state["collecting_lead"] = True
        else:
            self.state["intent"] = intent

    def chat(self, user_message: str) -> dict:
        """
        Process a user message and return agent response.

        Returns dict with:
            - response: str (agent's reply)
            - intent: str
            - lead_captured: bool
            - lead_data: dict | None
        """
        # Guard: already captured
        if self.state["lead_captured"]:
            return {
                "response": "I've already captured your details! 🎉 Our team will reach out to you soon. Is there anything else I can help you with?",
                "intent": self.state["intent"],
                "lead_captured": True,
                "lead_data": None,
            }

        # Update intent
        self._update_state_from_response("", user_message)

        # Append user message to history
        self.state["conversation_history"].append({
            "role": "user",
            "content": user_message
        })

        # Build messages for Groq
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.state["conversation_history"])

        # Call Groq LLM
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.4,
            max_tokens=512,
        )
        raw_response = completion.choices[0].message.content.strip()

        # Check if lead data is ready
        lead_data = self._extract_lead_data(raw_response)
        lead_captured = False

        if lead_data:
            # Execute lead capture tool
            capture_result = mock_lead_capture(
                name=lead_data["name"],
                email=lead_data["email"],
                platform=lead_data["platform"]
            )
            self.state["lead_captured"] = True
            self.state["lead_name"] = lead_data["name"]
            self.state["lead_email"] = lead_data["email"]
            self.state["lead_platform"] = lead_data["platform"]
            lead_captured = True

            # Clean response for display
            clean_response = re.sub(r"LEAD_READY::\{.+?\}", "", raw_response, flags=re.DOTALL).strip()
            if not clean_response:
                clean_response = (
                    f"✅ You're all set, **{lead_data['name']}**! I've captured your details and our team will reach out to {lead_data['email']} shortly. "
                    f"Welcome to AutoStream! 🎬"
                )
            final_response = clean_response
        else:
            final_response = raw_response

        # Append assistant response to history
        self.state["conversation_history"].append({
            "role": "assistant",
            "content": raw_response  # Store raw in history for context continuity
        })

        return {
            "response": final_response,
            "intent": self.state["intent"],
            "lead_captured": lead_captured,
            "lead_data": lead_data if lead_captured else None,
        }

    def get_state(self) -> AgentState:
        return self.state
