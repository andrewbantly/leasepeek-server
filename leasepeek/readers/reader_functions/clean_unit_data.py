reshID_keyords = ['Resh ID']
unit_keywords = ['Unit', 'Bldg/Unit', 'Unit Number']
address_keywords = ['Address Line 1']
floorplan_keywords = ['Unit Type', 'Floorplan', 'Unit  Type', 'Type']
sqft_keywords = ['sq ft', 'sqft', 'SQFT', 'Unit Sq Ft', 'Sq Ft', 'Unit Sqft']
market_keywords = ['Market', 'Market Rent', 'Market + Addl.']
rent_keywords = ['Rent', 'rnt', 'rent', 'Lease Rent', 'RENT-Rent']
status_keywords = ['Status', 'Unit/Lease Status', 'Unit Status']
tenant_keywords = ['Name', 'Tenant']
lease_keywords = ['Lease Dates']
resident_id_keywords = ['Resident', 'Lease ID']
move_in_keywords = ['Move In', 'Move-In', 'Move IN Date']
move_out_keywords = ['Move Out', 'Move-Out']
lease_start_keywords = ['Lease From', 'Lease Start']
lease_expire_keywords = ['Lease Expiration', 'Lease To', 'Lease End', 'Lease Expiration Date']
resident_deposit_keywords = ['Resident Deposit', 'Deposit', 'Dep On Hand']
other_deposit_keywords = ['Other Deposit']
balance_keywords = ['Balance', 'Resident Balance', 'Past Due']
total_keywords = ['Total', 'Total Billing']
NSF_keywords = ['NSF Count']
charge_codes = ['rub', 'valtsh', 'cmf', 'package', 'pst', 'prk', 'covpark', 'bbpest', 'conciere', 'bbtr', 'zero', 'ptr', 'CNSVCpst', 'mtm', 'rubsew', 'emp', 'petf', 'conc-prk', 'insur', 'stor', 'svcanml', 'conc-lmp', 'conc-sto', 'Utility', 'Utility Recapture', 'TECH', 'PETF', 'CONC', 'STOR', 'EMPL', 'MODL', 'OFCR', 'LTOR-Loss To Lease In Force', 'STOR-Storage Space #', 'CABL-Cable Television Charges', 'INTR-Internet Access', 'PARK-Parking', 'MTOM-Month To Month Charges', 'RLL-PDLW', 'LTOL-Loss To Lease In Force', 'GAR-Garage Rental', 'RLLG-PDLW LEGACY', 'PETR-Pet Rent', 'W/D Washer/Dryer Rental Charges', 'VAC -Vacancy Loss', 'GTOL-Gain To Lease In Force', 'GTOR-Gain To Lease In Force', 'W/D-Washer/Dryer Rental Charges', 'PETF-Pet Fees Or Charges', 'GAR-Garage Rental #', 'MODE-Model', 'park', 'mtmf', 'conc-rec']
negative_charge_codes = ['MODE-Model', 'LTOL-Loss To Lease In Force', 'VAC -Vacancy Loss']

def classify_key(key):
    if any(keyword == key for keyword in reshID_keyords):
        return 'resh'
    if any(keyword == key for keyword in unit_keywords):
        return 'unit'
    if any(keyword == key for keyword in lease_keywords):
        return 'leaseDates'
    if any(keyword == key for keyword in address_keywords):
        return 'address'
    elif any(keyword == key for keyword in floorplan_keywords):
        return 'floorplan'
    elif any(keyword == key for keyword in sqft_keywords):
        return 'sqft'
    elif any(keyword == key for keyword in market_keywords):
        return 'market'
    elif any(keyword == key for keyword in rent_keywords):
        return 'rent'
    elif any(keyword == key for keyword in status_keywords):
        return 'status'
    elif any(keyword == key for keyword in tenant_keywords):
        return 'tenant'
    elif any(keyword == key for keyword in resident_id_keywords):
        return 'residentId'
    elif any(keyword == key for keyword in move_in_keywords):
        return 'moveIn'
    elif any(keyword == key for keyword in move_out_keywords):
        return 'moveOut'
    elif any(keyword == key for keyword in lease_start_keywords):
        return 'leaseStart'
    elif any(keyword == key for keyword in lease_expire_keywords):
        return 'leaseExpire'
    elif any(keyword == key for keyword in resident_deposit_keywords):
        return 'residentDeposit'
    elif any(keyword == key for keyword in other_deposit_keywords):
        return 'otherDeposit'
    elif any(keyword == key for keyword in balance_keywords):
        return 'balance'
    elif any(keyword == key for keyword in total_keywords):
        return 'total'
    elif any(keyword == key for keyword in charge_codes):
        return 'charges'
    elif any(keyword == key for keyword in NSF_keywords):
        return 'nsf'
    else:
        return 'unclassified'

def clean_unit_data(data_array):
    cleaned_data = []
    for entry in data_array:
        cleaned_entry = {
            'unit': None,
            'address': None,
            'floorplan': None,
            'sqft': None,
            'market': 0,
            'rent': 0,
            'status': None,
            'tenant': None,
            'residentId': None,
            'moveIn': None,
            'moveOut': None,
            'leaseStart': None,
            'leaseExpire': None,
            'residentDeposit': None,
            'otherDeposit': None,
            'balance': None,
            'total': None,
            'nsf': None,
            'resh': None,
            'charges': [],
            'unclassified': {}
        }
        for key, value in entry.items():
            category = classify_key(key)
            if category in ['unit', 'address', 'floorplan', 'sqft', 'tenant', 'residentId', 'status', 'moveIn', 'moveOut', 'leaseStart','leaseExpire', 'resh','nsf']:
                cleaned_entry[category] = value
            elif category in ['rent', 'total', 'market', 'balance', 'residentDeposit', 'otherDeposit']:
                if isinstance(value, str):
                    value = value.replace('*', '').replace(',', '').strip()
                    try:
                        value = int(round(float(value)))
                    except ValueError:
                        print(f"Error converting '{value}' to integer for key '{key}'. Using raw value.")
                if value == '':
                    cleaned_entry[category] = 0
                else:
                    cleaned_entry[category] = value
            elif category == 'charges':
                if isinstance(value, str):
                    value = value.replace('*', '').replace(',','').strip()
                    try:
                        value = int(round(float(value)))
                    except ValueError:
                        print(f"Error converting '{value}' to integer for key '{key}'. Using raw value.")
                if key in negative_charge_codes:
                    value = -abs(value)
                cleaned_entry['charges'].append({'code': key, 'value': value})
            elif category == 'leaseDates':
                if len(value) == 21:
                    start, end = value.split()
                    cleaned_entry['leaseStart'] = start
                    cleaned_entry['leaseExpire'] = end
            else:
                cleaned_entry['unclassified'][key] = value

        cleaned_data.append(cleaned_entry)

    return cleaned_data
