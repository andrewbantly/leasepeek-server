from datetime import datetime, timedelta

keywords = {'Former applicant', 'Future Residents/Applicants', 'Applicant'}

def recent_leases(unit_data, as_of_date_str):
    if as_of_date_str == 'Date not found':
        as_of_date = datetime.today()
    else:
        as_of_date = datetime.strptime(as_of_date_str, '%m/%d/%Y')

    date_90_days_ago = as_of_date - timedelta(days=90)
    # print(f"90 days ago is: {date_90_days_ago}")
    date_60_days_ago = as_of_date - timedelta(days=60)
    # print(f"60 days ago is: {date_60_days_ago}")
    date_30_days_ago = as_of_date - timedelta(days=30)
    # print(f"30 days ago is: {date_30_days_ago}")

    recent_two = {}
    recent_time_windows = {
        'last_90_days': {},
        'last_60_days': {},
        'last_30_days': {}
    }

    floorplan_data = {}

    # Initialize floorplan data for all floorplans in unit_data
    for unit in unit_data:
        floorplan = unit['floorplan']
        if floorplan not in floorplan_data:
            floorplan_data[floorplan] = {
                'recent_two': {
                    'count': 0,
                    'total_rent': 0,
                    'average_rent': 0
                },
                'recent_leases': {
                    'last_90_days': {'count': 0, 'total_rent': 0, 'average_rent': 0},
                    'last_60_days': {'count': 0, 'total_rent': 0, 'average_rent': 0},
                    'last_30_days': {'count': 0, 'total_rent': 0, 'average_rent': 0}
                }
            }

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
                recent_two[floorplan] = {'count': 0, 'total_rent': 0}

            if recent_two[floorplan]['count'] < 2:
                recent_two[floorplan]['count'] += 1
                recent_two[floorplan]['total_rent'] += unit.get('rent', 0)

            for window in recent_time_windows.keys():
                start_date = {
                    'last_90_days': date_90_days_ago,
                    'last_60_days': date_60_days_ago,
                    'last_30_days': date_30_days_ago
                }[window]

                if start_date <= sort_date <= as_of_date:
                    if floorplan not in recent_time_windows[window]:
                        recent_time_windows[window][floorplan] = []

                    window_data = recent_time_windows[window][floorplan]
                    window_data.append(unit)

    # Calculate average rent for recent_two and each time window
    for floorplan in floorplan_data:
        # Calculate average rent for recent_two
        recent_two_data = recent_two.get(floorplan, {'count': 0, 'total_rent': 0})
        count_recent_two = recent_two_data['count']
        total_rent_recent_two = recent_two_data['total_rent']
        average_rent_recent_two = total_rent_recent_two / count_recent_two if count_recent_two > 0 else 0
        floorplan_data[floorplan]['recent_two'] = {
            'count': count_recent_two,
            'total_rent': total_rent_recent_two,
            'average_rent': average_rent_recent_two
        }

        # Calculate averages for each time window
        for window in recent_time_windows:
            lease_count = len(recent_time_windows[window].get(floorplan, []))
            total_rent = sum(unit.get('rent', 0) for unit in recent_time_windows[window].get(floorplan, []))
            average_rent = round(total_rent / lease_count, 2) if lease_count > 0 else 0
            floorplan_data[floorplan]['recent_leases'][window] = {
                'count': lease_count,
                'total_rent': total_rent,
                'average_rent': average_rent
            }
            
    return floorplan_data