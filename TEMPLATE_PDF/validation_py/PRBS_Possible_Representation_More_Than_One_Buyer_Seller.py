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
                        name.replace("<", "").replace(">", "").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = json_data["text_fields"][name]
            elif key == "checkboxes":
                for name in json_data["checkboxes"]:
                    normalized_key = (
                        name.replace("<", "").replace(">", "").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = json_data["checkboxes"][name]["state"]
            elif key == "signatures":
                for name in json_data["signatures"]:
                    normalized_key = (
                        "sign_" + name.replace("<", "").replace(">", "").replace("-", "_").lower()
                    )
                    new_dict[normalized_key] = True
            else:
                normalized_key = key.replace("<", "").replace(">", "").replace("-", "_").lower()
                new_dict[normalized_key] = value
        return new_dict
    

class PRBS_Possible_Representation_More_Than_One_Buyer_Seller_Page1(BaseDoc):
    seller_1_name: str = Field(None, description="seller_1_name", error_message="seller_1_name is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing",)
    buyer_1_name: str = Field(description="buyer_1_name", error_message="buyer_1_name is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing")

    buyer_brokerage: str = Field(None, description="buyer_brokerage", error_message="buyer_brokerage is missing")
    name_1: str = Field(None, description="name_1", error_message="name_1 is missing",)
    seller_brokerage: str = Field(description="seller_brokerage", error_message="seller_brokerage is missing")
    name_2: str = Field(None, description="name_2", error_message="name_2 is missing")
    license_1: str = Field(None, description="license_1", error_message="license_1 is missing",)
    license_2: str = Field(description="license_2", error_message="license_2 is missing")
    license_3: str = Field(None, description="license_3", error_message="license_3 is missing")
    license_4: str = Field(None, description="license_4", error_message="license_4 is missing")
    
    date_1: str = Field(None, description="Date_1", error_message="Date_1 is missing")
    date_2: str = Field(None, description="Date_2", error_message="Date_2 is missing")
    date_3: str = Field(None, description="Date_3", error_message="Date_3 is missing")
    date_4: str = Field(description="date_4", error_message="date_4 is missing")
    date_5: str = Field(None, description="date_5", error_message="date_5 is missing")
    date_6: str = Field(description="date_6", error_message="date_6 is missing")
      

class DocumentModel(BaseModel):
    page_1: PRBS_Possible_Representation_More_Than_One_Buyer_Seller_Page1


PAGE_SCHEMA_MAPPING = {1: PRBS_Possible_Representation_More_Than_One_Buyer_Seller_Page1}
