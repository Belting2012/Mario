import numpy as np
import sounddevice as sd

mic_level = 0.0

def audio_cb(indata, frames, time, status):
    global mic_level
    rms = float(np.sqrt(np.mean(indata ** 2)))
    mic_level = 0.85 * mic_level + 0.01 * rms
