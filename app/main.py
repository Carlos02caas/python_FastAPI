import time
from typing import Annotated
import zoneinfo
from fastapi import Depends, FastAPI, HTTPException, Request, status
from datetime import datetime

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models import  Transaction, Invoice

from db import SessionDep, create_all_tables
from sqlmodel import select
from .routers import customers, transactions, plans

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(plans.router)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request {request.method} {request.url} executed in {process_time:.4f} seconds")
    return response

security = HTTPBasic()

@app.get("/")
def read_root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    print(credentials)
    if credentials.username == "calavez" and credentials.password == "123456":
        return {"message": f"Hola, {credentials.username}"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

country_timezones = {
    "BR": "America/Sao_Paulo",
    "US": "America/New_York",
    "IN": "Asia/Kolkata",
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "PE": "America/Lima",
}

@app.get("/time/{iso_code}")
async def get_time_by_iso(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    now = datetime.now(tz)
    return {"time": f"{now}"}


@app.post("/invoices")
async def create_invoices(invoice_data: Invoice):
    return invoice_data