def market_value_per_floorplan(data):
    float_count = 0
    str_count = 0
    int_count = 0
    other = 0
    for unit in data:
        if type(unit['market']) == float:
            float_count += 1
        elif type(unit['market']) == str:
            str_count += 1
        elif type(unit['market']) == int:
            int_count += 1
        else:
            other += 1
    print("Ints", int_count)
    print("Floats", float_count)
    print("Strs", str_count)
    print("Other", other)