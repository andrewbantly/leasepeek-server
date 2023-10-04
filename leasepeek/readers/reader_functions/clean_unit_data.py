unit_keywords = ['Unit', 'Bldg/Unit']
floorplan_keywords = ['Unit Type', 'Floorplan']
sqft_keywords = ['sq ft', 'sqft', 'SQFT', 'Unit Sq Ft']
market_keywords = ['Market', 'Market Rent']
tenant_keywords = ['Name']
lease_keywords = ['Lease Dates']

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
    else:
        return 'unclassified'

def clean_unit_data(data_array):
    cleaned_data = []
    print(data_array[0])
    for entry in data_array:
        cleaned_entry = {
            'unit': None,
            'floorplan': None,
            'sqft': None,
            'market': None,
            'tenant': None,
            'unclassified': {}
        }
        for key, value in entry.items():
            category = classify_key(key)
            if category in ['unit', 'floorplan', 'sqft', 'market', 'tenant']:
                cleaned_entry[category] = value
            else:
                cleaned_entry['unclassified'][key] = value

        cleaned_data.append(cleaned_entry)
    return cleaned_data
