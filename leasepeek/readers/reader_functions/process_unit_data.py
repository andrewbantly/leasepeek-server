import pandas as pd

edge_cases = ["Description", "Charge Amount", "Credit Amount"]

def process_unit_data(df, data_types):
    print("Processing unit data.")
    title_row_index = data_types.pop() + 1
    all_units = []
    current_unit = {}
    charge_line = ""
    charge_amount = None  # Set to None for initial state

    for i, row in df.iloc[title_row_index:].iterrows():
        # If we reach a "Total"
        if df.iloc[i, 0] == "Total":
            if current_unit:
                all_units.append(current_unit)
            break

        # If we encounter a new unit while processing an existing one
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

                # Use this condition to ensure we have both charge_line and charge_amount before adding to current_unit
                if charge_line and charge_amount is not None:
                    current_unit[charge_line] = charge_amount
                    charge_line = ""
                    charge_amount = None  # Reset to None for next potential value
            else:
                # If the column isn't already populated (for cases where we process charges for the same unit)
                if data_types[x] not in current_unit:
                    current_unit[data_types[x]] = df.iloc[i, x]

    if current_unit:  # Add the last unit if there's any data left
        all_units.append(current_unit)
        
    print(all_units[1])
