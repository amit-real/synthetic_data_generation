"""
PDF Checkbox Dataset Creator
===========================

This module provides tools to process PDF documents, detect checkboxes, and create
a YOLO-compatible dataset for training object detection models.

Overview
--------
The package is organized into several modules that each handle a specific part of the workflow:

1. pdf_processor: Handles finding and processing PDF files, yielding individual pages
2. checkbox_detector: Provides functionality to detect checkboxes in images
3. yolo_dataset: Manages creation of YOLO-compatible dataset formats
4. main: Orchestrates the entire workflow

Features
--------
- Process multiple PDF documents in a directory
- Extract pages from PDFs and convert them to OpenCV format
- Detect checked and unchecked checkboxes using a machine learning model
- Create a properly structured YOLO dataset with images and annotations
- Generate dataset configuration files for training

Requirements
-----------
- Python 3.6+
- OpenCV (cv2)
- NumPy
- pdf2image (requires poppler to be installed)
- inference_sdk (for the inference client)

Usage
-----
Basic usage:

```python
from pdf_checkbox_detector import main

# Run the complete pipeline with default settings
main.main()"""