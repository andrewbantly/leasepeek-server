import pandas as pd

keywords = ['Total', 'Totals', 'Totals:', 'Total Market Rent', 'Applications', 'Summary Groups', 'Future Residents']

charge_types = ['Charge Code', 'Amount', 'Rent Charge Description', 'Rent Charge Amount', 'Description', 'Charge Amount', 'Credit Amount']

def process_unit_data(df, data_types):
    data_starting_row = data_types["Title Row"] + 1
    data_types.pop("Title Row")
    data_ending_row = 0
    for i, row in df.iterrows():
        cell_value = str(row.iloc[0])
        if any(keyword in cell_value for keyword in keywords):
            data_ending_row = i
            break
    if data_ending_row == 0:
        print("Data read error. No ending row for unit data recognized.")
    
    new_data_types = {}
    charge_codes = {}
    for d in data_types:
        if d not in charge_codes:
            new_data_types[data_types[d]] = d

    data = []
    
    for i in range(data_starting_row, data_ending_row):
        current_unit = {}
        if df.iloc[i,0] == "Current/Notice/Vacant Residents":
            continue
        if str(df.iloc[i,0]) == "nan":
            continue
        for d in new_data_types:
            current_unit[new_data_types[d]] = df.iloc[i, d]
        data.append(current_unit)
        current_unit = {}
    print(data[1])
    # iterate through each row and column
    # use the hash table to match column value = column titles 
    # add column title and value into a unit data dictionary (not started)
    # finish the loop, add the unit data dictionary to the bigger data dictionary

        