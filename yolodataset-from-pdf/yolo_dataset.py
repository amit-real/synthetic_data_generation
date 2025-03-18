import os
import cv2
from typing import List, Tuple


def create_dataset_dirs(base_dir: str) -> Tuple[str, str]:
    """
    Create directories for YOLO dataset.

    Args:
        base_dir: Base directory for the dataset

    Returns:
        Tuple containing (image_dir, label_dir)
    """
    image_dir = os.path.join(base_dir, "images")
    label_dir = os.path.join(base_dir, "labels")

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    return image_dir, label_dir


def create_yolo_annotation(detection: Tuple, img_width: int, img_height: int) -> str:
    """
    Convert a detection to YOLO format.

    Args:
        detection: Tuple (class_id, x1, y1, x2, y2, confidence)
        img_width: Width of the image
        img_height: Height of the image

    Returns:
        YOLO format annotation string
    """
    class_id, x1, y1, x2, y2, _ = detection

    # Convert to YOLO format (normalized)
    center_x = ((x1 + x2) / 2) / img_width
    center_y = ((y1 + y2) / 2) / img_height
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height

    # Ensure values are within [0, 1]
    center_x = max(0, min(1, center_x))
    center_y = max(0, min(1, center_y))
    width = max(0, min(1, width))
    height = max(0, min(1, height))

    return f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"


def save_detection(image: cv2.Mat,
                   detections: List[Tuple],
                   image_dir: str,
                   label_dir: str,
                   image_id: int) -> bool:
    """
    Save an image and its annotations in YOLO format.

    Args:
        image: OpenCV image
        detections: List of detections
        image_dir: Directory to save images
        label_dir: Directory to save labels
        image_id: Unique ID for the image

    Returns:
        True if saved successfully, False otherwise
    """
    if not detections:
        return False

    try:
        # Save image
        img_filename = f"{image_id}.png"
        img_path = os.path.join(image_dir, img_filename)
        cv2.imwrite(img_path, image)

        # Create and save YOLO annotations
        height, width = image.shape[:2]
        yolo_annotations = [create_yolo_annotation(detection, width, height)
                            for detection in detections]

        label_filename = f"{image_id}.txt"
        label_path = os.path.join(label_dir, label_filename)
        with open(label_path, 'w') as f:
            f.write('\n'.join(yolo_annotations))

        return True
    except Exception as e:
        print(f"Error saving detection {image_id}: {str(e)}")
        return False


def create_dataset_yaml(dataset_dir: str, total_images: int) -> None:
    """
    Create a YOLO training compatible dataset.yaml file.

    Args:
        dataset_dir: Directory containing the dataset
        total_images: Total number of images in the dataset
    """
    # Calculate train/val split (80/20)
    train_images = int(total_images * 0.8)

    # Create list of training and validation images
    train_list = [f"{i}.png" for i in range(train_images)]
    val_list = [f"{i}.png" for i in range(train_images, total_images)]

    # Create dataset.yaml
    with open(os.path.join(dataset_dir, "dataset.yaml"), 'w') as f:
        f.write("# Checkbox detection dataset\n")
        f.write(f"path: {dataset_dir}\n")
        f.write("train: images/train.txt\n")
        f.write("val: images/val.txt\n")
        f.write("\n")
        f.write("# Classes\n")
        f.write("names:\n")
        f.write("  0: checked\n")
        f.write("  1: unchecked\n")

    # Make sure the directory exists
    os.makedirs(os.path.join(dataset_dir, "images"), exist_ok=True)

    # Create train.txt and val.txt files with the list of images
    with open(os.path.join(dataset_dir, "images/train.txt"), 'w') as f:
        f.write('\n'.join([os.path.join(dataset_dir, "images", img) for img in train_list]))

    with open(os.path.join(dataset_dir, "images/val.txt"), 'w') as f:
        f.write('\n'.join([os.path.join(dataset_dir, "images", img) for img in val_list]))