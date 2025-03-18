import os
import json
import glob
import shutil
import random

def convert_to_yolo_format(json_path: str, img_path: str, output_dir: str, train_ratio: float = 0.8, val_ratio: float = 0.1):
    """
    Convert checkbox annotations from JSON to YOLO format and organize into train/val/test folders.
    """
    # Create output directories with train/val/test subfolders
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(output_dir, "labels", split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)

    # Get all JSON files recursively
    json_files = glob.glob(os.path.join(json_path, '**', '*.json'), recursive=True)

    # Shuffle files for random split
    random.shuffle(json_files)

    # Calculate split indices
    train_end = int(len(json_files) * train_ratio)
    val_end = train_end + int(len(json_files) * val_ratio)

    # Split into train, val, test
    splits = [
        ("train", json_files[:train_end]),
        ("val", json_files[train_end:val_end]),
        ("test", json_files[val_end:])
    ]

    # Class mapping: 0 for unchecked, 1 for checked
    class_dict = {
        "unchecked": 0,
        "checked": 1
    }

    # Process each split
    for split_name, files in splits:
        print(f"Processing {split_name} set ({len(files)} files)...")

        # Process each JSON file in the split
        for idx, json_file in enumerate(files):
            # Get relative path from json_path
            rel_path = os.path.relpath(json_file, json_path)
            # Construct corresponding image path
            img_file = os.path.join(img_path, os.path.splitext(rel_path)[0] + '.jpg')

            # Check if image exists (try different extensions if needed)
            if not os.path.exists(img_file):
                img_file = os.path.join(img_path, os.path.splitext(rel_path)[0] + '.png')
                if not os.path.exists(img_file):
                    print(f"Warning: No matching image found for {json_file}")
                    continue

            # Create a unique filename for the flat structure
            base_name = f"{idx:05d}"
            output_label = os.path.join(output_dir, "labels", split_name, f"{base_name}.txt")
            img_ext = os.path.splitext(img_file)[1]
            output_img = os.path.join(output_dir, "images", split_name, f"{base_name}{img_ext}")

            try:
                # Read and process JSON data
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Find image dimensions
                image_width = 0
                image_height = 0

                # Find all checkbox entries and convert coordinates
                yolo_annotations = []

                for key, value in data.items():
                    # Check if this is a checkbox (key starts with "<cb_")
                    if key.startswith("<cb_") and "data" in value:
                        checkbox_state = value["data"]

                        # Skip if not a checkbox state we're interested in
                        if checkbox_state not in class_dict:
                            continue

                        # Extract bounding box coordinates
                        xmin = float(value["xmin"])
                        ymin = float(value["ymin"])
                        xmax = float(value["xmax"])
                        ymax = float(value["ymax"])

                        # Update image dimensions based on bbox coordinates
                        image_width = max(image_width, xmax)
                        image_height = max(image_height, ymax)

                        # Store for later YOLO conversion
                        yolo_annotations.append((checkbox_state, xmin, ymin, xmax, ymax))

                # Skip if no valid image dimensions found
                if image_width == 0 or image_height == 0:
                    print(f"Warning: Invalid image dimensions for {json_file}")
                    continue

                # Convert to YOLO format and write to output file
                with open(output_label, 'w') as f:
                    for checkbox_state, xmin, ymin, xmax, ymax in yolo_annotations:
                        # YOLO format: class_id center_x center_y width height
                        # All values normalized to [0, 1]
                        x_center = (xmin + xmax) / 2.0 / image_width
                        y_center = (ymin + ymax) / 2.0 / image_height
                        width = (xmax - xmin) / image_width
                        height = (ymax - ymin) / image_height

                        class_id = class_dict[checkbox_state]
                        f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

                # Copy image to output directory
                shutil.copy(img_file, output_img)

                if (idx + 1) % 100 == 0:
                    print(f"Processed {idx + 1} files in {split_name} set...")

            except Exception as e:
                print(f"Error processing {json_file}: {e}")

        print(f"Completed {split_name} set: {len(files)} images")

def create_yaml_file(output_dir: str):
    """Create YAML configuration file for YOLOv5 with updated paths."""
    yaml_content = """# Checkbox dataset
path: .  # relative to where the yaml file is located
train: images/train
val: images/val
test: images/test

# Number of classes
nc: 2

# Class names
names:
  0: unchecked
  1: checked
"""
    with open(os.path.join(output_dir, 'checkbox.yaml'), 'w') as f:
        f.write(yaml_content)

if __name__ == "__main__":
    # Define paths
    base_dir = "/Users/shubham/Documents/codes/synthetic_data_generation/abr_dataset_from_annotated_pdf/OUT_DIR/2_syn_generated"
    img_dir = os.path.join(base_dir, "imgs")
    json_dir = os.path.join(base_dir, "json")
    output_dir = "/Users/shubham/Documents/codes/synthetic_data_generation/abr_dataset_from_annotated_pdf/OUT_DIR/yolo_dataset"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Starting conversion...")
    # Convert to YOLO format and create dataset splits in one function
    convert_to_yolo_format(json_dir, img_dir, output_dir)

    print("Creating YAML configuration file...")
    # Create YAML file for YOLOv5
    create_yaml_file(output_dir)

    print(f"Conversion complete. YOLO format dataset created at: {output_dir}")