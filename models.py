from typing import Optional
from datetime import datetime,timezone
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rollno: str = Field(index=True)  # Add index for faster lookups  

    cheese_roll: int = 0
    paneer_tikka: int = 0
    schezwan_paneer: int = 0
    extra_cheese: int = 0
    normal_brownie: int = 0
    brownie_with_icecream: int = 0
    lime_juice: int = 0
    lemon_soda: int = 0
    margherita: int = 0
    peppy_paneer: int = 0
    farmhouse: int = 0
    choco_lava_cake: int = 0
    french_fries: int = 0
    cheese_nuggets: int = 0
    corn: int = 0
    spiral_potato: int = 0
    rabadi_kulfi: int = 0
    shahi_gulab: int = 0
    strawberry: int = 0
    choclate: int = 0
    pista_badam: int = 0
    malai_kulfi: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))