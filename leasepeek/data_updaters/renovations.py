from ..mongo_models import data_collection
from bson.objectid import ObjectId

def update_renovations_data(data):
    objectId = data.get('objectId')
    renovatedUnits = data.get('renovatedUnits')
    renovatedFloorPlans = data.get('renovatedFloorPlans')
    dataType = data.get('type')

    unit_data = data_collection.find_one({"_id": ObjectId(objectId)})
    if not unit_data:
        raise Exception(f"No document found with _id: {objectId}")
    
    data_inputted_successfully = False

    # Update unit data based on renovatedFloorPlans
    if dataType == 'floorPlan':
        if "floorplans" in unit_data:
            for plan_name in unit_data['floorplans']:
                is_renovated = plan_name in renovatedFloorPlans
                field_path = f"floorplans.{plan_name}.renovated"
                update_query = {"$set": {field_path: is_renovated}}
                result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)
                if result.matched_count > 0:
                    data_inputted_successfully = True
                else:
                    raise Exception("Data input error")
                
        if "data" in unit_data:
            for unit_info in unit_data['data']:                    
                unit_floorplan = unit_info['floorplan']
                is_renovated = unit_floorplan in renovatedFloorPlans
                field_path = f"data.{unit_info['unit']}.renovated"
                update_query = {"$set": {"data.$[elem].renovated": is_renovated}}
                array_filters = [{"elem.floorplan": unit_floorplan}]
                result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query, array_filters=array_filters)
            
            if result.matched_count > 0:
                data_inputted_successfully = True
            else:
                raise Exception("Data input error")

    # Update unit data based on renovatedUnits
    else:
        floorplans_to_update = []
        if "data" in unit_data:
            for unit_info in unit_data['data']:                    
                unit_id = unit_info['unit'] 
                is_renovated = unit_id in renovatedUnits
                if is_renovated:
                    floorplans_to_update.append(unit_info['floorplan'])
                field_path = f"data.{unit_id}.renovated"
                update_query = {"$set": {"data.$[elem].renovated": is_renovated}}
                array_filters = [{"elem.unit": unit_id}]
                result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query, array_filters=array_filters)
                if result.matched_count > 0:
                    data_inputted_successfully = True
                else:
                    raise Exception("Data input error")
        if "floorplans" in unit_data:
            for plan_name in unit_data['floorplans']:
                is_renovated = plan_name in floorplans_to_update
                field_path = f"floorplans.{plan_name}.renovated"
                update_query = {"$set": {field_path: is_renovated}}
                result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)
                if result.matched_count > 0:
                    data_inputted_successfully = True
                else:
                    raise Exception("Data input error")

    return "Document updated successfully." if data_inputted_successfully else "Data input error."