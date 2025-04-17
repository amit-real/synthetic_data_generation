import os
import random
import cv2
import json

# Configuration
coco_dir = "split_coco"  # Directory containing COCO train and val datasets
num_samples = 500  # Number of samples to visualize

# Class names
class_names = [
    "checkbox_unchecked",
    "checkbox_checked",
    "textfield",
    "signature"
]

# Define colors
colors = {
    "checkbox_unchecked": (0, 0, 255),  # Red
    "checkbox_checked": (0, 255, 0),    # Green
    "textfield": (255, 0, 0),           # Blue
    "signature": (255, 255, 0)          # Cyancd
}

# Function to plot bounding boxes and save images
def plot_image_with_boxes(image_path, boxes, output_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    for box in boxes:
        class_id, xmin, ymin, width, height = box
        xmax = xmin + width
        ymax = ymin + height

        # Choose color based on class
        label = class_names[class_id]
        color = colors[label]

        # Draw bounding box and label
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save the plotted image
    cv2.imwrite(output_path, image)
    print(f"Saved: {output_path}")

# Visualize random samples from COCO format
def visualize_coco(split):
    annotation_path = os.path.join(coco_dir, 'annotations', f"{split}.json")
    output_dir = f"visualizations/coco/{split}"
    os.makedirs(output_dir, exist_ok=True)

    with open(annotation_path, "r") as f:
        data = json.load(f)

    random_images = random.sample(data["images"], min(len(data["images"]), num_samples))

    for image_info in random_images:
        image_id = image_info["id"]
        image_path = os.path.join(coco_dir, "images",split, image_info["file_name"])

        # Collect annotations for this image
        boxes = []
        for annotation in data["annotations"]:
            if annotation["image_id"] == image_id:
                class_id = annotation["category_id"]
                xmin, ymin, width, height = map(int, annotation["bbox"])
                boxes.append((class_id, xmin, ymin, width, height))

        output_path = os.path.join(output_dir, f"vis_{image_info['file_name']}")
        plot_image_with_boxes(image_path, boxes, output_path)

# Run visualization for both train and val sets
visualize_coco("train")
visualize_coco("val")
