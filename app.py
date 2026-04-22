"""
app.py — AutoStream Agent | Streamlit Web UI
Run with: streamlit run app.py
"""

import streamlit as st
import os
import time
from agent.autostream_agent import AutoStreamAgent

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AutoStream — AI Sales Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root theme */
:root {
    --bg-dark: #0a0a0f;
    --bg-card: #13131a;
    --bg-input: #1c1c26;
    --accent: #7c5cfc;
    --accent-glow: rgba(124, 92, 252, 0.3);
    --accent2: #00e5a0;
    --text-primary: #f0f0ff;
    --text-secondary: #8888aa;
    --border: rgba(124, 92, 252, 0.2);
    --user-bubble: #1e1840;
    --agent-bubble: #13131a;
    --success: #00e5a0;
    --warning: #ffc107;
}

/* Global */
.stApp {
    background-color: var(--bg-dark) !important;
    font-family: 'DM Sans', sans-serif;
}
.stApp * { color: var(--text-primary); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Space Mono', monospace;
    color: var(--accent) !important;
}

/* Header */
.header-block {
    background: linear-gradient(135deg, #1a1040 0%, #0a0a0f 60%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.header-block::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    border-radius: 50%;
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #fff 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 4px 0;
}
.header-subtitle {
    color: var(--text-secondary) !important;
    font-size: 0.9rem;
    margin: 0;
}

/* Chat container */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 16px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 16px;
    scroll-behavior: smooth;
}

/* Chat bubbles */
.msg-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    align-items: flex-start;
}
.msg-row.user { flex-direction: row-reverse; }
.avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.avatar-agent { background: linear-gradient(135deg, var(--accent), #a78bfa); }
.avatar-user  { background: linear-gradient(135deg, #334155, #475569); }
.bubble {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 0.92rem;
    line-height: 1.6;
}
.bubble-agent {
    background: var(--agent-bubble);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
}
.bubble-user {
    background: var(--user-bubble);
    border: 1px solid rgba(124,92,252,0.3);
    border-top-right-radius: 4px;
}
.bubble-time {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Intent badge */
.intent-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    margin-top: 6px;
}
.badge-greeting       { background: #1a3a2a; color: var(--success); border: 1px solid var(--success); }
.badge-product_inquiry { background: #1a2a3a; color: #60a5fa; border: 1px solid #60a5fa; }
.badge-high_intent    { background: #3a1a2a; color: #f472b6; border: 1px solid #f472b6; }
.badge-unknown        { background: #2a2a2a; color: #888; border: 1px solid #555; }

/* Lead capture success card */
.lead-success {
    background: linear-gradient(135deg, #0a2a1a, #051a0f);
    border: 1px solid var(--success);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}
.lead-success h3 { color: var(--success) !important; font-family: 'Space Mono', monospace; }

/* Status panel */
.status-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}
.status-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 0.85rem;
}
.status-key { color: var(--text-secondary); }
.status-val { color: var(--text-primary); font-weight: 500; }
.status-val.filled { color: var(--success); }
.status-val.missing { color: #666; }

/* Input overrides */
.stTextInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #a78bfa) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
}
.stButton[data-testid] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
}

/* Suggested prompts */
.prompt-chip {
    display: inline-block;
    padding: 6px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 20px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin: 4px;
    cursor: pointer;
    transition: all 0.2s;
}
.prompt-chip:hover {
    border-color: var(--accent);
    color: var(--accent);
}

/* Section label */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Scrollbar */
.chat-container::-webkit-scrollbar { width: 4px; }
.chat-container::-webkit-scrollbar-track { background: transparent; }
.chat-container::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* Divider */
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
def init_session():
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "lead_captured" not in st.session_state:
        st.session_state.lead_captured = False
    if "lead_data" not in st.session_state:
        st.session_state.lead_data = None
    if "last_intent" not in st.session_state:
        st.session_state.last_intent = "unknown"
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = bool(os.environ.get("GROQ_API_KEY"))

init_session()


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎬 AutoStream")
    st.markdown('<div class="section-label">Agent Configuration</div>', unsafe_allow_html=True)

    # API Key input
    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Get your free key at console.groq.com"
    )
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input
        st.session_state.api_key_set = True

    st.markdown("---")
    st.markdown("#### 📊 Agent Status")

    # State display
    if st.session_state.agent:
        state = st.session_state.agent.get_state()
        turns = len([m for m in st.session_state.messages if m["role"] == "user"])

        intent_colors = {
            "greeting": "🟢",
            "product_inquiry": "🔵",
            "high_intent": "🟣",
            "unknown": "⚪",
        }
        intent = state.get("intent", "unknown")

        st.markdown(f"""
        <div class="status-panel">
            <div class="status-item"><span class="status-key">Intent</span>
            <span class="status-val">{intent_colors.get(intent,'⚪')} {intent.replace('_',' ').title()}</span></div>
            <div class="status-item"><span class="status-key">Turns</span>
            <span class="status-val">{turns}</span></div>
            <div class="status-item"><span class="status-key">Name</span>
            <span class="status-val {'filled' if state.get('lead_name') else 'missing'}">{state.get('lead_name') or '—'}</span></div>
            <div class="status-item"><span class="status-key">Email</span>
            <span class="status-val {'filled' if state.get('lead_email') else 'missing'}">{state.get('lead_email') or '—'}</span></div>
            <div class="status-item"><span class="status-key">Platform</span>
            <span class="status-val {'filled' if state.get('lead_platform') else 'missing'}">{state.get('lead_platform') or '—'}</span></div>
            <div class="status-item"><span class="status-key">Lead Captured</span>
            <span class="status-val {'filled' if state.get('lead_captured') else 'missing'}">{'✅ Yes' if state.get('lead_captured') else 'No'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Start a conversation to see agent state.")

    st.markdown("---")
    st.markdown("#### 💰 AutoStream Plans")
    st.markdown("""
    **Basic — $29/mo**
    - 10 videos/month
    - 720p resolution
    - Email support

    **Pro — $79/mo**
    - Unlimited videos
    - 4K resolution
    - AI captions
    - 24/7 support
    """)

    st.markdown("---")
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lead_captured = False
        st.session_state.lead_data = None
        st.session_state.last_intent = "unknown"
        if st.session_state.agent:
            st.session_state.agent.reset()
        st.rerun()


# ─────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-block">
    <p class="header-title">🎬 AutoStream AI Assistant</p>
    <p class="header-subtitle">Powered by Groq · Social-to-Lead Agentic Workflow · Built with Inflx</p>
</div>
""", unsafe_allow_html=True)

# API key warning
if not st.session_state.api_key_set:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to start chatting.")
    st.stop()

# Initialize agent
if st.session_state.agent is None:
    try:
        st.session_state.agent = AutoStreamAgent()
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi there! I'm **Aria**, AutoStream's AI assistant. I can help you learn about our video editing plans, pricing, and get you set up. What can I help you with today?",
            "intent": "greeting",
            "time": time.strftime("%H:%M")
        })
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.stop()


# ─── Lead Captured Banner ───
if st.session_state.lead_captured and st.session_state.lead_data:
    ld = st.session_state.lead_data
    st.markdown(f"""
    <div class="lead-success">
        <h3>🎉 Lead Captured Successfully!</h3>
        <p><b>Name:</b> {ld.get('name')}</p>
        <p><b>Email:</b> {ld.get('email')}</p>
        <p><b>Platform:</b> {ld.get('platform')}</p>
        <p style="color: #8888aa; font-size: 0.85rem; margin-top: 8px;">
        mock_lead_capture() was called and logged to console. In production, this posts to your CRM.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─── Chat Messages ───
st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)

chat_html = '<div class="chat-container" id="chat-container">'
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    t = msg.get("time", "")
    intent = msg.get("intent", "")

    if role == "assistant":
        badge = ""
        if intent and intent != "unknown":
            badge = f'<div><span class="intent-badge badge-{intent}">{intent.replace("_"," ").upper()}</span></div>'
        chat_html += f"""
        <div class="msg-row agent">
            <div class="avatar avatar-agent">🤖</div>
            <div>
                <div class="bubble bubble-agent">{content}</div>
                {badge}
                <div class="bubble-time">{t}</div>
            </div>
        </div>"""
    else:
        chat_html += f"""
        <div class="msg-row user">
            <div class="avatar avatar-user">👤</div>
            <div>
                <div class="bubble bubble-user">{content}</div>
                <div class="bubble-time" style="text-align:right">{t}</div>
            </div>
        </div>"""

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)


# ─── Suggested Prompts ───
if len(st.session_state.messages) <= 1:
    st.markdown('<div class="section-label" style="margin-top:12px">Try asking</div>', unsafe_allow_html=True)
    prompts = [
        "What's your pricing?",
        "Tell me about the Pro plan",
        "Do you offer refunds?",
        "I want to sign up for Pro!",
    ]
    cols = st.columns(len(prompts))
    for i, prompt in enumerate(prompts):
        if cols[i].button(prompt, key=f"prompt_{i}"):
            st.session_state["prefill"] = prompt
            st.rerun()


# ─── Input Form ───
st.markdown("---")
col1, col2 = st.columns([5, 1])

prefill = st.session_state.pop("prefill", "") if "prefill" in st.session_state else ""

with col1:
    user_input = st.text_input(
        "Message",
        value=prefill,
        placeholder="Ask about pricing, features, or say you're ready to sign up...",
        label_visibility="collapsed",
        key="chat_input"
    )
with col2:
    send = st.button("Send →", use_container_width=True)


# ─── Process Input ───
if (send or user_input) and user_input.strip():
    user_msg = user_input.strip()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_msg,
        "time": time.strftime("%H:%M")
    })

    # Get agent response
    with st.spinner("Aria is thinking..."):
        try:
            result = st.session_state.agent.chat(user_msg)
            response = result["response"]
            intent = result["intent"]
            captured = result["lead_captured"]
            lead_data = result.get("lead_data")

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "intent": intent,
                "time": time.strftime("%H:%M")
            })
            st.session_state.last_intent = intent

            if captured and lead_data:
                st.session_state.lead_captured = True
                st.session_state.lead_data = lead_data

        except Exception as e:
            st.error(f"Agent error: {e}")

    st.rerun()


# ─── Footer ───
st.markdown("""
<div style="text-align:center; margin-top:40px; color: #444; font-size: 0.78rem; font-family: 'Space Mono', monospace;">
    AutoStream Agent · Built with Groq + Streamlit
</div>
""", unsafe_allow_html=True)
