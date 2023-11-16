from datetime import datetime, timedelta

keywords = {'Former applicant'}

def recent_leases(unit_data, as_of_date_str):
    print('Finding recent leases.')
    print(unit_data[3])
    print(f'As of date string: {as_of_date_str}')

    if as_of_date_str == 'Date not found':
        as_of_date = datetime.today()
        print(f"Using {as_of_date} for as of date in recent_leases.py.")
    else:
        as_of_date = datetime.strptime(as_of_date_str, '%m/%d/%Y')
        print(f"Using as of date: {as_of_date}")

    date_90_days_ago = as_of_date - timedelta(days=90)
    print(f"90 days ago is: {date_90_days_ago}")
    date_60_days_ago = as_of_date - timedelta(days=60)
    print(f"60 days ago is: {date_60_days_ago}")
    date_30_days_ago = as_of_date - timedelta(days=30)
    print(f"30 days ago is: {date_30_days_ago}")

    recent_two = {}
    recent_time_windows = {
        'last_90_days': {},
        'last_60_days': {},
        'last_30_days': {}
    }

    # Initialize dictionaries for floorplans
    floorplan_data = {}

    for unit in unit_data:
        floorplan = unit['floorplan']
        if floorplan not in floorplan_data:
            floorplan_data[floorplan] = {
                'recent_two': 0,
                'recent_leases': {
                    'last_90_days': 0,
                    'last_60_days': 0,
                    'last_30_days': 0
                }
            }
        if floorplan not in recent_two:
            recent_two[floorplan] = []
        for window in recent_time_windows:
            if floorplan not in recent_time_windows[window]:
                recent_time_windows[window][floorplan] = []

    def parse_date(date_str):
        if isinstance(date_str, str) and date_str.strip():
            try:
                return datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                pass  

            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None  
        return None

    unit_data_sorted = sorted(unit_data, key=lambda unit: parse_date(unit.get('moveIn') or unit.get('leaseStart')) or datetime.min, reverse=True)

    for unit in unit_data_sorted:
        floorplan = unit['floorplan']
        sort_date = parse_date(unit.get('moveIn') or unit.get('leaseStart'))

        if sort_date and sort_date <= as_of_date and unit['status'] not in keywords:
            if floorplan not in recent_two:
                recent_two[floorplan] = [unit]
            elif len(recent_two[floorplan]) < 2:
                recent_two[floorplan].append(unit)

            for window in recent_time_windows.keys():
                start_date = {
                    'last_90_days': date_90_days_ago,
                    'last_60_days': date_60_days_ago,
                    'last_30_days': date_30_days_ago
                }[window]

                if start_date <= sort_date <= as_of_date:
                    if floorplan not in recent_time_windows[window]:
                        recent_time_windows[window][floorplan] = [unit]
                    else:
                        recent_time_windows[window][floorplan].append(unit)

    # Populate floorplan_data with counts
    for floorplan in floorplan_data:
        floorplan_data[floorplan]['recent_two'] = len(recent_two.get(floorplan, []))
        for window in recent_time_windows:
            floorplan_data[floorplan]['recent_leases'][window] = len(recent_time_windows[window].get(floorplan, []))

    # Return the combined counts
    return floorplan_data
