import fitz
import cv2
import numpy as np
import os
import shutil
import json
import random
from multiprocessing import Pool, Value, Lock
osp = os.path.join

counter = Value('i', 0)
lock = Lock()

def extract_pdf_pages(page, out_path, target_width):
    original_width = page.rect.width  # Page width in points (1 point = 1/72 inch)
    scale_factor = target_width / original_width
    matrix = fitz.Matrix(scale_factor, scale_factor)
    pix = page.get_pixmap(matrix=matrix)
    pix.save(out_path)

def get_xstart_ystart(text, xmin, ymin, xmax, ymax, font_size):
    if text in ['X', "\u2713", "\u2714", "\u25CF"]: #if it is a checkbox, then return same position
        return xmin+1, ymax-2
    
    width, height = abs(xmax-xmin), abs(ymax-ymin)
    align = random.choice(['left', 'center', 'right'])
    
    if align=='left':
        x_buffer, y_buffer = random.choice([1,2,3]), random.choice([0,1,2,3,4])
        x_start, y_start = xmin+x_buffer, ymax-y_buffer

        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start
        
    elif align=='center':
        x_buffer, y_buffer = random.choice([-1,-2,-3,0,1,2,3]), random.choice([0,1,2,3,4])
        x_start = xmin + (width/2) - ((len(text)*font_size)/2)
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer
        
        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start

    elif align=='right':
        x_buffer, y_buffer = random.choice([-1,-2,-3,0]), random.choice([0,1,2,3,4])
        x_start = xmax - ((len(text)*font_size)) - 4
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer

        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start

fonts = ['cobi', 'cobo', 'coit', 'cour', 'hebo', 'heit', 'helv', 'tibi', 'tibo', 'tiit', 'tiro']

PAGE_WIDTH = 2048
extracted_imgs_dir = 'OUT_DIR/1_extracted_pages'
template_pdf_dir = 'TEMPLATE_PDF/annotated_pdfs'
syn_data_dir = 'TEMPLATE_PDF/synthetic_json'
syn_pdfs = os.listdir(syn_data_dir)
syn_pdfs = [i for i in syn_pdfs if i.endswith('.pdf')]

out_dir = 'OUT_DIR/2_syn_generated'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir, exist_ok=True)

def generate_synthetic_data(pdf_name, template_pdf_path, page_number_syn, json_entry, idx2, total):
    json_out_path = osp(out_dir, 'json', pdf_name, f'{page_number_syn}_{idx2}.json')
    img_out_path = osp(out_dir, 'imgs', pdf_name, f'{page_number_syn}_{idx2}.jpg')

    if os.path.exists(json_out_path)==True and os.path.exists(img_out_path)==True:
        with lock:
            counter.value += 1
            print(f"Processed {counter.value}/{total}")
        return

    doc = fitz.open(template_pdf_path)
    page = doc[page_number_syn-1]
    original_width = page.rect.width
    scale_factor = PAGE_WIDTH / original_width
    page.insert_font(fontfile='DejaVuSans.ttf', fontname="DVS")
    tmp_dict = {}
    
    for widget in page.widgets():
        field_name = widget.field_name
        if 'ENVELOPEID' in field_name: #used for signatures
            if field_name in tmp_dict:
                del tmp_dict[field_name]
            continue

        # field_type = widget.field_type # 2 for checkbox, 7 for text_area
        xmin, ymin, xmax, ymax = widget.rect
        page.delete_widget(widget)

        xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = xmin*scale_factor, ymin*scale_factor, xmax*scale_factor, ymax*scale_factor
        xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = int(xmin_scaled), int(ymin_scaled), int(xmax_scaled), int(ymax_scaled)

        if len(json_entry)==0:
            req_text={'data':'', 'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}
        else:
            req_text =  str(json_entry[field_name]) # from synthetic data json
            tmp_dict[field_name] = {'data':req_text, 'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}

        if random.random()>0.8: #keep 20% of the elements empty
            if '<cb_' not in field_name:
                del tmp_dict[field_name]
                continue

        if req_text.lower()=='unchecked': # no need to fill anything
            tmp_dict[field_name] = {'data':'unchecked', 'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}
            continue  

        elif req_text.lower()=='checked':
            tmp_dict[field_name] = {'data':'checked', 'xmin':xmin_scaled, 'ymin':ymin_scaled, 'xmax':xmax_scaled, 'ymax':ymax_scaled}
            req_text = random.choice(["X", "\u2713", "\u2714", "\u25CF"])

        ##################################################
        font_size = 10
        x_start, y_start = get_xstart_ystart(req_text, xmin, ymin, xmax, ymax, font_size)

        r,g,b = 0,0,0

        if random.random()>0.7:
            r,g,b = random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)
        r,g,b = r/256, g/256, b/256

        if r==1 and g==1 and b==1: #if white, then not visible to the eye
            del tmp_dict[field_name]

        font = random.choice(fonts)
        if '<cb' in field_name:
            font = random.choice(['DVS'])  #DejaVuSans font for checkboxes, because it supports tick and filled-dot.

        font_size=random.choice([8,9,10,11])

        if 'init>' in field_name.lower():
            font_size = 7

        page.insert_text((x_start, y_start), req_text, fontname=font, fontsize=font_size, rotate=0, color=(r,g,b))

    json.dump(tmp_dict, open(json_out_path, 'w'), indent=4)
    extract_pdf_pages(page, img_out_path, target_width=PAGE_WIDTH)

    with lock:
        counter.value += 1
        print(f"Processed {counter.value}/{total}")
    
total = 0

def main():
    tasks = []
    for idx, pdf_name in enumerate(syn_pdfs):
        
        print(f'ADDING TASKS {idx+1}/{len(syn_pdfs)}  {pdf_name}')

        if pdf_name=='FHDA.pdf':
            continue

        os.makedirs(osp(out_dir, 'imgs', pdf_name), exist_ok=True)
        os.makedirs(osp(out_dir, 'json', pdf_name), exist_ok=True)

        syn_json_path = osp(syn_data_dir, pdf_name)
        syn_json_names = os.listdir(syn_json_path)
        syn_json_names = [i for i in syn_json_names if i.endswith('.json')]

        for syn_json_name in syn_json_names:
            page_number_syn = int(syn_json_name.replace('.json',''))
            syn_json = json.load(open(osp(syn_json_path, syn_json_name)))
            print(f"Page {page_number_syn}:")
            
            for idx2, json_entry in enumerate(syn_json):
                if idx2>10:
                    break
                json_out_path = osp(out_dir, 'json', pdf_name, f'{page_number_syn}_{idx2}.json')
                img_out_path = osp(out_dir, 'imgs', pdf_name, f'{page_number_syn}_{idx2}.jpg')

                if os.path.exists(json_out_path)==True and os.path.exists(img_out_path)==True:
                    continue

                template_pdf_path = osp(template_pdf_dir, pdf_name)
                tasks.append([pdf_name, template_pdf_path, page_number_syn, json_entry, idx2])

        # pages with no entries - negative empty data
        orig_pdf_path = osp(template_pdf_dir, pdf_name)
        doc = fitz.open(orig_pdf_path)
        total_pages = doc.page_count

        for page_num in range(1, total_pages+1):
            json_path = osp(syn_data_dir, pdf_name, f'{page_num}.json')
            if os.path.exists(json_path): #only if data is missing
                continue
            
            for idx2 in range(50): # only 50 negative samples per empty page
                template_pdf_path = osp(template_pdf_dir, pdf_name)
                json_entry = {} #empty entry
                tasks.append([pdf_name, template_pdf_path, page_num, {}, idx2])

    total = len(tasks)          
    for idx in range(len(tasks)):
        tasks[idx].append(total)

    with Pool(processes=50) as pool:
        results = pool.starmap(generate_synthetic_data, tasks)
    
    # Aggregate or save the results as needed
    print(f"Total pages processed: {counter.value}")
    print('done')

if __name__=='__main__':
    main()
                     
