import threading
import customtkinter as ctk
from modules.voice_in import calibrate_mic, listen_audio
from modules.voice_out import speak_text
from modules.brain import query_stream_ollama

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Mona AI - Companion Project")
root.geometry("620x640")

status_label = ctk.CTkLabel(root, text="Starting Mona...", font=("Arial", 14))
status_label.pack(pady=8)

chat_box = ctk.CTkTextbox(root, width=560, height=360, font=("Arial", 15), wrap="word")
chat_box.pack(pady=8)

entry = ctk.CTkEntry(root, width=440, height=40, placeholder_text="Mona-কে কিছু বলো...")
entry.pack(pady=5)

stop_flag = False

def update_chat(sender, text):
    root.after(0, lambda: chat_box.insert("end", f"{sender}: {text}\n\n"))
    root.after(0, lambda: chat_box.see("end"))

def set_status(text):
    root.after(0, lambda: status_label.configure(text=text))

def handle_user_input(text):
    global stop_flag
    if not text:
        return
    update_chat("You", text)
    set_status("🧠 Mona ভাবছে...")

    def on_sentence(sentence):
        speak_text(sentence, lambda: stop_flag)

    full_ans = query_stream_ollama(text, on_sentence, lambda: stop_flag)
    update_chat("Mona", full_ans)
    set_status("🎙️ Mona প্রস্তুত...")

def voice_chat_loop():
    set_status("🎙️ শুনছি, বলো...")
    user_text = listen_audio(timeout_sec=5, limit_sec=10)
    if user_text:
        handle_user_input(user_text)

# Buttons
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="🎙️ Speak", width=120, command=lambda: threading.Thread(target=voice_chat_loop, daemon=True).start()).pack(side="left", padx=5)
ctk.CTkButton(btn_frame, text="Send Text", width=120, command=lambda: [handle_user_input(entry.get()), entry.delete(0, "end")]).pack(side="left", padx=5)

threading.Thread(target=calibrate_mic, daemon=True).start()
root.mainloop()