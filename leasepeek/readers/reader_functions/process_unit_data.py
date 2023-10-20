"""
This module is designed to process unit data from a DataFrame, originating from an Excel (.xlsx) spreadsheet.

It contains predefined keywords, charge types, and unit describers, and uses these to identify, categorize, and extract specific data from the input DataFrame.

The main function in this module looks for certain indicators in the data to recognize the start and end of relevant sections, then extracts this data into a structured format.

Functions:
    process_unit_data(df, data_types): Extracts unit data from the provided DataFrame based on the specified data types.

Variables:
    keywords: Keywords indicating the end of the data section in the DataFrame.
    charge_types: Keywords identifying the types of charges in the data.
    unit_describers: Keywords identifying unit descriptors in the data.
"""
import datetime

# Set of keywords used to identify the end of the data section in the DataFrame
data_end_keywords = {'Total', 'Totals', 'Totals:', 'Total Market Rent', 'Applications', 'Summary Groups'}

# Set of keywords representing various types of charges in the data. These charges can include rent but typically are more granular, encompassing specific fees such as those for garage, pet, or laundry.
charge_types = {'Charge Code', 'Amount', 'Rent Charge Description', 'Rent Charge Amount', 'Description', 'Charge Amount', 'Credit Amount'}

# Set of keywords used for describing unit information in the data
unit_describers = {'Bldg/Unit', "Unit", "Unit Number"}

def process_unit_data(df, data_types):
    """ 
    Processes and extracts unit data from the input DataFrame.

    The function first identifies the start and end of the data section based on the "Title Row" and specific `data_end_keywords`, then categorizes each data entry according to predefined `data_types` and structures the data into a more usable format. It also handles a special case where unit statuses (e.g., "Current/Notice/Vacant Residents," "Future Residents/Applicants") are used as row separators within the data rather than standard column headers, identifying these statuses and including them in the extracted data.

    Parameters:
        df (DataFrame): The input data in a pandas DataFrame format.
        data_types (dict): A dictionary where keys are descriptive names of the data type (including a special "Title Row" key to indicate where the data starts) and values are the corresponding column numbers in the DataFrame. Example: 
            {'Unit': 0, 'Unit Type': 1, 'Unit Sq Ft': 2, 'Resident': 3, 'Name': 4, 'Market Rent': 5, 'Charge Code': 6, 'Amount': 7, 'Resident Deposit': 8, 'Other Deposit': 9, 'Move In': 10, 'Lease Expiration': 11, 'Move Out': 12, 'Balance': 13, 'Title Row': 5}

    Returns:
        list: A list of dictionaries, where each dictionary contains processed data of a single unit, 
              including its status if available.
    """

    # Determine the row where the data starts, based on the "Title Row" entry. Then remove this entry from data_types.
    data_starting_row = data_types["Title Row"] + 1
    data_types.pop("Title Row")

    # Initialize the variable that will hold the row number where the data ends.
    data_ending_row = 0
    # Iterate through each row in the DataFrame to find where the relevant data ends, based on specific `data_end_keywords`.
    for i, row in df.iterrows():
        cell_value = str(row.iloc[0])
        if any(keyword in cell_value for keyword in data_end_keywords):
            data_ending_row = i
            break
    # If no ending row is found, report an error.
    if data_ending_row == 0:
        print("Data read error. No ending row for unit data recognized.")

    # Separate charge codes from other data types in the initial data_types dictionary. This distinction is necessary because charge codes are represented differently and require a different processing approach to accurately extract their information.
    main_data_types = {}
    charge_codes = {}
    for d in data_types:
        if d in charge_types:
            charge_codes[data_types[d]] = d
        else:
            main_data_types[data_types[d]] = d
    
    # Initialize the list that will store the processed data dictionaries.
    data = []

    # Determine whether there are any charges to find based on the presence of charge codes.
    find_charges = bool(charge_codes)

    # Initialize the dictionary that will hold the current unit's data.
    current_unit = {}
    
    # Identify the column number for the unit description, based on predefined `unit_describers`. This column's value will later be checked to determine if it's string value is 'nan' (indicating the end of the current unit's data) or an inputted string value (indicating a new unit to process). If no describer is found in data_types, the script will raise an error to avoid unintended behavior.
    unit_index = None
    for unit in unit_describers:
        if unit in data_types:
            unit_index = data_types[unit]
            break
    if unit_index is None:
        raise ValueError("No valid unit describer found in data types.")

    # Initialize the unit status in the case where unit statuses are used as row separators within the data rather than standard column headers.
    status=''

    # Process each row in the range of the data, extracting relevant information.
    for row_index in range(data_starting_row, data_ending_row):
        # Skip the row if it's a status header or doesn't contain unit data.
        if df.iloc[row_index, 0] == "Current/Notice/Vacant Residents":
            status = "Current/Notice/Vacant Residents"
            continue
        if df.iloc[row_index, 0] == "Future Residents/Applicants":
            status = "Future Residents/Applicants"
            continue

        # If the unit field is not empty, append the current unit (if it exists) and begin to process a new unit at the current row.
        if str(df.iloc[row_index, unit_index]) != 'nan':
            # If there's existing data in the current unit, add it to the list and start a new unit. Add the edge case status if necessary.
            if current_unit:
                if status:
                    current_unit['Status'] = status
                data.append(current_unit)
            
            # Reset current unit dictionary before processing. 
            current_unit = {} 

            # Extract and store each piece of information from the current row into the current_unit dictionary.
            for data_column_index in main_data_types:
                cell_value = df.iloc[row_index, data_column_index]
                # Convert datetime objects to string format.
                if isinstance(cell_value, datetime.datetime):
                    cell_value = cell_value.strftime('%Y-%m-%d')
                # Convert NaN values to an empty string.
                if str(cell_value) == 'nan':
                    cell_value = ''
                data_description = main_data_types[data_column_index]
                current_unit[data_description] = cell_value

        # If there are charges in the row, process them separately and store the description and values in the current unit.
        if find_charges:
            charge_line = ""
            charge_amount = 0
            # Process each potential charge in the row.
            for charge_index in charge_codes:
                # Identify the charge description.
                if type(df.iloc[row_index, charge_index]) == str:
                    charge_line = df.iloc[row_index, charge_index]
                # Identify the charge amount.
                if type(df.iloc[row_index, charge_index]) == int:
                    charge_amount = df.iloc[row_index, charge_index]
                # If both charge description and amount are identified, store them in the current unit.
                if charge_line and charge_amount:
                    current_unit[charge_line] = charge_amount
                    charge_line = ""
                    charge_amount = 0

    # Add the last unit to the data list after finishing the row iteration. Add the `status` edge case if necessary.
    if status:
        current_unit['Status'] = status
    data.append(current_unit) 

    # Return the list of processed data.
    return data