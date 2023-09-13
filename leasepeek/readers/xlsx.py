from leasepeek.readers.reader_functions.property_name import find_property_name
from leasepeek.readers.reader_functions.as_of_date import find_as_of_date
from leasepeek.readers.reader_functions.unit_data_types import find_unit_data_types
from leasepeek.readers.reader_functions.process_unit_data import process_unit_data

def read_xlsx(data_frame):
    df = data_frame
    # All uploads feature basic to detailed background information on the rental property before going into the unit data
    # So before we start looking for unit information, let's gather the background information
    property = find_property_name(df)
    as_of_date = find_as_of_date(df)
    unit_data_types = find_unit_data_types(df)
    processed_data = process_unit_data(df, unit_data_types)
