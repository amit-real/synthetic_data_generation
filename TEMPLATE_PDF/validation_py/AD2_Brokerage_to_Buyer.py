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
    

class AD2BrokerageToBuyer_Page1(BaseDoc):
    name_1: str = Field(description="Buyer 1 Name", error_message="Name_1 is missing")
    name_2: str = Field(None, description="Name_2", error_message="Name_2 is missing")
    agent: str = Field(None, description="Broker's name", error_message="Broker's name is missing")
    name_3: str = Field(
        None,
        description="Broker Associate's name",
        error_message="Broker Associate's name is missing",
    )
    date_1: str = Field(None, description="Date_1", error_message="Date_1 is missing")
    date_2: str = Field(None, description="Date_2", error_message="Date_2 is missing")
    date_3: str = Field(None, description="Date_3", error_message="Date_3 is missing")
    license_1: str = Field(description="DRE License_1", error_message="DRE License_1 is missing")
    license_2: str = Field(
        None, description="Dre License_2", error_message="DRE License_2 is missing"
    )

    cb_1: Literal["checked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_2: Literal["unchecked"] = Field(
        description="checkbox_2", error_message="checkbox_2 should be unchecked"
    )
    cb_3: Literal["checked", "unchecked"] = Field(
        description="checkbox_3", error_message="checkbox_3 should be checked"
    )
    cb_4: Literal["checked", "unchecked"] = Field(
        description="checkbox_4", error_message="checkbox_4 should be checked"
    )
    cb_5: Literal["checked", "unchecked"] = Field(
        description="checkbox_5", error_message="checkbox_5 should be checked"
    )
    cb_6: Literal["checked", "unchecked"] = Field(
        description="checkbox_6", error_message="checkbox_6 should be checked"
    )
    cb_7: Literal["checked", "unchecked"] = Field(
        description="checkbox_7", error_message="checkbox_7 should be checked"
    )
    cb_8: Literal["checked"] = Field(
        description="checkbox_8", error_message="checkbox_8 should be checked"
    )
    cb_9: Literal["checked", "unchecked"] = Field(
        description="checkbox_9", error_message="checkbox_9 should be checked"
    )

    sign_name_1: bool = Field(
        description="Name_1 signature", error_message="Signature in Name_1 is missing"
    )
    sign_name_2: bool = Field(
        description="Name_2 signature", error_message="Signature in Name_2 is missing"
    )
    sign_name_3: bool = Field(
        description="Broker Associate's signature",
        error_message="Broker Associate's signature is missing",
    )
    sign_agent: bool = Field(
        description="Broker's signature", error_message="Broker's signature is missing"
    )


class AD2BrokerageToBuyer_Page2(BaseDoc):
    cb_1: Literal["checked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_2: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_3: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_4: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_5: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_6: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_7: Literal["checked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )
    cb_8: Literal["checked", "unchecked"] = Field(
        description="checkbox for lease", error_message="checkbox_1 should be checked"
    )

    license_1: str = Field(
        description="License of Agent_1", error_message="Agent_1's license is missing"
    )
    license_2: str = Field(
        description="License of Agent_2", error_message="Agent_2's license is missing"
    )
    license_3: str = Field(
        description="License of Agent_3", error_message="Agent_3's license is missing"
    )
    license_4: str = Field(
        description="License of Agent_4", error_message="Agent_4's license is missing"
    )


class DocumentModel(BaseModel):
    page_1: AD2BrokerageToBuyer_Page1
    page_2: AD2BrokerageToBuyer_Page2


PAGE_SCHEMA_MAPPING = {1: AD2BrokerageToBuyer_Page1, 2: AD2BrokerageToBuyer_Page2}
