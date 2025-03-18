"""
This script is used to visualize the YOLO dataset using gradio.
"""
import gradio as gr
import cv2

def visualize_yolo(image_file, label_file):
    # Read the image
    image = cv2.imread(image_file.name)
    img_height, img_width = image.shape[:2]

    # Parse YOLO format labels
    bboxes = []
    if label_file:
        with open(label_file.name, 'r') as f:
            for line in f:
                data = line.strip().split()
                if len(data) >= 5:  # class_id, x_center, y_center, width, height
                    class_id = int(data[0])
                    x_center = float(data[1]) * img_width
                    y_center = float(data[2]) * img_height
                    width = float(data[3]) * img_width
                    height = float(data[4]) * img_height

                    # Calculate bbox coordinates
                    x1 = int(x_center - width / 2)
                    y1 = int(y_center - height / 2)
                    x2 = int(x_center + width / 2)
                    y2 = int(y_center + height / 2)

                    bboxes.append((class_id, x1, y1, x2, y2))

    # Draw bounding boxes on the image
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]

    for box in bboxes:
        class_id, x1, y1, x2, y2 = box
        color = colors[class_id % len(colors)]
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, f"Class {class_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Convert from BGR to RGB for display in Gradio
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

# Create Gradio interface
with gr.Blocks(title="YOLO Dataset Visualizer") as demo:
    gr.Markdown("# YOLO Dataset Visualizer")
    gr.Markdown("Upload an image and its corresponding YOLO format label file to visualize bounding boxes.")

    with gr.Row():
        with gr.Column():
            image_input = gr.File(label="Upload Image")
            label_input = gr.File(label="Upload YOLO Label File (.txt)")
            submit_btn = gr.Button("Visualize")

        with gr.Column():
            image_output = gr.Image(label="Visualization Result")

    submit_btn.click(
        fn=visualize_yolo,
        inputs=[image_input, label_input],
        outputs=image_output
    )

if __name__ == "__main__":
    demo.launch()