import os
import sys
import time
import wave
import platform
from datetime import datetime
try:
    import sounddevice as sd
    import numpy as np
except Exception:
    print("sounddevice not found. Install with: pip install sounddevice")
    sys.exit(1)

def main():
    is_windows = platform.system() == "Windows"
    use_kb = False
    if is_windows:
        try:
            import msvcrt
            use_kb = True
        except Exception:
            use_kb = False

    sr = 44100
    ch = 1
    buf = []

    def cb(indata, frames, time_info, status):
        if status:
            pass
        buf.append(indata.copy())

    print("Audio Recorder")
    print("Sampling: {0} Hz  Channels: {1}".format(sr, ch))
    print("Press Q to stop recording")

    try:
        with sd.InputStream(samplerate=sr, channels=ch, dtype="int16", callback=cb):
            start = time.time()
            while True:
                if use_kb and msvcrt.kbhit():
                    c = msvcrt.getch()
                    if c in [b"q", b"Q"]:
                        break
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    data = np.concatenate(buf, axis=0) if buf else np.zeros((0, ch), dtype="int16")
    cur = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(cur))
    out_dir = os.path.join(root, "results", "audio")
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, "audio_{0}.wav".format(ts))

    wf = wave.open(out_path, "wb")
    wf.setnchannels(ch)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(data.tobytes())
    wf.close()
    print("Saved: {0}".format(out_path))

if __name__ == "__main__":
    main()
