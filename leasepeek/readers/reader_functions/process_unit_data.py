import pandas as pd

def process_unit_data(df, data_types):
    data_starting_row = data_types["Title Row"]
    data_types.pop("Title Row")
    print(data_starting_row)