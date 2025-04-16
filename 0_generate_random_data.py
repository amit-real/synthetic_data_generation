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


def do_bboxes_overlap(bbox1: dict, bbox2: dict) -> bool:
    if (bbox1['xmax'] <= bbox2['xmin'] or bbox1['xmin'] >= bbox2['xmax'] or
        bbox1['ymax'] <= bbox2['ymin'] or bbox1['ymin'] >= bbox2['ymax']):
        return False
    return True


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


def get_fontsize_for_target_height(fontfile: str, target_height_px: float) -> float:
    font = fitz.Font(fontfile=fontfile)
    ascender = font.ascender
    descender = abs(font.descender)
    total_font_units = ascender + descender
    fontsize = target_height_px / total_font_units
    return fontsize


def get_font_baseline_y(fontfile: str, fontsize: float, ymin: float, ymax: float) -> float:
    font = fitz.Font(fontfile=fontfile)
    
    ascent = font.ascender / 1000 * fontsize
    descent = abs(font.descender) / 1000 * fontsize

    bbox_height = ymax - ymin
    baseline_y = ymin + (bbox_height + (ascent - descent)) / 2

    return baseline_y


def add_signatures_to_textfields(page, sign_enclosure_dir):
    font_names = os.listdir('TEMPLATE_PDF/fonts')
    font_dict = {i: f'TEMPLATE_PDF/fonts/{i}' for i in font_names}

    for font_name in font_dict:
        page.insert_font(fontfile=font_dict[font_name], fontname=font_name)   
    
    sign_enclosure_files = os.listdir(sign_enclosure_dir) 
    
    if not sign_enclosure_files:
        print(f"No signature files found in {sign_enclosure_dir}")
        return page, {}
    
    gt = {}
    sign_count = 0

    locales = [
        'en_US', 'en_GB', 'en_CA', 'en_AU', 'en_NZ', 'en_IE',  # English-speaking
        'en_IN',# 'ja_JP', 'ko_KR', 'zh_CN', 'zh_TW',  # Asian
        'fr_FR', 'de_DE', 'it_IT', 'nl_NL', 'pt_PT',  # European
        'es_MX', 'es_ES', 'es_CO', 'es_AR', 'es_CL'  # Spanish-speaking (Latin America and Europe)
    ]

    for widget in page.widgets():
        widget_name = widget.field_name
        widget_type = widget.field_type_string
        
        if widget_type!='Text':
            continue

        if random.random() > 0.3:
            continue

        xmin, ymin, xmax, ymax = widget.rect
        widget_w, widget_h = xmax - xmin, ymax - ymin
        
        sign_filename = random.choice(sign_enclosure_files)
        sign_path = sign_enclosure_dir/sign_filename
        with open(str(sign_path), "rb") as img_file:
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
        target_height = int(widget_h * random.uniform(1.3, 2.5))
        target_width = int(target_height * sign_aspect_ratio)
        
        if target_width >= widget_w * 0.8:
            target_width = int(widget_w * 0.9)
            target_height = int(target_width / sign_aspect_ratio)
                
        position = random.choice(['start', 'center'])

        if position == 'start':
            img_xmin = xmin + random.uniform(-5, 20)
            img_ymin = ymin - random.choice(list(range(-5,20)))
            img_xmax = img_xmin + target_width
            img_ymax = img_ymin + target_height
            if img_xmin>=img_xmax or img_ymin>=img_ymax:
                continue
        
        elif position=='center':
            img_xmin = xmin + (widget_w - target_width) / 2 + random.uniform(-5, 10)
            img_ymin = ymin - random.choice(list(range(-5,20)))
            img_xmax = img_xmin + target_width
            img_ymax = img_ymin + target_height
            if img_xmin>=img_xmax or img_ymin>=img_ymax:
                continue
            
        if 'real' not in sign_filename:
            # print(sign_filename, img_xmin, img_ymin, img_xmax, img_ymax)
            rect = fitz.Rect(img_xmin, img_ymin, img_xmax, img_ymax)
            page.insert_image(rect, stream=signature_bytes)
            if img_xmin>=img_xmax or img_ymin>=img_ymax:
                continue
        
        r,g,b = 0,0,0
        if random.random()>0.7:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
        r,g,b = r/256, g/256, b/256
        
        locale = random.choice(locales)
        localized_fake = Faker(locale)
        first_name = localized_fake.first_name()
        
        font_name = random.choice(list(font_dict.keys()))
        font_path = font_dict[font_name]
        font = fitz.Font(fontfile=font_path)
        
        text_height = (img_ymax-img_ymin)*random.uniform(0.8, 1.2)
        font_size = get_fontsize_for_target_height(font_path, text_height)
        text_width = font.text_length(first_name, fontsize=font_size)
        
        text_xmin = img_xmin + random.randint(1, 10)
        text_xmax = text_xmin + text_width
        text_ymax = img_ymax - random.randint(1, 5)
        text_ymin = text_ymax - text_height
        
        #if its purple colored logo, then we need to shift it to the right
        if 'real' in sign_filename:
            text_height = (ymax-ymin)*random.uniform(1.5, 2)
            font_size = get_fontsize_for_target_height(font_path, text_height)
            text_width = font.text_length(first_name, fontsize=font_size)
            
            text_xmin = xmin + random.randint(5, 10)
            text_xmax = text_xmin + text_width
            text_ymin = ymin  
            text_ymax = ymax
            
            img_height = widget_h * random.uniform(0.4, 0.8)
            img_ymin = text_ymin + random.choice(list(range(2, 5)))
            img_ymax = img_ymin + img_height

            # recompute width using original aspect ratio
            img_width = img_height * sign_aspect_ratio
            img_xmin = text_xmax + random.uniform(2, 5)
            img_xmax = img_xmin + img_width
            
            rect = fitz.Rect(img_xmin, img_ymin, img_xmax, img_ymax)
            page.insert_image(rect, stream=signature_bytes)
            
        text_y_baseline = text_ymax - 2
        
        page.insert_text(
            (text_xmin, text_y_baseline),
            first_name,
            fontname=font_name,
            fontsize = font_size,
            color=(r, g, b)
        )

        tmp_dict =  {
            "type": "signature",
            "value": "signature",
            "bbox":{
                    "xmin": min(img_xmin, text_xmin),
                    "ymin": min(img_ymin, text_ymin),
                    "xmax": max(img_xmax, text_xmax),
                    "ymax": max(img_ymax, text_ymax)
                    }
        }
        gt[f"<SIGN_{sign_count}>"] = tmp_dict
        sign_count += 1
    
    return page, gt

    
def add_random_checkboxes(page: fitz.Page, copy_paste: bool = True) -> tuple[fitz.Page, dict]:
    font = 'DVS'
    page.insert_font(fontfile='TEMPLATE_PDF/fonts/DejaVuSans.ttf', fontname=font)
    page_w, page_h = int(page.rect.width), int(page.rect.height)
    gt = {}

    for widget in page.widgets():
        widget_name = widget.field_name
        widget_type = widget.field_type_string

        if widget_type != 'CheckBox':
            continue

        xmin, ymin, xmax, ymax = widget.rect
        width = xmax - xmin
        height = ymax - ymin
        font_size = int(min(width, height) * random.uniform(0.9, 1.6))
        page.delete_widget(widget)

        # keep 40% cboxes empty
        if random.random() <= 0.4:
            gt[widget_name] = {
                "widget_type": "checkbox",
                "state": "unchecked",
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
            continue

        r,g,b = 0,0,0
        if random.random()>0.5:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
        r, g, b = r/256, g/256, b/256 
        symbol = random.choice(["●", "◉", "✖", "X", "✔", "✓"])
        page.insert_text((xmin + 1, ymax - 2), symbol, fontsize=font_size, fontname=font, color=(0, 0, 0))

        gt[widget_name] = {
            "widget_type": "checkbox",
            "state": "checked",
            "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
        }

    # Copy-paste augmentation
    if copy_paste and len(gt)>0:
        for copied_idx in range(random.randint(1, max(len(gt), 10))):
            src_key = random.choice(list(gt.keys()))
            src_cbox = gt[src_key]
            bbox = src_cbox['bbox']
            width =  bbox['xmax'] - bbox['xmin']
            height = bbox['ymax'] - bbox['ymin']
            font_size = int(min(width, height) * random.uniform(0.9, 1.6))
            
            for _ in range(20):
                xmin = random.randint(0, page_w)
                ymin = random.randint(0, page_h)
                xmax = xmin + width
                ymax = ymin + height
                
                if xmax>=page_w or ymax>=page_h:
                    continue
                
                does_overlap = False
                for key, gt_cbox in gt.items():
                    copied_bbox = {'xmin': xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax}
                    gt_bbox = gt_cbox['bbox']
                    if do_bboxes_overlap(copied_bbox,gt_bbox)==True:
                        does_overlap = True
                        break
                if not does_overlap:
                    break                

            # Whiten background
            pad_px = 3
            white_background = fitz.Rect(xmin-pad_px, ymin-pad_px, xmax+pad_px, ymax+pad_px)
            cbox_boundary = fitz.Rect(xmin, ymin, xmax, ymax)
            page.draw_rect(white_background, color=(1, 1, 1), fill=(1, 1, 1), width=0)
            page.draw_rect(cbox_boundary, color=(0, 0, 0), width=random.uniform(1, 2))
            
            r,g,b = 0,0,0
            if random.random()>0.4:
                r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
            r,g,b = r/256, g/256, b/256
            
            symbol = random.choice(["●", "◉", "✖", "X", "✔", "✓"])
            page.insert_text((xmin, ymax), symbol, fontsize=font_size, color=(r,g,b), fontname=font)

            gt[f"<cb_COPIED_{copied_idx}>"] = {
                "widget_type": "checkbox",
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

def select_text_widthwise(fake_dict: dict, max_chars: int) -> str:
    min_len_diff = 10000
    min_dif_text = ''
    
    for datatype, text in fake_dict.items():
        len_diff = abs(len(text) - max_chars)
        if len_diff < min_len_diff:
            min_len_diff = len_diff
            min_dif_text = text
            
    if len(min_dif_text)>=max_chars:
        return min_dif_text[:max_chars - 2]  

    return min_dif_text


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


def generate_fake_data():
    locales = [
        'en_US', 'en_GB', 'en_CA', 'en_AU', 'en_NZ', 'en_IE',  # English-speaking
        'en_IN', #'ja_JP', 'ko_KR', 'zh_CN', 'zh_TW',  # Asian
        'fr_FR', 'de_DE', 'it_IT', 'nl_NL', 'pt_PT',  # European
        'es_MX', 'es_ES', 'es_CO', 'es_AR', 'es_CL'  # Spanish-speaking (Latin America and Europe)
    ]
    fake = Faker()
    
    data_types = ['name', 'company', 'date', 'license', 'initials', 'address', 
                    'sentence', 'county', 'city', 'country', 'number', 'word'
                ]

    fake_dict = {}
    
    for data_type in data_types:
        if data_type == "name":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.name()
            text = remove_accents(text)
            fake_dict[data_type] = text

        elif data_type == "company":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.company()
            text = remove_accents(text)
            fake_dict[data_type] = text
            
        elif data_type == "date":
            text = fake.date(pattern='%m/%d/%Y')
            text = remove_accents(text)
            fake_dict[data_type] = text

        elif data_type == "license":
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            digits = ''.join(random.choices(string.digits, k=7))
            text = f"{letters}{digits}"
            text = remove_accents(text)
            fake_dict[data_type] = text

        elif data_type == "initials":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = f"{localized_fake.first_name()[0]}.{localized_fake.last_name()[0]}."
            text = remove_accents(text)
            fake_dict[data_type] = text
        
        elif data_type == "address":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.address().replace("\n", ", ")
            text = remove_accents(text)
            fake_dict[data_type] = text
        
        elif data_type == "sentence":
            text = fake.sentence(nb_words=random.randint(5, 12))
            text = remove_accents(text)
            fake_dict[data_type] = text
        
        elif data_type == "county" or data_type == "city":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.city()
            text = remove_accents(text)
            fake_dict[data_type] = text

        elif data_type == "country":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.country()
            text = remove_accents(text)
            fake_dict[data_type] = text

        elif data_type == "number":
            text = str(random.randint(1, 100))
            fake_dict[data_type] = text
        
        elif data_type == "word":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.word()
            text = remove_accents(text)
            fake_dict[data_type] = text
            
    return fake_dict


def add_fake_textfield_data(page: fitz.Page) -> tuple[fitz.Page, dict[str, str]]:
    gt = {}
    for widget in page.widgets():
        widget_name = widget.field_name
        widget_type = widget.field_type_string
        
        if widget_type!='Text':
            continue
              
        xmin, ymin, xmax, ymax = widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1
        width = xmax-xmin

        if random.random() < 0.2:
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": "",
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
            continue

        
        r,g,b = 0,0,0
        if random.random()>0.4:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
        r,g,b = r/256, g/256, b/256
          
        font_name = random.choice(['cobi', 'cobo', 'coit', 'cour', 'hebo', 'heit', 'helv', 'tibi', 'tibo', 'tiit', 'tiro'])
        font_size = random.choice([9, 10, 11, 12, 13])
        
        char_size = random.choice([7,8,9])
        max_chars =int(width / (char_size * (font_size / 13)))
        
        fake_dict = generate_fake_data()
        text = select_text_widthwise(fake_dict, max_chars)

        x, y = get_xstart_ystart('textfield', text, xmin, ymin, xmax, ymax, font_size)
        page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
        
        gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
    return page, gt


def add_fake_textfield_data_bak(page: fitz.Page) -> tuple[fitz.Page, dict[str, str]]:
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
        widget_type = widget.field_type_string
        
        if widget_type!='Text':
            continue
                
        font_name = random.choice(['cobi', 'cobo', 'coit', 'cour', 'hebo', 'heit', 'helv', 'tibi', 'tibo', 'tiit', 'tiro'])
        font_size = random.choice([9, 10, 11, 12, 13])
        
        xmin, ymin, xmax, ymax = widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1

        r,g,b = 0,0,0
        if random.random()>0.4:
            r,g,b = random.randint(1, 200), random.randint(1, 200), random.randint(1, 200)
        r,g,b = r/256, g/256, b/256

        data_types = ['name', 'company', 'date', 'license', 'initials', 'address', 
                      'sentence', 'county', 'city', 'country', 'number', 'word']
        
        field_type = random.choice(data_types)
            
        if random.random() < 0.1:
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": "",
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
            continue

        if field_type == "name":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.name()
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "company":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.company()
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "date":
            text = fake.date(pattern='%m/%d/%Y')
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "license":
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            digits = ''.join(random.choices(string.digits, k=7))
            text = f"{letters}{digits}"
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "initials":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = f"{localized_fake.first_name()[0]}.{localized_fake.last_name()[0]}."
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
        elif field_type == "address":
            locale = random.choice(locales)
            localized_fake = Faker(locale)
            text = localized_fake.address().replace("\n", ", ")
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            text = trim_text_to_width(text, xmax-xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))
            
            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
        elif field_type == "sentence":
            text = fake.sentence(nb_words=random.randint(5, 12))
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax-xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
        elif field_type == "county" or field_type == "city":
            text = fake.city()
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "country":
            text = fake.country()
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }

        elif field_type == "number":
            text = str(random.randint(1, 100))
            text = trim_text_to_width(text, xmax-xmin, font_size, char_width=8)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
        elif field_type == "word":
            text = fake.word()
            text = remove_accents(text)
            text = trim_text_to_width(text, xmax - xmin, font_size, char_width=7)
            x, y = get_xstart_ystart(field_type, text, xmin, ymin, xmax, ymax, font_size)
            page.insert_text((x, y), text, fontname=font_name, fontsize=font_size, color=(r, g, b))

            gt[widget_name] = {
                "widget_type": "textfield",
                "value": text,
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            }
        
    return page, gt


def add_fake_data(page: fitz.Page) -> tuple[fitz.Page, dict]:
    page, gt_checkboxes = add_random_checkboxes(page, copy_paste=True)
    page, gt_textfield = add_fake_textfield_data(page)
    page, gt_signatures = add_signatures_to_textfields(page, signature_enclosure_dir)
    gt = {**gt_checkboxes, **gt_textfield, **gt_signatures}
    return page, gt


PAGE_WIDTH, PAGE_HEIGHT = 2048, 2650
SAMPLES_PER_PAGE = 2
SUPPORTED_TYPES = ['checkbox', 'name', 'company', 'date', 'license', 'county', 'city', 
                   'initials', 'address', 'sentence', 'number', 'initials', 'country',
                   'word']

template_pdf_dir = Path('TEMPLATE_PDF/annotated_pdfs')
pdf_paths = list(template_pdf_dir.rglob('*.pdf'))

signature_enclosure_dir = Path('TEMPLATE_PDF/signature_enclosures')
out_dir = Path('out')
shutil.rmtree(out_dir, ignore_errors=True)
os.makedirs(out_dir)


for idx, pdf_path in enumerate(pdf_paths):
    pdf_name = pdf_path.name    
    page_nums = len(fitz.open(str(pdf_path)))

    os.makedirs(out_dir/pdf_name/"image", exist_ok=True)
    os.makedirs(out_dir/pdf_name/"json", exist_ok=True)
    os.makedirs(out_dir/pdf_name/"plot", exist_ok=True)

    for page_num in range(page_nums):
        for sample_no in range(SAMPLES_PER_PAGE):
            print(f"{idx+1}/{len(pdf_paths)} {page_num+1}/{page_nums} {sample_no+1}/{SAMPLES_PER_PAGE}  {pdf_path}")
            doc = fitz.open(str(pdf_path))
            page = doc.load_page(page_num)
            
            page, gt = add_fake_data(page)
            gt = scale_coords(gt, page, PAGE_WIDTH, PAGE_HEIGHT)
            img = get_page_raster(page, PAGE_WIDTH, PAGE_HEIGHT)
            doc.close()
           
            json.dump(gt, open(out_dir/pdf_name/"json"/f'{page_num+1}_{sample_no}.json', 'w'), indent=4)
            cv2.imwrite(out_dir/pdf_name/"image"/f'{page_num+1}_{sample_no}.jpg', img)

            # for field_name, entry in gt.items():
            #     bbox = entry['bbox']
            #     xmin, ymin, xmax, ymax = bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']
            #     xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            #     cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # cv2.imwrite(out_dir/pdf_name/"plot"/f'{page_num+1}_{sample_no}_bbox.jpg', img)
   
print('Done...!')