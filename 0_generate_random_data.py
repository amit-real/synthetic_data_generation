import fitz
import cv2
import numpy as np
import os
import shutil
import unicodedata
from pathlib import Path
import tempfile
import json
import random
import string
from faker import Faker


def get_page_raster(page: fitz.Page, target_width: int, target_height: int) -> np.ndarray:
    scale_w = target_width / page.rect.width
    scale_h = target_height / page.rect.height
    matrix = fitz.Matrix(scale_w, scale_h)
    pix = page.get_pixmap(matrix=matrix)
    with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as temp_file: 
        pix.save(temp_file.name)
        img = cv2.imread(temp_file.name)
    return img


def scale_bbox(bbox: dict, scale_w: float, scale_h: float) -> dict:
    scaled_bbox = {}
    scaled_bbox['xmin'] = bbox['xmin']*scale_w
    scaled_bbox['ymin'] = bbox['ymin']*scale_h
    scaled_bbox['xmax'] = bbox['xmax']*scale_w
    scaled_bbox['ymax'] = bbox['ymax']*scale_h
    return scaled_bbox


def render_textfield_annotations(page: fitz.Page) -> fitz.Page:
    for widget in page.widgets():
        field_name = widget.field_name
        field_type = widget.field_type # 2 for checkbox, 7 for text_area
        text =  widget.field_value
        xmin, ymin, xmax, ymax = widget.rect
  
        if field_type==7:  # a textfield
            font_size = 10
            width, height = abs(xmax-xmin), abs(ymax-ymin)

            if 'init>' in field_name.lower():
                font_size = 7

            x_start = xmin + (width/2) - ((len(field_name)*font_size)/2)
            if x_start<xmin:
                x_start=xmin+4

            y_start = ymax-2
            r,g,b = 4,139,255
            r,g,b = r/256, g/256, b/256
            page.insert_text((x_start,y_start), field_name, fontname = "helv", fontsize=font_size, rotate=0, color=(r,g,b))
    
    return page     


def get_page_widgets(page: fitz.Page, target_width: int, target_height: int) -> list:
    scale_w = target_width / page.rect.width
    scale_h = target_height / page.rect.height

    widgets_list = []
    
    for widget in page.widgets():
        field_name = widget.field_name
        field_type = widget.field_type # 2 for checkbox, 7 for text_area
        text =  widget.field_value
        xmin, ymin, xmax, ymax = widget.rect        
        xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = xmin*scale_w, ymin*scale_h,\
                                    xmax*scale_w, ymax*scale_h

        tmp_dict = {}
        if field_type==2:
            tmp_dict['name'] = field_name.strip()
            tmp_dict['type'] = 'checkbox'
            tmp_dict['state'] = text.strip()
            tmp_dict['bbox'] = {'xmin':xmin_scaled, 
                                'ymin':ymin_scaled, 
                                'xmax':xmax_scaled, 
                                'ymax':ymax_scaled
                                }

        elif field_type==7:
            tmp_dict['name'] = field_name.strip()
            tmp_dict['type'] = 'text_area'
            tmp_dict['text'] = text.strip()
            tmp_dict['bbox'] = {'xmin':xmin_scaled, 
                                'ymin':ymin_scaled, 
                                'xmax':xmax_scaled, 
                                'ymax':ymax_scaled
                                }
            
        widgets_list.append(tmp_dict)
    return widgets_list
            

def get_xstart_ystart(widget_type: str, text: str, xmin: int, ymin: 
                      int, xmax: int, ymax: int, font_size: int
                      ) -> tuple:
    if widget_type=='checkbox': #if it is a checkbox, then return same position
        return xmin+1, ymax-2
    
    width, height = abs(xmax-xmin), abs(ymax-ymin)
    align_x = random.choice(['left', 'center', 'right'])
    # align_y = random.choice(['above', 'same', 'below'])

    if align_x=='left':
        x_buffer, y_buffer = random.choice([1,2,3]), random.choice([0,1,2,3,4])
        x_start, y_start = xmin+x_buffer, ymax-y_buffer

        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start
        
    elif align_x=='center':
        x_buffer, y_buffer = random.choice([-1,-2,-3,0,1,2,3]), random.choice([0,1,2,3,4])
        x_start = xmin + (width/2) - ((len(text)*font_size)/2)
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer
        
        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start

    elif align_x=='right':
        x_buffer, y_buffer = random.choice([-1,-2,-3,0]), random.choice([0,1,2,3,4])
        x_start = xmax - ((len(text)*font_size)) - 4
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer

        if x_start<xmin:
            x_start=xmin+4
        return x_start, y_start


def add_signatures_to_textfields(page, signature_dir):
    signature_dir = Path(signature_dir)
    signature_files = list(signature_dir.rglob('*.png')) + list(signature_dir.rglob('*.jpg'))
    
    if not signature_files:
        print(f"No signature files found in {signature_dir}")
        return page, {}
    
    gt = {}
    sign_count = 0

    for widget in page.widgets():
        if  widget.field_type != 7:
            continue

        if random.random() > 0.6:
            continue

        xmin, ymin, xmax, ymax = widget.rect
        widget_w, widget_h = xmax - xmin, ymax - ymin
        
        sig_filename = random.choice(signature_files)
        
        with open(str(sig_filename), "rb") as img_file:
            signature_bytes = img_file.read()
        
        img_rect = fitz.Rect(0, 0, 0, 0)
        try:
            img_doc = fitz.open(stream=signature_bytes, filetype="png")
            if img_doc.page_count > 0:
                img_page = img_doc[0]
                img_rect = img_page.rect
                img_doc.close()
        except:
            try:
                img_doc = fitz.open(stream=signature_bytes, filetype="jpeg")
                if img_doc.page_count > 0:
                    img_page = img_doc[0]
                    img_rect = img_page.rect
                    img_doc.close()
            except Exception as e:
                print(f"Error reading image dimensions: {e}")
                continue
                 
        sign_aspect_ratio = img_rect.width / img_rect.height
        target_height = int(widget_h * random.uniform(1.5, 2.1))
        target_width = int(target_height * sign_aspect_ratio)
        
        if target_width > widget_w * 0.9:
            target_width = int(widget_w * 0.9)
            target_height = int(target_width / sign_aspect_ratio)
                
        position = random.choice(['start', 'center'])

        if position == 'start':
            x_pos = xmin + random.uniform(-20, 20)
            y_pos = ymin + (widget_h - target_height) / 2 + random.uniform(-10, 10)
       
        elif position=='center':
            x_pos = xmin + (widget_w - target_width) / 2 + random.uniform(-10, 10)
            y_pos = ymin + (widget_h - target_height) / 2 + random.uniform(-10, 10)
            
        x_pos = max(xmin, min(x_pos, xmax - target_width))
        y_pos = max(ymin, min(y_pos, ymax - target_height))
        
        rect = fitz.Rect(x_pos, y_pos, x_pos + target_width, y_pos + target_height)
        page.insert_image(rect, stream=signature_bytes)
        
        tmp_dict =  {
            "value": "signature",
            "bbox":{
                "xmin": int(x_pos),
                "ymin": int(y_pos),
                "xmax": int(x_pos + target_width),
                "ymax": int(y_pos + target_height),
            }
        }
        gt[f"<SIGN_{sign_count}>"] = tmp_dict
        sign_count += 1
    
    return page, gt

    
def add_random_checkboxes(page: fitz.Page, schema: dict[str, str]) -> tuple[fitz.Page, dict]:
    page.insert_font(fontfile='DejaVuSans.ttf', fontname="DVS")
    gt = {}

    for widget in page.widgets():
        field_name = widget.field_name

        if "<cb_" not in field_name :
            continue

        font = 'DVS'
        xmin, ymin, xmax, ymax = widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1
        xc, yc = xmin, ymax
        outer_radius = (xmax-xmin)

        page.delete_widget(widget)

        if field_name not in schema: # if not specified in schema, then don't touch it
            gt[field_name] = {
                "state": "unchecked",
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
            continue
        
        if random.random() > 0.5:
            gt[field_name] = {
                "state": "unchecked",
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
            continue

        if random.random() > 0.7: # adding under-shadow effect to cbox
            line_annot = page.add_line_annot((xmin,ymax), (xmax,ymax))
            line_annot.set_colors(stroke=(0.25, 0.25, 0.25))
            line_annot.set_border(width=2)
            line_annot.update()

        elif random.random() > 0.7: # making all boundaries of cbox bold
            width = random.choice([1,2])
            coord_set = [[(xmin,ymin), (xmax,ymin)], 
                         [(xmax,ymin), (xmax,ymax)],
                         [(xmax,ymax), (xmin,ymax)], 
                         [(xmin,ymax), (xmin,ymin)]
                        ]
            for coord in coord_set: # covering 4 boundaries of cbox
                line_annot = page.add_line_annot(coord[0], coord[1])
                line_annot.set_colors(stroke=(0,0,0))
                line_annot.set_border(width=width)
                line_annot.update()


        r,g,b = 0,0,0
        if random.random()>0.5:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
            
        symbol = random.choice(["●", "◉", "✖", "X", "✔", "✓"])
        font_size = int(outer_radius * random.uniform(1, 1.8))
        page.insert_text((xc , yc ), symbol,
                        fontsize=font_size,
                        color=(r / 255, g / 255, b / 255),
                        fontname=font)
        
        gt[field_name] = {
            "state": "checked",
            "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
        }
  
    return page, gt


def remove_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn' and ord(c) < 128)

def trim_text_to_width(text: str, max_width: int, font_size: int=13, char_width: int=7) -> str:
    max_chars = int(max_width / (char_width * (font_size / 13)))
    if len(text) > max_chars:
        return text[:max_chars - 2]
    return text

def scale_coords(
    json_data: dict[str, dict], 
    page: fitz.Page, target_width: int, 
    target_height: int
    ) -> dict[str, dict]:

    scale_w = target_width / page.rect.width
    scale_h = target_height / page.rect.height

    for field_name, data in json_data.items():
        xmin, ymin, xmax, ymax = data['bbox']['xmin'], data['bbox']['ymin'], data['bbox']['xmax'], data['bbox']['ymax']
        xmin, ymin, xmax, ymax = int(xmin*scale_w), int(ymin*scale_h), int(xmax*scale_w), int(ymax*scale_h)
        
        json_data[field_name]['bbox'] = {
        'xmin': xmin, 
        'ymin': ymin, 
        'xmax': xmax, 
        'ymax': ymax
        }

    return json_data


def add_fake_textfield_data(page: fitz.Page, schema: dict[str, str]) -> tuple[fitz.Page, dict[str, str]]:
    locales = [
        'en_US', 'en_GB', 'en_CA', 'en_AU', 'en_NZ', 'en_IE',  # English-speaking
        'en_IN', 'ja_JP', 'ko_KR', 'zh_CN', 'zh_TW',  # Asian
        'fr_FR', 'de_DE', 'it_IT', 'nl_NL', 'pt_PT',  # European
        'es_MX', 'es_ES', 'es_CO', 'es_AR', 'es_CL'  # Spanish-speaking (Latin America and Europe)
    ]
    fake = Faker()

    gt = {}
    
    for widget in page.widgets():
        widget_name = widget.field_name
        
        font_name = random.choice(['cobi', 'cobo', 'coit', 'cour', 'hebo', 'heit', 'helv', 'tibi', 'tibo', 'tiit', 'tiro'])
        font_size = random.choice([9, 10, 11, 12, 13])
        
        xmin, ymin, xmax, ymax = widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1

        r,g,b = 0,0,0
        if random.random()>0.4:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
        r,g,b = r/256, g/256, b/256

        if widget_name not in schema:
            if '<cb_' in widget_name:
                gt[widget_name] = {
                    "state": "unchecked",
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
            else:
                gt[widget_name] = {
                        "value": "",
                        "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                    }

        for field_name, field_type in schema.items():
            if field_name != widget_name:
                continue
            
            if field_type == "checkbox" or field_name.startswith("<cb_"):
                continue
            
            if random.random() > 0.7:
                gt[field_name] = {
                    "value": "",
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                continue

            if field_type == "name":
                locale = random.choice(locales)
                localized_fake = Faker(locale)
                text = localized_fake.name()
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "company":
                locale = random.choice(locales)
                localized_fake = Faker(locale)
                text = localized_fake.company()
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "date":
                text = fake.date(pattern='%m/%d/%Y')
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "license":
                letters = ''.join(random.choices(string.ascii_uppercase, k=2))
                digits = ''.join(random.choices(string.digits, k=7))
                text = f"{letters}{digits}"
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "initials":
                locale = random.choice(locales)
                localized_fake = Faker(locale)
                text = f"{localized_fake.first_name()[0]}.{localized_fake.last_name()[0]}."
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break
            
            elif field_type == "address":
                locale = random.choice(locales)
                localized_fake = Faker(locale)
                text = localized_fake.address().replace("\n", ", ")
                text = remove_accents(text)
                text = trim_text_to_width(text, xmax-xmin, font_size, char_width=7)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
                
                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break
            
            elif field_type == "sentence":
                text = fake.sentence(nb_words=random.randint(5, 12))
                text = remove_accents(text)
                text = trim_text_to_width(text, xmax-xmin, font_size, char_width=7)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break
            elif field_type == "county" or field_type == "city":
                text = fake.city()
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "country":
                text = fake.country()
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break

            elif field_type == "number":
                text = str(random.randint(1, 100))
                text = trim_text_to_width(text, xmax-xmin, font_size, char_width=8)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break
            elif field_type == "word":
                text = fake.word()
                text = remove_accents(text)
                x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
                page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

                gt[field_name] = {
                    "value": text,
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                break
            else:
                gt[field_name] = {
                    "value": "",
                    "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                }
                print(f"Unknown field type '{field_type}' for field '{field_name}'.")
                break

    return page, gt


def add_fake_data(page: fitz.Page, schema: dict[str, str]) -> tuple[fitz.Page, dict]:
    page, gt_checkboxes = add_random_checkboxes(page, schema)
    page, gt_textfield = add_fake_textfield_data(page, schema)
    page, gt_signatures = add_signatures_to_textfields(page, signature_dir)
    gt = {**gt_checkboxes, **gt_textfield, **gt_signatures}
    return page, gt


def validate_template_and_schemas(template_pdf_dir: str, 
                                  template_schema_dir: str
    ) -> None:
    pdf_paths = list(template_pdf_dir.rglob('*.pdf'))

    invalid = False
    critical_errors = []
    warnings = []

    for idx, pdf_path in enumerate(pdf_paths):
        pdf_name = pdf_path.name
        page_nums = len(fitz.open(str(pdf_path)))

        if not os.path.exists(template_schema_dir/pdf_name.replace('.pdf', '.json')):
            warnings.append(f"warning: Schema file not found for '{pdf_name}'")
            continue
        
        doc = fitz.open(str(pdf_path))
        schema = json.load(open(template_schema_dir/pdf_name.replace('.pdf', '.json')))        
        schema = {int(k): v for k, v in schema.items()}
        
        for page_num in range(page_nums):
            page = doc.load_page(page_num)

            page_field_names = [i.field_name for i in page.widgets()]

            if len(page_field_names)==0:
                continue

            if page_num+1 not in schema:
                warnings.append(f"warning: Page missing in schema for '{pdf_name}' page {page_num+1}")
                continue

            page_schema = schema[page_num+1]

            for field_name, field_type in page_schema.items():
                if field_type not in SUPPORTED_TYPES:
                    critical_errors.append(f"Unsupported type '{field_type}' in '{pdf_name}' for page {page_num+1}.")
                    invalid = True
        doc.close()
        
    if len(warnings) > 0:
        print('WARNINGS:')
        for warning in warnings:
            print(warning)

    print('')
    if len(critical_errors) > 0:
        print('CRITICAL ERRORS:')
        for error in critical_errors:
            print(error)
            
    print()
    if invalid:
        print('Please fix the errors first...')
        exit()


PAGE_WIDTH, PAGE_HEIGHT = 2048, 2650
SAMPLES_PER_PAGE = 3
SUPPORTED_TYPES = ['checkbox', 'name', 'company', 'date', 'license', 'county', 'city', 
                   'initials', 'address', 'sentence', 'number', 'initials', 'country',
                   'word']

template_pdf_dir = Path('TEMPLATE_PDF/annotated_pdfs')
template_schema_dir = Path('TEMPLATE_PDF/schema')
signature_dir = Path('TEMPLATE_PDF/signatures')
pdf_paths = list(template_pdf_dir.rglob('*.pdf'))

out_dir = Path('out')
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)

validate_template_and_schemas(template_pdf_dir, template_schema_dir)

for idx, pdf_path in enumerate(pdf_paths):
    pdf_name = pdf_path.name    
    page_nums = len(fitz.open(str(pdf_path)))

    schema = json.load(open(template_schema_dir/pdf_name.replace('.pdf', '.json')))
    schema = {int(k): v for k, v in schema.items()}
    os.makedirs(out_dir/pdf_name/"image", exist_ok=True)
    os.makedirs(out_dir/pdf_name/"json", exist_ok=True)
    os.makedirs(out_dir/pdf_name/"plot", exist_ok=True)

    for page_num in range(page_nums):
        if page_num+1 not in schema:
            continue
        for sample_no in range(SAMPLES_PER_PAGE):
            print(f"{idx+1}/{len(pdf_paths)} {page_num+1}/{page_nums} {sample_no+1}/{SAMPLES_PER_PAGE}  {pdf_path}")
            doc = fitz.open(str(pdf_path))
            page = doc.load_page(page_num)
            page_schema = schema[page_num+1]

            page, gt = add_fake_data(page, page_schema)
            gt = scale_coords(gt, page, PAGE_WIDTH, PAGE_HEIGHT)
            img = get_page_raster(page, PAGE_WIDTH, PAGE_HEIGHT)
            doc.close

            json.dump(gt, open(out_dir/pdf_name/"json"/f'{page_num+1}_{sample_no}.json', 'w'), indent=4)
            cv2.imwrite(out_dir/pdf_name/"image"/f'{page_num+1}_{sample_no}.jpg', img)

            for field_name, entry in gt.items():
                bbox = entry['bbox']
                xmin, ymin, xmax, ymax = bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']
                xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            cv2.imwrite(out_dir/pdf_name/"plot"/f'{page_num+1}_{sample_no}_bbox.jpg', img)

print('Done...!')