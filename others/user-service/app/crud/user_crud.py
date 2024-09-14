from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.user_model import User, UserUpdate

# Add a New User to the Database
def add_new_user(user_data: User, session: Session):
    print("Adding User to Database")
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data

# Get All Users from the Database
def get_all_users(session: Session):
    all_users = session.exec(select(User)).all()
    return all_users

# Get a User by ID
def get_user_by_id(user_id: int, session: Session):
    user = session.exec(select(User).where(User.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_credentials(user_name: str, user_pass: str, session: Session):
    print('USER:', user_name, user_pass)
    user = session.exec(select(User).where(User.name == user_name and User.password == user_pass)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    return user

def validate_user(user_name: str, session: Session):
    user = session.exec(select(User).where(User.name == user_name)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    return user

# Delete User by ID
def delete_user_by_id(user_id: int, session: Session):
    # Step 1: Get the User by ID
    user = session.exec(select(User).where(User.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Step 2: Delete the User
    session.delete(user)
    session.commit()
    return {"message": "User Deleted Successfully"}

# Update User by ID
def update_user_by_id(user_id: int, to_update_user_data:UserUpdate, session: Session):
    # Step 1: Get the User by ID
    user = session.exec(select(User).where(User.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Step 2: Update the User
    hero_data = to_update_user_data.model_dump(exclude_unset=True)
    print(type(hero_data))
    user.sqlmodel_update(hero_data)
    session.add(user)
    session.commit()
    return user

