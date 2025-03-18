import fitz
import os
import json
import fitz
import cv2
import numpy as np
import os
import shutil

def extract_pdf_metadata(pdf_paths, output_dir, page_width):
    """
    Extract metadata from PDFs and save both annotated PDFs and metadata to output directory
    """
    for pdf_path in pdf_paths:
        pdf_name = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)

        data = {}
        data['meta_info'] = {'path': pdf_path}

        for page_number, page in enumerate(doc, start=1):
            original_width = page.rect.width
            scale_factor = page_width / original_width

            data[page_number] = []

            for widget in page.widgets():
                field_name = widget.field_name
                field_type = widget.field_type  # 2 for checkbox, 7 for text_area
                text = widget.field_value
                xmin, ymin, xmax, ymax = widget.rect
                xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = (
                    xmin*scale_factor, ymin*scale_factor,
                    xmax*scale_factor, ymax*scale_factor
                )
                page.delete_widget(widget)

                tmp_dict = {}

                if field_type == 2:
                    tmp_dict['name'] = field_name.strip()
                    tmp_dict['type'] = 'checkbox'
                    tmp_dict['text'] = text.strip()
                    tmp_dict['bbox'] = {
                        'xmin': xmin_scaled, 'ymin': ymin_scaled,
                        'xmax': xmax_scaled, 'ymax': ymax_scaled
                    }

                if field_type == 7:
                    tmp_dict['name'] = field_name.strip()
                    tmp_dict['type'] = 'text_area'
                    tmp_dict['text'] = text.strip()
                    tmp_dict['bbox'] = {
                        'xmin': xmin_scaled, 'ymin': ymin_scaled,
                        'xmax': xmax_scaled, 'ymax': ymax_scaled
                    }

                    font_size = 10
                    width, height = abs(xmax-xmin), abs(ymax-ymin)

                    if 'init>' in field_name.lower():
                        font_size = 7

                    x_start = xmin + (width/2) - ((len(field_name)*font_size)/2)
                    if x_start < xmin:
                        x_start = xmin + 4

                    y_start = ymax - 2
                    r, g, b = 4/256, 139/256, 255/256
                    page.insert_text(
                        (x_start, y_start),
                        field_name,
                        fontname="helv",
                        fontsize=font_size,
                        rotate=0,
                        color=(r, g, b)
                    )

                if tmp_dict:
                    data[page_number].append(tmp_dict)

        out_pdf_path = os.path.join(output_dir, pdf_name)
        doc.save(out_pdf_path)

        json_path = os.path.join(output_dir, pdf_name.replace('.pdf', '.json'))
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)

def extract_pdf_pages(pdf_paths, out_dir, target_width):

    for pdf_path in pdf_paths:
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            original_width = page.rect.width  # Page width in points (1 point = 1/72 inch)
            scale_factor = target_width / original_width
            matrix = fitz.Matrix(scale_factor, scale_factor)
            pix = page.get_pixmap(matrix=matrix)
            pix.save(os.path.join(out_dir, str(page_num+1)+'.jpg'))
        pdf.close()
