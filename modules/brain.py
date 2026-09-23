import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4"  # অথবা gemma:2b

SYSTEM_PROMPT = """
You are Mona, a caring, warm, and natural Bengali companion.
Rules:
- Speak naturally like a real companion.
- Keep responses short and sweet (1-3 sentences).
- Give immediate comforting answers in conversational Bengali.
"""

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def query_stream_ollama(user_msg, on_sentence_callback, stop_check_callback=None):
    global conversation_history
    conversation_history.append({"role": "user", "content": user_msg})
    
    # মেমোরি কন্ট্রোল
    if len(conversation_history) > 11:
        conversation_history = [conversation_history[0]] + conversation_history[-10:]

    full_response = ""
    buffer = ""

    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": conversation_history,
                "stream": True,
                "options": {"temperature": 0.7, "num_predict": 80}
            },
            stream=True,
            timeout=15
        )

        for line in res.iter_lines():
            if stop_check_callback and stop_check_callback():
                break
            if line:
                chunk = json.loads(line.decode("utf-8"))
                token = chunk.get("message", {}).get("content", "")
                full_response += token
                buffer += token

                if any(p in buffer for p in ["।", "?", "!", "\n"]):
                    parts = re.split(r'([।?!]+)', buffer)
                    if len(parts) >= 2:
                        sentence = parts[0] + parts[1]
                        buffer = "".join(parts[2:])
                        on_sentence_callback(sentence)

        if buffer.strip() and not (stop_check_callback and stop_check_callback()):
            on_sentence_callback(buffer.strip())

        conversation_history.append({"role": "assistant", "content": full_response.strip()])
        return full_response.strip()

    except Exception as e:
        print("Ollama Error:", e)
        err_msg = "একটু সমস্যা হচ্ছে, আবার বলবে?"
        on_sentence_callback(err_msg)
        return err_msg