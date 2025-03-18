"""
This script is used to augment the YOLO dataset with transformed versions of images and labels.
"""

import os
import json
import glob
import shutil
import random
import cv2
import albumentations as A
import numpy as np
from tqdm import tqdm

def apply_augmentations(image, bboxes, labels):
    """Apply augmentations to image and bounding boxes"""
    transforms = A.Compose([
        A.RandomScale(scale_limit=(-0.5, 2), p=0.5),
        A.PadIfNeeded(min_height=1024, min_width=1024, border_mode=0, p=1),
        A.RandomCrop(width=1024, height=1024, p=0.5),
        A.HorizontalFlip(p=0.3),
        A.Perspective(scale=(0.05, 0.1), p=0.5),
        A.GridDistortion(num_steps=5, distort_limit=0.2, p=0.5),
        A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
        A.GaussianBlur(blur_limit=(3, 7), p=0.3),
        A.RandomShadow(p=0.5),
        A.InvertImg(p=0.2),
        A.ShiftScaleRotate(p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.RGBShift(r_shift_limit=30, g_shift_limit=30, b_shift_limit=30, p=0.3),
    ],
    bbox_params=A.BboxParams(format='yolo', label_fields=['labels']))

    transformed = transforms(image=image, bboxes=bboxes, labels=labels)
    return transformed['image'], transformed['bboxes']

def augment_yolo_dataset(dataset_dir: str, num_augmentations: int = 3):
    """
    Augment existing YOLO dataset with transformed versions of images and labels.
    
    Args:
        dataset_dir: Path to YOLO dataset directory containing images/ and labels/
        num_augmentations: Number of augmented versions to create for each image
    """
    splits = ['train', 'val']  # Usually we don't augment test set
    
    for split in splits:
        images_dir = os.path.join(dataset_dir, 'images', split)
        labels_dir = os.path.join(dataset_dir, 'labels', split)
        
        # Get all images
        image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        print(f"\nProcessing {split} set: {len(image_files)} original images")
        
        for img_file in tqdm(image_files, desc=f"Augmenting {split} set"):
            # Read image
            img_path = os.path.join(images_dir, img_file)
            image = cv2.imread(img_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Read corresponding label file
            label_path = os.path.join(labels_dir, os.path.splitext(img_file)[0] + '.txt')
            if not os.path.exists(label_path):
                continue
                
            # Read YOLO format labels
            bboxes = []
            labels = []
            with open(label_path, 'r') as f:
                for line in f:
                    label, x_center, y_center, width, height = map(float, line.strip().split())
                    bboxes.append([x_center, y_center, width, height])
                    labels.append(label)
            
            # Generate augmented versions
            for aug_idx in range(num_augmentations):
                # Apply augmentations
                aug_image, aug_bboxes = apply_augmentations(image, bboxes, labels)
                
                if len(aug_bboxes) == 0:  # Skip if all bboxes were dropped
                    continue
                
                # Generate new filenames
                base_name = os.path.splitext(img_file)[0]
                aug_img_path = os.path.join(images_dir, f"{base_name}_aug{aug_idx}{os.path.splitext(img_file)[1]}")
                aug_label_path = os.path.join(labels_dir, f"{base_name}_aug{aug_idx}.txt")
                
                # Save augmented image
                aug_image = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(aug_img_path, aug_image)
                
                # Save augmented labels
                with open(aug_label_path, 'w') as f:
                    for bbox, label in zip(aug_bboxes, labels):
                        f.write(f"{int(label)} {' '.join(map(str, bbox))}\n")

def main():
    # Example usage
    dataset_dir = "OUT_DIR/yolo_dataset"  # Update this path
    num_augmentations = 3  # Number of augmented versions per image
    
    print("Starting dataset augmentation...")
    augment_yolo_dataset(dataset_dir, num_augmentations)
    print("\nAugmentation complete!")

if __name__ == "__main__":
    main()