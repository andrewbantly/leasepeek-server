from ..mongo_models import data_collection
from bson.objectid import ObjectId

def update_renovations_data(data):
    objectId = data.get('objectId')
    renovatedUnits = data.get('renovatedUnits')
    renovatedFloorPlans = data.get('renovatedFloorPlans')
    dataType = data.get('type')

    unit_data = data_collection.find_one({"_id": ObjectId(objectId)})

    data_inputted_successfully = False

    print(f'renovated units: {renovatedUnits}')
    print(f'renovated floor plans: {renovatedFloorPlans}')

    if unit_data and "floorplans" in unit_data:
        for plan_name, plan_data in unit_data['floorplans'].items():
            is_renovated = plan_name in renovatedFloorPlans

            field_path = f"floorplans.{plan_name}.renovated"

            update_query = {"$set": {field_path: is_renovated}}
            result = data_collection.update_one({"_id": ObjectId(objectId)}, update_query)

            if result.matched_count > 0:
                data_inputted_successfully = True
            else:
                raise Exception("Data input error")

    if data_inputted_successfully:
        print("Data updated successfully")
    else:
        print("No data updated")





    #     print('data type')
    # elif dataType == "unitNumber":
    #     print('data type unit Num')
    # else:
    #     print('errror')


    #  data type: floorPlan
    #  ['B3', 'E1A', 'A5']

    # data type: unitNumber
    # ['1-1302', '1-1306', '1-1308']

    print()
    print(f"true? {data_inputted_successfully}")

    return 'success'