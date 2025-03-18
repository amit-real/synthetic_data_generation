import cv2
import numpy as np
import math
from typing import List, Tuple
from inference_sdk import InferenceHTTPClient


def slice_image(image: np.ndarray, slice_size: tuple, overlap_prcnt: float) -> dict:
    """Slice an image into overlapping chunks."""
    height, width, *_ = image.shape
    stride_x = math.ceil(slice_size[0] * (1 - overlap_prcnt))
    stride_y = math.ceil(slice_size[1] * (1 - overlap_prcnt))

    main_dict = {
        "img_w_orig": width,
        "img_h_orig": height,
        "stride_x": stride_x,
        "stride_y": stride_y,
    }
    img_slices = []
    for y in range(0, height, stride_y):
        for x in range(0, width, stride_x):
            tmp_dict = {}
            xmin, ymin, xmax, ymax = (
                x,
                y,
                min(x + slice_size[0], width),
                min(y + slice_size[1], height),
            )

            slice_img = image[ymin:ymax, xmin:xmax]
            tmp_dict["xmin"], tmp_dict["ymin"], tmp_dict["xmax"], tmp_dict["ymax"] = (
                xmin,
                ymin,
                xmax,
                ymax,
            )
            # Pad if necessary
            h, w, *_ = slice_img.shape
            if h < slice_size[1] or w < slice_size[0]:
                padded_img = np.zeros((slice_size[1], slice_size[0], 3), dtype=np.uint8)
                padded_img[:h, :w] = slice_img
                slice_img = padded_img
            tmp_dict["img"] = slice_img
            img_slices.append(tmp_dict)
    main_dict["img_slices"] = img_slices
    return main_dict


def detect_checkboxes(image: np.ndarray,
                      inference_url: str = "http://localhost:9002",
                      model_id: str = "checkbox-detection/1",
                      chunk_size: int = 1024,
                      overlap: float = 0.2) -> List[Tuple[int, float, float, float, float, float]]:
    """
    Detect checkboxes in an image.

    Args:
        image: Input image (OpenCV format)
        inference_url: URL of the inference server
        model_id: Model ID to use for detection
        chunk_size: Size of image chunks for processing
        overlap: Overlap percentage between chunks

    Returns:
        List of detections in format (class_id, x1, y1, x2, y2, confidence)
        where class_id is 0 for checked and 1 for unchecked
    """
    # Resize the image to have width of 2048 while maintaining aspect ratio
    h, w = image.shape[:2]
    new_w = 2048
    new_h = int(h * (new_w / w))
    resized_image = cv2.resize(image, (new_w, new_h))

    # Store the resize ratio for converting back to original coordinates
    resize_ratio_w = w / new_w
    resize_ratio_h = h / new_h

    # Slice the image
    sliced_data = slice_image(resized_image, (chunk_size, chunk_size), overlap)

    # Extract slices and their positions
    slices = [slice_info["img"] for slice_info in sliced_data["img_slices"]]
    positions = [(slice_info["xmin"], slice_info["ymin"]) for slice_info in sliced_data["img_slices"]]

    # Create a client for inference
    client = InferenceHTTPClient(api_url=inference_url)

    # Process all chunks and collect detections
    all_detections = []

    try:
        batch_results = client.infer(slices, model_id=model_id)

        # Check if batch_results is a list (multiple results) or dict (single result)
        if isinstance(batch_results, list):
            results_to_process = zip(batch_results, positions)
        else:
            # If only one chunk was processed, wrap it in a list
            results_to_process = [(batch_results, positions[0])]

        for result, position in results_to_process:
            if 'predictions' in result:
                for pred in result['predictions']:
                    # Extract box in center x, center y, width, height format
                    cx, cy = pred['x'], pred['y']
                    w, h = pred['width'], pred['height']
                    confidence = pred['confidence']
                    label = pred['class']

                    # Convert to xmin, ymin, xmax, ymax format
                    x1 = cx - w/2
                    y1 = cy - h/2
                    x2 = cx + w/2
                    y2 = cy + h/2

                    # Adjust coordinates to the original image space
                    global_x1 = (position[0] + x1) * resize_ratio_w
                    global_y1 = (position[1] + y1) * resize_ratio_h
                    global_x2 = (position[0] + x2) * resize_ratio_w
                    global_y2 = (position[1] + y2) * resize_ratio_h

                    # Store detection
                    class_id = 0 if label == 'checked' else 1  # 0 for checked, 1 for unchecked
                    all_detections.append((class_id, global_x1, global_y1, global_x2, global_y2, confidence))

        return all_detections
    except Exception as e:
        print(f"Error during inference: {str(e)}")
        return []