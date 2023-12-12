from ..mongo_models import data_collection
from bson.objectid import ObjectId

def update_unit_statuses(data):
    objectId = data.get('objectId')
    unit_status_data = data.get('unitStatuses')

    update_query = {
            "$set": {
                "vacancy": unit_status_data
            }
        }

    result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)

    if result.matched_count > 0:
        return "Document updated successfully."
    else:
        raise Exception(f"No document found with _id: {objectId}")