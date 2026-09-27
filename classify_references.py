from pathlib import Path
import cv2
import csv

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "pothole_audit" / "images"
OUTPUT_CSV = ROOT / "pothole_audit" / "reference_classification.csv"

# Load all pothole images
image_files = sorted(
    list(IMAGE_DIR.glob("*.jpg")) +
    list(IMAGE_DIR.glob("*.jpeg")) +
    list(IMAGE_DIR.glob("*.png"))
)

if not image_files:
    print("No images found.")
    print("Expected folder:")
    print(IMAGE_DIR.resolve())
    exit()

# Read previous classifications so the program can resume
results = {}

if OUTPUT_CSV.exists():
    with open(OUTPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            results[row["filename"]] = row["reference_class"]

print(f"Images found: {len(image_files)}")
print(f"Already classified: {len(results)}")
print()
print("Controls:")
print("0 = R0 - No useful reference")
print("1 = R1 - Object visible but unsuitable")
print("2 = R2 - Potential usable road-plane reference")
print("3 = R3 - Strong / confirmed reference candidate")
print("S = Skip")
print("Q = Save and quit")
print()


def save_results():
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["filename", "reference_class"]
        )

        writer.writeheader()

        for filename, classification in results.items():
            writer.writerow({
                "filename": filename,
                "reference_class": classification
            })


for index, image_path in enumerate(image_files, start=1):

    # Skip images already classified
    if image_path.name in results:
        continue

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not open: {image_path.name}")
        continue

    # Resize large images while preserving aspect ratio
    max_width = 1200
    max_height = 800

    height, width = image.shape[:2]

    scale = min(
        max_width / width,
        max_height / height,
        1
    )

    if scale < 1:
        image = cv2.resize(
            image,
            (int(width * scale), int(height * scale))
        )

    # Add image information
    text = f"{index}/{len(image_files)}  {image_path.name}"

    cv2.putText(
        image,
        text,
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        image,
        "0:R0  1:R1  2:R2  3:R3  S:Skip  Q:Quit",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 255),
        2
    )

    cv2.imshow("RDD2022 Reference Audit", image)

    while True:
        key = cv2.waitKey(0) & 0xFF

        if key == ord("0"):
            results[image_path.name] = "R0"
            break

        elif key == ord("1"):
            results[image_path.name] = "R1"
            break

        elif key == ord("2"):
            results[image_path.name] = "R2"
            break

        elif key == ord("3"):
            results[image_path.name] = "R3"
            break

        elif key in [ord("s"), ord("S")]:
            break

        elif key in [ord("q"), ord("Q")]:
            save_results()
            cv2.destroyAllWindows()

            print("\nProgress saved.")
            print(f"Classified: {len(results)}")
            print(f"CSV: {OUTPUT_CSV.resolve()}")

            exit()

    # Save after every classification
    save_results()

cv2.destroyAllWindows()

print("\n===== CLASSIFICATION COMPLETE =====")

for category in ["R0", "R1", "R2", "R3"]:
    count = list(results.values()).count(category)
    print(f"{category}: {count}")

print(f"\nResults saved to:")
print(OUTPUT_CSV.resolve())