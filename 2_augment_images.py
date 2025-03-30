import os, shutil
import cv2
import json
import random
from pathlib import Path
import albumentations as A

# Augmentation pipeline
import albumentations as A

transforms = A.Compose([
    A.HorizontalFlip(p=0.3),
    A.Perspective(scale=(0.05, 0.1), p=0.5),
    A.GridDistortion(num_steps=5, distort_limit=0.2, p=0.5),
    A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
    A.GaussianBlur(blur_limit=(3, 7), p=0.3),
    # Shadow with lighter range
    A.RandomShadow(
        shadow_gray_value=(120, 180),  # lighten shadows
        p=0.5
    ),
    A.InvertImg(p=0.2),
    # Limit rotation angle
    A.ShiftScaleRotate(
        shift_limit=0.1,
        scale_limit=0.1,
        rotate_limit=3,   # smaller rotation
        p=0.5
    ),
    A.RandomBrightnessContrast(p=0.3),
    A.RGBShift(r_shift_limit=30, g_shift_limit=30, b_shift_limit=30, p=0.3),
],
bbox_params=A.BboxParams(format='pascal_voc',
                         label_fields=['category_ids'],
                         min_visibility=0.4)
)


def augment_image(image, bboxes, category_ids):
    return transforms(image=image, bboxes=bboxes, category_ids=category_ids)

def process_augmentation(image_path, json_path, out_img_path, out_json_path):
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Could not load image: {image_path}")
        return
    
    with open(json_path, 'r') as f:
        annotations = json.load(f)
    
    # original_data will hold each annotation's key and its bounding box
    # We'll assign a unique numeric ID to each bounding box for label matching
    original_data = []
    for i, (key, value) in enumerate(annotations.items()):
        bbox = value['bbox']
        original_data.append({
            'id': i,             # Unique bounding box ID
            'key': key,          # The annotation key (e.g., "<cb_2>")
            'bbox': [bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']],
        })
    
    # Prepare lists for Albumentations
    bboxes = [item['bbox'] for item in original_data]
    category_ids = [item['id'] for item in original_data]  # use numeric IDs
    
    # Randomly apply augmentation
    if random.random() < 0.5:  # 50% probability
        augmented = augment_image(image, bboxes, category_ids)
        aug_image = augmented['image']
        aug_bboxes = augmented['bboxes']
        aug_labels = augmented['category_ids']
    else:
        aug_image = image
        aug_bboxes = bboxes
        aug_labels = category_ids
    
    # Rebuild annotations based on the new bounding boxes
    updated_annotations = {}
    for bbox, bbox_id in zip(aug_bboxes, aug_labels):
        bbox_id = int(bbox_id)  # <-- Cast to int
        orig_item = original_data[bbox_id]
        
        # Create or update the annotation
        updated_annotations[orig_item['key']] = annotations[orig_item['key']]
        # Overwrite with the new bounding box
        updated_annotations[orig_item['key']]['bbox'] = {
            'xmin': int(bbox[0]),
            'ymin': int(bbox[1]),
            'xmax': int(bbox[2]),
            'ymax': int(bbox[3])
        }
    
    # Write out the augmented image and JSON
    cv2.imwrite(str(out_img_path), aug_image)
    with open(out_json_path, 'w') as f:
        json.dump(updated_annotations, f, indent=4)

# ------------------ Main Execution ------------------
cropped_dir = Path('out_cropped_images')
out_dir = Path('augmented_images')
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

image_paths = list(cropped_dir.rglob('*.jpg'))
for idx, image_path in enumerate(image_paths):
    print(f'augmenting {idx+1}/{len(image_paths)}', end='\r')
    
    # Infer JSON path
    json_path = Path(str(image_path).replace('/image/', '/json/').replace('.jpg', '.json'))
    if not json_path.exists():
        print(f"JSON file does not exist for {image_path}. Skipping...")
        continue

    # Create output directories
    img_name = image_path.name
    rel_img_path = image_path.relative_to(cropped_dir).parent
    img_out_dir = out_dir / rel_img_path
    os.makedirs(img_out_dir, exist_ok=True)
    out_img_path = img_out_dir / img_name

    json_name = json_path.name
    rel_json_path = json_path.relative_to(cropped_dir).parent
    json_out_dir = out_dir / rel_json_path
    os.makedirs(json_out_dir, exist_ok=True)
    out_json_path = json_out_dir / json_name

    process_augmentation(image_path, json_path, out_img_path, out_json_path)
