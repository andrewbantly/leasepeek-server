
def find_property_name(df):
    print("Searching for property name")
    keywords = ['Building', 'Property', 'Village', 'Apartment', 'District', 'North', 'East', 'West', 'South', 'Shadows', 'Place', 'Street', 'Aveneue', 'Circle', 'Court']
    building_name = ''
    for i, row in df.iterrows():
        row_str = ' '.join(row.dropna().astype(str))
        # Check if any keyword exists in row_str
        if any(keyword in row_str for keyword in keywords):
            # Here, instead of assigning the keyword to building_name, 
            # we want to assign the entire row string as it's the building's name.
            building_name = row_str
            print("Property name found")
            break
    return building_name



def read_xlsx(data_frame):
    df = data_frame
    print("new xlsx reader triggered")
    # All uploads feature basic to detailed background information on the rental property before going into the unit data
    # So before we start looking for unit information, let's gather the background information
    property = find_property_name(df)
