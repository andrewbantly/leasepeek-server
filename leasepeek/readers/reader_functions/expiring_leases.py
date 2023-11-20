from datetime import datetime, timedelta

def determine_date_format(date_str):
        parts = date_str.split("/")

        if len(parts) != 3:
            raise ValueError("Invalid date format")
        
        first, third = parts[0], parts[2]
        if len(first) == 4 and first.isdigit():
            return "%Y/%m/%d"
        elif len(third) == 4 and third.isdigit():
            return "%m/%d/%Y"
        else:
            raise ValueError("Unknown date format")

def expiring_leases(unit_data, as_of_date_str):
    as_of_date = datetime.strptime(as_of_date_str, "%m/%d/%Y")
    ninety_days_from_as_of_date = as_of_date + timedelta(days=90)
    floorplan_expiration_data = {}

    # Initialize floorplan data for all floorplans in unit_data
    for unit in unit_data:
        floorplan = unit['floorplan']
        if floorplan not in floorplan_expiration_data:
            floorplan_expiration_data[floorplan] = {
                    'expiring_in_90_days': {'count': 0, 'total_rent': 0},
                    'expired': {'count': 0, 'total_rent': 0}
                }

    for unit in unit_data:
        floorplan = unit['floorplan']
        if unit['leaseExpire']:
            try:
                expire_str = unit['leaseExpire'].replace('.', '/').replace('_', '/').replace('-', '/')
                date_format = determine_date_format(expire_str)
                lease_expire_date = datetime.strptime(expire_str, date_format)

                if lease_expire_date >= as_of_date and lease_expire_date <= ninety_days_from_as_of_date:
                    floorplan_expiration_data[floorplan]['expiring_in_90_days']['count'] += 1
                    floorplan_expiration_data[floorplan]['expiring_in_90_days']['total_rent'] += unit['rent']
                elif lease_expire_date <= as_of_date:
                    floorplan_expiration_data[floorplan]['expired']['count'] += 1
                    floorplan_expiration_data[floorplan]['expired']['total_rent'] += unit['rent']
            
            except ValueError:
                # The date format is not valid or is empty
                print(f"Can not determine lease expire of unit. Invalid date format for unit: {unit}")

    return floorplan_expiration_data