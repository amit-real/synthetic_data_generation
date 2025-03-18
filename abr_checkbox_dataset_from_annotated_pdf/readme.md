# PDF Checkbox Dataset Generator

This script generates a synthetic dataset of checkbox annotations from annotated PDF templates, specifically designed for training YOLO object detection models to detect checked and unchecked checkboxes.

## Quick Start

1. Add your editable PDFs to `abr_checkbox_dataset_from_annotated_pdf/TEMPLATE_PDF/annotated_pdfs/`
2. Create synthetic JSON files in `abr_checkbox_dataset_from_annotated_pdf/TEMPLATE_PDF/synthetic_json/`
   - Each JSON file corresponds to a PDF page
   - Each element in the JSON file represents data for generating one synthetic image
   - You can use LLMs to automatically generate this synthetic data
3. Run the script:
   ```bash
   python main.py
   ```
4. Run augment_images.py on yolo dataset if you want to create different augmentations of images.
## Overview

The script performs the following operations:
1. Extracts metadata from annotated PDF templates
2. Converts PDF pages to images
3. Generates synthetic data using various fonts
4. Converts annotations to YOLO format (currently only checkbox labels)
5. Creates a dataset split into train/val/test sets (80%/10%/10%)

## Prerequisites

- Python 3.x
- Required directory structure:
  ```
  abr_checkbox_dataset_from_annotated_pdf/
  ├── TEMPLATE_PDF/
  │   ├── annotated_pdfs/      # Your annotated PDF templates
  │   └── synthetic_json/      # JSON templates for synthetic data generation
  ├── main.py
  └── [other script files]
  ```

## Installation

1. Clone this repository
2. Install required dependencies (TODO: add requirements.txt)

## Output Structure

The script creates the following directory structure: