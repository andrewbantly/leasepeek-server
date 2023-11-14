from datetime import datetime, timedelta

def recent_leases(unit_data, as_of_date_str):
    print('Finding recent leases.')

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

    # Initialize recent_two and recent_time_windows for each floorplan
    for unit in unit_data:
        floorplan = unit['floorplan']
        if floorplan not in recent_two:
            recent_two[floorplan] = []
        for window in recent_time_windows:
            if floorplan not in recent_time_windows[window]:
                recent_time_windows[window][floorplan] = []


    def parse_date(date_str):
        if isinstance(date_str, str) and date_str.strip():
            # First try parsing with the '%m/%d/%Y' format
            try:
                return datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                # If it fails, move on to the next format
                pass  

            # Then try parsing with the '%Y-%m-%d' format
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # If it still fails, return None
                return None  
        return None


    # Sort the unit_data by the sort_date
    unit_data_sorted = sorted(unit_data, key=lambda unit: parse_date(unit.get('moveIn') or unit.get('leaseStart')) or datetime.min, reverse=True)

    # Collect the most recent two units per floorplan
    for unit in unit_data_sorted:
        floorplan = unit['floorplan']
        sort_date = parse_date(unit.get('moveIn') or unit.get('leaseStart'))

        if sort_date is None:
            continue
        
        if sort_date <= as_of_date:
            print(f"unit: {unit['unit']}, floorplan: {unit['floorplan']}, rent: {unit['rent']}")
            if floorplan not in recent_two:
                recent_two[floorplan] = [unit]
            elif len(recent_two[floorplan]) < 2:
                recent_two[floorplan].append(unit)

        # Assign unit to the appropriate time window
        for window in recent_time_windows.keys():
            start_date = {
                'last_90_days': date_90_days_ago,
                'last_60_days': date_60_days_ago,
                'last_30_days': date_30_days_ago
            }[window]

            if start_date <= sort_date <= as_of_date:
                print(f"unit: {unit['unit']}, move in date: {sort_date}, start date: {start_date}")
                if floorplan not in recent_time_windows[window]:
                    recent_time_windows[window][floorplan] = [unit]
                else:
                    recent_time_windows[window][floorplan].append(unit)

    # Now calculate the counts per floorplan
    recent_lease_counts = {floorplan: {} for floorplan in recent_two}

    for floorplan in recent_two:
        recent_lease_counts[floorplan]['recent_two'] = len(recent_two[floorplan])
        for window in recent_time_windows:
            recent_lease_counts[floorplan][window] = len(recent_time_windows[window].get(floorplan, []))

    # Print the lease counts per floorplan
    for floorplan, counts in recent_lease_counts.items():
        print(f"Floorplan: {floorplan}")
        for category, count in counts.items():
            print(f"  {category}: {count}")


    return recent_lease_counts
