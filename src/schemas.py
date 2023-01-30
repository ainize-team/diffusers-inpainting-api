import json
from typing import Dict, Union

from pydantic import BaseModel, Field, HttpUrl

from enums import ResponseStatusEnum


class FormDataBaseModel(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value: any):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class AsyncTaskResponse(BaseModel):
    task_id: str
    updated_at: int


class Error(BaseModel):
    status_code: int
    error_message: str


class InpaintRequestParams(FormDataBaseModel):
    prompt: str = Field(
        ...,
        description="Your prompt (what you want to add in place of what you are removing)",
    )
    seed: int = Field(default=42, ge=0, le=4294967295)
    num_images_per_prompt: int = Field(2, ge=1, le=4, description="How many images you wish to generate")
    guidance_scale: float = Field(7.5, ge=0, le=50, description="how much the prompt will influence the results")


class InpaintingResponse(BaseModel):
    status: ResponseStatusEnum = ResponseStatusEnum.PENDING
    updated_at: int = 0
    result: Union[Dict[str, HttpUrl], None, str] = None
