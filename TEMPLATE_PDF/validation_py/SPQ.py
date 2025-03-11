import types
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import BaseModel, ValidationError, model_validator


class BaseDoc(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def update_keys(self, json_data: dict) -> dict:
        new_dict = {}
        for key, value in json_data.items():
            if key == "text_fields":
                for name in json_data["text_fields"]:
                    if (
                        len(json_data["text_fields"][name]) == 0
                        or json_data["text_fields"][name] is None
                    ):  # removing empty strings
                        continue
                    normalized_key = (
                        name.replace("<", "AAAAAA").replace(">", "AAAAAA").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = json_data["text_fields"][name]
            elif key == "checkboxes":
                for name in json_data["checkboxes"]:
                    normalized_key = (
                        name.replace("<", "AAAAAA").replace(">", "AAAAAA").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = json_data["checkboxes"][name]["state"]
            elif key == "signatures":
                for name in json_data["signatures"]:
                    normalized_key = (
                        "sign_" + name.replace("<", "AAAAAA").replace(">", "AAAAAA").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = True
            else:
                normalized_key = key.replace("<", "AAAAAA").replace(">", "AAAAAA").replace("-", "_").lower()
                new_dict[normalized_key] = value
        return new_dict
    

class SPQ_Page1(BaseDoc):
    parcel_num: str = Field(None, description="parcel_num", error_message="parcel_num is missing")
    locality: str = Field(None, description="locality", error_message="locality is missing",)
    county: str = Field(description="county", error_message="county is missing")
    units: str = Field(None, description="units", error_message="units is missing")
    address_1: str = Field(None, description="address_1", error_message="address_1 is missing")
    explanation_1: str = Field(None, description="explanation_1", error_message="explanation_1 is missing",)
    b_1_init: str = Field(description="b_1_init", error_message="b_1_init is missing")
    b_2_init: str = Field(None, description="b_2_init", error_message="b_2_init is missing")
    s_1_init: str = Field(None, description="s_1_init", error_message="s_1_init is missing",)
    s_2_init: str = Field(description="s_2_init", error_message="s_2_init is missing")
    address_2: str = Field(None, description="address_2", error_message="address_2 is missing")
    

class SPQ_Page2(BaseDoc):
    address_1: str = Field(None, description="address_1", error_message="address_1 is missing")
    attached_1: str = Field(None, description="attached_1", error_message="attached_1 is missing",)
    attached_2: str = Field(description="attached_2", error_message="attached_2 is missing")
    explanation_1: str = Field(None, description="explanation_1", error_message="explanation_1 is missing")
    b_1_init: str = Field(None, description="b_1_init", error_message="b_1_init is missing")
    b_2_init: str = Field(None, description="b_2_init", error_message="b_2_init is missing",)
    s_1_init: str = Field(description="s_1_init", error_message="s_1_init is missing")
    s_2_init: str = Field(None, description="s_2_init", error_message="s_2_init is missing")
    explanation_2: str = Field(None, description="explanation_2", error_message="explanation_2 is missing",)
    explanation_3: str = Field(description="explanation_3", error_message="explanation_3 is missing")
    

class SPQ_Page3(BaseDoc):
    address_1: str = Field(None, description="address_1", error_message="address_1 is missing")
    explanation_1: str = Field(None, description="explanation_1", error_message="explanation_1 is missing",)
    explanation_2: str = Field(description="explanation_2", error_message="explanation_2 is missing")
    explanation_3: str = Field(None, description="explanation_3", error_message="explanation_3 is missing")
    explanation_4: str = Field(None, description="explanation_4", error_message="explanation_4 is missing")
    explanation_5: str = Field(None, description="explanation_5", error_message="explanation_5 is missing",)
    b_1_init: str = Field(description="b_1_init", error_message="b_1_init is missing")
    b_2_init: str = Field(None, description="b_2_init", error_message="b_2_init is missing")
    s_1_init: str = Field(None, description="s_1_init", error_message="s_1_init is missing",)
    s_2_init: str = Field(description="s_2_init", error_message="s_2_init is missing")
    

class SPQ_Page4(BaseDoc):
    address_1: str = Field(None, description="address_1", error_message="address_1 is missing")
    explanation_1: str = Field(None, description="explanation_1", error_message="explanation_1 is missing",)
    explanation_2: str = Field(description="explanation_2", error_message="explanation_2 is missing")
    explanation_3: str = Field(None, description="explanation_3", error_message="explanation_3 is missing")
    explanation_4: str = Field(None, description="explanation_4", error_message="explanation_4 is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing",)
    buyer_1_name: str = Field(description="buyer_1_name", error_message="buyer_1_name is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing")
    date_2: str = Field(None, description="date_2", error_message="date_2 is missing",)
    seller_1_name: str = Field(description="seller_1_name", error_message="seller_1_name is missing")
    date_3: str = Field(None, description="date_3", error_message="date_3 is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing")
    date_4: str = Field(description="date_4", error_message="date_4 is missing")
    

class SPQ_Page5(BaseDoc):
    addendum: str = Field(None, description="addendum", error_message="addendum is missing")
    address_1: str = Field(None, description="address_1", error_message="address_1 is missing",)
    address_2: str = Field(description="address_2", error_message="address_2 is missing")
    buyer_name: str = Field(None, description="buyer_name", error_message="buyer_name is missing")
    seller_name: str = Field(None, description="seller_name", error_message="seller_name is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing",)
    buyer_1_name: str = Field(description="buyer_1_name", error_message="buyer_1_name is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing")
    date_2: str = Field(None, description="date_2", error_message="date_2 is missing",)
    seller_1_name: str = Field(description="seller_1_name", error_message="seller_1_name is missing")
    date_3: str = Field(None, description="date_3", error_message="date_3 is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing")
    date_4: str = Field(description="date_4", error_message="date_4 is missing")
    

class DocumentModel(BaseModel):
    page_1: SPQ_Page1
    page_2: SPQ_Page2
    page_3: SPQ_Page3
    page_4: SPQ_Page4
    page_5: SPQ_Page5


PAGE_SCHEMA_MAPPING = {1: SPQ_Page1,
                       2: SPQ_Page2,
                       3: SPQ_Page3,
                       4: SPQ_Page4,
                       5: SPQ_Page5,
                    }
