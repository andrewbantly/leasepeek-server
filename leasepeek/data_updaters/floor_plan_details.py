from ..mongo_models import data_collection
from bson.objectid import ObjectId
from collections import defaultdict

def update_floor_plan_data(data):
    objectId = data.get('objectId')
    floorPlanData = data.get('floorPlans')
    
    floorplans = defaultdict(list)

    for plan in floorPlanData:
        floorplans[plan['planCode']] = {
            'avgRent': plan['avgRent'],
            'sumRent': plan['sumRent'],
            'avgMarket': plan['avgMarket'],
            'sumMarket': plan['sumMarket'],
            'unitCount': plan['unitCount'],
            'avgSqft': plan['avgSqft'],
            'unitStatuses': plan['unitStatuses'],
            'planName': plan['planName'],
            'planType': plan['planType'],
            'beds': plan['beds'],
            'baths': plan['baths'],
            'renovated': plan['renovated'],
        }
        
    update_query = {
        "$set": {
            "floorplans": dict(floorplans)
        }
    }
    result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)

    if result.matched_count > 0:
        return "Document updated successfully."
    else:
        raise Exception(f"No document found with _id: {objectId}")