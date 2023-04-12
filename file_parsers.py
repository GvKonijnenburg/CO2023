import instances

def file_parser(inputfile):
    # "Global" Variables
    # days = None
    # capacity = None
    # MAX_TRIP_DISTANCE = None
    # DEPOT_COORDINATE = None
    # VEHICLE_COST = None
    # VEHICLE_DAY_COST = None
    # DISTANCE_COST = None
    global_dict = {}

    # "Local" Variables
    tools = []
    coordinates = []
    requests = []

    with open(inputfile, 'r') as f:
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
                    tool_type = next(f).split()
                    tools.append(
                    instances.Tool(id=int(tool_type[0]), weight=int(tool_type[1]),
                                   amount=int(tool_type[2]),cost=int(tool_type[3])))
                continue
            elif "COORDINATES" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    co_type = next(f).split()
                    coordinates.append(instances.Coordinates(id=int(co_type[0]), x_co=int(co_type[1]),
                                                             y_co=int(co_type[2])))
                continue

            elif "REQUESTS" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    req_type = next(f).strip().split()
                    requests.append(instances.Request(id=int(req_type[0]),locid=int(req_type[1]),
                                                      fromDay=int(req_type[2]),toDay=int(req_type[3]),
                                                      numDays=int(req_type[4]),toolid=int(req_type[5]),
                                                      toolCount=int(req_type[6])))
                continue

    return global_dict, tools, coordinates, requests