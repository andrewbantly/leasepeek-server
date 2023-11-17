"""
This module is designed to clean and standardize rental property unit data extracted from variously formatted data sources, specifically a list of  dictionaries originating from Excel (.xlsx) spreadsheets.

It contains predefined keywords related to real estate units, charge codes, and various data descriptors, utilizing these to identify, categorize, and clean specific data points from the input data structure.

The main function in this module interprets individual data entries, recognizing the associated category of each piece of information, and cleanses this data into a consistent and structured format.

Functions:
    classify_key(key: str) -> str: Categorizes a single piece of data based on predefined keywords.
    clean_unit_data(data_array: list) -> list: Processes an array of dictionaries, each representing a unit's raw data, and standardizes and cleans this data into a uniform structure.

Variables:
    unit_keywords, address_keywords, floorplan_keywords, ... , charge_codes, negative_charge_codes: Sets of keywords and codes used for data categorization and identification during the cleaning process.
"""
from datetime import datetime

# Sets of keyword groupings used to classify data from an input source. Each list contains variations or possible headings found in the dataset that represent the same type of information
unit_keywords = {'Unit', 'Bldg/Unit', 'Unit Number'}
address_keywords = {'Address Line 1'}
floorplan_keywords = {'Unit Type', 'Floorplan', 'Unit  Type', 'Type'}
sqft_keywords = {'sq ft', 'sqft', 'SQFT', 'Unit Sq Ft', 'Sq Ft', 'Unit Sqft'}
market_keywords = {'Market', 'Market Rent', 'Market + Addl.'}
rent_keywords = {'Rent', 'rnt', 'rent', 'Lease Rent', 'RENT-Rent'}
status_keywords = {'Status', 'Unit/Lease Status', 'Unit Status'}
tenant_keywords = {'Name', 'Tenant'}
lease_keywords = {'Lease Dates'}
resident_id_keywords = {'Resident', 'Lease ID', 'Resh ID'}
move_in_keywords = {'Move In', 'Move-In', 'Move IN Date'}
move_out_keywords = {'Move Out', 'Move-Out'}
lease_start_keywords = {'Lease From', 'Lease Start'}
lease_expire_keywords = {'Lease Expiration', 'Lease To', 'Lease End', 'Lease Expiration Date'}
resident_deposit_keywords = {'Resident Deposit', 'Deposit', 'Dep On Hand'}
other_deposit_keywords = {'Other Deposit'}
balance_keywords = {'Balance', 'Resident Balance', 'Past Due'}
total_keywords = {'Total', 'Total Billing'}
NSF_keywords = {'NSF Count'}

# Sets of charge codes, including those that are specifically for negative values
charge_codes = {'rub', 'valtsh', 'cmf', 'package', 'pst', 'prk', 'covpark', 'bbpest', 'conciere', 'bbtr', 'zero', 'ptr', 'CNSVCpst', 'mtm', 'rubsew', 'emp', 'petf', 'conc-prk', 'insur', 'stor', 'svcanml', 'conc-lmp', 'conc-sto', 'Utility', 'Utility Recapture', 'TECH', 'PETF', 'CONC', 'STOR', 'EMPL', 'MODL', 'OFCR', 'LTOR-Loss To Lease In Force', 'STOR-Storage Space #', 'CABL-Cable Television Charges', 'INTR-Internet Access', 'PARK-Parking', 'MTOM-Month To Month Charges', 'RLL-PDLW', 'LTOL-Loss To Lease In Force', 'GAR-Garage Rental', 'RLLG-PDLW LEGACY', 'PETR-Pet Rent', 'W/D Washer/Dryer Rental Charges', 'VAC -Vacancy Loss', 'GTOL-Gain To Lease In Force', 'GTOR-Gain To Lease In Force', 'W/D-Washer/Dryer Rental Charges', 'PETF-Pet Fees Or Charges', 'GAR-Garage Rental #', 'MODE-Model', 'park', 'mtmf', 'conc-rec'}
negative_charge_codes = {'MODE-Model', 'LTOL-Loss To Lease In Force', 'VAC -Vacancy Loss'}
vacancy_loss_charge_codes = {'VAC -Vacancy Loss'}
model_loss_charge_codes = {'MODE-Model'}

def classify_key(key):
    """
    Classify a given key into predefined categories based on the keyword groupings.
    
    Args:
    key (str): The key from the input data to classify.

    Returns:
    str: A string that represents the category into which the key is classified. If the key does not match any predefined category, it is classified as 'unclassified'.
    """

    # Check if the key matches any of the 'Unit' keywords.
    if any(keyword == key for keyword in unit_keywords):
        return 'unit'

    # Check if the key matches any of the 'Lease Dates' keywords.
    if any(keyword == key for keyword in lease_keywords):
        return 'leaseDates'

    # Check if the key matches any of the 'Address' keywords.
    if any(keyword == key for keyword in address_keywords):
        return 'address'

    # Check if the key matches any of the 'Floor Plan Type' keywords.
    elif any(keyword == key for keyword in floorplan_keywords):
        return 'floorplan'
    
    # Check if the key matches any of the 'Unit Sq Ft' keywords.
    elif any(keyword == key for keyword in sqft_keywords):
        return 'sqft'
    
    # Check if the key matches any of the 'Market Value' keywords.
    elif any(keyword == key for keyword in market_keywords):
        return 'market'
    
    # Check if the key matches any of the 'Rent Charge' keywords.
    elif any(keyword == key for keyword in rent_keywords):
        return 'rent'
    
    # Check if the key matches any of the 'Unit Status' keywords.
    elif any(keyword == key for keyword in status_keywords):
        return 'status'
    
    # Check if the key matches any of the 'Tenant Name' keywords.
    elif any(keyword == key for keyword in tenant_keywords):
        return 'tenant'
    
    # Check if the key matches any of the 'Tenant ID' keywords.
    elif any(keyword == key for keyword in resident_id_keywords):
        return 'residentId'
    
    # Check if the key matches any of the 'Move In Date' keywords.
    elif any(keyword == key for keyword in move_in_keywords):
        return 'moveIn'
    
    # Check if the key matches any of the 'Move Out Date' keywords.
    elif any(keyword == key for keyword in move_out_keywords):
        return 'moveOut'
    
    # Check if the key matches any of the 'Lease Start Date' keywords.
    elif any(keyword == key for keyword in lease_start_keywords):
        return 'leaseStart'
    
    # Check if the key matches any of the 'Lease Expire Date' keywords.
    elif any(keyword == key for keyword in lease_expire_keywords):
        return 'leaseExpire'
    
    # Check if the key matches any of the 'Resident Deposit' keywords.
    elif any(keyword == key for keyword in resident_deposit_keywords):
        return 'residentDeposit'
    
    # Check if the key matches any of the 'Other Deposit' keywords.
    elif any(keyword == key for keyword in other_deposit_keywords):
        return 'otherDeposit'
    
    # Check if the key matches any of the 'Outstanding Balance' keywords.
    elif any(keyword == key for keyword in balance_keywords):
        return 'balance'
    
    # Check if the key matches any of the 'Total Value of Combined Charges' keywords.
    elif any(keyword == key for keyword in total_keywords):
        return 'total'
    
    # Check if the key matches any of the 'Charges (excl. rent)' keywords.
    elif any(keyword == key for keyword in charge_codes):
        return 'charges'
    
    # Check if the key matches any of the 'NSF' keywords.
    elif any(keyword == key for keyword in NSF_keywords):
        return 'nsf'
    
    # If the key doesn't match any category, classify as 'unclassified'.
    else:
        return 'unclassified'


def clean_unit_data(data_array):
    """
    Clean and structure raw data into a more uniform format.

    This function takes an array of dictionaries (representing rental property units) and cleans/converts relevant information into a standardized format. Irrelevant or unclassified data is preserved in the 'unclassified' field of the resulting dictionaries.

    Args:
    data_array (list): A list of dictionaries where each dictionary represents a unit and contains various information about it.

    Returns:
    list: A list of cleaned dictionaries with a uniform structure, ready for analysis.
    """
    # Initialize an empty list to hold the cleaned data.
    cleaned_data = []


    for entry in data_array:

        # Initialize a dictionary with the structure we want each unit of data to have after cleaning.
        cleaned_entry = {
            'unit': None,
            'address': None,
            'floorplan': None,
            'sqft': 0,
            'market': 0,
            'rent': 0,
            'status': None,
            'tenant': None,
            'residentId': None,
            'moveIn': None,
            'moveOut': None,
            'leaseStart': None,
            'leaseExpire': None,
            'residentDeposit': 0,
            'otherDeposit': 0,
            'balance': 0,
            'total': 0,
            'nsf': None,
            'charges': [],
            'unclassified': {}
        }

        # Iterate through each key-value pair in the current unit's dictionary.
        for key, value in entry.items():
            # Determine the category of the current key using the classify_key function.
            category = classify_key(key)

            # If the key belongs to certain predefined categories, assign the value to the corresponding field in the cleaned_entry.
            if category in {'unit', 'address', 'floorplan', 'tenant', 'residentId', 'status', 'moveIn', 'moveOut', 'leaseStart','leaseExpire','nsf'}:
                cleaned_entry[category] = value

            # If the key belongs to categories related to monetary values, perform additional cleaning and conversion.
            elif category in ['rent', 'total', 'market', 'balance', 'residentDeposit', 'otherDeposit', 'sqft']:
                # If the value is a string, clean it by removing certain characters and whitespace, then attempt to convert it to an integer.
                if isinstance(value, str):
                    value = value.replace('*', '').replace(',', '').strip()
                    try:
                        value = int(round(float(value)))
                    except ValueError:
                        # If conversion fails, log an error and keep the original raw value.
                        print(f"Error converting '{value}' to integer for key '{key}'. Using raw value.")
                # Assign the cleaned/conversion_attempted value to the corresponding field in the cleaned_entry.
                if value == '':
                    cleaned_entry[category] = 0
                else:
                    cleaned_entry[category] = value

            # Process entries categorized as 'charges'.
            elif category == 'charges':
                # Check if the value associated with the charge is a string.
                if isinstance(value, str):
                    # Remove any '*' or ',' characters and strip whitespace, as these can interfere with numerical conversion.
                    value = value.replace('*', '').replace(',', '').strip()
                    # Attempt to convert the cleaned string to a float, then to an integer (after rounding), as charge data is expected to be numerical.
                    try:
                        value = int(round(float(value)))
                    except ValueError:
                        # If the conversion fails (e.g., if the string contains non-numeric characters), log an error message and retain the original string value.
                        print(f"Error converting '{value}' to integer for key '{key}'. Using raw value.")
                # Check if the current key is in the list of codes representing negative charges.
                if key in negative_charge_codes:
                    # Ensure the value is stored as a negative number.
                    value = -abs(value)
                # Append a new dictionary to the 'charges' list in the cleaned_entry. 
                cleaned_entry['charges'].append({'code': key, 'value': value})

            
            # If the key indicates lease dates (two dates in a single string) and the value has a specific length (21 = MM/DD/YYYY + ' ' + MM/DD/YYYY), split the value into separate 'leaseStart' and 'leaseExpire' dates.
            elif category == 'leaseDates':
                if len(value) == 21:
                    # Split the value into start and end dates.
                    start, end = value.split()
                    cleaned_entry['leaseStart'] = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
                    cleaned_entry['leaseExpire'] = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

            # If the key's category is not recognized, add it to the 'unclassified' field in the cleaned_entry.
            else:
                cleaned_entry['unclassified'][key] = value

        for charge in cleaned_entry.get('charges', []):
            if charge['code'] in vacancy_loss_charge_codes:
                # Subtract the charge value from the rent
                cleaned_entry['rent'] += charge['value']
            elif charge['code'] in model_loss_charge_codes:
                cleaned_entry['rent'] += charge['value']

        # Add the cleaned_entry dictionary to the cleaned_data list.
        cleaned_data.append(cleaned_entry)

    # Return the list of cleaned data.
    return cleaned_data
