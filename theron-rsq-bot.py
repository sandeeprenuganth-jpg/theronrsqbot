#!/usr/bin/env python3
"""
Theron RSQ Bot - terminal chat client
Calm, professional chatbot for healthcare-related and general messages.

Usage:
    1. Install requirements (see README.md)
    2. Set OPENAI_API_KEY in environment or in .env (this script reads env only)
    3. python3 theron_rsq_bot.py
"""

import os
import json
import time
import readline         # nicer input editing on many systems
from typing import List, Dict

try:
    import openai
except Exception as e:
    raise RuntimeError("Missing dependency 'openai'. Install from requirements.txt") from e

CONFIG_PATH = "config.json"
HISTORY_PATH = "conversation_history.md"

def load_config(path: str = CONFIG_PATH) -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(entry: str, path: str = HISTORY_PATH):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"---\n**{ts}**\n\n{entry}\n\n")

def build_message_system(config: Dict) -> Dict:
    return {"role": "system", "content": config.get("system_prompt", "")}

def chat_with_openai(messages: List[Dict], model: str, temperature: float = 0.2, max_tokens: int = 800) -> str:
    """
    Sends messages to OpenAI chat completion API and returns assistant reply text.
    Adjust model name to the model you have access to.
    """
    # Make sure API key present
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set. See README.md")
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # extract reply
    return response.choices[0].message.content.strip()

def terminal_chat_loop(config: Dict):
    model = config.get("model", "gpt-4o-mini")  # change to the model you prefer/own
    system_msg = build_message_system(config)

    print()
    print("Theron RSQ Bot — calm & professional (type 'exit' or 'quit' to end)")
    print("Disclaimer: This bot provides informational responses and is not a substitute for professional medical advice.")
    print()

    # conversation message list (keeps system message)
    messages = [system_msg]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        # append user message
        messages.append({"role": "user", "content": user_input})

        # call OpenAI
        try:
            assistant_reply = chat_with_openai(messages, model=model,
                                               temperature=config.get("temperature", 0.2),
                                               max_tokens=config.get("max_tokens", 800))
        except Exception as e:
            print(f"[Error] API call failed: {e}")
            # remove last user message to avoid growing messages infinitely on errors
            messages.pop()
            continue

        # append assistant reply to messages (for context in turn-based chat)
        messages.append({"role": "assistant", "content": assistant_reply})

        # print and log
        print("\nTheron RSQ Bot:\n" + assistant_reply + "\n")
        save_history(f"User: {user_input}\n\nBot: {assistant_reply}")

def main():
    config = load_config(CONFIG_PATH)
    terminal_chat_loop(config)

if __name__ == "__main__":
    main()
