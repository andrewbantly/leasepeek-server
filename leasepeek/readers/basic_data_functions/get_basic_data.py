def find_basic_data(cursor):
    basic_data_list = []
    for doc in cursor:
        unit_data = doc.get('data')
        vacants = 0
        total_units = len(unit_data)
        floor_plans = {}
        for unit in unit_data:
            if unit['tenant'] == 'VACANT':
                vacants += 1
            if unit['floorplan'] in floor_plans:
                floor_plans[unit['floorplan']].append(unit['market'])
            if unit['floorplan'] not in floor_plans:
                floor_plans[unit['floorplan']] = [unit['market']]
        for plan in floor_plans:
            plan_count = len(floor_plans[plan])
            avg_market = round(sum(floor_plans[plan]) / plan_count,2)
            floor_plans[plan] = {'avg':avg_market, 'count':plan_count}
        basic_data = {
            'objectId': str(doc.get('_id')),
            'location': doc.get('location', None),
            'date': doc.get('date', None),
            'asOf': doc.get('asOf', None),
            'totalUnits': total_units,
            'vacants': vacants,
            'floorplans': floor_plans,
        }
        basic_data_list.append(basic_data)
    return basic_data_list