

status_keywords = {'upcoming', 'approved', 'Future Residents/Applicants', 'Applicant', 'Pending renewal', 'Former resident', 'Former applicant'}

def find_loss_to_lease(unit_data):
    market_sum = 0
    rent_income = 0
    for unit in unit_data:
        if unit['status'] not in status_keywords:
            market_sum += unit['market']
            rent_income += unit['rent']

    print()
    print("##### LOSS TO LEASE")
    print({
        'marketSum': market_sum,
        'rentIncome': rent_income
    })
    print()
    
    return {
        'marketSum': market_sum,
        'rentIncome': rent_income
    }