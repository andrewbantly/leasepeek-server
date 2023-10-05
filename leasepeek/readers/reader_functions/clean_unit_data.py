unit_keywords = ['Unit', 'Bldg/Unit']
floorplan_keywords = ['Unit Type', 'Floorplan']
sqft_keywords = ['sq ft', 'sqft', 'SQFT', 'Unit Sq Ft']
market_keywords = ['Market', 'Market Rent']
tenant_keywords = ['Name']
lease_keywords = ['Lease Dates']
resident_id_keywords = ['Resident']
move_in_keywords = ['Move In']
move_out_keywords = ['Move Out']
lease_expire_keywords = ['Lease Expiration']
resident_deposit_keyords = ['Resident Deposit']
other_deposit_keyords = ['Other Deposit']
balance_keyords = ['Balance']
total_keywords = ['Total']
charge_codes = ['rnt', 'rub', 'valtsh', 'cmf', 'package', 'pst', 'prk', 'covpark', 'rent', 'bbpest', 'conciere', 'bbtr', 'zero', 'ptr', 'CNSVCpst', 'mtm', 'rubsew', 'emp', 'petf', 'conc-prk', 'insur', 'stor', 'svcanml', 'conc-lmp', 'conc-sto']

def classify_key(key):
    if any(keyword == key for keyword in unit_keywords):
        return 'unit'
    elif any(keyword == key for keyword in floorplan_keywords):
        return 'floorplan'
    elif any(keyword == key for keyword in sqft_keywords):
        return 'sqft'
    elif any(keyword == key for keyword in market_keywords):
        return 'market'
    elif any(keyword == key for keyword in tenant_keywords):
        return 'tenant'
    elif any(keyword == key for keyword in resident_id_keywords):
        return 'residentId'
    elif any(keyword == key for keyword in move_in_keywords):
        return 'moveIn'
    elif any(keyword == key for keyword in move_out_keywords):
        return 'moveOut'
    elif any(keyword == key for keyword in lease_expire_keywords):
        return 'leaseExpire'
    elif any(keyword == key for keyword in resident_deposit_keyords):
        return 'residentDeposit'
    elif any(keyword == key for keyword in other_deposit_keyords):
        return 'otherDeposit'
    elif any(keyword == key for keyword in balance_keyords):
        return 'balance'
    elif any(keyword == key for keyword in total_keywords):
        return 'total'
    elif any(keyword == key for keyword in charge_codes):
        return 'charges'
    else:
        return 'unclassified'

def clean_unit_data(data_array):
    cleaned_data = []
    print("### RAW DATA")
    print(data_array[0])
    print("")
    for entry in data_array:
        cleaned_entry = {
            'unit': None,
            'floorplan': None,
            'sqft': None,
            'market': None,
            'tenant': None,
            'residentId': None,
            'moveIn': None,
            'moveOut': None,
            'leaseExpire': None,
            'residentDeposit': None,
            'otherDeposit': None,
            'balance': None,
            'total': None,
            'charges': [],
            'unclassified': {}
        }
        for key, value in entry.items():
            category = classify_key(key)
            if category in ['unit', 'floorplan', 'sqft', 'market', 'tenant', 'residentId', 'moveIn', 'moveOut', 'leaseExpire', 'residentDeposit', 'otherDeposit', 'balance', 'total']:
                cleaned_entry[category] = value
            elif category == 'charges':
                cleaned_entry['charges'].append({'code': key, 'value': value})
            else:
                cleaned_entry['unclassified'][key] = value

        cleaned_data.append(cleaned_entry)
    print("### CLEAN DATA")
    print(cleaned_data[0])
    print("")
    fix_data = []
    for c in cleaned_data:
        if c['unclassified'] != {}:
            a = c['unclassified']
            if a not in fix_data:
                fix_data.append(a)
    
    print("### MISSING CHARGE CODES")
    print(fix_data)
    return cleaned_data
