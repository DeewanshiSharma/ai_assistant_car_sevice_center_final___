import sounddevice as sd
import numpy as np
import wavio
import os

SAMPLE_RATE = 16000
DURATION = 5  # seconds
MIC_INDEX = 1  # replace with your mic index

output_file = os.path.join(os.getcwd(), "test.wav")
print("Recording...")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, device=MIC_INDEX, dtype='float32')
sd.wait()
audio = np.squeeze(audio)
wavio.write(output_file, audio, SAMPLE_RATE, sampwidth=3)
print("Saved test.wav at:", output_file)
