import os
import uuid
import time
import asyncio
import edge_tts
import pygame

VOICE = "bn-IN-TanishaaNeural"
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

try:
    pygame.mixer.init()
except Exception as e:
    print("Pygame Error:", e)

async def _generate_audio(text, filepath):
    communicate = edge_tts.Communicate(text, VOICE, rate="+10%")
    await communicate.save(filepath)

def speak_text(text, stop_flag_callback=None):
    if not text.strip():
        return
    
    unique_file = os.path.join(TEMP_DIR, f"v_{uuid.uuid4().hex[:8]}.mp3")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_audio(text, unique_file))
        loop.close()

        if os.path.exists(unique_file):
            pygame.mixer.music.load(unique_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if stop_flag_callback and stop_flag_callback():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.04)
    finally:
        try:
            pygame.mixer.music.unload()
            if os.path.exists(unique_file):
                os.remove(unique_file)
        except Exception:
            pass