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
    dict_club = dict(club)
    dict_club.update({"thumbnail_id": str()})
    dict_club.update({"photo_id_list": list()})
    insert_result, inserted_id = db_controller.insert_document(collection_name, dict_club)
    if insert_result:
        return {"result": insert_result, "inserted_id": str(inserted_id)}
    return {}


@app.post("/clubs/{club_id}/upload_thumbnail")
async def post_club_thumbnail(club_id: str, thumbnail: UploadFile):
    content = await thumbnail.read()
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}

    if db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        thumbnail_id = db_controller.put_file(content, thumbnail.filename)
        update_thumbnail_result = db_controller.update_document(collection_name, {"_id": club_object_id},
                                                                {"thumbnail_id": thumbnail_id})
        return {"result": update_thumbnail_result}
    return {}


@app.post("/clubs/{club_id}/upload_photos")
async def post_club_photo(club_id: str, photos: List[UploadFile]):
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        photo_id_list = found_club["photo_id_list"]
        for photo in photos:
            content = await photo.read()
            photo_id = db_controller.put_file(content, photo.filename)
            photo_id_list.append(photo_id)
        update_photos_result = db_controller.update_document(collection_name, {"_id": club_object_id},
                                                             {"photo_id_list": photo_id_list})
        return {"result": update_photos_result}
    return {}


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
    include_keys = ["name", "current_number_of_people", "maximum_number_of_people"]
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        return_value = {include_key: found_club[include_key] for include_key in include_keys}
        return return_value
    return {}


@app.get("/clubs/{club_id}/detail_info")
async def get_club_detail_info(club_id: str):
    include_keys = ["name", "hashtag", "current_number_of_people", "maximum_number_of_people", "deadline", "dues"]
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        return_value = {include_key: found_club[include_key] for include_key in include_keys}
        return return_value
    return {}


@app.get("/clubs/{club_id}/thumbnail")
async def get_club_thumbnail(club_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}
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
    if not club_object_id:
        return {"result": "Invalid club id."}
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        for photo_id in found_club["photo_id_list"]:
            photo_id_list.append(str(photo_id))
        return {"photo_id_list": photo_id_list}
    return {}


@app.get("/clubs/{club_id}/photos/{photo_id}")
async def get_club_photo(club_id: str, photo_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    if not club_object_id:
        return {"result": "Invalid club id."}
    photo_object_id = db_controller.get_object_id(photo_id)
    if not photo_object_id:
        return {"result": "Invalid photo id."}
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        photo_id_list = found_club["photo_id_list"]
        if photo_object_id in photo_id_list:
            output_data = db_controller.get_file(photo_object_id)
            return StreamingResponse(BytesIO(output_data), media_type="image/png")
    return {}


@app.delete("/clubs/{club_id}")
async def delete_club(club_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        if found_club["thumbnail_id"]:
            await delete_club_thumbnail(club_id)
        if photo_id_list := found_club["photo_id_list"]:
            for photo_id in photo_id_list:
                await delete_club_photo(club_id, photo_id)
        if delete_club_result := db_controller.delete_document(collection_name, {"_id": club_object_id}):
            return {"result": delete_club_result}
    return {}


@app.delete("/club/{club_id}/thumbnail")
async def delete_club_thumbnail(club_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        if thumbnail_id := found_club["thumbnail_id"]:
            thumbnail_object_id = db_controller.get_object_id(thumbnail_id)
            db_controller.delete_file(thumbnail_object_id)
            if update_thumbnail_id_result := db_controller.update_document(collection_name, {"_id": club_object_id},
                                                                           {"thumbnail_id": str()}):
                return {"result": update_thumbnail_id_result}
    return {}


@app.delete("/club/{club_id}/photos/{photo_id}")
async def delete_club_photo(club_id: str, photo_id: str):
    club_object_id = db_controller.get_object_id(club_id)
    photo_object_id = db_controller.get_object_id(photo_id)
    if found_club := db_controller.find_one_document(collection_name, {"_id": club_object_id}):
        if (photo_id_list := found_club["photo_id_list"]) and photo_object_id in found_club["photo_id_list"]:
            db_controller.delete_file(photo_object_id)
            photo_id_list.remove(photo_object_id)
            if update_photo_id_list_result := db_controller.update_document(collection_name, {"_id": club_object_id},
                                                                            {"photo_id_list": photo_id_list}):
                return {"result": update_photo_id_list_result}
    return {}
