from ..mongo_models import data_collection
from bson.objectid import ObjectId

def update_basic_data(data):
    objectId = data.get('objectId')
    updated_asOf = data.get('asOf')
    updated_market = data.get('market')
    updated_buildingName = data.get('buildingName')
    updated_unitsConfirmed = data.get('unitsConfirmed')
    updated_addressLine1 = data.get('addressLine1')
    updated_addressLine2 = data.get('addressLine2')
    updated_city = data.get('city')
    updated_state = data.get('state')
    updated_zipCode = data.get('zipCode')

    update_query = {
        "$set": {
            "asOf": updated_asOf,
            "unitsConfirmed": updated_unitsConfirmed,
            "location.market": updated_market,
            "location.buildingName": updated_buildingName,
            "location.address.addressLine1": updated_addressLine1,
            "location.address.addressLine2": updated_addressLine2,
            "location.address.city": updated_city,
            "location.address.state": updated_state,
            "location.address.zipCode": updated_zipCode
        }
    }

    result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)

    if result.matched_count > 0:
        return "Document updated successfully."
    else:
        raise Exception(f"No document found with _id: {objectId}")
