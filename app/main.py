import datetime
from io import BytesIO
from typing import List

from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.db_controller import DBController

app = FastAPI()

db_name = "Udong"
collection_name = "circle"
db_controller = DBController(db_name)


class Circle(BaseModel):
    name: str
    hashtag: list
    current_number_of_people: int
    maximum_number_of_people: int
    deadline: datetime.datetime
    dues: int


@app.post("/circles")
async def post_circle_info(circle: Circle):
    if insert_result := db_controller.insert_document(collection_name, dict(circle)):
        return {"result": insert_result}
    return {}


@app.post("/circles/{circle_id}/upload_thumbnail")
async def post_circle_thumbnail(circle_id: str, thumbnail: UploadFile):
    content = await thumbnail.read()
    circle_object_id = db_controller.get_object_id(circle_id)
    thumbnail_id = db_controller.put_file(content, thumbnail.filename)
    update_thumbnail_result = db_controller.update_document(collection_name, {"_id": circle_object_id},
                                                            {"thumbnail_id": thumbnail_id})
    return {"result": update_thumbnail_result}


@app.post("/circles/{circle_id}/upload_photos")
async def post_circle_photo(circle_id: str, photos: List[UploadFile]):
    photo_id_list = list()
    circle_object_id = db_controller.get_object_id(circle_id)
    for photo in photos:
        content = await photo.read()
        photo_id = db_controller.put_file(content, photo.filename)
        photo_id_list.append(photo_id)
    update_photos_result = db_controller.update_document(collection_name, {"_id": circle_object_id},
                                                         {"photo_id_list": photo_id_list})
    return {"result": update_photos_result}


@app.get("/circles")
async def get_circle_id_list():
    circle_id_list = list()
    if found_circles := db_controller.find_documents(collection_name, {}):
        for circle in found_circles:
            circle_id_list.append(str(circle['_id']))
        return {"circle_id_list": circle_id_list}
    return {}


@app.get("/circles/{circle_id}/concise_info")
async def get_circle_concise_info(circle_id: str):
    removed_keys = ["hashtag", "deadline", "dues", "thumbnail_id", "photo_id_list"]
    circle_object_id = db_controller.get_object_id(circle_id)
    if found_circle := db_controller.find_one_document(collection_name, {"_id": circle_object_id}):
        found_circle["_id"] = str(found_circle["_id"])
        for removed_key in removed_keys:
            if removed_key in found_circle:
                found_circle.pop(removed_key)
        return found_circle
    return {}


@app.get("/circles/{circle_id}/detail_info")
async def get_circle_detail_info(circle_id: str):
    removed_keys = ["thumbnail_id", "photo_id_list"]
    circle_object_id = db_controller.get_object_id(circle_id)
    if found_circle := db_controller.find_one_document(collection_name, {"_id": circle_object_id}):
        found_circle["_id"] = str(found_circle["_id"])
        for removed_key in removed_keys:
            if removed_key in found_circle:
                found_circle.pop(removed_key)
        return found_circle
    return {}


@app.get("/circles/{circle_id}/thumbnail")
async def get_circle_thumbnail(circle_id: str):
    circle_object_id = db_controller.get_object_id(circle_id)
    if found_circle := db_controller.find_one_document(collection_name, {"_id": circle_object_id}):
        thumbnail_id = found_circle["thumbnail_id"]
        thumbnail_object_id = db_controller.get_object_id(thumbnail_id)
        output_data = db_controller.get_file(thumbnail_object_id)
        return StreamingResponse(BytesIO(output_data), media_type="image/png")
    return {}


@app.get("/circles/{circle_id}/photos")
async def get_photo_id_list(circle_id: str):
    photo_id_list = list()
    circle_object_id = db_controller.get_object_id(circle_id)
    if found_circle := db_controller.find_one_document(collection_name, {"_id": circle_object_id}):
        for photo_id in found_circle["photo_id_list"]:
            photo_id_list.append(str(photo_id))
        return {"photo_id_list": photo_id_list}
    return {}


@app.get("/circles/{circle_id}/photos/{photo_id}")
async def get_circle_photo(circle_id: str, photo_id: str):
    circle_object_id = db_controller.get_object_id(circle_id)
    photo_object_id = db_controller.get_object_id(photo_id)
    if found_circle := db_controller.find_one_document(collection_name, {"_id": circle_object_id}):
        photo_id_list = found_circle["photo_id_list"]
        if photo_object_id in photo_id_list:
            output_data = db_controller.get_file(photo_object_id)
            return StreamingResponse(BytesIO(output_data), media_type="image/png")
    return {}
