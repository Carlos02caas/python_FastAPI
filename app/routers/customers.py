from fastapi import APIRouter, Query, status, HTTPException
from sqlmodel import select
from models import CustomerCreate,CustomerUpdate,Customer, Plan, CustomerPlan, StatusEnum
from db import SessionDep

router = APIRouter()

@router.post("/customers", response_model=Customer,status_code=status.HTTP_201_CREATED, tags=["Customers"])
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

@router.post("/customers/{customer_id}/plans/{plan_id}", tags=["Customers"])
async def subscribe_customer_to_plan(
    customer_id: int, 
    plan_id: int, 
    session: SessionDep,
    plan_status: StatusEnum = Query()
):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer or Plan not found")
    
    customer_plan_db = CustomerPlan(
        plan_id=plan_db.id, 
        customer_id=customer_db.id,
        status=plan_status
    )
    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db

@router.get("/customers/{customer_id}/plans", tags=["Customers"])
async def customer_plans(customer_id: int,session: SessionDep, plan_status: StatusEnum = Query()):
    customer_db =session.get(Customer, customer_id)

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    query = (
        select(CustomerPlan)
        .where(CustomerPlan.customer_id == customer_db.id)
        .where(CustomerPlan.status == plan_status)
    )
    customer_plans = session.exec(query).all()
    return customer_plans
