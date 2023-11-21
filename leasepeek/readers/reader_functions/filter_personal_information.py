

def filter_personal_info(unit_data):

    for unit in unit_data:
        unit.pop('tenant')
        unit.pop('address')
        unit.pop('residentId')
        unit.pop('nsf')
        unit.pop('unclassified')

    return unit_data