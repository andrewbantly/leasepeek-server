import pandas as pd

edge_cases = ["Description", "Charge Amount", "Credit Amount"]

def process_unit_data(df, data_types):
    print("Processing unit data.")
    title_row_index = data_types.pop() + 1
    all_units = []
    current_unit = {}
    charge_line = ""
    charge_amount = None 
    print()
    print(data_types)
    for i, row in df.iloc[title_row_index:].iterrows():
        if df.iloc[i, 0] == "Total":
            if current_unit:
                all_units.append(current_unit)
            break

        if not pd.isna(df.iloc[i, 0]) and current_unit:
            all_units.append(current_unit)
            current_unit = {}

        for x in range(len(data_types)):
            if data_types[x] in edge_cases:
                if data_types[x] == "Description":
                    charge_line = df.iloc[i, x]
                if data_types[x] == "Charge Amount" and not pd.isna(df.iloc[i, x]):
                    charge_amount = float(df.iloc[i, x])
                if data_types[x] == "Credit Amount" and not pd.isna(df.iloc[i, x]):
                    charge_amount = -abs(float(df.iloc[i, x]))

                if charge_line and charge_amount is not None:
                    current_unit[charge_line] = charge_amount
                    charge_line = ""
                    charge_amount = None
            else:
                if data_types[x] not in current_unit:
                    current_unit[data_types[x]] = df.iloc[i, x]

    if current_unit: 
        all_units.append(current_unit)
    print()
    print(all_units[0])
    print()
