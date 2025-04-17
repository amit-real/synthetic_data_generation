import os
import json
import shutil
import cv2  # <-- For reading image dimensions

# Define class mappings
class_mapping = {
    "checkbox_unchecked": 0,
    "checkbox_checked": 1,
    "textfield": 2,
    "signature": 3
}

def get_class_id(widget):
    if widget['widget_type']=='checkbox':
        if widget['state']=='unchecked':
            return class_mapping['checkbox_unchecked']
        if widget['state']=='checked':
            return class_mapping['checkbox_checked']
        
    if widget['widget_type']=='textfield':
        return class_mapping['textfield']
    
    if widget['widget_type']=='signature':
        return class_mapping['signature']
    
    return None

def convert_to_yolo(xmin, ymin, xmax, ymax, img_width, img_height):
    x_center = ((xmin + xmax) / 2) / img_width
    y_center = ((ymin + ymax) / 2) / img_height
    width = (xmax - xmin) / img_width
    height = (ymax - ymin) / img_height
    return x_center, y_center, width, height

def process_yolo_annotation(
    doc_type,
    json_path,
    img_name,
    img_path,
    output_dir
):
    """Reads the JSON, converts bboxes to YOLO format, 
    and writes .txt + image with doc_type prefix."""
    # Read image dimensions dynamically
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error reading image {img_path}. Skipping...")
        return
    img_height, img_width = img.shape[:2]

    # Load JSON
    with open(json_path, "r") as f:
        widgets = json.load(f)

    yolo_lines = []
    for widget_name, widget_dict in widgets.items():
        class_id = get_class_id(widget_dict)
        if class_id is None:
            continue
        
        bbox = widget_dict["bbox"]
        xmin, ymin, xmax, ymax = bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]

        # Convert to YOLO format
        x_center, y_center, width, height = convert_to_yolo(xmin, ymin, xmax, ymax, img_width, img_height)
        yolo_line = f"{class_id} {x_center} {y_center} {width} {height}\n"
        yolo_lines.append(yolo_line)

    # Add document type prefix to file names
    # e.g. "invoice_<filename>.jpg"
    prefixed_name = f"{doc_type}_{os.path.splitext(img_name)[0]}"

    # Save YOLO annotation file
    yolo_annot_dir = os.path.join(output_dir, "labels")
    yolo_image_dir = os.path.join(output_dir, "images")
    os.makedirs(yolo_annot_dir, exist_ok=True)
    os.makedirs(yolo_image_dir, exist_ok=True)

    # Write annotation file
    yolo_output_path = os.path.join(yolo_annot_dir, f"{prefixed_name}.txt")
    with open(yolo_output_path, "w") as f:
        f.writelines(yolo_lines)

    # Copy image to the YOLO output directory with prefixed name
    dest_image_path = os.path.join(yolo_image_dir, f"{prefixed_name}.jpg")
    shutil.copy(img_path, dest_image_path)

def traverse_and_convert_yolo(root_dir, output_dir):
    """Traverses root_dir looking for JSON files, 
    finds corresponding images, and converts bounding boxes to YOLO."""
    # Collect all JSON file paths
    json_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):
                json_path = os.path.join(dirpath, file)
                json_files.append(json_path)

    total_files = len(json_files)
    print(f"Found {total_files} JSON files to process.")

    processed_count = 0
    for json_path in json_files:
        parts = json_path.split(os.sep)
        # e.g. augmented_images/<doc_type>/json/file.json
        # doc_type is typically parts[-3], but adjust as needed for your structure
        doc_type = parts[-3]

        img_name = os.path.basename(json_path).replace(".json", ".jpg")
        img_dir = json_path.replace("json", "image").rsplit("/", 1)[0]
        img_path = os.path.join(img_dir, img_name)

        if not os.path.exists(img_path):
            print(f"Image file not found for {json_path}. Skipping...")
            continue

        process_yolo_annotation(doc_type, json_path, img_name, img_path, output_dir)

        processed_count += 1
        print(f"Processed {processed_count}/{total_files}")

# Configuration
root_dir = "augmented_images"
output_dir = "converted_yolo"

# Clear previous output
shutil.rmtree(output_dir, ignore_errors=True)
os.makedirs(output_dir)

# Convert
traverse_and_convert_yolo(root_dir, output_dir)
print("YOLO conversion complete.")
