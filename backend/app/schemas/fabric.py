from pydantic import BaseModel, Field

class FabricWidthUpdate(BaseModel):
    fabric_width: float = Field(gt=0)
