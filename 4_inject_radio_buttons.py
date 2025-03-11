import os, shutil
import json
import cv2
import random
from multiprocessing import Pool, Value, Lock
osp = os.path.join


meta_info_dir = 'OUT_DIR/0_export_pdf_meta'
src_dir = 'OUT_DIR/2_syn_generated'
out_dir = 'OUT_DIR/3_rb_added'
shutil.rmtree(out_dir, ignore_errors=True)

total_files = 0

for root, dirs, files in os.walk(osp(src_dir, 'json')):
    req_files = [i for i in files if i.endswith('.json')]
    total_files += len(req_files)

pdf_names = os.listdir(osp(src_dir, 'json'))

cur_count=0
for pdf_name in pdf_names:
    os.makedirs(osp(out_dir, 'imgs', pdf_name))
    os.makedirs(osp(out_dir, 'json', pdf_name))
    
    json_names = os.listdir(osp(src_dir, 'json', pdf_name))
    global_fields_meta_info = json.load(open(osp(meta_info_dir, pdf_name.replace('.pdf', '.json'))))

    for json_name in json_names:
        print(f'{cur_count+1}/{total_files}  {pdf_name}  {json_name}')
        page_num = json_name.split('_')[0]
        meta_info = {i['name']:i for i in global_fields_meta_info[page_num] }
        json_data = json.load(open(osp(src_dir, 'json', pdf_name, json_name)))      
        img = cv2.imread(osp(src_dir, 'imgs', pdf_name, json_name.replace('.json', '.jpg')))
  
        for field_name in json_data:
            if '<cb_' not in field_name:
               continue
            if json_data[field_name]['data'].lower()!='unchecked':
                continue
            if random.random()>0.2:
                continue
            
            bbox = meta_info[field_name]['bbox']
            xmin, ymin, xmax, ymax = bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']
            width, height = xmax-xmin, ymax-ymin
            xc, yc = int(xmin+(width/2)), int(ymin+(height/2))

            outer_radius = width/2
            prcnt = random.choice([-0.2, -0.15, -0.1, 0, 0.1, 0.15, 0.2, 0.25])
            outer_radius = int((1+prcnt)*outer_radius)
            inner_radius = int(0.7*outer_radius)
            thickness = int(0.1*outer_radius)

            r,g,b = 0,0,0
            if random.random()>0.3:
                r,g,b = random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)
            if r==255 and g==255 and b==255:
                r,g,b = random.choice([(255,0,0), (0,255,0), (0,0,255)])
            cv2.circle(img, (xc,yc), outer_radius, (r,g,b), thickness)
            cv2.circle(img, (xc,yc), inner_radius, (r,g,b), -1)
            json_data[field_name]['data'] = 'checked'
        
        cv2.imwrite(osp(out_dir, 'imgs', pdf_name, json_name.replace('.json','.jpg')), img)
        json.dump(json_data, open(osp(out_dir, 'json', pdf_name, json_name),'w'), indent=4)
        cur_count+=1    
       
        if cur_count>50:
            break