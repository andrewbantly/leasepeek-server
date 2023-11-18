"""
Vacancy Analysis Module

This module is designed to analyze a rental property's vacancy. The expected input is a list of dictionaries, each representing a rental unit's data extracted from a pre-processed Excel dataset.

The module identifies vacancy status based on predefined keywords and categorizes units accordingly. It distinguishes between non-explicit statuses by investigating related fields such as 'tenant' and 'moveOut' information. 

Functions:
    vacancy(unit_data): Analyzes and categorizes the vacancy status of units from the provided list.

Variables:
    combined_vacancy_keywords: Set of keywords used to identify units with non-explicit statuses that require further classification.
"""

# Set of keywords used to identify units with non-explicit statuses that require further classification.
combined_vacancy_keywords =  {"Current/Notice/Vacant Residents",  "Future Residents/Applicants"}
occupied_keywords = {'Occupied', 'occupied', 'Occupied-NTV', 'Occupied-NTVL', 'O', 'NR', 'NU'}
vacant_keywords = {'Vacant', 'vacant', 'Vacant-Leased', 'VU', 'VR'}

def vacancy(unit_data):
    """
    Analyze and categorize the vacancy status of units.

    This function processes a list of unit data dictionaries, categorizing each unit's vacancy status based on specific criteria. For units with explicit statuses, it increments the count of their respective status in a report dictionary.
    
    For units with non-explicit statuses, it determines their status based on additional information (e.g., 'tenant', 'moveOut') and updates the report.
    
    If unit data lacks status information, the function counts the number of 'vacant' occurrences in the 'tenant' field.

    Args:
    unit_data (list): A list of dictionaries, each containing data about a rental unit.

    Returns:
    dict: A dictionary summarizing the number of units in each vacancy status category.
    """
    
    # Initialize a dictionary to hold counts of units per vacancy status.
    vacancy_statuses = {}
    
    # Counter for units explicitly marked as 'vacant'.
    vacants = 0
    # Total number of units in the dataset.
    total_units = len(unit_data)

    # Process each unit's data.
    for unit in unit_data:
        # Handle units with combined statuses that require further classification.
        if unit['status'] in combined_vacancy_keywords:
            # If the status indicates future residents or applicants, increment the 'Applicant' count.
            if unit['status'] ==  "Future Residents/Applicants":
                if 'Applicant' in vacancy_statuses:
                    vacancy_statuses['Applicant'] += 1
                else:
                    vacancy_statuses['Applicant'] = 1
            else:
                # If the tenant field contains 'vacant', increment the 'Vacant' count.
                if 'vacant' in unit['tenant'].lower():
                    if 'Vacant' in vacancy_statuses:
                        vacancy_statuses['Vacant'] += 1
                    else:
                        vacancy_statuses['Vacant'] = 1
                # If there's a move-out date, increment the 'Notice' count (indicating upcoming vacancy).
                elif 'model' in unit['tenant'].lower():
                    if 'Model' in vacancy_statuses:
                        vacancy_statuses['Model'] += 1
                    else:
                        vacancy_statuses['Model'] = 1
                # If none of the above, the unit is considered 'Occupied' (occupied with no known upcoming vacancy).
                else:
                    if 'Occupied' in vacancy_statuses:
                        vacancy_statuses['Occupied'] += 1
                    else:
                        vacancy_statuses['Occupied'] = 1
        
        # Handle units with explicit statuses.
        elif unit['status']:
            if unit['status'] in occupied_keywords:
            # Increment the count for the unit's status.
                if 'Occupied' in vacancy_statuses:
                    vacancy_statuses['Occupied'] += 1
                else:
                    vacancy_statuses['Occupied'] = 1
            elif unit['status'] in vacant_keywords:
                if 'Vacant' in vacancy_statuses:
                    vacancy_statuses['Vacant'] += 1
                else:
                    vacancy_statuses['Vacant'] = 1
            else:
                if unit['status'] in vacancy_statuses:
                    vacancy_statuses[unit['status']] += 1
                else:
                    vacancy_statuses[unit['status']] = 1
                    
        # For units without a status, check if 'vacant' is mentioned in the 'tenant' field.
        else:
            if 'vacant' in unit['tenant'].lower():
                vacants += 1

    # Compile the final vacancy report.
    if vacancy_statuses:
        vacancy_data = vacancy_statuses
    else: 
        # If there was no status data, report based on 'vacant' counts.
        occupied = total_units - vacants
        vacancy_data = {"Vacant": vacants, "Occupied": occupied}
    print()
    print("#### Vacancy:")
    print(vacancy_data)
    print()
    return vacancy_data