import datetime
from io import BytesIO
from typing import List

from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.db_controller import DBController

app = FastAPI()

db_name = "Udong"
collection_name = "club"
db_controller = DBController(db_name)


class Club(BaseModel):
    name: str
    hashtag: list
    current_number_of_people: int
    maximum_number_of_people: int
    deadline: datetime.datetime
    dues: int


@app.post("/clubs")
async def post_club_info(club: Club):
    if insert_result := db_controller.insert_document(collection_name, dict(club)):
        return {"result": insert_result}
    return {}


@app.post("/clubs/{club_id}/upload_thumbnail")
async def post_club_thumbnail(club_id: str, thumbnail: UploadFile):
    content = await thumbnail.read()
    club_object_id = db_controller.get_object_id(club_id)
    thumbnail_id = db_controller.put_file(content, thumbnail.filename)
    update_thumbnail_result = db_controller.update_document(collection_name, {"_id": club_object_id},
                                                            {"thumbnail_id": thumbnail_id})
    return {"result": update_thumbnail_result}


@app.post("/clubs/{club_id}/upload_photos")
async def post_club_photo(club_id: str, photos: List[UploadFile]):
    photo_id_list = list()
    club_object_id = db_controller.get_object_id(club_id)
    for photo in photos:
        content = await photo.read()
        photo_id = db_controller.put_file(content, photo.filename)
        photo_id_list.append(photo_id)
    update_photos_result = db_controller.update_document(collection_name, {"_id": club_object_id},
                                                         {"photo_id_list": photo_id_list})
    return {"result": update_photos_result}


@app.get("/clubs")
async def get_club_id_list():
    club_id_list = list()
    if found_clubs := db_controller.find_documents(collection_name, {}):
        for club in found_clubs:
            club_id_list.append(str(club['_id']))
        return {"club_id_list": club_id_list}
    return {}


@app.get("/clubs/{club_id}/concise_info")
async def get_club_concise_info(club_id: str):
    removed_keys = ["_id", "hashtag", "deadline", "dues", "thumbnail_id", "photo_id_list"]
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        found_club["_id"] = str(found_club["_id"])
        for removed_key in removed_keys:
            if removed_key in found_club:
                found_club.pop(removed_key)
        return found_club
    return {}


@app.get("/clubs/{club_id}/detail_info")
async def get_club_detail_info(club_id: str):
    removed_keys = ["_id", "thumbnail_id", "photo_id_list"]
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        found_club["_id"] = str(found_club["_id"])
        for removed_key in removed_keys:
            if removed_key in found_club:
                found_club.pop(removed_key)
        return found_club
    return {}


@app.get("/clubs/{club_id}/thumbnail")
async def get_club_thumbnail(club_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        thumbnail_id = found_club["thumbnail_id"]
        thumbnail_object_id = db_controller.get_object_id(thumbnail_id)
        output_data = db_controller.get_file(thumbnail_object_id)
        return StreamingResponse(BytesIO(output_data), media_type="image/png")
    return {}


@app.get("/clubs/{club_id}/photos")
async def get_photo_id_list(club_id: str):
    photo_id_list = list()
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        for photo_id in found_club["photo_id_list"]:
            photo_id_list.append(str(photo_id))
        return {"photo_id_list": photo_id_list}
    return {}


@app.get("/clubs/{club_id}/photos/{photo_id}")
async def get_club_photo(club_id: str, photo_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    photo_object_id = db_controller.get_object_id(photo_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        photo_id_list = found_club["photo_id_list"]
        if photo_object_id in photo_id_list:
            output_data = db_controller.get_file(photo_object_id)
            return StreamingResponse(BytesIO(output_data), media_type="image/png")
    return {}
