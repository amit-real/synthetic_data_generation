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
    

class BHIA_HOME_Insurance_Advisory_Page1(BaseDoc):
    buyer_1_name: str = Field(description="Buyer 1 Name", error_message="Name_1 is missing")
    buyer_2_name: str = Field(None, description="Buyer 2 Name", error_message="Name_2 is missing")
    date_1: str = Field(None, description="Date_1", error_message="Date_1 is missing")
    date_2: str = Field(None, description="Date_2", error_message="Date_2 is missing")
    

class DocumentModel(BaseModel):
    page_1: BHIA_HOME_Insurance_Advisory_Page1


PAGE_SCHEMA_MAPPING = {1: BHIA_HOME_Insurance_Advisory_Page1}
