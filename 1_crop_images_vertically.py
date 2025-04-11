import os
import cv2
import json
import random
from pathlib import Path
import shutil

def crop_image_vertically(image, crop_height):
    """
    Crop the image into multiple vertical tiles, each of height 'crop_height',
    with random overlap controlled by 'shift'.
    Returns a list of (cropped_image, offset_y, shift).
    """
    img_h, img_w = image.shape[:2]
    crops = []
    y = 0
    while y < img_h:
        # Random shift for overlap
        shift = random.randint(int(0.01 * img_h), int(0.1 * img_h))

        # Crop from y to y + crop_height
        cropped = image[y : y + crop_height, :]

        # Append: (the cropped tile, the top offset y, and shift)
        crops.append((cropped, y, shift))

        # Move 'y' downward, leaving some overlap
        y += max(1, crop_height - shift)

        # If we're near the end, do one final crop to avoid any leftover portion
        if y >= img_h - crop_height:
            final_offset = img_h - crop_height
            # If final_offset < 0, it means the image is smaller than crop_height
            if final_offset < 0:
                final_offset = 0
            cropped = image[final_offset : final_offset + crop_height, :]
            crops.append((cropped, final_offset, 0))
            break

    return crops


def adjust_bboxes_single(widget_dict, offset_y, crop_height, visibility=0.5):
    ymin, ymax = widget_dict['bbox']['ymin'], widget_dict['bbox']['ymax']
    
    if widget_dict['widget_type']=='textfield':
        if ymax<offset_y or ymax>offset_y+crop_height: # if the underline of the textfield is not visible, then skip
            return []
    
    bbox_height = ymax - ymin

    # Intersection with the crop [offset_y, offset_y + crop_height]
    intersection_ymin = max(ymin, offset_y)
    intersection_ymax = min(ymax, offset_y + crop_height)
    visible_height = max(0, intersection_ymax - intersection_ymin)

    # If at least 'visibility'% of the bbox is present, include it
    if bbox_height > 0 and (visible_height / bbox_height) >= visibility:
        new_bbox = widget_dict['bbox'].copy()

        # Shift bbox coords relative to top of crop
        new_bbox['ymin'] = intersection_ymin - offset_y
        new_bbox['ymax'] = intersection_ymax - offset_y

        # Clamp within [0, crop_height]
        new_bbox['ymin'] = max(0, new_bbox['ymin'])
        new_bbox['ymax'] = min(crop_height, new_bbox['ymax'])

        return [new_bbox]
    else:
        return []

def adjust_widget_bboxes(widgets, offset_y, crop_height):
    updated = {}
    for widget_name, widget_dict in widgets.items():
        #TODO: handle signatures
        # if widget_name == 'SIGNATURES' and isinstance(widget_dict, list):
        #     # 'SIGNATURES' is a list of bounding boxes
        #     new_signatures = []
        #     for sign_bbox in widget_dict:
        #         adjusted_list = adjust_bboxes_single(sign_bbox, offset_y, crop_height, visibility=0.5)
        #         if adjusted_list:  # We have an adjusted box that meets threshold
        #             new_signatures.append(adjusted_list[0])
        #     if new_signatures:
        #         updated[widget_name] = new_signatures

        # else:
        # Normal single bounding box: 'bbox'
        if 'bbox' in widget_dict:
            adjusted_list = adjust_bboxes_single(widget_dict, offset_y, crop_height, visibility=0.5)
            if adjusted_list:
                # Keep the rest of 'value' but override 'bbox'
                new_value = widget_dict.copy()
                new_value['bbox'] = adjusted_list[0]
                updated[widget_name] = new_value
        else:
            # If there's no 'bbox' field, keep the entry as-is (or skip)
            updated[widget_name] = widget_dict

    return updated

def process_image(image_path, json_path, out_dir, crop_height):
    """
    Reads the image and JSON, performs vertical cropping, and writes out
    the cropped images and their updated JSON files.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Could not read image: {image_path}")
        return

    with open(json_path, 'r') as f:
        widgets = json.load(f)

    # Derive output subdirectories
    img_rel_path = image_path.relative_to(src_dir).parent
    json_rel_path = json_path.relative_to(src_dir).parent
    img_out_dir = out_dir / img_rel_path
    json_out_dir = out_dir / json_rel_path

    os.makedirs(img_out_dir, exist_ok=True)
    os.makedirs(json_out_dir, exist_ok=True)

    # Perform crops
    crops = crop_image_vertically(image, crop_height)

    base_name = image_path.stem
    for i, (crop, offset_y, shift) in enumerate(crops):
        crop_name = f"{base_name}_crop_{i}.jpg"
        crop_path = img_out_dir / crop_name
        cv2.imwrite(str(crop_path), crop)

        # Adjust the bounding boxes for this specific crop
        updated_widgets = adjust_widget_bboxes(widgets, offset_y, crop_height)

        # Save updated JSON
        json_name = f"{base_name}_crop_{i}.json"
        json_path = json_out_dir / json_name
        with open(json_path, 'w') as f:
            json.dump(updated_widgets, f, indent=4)

# -----------------------------
# Main Script
# -----------------------------
src_dir = Path('out')
out_dir = Path('out_cropped_vertically')

# Remove old outputs, create fresh directory
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir, exist_ok=True)

CROP_HEIGHT = 1024

# Gather all images
image_paths = list(src_dir.rglob('*.jpg'))
image_paths = [i for i in image_paths if '/plot/' not in str(i)]

for idx, image_path in enumerate(image_paths):
    print(f'Processing {idx + 1}/{len(image_paths)}: {image_path}')
    
    json_path = Path(str(image_path).replace('/image/', '/json/').replace('.jpg', '.json'))
        
    if json_path.exists():
        process_image(image_path, json_path, out_dir, CROP_HEIGHT)
    else:
        print(f"No JSON found for {image_path}")
