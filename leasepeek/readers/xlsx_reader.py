from datetime import datetime
import json

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%m-%d-%Y")
        return super().default(obj)

def read_rentroll(data_frame):
    df = data_frame
    # Building Data info
    building = df.iloc[0,0]
    as_of = str(df.iloc[1,0])
    as_of_split = as_of.split("=")
    as_of_date_strip = as_of_split[1].strip()
    as_of_date = datetime.strptime(as_of_date_strip, "%m/%d/%Y")
    as_of_date_formatted = as_of_date.strftime("%m-%d-%Y")
    # building_info = {"Location": building, "As of date": as_of_date_formatted}

    # find the start of the unit information
    i = 0 
    while df.iloc[i, 0] != "Current/Notice/Vacant Residents":
        i += 1
    # Residents of building info
    i += 1
    residents_scan = True
    residents_list = []
    c = {}
    status = "Current/Notice/Vacant"
    while residents_scan:
        cell_obj = df.iloc[i, 0]
        if cell_obj == "Summary Groups":
            residents_list.append(c)
            residents_scan = False
        elif cell_obj == "Future Residents/Applicants":
            status = "Future Residents/Applicants"
        elif str(cell_obj) != "nan":
            if c:
                residents_list.append(c)
            c = {}
            unit = df.iloc[i,0]
            unit_type = df.iloc[i,1]
            sq_ft = df.iloc[i,2]
            res_id = df.iloc[i,3]
            res_name = df.iloc[i,4]
            market_rent = df.iloc[i,5]
            charge_line = df.iloc[i,6]
            amount_line = df.iloc[i,7]
            res_deposit = df.iloc[i,8]
            other_deposit = df.iloc[i,9]
            move_in_date  = df.iloc[i,10]
            lease_expire_date  = df.iloc[i,11]
            move_out_date  = df.iloc[i,12]
            balance  = df.iloc[i,13]
            c["building"] = building
            c["date"] = as_of_date_formatted
            c["status"] = status
            c["unit"] = unit
            c["unitType"] = unit_type
            c["unitSqFt"] = sq_ft
            c["resident"] = res_id
            c["name"] = res_name
            c["marketRent"] = market_rent
            if str(charge_line) != "nan" and str(amount_line) != "nan":
                c[charge_line] = amount_line
                # print(charge_line, amount_line)
            c["resDeposit"] = res_deposit
            c["otherDeposit"] = other_deposit
            if str(move_in_date) != "nan":
                move_in_date_formatted = move_in_date.strftime('%Y-%m-%d')
                c["moveIn"] = move_in_date_formatted
            else:
                c["moveIn"] = ""
            if str(lease_expire_date) != "nan":
                lease_expire_date_formatted = lease_expire_date.strftime('%Y-%m-%d')
                c["leaseExp"] = lease_expire_date_formatted
            else:
                c["leaseExp"] = ""
            if str(move_out_date) != "nan":
                move_out_date_formatted = move_out_date.strftime('%Y-%m-%d')
                c["moveOut"] = move_out_date_formatted
            else:
                c["moveOut"] = ""
            c["balance"] = balance
        elif str(cell_obj) == "nan":
            charge_line = df.iloc[i, 6]
            amount_line = df.iloc[i, 7]
            if str(charge_line) != "nan" and str(amount_line) != "nan":
                if charge_line in c:
                    c[charge_line] += amount_line
                else:
                    c[charge_line] = amount_line
        i += 1

    # Summary Group info
    summary_group_scan = True
    summary_groups = []
    g = {}
    while summary_group_scan:
        cell_obj = df.iloc[i, 0]
        if cell_obj == "Totals:":
            summary_groups.append(g)
            summary_group_scan = False
        elif str(cell_obj) != "nan":
            if g:
                summary_groups.append(g)
            g = {}
            group = df.iloc[i, 0]
            sq_ft = df.iloc[i, 5]
            market_rent = df.iloc[i, 6]
            lease_charges = df.iloc[i, 7]
            security_deposit = df.iloc[i, 8]
            other_deposits = df.iloc[i, 9]
            unit_count = df.iloc[i, 10]
            unit_occupancy = df.iloc[i, 11]
            sqft_occupied = df.iloc[i, 12]
            balance = df.iloc[i, 13]
            g["Group"] = group
            g["Square Footage"] = sq_ft
            g["Market Rent"] = market_rent
            g["Lease Charges"] = lease_charges
            g["Security Deposit"] = security_deposit
            g["Other Deposits"] = other_deposits
            g["Number of Units"] = unit_count
            g["Percentage Unit Occupancy"] = unit_occupancy
            g["Percentage Sqft Occupied"] = sqft_occupied
            g["Balance"] = balance
        i += 1
    # print(residents_list)

    # Summary charges info
    max_row = df.iloc[:,0].last_valid_index()
    summary_charges_scan = False
    summary_charges = []
    s = {}
    for x in range(i, max_row + 1):
        cell_obj = df.iloc[x, 0]
        if summary_charges_scan:
            if cell_obj != "Total":
                charge_type = df.iloc[x, 0]
                charge_amount = df.iloc[x, 3]
                s[charge_type] = charge_amount
            else:
                summary_charges.append(s)
        else:
            if cell_obj == "Charge Code":
                summary_charges_scan = True

    rent_roll_list = [ #building_info, 
                      {"Tenants": residents_list},
                      {"Summary Groups": summary_groups},
                      {"Summary Charges": summary_charges}
                    ]

    return rent_roll_list