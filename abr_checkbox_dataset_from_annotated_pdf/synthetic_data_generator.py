import fitz
import os
import json
import random
from tqdm import tqdm
import multiprocessing

def extract_pdf_pages(page, out_path, target_width):
    original_width = page.rect.width
    scale_factor = target_width / original_width
    matrix = fitz.Matrix(scale_factor, scale_factor)
    pix = page.get_pixmap(matrix=matrix)
    pix.save(out_path)

def get_xstart_ystart(text, xmin, ymin, xmax, ymax, font_size):
    if text in ['X', "\u2713", "\u2714", "\u25CF"]:
        return xmin+1, ymax-2

    width, height = abs(xmax-xmin), abs(ymax-ymin)
    align = random.choice(['left', 'center', 'right'])

    if align == 'left':
        x_buffer, y_buffer = random.choice([1,2,3]), random.choice([0,1,2,3,4])
        x_start, y_start = xmin+x_buffer, ymax-y_buffer
    elif align == 'center':
        x_buffer, y_buffer = random.choice([-1,-2,-3,0,1,2,3]), random.choice([0,1,2,3,4])
        x_start = xmin + (width/2) - ((len(text)*font_size)/2)
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer
    else:  # right
        x_buffer, y_buffer = random.choice([-1,-2,-3,0]), random.choice([0,1,2,3,4])
        x_start = xmax - ((len(text)*font_size)) - 4
        y_start = ymax
        x_start, y_start = x_start+x_buffer, y_start-y_buffer

    if x_start < xmin:
        x_start = xmin+4
    return x_start, y_start

def generate_synthetic_data_parallel(task_args):
    # Unpack task_args to get all the parameters needed
    pdf_name, template_pdf_path, page_number_syn, json_entry, idx2, page_width, fonts, out_dir = task_args
    osp = os.path.join

    json_out_path = osp(out_dir, 'json', pdf_name, f'{page_number_syn}_{idx2}.json')
    img_out_path = osp(out_dir, 'imgs', pdf_name, f'{page_number_syn}_{idx2}.jpg')

    # Create parent directories
    os.makedirs(os.path.dirname(json_out_path), exist_ok=True)
    os.makedirs(os.path.dirname(img_out_path), exist_ok=True)

    # Skip if already processed
    if os.path.exists(json_out_path) and os.path.exists(img_out_path):
        return

    doc = fitz.open(template_pdf_path)
    page = doc[page_number_syn-1]
    original_width = page.rect.width
    scale_factor = page_width / original_width
    page.insert_font(fontfile='DejaVuSans.ttf', fontname="DVS")
    tmp_dict = {}

    for widget in page.widgets():
        field_name = widget.field_name
        if 'ENVELOPEID' in field_name:
            if field_name in tmp_dict:
                del tmp_dict[field_name]
            continue

        xmin, ymin, xmax, ymax = widget.rect
        page.delete_widget(widget)

        xmin_scaled, ymin_scaled, xmax_scaled, ymax_scaled = [int(val * scale_factor) for val in [xmin, ymin, xmax, ymax]]

        if not json_entry:
            req_text = {'data': '', 'xmin': xmin_scaled, 'ymin': ymin_scaled, 'xmax': xmax_scaled, 'ymax': ymax_scaled}
        else:
            req_text = str(json_entry[field_name])
            tmp_dict[field_name] = {'data': req_text, 'xmin': xmin_scaled, 'ymin': ymin_scaled, 'xmax': xmax_scaled, 'ymax': ymax_scaled}

        # Skip 20% of elements randomly
        if random.random() > 0.8 and '<cb_' not in field_name:
            if field_name in tmp_dict:
                del tmp_dict[field_name]
            continue

        if req_text.lower() == 'unchecked':
            tmp_dict[field_name] = {'data': 'unchecked', 'xmin': xmin_scaled, 'ymin': ymin_scaled, 'xmax': xmax_scaled, 'ymax': ymax_scaled}
            continue
        elif req_text.lower() == 'checked':
            tmp_dict[field_name] = {'data': 'checked', 'xmin': xmin_scaled, 'ymin': ymin_scaled, 'xmax': xmax_scaled, 'ymax': ymax_scaled}
            req_text = random.choice(["X", "\u2713", "\u2714", "\u25CF"])

        font_size = 10
        x_start, y_start = get_xstart_ystart(req_text, xmin, ymin, xmax, ymax, font_size)

        r, g, b = 0, 0, 0
        if random.random() > 0.7:
            r, g, b = random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)
        r, g, b = r/256, g/256, b/256

        if r == 1 and g == 1 and b == 1:  # If white, not visible
            if field_name in tmp_dict:
                del tmp_dict[field_name]
            continue

        font = random.choice(fonts)
        if '<cb' in field_name:
            font = 'DVS'  # DejaVuSans font for checkboxes

        font_size = random.choice([8, 9, 10, 11])
        if 'init>' in field_name.lower():
            font_size = 7

        page.insert_text((x_start, y_start), req_text, fontname=font, fontsize=font_size, rotate=0, color=(r, g, b))

    # Save outputs
    with open(json_out_path, 'w') as f:
        json.dump(tmp_dict, f, indent=4)
    extract_pdf_pages(page, img_out_path, target_width=page_width)
    doc.close()

def process_all_pdfs(syn_data_dir, template_pdf_dir, out_dir, page_width, fonts, num_cores=10):
    osp = os.path.join
    syn_pdfs = [i for i in os.listdir(syn_data_dir) if i.endswith('.pdf')]
    tasks = []

    # First, collect all tasks
    for pdf_name in syn_pdfs:
        if pdf_name == 'FHDA.pdf':
            continue

        os.makedirs(osp(out_dir, 'imgs', pdf_name), exist_ok=True)
        os.makedirs(osp(out_dir, 'json', pdf_name), exist_ok=True)

        # Process pages with entries
        syn_json_path = osp(syn_data_dir, pdf_name)
        syn_json_names = [i for i in os.listdir(syn_json_path) if i.endswith('.json')]

        for syn_json_name in syn_json_names:
            page_number_syn = int(syn_json_name.replace('.json', ''))

            # Load JSON data outside the task to avoid pickling issues
            with open(osp(syn_json_path, syn_json_name), 'r') as f:
                syn_json = json.load(f)

            for idx2, json_entry in enumerate(syn_json):
                if idx2 > 10:
                    break

                json_out_path = osp(out_dir, 'json', pdf_name, f'{page_number_syn}_{idx2}.json')
                img_out_path = osp(out_dir, 'imgs', pdf_name, f'{page_number_syn}_{idx2}.jpg')

                if os.path.exists(json_out_path) and os.path.exists(img_out_path):
                    continue

                template_pdf_path = osp(template_pdf_dir, pdf_name)
                # Package all the arguments needed (pickleable types only)
                tasks.append([pdf_name, template_pdf_path, page_number_syn, json_entry, idx2, page_width, fonts, out_dir])

        # Process pages without entries (negative samples)
        orig_pdf_path = osp(template_pdf_dir, pdf_name)
        doc = fitz.open(orig_pdf_path)
        total_pages = doc.page_count
        doc.close()

        for page_num in range(1, total_pages+1):
            json_path = osp(syn_data_dir, pdf_name, f'{page_num}.json')
            if os.path.exists(json_path):
                continue

            # Only 50 negative samples per empty page
            for idx2 in range(50):
                template_pdf_path = osp(template_pdf_dir, pdf_name)
                tasks.append([pdf_name, template_pdf_path, page_num, {}, idx2, page_width, fonts, out_dir])

    # Use multiprocessing pool to process tasks in parallel
    with multiprocessing.Pool(processes=num_cores) as pool:
        list(tqdm(pool.imap(generate_synthetic_data_parallel, tasks), total=len(tasks), desc="Generating synthetic data"))

if __name__ == "__main__":
    # Example usage
    syn_data_dir = "path/to/syn_data"
    template_pdf_dir = "path/to/templates"
    out_dir = "path/to/output"
    page_width = 1000  # Example value
    fonts = ["Helvetica", "Times-Roman"]  # Example fonts

    # Process with 10 cores in parallel
    process_all_pdfs(syn_data_dir, template_pdf_dir, out_dir, page_width, fonts, num_cores=10)