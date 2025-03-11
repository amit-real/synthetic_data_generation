import os
import random
import shutil
osp = os.path.join

pdf_names = os.listdir('OUT_DIR/4_augmented/json')
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]
# pdf_names = pdf_names[::-1]  #to include SPQ.pdf into training set

yolo_dir = 'OUT_DIR/5a_yolo_format'
out_dir = 'OUT_DIR/5b_yolo_split'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

val_prcnt = 0.1
val_idx = int((1-val_prcnt)*len(pdf_names))
train_pdf_names = pdf_names[:val_idx]
val_pdf_names = pdf_names[val_idx:]

print(pdf_names)
print(val_idx)
print(train_pdf_names)
print(val_pdf_names)
# exit()
for idx, pdf_name in enumerate(train_pdf_names):
    os.makedirs(osp(out_dir, 'train', 'images'), exist_ok=True)
    os.makedirs(osp(out_dir, 'train', 'labels'), exist_ok=True)
    img_names = os.listdir(osp(yolo_dir, 'images'))
    
    for idx2, img_name in enumerate(img_names):
        # if random.random()<0.3:
        #     continue
        print(f'train  {idx+1}/{len(train_pdf_names)}  {idx2+1}/{len(img_names)}  {pdf_name}  {img_name}')
        txt_name = img_name.replace(".jpg", ".txt")
        if pdf_name in img_name:
            txt_path = osp(yolo_dir, 'labels', txt_name)
            txt_content = open(txt_path).read().strip()
            # if len(txt_content)==0:
            #     if random.random()<0.8:
            #         continue
            shutil.copy(osp(yolo_dir, 'images', img_name), osp(out_dir, 'train', 'images', img_name))
            shutil.copy(osp(yolo_dir, 'labels', txt_name), osp(out_dir, 'train', 'labels', txt_name))


for idx, pdf_name in enumerate(val_pdf_names):
    os.makedirs(osp(out_dir, 'val', 'images'), exist_ok=True)
    os.makedirs(osp(out_dir, 'val', 'labels'), exist_ok=True)
    img_names = os.listdir(osp(yolo_dir, 'images'))

    for idx2, img_name in enumerate(img_names):
        # if random.random()<0.4:
        #     continue

        print(f'val  {idx+1}/{len(val_pdf_names)}  {idx2+1}/{len(img_names)}  {pdf_name}  {img_name}')
        txt_name = img_name.replace(".jpg", ".txt")
        if pdf_name in img_name:
            txt_path = osp(yolo_dir, 'labels', txt_name)
            txt_content = open(txt_path).read().strip()
            # if len(txt_content)==0:
            #     if random.random()<0.6:
            #         continue

            shutil.copy(osp(yolo_dir, 'images', img_name), osp(out_dir, 'val', 'images', img_name))
            shutil.copy(osp(yolo_dir, 'labels', txt_name), osp(out_dir, 'val', 'labels', txt_name))