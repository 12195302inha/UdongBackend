from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS
import datetime


class DBController():
    def __init__(self, database):
        client = MongoClient(host='localhost', port=27017)
        self.db = client[database]
        self.fs = GridFS(self.db)

    def insert_document(self, collection, document):
        collection = self.db[collection]
        if insert_result := collection.insert_one(document):
            return insert_result.acknowledged, insert_result.inserted_id
        else:
            return False

    def find_one_document(self, collection, query):
        collection = self.db[collection]
        if find_result := collection.find_one(query):
            return find_result
        else:
            return None

    def find_documents(self, collection, query):
        collection = self.db[collection]
        if find_results := collection.find(query):
            return list(find_results)
        else:
            return None

    def update_document(self, collection, query, update_value):
        collection = self.db[collection]
        if update_result := collection.update_one(query, {"$set": update_value}):
            return update_result.acknowledged
        else:
            return False

    def delete_document(self, collection, query):
        collection = self.db[collection]
        if delete_result := collection.delete_one(query):
            return delete_result.acknowledged
        else:
            return False

    @staticmethod
    def get_object_id(_id):
        return ObjectId(_id)

    def put_file(self, contents, filename):
        return self.fs.put(contents, filename=filename)

    def get_file(self, thumbnail_id):
        return self.fs.get(thumbnail_id).read()


if __name__ == '__main__':
    db_controller = DBController("Udong")
    print(db_controller.insert_document("club", {
        "name": "심준열",
        "hashtag": ["즐거운", "활기찬"],
        "current_number_of_people": 12,
        "maximum_number_of_people": 90,
        "deadline": datetime.datetime.now(),
        "dues": 10000}))
    print(db_controller.find_one_document("club", {"name": "심준열"}))
    print(db_controller.update_document("club", {"name": "심준열"}, {"dues": 12000}))
    print(db_controller.delete_document("club", {"name": "심준열"}))
    print(db_controller.find_documents("club", {}))

