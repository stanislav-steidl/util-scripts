"""photo ordering script"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS


def get_image_timestamp(image_path):
    """Try to read EXIF DateTimeOriginal, fallback to file modified time."""
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTime":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(image_path.stat().st_mtime)


def collect_images(folder):
    """Collect all images from a folder (non-recursive)."""
    exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    return [p for p in folder.iterdir() if p.suffix.lower() in exts]


def main():
    parser = argparse.ArgumentParser(
        description="Rename images in a folder sequentially based on timestamp."
    )
    parser.add_argument(
        "--folder",
        type=Path,
        default="C:\development\data\Matej-rok_2_a_3",
        help="Path to the folder with images",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="C:\development\data\Matej-rok_2_a_3_ordered",
        help="Optional output folder (copies files instead of renaming in place)",
    )
    args = parser.parse_args()

    if not args.folder.is_dir():
        parser.error(f"{args.folder} is not a valid folder.")

    images = collect_images(args.folder)
    if not images:
        print("No images found.")
        return

    images.sort(key=get_image_timestamp)

    output_folder = args.output if args.output else args.folder
    output_folder.mkdir(parents=True, exist_ok=True)

    for idx, img_path in enumerate(images, start=1):
        new_name = f"{idx}{img_path.suffix.lower()}"
        new_path = output_folder / new_name

        if args.output:
            shutil.copy2(img_path, new_path)
        else:
            # Avoid overwriting by renaming safely
            if new_path.exists() and new_path != img_path:
                temp_path = output_folder / f"temp_{idx}{img_path.suffix.lower()}"
                shutil.move(img_path, temp_path)
                img_path = temp_path
            img_path.rename(new_path)

    print(f"Processed {len(images)} images → saved to {output_folder}")


if __name__ == "__main__":
    main()
