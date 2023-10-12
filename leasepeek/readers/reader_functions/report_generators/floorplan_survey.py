def floorplan_survey(data):
    # Initialize floor plans dictionary that will be returned 
    floorplans = {}

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        # Only accept values that are integers.
        if type(unit['market']) != int or type(unit['rent']) != int:
            print(f"Type Error. {unit['market']} or {unit['rent']} is not an integer.")

        if unit['floorplan'] in floorplans:
            floorplans[unit['floorplan']].append({'market': unit['market'], 'rent': unit['rent']})
        else:
            floorplans[unit['floorplan']] = [{'market': unit['market'], 'rent': unit['rent']}]
   
    # Modify the floorplans dictionary to give relevant information
    for plan in floorplans:
        plan_count = len(floorplans[plan])
        market_sum = sum([unit['market'] for unit in floorplans[plan]])
        rent_sum = sum([unit['rent'] for unit in floorplans[plan]])
        
        avg_market = round(market_sum / plan_count, 2)
        avg_rent = round(rent_sum / plan_count, 2)

        floorplans[plan] = {
            'market': {'sum': market_sum, 'count': plan_count, 'average': avg_market},
            'rent': {'sum': rent_sum, 'count': plan_count, 'average': avg_rent}
        }
    
    return floorplans
