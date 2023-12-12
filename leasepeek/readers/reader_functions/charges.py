def charge_codes(unit_data, loss_to_lease):
    charges = {'rent': {
        'value': loss_to_lease['rentIncome'],
        'type': 'contractualRent',
    }}

    for unit in unit_data:
        for charge in unit['charges']:
            code = charge['code']
            if code in charges:
                charges[code]['value'] += charge['value']
            else:
                charges[code] = {
                    'value': charge['value'],
                    'type': ''
                }

    return charges