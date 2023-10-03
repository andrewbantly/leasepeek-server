from leasepeek.readers.reader_functions.property_name import find_property_name
from leasepeek.readers.reader_functions.as_of_date import find_as_of_date
from leasepeek.readers.reader_functions.unit_data_types import find_unit_data_types
from leasepeek.readers.reader_functions.process_unit_data import process_unit_data

def read_xlsx(data_frame, user_id):
    # Find the name of the property
    property = find_property_name(data_frame)

    # Find the 'as of' date
    as_of_date = find_as_of_date(data_frame)

    # Find the different types of data
    unit_data_types = find_unit_data_types(data_frame)

    # Process the unit data
    processed_unit_data = process_unit_data(data_frame, unit_data_types)

    unit_data = {'user_id': user_id,
                 'location': property,
                 'date': as_of_date,
                 'data': processed_unit_data
                 }
    print(unit_data)
    return unit_data