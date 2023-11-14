def find_total_units(unit_data):
    units = set()
    for unit in unit_data:
        units.add(unit['unit'])

    return len(units)