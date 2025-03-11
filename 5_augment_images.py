import os, shutil
import albumentations as A
import cv2
import json
import random
from multiprocessing import Pool, Value, Lock
osp = os.path.join

counter = Value('i', 0)
lock = Lock()

src_dir = 'OUT_DIR/3_rb_added'
out_dir = 'OUT_DIR/4_augmented'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(osp(out_dir,'imgs'), exist_ok=True)
os.makedirs(osp(out_dir,'json'), exist_ok=True)  

pdf_names = os.listdir(osp(src_dir, 'imgs'))

transforms = A.Compose([
        A.RandomScale(scale_limit=(-0.5,2), p=1),
        A.PadIfNeeded(min_height=1024, min_width=1024, border_mode=0, p=1),
        A.RandomCrop(width=1024, height=1024, p=1.0),
        A.HorizontalFlip(p=0.3),
        A.Perspective(scale=(0.05, 0.1), p=0.5),
        A.GridDistortion(num_steps=5, distort_limit=0.2, p=0.5),
        A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
        A.GaussianBlur(blur_limit=(3, 7), p=0.3),
        A.RandomShadow(p=0.5),
        A.InvertImg(p=0.2),
        A.ShiftScaleRotate(p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.RGBShift(r_shift_limit=30, g_shift_limit=30, b_shift_limit=30, p=0.3),
    ],
    bbox_params=A.BboxParams(format='pascal_voc', label_fields=['category_ids'], min_visibility=0.5),
)

def augment_img(pdf_name, img_name, total_files):
    img = cv2.imread(osp(src_dir, 'imgs', pdf_name, img_name))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    dets_json = json.load(open(osp(src_dir, 'json', pdf_name, img_name.replace('.jpg','.json'))))
        
    label_map_label2id = {'unchecked':0, 'checked':1}
    label_map_id2label = {v:k for k,v in label_map_label2id.items()}

    bboxes, label_ids = [], []
    key_names = []
    for key_name in dets_json:
        if '<cb_' not in key_name:
            continue
        key_names.append(key_name)
        bbox = [dets_json[key_name]['xmin'], dets_json[key_name]['ymin'], dets_json[key_name]['xmax'], dets_json[key_name]['ymax'],]
        label_id = label_map_label2id[dets_json[key_name]['data']]
        bboxes.append(bbox)
        label_ids.append(label_id)

    transformed = transforms(image=img, bboxes=bboxes, category_ids=label_ids)

    if len(bboxes)!=0 and len(transformed['bboxes'])==0:
        if random.random()>0.3: # give it a chance to  
            for i in range(20):
                transformed = transforms(image=img, bboxes=bboxes, category_ids=label_ids)
                if len(transformed['bboxes'])!=0:
                    break

    new_img, new_bboxes, new_label_ids = transformed['image'], transformed['bboxes'], transformed['category_ids']
  
    new_dets_json = {}
    for idx in range(len(new_bboxes)):
        tmp_dict = {}
        key_name = key_names[idx]
        xmin, ymin, xmax, ymax = new_bboxes[idx]
        xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
        label_id = new_label_ids[idx]
        label = label_map_id2label[label_id]
        tmp_dict = {'xmin':xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax, 'state':label}
        new_dets_json[key_name] = tmp_dict

    img_out_path = osp(out_dir, 'imgs', pdf_name, img_name)
    json_out_path = osp(out_dir, 'json', pdf_name, img_name.replace('.jpg','.json'))

    cv2.imwrite(img_out_path, new_img)
    json.dump(new_dets_json, open(json_out_path, 'w'), indent=4)

    with lock:
        counter.value += 1
        print(f"Processed {counter.value}/{total_files}")


total_files=0
for root, dirs, files in os.walk(osp(src_dir, 'imgs')):
    for file in files:
        if file.endswith('.jpg'):
            total_files+=1

tasks = []
for pdf_name in pdf_names:
    img_names = os.listdir(osp(src_dir, 'imgs', pdf_name))
    os.makedirs(osp(out_dir, 'imgs', pdf_name))
    os.makedirs(osp(out_dir, 'json', pdf_name))

    for img_name in img_names:
        tasks.append([pdf_name, img_name, total_files])

with Pool(processes=28) as pool:
    pool.starmap(augment_img, tasks)

print('done')


