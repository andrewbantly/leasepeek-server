from datetime import datetime, timedelta
import calendar

keywords = {'Former applicant', 'Future Residents/Applicants'}

def analyze_lease_trends(unit_data, as_of_date_str):

    # Convert the as of date into a date object
    as_of_date = datetime.strptime(as_of_date_str, '%m/%d/%Y')

    # Initialize the last twelve months
    months = []

    for i in range(12):
        month = as_of_date.month - i
        year = as_of_date.year
        if month <= 0:
            month += 12
            year -= 1
        # Create datetime object to add to months list
        month_date = datetime(year, month, 1)
        months.append(month_date)
    
    # Reverse the list to start with the earliest month
    months.reverse()

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

    # Initialize a dictionary to hold data for each month
    monthly_data = {month.strftime("%Y-%m"): {} for month in months}

    # Initialize each floor plan for each month
    for unit in unit_data:
        floorplan = unit['floorplan']
        for month in monthly_data:
            if floorplan not in monthly_data[month]:
                monthly_data[month][floorplan] = []

    # Add SqFt and Rent to each month
    for unit in unit_data:
        if unit['status'] in keywords:
            continue
        sort_date = parse_date(unit['moveIn'] or unit['leaseStart'])
        sqft = unit['sqft']
        rent = unit['rent']
        floorplan = unit['floorplan']
        if sort_date:
            for month in months:
                if sort_date.year == month.year and sort_date.month == month.month:
                    month_key = month.strftime("%Y-%m")
                    monthly_data[month_key][floorplan].append({
                        'sqft': sqft,
                        'rent': rent,
                    })
        
    # Calculate Number of Leases and Avg Lease per Sqft for each month
    results = {}
    for month in monthly_data:
        results[month] = {}
        for floorplan in monthly_data[month]:
            leases = monthly_data[month][floorplan]
            total_rent = sum(lease['rent'] for lease in leases)
            total_sqft = sum(lease['sqft'] for lease in leases)

            avg_lease_per_sqft = round(total_rent / total_sqft, 2) if total_sqft else 0
            
            lease_count = len(leases)

            results[month][floorplan] = {
                "NumOfLeases": lease_count,
                "AvgLeasePerSqFt": avg_lease_per_sqft
            }
        
    return results