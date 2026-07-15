from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, status, HTTPException
import crud
from config import init_db
from schema import StandardResponse, ResponseMeta, ShortenRequest

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
    
# task1 : shorten the url endpoint

@app.post("/shorten", response_model = StandardResponse, status_code = status.HTTP_201_CREATED)
def shorten_url(payload: ShortenRequest):
    existing_record = crud.get_active_url(payload.original_url)
    
    if existing_record : 
        return StandardResponse(
            meta = ResponseMeta(success= True, status_code = 200, message="Existing Short Code !"),
            data = {
                "short_code": existing_record["short_code"],
                "original_url" : existing_record["original_url"],
                "expires_at" : existing_record["expires_at"]
            }

        )
        
    new_record = crud.create_short_url(payload)
    
    return StandardResponse(
        
        meta = ResponseMeta(success = True,status_code = 200, message="New Short code created!"),
        
        data = new_record
        
    )
    
    
# task 2

@app.get("/url/{short_code}", response_model = StandardResponse)
def get_original_url(short_code:str):
    record = crud.get_url_record(short_code)
    
    if not record:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail= {"meta": {"success": False, "status_code": 404, "message": "Short code not found", "data": None}}
            
        )
    if record["expires_at"]:
        expiry = datetime.fromisoformat(record["expires_at"])
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code= status.HTTP_410_GONE,
                detail = {'meta': {"success": False, "status_code": 410, "message": "URL expired", "data": None}}
                
            )
            
    crud.update_clicks(short_code)
    
    # return StandardResponse
    # (
    # meta = ResponseMeta(success= True, status_code= 200, message= "URL retrieval successful"),
    # 
    
    # )
    
    return StandardResponse(
        
        meta = ResponseMeta(success= True, status_code= 200, message= "URL retrieval successful"),
        
        data = {"original_url": record["original_url"]}
        
    )
 
 
@app.get("/urls", response_model = StandardResponse) 
def list_urls(page:int = 1, limit: int=10):
    
    if page<1 :
        page =1
    if limit<1:
        limit = 1 
    
    records = crud.get_all_urls(page = page, limit = limit)
    # to match the required response 
    formatted_data = []
    for record in records:
        formatted_data.append({
            "short_code": record["short_code"],
            "original_url": record["original_url"],
            "click_count": record["click_count"],
            "created_at": record["created_at"],
            "expires_at": record["expires_at"],
            "last_accessed": record["last_accessed"]
            
        })
    return StandardResponse(
        meta = ResponseMeta(
            success= True,
            status_code = 200,
            message = "Paginated URL List retrieved!"
        ),
        
        data = formatted_data
    )