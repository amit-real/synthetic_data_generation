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

def convert_to_coco(xmin, ymin, xmax, ymax):
    width = xmax - xmin
    height = ymax - ymin
    return [xmin, ymin, width, height], width * height

def process_coco_annotation(doc_type, json_path, img_name, img_path, annotations, images, image_id, annotation_id, img_width, img_height):
    with open(json_path, "r") as f:
        data = json.load(f)

    # Add image metadata
    prefixed_name = f"{doc_type}_{img_name}"
    images.append({
        "id": image_id,
        "file_name": prefixed_name,
        "width": img_width,
        "height": img_height
    })

    # Process annotations
    for key, value in data.items():
        class_id = get_class_id(key, value)
        bbox = value["bbox"]
        xmin, ymin, xmax, ymax = bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]
        coco_bbox, area = convert_to_coco(xmin, ymin, xmax, ymax)

        annotations.append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": class_id,
            "bbox": coco_bbox,
            "area": area,
            "iscrowd": 0
        })
        annotation_id += 1

    # Copy image to output directory with prefixed name
    coco_image_dir = os.path.join(output_dir, "images")
    os.makedirs(coco_image_dir, exist_ok=True)
    dest_image_path = os.path.join(coco_image_dir, prefixed_name)
    shutil.copy(img_path, dest_image_path)

    return annotation_id

# Directory traversal with simple counter
def traverse_and_convert_coco(root_dir, output_dir, img_width, img_height):
    annotations = []
    images = []
    annotation_id = 1
    image_id = 1

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
            annotation_id = process_coco_annotation(
                doc_type, json_path, img_name, img_path, annotations, images,
                image_id, annotation_id, img_width, img_height
            )
            image_id += 1

        # Update and print the simple counter
        processed_count += 1
        print(f"Processed {processed_count}/{total_files}")

    # Save COCO JSON file
    coco_output = {
        "images": images,
        "annotations": annotations,
        "categories": [
            {"id": 0, "name": "checkbox_unchecked"},
            {"id": 1, "name": "checkbox_checked"},
            {"id": 2, "name": "textfield"},
            {"id": 3, "name": "signature"}
            # {"id": 2, "name": "textfield_empty"},
            # {"id": 3, "name": "textfield_filled"}
        ]
    }
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "annotations.json"), "w") as f:
        json.dump(coco_output, f, indent=4)

    print("COCO conversion and image copying complete.")

# Configuration
root_dir = "augmented_images"  # Root directory of the nested folders
output_dir = "converted_coco"  # Output directory for COCO annotations and images
img_width, img_height = 2048, 2650  # Replace with your image dimensions

traverse_and_convert_coco(root_dir, output_dir, img_width, img_height)
