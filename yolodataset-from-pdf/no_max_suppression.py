"""
This script is used to remove overlapping boxes from YOLO label files.
"""

import os
import numpy as np
from glob import glob

def calculate_iou(box1, box2):
    """Calculate IoU between two YOLO format bounding boxes"""
    # Convert YOLO format (x_center, y_center, width, height) to coordinates
    x1_min = box1[0] - box1[2]/2
    y1_min = box1[1] - box1[3]/2
    x1_max = box1[0] + box1[2]/2
    y1_max = box1[1] + box1[3]/2

    x2_min = box2[0] - box2[2]/2
    y2_min = box2[1] - box2[3]/2
    x2_max = box2[0] + box2[2]/2
    y2_max = box2[1] + box2[3]/2

    # Calculate intersection area
    x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    intersection = x_overlap * y_overlap

    # Calculate union area
    box1_area = box1[2] * box1[3]
    box2_area = box2[2] * box2[3]
    union = box1_area + box2_area - intersection

    # Calculate IoU
    iou = intersection / union if union > 0 else 0
    return iou

def filter_overlapping_boxes(boxes):
    """Remove overlapping boxes with IOU > 0.5, keeping the largest one"""
    if not boxes:
        return []

    # Sort boxes by area (largest first)
    areas = [box[2] * box[3] for box in boxes]
    sorted_indices = np.argsort(areas)[::-1]
    sorted_boxes = [boxes[i] for i in sorted_indices]

    kept_boxes = []
    for box in sorted_boxes:
        should_keep = True

        for kept_box in kept_boxes:
            if calculate_iou(box, kept_box) > 0.5:
                should_keep = False
                break

        if should_keep:
            kept_boxes.append(box)

    return kept_boxes

def process_label_file(file_path):
    """Process a single YOLO label file to remove overlapping boxes"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Parse boxes from file
    boxes_by_class = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            class_id = int(parts[0])
            box = [float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])]

            if class_id not in boxes_by_class:
                boxes_by_class[class_id] = []

            boxes_by_class[class_id].append(box)

    # Filter boxes for each class
    filtered_boxes_by_class = {}
    for class_id, boxes in boxes_by_class.items():
        filtered_boxes_by_class[class_id] = filter_overlapping_boxes(boxes)

    # Write filtered boxes back to file
    with open(file_path, 'w') as f:
        for class_id, boxes in filtered_boxes_by_class.items():
            for box in boxes:
                f.write(f"{class_id} {box[0]} {box[1]} {box[2]} {box[3]}\n")

def remove_overlapping_bboxes(labels_dir):
    """Process all YOLO label files in the specified directory"""
    label_files = glob(os.path.join(labels_dir, "*.txt"))

    for file_path in label_files:
        process_label_file(file_path)

    print(f"Processed {len(label_files)} label files")

# Usage
if __name__ == "__main__":
    labels_dir = "../checkbox_dataset/labels/train"  # Change this to your labels directory path
    remove_overlapping_bboxes(labels_dir)

    labels_dir = "../checkbox_dataset/labels/val"  # Change this to your labels directory path
    remove_overlapping_bboxes(labels_dir)