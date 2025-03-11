import os
import shutil
import json

json_dir = 'OUT_DIR/0_export_pdf_meta'
syn_json_dir = 'TEMPLATE_PDF/synthetic_json'

pdf_names = os.listdir(syn_json_dir)
pdf_names = [i for i in pdf_names if i.endswith('.pdf')]

not_found = {}
keys_not_found = {}

for pdf_name in pdf_names:
    just_name = pdf_name.replace('.pdf', '')
    template_json_path = os.path.join(json_dir, f'{just_name}.json')
    template_json = json.load(open(template_json_path))
    
    # if pdf_name=='RCSD_Representative_Capacity_Signature.pdf':
    # #     continue
    #     print(template_json_path)
    #     exit()

    for page_num in template_json:
        print(f'{pdf_name}  {page_num} -----------')
        if page_num=='meta_info':
            continue
        keys = [i['name'] for i in template_json[page_num]]
        if len(keys)==0:  #there is not fillable element in the pdf template
            continue 

        syn_data_path = os.path.join(syn_json_dir, pdf_name, f'{page_num}.json')
        if os.path.exists(syn_data_path)==False:
            print(f'page: {page_num} not found in synthetic data')
            continue

        syn_data = json.load(open(syn_data_path))
        
        for entry in syn_data:
            syn_keys = list(entry.keys())
            
            if len(keys)!=len(syn_keys):
                print('\t\t 1 not found')
                if pdf_name not in not_found:
                    not_found[pdf_name]=0
                    print(keys)
                    print(syn_keys)
                    exit()
                not_found[pdf_name]+=1
                

            for k1 in keys:
                if k1 not in syn_keys:
                    print(f'\t\t 2 not found: {k1}')
                    # exit()
                    if pdf_name not in not_found:
                        not_found[pdf_name]=0
                    not_found[pdf_name]+=1

                    if f'{pdf_name}_{page_num}' not in keys_not_found:
                        keys_not_found[f'{pdf_name}_{page_num}']=[]
                    if k1 not in keys_not_found[f'{pdf_name}_{page_num}']:
                        keys_not_found[f'{pdf_name}_{page_num}'].append(k1)


            for k1 in syn_keys:
                if k1 not in keys:
                    print(f'\t\t 3 not found: {k1}')
                    # exit()
                    if pdf_name not in not_found:
                        not_found[pdf_name]=0
                    not_found[pdf_name]+=1

                    if f'{pdf_name}_{page_num}' not in keys_not_found:
                        keys_not_found[f'{pdf_name}_{page_num}']=[]
                    if k1 not in keys_not_found[f'{pdf_name}_{page_num}']:
                        keys_not_found[f'{pdf_name}_{page_num}'].append(k1)
    print()

print(not_found)
print(keys_not_found)