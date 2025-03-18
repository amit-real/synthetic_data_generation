"""
This script is used to create a YOLO dataset from a directory of PDF files.
Algorithm:
1) extract pages from pdf
2) detect checkboxes in each page
3) save page image and labels in yolo format
4) create a yaml file for the dataset
5) remove overlapping boxes from labels
This script is helpful to create a dataset from a directory of PDF files.
using this type of auto labeling, most of the checkboxes are detected and data annotation team just need to verify the boxes and create a dataset.
"""


import os
from pdf_processor import pdf_page_generator
from checkbox_detector import detect_checkboxes
from yolo_dataset import create_dataset_dirs, save_detection, create_dataset_yaml


def main():
    # Define directories
    pdf_dir = "./pdf_files"
    dataset_base_dir = "./checkbox_dataset"

    # Create dataset directories
    image_dir, label_dir = create_dataset_dirs(dataset_base_dir)

    # Process all PDFs and create dataset
    img_counter = 0

    # Get pages from PDFs
    for pdf_path, page_num, page_img in pdf_page_generator(pdf_dir):

        # Detect checkboxes
        detections = detect_checkboxes(page_img)

        if detections:
            # Save to YOLO format
            success = save_detection(page_img, detections, image_dir, label_dir, img_counter)

            if success:
                print(f"Saved image and labels for {os.path.basename(pdf_path)}, "
                      f"page {page_num+1} as {img_counter}.png")
                img_counter += 1
        else:
            print(f"No checkboxes found in {os.path.basename(pdf_path)}, page {page_num+1}")

    # Create YOLO dataset files
    if img_counter > 0:
        create_dataset_yaml(dataset_base_dir, img_counter)
        print(f"Created YOLO dataset with {img_counter} images")
    else:
        print("No images with checkboxes found")
    
    #remove overlapping boxes from labels
    remove_overlapping_bboxes("./checkbox_dataset/labels/train")
    remove_overlapping_bboxes("./checkbox_dataset/labels/val")


if __name__ == "__main__":
    main()