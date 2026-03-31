import zoneinfo
from fastapi import FastAPI, HTTPException, status
from datetime import datetime

from models import  Transaction, Invoice

from db import SessionDep, create_all_tables
from sqlmodel import select
from .routers import customers

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
async def time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    now = datetime.now(tz)
    return {"time": f"{now}"}


@app.post("/transactions")
async def create_transactions(transaction_data: Transaction):
    return transaction_data

@app.post("/invoices")
async def create_invoices(invoice_data: Invoice):
    return invoice_data