import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

with open(os.path.join(OUTPUTS_DIR,"audio.txt"), "r") as file:
    data = json.load(file)

BATCH_SIZE = 10
batches = []

for lang_data in data:
    files = lang_data["files"]
    language = lang_data["name_of_folder"]

    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i : i + BATCH_SIZE]
        batches.append(
            {"language": language, "batch_id": len(batches) + 1, "files": batch}
        )

with open(os.path.join(OUTPUTS_DIR,"batches.txt"), "w") as l:
    json.dump(batches, l, indent=2)
