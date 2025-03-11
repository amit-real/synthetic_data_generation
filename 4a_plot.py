import os, shutil
import cv2
import json
import random
osp = os.path.join

src_dir = 'OUT_DIR/3_rb_added'
out_dir = 'OUT_DIR/3a_rb_plot'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)  

pdf_names = os.listdir(osp(src_dir, 'json'))

count=0
for pdf_name in pdf_names:
    json_names = os.listdir(osp(src_dir, 'json', pdf_name))
    os.makedirs(osp(out_dir, pdf_name))

    for json_name in json_names:
        # if random.random()<0.95:
        #     continue
        print(count)
        img_name = json_name.replace('.json','.jpg')
        img = cv2.imread(osp(src_dir, 'imgs', pdf_name, img_name))
        json_data = json.load(open(osp(src_dir,'json', pdf_name, json_name)))
        
        for field_name in json_data:
            xmin, ymin, xmax, ymax = json_data[field_name]['xmin'], json_data[field_name]['ymin'],json_data[field_name]['xmax'],json_data[field_name]['ymax']
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            cv2.rectangle(img, (xmin,ymin), (xmax,ymax), (0,255,0), 2)
           
        cv2.imwrite(osp(out_dir, pdf_name, img_name), img)

        count+=1
