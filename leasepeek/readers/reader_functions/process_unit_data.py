import pandas as pd

keywords = ['Total', 'Totals', 'Totals:', 'Total Market Rent', 'Applications', 'Summary Groups', 'Future Residents']

def process_unit_data(df, data_types):
    data_starting_row = data_types["Title Row"]
    data_types.pop("Title Row")
    print("")

    for i, row in df.iterrows():
        cell_value = str(row.iloc[0])
        if any(keyword in cell_value for keyword in keywords):
            print(row)
            print(i)
            break

    print("")