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
    

class BuyerAdvisory_Page1(BaseDoc):
    address: str = Field(description="Address", error_message="Address")
    

class BuyerAdvisory_Page2(BaseDoc):
    buyer_1_name: str = Field(
        description="buyer_1_name", error_message="buyer_1_name is missing"
    )
    buyer_2_name: str = Field(
        description="buyer_2_name", error_message="buyer_2_name is missing"
    )
    date_1: str = Field(
        description="date_1", error_message="date_1 is missing"
    )
    date_2: str = Field(
        description="date_2", error_message="date_2 is missing"
    )


class DocumentModel(BaseModel):
    page_1: BuyerAdvisory_Page1
    page_2: BuyerAdvisory_Page2


PAGE_SCHEMA_MAPPING = {1: BuyerAdvisory_Page1, 2: BuyerAdvisory_Page2}
