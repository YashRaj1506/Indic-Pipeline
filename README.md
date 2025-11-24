# Audio Filtering Pipeline for IndicVoices Dataset

This repository contains an **audio filtering pipeline** designed specifically for the dataset:

➡️ **IndicVoices Dataset** (AI4Bharat)  
https://huggingface.co/datasets/ai4bharat/IndicVoices

This pipeline filters, processes, and validates audio clips using multiple audio-quality metrics to ensure only clean, usable, and high‑quality data enters downstream training pipelines.

---

## Clone the Repo

```sh
git clone https://github.com/YashRaj1506/Indic-Pipeline
```

---

## 📌 Makefile Commands
You can run the entire pipeline using the following commands:

### **1. Build containers**
```sh
docker-compose build
```
Run using:
```
make build
```

### **2. Prepare batches**
This step categorizes and batches the dataset.
```sh
python batching/data_categorizer.py
python batching/batch_creator.py
```
Run using:
```
make ready
```

### **3. Start the Docker pipeline**
```sh
docker-compose up
```
Run using:
```
make up
```

### **4. Start publishers**
This runs the message‑publishing component.
```sh
python publishers.py
```
Run using:
```
make start
```

---

## 📌 Metrics Used for Audio Filtering
A `metrics.py` file contains several metric functions used to filter poor‑quality or unusable audio clips. Below are the functions exactly as described.

---

### **1) is_valid_duration()**
This metric function helps us analyze whether the audio duration falls between 2 and 30 seconds.

**Why:** On my research i got to know a good audio dataset should be between this time duration only.

---

### **2) estimate_snr_and_Silence**
This metric function helpus us calculate the estimate SNR and silence Ratio.

**Why:**
- SNR shows us how strong the useful speech signal is compared to noise.
- High SNR → little noise → clean speech
- Low SNR → lots of noise → poor quality speech (traffic, fan, distortion, background voices)

If dataset has too much noise, then your model becomes unstable, slow to train, and generalizes badly.

Silence Ratio shows percentage of audio duration that contains silence instead of speech.

So we set a threshold for this, if a audio’s silence ratio is above than that, we consider it as untrainable data.

---

### **3) detect_clipping_consecutive**
This metric function helps us detect if the audio is clipped or not in a consecutive manner.

**Why:** We use this function because clipped audio is destroyed audio, the waveform has lost information permanently and cannot be restored. Training on clipped audio corrupts speech models.

---

### **4) compute_vad_ratio**
VAD = Voice Activity Detection. It detects which parts of the audio contain speech and which parts contain silence/noise/background.

**Why:** We use VAD to measure how much of the clip actually contains speech. VAD ensures the audio has real speech content, not silence or random noise.

---

### **5) whisper_confidence [our asr check]**
ASR = Automatic Speech Recognition. ASR confidence tells us how “transcribable” the audio is.

We are using open ai’s whisper for the asr check.

**Why:** Low-confidence scores indicate noisy, distorted, or non-speech clips that would hurt model training.

Using ASR filtering ensures only clean, transcribable, high-quality speech enters the dataset, improving downstream model accuracy.

---

## 📌 Metrics Configuration File
There is a configuration file named **`metrics_config.json`**, which contains the threshold values used by `metrics.py`:

```json
{
    "snr_min": 20.00,
    "silence_ratio_min": 0.50,
    "vad_ratio": 0.40,
    "asr_confidence": 0.35
}
```

```sh
Our Threshold Logic :
    result["has_clipping"] == False
    result["snr_db"] > snr_val
    result["silence_ratio"] < silence_ratio_val
    result["overall_duration"] == True
    result["vad_ratio"] > vad_ratio_val
    result["asr_confidence"] > asr_confidence_val
```

You can modify this file to adjust the audio‑filtering thresholds as needed.

---

## Output

The final CSV file "good_audio_list.csv" will be build inside outputs folder.

output format :

```sh
Rejected,/path/to/file.flac,False,22.29,0.0,True,0.75,0.41
Rejected,/path/to/file.flac,False,36.36,0.29,True,0.73,0.37
Rejected,/path/to/file.flac,False,44.95,0.13,True,0.86,0.42
...
Accepted,/path/to/file.flac,False,41.08,0.22,True,0.81,0.23
```

---

## ✔️ Summary
This pipeline provides a robust filtering mechanism for the **IndicVoices** dataset by applying industry‑standard audio metrics. By using duration checks, SNR, silence ratio, clipping detection, VAD, and ASR confidence, we ensure that only high-quality, speech‑rich, and model‑friendly audio samples pass through. This improves downstream training stability, accuracy, and overall dataset cleanliness.

Feel free to modify thresholds and extend the pipeline as per your project needs!

