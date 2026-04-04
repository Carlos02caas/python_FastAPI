from fastapi import APIRouter, status, HTTPException, Query
from db import SessionDep
from sqlmodel import select
from models import Transaction, TransactionCreate, Customer

router = APIRouter()

@router.post("/transactions", response_model=Transaction,status_code=status.HTTP_201_CREATED, tags=["Transactions"])
async def create_transactions(transaction_data: TransactionCreate, session: SessionDep):
    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get("customer_id"))

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    transaction_db = Transaction.model_validate(transaction_data_dict)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)

    return transaction_db

@router.get("/transactions", tags=["Transactions"])
async def list_transactions(
    session: SessionDep, 
        skip: int = Query(0, description="Registros omitidos"),
        limit: int = Query(10, description="Registros a mostrar")
    ):
    query = select(Transaction).offset(skip).limit(limit)
    transactions = session.exec(query).all()
    return transactions