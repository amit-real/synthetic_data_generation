import os
import shutil
import json

osp = os.path.join
src_dir = 'OUT_DIR/0_export_pdf_meta'
syn_dir = 'TEMPLATE_PDF/synthetic_json'
pdf_names = os.listdir(syn_dir)
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]
out_dir = 'OUT_DIR/fixed_keys'
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

count=0
count_rev=0

keys = []

for pdf_name in pdf_names:
    print(pdf_name)
    os.makedirs(osp(out_dir, pdf_name))
    orig_json = json.load(open(osp(src_dir, pdf_name.replace(".pdf",".json"))))
    syn_json_names = os.listdir(osp(syn_dir, pdf_name))
    
    for syn_json_name in syn_json_names:
        page_num = syn_json_name.split('_')[0]
        syn_json = json.load(open(osp(syn_dir, pdf_name, syn_json_name)))
        
        orig_dict = {}
        for i in orig_json[page_num]:
            orig_dict[i['name']] = i['bbox']

        for key in orig_dict:
            if key not in syn_json:
                if '<cb' in key:
                    syn_json[key] = 'unchecked'
                    continue
                syn_json[key] = ''
                count+=1
                # keys.append(key)
        json.dump(syn_json, open(osp(out_dir, pdf_name, syn_json_name), 'w'), indent=4)

print(count)
print('done')


        
