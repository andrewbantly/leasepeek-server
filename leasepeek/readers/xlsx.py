from leasepeek.readers.reader_functions.property_name import find_property_name


def read_xlsx(data_frame):
    df = data_frame
    # All uploads feature basic to detailed background information on the rental property before going into the unit data
    # So before we start looking for unit information, let's gather the background information
    property = find_property_name(df)

