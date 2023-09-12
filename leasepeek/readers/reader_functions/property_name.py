keywords = ['Building', 'Property', 'Village', 'Apartment', 'District', 'North', 'East', 'West', 'South', 'Shadows', 'Place', 'Street', 'Aveneue', 'Circle', 'Court', 'Place']

def find_property_name(df):
    property_name = ''
    for i, row in df.iterrows():
        row_str = ' '.join(row.dropna().astype(str))
        # Check if any keyword exists in row_str
        if any(keyword in row_str for keyword in keywords):
            # Here, instead of assigning the keyword to building_name, 
            # we want to assign the entire row string as it's the building's name.
            property_name = row_str
            break
    print("Property:", property_name)
    return property_name