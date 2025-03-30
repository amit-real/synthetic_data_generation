import PyPDF2

def remove_signatures_and_make_editable(in_pdf_path: str, out_pdf_path: str) -> None:
    with open(in_pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            
            if '/Annots' in page:
                annotations = page['/Annots']
                if annotations:
                    new_annotations = []
                    for annot in annotations:
                        if isinstance(annot, PyPDF2.generic.IndirectObject):
                            annot_object = annot.get_object()
                            
                            if '/Subtype' in annot_object and annot_object['/Subtype'] == '/Widget' and \
                               '/FT' in annot_object and annot_object['/FT'] == '/Sig':
                                continue

                        new_annotations.append(annot)
                    
                    if new_annotations:
                        try:
                            page['/Annots'] = new_annotations
                        except Exception as e:
                            pass
                    else:
                        del page['/Annots']
            
            pdf_writer.add_page(page)
        
        if '/AcroForm' in pdf_reader.trailer['/Root']:
            acroform = pdf_reader.trailer['/Root']['/AcroForm'].get_object()
            if '/Fields' in acroform:
                new_fields = []
                for field in acroform['/Fields']:
                    field_obj = field.get_object()
                    if '/FT' in field_obj and field_obj['/FT'] == '/Sig':
                        continue
                    
                    if isinstance(field, PyPDF2.generic.IndirectObject):
                        new_fields.append(field)
                    else:
                        new_fields.append(PyPDF2.generic.IndirectObject(field.idnum, field.generation, field.pdf))
                        
                acroform[PyPDF2.generic.NameObject('/Fields')] = PyPDF2.generic.ArrayObject(new_fields)

        with open(out_pdf_path, 'wb') as output_file:
            pdf_writer.write(output_file)


def is_pdf_signed(pdf_path: str) -> bool:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        if '/AcroForm' in pdf_reader.trailer['/Root']:
            acroform = pdf_reader.trailer['/Root']['/AcroForm'].get_object()
            if '/Fields' in acroform:
                for field in acroform['/Fields']:
                    field_obj = field.get_object()
                    if '/FT' in field_obj and field_obj['/FT'] == '/Sig':
                        if '/V' in field_obj:
                            return True
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            if '/Annots' in page:
                annotations = page['/Annots']
                if annotations:
                    for annot in annotations:
                        if isinstance(annot, PyPDF2.generic.IndirectObject):
                            annot_object = annot.get_object()
                            if '/Subtype' in annot_object and annot_object['/Subtype'] == '/Widget':
                                if '/FT' in annot_object and annot_object['/FT'] == '/Sig':
                                    if '/V' in annot_object:
                                        return True
        
        if '/Root' in pdf_reader.trailer:
            catalog = pdf_reader.trailer['/Root']
            if '/Perms' in catalog:
                perms = catalog['/Perms']
                if '/DocMDP' in perms:
                    return True
        
        return False


if __name__=='__main__':
    pdf_path = "/mnt/c/Users/msoff/OneDrive/Desktop/ABR_Forms_1/prepare_dataset_for_yolov9/synthetic_data_generation/TEMPLATE_PDF/annotated_pdfs/RCSD_Representative_Capacity_Signature.pdf"
    out_path = "editbale.pdf"
    remove_signatures_and_make_editable(pdf_path, out_path)
    is_signed = is_pdf_signed(out_path)
    print(f'pdf is signed: {is_signed}')
