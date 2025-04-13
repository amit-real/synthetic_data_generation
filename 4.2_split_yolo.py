import os
import shutil
import random

# Configuration
yolo_dir = "converted_yolo"  # Directory containing YOLO images and labels
output_dir = "split_yolo"  # Directory to save the split datasets
shutil.rmtree(output_dir, ignore_errors=True)  # Clear previous output
os.makedirs(output_dir)  # Create output directory

train_ratio = 0.9  # Ratio for train split

# Create split directories
def create_split_dirs():
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, split, "labels"), exist_ok=True)

# Split files into train and validation sets
def split_files(file_list):
    random.shuffle(file_list)
    train_count = int(len(file_list) * train_ratio)
    train_files = file_list[:train_count]
    val_files = file_list[train_count:]
    return train_files, val_files

# Split and move YOLO files
def split_yolo_files():
    print("Splitting YOLO files...")
    label_dir = os.path.join(yolo_dir, "labels")
    image_dir = os.path.join(yolo_dir, "images")
    label_files = [f for f in os.listdir(label_dir) if f.endswith(".txt")]

    # Split into train and validation sets
    train_files, val_files = split_files(label_files)

    for split, files in zip(['train', 'val'], [train_files, val_files]):
        for label_file in files:
            img_name = label_file.replace(".txt", ".jpg")
            img_src = os.path.join(image_dir, img_name)
            label_src = os.path.join(label_dir, label_file)

            img_dest = os.path.join(output_dir, split, "images", img_name)
            label_dest = os.path.join(output_dir, split, "labels", label_file)

            shutil.copy(img_src, img_dest)
            shutil.copy(label_src, label_dest)

    print("YOLO dataset splitting complete.")

# Run the script
create_split_dirs()
split_yolo_files()
