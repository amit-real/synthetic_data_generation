import fitz
import cv2
import numpy as np
import os
import shutil

def extract_pdf_pages(pdf_path, out_dir, target_width):
    pdf = fitz.open(pdf_path)
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        original_width = page.rect.width  # Page width in points (1 point = 1/72 inch)
        scale_factor = target_width / original_width
        matrix = fitz.Matrix(scale_factor, scale_factor)
        pix = page.get_pixmap(matrix=matrix)
        pix.save(os.path.join(out_dir, str(page_num+1)+'.jpg'))
    pdf.close()

PAGE_WIDTH = 2048
src_dir = 'OUT_DIR/0_export_pdf_meta'
out_dir = 'OUT_DIR/1_extracted_pages'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

pdf_names = os.listdir(src_dir)
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]

for pdf_name in pdf_names:
    pdf_path = os.path.join(src_dir, pdf_name)
    img_out_dir = os.path.join(out_dir, pdf_name)
    os.makedirs(img_out_dir)
    extract_pdf_pages(pdf_path, img_out_dir, target_width=PAGE_WIDTH)
