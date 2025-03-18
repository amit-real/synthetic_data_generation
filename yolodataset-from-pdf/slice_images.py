import os
import cv2
import numpy as np
import shutil
import math
from pathlib import Path
import argparse
from tqdm import tqdm


def slice_image(image: np.ndarray, slice_size: tuple, overlap_prcnt: float) -> dict:
    """Slice an image into smaller chunks with specified overlap"""
    height, width, *_ = image.shape
    stride_x = math.ceil(slice_size[0] * (1 - overlap_prcnt))
    stride_y = math.ceil(slice_size[1] * (1 - overlap_prcnt))

    main_dict = {
        "img_w_orig": width,
        "img_h_orig": height,
        "stride_x": stride_x,
        "stride_y": stride_y,
    }
    img_slices = []
    for y in range(0, height, stride_y):
        for x in range(0, width, stride_x):
            tmp_dict = {}
            xmin, ymin, xmax, ymax = (
                x,
                y,
                min(x + slice_size[0], width),
                min(y + slice_size[1], height),
            )

            slice_img = image[ymin:ymax, xmin:xmax]
            tmp_dict["xmin"], tmp_dict["ymin"], tmp_dict["xmax"], tmp_dict["ymax"] = (
                xmin,
                ymin,
                xmax,
                ymax,
            )
            # Pad if necessary
            h, w, *_ = slice_img.shape
            if h < slice_size[1] or w < slice_size[0]:
                padded_img = np.zeros((slice_size[1], slice_size[0], 3), dtype=np.uint8)
                padded_img[:h, :w] = slice_img
                slice_img = padded_img
            tmp_dict["img"] = slice_img
            img_slices.append(tmp_dict)
    main_dict["img_slices"] = img_slices
    return main_dict


def resize_image(image, target_width=2048):
    """Resize image to target width while maintaining aspect ratio"""
    h, w = image.shape[:2]
    new_w = target_width
    new_h = int(h * (new_w / w))
    return cv2.resize(image, (new_w, new_h))


def convert_yolo_coordinates(box, img_width, img_height, slice_xmin, slice_ymin, slice_width, slice_height):
    """
    Convert YOLO format bounding box coordinates to fit within a slice

    YOLO format: [class_id, x_center, y_center, width, height] (normalized)
    """
    class_id, x_center, y_center, width, height = box

    # Denormalize the coordinates to actual pixel values
    x_center = x_center * img_width
    y_center = y_center * img_height
    width = width * img_width
    height = height * img_height

    # Adjust coordinates to be relative to the slice
    x_center = x_center - slice_xmin
    y_center = y_center - slice_ymin

    # Check if the bounding box is within the slice
    # A box is within the slice if its center is within the slice
    if (0 <= x_center < slice_width) and (0 <= y_center < slice_height):
        # Clip the bounding box to fit within the slice
        bbox_xmin = max(0, x_center - width / 2)
        bbox_ymin = max(0, y_center - height / 2)
        bbox_xmax = min(slice_width, x_center + width / 2)
        bbox_ymax = min(slice_height, y_center + height / 2)

        # Calculate new width and height
        new_width = bbox_xmax - bbox_xmin
        new_height = bbox_ymax - bbox_ymin

        # Skip tiny boxes
        if new_width <= 1 or new_height <= 1:
            return None

        # Calculate new center coordinates
        new_x_center = (bbox_xmin + bbox_xmax) / 2
        new_y_center = (bbox_ymin + bbox_ymax) / 2

        # Normalize the coordinates again
        new_x_center /= slice_width
        new_y_center /= slice_height
        new_width /= slice_width
        new_height /= slice_height

        return [class_id, new_x_center, new_y_center, new_width, new_height]

    return None


def process_dataset(dataset_path, output_path, slice_sizes=[(1024, 1024), (684, 684), (1296, 1296)], overlap=0.2):
    """Process the YOLO dataset by resizing and slicing images, adjusting labels accordingly"""
    dataset_path = Path(dataset_path)
    output_path = Path(output_path)

    # Create output directory structure for a single dataset
    os.makedirs(output_path / "images" / "train", exist_ok=True)
    os.makedirs(output_path / "images" / "val", exist_ok=True)
    os.makedirs(output_path / "labels" / "train", exist_ok=True)
    os.makedirs(output_path / "labels" / "val", exist_ok=True)

    # Copy and modify the dataset.yaml file
    try:
        yaml_path = next(dataset_path.glob("*.yaml"))
        shutil.copy(yaml_path, output_path / "dataset.yaml")
    except StopIteration:
        print("No YAML file found in the dataset directory. Creating a new one.")
        with open(output_path / "dataset.yaml", "w") as f:
            f.write(f"# Checkbox detection dataset - Multiple resolution slices\n")
            f.write(f"path: {str(output_path.absolute())}\n")
            f.write("train: images/train\n")
            f.write("val: images/val\n")
            f.write("# Classes\n")
            f.write("names:\n")
            f.write("  0: checked\n")
            f.write("  1: unchecked\n")

    # Process train and validation sets
    for subset in ["train", "val"]:
        # Get all image files
        img_dir = dataset_path / "images" / subset
        label_dir = dataset_path / "labels" / subset

        img_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png"))

        print(f"Processing {subset} set: {len(img_files)} images")

        for img_file in tqdm(img_files):
            # Read image
            img = cv2.imread(str(img_file))
            if img is None:
                print(f"Couldn't read {img_file}. Skipping.")
                continue

            # Resize image
            resized_img = resize_image(img, target_width=2048)

            # Get corresponding label file
            label_file = label_dir / f"{img_file.stem}.txt"

            if not label_file.exists():
                print(f"No label file for {img_file}. Skipping.")
                continue

            # Read labels
            with open(label_file, 'r') as f:
                boxes = []
                for line in f:
                    values = line.strip().split()
                    if len(values) == 5:
                        boxes.append([int(values[0]), float(values[1]), float(values[2]),
                                      float(values[3]), float(values[4])])

            # Set output directories
            out_img_dir = output_path / "images" / subset
            out_label_dir = output_path / "labels" / subset

            # Process each slice size
            for size_idx, slice_size in enumerate(slice_sizes):
                # Create a size identifier
                size_id = f"{slice_size[0]}x{slice_size[1]}"

                # Slice the image
                sliced_data = slice_image(resized_img, slice_size, overlap)

                # Process each slice
                for slice_idx, slice_info in enumerate(sliced_data["img_slices"]):
                    slice_img = slice_info["img"]
                    xmin, ymin = slice_info["xmin"], slice_info["ymin"]
                    slice_width, slice_height = slice_size

                    # Ensure the slice is the correct size
                    h, w = slice_img.shape[:2]
                    if h != slice_size[1] or w != slice_size[0]:
                        # Skip slices that don't match the expected size after padding
                        continue

                    # Create a unique filename for this slice
                    out_filename = f"{img_file.stem}_{size_id}_{slice_idx}"

                    # Save the slice image
                    out_img_path = out_img_dir / f"{out_filename}.jpg"
                    cv2.imwrite(str(out_img_path), slice_img)

                    # Adjust the bounding boxes for this slice
                    slice_boxes = []
                    for box in boxes:
                        adjusted_box = convert_yolo_coordinates(
                            box,
                            sliced_data["img_w_orig"],
                            sliced_data["img_h_orig"],
                            xmin,
                            ymin,
                            slice_width,
                            slice_height
                        )
                        if adjusted_box:
                            slice_boxes.append(adjusted_box)

                    # Only save slices with at least one box
                    if slice_boxes:
                        # Write the adjusted labels
                        out_label_path = out_label_dir / f"{out_filename}.txt"
                        with open(out_label_path, 'w') as f:
                            for box in slice_boxes:
                                f.write(f"{int(box[0])} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f} {box[4]:.6f}\n")
                    else:
                        # Remove the image if no valid boxes
                        if out_img_path.exists():
                            os.remove(out_img_path)



if __name__ == "__main__":

    dataset = "/Users/shubham/Documents/codes/synthetic_data_generation/checkbox_dataset"
    output = "/Users/shubham/Documents/codes/synthetic_data_generation/sliced_checkbox_dataset"
    overlap = 0.2

    #delete output dir
    shutil.rmtree(output, ignore_errors=True)

    # Standard slice sizes
    slice_sizes = [(1024, 1024), (684, 684), (1296, 1296)]

    process_dataset(dataset, output, slice_sizes, overlap)

    print("Dataset processing complete!")