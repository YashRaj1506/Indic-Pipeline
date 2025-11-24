import numpy as np
import soundfile as sf
import torch
import whisper

"""
Below are the requirements we've set up to ensure that our VAD and ASR checks run smoothly.
"""

torch.hub.HASH_CHECK = False

print("Loading Silero VAD model...")
VAD_MODEL, VAD_UTILS = torch.hub.load(
    "snakers4/silero-vad",
    "silero_vad",
    trust_repo=True,
    skip_validation=True,
    force_reload=False,
    onnx=False
)
print("VAD loaded.")

WHISPER_MODEL = whisper.load_model("tiny")

"""
The function below helps us analyze whether the audio duration falls between 2 and 30 seconds.
"""

def is_valid_duration(audio, sr, min_sec=2, max_sec=30):

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    num_samples = len(audio)
    duration = num_samples / sr

    print(f"Duration: {duration:.2f} seconds")

    return min_sec <= duration <= max_sec

"""
The function below helps calculate the estimated SNR and the silence ratio.
"""

def estimate_snr_and_silence(audio, sr, frame_length=1024, silence_threshold_db=-40):
    
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Normalize
    audio = audio.astype(np.float64)
    audio = audio / (np.max(np.abs(audio)) + 1e-10)
    
    # Frame the signal
    num_frames = len(audio) // frame_length
    frames = audio[:num_frames * frame_length].reshape(num_frames, frame_length)

    # Frame power
    frame_power = np.mean(frames ** 2, axis=1)

    # ---- SNR Calculation ----
    num_noise_frames = max(1, num_frames // 20)
    noise_power = np.mean(np.sort(frame_power)[:num_noise_frames])
    signal_power = np.mean(frame_power)
    noise_power = max(noise_power, 1e-8)
    snr_db = 10 * np.log10(signal_power / noise_power)
    snr_db = min(snr_db, 60.0)

    # ---- Silence Ratio Calculation ----
    # Convert silence threshold from dB to linear scale
    threshold = 10 ** (silence_threshold_db / 10.0)

    # Fraction of frames below threshold
    silent_frames = np.sum(frame_power < threshold)
    silent_ratio = silent_frames / num_frames

    return snr_db, silent_ratio


"""
This helps us Detecting if the clips has clipping or not.
"""

def detect_clipping_consecutive(audio, sr, consecutive_threshold=3):
    

    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Audio is usually float32 in [-1.0, 1.0]
    clipping_threshold = 0.98  # 98% of max amplitude
    at_max = np.abs(audio) > clipping_threshold
    
    clipping_events = []
    in_clip = False
    clip_start = 0
    clip_count = 0
    
    for i, is_clipped in enumerate(at_max):
        if is_clipped:
            if not in_clip:
                in_clip = True
                clip_start = i
                clip_count = 1
            else:
                clip_count += 1
        else:
            if in_clip and clip_count >= consecutive_threshold:
                clipping_events.append((clip_start, i))
            in_clip = False
    
    clipping_percentage = (sum(e[1]-e[0] for e in clipping_events) / len(audio)) * 100
    
    return {
        'has_clipping': len(clipping_events) > 0,
        'clipping_events_count': len(clipping_events),
        'clipping_percentage': clipping_percentage
    }


"""
Returns the VAD ratio, speech duration, and total duration for the given audio.
"""

def compute_vad_ratio(audio, sr):

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     vad_iterator,
     collect_chunks) = VAD_UTILS

    speech_timestamps = get_speech_timestamps(audio, VAD_MODEL, sampling_rate=sr)

    speech_samples = sum(ts["end"] - ts["start"] for ts in speech_timestamps)

    speech_seconds = speech_samples / sr
    total_seconds = len(audio) / sr

    vad_ratio = speech_seconds / total_seconds if total_seconds > 0 else 0

    return vad_ratio, speech_seconds, total_seconds


"""
Returns the average Whisper transcription confidence ( ASR Confidence ) for the given audio file.
"""

def whisper_confidence(audio_path):
    
    result = WHISPER_MODEL.transcribe(audio_path, temperature=0)

    tokens = result["segments"]
    if len(tokens) == 0:
        return 0.0 

    probs = []
    for seg in tokens:
        if "avg_logprob" in seg:
            probs.append(seg["avg_logprob"])

    probs = np.exp(probs)

    return float(np.mean(probs))


def analyze_audio_quality(audio_path):
    """
    Runs SNR, Silence Ratio, and Clipping detection
    and returns a combined dictionary.
    """

    audio, sr = sf.read(audio_path)

    overall_duration = is_valid_duration(audio, sr)
    snr_db, silence_ratio = estimate_snr_and_silence(audio, sr)
    clipping_info = detect_clipping_consecutive(audio, sr)
    vad_ratio, speech_seconds, total_seconds = compute_vad_ratio(audio, sr)
    asr_conf = whisper_confidence(audio_path)


    return {
        "overall_duration": overall_duration,
        "snr_db": float(snr_db),
        "silence_ratio": float(silence_ratio),
        "has_clipping": clipping_info["has_clipping"],
        "clipping_events_count": clipping_info["clipping_events_count"],
        "clipping_percentage": clipping_info["clipping_percentage"],
        "vad_ratio": vad_ratio,
        "speech_seconds": speech_seconds,
        "total_seconds": total_seconds,
        "asr_confidence": asr_conf 
    }



if __name__ == "__main__":
    result = analyze_audio_quality("hehe.flac")
    print(result)


