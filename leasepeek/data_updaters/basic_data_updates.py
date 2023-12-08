def update_basic_data(data):
    print('update basic data')
    asOf = data.get('asOf')
    market = data.get('market')
    buildingName = data.get('buildingName')
    unitsConfirmed = data.get('unitsConfirmed')
    addressLine1 = data.get('addressLine1')
    addressLine2 = data.get('addressLine2')
    city = data.get('city')
    state = data.get('state')
    zipCode = data.get('zipCode')

    print()
    print("### RAW DATA")
    print(data)
    print()
    print(f"""Form Data:
As Of: {asOf}
Market: {market}
Building Name: {buildingName}
Units Confirmed: {unitsConfirmed}
Address Line 1: {addressLine1}
Address Line 2: {addressLine2}
City: {city}
State: {state}
Zip Code: {zipCode}
""")
    print()