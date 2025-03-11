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
    

class AVID_Buyer_Side_Page1(BaseDoc):
    city: str = Field(description="City name", error_message="City name is missing")
    county: str = Field(None, description="County name", error_message="County name is missing")
    add_1: str = Field(None, description="Address 1", error_message="Address 1 is missing")
    add_2: str = Field(None,description="Address 2", error_message="Address 2 is missing",)
    units: str = Field(None, description="Units", error_message="Units value is missing")
    broker_firm: str = Field(None, description="Broker's Firm", error_message="Broker's Firm is missing")
    b_1_init: str = Field(None, description="Buyer_1 initials", error_message="Buyer_1 initials is missing")
    b_2_init: str = Field(description="Buyer_2 ", error_message="Buyer_2 is missing")
    
    cb_1: Literal["checked"] = Field(description="checkbox_1", error_message="checkbox_1 should be checked")
    cb_2: Literal["unchecked"] = Field(description="checkbox_2", error_message="checkbox_2 should be unchecked")
    

class AVID_Buyer_Side_Page2(BaseDoc):
    unit: str = Field(description="Unit", error_message="Unit is missing")
    entry_1: str = Field(None, description="entry_1", error_message="entry_1 is missing")
    entry_2: str = Field(None, description="entry_2", error_message="entry_2 is missing")
    entry_3: str = Field(None,description="entry_3", error_message="entry_3 is missing",)
    
    living_room_1: str = Field(None, description="living_room_1", error_message="living_room_1 is missing")
    living_room_2: str = Field(None, description="living_room_2", error_message="living_room_2 is missing")
    living_room_3: str = Field(None, description="living_room_3", error_message="living_room_3 is missing")
    
    dining_room_1: str = Field(description="dining_room_1", error_message="dining_room_1 is missing")
    dining_room_2: str = Field(description="dining_room_2", error_message="dining_room_2 is missing")
    dining_room_3: str = Field(description="dining_room_3", error_message="dining_room_3 is missing")
    
    kitchen_1: str = Field(description="kitchen_1", error_message="kitchen_1 is missing")
    kitchen_2: str = Field(description="kitchen_2", error_message="kitchen_2 is missing")
    kitchen_3: str = Field(description="kitchen_3", error_message="kitchen_3 is missing")

    other_1: str = Field(description="other_1", error_message="other_1 is missing")
    other_2: str = Field(description="other_2", error_message="other_2 is missing")
    other_3: str = Field(description="other_3", error_message="other_3 is missing")

    hall_1: str = Field(description="hall_1", error_message="hall_1 is missing")
    hall_2: str = Field(description="hall_2", error_message="hall_2 is missing")
    hall_3: str = Field(description="hall_3", error_message="hall_3 is missing")
    
    n1: str = Field(description="n1", error_message="n1 is missing")
    bedroom_1a: str = Field(description="bedroom_1a", error_message="bedroom_1a is missing")
    bedroom_1b: str = Field(description="bedroom_1b", error_message="bedroom_1b is missing")
    bedroom_1c: str = Field(description="bedroom_1c", error_message="bedroom_1c is missing")

    n2: str = Field(description="n2", error_message="n2 is missing")
    bedroom_2a: str = Field(description="bedroom_2a", error_message="bedroom_2a is missing")
    bedroom_2b: str = Field(description="bedroom_2b", error_message="bedroom_2b is missing")
    bedroom_2c: str = Field(description="bedroom_2c", error_message="bedroom_2c is missing")

    n3: str = Field(description="n3", error_message="n3 is missing")
    bedroom_3a: str = Field(description="bedroom_3a", error_message="bedroom_3a is missing")
    bedroom_3b: str = Field(description="bedroom_3b", error_message="bedroom_3b is missing")
    bedroom_3c: str = Field(description="bedroom_3c", error_message="bedroom_3c is missing")

    n4: str = Field(description="n4", error_message="n4 is missing")
    bedroom_4a: str = Field(description="bedroom_4a", error_message="bedroom_4a is missing")
    bedroom_4b: str = Field(description="bedroom_4b", error_message="bedroom_4b is missing")
    bedroom_4c: str = Field(description="bedroom_4c", error_message="bedroom_4c is missing")

    n5: str = Field(description="n5", error_message="n5")
    bath_1a: str = Field(description="bath_1a", error_message="bath_1a is missing")
    bath_1b: str = Field(description="bath_1b", error_message="bath_1b is missing")
    bath_1c: str = Field(description="bath_1c", error_message="bath_1c is missing")

    n6: str = Field(description="n6", error_message="n6 is missing")
    bath_2a: str = Field(description="bath_2a", error_message="bath_2a is missing")
    bath_2b: str = Field(description="bath_2b", error_message="bath_2b is missing")
    bath_2c: str = Field(description="bath_2c", error_message="bath_2c is missing")

    n7: str = Field(description="n7", error_message="n7 is missing")
    bath_3a: str = Field(description="bath_3a", error_message="bath_3a is missing")
    bath_3b: str = Field(description="bath_3b", error_message="bath_3b is missing")
    bath_3c: str = Field(description="bath_3c", error_message="bath_3c is missing")

    n8: str = Field(description="n8", error_message="n8 is missing")
    bath_4a: str = Field(description="bath_4a", error_message="bath_4a is missing")
    bath_4b: str = Field(description="bath_4b", error_message="bath_4b is missing")
    bath_4c: str = Field(description="bath_4c", error_message="bath_4c is missing")

    b_1_init: str = Field(description="Buyer_1 initials", error_message="Buyer_1 initials is missing")
    b_2_init: str = Field(description="Buyer_2 ", error_message="Buyer_2 is missing")
    

class AVID_Buyer_Side_Page3(BaseDoc):
    unit: str = Field(description="unit", error_message="unit")
    
    other_1a: str = Field(description="other_1a", error_message="other_1a is missing")
    other_1b: str = Field(description="other_1b", error_message="other_1b is missing")
    other_1c: str = Field(description="other_1c", error_message="other_1c is missing")

    other_2a: str = Field(description="other_2a", error_message="other_2a is missing")
    other_2b: str = Field(description="other_2b", error_message="other_2b is missing")
    other_2c: str = Field(description="other_2c", error_message="other_2c is missing")

    other_3a: str = Field(description="other_3a", error_message="other_3a is missing")
    other_3b: str = Field(description="other_3b", error_message="other_3b is missing")
    other_3c: str = Field(description="other_3c", error_message="other_3c is missing")

    cb_1: Literal["checked"] = Field(description="checkbox_1", error_message="checkbox_1 should be checked")

    structures_1a: str = Field(description="structures_1a", error_message="structures_1a is missing")
    structures_1b: str = Field(description="structures_1b", error_message="structures_1b is missing")
    
    garage_1a: str = Field(description="garage_1a", error_message="garage_1a is missing")
    garage_1b: str = Field(description="garage_1b", error_message="garage_1b is missing")
    garage_1c: str = Field(description="garage_1c", error_message="garage_1c is missing")
    garage_1d: str = Field(description="garage_1d", error_message="garage_1d is missing")

    exterior_1a: str = Field(description="exterior_1a", error_message="exterior_1a is missing")
    exterior_1b: str = Field(description="exterior_1b", error_message="exterior_1b is missing")
    exterior_1c: str = Field(description="exterior_1c", error_message="exterior_1c is missing")

    observed_1a: str = Field(description="observed_1a", error_message="observed_1a is missing")
    observed_1b: str = Field(description="observed_1b", error_message="observed_1b is missing")
    observed_1c: str = Field(description="observed_1c", error_message="observed_1c is missing")

    inspection_firm: str = Field(description="inspection_firm", error_message="inspection_firm is missing")
    inspection_agent: str = Field(description="inspection_agent", error_message="inspection_agent is missing")
    date_time: str = Field(description="date_time", error_message="date_time is missing")
    weather: str = Field(description="weather", error_message="weather is missing")
    other_person: str = Field(description="other_person ", error_message="other_person  is missing")
    name_1: str = Field(description="name_1", error_message="name_1 is missing")
    date_1: str = Field(description="date_1", error_message="date_1 is missing")

    buyer_1_name: str = Field(description="buyer_1_name", error_message="buyer_1_name is missing")
    date_2: str = Field(description="date_2", error_message="date_2 is missing")
    buyer_2_name: str = Field(description="buyer_2_name", error_message="buyer_2_name is missing")
    date_3: str = Field(description="date_3", error_message="date_3 is missing")
    s_1_init: str = Field(description="s_1_init", error_message="s_1_init is missing")
    s_2_init: str = Field(description="s_2_init", error_message="s_2_init is missing")
    broker_1: str = Field(description="broker_1", error_message="broker_1 is missing")
    name_2: str = Field(description="name_2", error_message="name_2 is missing")
    date_4: str = Field(description="date_4", error_message="date_4 is missing")
    

class AVID_Buyer_Side_Page4(BaseDoc):
    addendum: str = Field(description="addendum", error_message="addendum is missing")
    add_1: str = Field(None, description="Address 1", error_message="Address 1 is missing")
    add_2: str = Field(None, description="Address 2", error_message="Address 2 is missing")
    buyer: str = Field(None,description="buyer", error_message="buyer is missing",)
    seller: str = Field(None, description="seller", error_message="seller is missing")
    buyer_1_name: str = Field(None, description="buyer_1_name", error_message="buyer_1_name is missing")
    date_1: str = Field(None, description="date_1", error_message="date_1 is missing")
    buyer_2_name: str = Field(description="buyer_2_name ", error_message="buyer_2_name is missing")
    date_2: str = Field(None, description="date_2", error_message="date_2 is missing")

    seller_1_name: str = Field(None, description="seller_1_name", error_message="seller_1_name is missing")
    date_3: str = Field(None, description="date_3", error_message="date_3 is missing")
    seller_2_name: str = Field(description="seller_2_name ", error_message="seller_2_name is missing")
    date_4: str = Field(None, description="date_4", error_message="date_4 is missing")
    


class DocumentModel(BaseModel):
    page_1: AVID_Buyer_Side_Page1
    page_2: AVID_Buyer_Side_Page2
    page_3: AVID_Buyer_Side_Page3
    page_4: AVID_Buyer_Side_Page4


PAGE_SCHEMA_MAPPING = {1: AVID_Buyer_Side_Page1, 
                       2: AVID_Buyer_Side_Page2,
                       3: AVID_Buyer_Side_Page3,
                       4: AVID_Buyer_Side_Page4
                       }
