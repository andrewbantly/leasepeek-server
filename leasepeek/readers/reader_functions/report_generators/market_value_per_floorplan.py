def market_value_per_floorplan(data):
    # Initialize floor plans dictionary that will be returned 
    floor_plans = {}

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        # Only accept values that are integers.
        if type(unit['market']) != int:
            print(f"Type Error. {unit['market']} is not an integer.")
        else:
            if unit['floorplan'] in floor_plans:
                floor_plans[unit['floorplan']].append(unit['market'])
            if unit['floorplan'] not in floor_plans:
                floor_plans[unit['floorplan']] = [unit['market']]
   
    # Modify the floor_plans dictionary to give relevant information
    for plan in floor_plans:
        plan_count = len(floor_plans[plan])
        market_sum = sum(floor_plans[plan]) / plan_count
        avg_market = round(sum(floor_plans[plan]) / plan_count, 2)
        floor_plans[plan] = {'sum': market_sum, 'count': plan_count, 'average': avg_market}
        
    return floor_plans