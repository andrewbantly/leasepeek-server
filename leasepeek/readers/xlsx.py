"""
Module Description:
This module is responsible for processing Excel data related to real estate properties. It leverages a series of helper functions
to extract, clean, and structure the data from a given Excel sheet. This processed data is then returned in a structured 
format that includes various property-related metrics.

Imported functions:
- find_property_name: Extracts the property name from the Excel data.
- find_as_of_date: Determines the 'as of' date from the Excel data or filename.
- find_unit_data_types: Identifies the different types of unit data in the Excel sheet.
- process_unit_data: Processes raw unit data into a structured format.
- clean_unit_data: Cleans and normalizes the processed unit data.
- vacancy: Computes the vacancy data based on the cleaned unit data.
- floorplan_survey: Generates a survey of floorplans based on the cleaned unit data.

Functions:
- read_xlsx: Main function that orchestrates the reading and processing of the Excel data.

"""
from leasepeek.readers.reader_functions.property_name import find_property_name
from leasepeek.readers.reader_functions.as_of_date import find_as_of_date
from leasepeek.readers.reader_functions.unit_data_types import find_unit_data_types
from leasepeek.readers.reader_functions.process_unit_data import process_unit_data
from leasepeek.readers.reader_functions.clean_unit_data import clean_unit_data
from leasepeek.readers.reader_functions.vacancy import vacancy
from leasepeek.readers.reader_functions.total_units import find_total_units
from leasepeek.readers.reader_functions.floorplan_survey import floorplan_survey
from leasepeek.readers.reader_functions.loss_to_lease import find_loss_to_lease
from leasepeek.readers.reader_functions.charges import charge_codes
from leasepeek.readers.reader_functions.expiring_leases import expiring_leases
from leasepeek.readers.reader_functions.recent_leases import recent_leases
from leasepeek.readers.reader_functions.lease_trends import analyze_lease_trends
from leasepeek.readers.reader_functions.outstandingBalance import calculate_outstanding_balance
from leasepeek.readers.reader_functions.filter_personal_information import filter_personal_info
from datetime import datetime, timezone

def read_xlsx(data_frame, user_id, file_name):
    """
    Processes the given Excel data frame to extract, clean, and structure property-related data.

    Parameters:
    - data_frame (DataFrame): The raw Excel data.
    - user_id (str): The ID of the user uploading/processing the data.
    - file_name (str): The name of the uploaded Excel file.

    Returns:
    - dict: A structured dictionary containing various metrics and data related to the property.
    """

    # Identify the different types of unit data present in the Excel sheet
    unit_data_types = find_unit_data_types(data_frame)

    # Determine the row that separates background information from unit-specific data
    title_row = unit_data_types['Title Row']
    
    # Extract the name of the property from the Excel data
    property = find_property_name(data_frame, title_row)

    # Determine the 'as of' date either from the data or the file name
    as_of_date = find_as_of_date(data_frame, title_row, file_name)

    # Process and structure the raw unit data from the Excel sheet
    processed_unit_data = process_unit_data(data_frame, unit_data_types)

    # Clean and normalize the processed unit data
    cleaned_unit_data = clean_unit_data(processed_unit_data)

    # Calculate the total number of units from the cleaned data
    total_units = find_total_units(cleaned_unit_data)    

    # Calculate the total outstanding balance from the cleaned data
    outstanding_balance = calculate_outstanding_balance(cleaned_unit_data)

    # Calculate vacancy metrics based on the cleaned unit data
    vacancy_data = vacancy(cleaned_unit_data)

    # Survey the floorplans from the cleaned unit data
    surveyed_floorplans = floorplan_survey(cleaned_unit_data)

    # Calculate loss to lease using the cleaned unit data
    loss_to_lease = find_loss_to_lease(cleaned_unit_data)

    # Charge codes
    charges = charge_codes(cleaned_unit_data, loss_to_lease)

    # Recent lease signing analysis
    recent_leases_analysis = recent_leases(cleaned_unit_data, as_of_date)

    # Expiring leases
    expired_leases = expiring_leases(cleaned_unit_data, as_of_date)

    # Analyze Lease trends of last 12 months
    lease_trends = analyze_lease_trends(cleaned_unit_data, as_of_date)

    # Filter personal out personal data
    filtered_clean_data = filter_personal_info(cleaned_unit_data)

    # Construct the final structured data 
    property_data = {'user_id': user_id,
                 'date': datetime.now(timezone.utc).isoformat(),
                 'location': property,
                 'asOf': as_of_date,
                 'totalUnits': total_units,
                 'unitsConfirmed': False,
                 'totalBalance': outstanding_balance,
                 'floorplans': surveyed_floorplans,
                 'vacancy': vacancy_data,
                 'lossToLease': loss_to_lease,
                 'charges': charges,
                 'recentLeases': recent_leases_analysis,
                 'expiringLeases': expired_leases,
                 'leaseTrends': lease_trends,
                 'data': filtered_clean_data,
                 }          

    return property_data