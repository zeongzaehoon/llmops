from pydantic import BaseModel, Field
from typing import Optional



class CreateStorePayload(BaseModel):
    # Required
    service: str = Field(...)

    # Not Required
    display_name: Optional[str] = Field(None, alias="displayName")


class GetStoresPayload(BaseModel):
    # Required
    service: str = Field(...)


class ImportFilePayload(BaseModel):
    # Required
    service: str = Field(...)
    store_name: str = Field(..., alias="storeName")
    buckets: list[str] = Field(...)
    keys: list[str] = Field(...)

    # Not Required
    title: Optional[str] = Field(
        None,
        description="Title is also retrieved. So, user should consider write title well"
    )

    # For Domain
    file_path: Optional[list[str]] = Field([], description="Please don't input any data")


class GetFilesPayload(BaseModel):
    # Required
    service: str = Field(...)
    store_name: str = Field(..., alias="storeName")


class DeleteStorePayload(BaseModel):
    # Required
    service: str = Field(...)
    store_name: str = Field(..., alias="storeName")


class DeleteDocumentPayload(BaseModel):
    # Required
    service: str = Field(...)
    document_name: tuple[str] | list[str] | str = Field(
        ...,
        alias="documentName",
        description="1: str, 2 or more: tuple or list"
    )
