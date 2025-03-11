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
    

class SPBB_Page1(BaseDoc):
    field: str = Field(None, description="field", error_message="field is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing",)
    property_1: str = Field(description="property_1", error_message="property_1 is missing")
    buyer_0_name: str = Field(None, description="buyer_0_name", error_message="buyer_0_name is missing")
    seller_0_name: str = Field(None, description="seller_0_name", error_message="seller_0_name is missing")
    buyer_broker: str = Field(None, description="buyer_broker", error_message="buyer_broker is missing",)
    seller_broker: str = Field(description="seller_broker", error_message="seller_broker is missing")
    any: str = Field(None, description="any", error_message="any is missing")
    price: str = Field(None, description="price", error_message="price is missing",)
    date_2: str = Field(description="date_2", error_message="date_2 is missing")
    seller_1_name: str = Field(None, description="seller_1_name", error_message="seller_1_name is missing")
    date_3: str = Field(None, description="date_3", error_message="date_3 is missing")
    date_4: str = Field(description="date_4", error_message="date_4 is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing")
    date_5: str = Field(None, description="date_5", error_message="date_5 is missing",)
    prcnt: str = Field(description="prcnt", error_message="prcnt is missing")
    buyer_1_name: str = Field(None, description="buyer_1_name", error_message="buyer_1_name is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing")
     

class DocumentModel(BaseModel):
    page_1: SPBB_Page1


PAGE_SCHEMA_MAPPING = {1: SPBB_Page1}
