"""
This script is used to detect checkboxes in an image using a sliding window approach.
"""
import cv2
import numpy as np
import gradio as gr
from inference_sdk import InferenceHTTPClient
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io
import math

def slice_image(image: np.ndarray, slice_size: tuple, overlap_prcnt: float) -> dict:
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

def process_image(input_image, chunk_size=1024, overlap=0.2):
    # Convert gradio image to numpy array if it's not already
    if not isinstance(input_image, np.ndarray):
        input_image = np.array(input_image)

    # Resize the image to have width of 2048 while maintaining aspect ratio
    h, w = input_image.shape[:2]
    new_w = 2048
    new_h = int(h * (new_w / w))
    resized_image = cv2.resize(input_image, (new_w, new_h))

    # Slice the image
    sliced_data = slice_image(resized_image, (chunk_size, chunk_size), overlap)

    # Extract slices and their positions
    slices = [slice_info["img"] for slice_info in sliced_data["img_slices"]]
    positions = [(slice_info["xmin"], slice_info["ymin"]) for slice_info in sliced_data["img_slices"]]

    # Create a client for inference
    client = InferenceHTTPClient(api_url="http://localhost:9002")

    # Create a copy of the resized image for visualization
    output_image = resized_image.copy()

    # Visualize chunks
    chunk_visualization = visualize_chunks(resized_image, sliced_data["img_slices"])

    # Process all chunks at once
    try:
        batch_results = client.infer(slices, model_id="checkbox-detection/1")

        # Process results
        all_detections = []

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

                    # Convert to top-left, bottom-right format
                    x1 = cx - w/2
                    y1 = cy - h/2
                    x2 = cx + w/2
                    y2 = cy + h/2

                    # Adjust coordinates to the original image space
                    global_x1 = position[0] + x1
                    global_y1 = position[1] + y1
                    global_x2 = position[0] + x2
                    global_y2 = position[1] + y2

                    # Draw bbox on the output image
                    color = (0, 255, 0) if label == 'checked' else (0, 0, 255)
                    cv2.rectangle(output_image, (int(global_x1), int(global_y1)),
                                  (int(global_x2), int(global_y2)), color, 2)

                    # Add label and confidence text
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(output_image, text, (int(global_x1), int(global_y1) - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                    all_detections.append((global_x1, global_y1, global_x2, global_y2, confidence, label))

    except Exception as e:
        return None, None, f"Error during inference: {str(e)}"

    return output_image, chunk_visualization, len(all_detections)

def visualize_chunks(image, slices):
    # Create a matplotlib figure for visualization
    plt.figure(figsize=(12, 12))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Plot each slice as a rectangle
    ax = plt.gca()
    for slice_info in slices:
        xmin, ymin = slice_info["xmin"], slice_info["ymin"]
        xmax, ymax = slice_info["xmax"], slice_info["ymax"]
        width = xmax - xmin
        height = ymax - ymin
        rect = patches.Rectangle((xmin, ymin), width, height, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    # Save the figure to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer to PIL Image
    chunk_vis = Image.open(buf)
    plt.close()

    return chunk_vis

def gradio_interface(input_image, chunk_size, overlap):
    # Validate inputs
    chunk_size = int(chunk_size)
    overlap = float(overlap)

    if chunk_size <= 0 or overlap < 0 or overlap >= 1:
        return None, None, "Chunk size must be positive and overlap must be between 0 and 1"

    # Process the image
    try:
        output_image, chunk_vis, num_detections = process_image(
            input_image, chunk_size=chunk_size, overlap=overlap
        )
        if isinstance(num_detections, int):
            return output_image, chunk_vis, f"Detected {num_detections} checkboxes"
        else:
            return None, None, num_detections
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Checkbox Detection with Sliding Window")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Input Image")
            chunk_size = gr.Number(value=1024, label="Chunk Size", precision=0)
            overlap = gr.Slider(minimum=0.0, maximum=0.9, value=0.2, step=0.1, label="Overlap Percentage")
            process_btn = gr.Button("Process Image")

        with gr.Column():
            output_image = gr.Image(label="Detected Checkboxes")
            chunk_vis = gr.Image(label="Chunk Visualization")
            status = gr.Textbox(label="Status")

    process_btn.click(
        fn=gradio_interface,
        inputs=[input_image, chunk_size, overlap],
        outputs=[output_image, chunk_vis, status]
    )

    gr.Markdown("""
    ## How to use
    1. Upload an image containing checkboxes
    2. Adjust chunk size and overlap percentage if needed
    3. Click "Process Image"
    4. View the detection results and chunk visualization
    """)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()