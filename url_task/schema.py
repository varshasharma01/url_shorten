from pydantic import BaseModel, HttpUrl, field_validator
from typing import Any, Optional
from datetime import datetime
import validators

class ResponseMeta(BaseModel):
    
    status_code : int
    success : bool
    message : str
    
class StandardResponse(BaseModel):
    meta : ResponseMeta
    data : Optional[Any] = None
    
    
# class for input validation schema
class ShortenRequest(BaseModel):
    original_url : str
    expires_in_days: Optional[int] = None
    
    @field_validator("original_url")
    @classmethod
    
    # method for url validation
    # it will take string as a parameter
    def validate_url(cls, v:str)->str:
        
        if not validators.url(v):
            
            raise ValueError("Invalid URL format")
        return v
    

class URLResponseData(BaseModel):
    short_code : str
    original_url : str
    expires_at : Optional[datetime] = None
    
    