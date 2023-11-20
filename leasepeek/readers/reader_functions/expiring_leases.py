from datetime import datetime, timedelta

def expiring_leases(unit_data, as_of_date_str):
    start = datetime.strptime(as_of_date_str, "%m/%d/%Y")
    ninety_days_from_start = start + timedelta(days=90)
    expiring_leases_count = 0
    # print("Leases are expiring if before:", ninety_days_from_start)
    # print()
    
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

    for unit in unit_data:
        if unit['leaseExpire']:
            try:
                expire_str = unit['leaseExpire'].replace('.', '/').replace('_', '/').replace('-', '/')
                date_format = determine_date_format(expire_str)
                lease_expire_date = datetime.strptime(expire_str, date_format)
                if lease_expire_date >= start and lease_expire_date <= ninety_days_from_start:
                    expiring_leases_count += 1
            except ValueError:
                # The date format is not valid or is empty
                print(f"Can not determine lease expire of unit. Invalid date format for unit: {unit}")
    print("expiring leases", expiring_leases_count)


    return expiring_leases_count