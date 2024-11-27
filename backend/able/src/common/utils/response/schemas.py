from datetime import datetime
from uuid import uuid4, UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, conint, ConfigDict
from typing import Generic, TypeVar

T = TypeVar("T")

class ImmutableBaseModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        json_encoders= {UUID:str}
    )

class ResponseModel(BaseModel, Generic[T]):
    status_code: conint(gt=99, lt=600)
    time_stamp: datetime  = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    tracking_id: UUID  = Field(default_factory=uuid4)
    data: T = None