# Defaultdict automatically initializes dictionary entries to a default value if the key has not been set yet. This means one doesn't need to check if the key exists in the dictionary before appending to it.
from collections import defaultdict

def floorplan_survey(data):
    # Initialize floor plans dictionary that will be returned using defaultdict
    floorplans = defaultdict(list)

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        try:
            market = unit['market']
            rent = unit['rent']
            sqft = unit['sqft']
            floorplans[unit['floorplan']].append({'market': market, 'rent': rent, 'sqft': sqft})
        except (ValueError, TypeError) as e:
            print(f"Error converting values for unit. Details: {e}")


    # Modify the floorplans dictionary to give relevant information
    for plan, units in floorplans.items():
        market_sum = sum(unit['market'] for unit in units)
        plan_count = len(units)
        rent_sum = sum(unit['rent'] for unit in units)
        rent_count = sum(1 for unit in units if unit['rent'] > 0)
        sqft_sum = sum(unit['sqft'] for unit in units)
        avg_market = round(market_sum / plan_count, 2)
        avg_rent = round(rent_sum / rent_count, 2) if rent_count > 0 else 0
        avg_sqft = round(sqft_sum / plan_count, 2) if sqft_sum > 0 else 0

        floorplans[plan] = {
            'avgRent': avg_rent,
            'sumRent': rent_sum,
            'avgMarket': avg_market,
            'sumMarket': market_sum,
            'unitCount': plan_count,
            'avgSqft': avg_sqft,
        }

    # Convert defaultdict back to dict for the return value
    return dict(floorplans)