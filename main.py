import zoneinfo
from fastapi import FastAPI, HTTPException, status
from datetime import datetime

from models import CustomerCreate,CustomerUpdate,Customer, Transaction, Invoice

from db import SessionDep, create_all_tables
from sqlmodel import select

app = FastAPI(lifespan=create_all_tables)


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

db_customers: list[Customer] = []


@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    #current_id = len(db_customers)
    #db_customers.append(customer)
    return customer

@app.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    return customer

@app.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def update_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    costumer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(costumer_data_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    session.delete(customer)
    session.commit()
    return {
        "deleted": True
    }

@app.get("/customers", response_model=list[Customer])
async def list_customers(session: SessionDep):
    db_customers = session.exec(select(Customer)).all()
    return db_customers

@app.post("/transactions")
async def create_transactions(transaction_data: Transaction):
    return transaction_data

@app.post("/invoices")
async def create_invoices(invoice_data: Invoice):
    return invoice_data