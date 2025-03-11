import cv2
import os
import shutil
osp = os.path.join

src_dir = 'OUT_DIR/5b_yolo_split'
out_dir = 'OUT_DIR/5c_bbox_plot'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

for idx, mode in enumerate(['train', 'val']):
    os.makedirs(osp(out_dir, mode))

    img_names = os.listdir(osp(src_dir, mode, 'images'))
    for idx2, img_name in enumerate(img_names):
        # if (idx2%100==0)==False:
        #     continue

        print(f'{idx+1}/{2}  {idx2+1}/{len(img_names)}  {mode}')
        img = cv2.imread(osp(src_dir, mode, 'images', img_name))
        img_w, img_h = img.shape[1], img.shape[0]

        with open(osp(src_dir, mode, 'labels', img_name.replace('.jpg', '.txt'))) as f:
            lines = f.readlines()

        for line in lines:
            label, xc, yc, w, h = line.strip().split(' ')
            xc, yc, w, h = float(xc)*img_w, float(yc)*img_h, float(w)*img_w, float(h)*img_h
            xmin, ymin, xmax, ymax = int(xc-(w/2)), int(yc-(h/2)), int(xc+(w/2)), int(yc+(h/2))
            # print(xmin, ymin, xmax, ymax)
            color = (0, 255, 0)
            if label=='0':
                color = (0, 0, 255)
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 2

            cv2.putText(img, label, (xmin, ymin+5), font, font_scale, color, thickness)

        cv2.imwrite(osp(out_dir, mode, img_name), img)
       
            


