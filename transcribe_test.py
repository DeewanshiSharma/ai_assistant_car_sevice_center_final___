from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import soundfile as sf

# Load audio
audio, sr = sf.read("test.wav")
audio = audio.astype("float32")  # ensure correct type

# Load model
processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Process audio
input_features = processor(audio, sampling_rate=sr, return_tensors="pt").input_features.to(device)

# Generate transcription
predicted_ids = model.generate(input_features)
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
print("Transcription:", transcription)
