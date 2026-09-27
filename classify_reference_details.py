from pathlib import Path
import cv2
import csv

ROOT = Path(__file__).resolve().parent

IMAGE_DIR = ROOT / "pothole_audit" / "images"

CLASS_CSV = (
    ROOT
    / "pothole_audit"
    / "reference_classification.csv"
)

OUTPUT_CSV = (
    ROOT
    / "pothole_audit"
    / "reference_details.csv"
)


# ---------------------------------------------------
# Load previous R0-R3 classifications
# ---------------------------------------------------

selected_images = []

with open(CLASS_CSV, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["reference_class"] in ["R2", "R3"]:
            selected_images.append({
                "filename": row["filename"],
                "reference_class": row["reference_class"]
            })


# ---------------------------------------------------
# Load previous detailed results if they exist
# ---------------------------------------------------

results = {}

if OUTPUT_CSV.exists():

    with open(OUTPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:

            # Only load rows using the current V/U system
            if row.get("dimension_status") in [
                "verifiable",
                "unknown"
            ]:
                results[row["filename"]] = row


# ---------------------------------------------------
# Save function
# ---------------------------------------------------

def save_results():

    with open(
        OUTPUT_CSV,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        fieldnames = [
            "filename",
            "reference_class",
            "reference_type",
            "dimension_status"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in results.values():
            writer.writerow(row)


# ---------------------------------------------------
# Instructions
# ---------------------------------------------------

print("===== REFERENCE DETAIL AUDIT =====")
print()
print(f"R2/R3 images found: {len(selected_images)}")
print(f"Already reviewed: {len(results)}")
print()

print("STEP 1 - REFERENCE TYPE")
print("1 = Road / lane marking")
print("2 = Drain / manhole cover")
print("3 = Vehicle")
print("4 = Road sign")
print("5 = Other")
print()

print("STEP 2 - PHYSICAL DIMENSION")
print("V = Verifiable")
print("U = Unknown / cannot be verified")
print()

print("Q = Save and quit")
print()


# ---------------------------------------------------
# Review images
# ---------------------------------------------------

for index, item in enumerate(selected_images, start=1):

    filename = item["filename"]
    reference_class = item["reference_class"]

    # Skip already reviewed images
    if filename in results:
        continue

    image_path = IMAGE_DIR / filename

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Cannot open: {filename}")
        continue


    # Resize image if needed
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
            (
                int(width * scale),
                int(height * scale)
            )
        )


    # Show image information
    cv2.putText(
        image,
        f"{index}/{len(selected_images)} | {reference_class} | {filename}",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.putText(
        image,
        "TYPE: 1=RoadMark  2=Drain/Manhole  3=Vehicle  4=Sign  5=Other",
        (15, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 255),
        1
    )

    cv2.imshow(
        "Reference Detail Audit",
        image
    )


    # ------------------------------------------------
    # STEP 1: Reference type
    # ------------------------------------------------

    reference_type = None

    while True:

        key = cv2.waitKey(0) & 0xFF

        if key == ord("1"):
            reference_type = "road_marking"
            break

        elif key == ord("2"):
            reference_type = "drain_or_manhole"
            break

        elif key == ord("3"):
            reference_type = "vehicle"
            break

        elif key == ord("4"):
            reference_type = "road_sign"
            break

        elif key == ord("5"):
            reference_type = "other"
            break

        elif key in [ord("q"), ord("Q")]:

            save_results()
            cv2.destroyAllWindows()

            print("Progress saved.")
            print(OUTPUT_CSV.resolve())

            exit()


    # ------------------------------------------------
    # STEP 2: Verifiable or unknown
    # ------------------------------------------------

    image2 = image.copy()

    cv2.putText(
        image2,
        "DIMENSION: V=Verifiable   U=Unknown",
        (15, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.imshow(
        "Reference Detail Audit",
        image2
    )

    dimension_status = None

    while True:

        key = cv2.waitKey(0) & 0xFF

        if key in [ord("v"), ord("V")]:
            dimension_status = "verifiable"
            break

        elif key in [ord("u"), ord("U")]:
            dimension_status = "unknown"
            break

        elif key in [ord("q"), ord("Q")]:

            save_results()
            cv2.destroyAllWindows()

            print("Progress saved.")
            print(OUTPUT_CSV.resolve())

            exit()


    results[filename] = {

        "filename": filename,

        "reference_class": reference_class,

        "reference_type": reference_type,

        "dimension_status": dimension_status
    }

    # Save after every image
    save_results()


cv2.destroyAllWindows()


# ---------------------------------------------------
# Summary
# ---------------------------------------------------

print()
print("===== DETAIL AUDIT COMPLETE =====")
print()

types = [
    "road_marking",
    "drain_or_manhole",
    "vehicle",
    "road_sign",
    "other"
]

print("Reference types:")

for ref_type in types:

    count = sum(
        1
        for row in results.values()
        if row["reference_type"] == ref_type
    )

    print(f"{ref_type}: {count}")


print()
print("Dimension status:")

for status in [
    "verifiable",
    "unknown"
]:

    count = sum(
        1
        for row in results.values()
        if row["dimension_status"] == status
    )

    print(f"{status}: {count}")


print()
print("Results saved to:")
print(OUTPUT_CSV.resolve())