# 🎬 AutoStream AI Sales Agent
### Social-to-Lead Agentic Workflow | ServiceHive × Inflx Assignment

> A production-grade conversational AI agent that converts social media conversations into qualified business leads using **intent detection**, **RAG-powered knowledge retrieval**, and **automated lead capture**.

---

## 📁 Project Structure

```
autostream_agent/
├── app.py                        # Streamlit Web UI
├── main.py                       # CLI runner (for terminal testing)
├── requirements.txt
├── .env.example
│
├── agent/
│   ├── __init__.py
│   ├── autostream_agent.py       # Core agent logic + state management
│   └── rag_pipeline.py           # RAG: KB loader + context builder
│
├── tools/
│   ├── __init__.py
│   └── lead_capture.py           # mock_lead_capture() tool
│
└── knowledge_base/
    └── autostream_kb.json        # Pricing, features, policies, FAQs
```

---

## 🚀 How to Run Locally

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set Your Groq API Key

Get a **free** Groq API key at [console.groq.com](https://console.groq.com)

**Option A — `.env` file (recommended):**
```bash
cp .env.example .env
# Now edit .env and paste your key:
# GROQ_API_KEY=gsk_your_actual_key_here
```

**Option B — Export directly (no .env needed):**
```bash
# macOS/Linux:
export GROQ_API_KEY=gsk_your_key_here

# Windows CMD:
set GROQ_API_KEY=gsk_your_key_here

# Windows PowerShell:
$env:GROQ_API_KEY="gsk_your_key_here"
```

### Step 5A — Launch the Streamlit Web UI
```bash
streamlit run app.py
```
Then open [http://localhost:8501](http://localhost:8501) in your browser.

> 💡 You can also paste your API key directly in the sidebar of the UI — no `.env` needed.

### Step 5B — Run in Terminal (CLI Mode)
```bash
python main.py
```

---

## 🧪 Example Conversation Flow

```
You:  Hi there!
Aria: 👋 Hi! I'm Aria, AutoStream's AI assistant...

You:  What's the difference between your plans?
Aria: [Retrieves from knowledge base] Basic is $29/mo for 10 videos...
      Pro is $79/mo with unlimited videos, 4K, and AI captions...

You:  That sounds great, I want to sign up for the Pro plan for my YouTube channel!
Aria: Awesome! I'd love to get you set up. What's your full name?

You:  Abhishek Sharma
Aria: Great, Abhishek! And what's your email address?

You:  abhishek@example.com
Aria: Perfect! Last thing — which platform do you primarily create for?

You:  YouTube
Aria: ✅ You're all set, Abhishek! I've captured your details...

# Console output:
# ==================================================
# ✅ Lead captured successfully!
#    Name     : Abhishek Sharma
#    Email    : abhishek@example.com
#    Platform : YouTube
#    Lead ID  : LEAD-XXXXX
# ==================================================
```

---

## 🏗️ Architecture Explanation (~200 words)

### Why Groq + Direct API (instead of LangChain/LangGraph)?

While the assignment lists LangChain/LangGraph as preferred, this project deliberately uses the **Groq API directly** for three reasons: (1) Groq's `llama-3.3-70b-versatile` model is exceptionally capable at instruction-following, making complex framework abstractions unnecessary for this scope; (2) Direct API usage produces cleaner, more readable, and more maintainable code — critical for a real-world production deployment evaluation; (3) LangGraph's overhead is better justified for multi-agent systems with branching workflows, not a single-agent linear flow.

### State Management

State is managed via a Python `TypedDict` (`AgentState`) held in memory within the `AutoStreamAgent` class instance. It tracks:
- **conversation_history**: Full message list passed to Groq on every turn (sliding context window)
- **intent**: Classified per turn (`greeting`, `product_inquiry`, `high_intent`)
- **lead fields**: `name`, `email`, `platform` — collected progressively
- **lead_captured / collecting_lead**: Boolean flags controlling tool execution gates

The LLM retains context across 5–6+ turns because the full conversation history is replayed on each API call — stateless API, stateful client.

### RAG Pipeline

The knowledge base (JSON) is loaded once at startup and converted into a structured text block injected into the system prompt. For this KB size (~1KB), this "prompt-stuffing RAG" is more reliable than vector retrieval. In production, this would be replaced with embeddings + FAISS/Pinecone.

---

## 📱 WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, the integration works as follows:

### Architecture
```
WhatsApp User
     ↓  (sends message)
WhatsApp Business API / Twilio for WhatsApp
     ↓  (HTTP POST to your webhook URL)
FastAPI / Flask Webhook Server  ←── your hosted server
     ↓
AutoStreamAgent.chat(message)
     ↓
Groq LLM API
     ↓  (response)
Webhook Server → WhatsApp API → User receives reply
```

### Step-by-Step Integration

1. **Register a WhatsApp Business App** on [Meta for Developers](https://developers.facebook.com/) or use [Twilio's WhatsApp Sandbox](https://www.twilio.com/whatsapp).

2. **Create a webhook endpoint** using FastAPI:
```python
from fastapi import FastAPI, Request
from agent.autostream_agent import AutoStreamAgent

app = FastAPI()
sessions = {}  # phone_number → AutoStreamAgent instance

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    phone = data["from"]         # e.g. "whatsapp:+91XXXXXXXXXX"
    message = data["body"]       # user's text message

    # Per-user agent session
    if phone not in sessions:
        sessions[phone] = AutoStreamAgent()

    result = sessions[phone].chat(message)
    return {"reply": result["response"]}
```

3. **Deploy** to a public URL (Railway, Render, AWS EC2, etc.).

4. **Register your webhook URL** in Meta Dashboard or Twilio Console.

5. **Verification**: Meta sends a `GET` request with a verify token — your server must echo back the `hub.challenge` value.

6. **Session persistence**: Replace the in-memory `sessions` dict with Redis for production-grade multi-instance deployments.

---

## 🧠 Agent Capabilities

| Capability | Implementation |
|---|---|
| Intent Detection | Rule-based pre-check + LLM classification |
| RAG | JSON KB → system prompt injection |
| State Management | `AgentState` TypedDict + full history replay |
| Lead Collection | Sequential one-field-at-a-time prompting |
| Tool Execution | `mock_lead_capture()` called only after all 3 fields |
| Memory (5-6 turns) | Full `conversation_history` passed each API call |

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| LLM Provider | Groq (llama-3.3-70b-versatile) |
| Web UI | Streamlit |
| Knowledge Base | Local JSON (RAG via prompt injection) |
| Lead Tool | Python mock function |

---

## 📬 Submission

- **GitHub Repo**: [your-github-link]
- **Demo Video**: [your-loom-or-youtube-link]

---

*Built for ServiceHive × Inflx — Social-to-Lead Agentic Workflow Assignment*
