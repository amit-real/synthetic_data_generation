import os
import json
import shutil
import random

# Configuration
coco_dir = "converted_coco"  # Directory containing COCO images and annotations
output_dir = "split_coco"  # Directory to save the split datasets
shutil.rmtree(output_dir, ignore_errors=True)  # Clear previous output
os.makedirs(output_dir)  # Create output directory

train_ratio = 0.8  # Ratio for train split

# Create split directories
def create_split_dirs():
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)

# Split files into train and validation sets
def split_files(image_list):
    random.shuffle(image_list)
    train_count = int(len(image_list) * train_ratio)
    train_images = image_list[:train_count]
    val_images = image_list[train_count:]
    return train_images, val_images

# Filter annotations based on image IDs
def filter_annotations(images, all_annotations):
    image_ids = {img["id"] for img in images}
    return [ann for ann in all_annotations if ann["image_id"] in image_ids]

# Split and move COCO files
def split_coco_files():
    print("Splitting COCO files...")
    image_dir = os.path.join(coco_dir, "images")
    annotation_path = os.path.join(coco_dir, "annotations.json")

    with open(annotation_path, "r") as f:
        data = json.load(f)

    # Split images into train and validation sets
    train_images, val_images = split_files(data["images"])

    for split, images in zip(['train', 'val'], [train_images, val_images]):
        # Create split annotations
        split_annotations = {
            "images": images,
            "annotations": filter_annotations(images, data["annotations"]),
            "categories": data["categories"]
        }

        # Save split annotations
        split_annotation_path = os.path.join(output_dir, f"{split}.json")
        with open(split_annotation_path, "w") as f:
            json.dump(split_annotations, f, indent=4)

        # Copy images to respective directories
        for image_info in images:
            img_name = image_info["file_name"]
            img_src = os.path.join(image_dir, img_name)
            img_dest = os.path.join(output_dir, "images", split, img_name)
            shutil.copy(img_src, img_dest)

    print("COCO dataset splitting complete.")

# Run the script
create_split_dirs()
split_coco_files()
