from datetime import datetime, timedelta


# TO DO
# If no date is found, the recent two should still be calculated. 
# Ensure the test data is working properly as it seems most of the test data isn't within the 90 days, etc window of the as of date. 



def recent_leases(unit_data, as_of_date_str):
    print('recent leases')

    if as_of_date_str == 'Date not found':
        print("DATE NOT FOUND")
        return

    as_of_date = datetime.strptime(as_of_date_str, '%m/%d/%Y')

    date_90_days_ago = as_of_date - timedelta(days=90)
    date_60_days_ago = as_of_date - timedelta(days=60)
    date_30_days_ago = as_of_date - timedelta(days=30)

    recent_two = {}
    recent_time_windows = {
        'last_90_days': {},
        'last_60_days': {},
        'last_30_days': {}
    }

    def parse_date(date_str):
        if isinstance(date_str, str) and date_str.strip():
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
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

    # Return the recent_two and counts
    return recent_two, recent_lease_counts
