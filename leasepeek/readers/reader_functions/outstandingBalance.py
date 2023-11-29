def calculate_outstanding_balance(unit_data):
    balance = 0

    for unit in unit_data:
        if unit['balance']:
            balance += unit['balance']
        unit['balance'] = float(unit['balance'])

    return float(balance)
