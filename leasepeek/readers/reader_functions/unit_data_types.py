import pandas as pd

keywords = ['Unit Type', 'Floorplan', 'Unit Sq Ft', 'Name', 'Market Rent', 'Charge Code', 'Amount', 'Resident Deposit', 'Other Deposit', 'Move In', 'Lease Expiration', 'Move Out', 'Balance', 'Code', 'Deposit', 'Expiration', 'Sq Ft', 'SQFT', 'Balance']

def find_unit_data_types(df):
    column_titles = []
    title_column_mapping = {}

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
    if len(title_rows) >= 2:
        first_row = df.iloc[title_rows[0]].astype(str).tolist()  # forward fill NaN values
        second_row = df.iloc[title_rows[1]].astype(str).tolist()  # forward fill NaN values
        print("second row:", second_row)
        seen_titles = []
        # Concatenate the titles and populate the mapping
        for col in range(len(first_row)):
            title = first_row[col]
            if not pd.isna(second_row[col]) and second_row[col] != "nan":
                title += " " + second_row[col]
            title = title.strip().replace('\n', ' ')

            if title in seen_titles:
                title = "nan"
            else:
                seen_titles.append(title)

            column_titles.append(title)

            if title != "nan":
                title_column_mapping[title] = col

    # Titles in single row
    else:
        seen_titles = []
        for index, row in df.head(15).iterrows():
            row = row.fillna(method='ffill').astype(str)  # forward fill NaN values
            row_str = ' '.join(row.dropna().astype(str))
            if any(keyword in row_str for keyword in keywords):
                column_titles_raw = row.dropna().astype(str).tolist()
                column_titles = []
                for title in column_titles_raw:
                    if title in seen_titles:
                        title = "nan"
                        column_titles.append(title)
                    else:
                        seen_titles.append(title)
                        title = title.replace('\n', ' ')
                        column_titles.append(title)
                for col, title in enumerate(column_titles):
                    if title != "nan":
                        title_column_mapping[title] = col
    title_row = title_rows.pop()
    title_column_mapping["Title Row"] = title_row
    return title_column_mapping
