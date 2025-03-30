import os
import json
import shutil

# Define class mappings
class_mapping = {
    "checkbox_unchecked": 0,
    "checkbox_checked": 1,
    "textfield": 2,
    "signature": 3
    # "textfield_empty": 2,
    # "textfield_filled": 3
}

def get_class_id(key, value):
    if "<cb_" in key:
        return class_mapping["checkbox_checked"] if value["state"] == "checked" else class_mapping["checkbox_unchecked"]
    elif "<SIGN_" in key:
        return class_mapping["signature"]
    else:
        # return class_mapping["textfield_filled"] if len(value["value"])>0 else class_mapping["textfield_empty"]
        return class_mapping["textfield"]
    
def convert_to_yolo(xmin, ymin, xmax, ymax, img_width, img_height):
    x_center = ((xmin + xmax) / 2) / img_width
    y_center = ((ymin + ymax) / 2) / img_height
    width = (xmax - xmin) / img_width
    height = (ymax - ymin) / img_height
    return x_center, y_center, width, height

def process_yolo_annotation(doc_type, json_path, img_name, img_path, img_width, img_height, output_dir):
    with open(json_path, "r") as f:
        data = json.load(f)

    yolo_lines = []
    for key, value in data.items():
        class_id = get_class_id(key, value)
        bbox = value["bbox"]
        xmin, ymin, xmax, ymax = bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]

        # Convert to YOLO format
        x_center, y_center, width, height = convert_to_yolo(xmin, ymin, xmax, ymax, img_width, img_height)
        yolo_line = f"{class_id} {x_center} {y_center} {width} {height}\n"
        yolo_lines.append(yolo_line)

    # Add document type prefix to file names
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

# Directory traversal with simple counter
def traverse_and_convert_yolo(root_dir, output_dir, img_width, img_height):
    # Collect all JSON file paths
    json_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):
                json_path = os.path.join(dirpath, file)
                json_files.append(json_path)

    total_files = len(json_files)
    print(f"Found {total_files} JSON files to process.")

    # Process files with simple counter
    processed_count = 0
    for json_path in json_files:
        parts = json_path.split(os.sep)
        doc_type = parts[-3]  # Extract the document type from the parent folder
        img_name = os.path.basename(json_path).replace(".json", ".jpg")
        img_path = os.path.join(json_path.replace("json", "image").rsplit("/", 1)[0], img_name)

        if os.path.exists(img_path):
            process_yolo_annotation(doc_type, json_path, img_name, img_path, img_width, img_height, output_dir)

        # Update and print the simple counter
        processed_count += 1
        print(f"Processed {processed_count}/{total_files}")

# Configuration
root_dir = "augmented_images"
output_dir = "converted_yolo"
shutil.rmtree(output_dir, ignore_errors=True)  # Clear previous output
os.makedirs(output_dir)

img_width, img_height = 2048, 2650

traverse_and_convert_yolo(root_dir, output_dir, img_width, img_height)
print("YOLO conversion complete.")
