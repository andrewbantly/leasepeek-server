def vacancy(unit_data):
    
    # Initialize tenant status report that will be used if unit data includes a tenant status
    tenant_status_report = {}
    
    # If unit data doesn't include tenant status, we are going to count how many times 'vacant' appears in the tenant column
    vacants = 0
    total_units = len(unit_data)

    for unit in unit_data:
        if unit['status']:
            if unit['status'] in tenant_status_report:
                tenant_status_report[unit['status']] += 1
            else:
                tenant_status_report[unit['status']] = 1

        else:
            if 'vacant' in unit['tenant'].lower():
                vacants += 1
    
    if tenant_status_report:
        vacancy_data = tenant_status_report
    else: 
        occupied = total_units - vacants
        vacancy_data = {"Vacant": vacants, "Occupied": occupied}

    return vacancy_data