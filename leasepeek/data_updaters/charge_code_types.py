from ..mongo_models import data_collection
from bson.objectid import ObjectId

def update_charge_code_types(data):
    objectId = data.get('objectId')
    chargeData = data.get('charges')

    update_query = {
        "$set": {
            "charges": chargeData
        }
    }

    result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)

    if result.matched_count > 0:
        return "Document updated successfully."
    else:
        raise Exception(f"No document found with _id: {objectId}")