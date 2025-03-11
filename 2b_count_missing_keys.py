import os
import shutil
import json

osp = os.path.join
src_dir = 'OUT_DIR/0_export_pdf_meta'
syn_dir = 'TEMPLATE_PDF/synthetic_json'
pdf_names = os.listdir(syn_dir)
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]

count=0
count_rev=0

keys = []

for pdf_name in pdf_names:
    print(pdf_name)
    # os.makedirs(osp(out_dir, pdf_name))
    orig_json = json.load(open(osp(src_dir, pdf_name.replace(".pdf",".json"))))
    syn_json_names = os.listdir(osp(syn_dir, pdf_name))
    
    for syn_json_name in syn_json_names:
        page_num = syn_json_name.split('.')[0]
        syn_json = json.load(open(osp(syn_dir, pdf_name, syn_json_name)))
        
        orig_dict = {}
        for i in orig_json[page_num]:
            orig_dict[i['name']] = i['bbox']

        for key in orig_dict:
            for entry in syn_json:
                if key not in entry:
                    count+=1

        for entry in syn_json:
            for key in entry:
                if key not in orig_dict:
                    count_rev+=1   

print(count, count_rev)
print('done')


        
