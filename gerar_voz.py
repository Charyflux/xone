#!/usr/bin/env python3
"""
Gera a voz metálica de mordomo do JARVIS.
Corre este script apenas se quiseres regenerar o welcome.mp3.
Requer: gtts, ffmpeg, sox
"""
import os, sys, subprocess

FRASE = "Bem vindo, senhor. Todos os sistemas estão operacionais."
DIR   = os.path.dirname(os.path.abspath(__file__))

def instalar():
    subprocess.run([sys.executable, "-m", "pip", "install", "gtts",
                    "--break-system-packages", "-q"], check=False)

def gerar():
    from gtts import gTTS
    print("[1/3] Gerando voz com Google TTS...")
    tts = gTTS(FRASE, lang='pt', slow=True)
    tts.save("/tmp/_jarvis_base.mp3")

    print("[2/3] Aplicando efeitos metálicos...")
    subprocess.run(["ffmpeg", "-i", "/tmp/_jarvis_base.mp3",
                    "/tmp/_jarvis_base.wav", "-y"], capture_output=True)

    subprocess.run(["sox", "/tmp/_jarvis_base.wav", "/tmp/_jarvis_fx.wav",
                    "pitch", "-280",
                    "chorus", "0.7", "0.9", "55", "0.45", "0.22", "2.2", "-s",
                    "reverb", "40", "35", "60", "80", "0", "-2",
                    "gain", "-6", "norm", "-1"], capture_output=True)

    print("[3/3] Exportando welcome.mp3...")
    out = os.path.join(DIR, "welcome.mp3")
    subprocess.run(["ffmpeg", "-i", "/tmp/_jarvis_fx.wav",
                    "-codec:a", "libmp3lame", "-b:a", "192k", "-ar", "44100",
                    out, "-y"], capture_output=True)
    print(f"[OK] Ficheiro gerado: {out}")

instalar()
gerar()
