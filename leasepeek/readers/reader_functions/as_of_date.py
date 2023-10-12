import re

date_patterns = [r'\d{1,2}/\d{1,2}/\d{4}', r'\d{1,2}/\d{4}']

def find_as_of_date(df, file_name, title_row):

    # Look for 'as of' date inside of dataframe (excel data)
    for i, row in df.head(title_row).iterrows(): 
        row_str = ' '.join(row.dropna().astype(str))
        for pattern in date_patterns:
            match = re.search(pattern, row_str)
            if match:
                found_date = match.group(0)
                return found_date
    
    # If no as of date is in excel file, look for it in the file name
    pattern = r'(\d{1,2}[._-]\d{1,2}[._-]\d{2,4})'
    match = re.search(pattern, file_name)
    if match:
        date = match.group(1)
        # Replace any separator with /
        date = date.replace('.', '/').replace('_', '/').replace('-', '/')
        
        # Handle two digit years to be YYYY format
        parts = date.split('/')
        if len(parts[2]) == 2:
            parts[2] = '20' + parts[2]
        
        # Handle one digit months or days to be MM or DD format
        parts[0] = parts[0].zfill(2)
        parts[1] = parts[1].zfill(2)
        found_date = '/'.join(parts)
        return found_date

    # If there is no date in the excel file or file name, return "date not found" 
    return "Date not found"