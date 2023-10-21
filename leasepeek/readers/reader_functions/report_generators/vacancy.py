
vague_keywords =  {"Current/Notice/Vacant Residents",  "Future Residents/Applicants"}


def vacancy(unit_data):
    
    # Initialize tenant status report that will be used if unit data includes a tenant status
    tenant_status_report = {}
    
    # If unit data doesn't include tenant status, we are going to count how many times 'vacant' appears in the tenant column
    vacants = 0
    total_units = len(unit_data)

    for unit in unit_data:
        if unit['status'] in vague_keywords:
            if unit['status'] ==  "Future Residents/Applicants":
                if 'Applicant' in tenant_status_report:
                    tenant_status_report['Applicant'] += 1
                else:
                    tenant_status_report['Applicant'] = 1
            else:
                if 'vacant' in unit['tenant'].lower():
                    print('add to vacant')
                    if 'Vacant' in tenant_status_report:
                        tenant_status_report['Vacant'] += 1
                    else:
                        tenant_status_report['Vacant'] = 1
                elif unit['moveOut']:
                    print('add to notice')
                    if 'Notice' in tenant_status_report:
                        tenant_status_report['Notice'] += 1
                    else:
                        tenant_status_report['Notice'] = 1
                else:
                    print('add to current')
                    if 'Current' in tenant_status_report:
                        tenant_status_report['Current'] += 1
                    else:
                        tenant_status_report['Current'] = 1

        elif unit['status']: 
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