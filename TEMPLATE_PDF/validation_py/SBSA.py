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
    

class SBSA_Page15(BaseDoc):
    disclosure_1: str = Field(None, description="disclosure_1", error_message="disclosure_1 is missing")
    disclosure_2: str = Field(None, description="disclosure_2", error_message="disclosure_2 is missing",)
    disclosure_3: str = Field(description="disclosure_3", error_message="disclosure_3 is missing")
    disclosure_4: str = Field(None, description="disclosure_4", error_message="disclosure_4 is missing")

    buyer_1_name: str = Field(None, description="buyer_1_name", error_message="buyer_1_name is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing",)
    seller_1_name: str = Field(description="seller_1_name", error_message="seller_1_name is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing",)
    date_2: str = Field(description="date_2", error_message="date_2 is missing")
    date_3: str = Field(None, description="date_3", error_message="date_3 is missing")
    date_4: str = Field(None, description="date_4", error_message="date_4 is missing")
      

class DocumentModel(BaseModel):
    page_15: SBSA_Page15


PAGE_SCHEMA_MAPPING = {15: SBSA_Page15}
