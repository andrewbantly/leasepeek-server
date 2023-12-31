# Defaultdict automatically initializes dictionary entries to a default value if the key has not been set yet. This means one doesn't need to check if the key exists in the dictionary before appending to it.
from collections import defaultdict

ignore_unit_keywords = {'upcoming', 'approved', 'Future Residents/Applicants', 'Applicant', 'applicant', 'Pending renewal', 'Former resident', 'Former applicant'}
occupied_keywords = {'Occupied', 'occupied', 'Occupied-NTV', 'Occupied-NTVL', 'O', 'NR', 'NU'}

def floorplan_survey(data):
    # Initialize floor plans dictionary that will be returned using defaultdict
    floorplans = defaultdict(list)

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        if unit['status'] not in ignore_unit_keywords:
            try:
                market = unit['market']
                rent = unit['rent']
                sqft = unit['sqft']
                status = unit['status']
                floorplans[unit['floorplan']].append({'market': market, 'rent': rent, 'sqft': sqft, 'status': status})
            except (ValueError, TypeError) as e:
                print(f"Error converting values for unit. Details: {e}")
        else:
            continue

    # Modify the floorplans dictionary to give relevant information
    for plan, units in floorplans.items():
        market_sum = sum(unit['market'] for unit in units)
        plan_count = len(units)
        rent_sum = sum(unit['rent'] for unit in units if unit['status'] in occupied_keywords)
        rent_count = sum(1 for unit in units if unit['status'] in occupied_keywords)
        sqft_sum = sum(unit['sqft'] for unit in units)
        avg_market = round(market_sum / plan_count, 2)
        avg_rent = round(rent_sum / rent_count, 2) if rent_count > 0 else 0
        avg_sqft = round(sqft_sum / plan_count, 2) if sqft_sum > 0 else 0
        
        status_count = {}
        for unit in units:
            status = unit['status']
            if status in status_count:
                status_count[status] += 1
            else:
                status_count[status] = 1

        floorplans[plan] = {
            'avgRent': avg_rent,
            'sumRent': rent_sum,
            'avgMarket': avg_market,
            'sumMarket': market_sum,
            'unitCount': plan_count,
            'avgSqft': avg_sqft,
            'unitStatuses': status_count,
            'planName': plan,
            'planType': 'residential',
            'beds': "0",
            'baths': "0",
            "renovated": False,
        }

    # for i, plan in enumerate(floorplans):
    #     print(f"07_TEST_FILE_FLOORPLAN_{i+1} = '{plan}'")
        
    # Convert defaultdict back to dic for the return value
    return dict(floorplans)