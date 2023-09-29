import re

date_patterns = [r'\d{1,2}/\d{1,2}/\d{4}', r'\d{1,2}/\d{4}']

def find_as_of_date(df):
    for i, row in df.head(10).iterrows(): 
        row_str = ' '.join(row.dropna().astype(str))
        for pattern in date_patterns:
            match = re.search(pattern, row_str)
            if match:
                found_date = match.group(0)
                print("Date found:", found_date)
                return found_date
    print("Date not found!")

    return None