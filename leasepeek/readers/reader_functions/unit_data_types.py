import pandas as pd

keywords = ['Unit Type', 'Floorplan', 'Unit Sq Ft', 'Name', 'Market Rent', 'Charge Code', 'Amount', 'Resident Deposit', 'Other Deposit', 'Move In', 'Lease Expiration', 'Move Out', 'Balance', 'Code', 'Deposit', 'Expiration', 'Sq Ft', 'SQFT', 'Balance']

def find_unit_data_types(df):
    column_titles = []

    # Determine titles are in multiple rows
    is_title_row = []
    for _, row in df.head(15).iterrows():
        row_str = ' '.join(row.dropna().astype(str))
        if any(keyword in row_str for keyword in keywords):
            is_title_row.append(True)
        else:
            is_title_row.append(False)

    # Assuming the titles are in two consecutive rows
    title_rows = [i for i, x in enumerate(is_title_row) if x]
    first_data_row = title_rows[-1] + 1
    
    if len(title_rows) >= 2:
        first_row = df.iloc[title_rows[0]].astype(str).tolist()
        second_row = df.iloc[title_rows[1]].astype(str).tolist()
    
        # Concatenate the titles
        for col in range(len(first_row)):
            title = first_row[col]
            if not pd.isna(second_row[col]) and second_row[col] != "nan":
                title += " " + second_row[col]
            
            # Check for merged cells and adjust
            if pd.isna(df.iloc[first_data_row, col]) and col < df.shape[1] - 1:
                next_val = df.iloc[first_data_row, col+1]
                if not pd.isna(next_val):  # Ensure it's not NaN before concatenation
                    title = str(title) + " " + str(next_val)

            # Ensure title is a string before stripping
            title = str(title).strip()
            column_titles.append(title)

    else:
        for index, row in df.head(15).iterrows():
            row_str = ' '.join(row.dropna().astype(str))
            if any(keyword in row_str for keyword in keywords):
                for col, title in enumerate(row):
                    # Check for merged cells and adjust
                    if pd.isna(df.iloc[first_data_row, col]) and col < df.shape[1] - 1:
                        next_val = df.iloc[first_data_row, col+1]
                        if not pd.isna(next_val):  # Ensure it's not NaN before concatenation
                            title = str(title) + " " + str(next_val)
                    title = str(title).strip()  # Ensure title is a string before stripping
                    column_titles.append(title)
                column_titles = [title.replace('\n', ' ') for title in column_titles]
                break

    print("Col titles:", column_titles)
    column_titles.append(title_rows.pop())
    return column_titles
