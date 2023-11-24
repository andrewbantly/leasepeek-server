# Set of keywords used to identify units with non-explicit statuses that require further classification.
combined_vacancy_keywords =  {"Current/Notice/Vacant Residents",  "Future Residents/Applicants"}
occupied_keywords = {'Occupied', 'occupied', 'Occupied-NTV', 'Occupied-NTVL', 'O', 'NR', 'NU'}
vacant_keywords = {'Vacant', 'vacant', 'Vacant-Leased', 'VU', 'VR'}
down_unit_keywords = {'down'}
model_unit_keywords = {'model'}
ignore_keywords = {'Former resident', 'Former applicant'}

def determine_unit_status(unit_data):

    # Handle units with combined statuses that require further classification.
    if unit_data['status'] in combined_vacancy_keywords:
        # If the status indicates future residents or applicants, increment the 'Applicant' count.
        if unit_data['status'] ==  "Future Residents/Applicants":
                return 'Applicant'
        else:
            # If the tenant field contains 'vacant', increment the 'Vacant' count.
            if 'vacant' in unit_data['tenant'].lower():
                return 'Vacant'
            # If there's a model unit, increment the 'Model' count.
            elif unit_data['tenant'].lower() in model_unit_keywords:
                return 'Model'
            # If there's a down unit, increment the 'Down' count.
            elif unit_data['tenant'].lower() in down_unit_keywords:
                return 'Down'
            # If none of the above, the unit is considered 'Occupied'.
            else:
                return 'Occupied'
    
    # Handle units with explicit statuses.
    elif unit_data['status']:
        if unit_data['status'] in occupied_keywords:
        # Increment the count for the unit's status.
            return 'Occupied'
        elif unit_data['status'] in vacant_keywords:
            return 'Vacant'
        elif unit_data['status'] in model_unit_keywords:
            return 'Model'
            # If there's a down unit, increment the 'Down' count.
        elif unit_data['status'] in down_unit_keywords:
            return 'Down'
        else:
            return unit_data['status']
                
    # For units without a status, check if 'vacant' is mentioned in the 'tenant' field.
    else:
        if 'vacant' in unit_data['tenant'].lower():
            return 'Vacant'
        # If there's a model unit, increment the 'Model' count.
        elif unit_data['tenant'].lower() in model_unit_keywords:
            return 'Model'
        # If there's a down unit, increment the 'Down' count.
        elif unit_data['tenant'].lower() in down_unit_keywords:
            return 'Down'
        # If none of the above, the unit is considered 'Occupied'.
        else:
            return 'Occupied'
                 

    return None