import fitz
import cv2
import numpy as np
import os
import shutil
import json


template_pdf_dir = 'TEMPLATE_PDF/annotated_pdfs'
template_pdfs = os.listdir(template_pdf_dir)
template_pdfs = [i for i in template_pdfs if i.endswith('.pdf')]

PAGE_WIDTH = 2048

out_dir = 'OUT_DIR/0_export_pdf_meta'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

for pdf_name in template_pdfs:
    pdf_path = os.path.join(template_pdf_dir, pdf_name)
    doc = fitz.open(pdf_path)

    data = {}
    data['meta_info'] = {'path': pdf_path}

    for page_number, page in enumerate(doc, start=1):
        print(f"Page {page_number}:")
        original_width = page.rect.width  #Page width in points (1 point = 1/72 inch)
        scale_factor = PAGE_WIDTH / original_width

        data[page_number] = []
        
        for widget in page.widgets():
            field_name = widget.field_name
            field_type = widget.field_type # 2 for checkbox, 7 for text_area
            text =  widget.field_value
            xmin, ymin, xmax, ymax = widget.rect
            xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = xmin*scale_factor, ymin*scale_factor,\
                                     xmax*scale_factor, ymax*scale_factor
            page.delete_widget(widget)

            tmp_dict = {}

            if field_type==2:
                tmp_dict['name'] = field_name.strip()
                tmp_dict['type'] = 'checkbox'
                tmp_dict['text'] = text.strip()
                tmp_dict['bbox'] = {'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}
                
            if field_type==7:
                tmp_dict['name'] = field_name.strip()
                tmp_dict['type'] = 'text_area'
                tmp_dict['text'] = text.strip()
                tmp_dict['bbox'] = {'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}

                font_size = 10
                width, height = abs(xmax-xmin), abs(ymax-ymin)

                if 'init>' in field_name.lower():
                    font_size = 7

                x_start = xmin + (width/2) - ((len(field_name)*font_size)/2)
                if x_start<xmin:
                    x_start=xmin+4

                y_start = ymax-2
                # xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
                r,g,b = 4,139,255
                r,g,b = r/256, g/256, b/256
                page.insert_text((x_start,y_start), field_name, fontname = "helv", fontsize=font_size, rotate=0, color=(r,g,b))
            
            if len(tmp_dict)>0:
                data[page_number].append(tmp_dict)
        
    out_path = os.path.join(out_dir, pdf_name)
    doc.save(out_path)

    json.dump(data, open(os.path.join(out_dir, pdf_name.replace('.pdf','.json')),'w'), indent=4)
    
print('done')