#!/bin/bash

# Function to display the help guide
display_help() {
    echo "Usage: $0 [option] <feature_name>"
    echo
    echo "Options:"
    echo "  -c, --create     Create a new feature folder with the specified name"
    echo "  -h, --help       Display this help message"
    echo
    echo "Example:"
    echo "  $0 -c user_profile"
    exit 0
}

# Function to create a feature folder with necessary files
create_feature() {
    FEATURE_NAME=$1
    if [ -z "$FEATURE_NAME" ]; then
        echo "Error: Feature name is required."
        display_help
    fi

    # Check if the folder already exists
    if [ -d "$FEATURE_NAME" ]; then
        echo "Error: Feature folder '$FEATURE_NAME' already exists."
        exit 1
    fi

    # Create the feature folder
    mkdir -p "$FEATURE_NAME"

    # Create __init__.py (Empty for now)
    touch "$FEATURE_NAME/__init__.py"

    # Create models.py
    cat <<EOL > "$FEATURE_NAME/models.py"
from sqlalchemy import Column, Integer, String
from app.core.database import Base  # Assuming you have a Base model class

class Item(Base):
    __tablename__ = "${FEATURE_NAME}_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
EOL


    # Create schemas.py
    cat <<EOL > "$FEATURE_NAME/schemas.py"
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
EOL


    # Create services.py
    cat <<EOL > "$FEATURE_NAME/services.py"
from sqlalchemy.orm import Session
from . import models, schemas

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
EOL

    # Create routes.py
    cat <<EOL > "$FEATURE_NAME/routes.py"
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_session
from . import schemas, services


router = APIRouter()


@router.get("/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = services.get_items(db, skip=skip, limit=limit)
    return items


@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return services.create_user_item(db=db, item=item)
EOL

    echo "Feature folder '$FEATURE_NAME' created successfully with necessary files."
}


# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    display_help
fi

# Parse command-line options
case "$1" in
    -c|--create)
        if [ -z "$2" ]; then
            echo "Error: Feature name is required."
            display_help
        fi
        create_feature "$2"
        ;;
    -h|--help)
        display_help
        ;;
    *)
        echo "Error: Invalid option."
        display_help
        ;;
esac
