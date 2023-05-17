def new_file_parser(input_file):
    global_dict = {}
    tools = {}
    coordinates = {}
    requests = {}
    with open(input_file, 'r') as f:
        for line in f:
            line.strip()
            if "DAYS" in line:
                global_dict["DAYS"] = int(line.split(" = ")[1])
                continue
            elif "CAPACITY" in line:
                global_dict["CAPACITY"] = int(line.split(" = ")[1])
                continue
            elif "MAX_TRIP_DISTANCE" in line:
                global_dict["MAX_TRIP_DISTANCE"] = int(line.split(" = ")[1])
                continue
            elif "DEPOT_COORDINATE" in line:
                global_dict["DEPOT_COORDINATE"] = int(line.split(" = ")[1])
                continue
            elif "VEHICLE_COST" in line:
                global_dict["VEHICLE_COST"] = int(line.split(" = ")[1])
                continue
            elif "VEHICLE_DAY_COST" in line:
                global_dict["VEHICLE_DAY_COST"] = int(line.split(" = ")[1])
                continue
            elif "DISTANCE_COST" in line:
                global_dict["DISTANCE_COST"] = int(line.split(" = ")[1])
                continue
            elif "TOOLS" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    tool_i = next(f).split()
                    tool_i = {"id": int(tool_i[0]), "size": int(tool_i[1]),
                                     "max_available": int(tool_i[2]), "cost": int(tool_i[3])}
                    tools[tool_i["id"]] = tool_i
                continue
            elif "COORDINATES" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    co_type = next(f).split()
                    geo_inf = {"id": int(co_type[0]), "x_co": int(co_type[1]), "y_co": int(co_type[2])}
                    coordinates[geo_inf["id"]] = geo_inf
                continue
            elif "REQUESTS" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    req_type = next(f).strip().split()
                    req_type = {"id": int(req_type[0]), "locid": int(req_type[1]),"fromDay": int(req_type[2]),
                               "toDay": int(req_type[3]),"numDays": int(req_type[4]), "toolid": int(req_type[5]),
                                "toolCount": int(req_type[6])} #"order": {'id': int(req_type[0]), 'locid': int(req_type[1]),
                               #           'fromDay': int(req_type[2]), 'toDay': int(req_type[3]),'numDays': int(req_type[4]),
                               #                                         'toolid': int(req_type[5]),'toolCount': int(req_type[6])}}
                    requests[req_type["id"]] = req_type
                continue
            elif "DATASET" in line:
                global_dict["DATASET"] = line.split(" = ")[1].strip()
                continue
            elif "NAME" in line:
                global_dict["NAME"] = line.split(" = ")[1].strip()
                continue

    return global_dict, tools, coordinates, requests