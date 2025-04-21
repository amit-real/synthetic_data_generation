import os
import json
import shutil
import cv2

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

def convert_to_coco(xmin, ymin, xmax, ymax):
    width = xmax - xmin
    height = ymax - ymin
    return [xmin, ymin, width, height], width * height

def process_coco_annotation(doc_type, json_path, img_name, img_path,
                            annotations, images,
                            image_id, annotation_id,
                            img_width, img_height,
                            output_dir):
    """
    Reads the JSON, appends image + annotation entries to the COCO structures,
    and copies the image to 'output_dir/images' with a doc_type prefix.
    """
    with open(json_path, "r") as f:
        widgets = json.load(f)

    # Add image metadata
    prefixed_name = f"{doc_type}_{img_name}"
    images.append({
        "id": image_id,
        "file_name": prefixed_name,
        "width": img_width,
        "height": img_height
    })

    # Process annotations
    for widget_name, widget_dict in widgets.items():
        class_id = get_class_id(widget_dict)
        if class_id is None:
            continue
        
        bbox = widget_dict["bbox"]
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

def traverse_and_convert_coco(root_dir, output_dir):
    """
    Traverses 'root_dir' looking for JSON files and matching images,
    creates COCO-style annotations, and writes them to 'output_dir'.
    """
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

    processed_count = 0
    for json_path in json_files:
        parts = json_path.split(os.sep)
        doc_type = parts[-3]
        img_name = os.path.basename(json_path).replace(".json", ".jpg")
        img_dir = json_path.replace("json", "image").rsplit("/", 1)[0]
        img_path = os.path.join(img_dir, img_name)

        if not os.path.exists(img_path):
            print(f"Warning: Image not found for JSON: {json_path}")
            continue

        # Read image to get actual width/height
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not open image: {img_path}")
            continue

        img_height, img_width = img.shape[:2]

        # Process COCO annotation
        annotation_id = process_coco_annotation(
            doc_type, json_path, img_name, img_path,
            annotations, images,
            image_id, annotation_id,
            img_width, img_height,
            output_dir
        )
        image_id += 1

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
        ]
    }
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "annotations.json"), "w") as f:
        json.dump(coco_output, f, indent=4)

    print("COCO conversion and image copying complete.")

# Configuration
root_dir = "out_2_augmented_images"  # Root directory containing doc-type folders, images, and JSON
output_dir = "out_3.1_converted_coco"  # Where COCO annotations + prefixed images will go

traverse_and_convert_coco(root_dir, output_dir)
