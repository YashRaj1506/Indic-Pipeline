import os
import json

path = "/home/yash/Desktop/sarvam/indicvoices_data/audios"

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

data_set_folders = []
batches = []

entries = os.listdir(path)
language_specific_paths = [f"{path}/{language_folder}" for language_folder in entries]

for language_folders in language_specific_paths:

    train_folders = os.listdir(language_folders)
    for individual_folder in train_folders:
        if individual_folder.startswith("train"):
            data_set_folders.append(f"{language_folders}/{individual_folder}")

            list_of_current_items = os.listdir(
                f"{language_folders}/{individual_folder}"
            )

            batches.append(
                {
                    "name_of_folder": f"{language_folders.split("/")[-1]}",
                    "files": [
                        f"/indicvoices_data/audios/{language_folders.split("/")[7]}/{individual_folder}/{name}"
                        for name in list_of_current_items
                    ],
                }
            )

with open(os.path.join(OUTPUTS_DIR, "audio.txt"), "w") as p:
    json.dump(batches, p, indent=2)

print("-----------------------------------------")

print(batches)
