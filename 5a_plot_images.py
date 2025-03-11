import os, shutil
import cv2
import json
import random
osp = os.path.join

src_dir = 'OUT_DIR/4_augmented'
out_dir = 'OUT_DIR/4_augmented_plot_cbox'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir, exist_ok=True)  

pdf_names = os.listdir(osp(src_dir, 'json'))

count=0
for pdf_name in pdf_names:
    json_names = os.listdir(osp(src_dir, 'json', pdf_name))
    os.makedirs(osp(out_dir, pdf_name))

    for json_name in json_names:

        # if random.random()<0.98:
        #     continue
        img_name = json_name.replace('.json','.jpg')
        img = cv2.imread(osp(src_dir, 'imgs', pdf_name, img_name))
        json_data = json.load(open(osp(src_dir,'json', pdf_name, json_name)))
        
        for field_name in json_data:
            if '<cb_' not in field_name:
                continue
            
            xmin, ymin, xmax, ymax = json_data[field_name]['xmin'], json_data[field_name]['ymin'],json_data[field_name]['xmax'],json_data[field_name]['ymax']
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            state = json_data[field_name]['state']
            color = (0,255,0)
            if state=='unchecked':
                color = (0,0,255)
            cv2.rectangle(img, (xmin,ymin), (xmax,ymax), color, 2)
        count+=1
        cv2.imwrite(osp(out_dir, pdf_name, img_name), img)
        print(count)
        if count>=500:
            exit()

