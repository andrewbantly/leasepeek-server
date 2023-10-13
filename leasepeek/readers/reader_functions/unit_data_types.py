import pandas as pd

# Set of keywords used to identify column titles in the dataframe
keywords = {'Unit Type', 'Floorplan', 'Unit Sq Ft', 'Name', 'Market Rent', 'Charge Code', 'Amount', 'Resident Deposit', 'Other Deposit', 'Move In', 'Lease Expiration', 'Move Out', 'Balance', 'Code', 'Deposit', 'Expiration', 'Sq Ft', 'SQFT'}

def find_unit_data_types(df):
    """
    Parses the input dataframe to identify and map column titles based on pre-defined keywords.

    The function checks the first 15 rows of the dataframe, assuming that column titles
    could be spread across multiple rows. If column titles are found in two consecutive rows, 
    they are concatenated. If a keyword is seen more than once, subsequent occurrences are marked "nan" to avoid duplicates caused by merged cells. 
    
    Parameters:
    - df (pandas.DataFrame): The input dataframe to process.

    Returns:
    - dict: A mapping of column titles to their respective column indices. Also includes the 
            index of the title row as "Title Row".
    
    Example Usage:
    >>> df = pd.read_excel("example.xlsx")
    >>> find_unit_data_types(df)
    {'Unit Type': 0, 'Floorplan': 1, 'Market Rent': 2, ... , 'Title Row': 8}
    """

    # List to store identified column titles
    column_titles = []

    # Dictionary to map column titles to column indices
    title_column_mapping = {}

    # Determine which row(s) might contain the titles
    # is_title_row example: [False, False, False, False, True, True, False, ...]
    is_title_row = []
    for _, row in df.head(15).iterrows():
        # row_str example: 'Unit Unit Type Unit Resident Name Market Charge Amount Resident Other Move In Lease Move Out Balance'
        row_str = ' '.join(row.dropna().astype(str))
        # Check if a keyword in keywords exists in row_str, if any does exists, any() will return True
        if any(keyword in row_str for keyword in keywords):
            is_title_row.append(True)
        else:
            is_title_row.append(False)

    # Identify rows that contain the titles. If two consecutive rows are detected, we assume the titles span across both rows.
    # The enumerate() function is used to iterate over `is_title_row`. It returns tuples of the form (index, value). For example, for the list [False, True, False], enumerate() would produce (0, False), (1, True), (2, False)
    # This list comprehension captures the indices where the value is True. 
    # So if `is_title_row` was [False, True, False, True], title_rows would be [1, 3].
    title_rows = [i for i, x in enumerate(is_title_row) if x]
    
    if len(title_rows) >= 2:
        # Create list of each of the two title rows 
        # First row example: ['Unit', 'Unit Type', 'Unit', 'Resident', 'Name', 'Market', 'Charge', ...]
        # Second row example: ['nan', 'nan', 'Sq Ft', 'nan', 'nan', 'Rent', 'Code', ...]
        first_row = df.iloc[title_rows[0]].astype(str).tolist() 
        second_row = df.iloc[title_rows[1]].astype(str).tolist()

        # Track titles that have been identified already
        seen_titles = [] 

        # Concatenate the titles if they span two rows
        for col in range(len(first_row)):
            # Start building the title from the first row's cell content
            title = first_row[col]

            # Check if the corresponding cell in the second row has valid content. If yes, concatenate it with the first row's cell content
            if not pd.isna(second_row[col]) and second_row[col] != "nan":
                title += " " + second_row[col]

            # Clean up the title: remove leading/trailing spaces and newline characters
            title = title.strip().replace('\n', ' ')

            # If the title has been seen before (i.e., it's a duplicate due to merged cells), then mark it as "nan" to avoid duplicates
            if title in seen_titles:
                title = "nan"
            else:
                # If the title is unique, store it in the seen_titles list
                seen_titles.append(title)

            # Add the processed title to the list of column titles
            column_titles.append(title)

            # If the title is valid (not marked as "nan"), store its corresponding column index in the mapping
            if title != "nan":
                title_column_mapping[title] = col


    # Titles are in a single row scenario
    else:
        # If there are no title rows identified, then there's no point proceeding further.
        if not title_rows:
            return {}

        # Initialize a list to keep track of titles we've seen so far
        seen_titles = []

        # Directly get the row which was identified as the title row
        title_row_index = title_rows[0]
        row = df.iloc[title_row_index].astype(str)

        # Drop NA values and convert the row content to a list of strings
        # column_titles_raw example: ['Unit', 'Type', 'Market', 'Name', 'Lease Dates', 'Notice', 'Net Change\nIn Balance', 'Resident\nBalance', 'Description', 'Charge Amount', 'Credit Amount']
        column_titles_raw = row.dropna().tolist()
        column_titles = []
        
        # Iterate over each title in the row
        for title in column_titles_raw:
            # If the title has been seen before (i.e., it's a duplicate due to merged cells), then mark it as "nan" to avoid duplicates
            if title in seen_titles:
                title = "nan"

            else:
                # If the title is unique, store it in the seen_titles list and clean it by removing newline characters
                seen_titles.append(title)
                title = title.replace('\n', ' ')

            # Add the processed title to the list of column titles
            column_titles.append(title)

        # Store the column index of each unique title in the mapping   
        for col, title in enumerate(column_titles):
            if title != "nan":
                title_column_mapping[title] = col

    # Pop the last identified title row index from the list. If it's a two-row title scenario, then it will be the lower title row. 
    title_row = title_rows.pop()
    # Store the identified title row index in the mapping for future reference
    title_column_mapping["Title Row"] = title_row

    # Return the mapping of titles to their column indexes
    return title_column_mapping