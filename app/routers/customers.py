from fastapi import APIRouter, status, HTTPException
from sqlmodel import select
from models import CustomerCreate,CustomerUpdate,Customer
from db import SessionDep

router = APIRouter()

@router.post("/customers", response_model=Customer, tags=["Customers"])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    #current_id = len(db_customers)
    #db_customers.append(customer)
    return customer

@router.get("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
async def read_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    return customer

@router.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=["Customers"])
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

@router.delete("/customers/{customer_id}", tags=["Customers"])
async def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    session.delete(customer)
    session.commit()
    return {
        "deleted": True
    }

@router.get("/customers", response_model=list[Customer], tags=["Customers"])
async def list_customers(session: SessionDep):
    db_customers = session.exec(select(Customer)).all()
    return db_customers