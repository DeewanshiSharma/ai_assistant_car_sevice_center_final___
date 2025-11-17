import sounddevice as sd
import numpy as np
import soundfile as sf
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch

# --- Step 1: Record voice ---
RATE = 16000
DURATION = 5  # seconds
FILENAME = "recorded.wav"

print(f"Recording for {DURATION} seconds...")
audio_data = sd.rec(int(DURATION * RATE), samplerate=RATE, channels=1)
sd.wait()  # Wait until recording is finished
audio_data = np.squeeze(audio_data)  # Convert 2D array to 1D
sf.write(FILENAME, audio_data, RATE)
print("Recording saved as", FILENAME)

# --- Step 2: Load audio ---
audio_data, sr = sf.read(FILENAME)

# --- Step 3: Load Whisper model ---
print("Loading Whisper model...")
processor = WhisperProcessor.from_pretrained("openai/whisper-medium")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# --- Step 4: Prepare input ---
input_features = processor(audio_data, sampling_rate=sr, return_tensors="pt").input_features
input_features = input_features.to(device)

# --- Step 5: Generate transcription ---
predicted_ids = model.generate(input_features)
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

print("Transcription:")
print(transcription[0])
