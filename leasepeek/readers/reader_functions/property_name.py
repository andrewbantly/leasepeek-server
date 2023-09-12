keywords = ['Building', 'Property', 'Village', 'Apartment', 'District', 'North', 'East', 'West', 'South', 'Shadows', 'Place', 'Street', 'Aveneue', 'Circle', 'Court', 'Place']

def find_property_name(df):
    property_name = ''
    for i, row in df.head(10).iterrows():
        row_str = ' '.join(row.dropna().astype(str))
        if any(keyword in row_str for keyword in keywords):
            property_name = row_str
            break
    print("Property:", property_name)
    return property_name