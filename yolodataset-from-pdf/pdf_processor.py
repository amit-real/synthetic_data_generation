import os
import numpy as np
import cv2
import fitz  # PyMuPDF
import tempfile
from typing import Generator, Tuple, List


def get_pdf_files(pdf_dir: str) -> List[str]:
    """Get all PDF files from a directory."""
    return [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir)
            if f.lower().endswith('.pdf')]


def pdf_page_generator(pdf_dir: str, target_width: int = 2048) -> Generator[Tuple[str, int, np.ndarray], None, None]:
    """
    Generate pages from all PDFs in a directory using PyMuPDF (fitz).

    Args:
        pdf_dir: Directory containing PDF files
        target_width: Target width for the extracted images

    Yields:
        Tuple containing (pdf_path, page_number, page_image)
    """
    pdf_files = get_pdf_files(pdf_dir)

    for pdf_path in pdf_files[1:]:
        try:
            print(f"Processing {pdf_path}")

            # Open the PDF
            pdf = fitz.open(pdf_path)

            for page_num in range(len(pdf)):
                # Get the page
                page = pdf[page_num]

                # Calculate scale factor based on target width
                original_width = page.rect.width
                scale_factor = target_width / original_width
                matrix = fitz.Matrix(scale_factor, scale_factor)

                # Get the pixmap (rendered page)
                pix = page.get_pixmap(matrix=matrix)

                # Create a temporary file to save the image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name

                # Save the pixmap to the temporary file
                pix.save(temp_path)

                # Read the image with OpenCV
                img = cv2.imread(temp_path)

                # Remove the temporary file
                os.unlink(temp_path)

                # Yield the result
                yield pdf_path, page_num, img

            # Close the PDF
            pdf.close()

        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")