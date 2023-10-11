from leasepeek.readers.reader_functions.property_name import find_property_name
from leasepeek.readers.reader_functions.as_of_date import find_as_of_date
from leasepeek.readers.reader_functions.unit_data_types import find_unit_data_types
from leasepeek.readers.reader_functions.process_unit_data import process_unit_data
from leasepeek.readers.reader_functions.clean_unit_data import clean_unit_data
from leasepeek.readers.reader_functions.report_generators.vacancy import vacancy
from leasepeek.readers.reader_functions.report_generators.floorplan_survey import floorplan_survey
from datetime import datetime, timezone

def read_xlsx(data_frame, user_id, file_name):
    # Find the name of the property
    property = find_property_name(data_frame)

    # Find the 'as of' date
    as_of_date = find_as_of_date(data_frame, file_name)

    # Find the different types of data
    unit_data_types = find_unit_data_types(data_frame)

    # Process the unit data
    processed_unit_data = process_unit_data(data_frame, unit_data_types)

    # Clean the unit data
    cleaned_unit_data = clean_unit_data(processed_unit_data)

    # Vacancy report
    vacancy_data = vacancy(cleaned_unit_data)

    # Average Market Value per Floorplan report
    surveyed_floorplans = floorplan_survey(cleaned_unit_data)

    unit_data = {'user_id': user_id,
                 'date': datetime.now(timezone.utc).isoformat(),
                 'location': property,
                 'asOf': as_of_date,
                 'vacancy': vacancy_data,
                 'floorplans': surveyed_floorplans,
                #  'data': cleaned_unit_data
                 }          
    

    return unit_data