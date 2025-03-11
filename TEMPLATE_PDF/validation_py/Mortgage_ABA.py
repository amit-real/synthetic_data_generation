from pydantic import BaseModel
from inference.leo.document_review_v2.validators.base_validator import BaseDoc, validate_document
import json


class mortgage_ABA_Disclosure_Page1(BaseDoc):
    name_1: str = None
    name_2: str = None
    date_1: str = None

    
class mortgage_ABA_Disclosure_Page2(BaseDoc):
    sign_name_1: bool = False
    date_1: str = None
    sign_name_2: bool = False
    date_2: str = None

class DocumentModel(BaseModel):
    page_1: mortgage_ABA_Disclosure_Page1
    page_2: mortgage_ABA_Disclosure_Page2

PAGE_SCHEMA_MAPPING = { 1: mortgage_ABA_Disclosure_Page1,
                        2: mortgage_ABA_Disclosure_Page2
                        }

## TODO: CHECK FOR TIMEZONE CONVERSIONS AND TIMEZONE DIFFERENCES WHILE DOING DATE_CONSISTENCY_CHECKS
def crosscheck_document_rules(document:DocumentModel)->list:
    document_errors = []
    name_consistency_check_1 = document.page_1.name_1 != document.page_2.sign_name_1
    name_consistency_check_2 = document.page_1.name_1 != document.page_2.sign_name_2
    name_consistency_check_3 = document.page_2.sign_name_1 != document.page_2.sign_name_2
    #date_consistency_check_1 = (document.page_1.date_1 > document.page_2.date_1) or (document.page_1.date_1 > document.page_2.date_2)
    #date_consistency_check_2 = document.page_2.date_1 == document.page_2.date_2
    sign_check_1 = document.page_2.sign_name_1
    sign_check_2 = document.page_2.sign_name_2


    # if name_consistency_check_1:
    #     error = ValueError(f'page_1.name_1: "{document.page_1.name_1}" doesn\'t match page_2.sign_name_1: "{document.page_2.sign_name_1}"')
    #     document_errors.append(error)
    #
    # if name_consistency_check_2:
    #     error = ValueError(f'page_1.name_1: "{document.page_1.name_1}" doesn\'t match page_2.sign_name_2: "{document.page_2.sign_name_2}"')
    #     document_errors.append(error)

    if name_consistency_check_3:
        error = ValueError(f'page_2.sign_name_1: "{document.page_2.sign_name_1}" doesn\'t match page_2.sign_name_2: "{document.page_2.sign_name_2}"')
        document_errors.append(error)

    # if date_consistency_check_1:
    #     if (document.page_1.date_1 > document.page_2.date_1):
    #         error = ValueError(f'page_1.date_1: "{document.page_1.date_1}" is a later date than page_2.date_1: "{document.page_2.date_1}"')
    #
    #     if (document.page_1.date_1 > document.page_2.date_2):
    #         error = ValueError(f'page_1.date_1: "{document.page_1.date_1}" is a later date than page_2.date2: "{document.page_2.date_2}"')
    #     document_errors.append(error)

    if not sign_check_1:
        error = ValueError(f'page_2.sign_name_1: "{document.page_2.sign_name_1}" signature missing!')
        document_errors.append(error)

    if not sign_check_2:
        error = ValueError(f'page_2.sign_name_1: "{document.page_2.sign_name_1}" signature missing!')
        document_errors.append(error)



    # if date_consistency_check_2:
    #     error = ValueError(f'page_2.date_1: "{document.page_2.date_1}" doesn\'t match page_2.date_2: "{document.page_2.date_2}"')
    #     document_errors.append(error)

    return document_errors



if __name__=='__main__':
    import os
    from inference.leo.document_review_v2.utils.misc import import_module_from_file
    osp = os.path.join

    validation_py_path = osp('.', 'validation.py')
    module_name = "validation"
    validation_py = import_module_from_file(module_name, validation_py_path)
    #dets = json.load(open('/mnt/c/Users/msoff/OneDrive/Desktop/ABR_Forms_1/leo_integration/leo/inference/leo/document_review_v2/artifacts/tmp/final_state.json'))
    dets = json.load(open('/Users/shahbazsingh/dev/real_repos/leo/inference/leo/document_review_v2/artifacts/tmp/final_state.json'))
    page_errors, document_errors = validate_document(dets, validation_py)
   
    
    if len(page_errors)==0 and len(document_errors)==0:
        print(f'The document follows all the rules.')
    else:
        print(f'The document doesn\'t follow these rules.')
        for page_num in page_errors:
            # print('Page:', page_num, end=' -> ')
            for error in page_errors[page_num]:
                print(error)
        for error in document_errors:
            print('  -', error)