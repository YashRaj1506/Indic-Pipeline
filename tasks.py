from celery import Celery
import time
from metrics.metrics import analyze_audio_quality
import os
import json
import logging


logger = logging.getLogger(__name__)


with open("metrics_config.json") as f:
    cfg = json.load(f)


snr_val = cfg["snr_min"]
silence_ratio_val = cfg["silence_ratio_min"]
vad_ratio_val = cfg["vad_ratio"]
asr_confidence_val = cfg["asr_confidence"]

PROJECT_ROOT = os.path.dirname(__file__)
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

app = Celery(
    "audio_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://user:password@localhost//"),
)


@app.task
def process_batch(batch):
    logger.info(f"Processing batch of {len(batch['files'])} audio files...")

    processed = 0
    errors = 0
    good_files = 0

    with open(os.path.join(OUTPUTS_DIR, "good_audio_list.txt"), "a") as f:
        for audios in batch["files"]:
            try:
                result = analyze_audio_quality(audios)
                processed += 1

                if (
                    result["has_clipping"] == False
                    and result["snr_db"] > snr_val
                    and result["silence_ratio"] < silence_ratio_val
                    and result["overall_duration"] == True
                    and result["vad_ratio"] > vad_ratio_val
                    and result["asr_confidence"] < asr_confidence_val
                ):
                    f.write(audios + "\n")
                    good_files += 1

            except Exception as e:
                errors += 1
                logger.error(f"Error processing {audios}: {str(e)[:100]}")
                continue

    logger.info(
        f" Done with batch: {processed} processed, {good_files} good, {errors} errors"
    )
    return {"processed": processed, "good": good_files, "errors": errors}
