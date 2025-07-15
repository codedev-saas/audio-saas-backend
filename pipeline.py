import os, tempfile
from pathlib import Path
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import soundfile as sf
import librosa
from spleeter.separator import Separator
import whisper

whisper_model = whisper.load_model("base")
separator = Separator('spleeter:2stems')

def extract_audio(input_path):
    ext = Path(input_path).suffix.lower()
    if ext in [".mp4", ".mkv", ".mov", ".avi"]:
        out = tempfile.mktemp(suffix=".wav")
        VideoFileClip(input_path).audio.write_audiofile(out, fps=44100, verbose=False, logger=None)
        return out
    return input_path

# (Include trim_audio, normalize_audio, separate_vocals, transcribe_audio, convert_to_mp3 as before)

def process_pipeline(file_path, start, end, steps):
  def trim_audio(audio_path, start_sec, end_sec):
    y, sr = librosa.load(audio_path, sr=None)
    trimmed = y[int(start_sec * sr):int(end_sec * sr)]
    temp_path = tempfile.mktemp(suffix=".wav")
    sf.write(temp_path, trimmed, sr)
    return temp_path

def separate_vocals(audio_path):
    output_dir = "static/spleeter_output"
    os.makedirs(output_dir, exist_ok=True)
    separator.separate_to_file(audio_path, output_dir)

    base_name = Path(audio_path).stem
    vocals = f"{output_dir}/{base_name}/vocals.wav"
    instrumental = f"{output_dir}/{base_name}/accompaniment.wav"

    return vocals if Path(vocals).exists() else None, instrumental if Path(instrumental).exists() else None

def normalize_audio(audio_path):
    sound = AudioSegment.from_file(audio_path)
    normalized = sound.apply_gain(-sound.dBFS)
    temp_path = tempfile.mktemp(suffix=".wav")
    normalized.export(temp_path, format="wav")
    return temp_path

def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def convert_to_mp3(wav_path):
    sound = AudioSegment.from_wav(wav_path)
    mp3_path = Path(wav_path).with_suffix(".mp3")
    sound.export(mp3_path, format="mp3")
    return str(mp3_path)

def process_pipeline(file_path, start_sec, end_sec, steps):
    input_path = extract_audio(file_path)
    trimmed_wav = trim_audio(input_path, start_sec, end_sec)

    result = {
        "trimmed": convert_to_mp3(trimmed_wav),
        "vocals": None,
        "instrumental": None,
        "normalized": None,
        "transcription": None
    }

    if "vocal" in steps:
        vocals, instrumental = separate_vocals(trimmed_wav)
        if vocals: result["vocals"] = convert_to_mp3(vocals)
        if instrumental: result["instrumental"] = convert_to_mp3(instrumental)

    if "normalize" in steps:
        norm_wav = normalize_audio(trimmed_wav)
        result["normalized"] = convert_to_mp3(norm_wav)

    if "transcribe" in steps:
        result["transcription"] = transcribe_audio(trimmed_wav)

    return result  
