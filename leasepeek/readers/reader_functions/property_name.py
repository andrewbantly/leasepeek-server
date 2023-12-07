keywords = {'Building', 'Property', 'Village', 'Apartment', 'District', 'North', 'East', 'West', 'South', 'Shadows', 'Place', 'Street', 'Avenue', 'Circle', 'Court', 'Place', 'Park'}

def find_property_name(df, title_row):
    """
    Searches the dataframe above the provided title row for a potential property name based on predefined keywords.
    
    The function checks each row, starting from the first row and going up to (but not including) the title row. 
    It concatenates the cell contents of the row where a keyword match is found, to produce the potential property name.

    Parameters:
    ----------
    df : pandas.DataFrame
        The dataframe to search.
        
    title_row : int
        The index of the title row in the dataframe. Rows above this will be checked for the property name.
    
    Returns:
    -------
    str
        The detected property name. Returns an empty string if no valid property name is found.
    
    Example:
    --------
    >>> df = pd.DataFrame({
    ...    'A': ["Building ABC", "Unit Type", "B101"],
    ...    'B': [np.nan, "Floorplan", "2BHK"],
    ...    'C': ["Property XYZ", "Unit Sq Ft", "1200"]
    ... })
    >>> find_property_name(df, 1)
    'Building ABC Property XYZ'
    """

    # Initialize the property name string
    property_name = ''

    # Iterate through each row up to the title row
    for i, row in df.head(title_row).iterrows():
        # Create a concatenated string of the row, omitting 'nan' values
        row_str = ' '.join(row.dropna().astype(str))
        
        # If the row string contains any of the predefined keywords, set it as the property name and break
        if any(keyword in row_str for keyword in keywords):
            property_name = row_str
            break
    
    location = {
        'market': None,
        'address': {
            'addressLine1': None,
            'addressLine2': None,
            'postalCode': None,
            'city': None,
            'state': None,
            'country': None,
        },
        'building': property_name
    }

    return location