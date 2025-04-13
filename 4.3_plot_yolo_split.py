import os
import random
import cv2

# Configuration
yolo_dir = "split_yolo"  # Directory containing YOLO train and val datasets
num_samples = 500  # Number of samples to visualize

# Class names
class_names = [
    "checkbox_unchecked",
    "checkbox_checked",
    "textfield",
    # "signature"
]

# Define colors
colors = {
    "checkbox_unchecked": (0, 0, 255),  # Red
    "checkbox_checked": (0, 255, 0),    # Green
    "textfield": (255, 0, 0),           # Blue
    "signature": (255, 255, 0)          # Cyan
    # "textfield_empty": (0, 255, 0),     # Red
    # "textfield_filled": (0, 255, 0)     # Green
}

# Function to plot bounding boxes and save images
def plot_image_with_boxes(image_path, boxes, output_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    for box in boxes:
        class_id, x_center, y_center, width, height = box
        img_height, img_width = image.shape[:2]

        # Convert from normalized YOLO format to pixel coordinates
        xmin = int((x_center - width / 2) * img_width)
        ymin = int((y_center - height / 2) * img_height)
        xmax = int((x_center + width / 2) * img_width)
        ymax = int((y_center + height / 2) * img_height)

        # Choose color based on class
        label = class_names[class_id]
        color = colors[label]

        # Draw bounding box and label
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save the plotted image
    cv2.imwrite(output_path, image)
    print(f"Saved: {output_path}")

# Visualize random samples from YOLO format
def visualize_yolo(split):
    label_dir = os.path.join(yolo_dir, split, "labels")
    image_dir = os.path.join(yolo_dir, split, "images")
    output_dir = f"visualizations/yolo/{split}"
    os.makedirs(output_dir, exist_ok=True)

    label_files = [f for f in os.listdir(label_dir) if f.endswith(".txt")]
    random_files = random.sample(label_files, min(len(label_files), num_samples))

    for label_file in random_files:
        image_path = os.path.join(image_dir, label_file.replace(".txt", ".jpg"))
        label_path = os.path.join(label_dir, label_file)

        boxes = []
        with open(label_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
                boxes.append((class_id, x_center, y_center, width, height))

        output_path = os.path.join(output_dir, f"vis_{label_file.replace('.txt', '.jpg')}")
        plot_image_with_boxes(image_path, boxes, output_path)

# Run visualization for both train and val sets
visualize_yolo("train")
visualize_yolo("val")
