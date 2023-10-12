from datetime import datetime, timedelta

def expiring_leases(unit_data, as_of_date):
    print("data as of", as_of_date)
    start = datetime.strptime(as_of_date, "%m/%d/%Y")
    ninety_days_from_start = start + timedelta(days=90)
    expiring_leases_count = 0
    for unit in unit_data:
        if unit['leaseExpire']:
            try:
                lease_expire_date = datetime.strptime(unit['leaseExpire'], "%m/%d/%Y")
                print("start date", start)
                print("lease expire date", lease_expire_date)
                print("90 day window close date", ninety_days_from_start)
                if lease_expire_date >= start and lease_expire_date <= ninety_days_from_start:
                    expiring_leases_count += 1
            except ValueError:
                # The date format is not valid or is empty
                print(f"Invalid date format for unit: {unit}")
    print("expiring leases", expiring_leases_count)
    return expiring_leases_count
