import os
import shutil
import json
import cv2
import random
from multiprocessing import Pool, Value, Lock
osp = os.path.join

counter = Value('i',0)
lock = Lock()

src_dir = 'OUT_DIR/4_augmented'
pdf_names = os.listdir(osp(src_dir, 'json'))
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]

out_dir = 'OUT_DIR/5a_yolo_format'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(osp(out_dir, 'images'))
os.makedirs(osp(out_dir, 'labels'))

def convert_to_yolo(pdf_name, img_name, out_dir, total_files):
    img_path = osp(src_dir, 'imgs', pdf_name, img_name)
    img = cv2.imread(img_path)
    img_w, img_h = img.shape[1], img.shape[0]
    
    json_name = img_name.replace('.jpg','.json')
    json_path = osp(src_dir, 'json', pdf_name, json_name)
    json_data = json.load(open(json_path))
    
    # if len(json_data)==0:
    #     if random.random()<0.9:
    #         with lock:
    #             counter.value += 1
    #             print(f"Processed {counter.value}/{total_files}")
    #         return

    txt_lines = []

    for field_name in json_data:
        xmin, ymin, xmax, ymax = json_data[field_name]['xmin'], json_data[field_name]['ymin'],\
                                    json_data[field_name]['xmax'], json_data[field_name]['ymax']
        xc, yc, width, height = (xmin+xmax)/2, (ymin+ymax)/2, abs(xmax-xmin), abs(ymax-ymin)
        xc_n, yc_n, width_n, height_n = xc/img_w, yc/img_h, width/img_w, height/img_h
        
        label = 0
        if json_data[field_name]['state']=="checked":
            label = 1
        
        txt_line = f'{label} {xc_n} {yc_n} {width_n} {height_n}\n'
        txt_lines.append(txt_line)
    
    img_out_path = osp(out_dir, 'images', f'{pdf_name}_{img_name}')
    shutil.copy(img_path, img_out_path)

    txt_out_path = osp(out_dir, 'labels', f'{pdf_name}_{img_name.replace(".jpg",".txt")}')
    with open(txt_out_path, 'w') as f:
        f.writelines(txt_lines)

    with lock:
        counter.value += 1
        print(f"Processed {counter.value}/{total_files}")


total_files = 0

for root, dirs, files in os.walk(osp(src_dir, 'imgs')):
    total_files+=len(files)

tasks = []


for idx, pdf_name in enumerate(pdf_names):
    img_names = os.listdir(osp(src_dir, 'imgs', pdf_name))

    for idx2, img_name in enumerate(img_names):
        tasks.append([pdf_name, img_name, out_dir, total_files])

with Pool(processes=50) as pool:
    pool.starmap(convert_to_yolo, tasks)

