"""
main.py — CLI runner for AutoStream Agent
Use this to test the agent in the terminal without Streamlit.
Run: python main.py
"""

import os
from agent.autostream_agent import AutoStreamAgent


def main():
    print("\n" + "="*60)
    print("  🎬 AutoStream AI Sales Agent — CLI Mode")
    print("  Type 'exit' or 'quit' to stop | 'reset' to restart")
    print("="*60 + "\n")

    # Check API key
    if not os.environ.get("GROQ_API_KEY"):
        api_key = input("Enter your Groq API Key: ").strip()
        if not api_key:
            print("❌ No API key provided. Exiting.")
            return
        os.environ["GROQ_API_KEY"] = api_key

    agent = AutoStreamAgent()
    print("Aria: 👋 Hi! I'm Aria, AutoStream's AI assistant. How can I help you today?\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        if user_input.lower() == "reset":
            agent.reset()
            print("\n🔄 Conversation reset.\n")
            print("Aria: Hi again! How can I help you?\n")
            continue

        result = agent.chat(user_input)
        print(f"\nAria: {result['response']}")
        print(f"      [Intent: {result['intent']}]")
        if result["lead_captured"]:
            print(f"\n🎉 Lead captured! Check console above for details.")
        print()


if __name__ == "__main__":
    main()
