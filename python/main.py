import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from contextlib import asynccontextmanager
import json
from fastapi import File, UploadFile
import hashlib



# Define the path to the images & sqlite3 database
images = pathlib.Path(__file__).parent.resolve() / "images"
db = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"


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
    items: list


@app.get("/", response_model=HelloResponse)
def hello():
    with open('items.json', 'r') as f:
        data = json.load(f)
    return HelloResponse(items=data.get("items", []))

class AddItemResponse(BaseModel):
    items: list

# add_item is a handler to add a new item for POST /items .
@app.post("/items", response_model=AddItemResponse)
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db),
):
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    hashed_value = hashlib.sha256(image.filename.encode()).hexdigest()
    image_name = hashed_value + ".jpg"

    items = insert_item(Item(name=name,category=category,image_name=image_name))
    return AddItemResponse(items=items)


# get_image is a handler to return an image for GET /images/{filename} .
@app.get("/items/{item_id}", response_model=HelloResponse)
def new_get(item_id:int):
    with open('items.json', 'r') as f:
        data = json.load(f)
    items=data.get("items", [])

    try:
        return HelloResponse(items=[items[item_id]])
    except IndexError:
        return HelloResponse(items=[])
    #with open('items.json', 'r') as f:

    #return HelloResponse(message=data.get("items", [item_id]))

@app.get("/images/{image_name}")
async def get_image(image_name):
    # Create image pat

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)


class Item(BaseModel):
    name: str
    category: str
    image_name: str

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
        "category": item.category,
        "image_name": item.image_name
    }
    data["items"].append(new_item)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    return data["items"]
