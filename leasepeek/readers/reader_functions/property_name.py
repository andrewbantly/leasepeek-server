keywords = ['Building', 'Property', 'Village', 'Apartment', 'District', 'North', 'East', 'West', 'South', 'Shadows', 'Place', 'Street', 'Aveneue', 'Circle', 'Court', 'Place']

def find_property_name(df, title_row):
    property_name = ''
    for i, row in df.head(title_row).iterrows():
        row_str = ' '.join(row.dropna().astype(str))
        if any(keyword in row_str for keyword in keywords):
            property_name = row_str
            break

    return property_name