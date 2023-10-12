def floorplan_survey(data):
    # Initialize floor plans dictionary that will be returned 
    floorplans = {}

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        # Only accept values that are integers.
        if type(unit['market']) != int:
            print(f"Type Error. {unit['market']} is not an integer.")
        else:
            if unit['floorplan'] in floorplans:
                floorplans[unit['floorplan']].append(unit['market'])
            if unit['floorplan'] not in floorplans:
                floorplans[unit['floorplan']] = [unit['market']]
   
    # Modify the floorplans dictionary to give relevant information
    for plan in floorplans:
        plan_count = len(floorplans[plan])
        market_sum = sum(floorplans[plan])
        avg_market = round(sum(floorplans[plan]) / plan_count, 2)
        floorplans[plan] = {'sum': market_sum, 'count': plan_count, 'average': avg_market}
    
    return floorplans