import os
import json
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List
import hashlib



# Define the path to the images & sqlite3 database
images = pathlib.Path(__file__).parent.resolve() / "images"
db = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"

class Item(BaseModel):
    name: str
    category: str

def get_db():
    if not db.exists():
        yield

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


# STEP 5-1: set up the database connection
def setup_database():
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield


app = FastAPI(lifespan=lifespan)

logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class HelloResponse(BaseModel):
    items: List[Item]


@app.get("/items", response_model=HelloResponse)
def hello():
    with open("items.json", "r") as f:
        data = json.load(f)

    return HelloResponse(**data)

class AddItemResponse(BaseModel):
    message: str

# add_item is a handler to add a new item for POST /items .
@app.post("/items", response_model=AddItemResponse)
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    db: sqlite3.Connection = Depends(get_db),
):
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    insert_item(Item(name=name, category=category))
    return AddItemResponse(**{"message": f"item received: {name}"})


# get_image is a handler to return an image for GET /images/{filename} .
@app.get("/images/{image_name}")
async def get_image(image_name):
    # Create image path
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)


def insert_item(item: Item):
    # STEP 4-2: add an implementation to store an item

    file_path = 'items.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({"items":[]},f, indent=4)
    with open(file_path, 'r') as f:
        data = json.load(f)
    new_item  = {
        "name": item.name,
        "category": item.category

    }
    data["items"].append(new_item)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    pass
