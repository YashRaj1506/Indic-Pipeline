# Audio Filtering Pipeline for IndicVoices Dataset

This repository contains an **audio filtering pipeline** designed specifically for the dataset:

➡️ **IndicVoices Dataset** (AI4Bharat)  
https://huggingface.co/datasets/ai4bharat/IndicVoices

This pipeline filters, processes, and validates audio clips using multiple audio-quality metrics to ensure only clean, usable, and high‑quality data enters downstream training pipelines.

---

##
Make sure the indicvoices_data dataset has been downloaded and is present in the root directory.

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

## System Architecture
This pipeline follows a message-driven, parallel-processing architecture built using RabbitMQ and Celery. The system operates in the following way:

1. The dataset folder contains all raw audio files from the IndicVoices dataset. These audio files are processed in batches of 10.

2. A batching component creates these batches and the publisher.py file sends each batch to a RabbitMQ queue. Each message in the queue represents one batch of 10 audio files.

3. On the other end of the queue, a consumer listens for incoming batches. When a batch arrives, Celery workers pick up the task and process the batch concurrently and in parallel. This allows multiple batches to be evaluated at the same time for efficiency.

4. For every audio clip inside the batch, the system applies all metric checks duration, SNR, silence ratio, clipping, VAD ratio, and ASR confidence.

5. After evaluation, the results are stored in a CSV file which contains the metric scores and pass or fail status for each audio clip.

A diagram will be added here to visually represent the entire flow from batching, queueing, consuming, parallel processing, and evaluation.

![System Design](system_diagram.png)

---

### How this archtiecutre Scales

1) RabbitMQ decouples producers from workers, letting you add any number of Celery worker nodes without changing the pipeline.

2) We can add more servers, each additional server running Celery workers will increases parallel processing capacity, allowing more audio files to be evaluated simultaneously.

3) Throughput scales linearl, the more worker machines you add, the faster large datasets are processed.

4) If we have better GPU resources, we can use better models in whispers to increase the accuracy of ASR checks.

## ✔️ Summary
This pipeline provides a robust filtering mechanism for the **IndicVoices** dataset by applying industry‑standard audio metrics. By using duration checks, SNR, silence ratio, clipping detection, VAD, and ASR confidence, we ensure that only high-quality, speech‑rich, and model‑friendly audio samples pass through. This improves downstream training stability, accuracy, and overall dataset cleanliness.

Feel free to modify thresholds and extend the pipeline as per your project needs!

