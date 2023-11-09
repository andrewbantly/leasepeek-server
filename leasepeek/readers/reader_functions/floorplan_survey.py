# Defaultdict automatically initializes dictionary entries to a default value if the key has not been set yet. This means one doesn't need to check if the key exists in the dictionary before appending to it.
from collections import defaultdict

def floorplan_survey(data):
    # Initialize floor plans dictionary that will be returned using defaultdict
    floorplans = defaultdict(list)

    # Add unit floor plan data to the floor_plans dictionary
    for unit in data:
        try:
            market = int(unit['market'])
            rent = int(unit['rent'])
            sqft = int(unit['sqft'])
            floorplans[unit['floorplan']].append({'market': market, 'rent': rent, 'sqft': sqft})
        except ValueError:
            print(f"Type Error. {unit['market']}, {unit['rent']}, or {unit['sqft']} is not an integer.")

    # Modify the floorplans dictionary to give relevant information
    for plan, units in floorplans.items():
        market_sum = sum(unit['market'] for unit in units)
        plan_count = len(units)
        rent_sum = sum(unit['rent'] for unit in units)
        rent_count = sum(1 for unit in units if unit['rent'] > 0)
        sqft_sum = sum(unit['sqft'] for unit in units)
        
        avg_market = round(market_sum / plan_count, 2)
        avg_rent = round(rent_sum / rent_count, 2) if rent_count > 0 else 0
        avg_sqft = round(sqft_sum / plan_count, 2)

        print(f"For floorplan {plan}, the average rent is {avg_rent} with an average sqft of {avg_sqft}. The stated market value is {avg_market} on average.")

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
