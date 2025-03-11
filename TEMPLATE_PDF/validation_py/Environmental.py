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
    

class Environmental_Page1(BaseDoc):
    address_1: str = Field(description="address_1", error_message="address_1 is missing")
    seller_1_name: str = Field(None, description="seller_1_name", error_message="seller_1_name is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing")
    seller_2_name: str = Field(None, description="seller_2_name", error_message="seller_2_name is missing")
    date_2: str = Field(None, description="date_2", error_message="date_2 is missing")
    seller_agent: str = Field(None, description="seller_agent", error_message="seller_agent is missing")
    date_3: str = Field(description="date_3", error_message="date_3 is missing")
    buyer_1_name: str = Field(None, description="buyer_1_name", error_message="buyer_1_name is missing")

    date_4: bool = Field(description="date_4", error_message="date_4 is missing")
    buyer_2_name: bool = Field(description="buyer_2_name", error_message="buyer_2_name is missing")
    date_5: bool = Field(description="date_5", error_message="date_5")
    buyer_agent: bool = Field(description="buyer_agent", error_message="buyer_agent")
    date_6: bool = Field(description="date_6", error_message="date_6 is missing")


class Environmental_Page2(BaseDoc):
    address_1: str = Field(description="address_1", error_message="address_1 is missing")
    address_2: str = Field(None, description="address_2", error_message="address_2 is missing")
    buyer_1_sign: str = Field(None, description="buyer_1_sign", error_message="buyer_1_sign is missing")
    buyer_2_sign: str = Field(None, description="buyer_2_sign", error_message="buyer_2_sign is missing")
    buyer_agent_sign: str = Field(None, description="buyer_agent_sign", error_message="buyer_agent_sign is missing")
    buyer_1_name: str = Field(None, description="buyer_1_name", error_message="buyer_1_name is missing")
    date_1: str = Field(description="date_1", error_message="date_1 is missing")
    buyer_2_name: str = Field(None, description="buyer_2_name", error_message="buyer_2_name is missing")
    date_2: bool = Field(description="date_2", error_message="date_2 is missing")
    buyer_agent_name: bool = Field(description="buyer_agent_name", error_message="buyer_agent_name is missing")
    date_3: bool = Field(description="date_3", error_message="date_3 is missing")
    broker_1_name: bool = Field(description="broker_1_name", error_message="broker_1_name is missing")
    sign_seller_1: bool = Field(description="sign_seller_1", error_message="sign_seller_1 is missing")
    seller_1_name: bool = Field(description="seller_1_name", error_message="seller_1_name is missing")
    date_4: bool = Field(description="date_4", error_message="date_4 is missing")
    sign_seller_2: bool = Field(description="sign_seller_2", error_message="sign_seller_2 is missing")
    seller_2_name: bool = Field(description="seller_2_name", error_message="seller_2_name is missing")
    date_5: bool = Field(description="date_5", error_message="date_5 is missing")
    date_6: bool = Field(description="date_6", error_message="date_6 is missing")
    sign_seller_agent: bool = Field(description="sign_seller_agent", error_message="sign_seller_agent is missing")
    seller_agent_name: bool = Field(description="seller_agent_name", error_message="seller_agent_name is missing")
    broker_2_name: bool = Field(description="broker_2_name", error_message="broker_2_name is missing")

class DocumentModel(BaseModel):
    page_1: Environmental_Page1
    page_2: Environmental_Page2


PAGE_SCHEMA_MAPPING = {1: Environmental_Page1, 2: Environmental_Page2}
