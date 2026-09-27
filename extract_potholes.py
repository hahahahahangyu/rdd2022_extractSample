from pathlib import Path
import json
import csv
import shutil

# Folder containing this Python script
ROOT = Path(__file__).resolve().parent

ANN_DIR = ROOT / "train" / "ann"
IMG_DIR = ROOT / "train" / "img"

OUTPUT_DIR = ROOT / "pothole_audit"
OUTPUT_IMG_DIR = OUTPUT_DIR / "images"
OUTPUT_ANN_DIR = OUTPUT_DIR / "annotations"
CSV_PATH = OUTPUT_DIR / "pothole_audit.csv"

OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_ANN_DIR.mkdir(parents=True, exist_ok=True)

total_json = 0
pothole_images = 0
pothole_instances = 0
missing_images = 0

rows = []

for json_path in ANN_DIR.glob("*.json"):
    total_json += 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find all objects labelled as pothole
    potholes = [
        obj for obj in data.get("objects", [])
        if str(obj.get("classTitle", "")).strip().lower() == "pothole"
    ]

    if not potholes:
        continue

    pothole_images += 1
    pothole_instances += len(potholes)

    # Annotation filename:
    # China_Drone_000035.jpg.json
    # Corresponding image:
    # China_Drone_000035.jpg
    image_filename = json_path.name[:-5]
    image_path = IMG_DIR / image_filename

    # Get source/country tag if available
    source = ""
    tags = data.get("tags", [])

    if tags:
        source = tags[0].get("name", "")

    if image_path.exists():
        shutil.copy2(
            image_path,
            OUTPUT_IMG_DIR / image_filename
        )

        shutil.copy2(
            json_path,
            OUTPUT_ANN_DIR / json_path.name
        )
    else:
        missing_images += 1

    rows.append({
        "filename": image_filename,
        "source": source,
        "pothole_count": len(potholes),

        # Fill these manually later
        "reference_class": "",
        "reference_type": "",
        "notes": ""
    })


# Create CSV for manual reference-object audit
with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
    fieldnames = [
        "filename",
        "source",
        "pothole_count",
        "reference_class",
        "reference_type",
        "notes"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print("===== RDD2022 SAMPLE POTHOLE AUDIT =====")
print(f"Annotation files checked : {total_json}")
print(f"Pothole images found     : {pothole_images}")
print(f"Pothole instances found  : {pothole_instances}")
print(f"Missing image files      : {missing_images}")
print()
print(f"Pothole images copied to : {OUTPUT_IMG_DIR}")
print(f"Audit CSV created at     : {CSV_PATH}")