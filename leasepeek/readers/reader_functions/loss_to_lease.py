
def find_loss_to_lease(unit_data):
    market_sum = 0
    rent_income = 0
    for unit in unit_data:
        market_sum += unit['market']
        rent_income += unit['rent']

    return {
        'marketSum': market_sum,
        'rentIncome': rent_income
    }