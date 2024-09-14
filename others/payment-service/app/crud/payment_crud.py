from typing import Annotated
from app.deps import get_session
from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from app.models.payment_model import Payment, PaymentUpdate

# Add a New Inventory Item to the Database
async def add_new_payment(payment_data: Payment, session: Annotated[Session, Depends(get_session)]):
    print("Adding Payment to Database")
    
    async with session() as db:
        db.add(payment_data)
        await db.commit()
        await db.refresh(payment_data)
    
    return {"message": "Payment Added Successfully"}

# Add a New Payment to the Database
def add_new_payment(payment_data: Payment, session: Annotated[Session, Depends(get_session)]):
    print("Adding Payment to Database")
    
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return {"message": "Payment Added Successfully"}

# Get All Inventory Items from the Database
def get_all_payments(session: Session):
    all_payments = session.exec(select(Payment)).all()
    return all_payments

# Get an Inventory Item by ID
def get_payment_by_id(payment_id: int, session: Session):
    payment_info = session.exec(select(Payment).where(Payment.receipt_id == payment_id)).one_or_none()
    if payment_info is None:
        raise HTTPException(status_code=404, detail="Payment details not found")
    return payment_info

# Delete Inventory Item by ID
def delete_payment_by_id(payment_id: int, session: Session):
    # Step 1: Get the Inventory Item by ID
    payment = session.exec(select(Payment).where(Payment.receipt_id == payment_id)).one_or_none()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Step 2: Delete the Inventory Item
    session.delete(payment)
    session.commit()
    return {"message": "payment Deleted Successfully"}

# # Update Product by ID
def update_payment_by_id(payment_id: int, to_update_payment_data:PaymentUpdate, session: Session):
    # Step 1: Get the Product by ID
    payment = session.exec(select(Payment).where(Payment.receipt_id == payment_id)).one_or_none()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Step 2: Update the Product
    hero_data = to_update_payment_data.model_dump(exclude_unset=True)
    payment.sqlmodel_update(hero_data)
    session.add(payment)
    session.commit()
    return {"message": "Your payment has been paid Successfully"}