from dataclasses import dataclass
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def filter_requests(schedule, global_dict, local_dict):
    depot_coordinate = global_dict['DEPOT_COORDINATE']
    day = local_dict['day']
    tool = local_dict['tool']
    #filters demand for a given day and tooltype
    returnvalue = []
    i = 0
    returnvalue.append(i)

    in_use = 0
        
    for request in range(len(schedule)):
        if schedule[request][4] == tool:
        # Deliveries
            if (schedule[request][2] == day):
                i += 1
            
                location = schedule[request][1]
                tool_count = schedule[request][5]

                returnvalue.append(
                        (i, location, request, tool_count)
                    )
            elif (schedule[request][2] < day):
                in_use += schedule[request][5]
            # Pickup
            if ((schedule[request][3] == day)):
                i += 1
            
                location = schedule[request][1]
                tool_count = schedule[request][5]

                returnvalue.append(
                        (i, location, request, -tool_count)
                    )
            elif (schedule[request][2] < day):
                in_use -= schedule[request][5]

    returnvalue[0] = (0, depot_coordinate, 0, 0)
    return returnvalue, in_use

def create_data_model(global_dict, local_dict):
    data = {}
    data['dataset'] = global_dict['DATASET']
    data['name'] = global_dict['NAME']
    data['schedule'] = local_dict['schedule']

    requests = []
    for i in range(len(data['schedule'])):
        requests.append(-data['schedule'][i][3])

    data['requests'] = requests
    data['tool_costs'] = local_dict['tool_costs']
    data['tools_used'] = local_dict['tools_used']
    data['distance_cost'] = global_dict['DISTANCE_COST']
    data['distance_matrix'] = local_dict['distance_matrix']
    data['num_vehicles'] = local_dict['num_vehicles']
    data['depot'] = 0 # in the filter we set the depot index to 0
    data['vehicle_capacity'] = global_dict['CAPACITY']
    data['vehicle_day_cost'] = global_dict['VEHICLE_DAY_COST']
    data['vehicle_cost'] = global_dict['VEHICLE_COST']
    data['max_trip'] = global_dict['MAX_TRIP_DISTANCE']

    inventory_depot = local_dict['bought_tool'] - local_dict['tools_at_farms']
    data['inventory'] = [inventory_depot] + [0] * (len(data['schedule']) - 1)
    
    return data

def node_to_loc(schedule, node):
    return schedule[node][1] 

def node_to_req(schedule, node):
    return schedule[node][2] 

def sign_positive(number):
    """For convienience return true for 0"""
    return(number >= 0)

def store_solution(data, manager, routing, solution):
    """Stores routes in array"""
    returnvalue = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_cost = 0
        vehicle_route = [0]

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            
            request = node_to_req(data['schedule'], node_index)

            if sign_positive(data['requests'][node_index]):
                vehicle_route.append(-request)
            else:
                vehicle_route.append(request)
                        
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_cost += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                  
        if route_cost > 0:
            vehicle_route[0] = int(route_cost / data['distance_cost'])
            vehicle_route.append(node_to_req(data['schedule'], 0))
            returnvalue.append(vehicle_route)
    
    return returnvalue

def solver(data):
    """Solve the problem."""
    
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['schedule']),
                                           data['num_vehicles'], 
                                           data['depot'])

   # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit distance callback
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Create and register a transit cost callback
    def distance_cost_callback(from_index, to_index):
        distance = distance_callback(from_index, to_index)
        return distance * data['distance_cost']

    transit_cost_callback_index = routing.RegisterTransitCallback(distance_cost_callback)

    previous_inventory = []

    def request_callback(from_index):  
        """Returns the nr of items to pickup at the node."""  
        from_node = manager.IndexToNode(from_index)  
        if from_node == data['depot']:  
            inventory = data['inventory'][:]  
            previous_inventory[:] = inventory  
        else:  
            inventory = previous_inventory[:]  
        demand = data['requests'][from_node]  
        if demand > 0:  
            inventory[from_node] += demand  
        else:  
            inventory[from_node] += demand  
            demand = max(0, -inventory[from_node])  
            inventory[from_node] -= demand  
        previous_inventory[:] = inventory  
        return demand 


    request_callback_index = routing.RegisterUnaryTransitCallback(request_callback)
    routing.AddDimension(
        request_callback_index,
        0,  # null capacity slack
        data['vehicle_capacity'],  # vehicle maximum capacities
        False,  # start cumul to zero
        'Capacity')
    
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cost_callback_index)
    #routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        data['max_trip'], #data['max_trip'],  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    #distance_dimension = routing.GetDimensionOrDie(dimension_name)
    #distance_dimension.SetGlobalSpanCostCoefficient(1000)

    # Add Fixed cost per vehicle used.
    #routing.SetFixedCostOfAllVehicles(data['vehicle_day_cost'])

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
    search_parameters.use_full_propagation = True

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        #print_solution(data, manager, routing, solution)
        return store_solution(data, manager, routing, solution)
    else:
        print('No solution found !')
    
    return solution

def generate_output(data, result, debug = False):
    body = '' 
    distance = 0
    vehicles = 0
    vehicle_days = 0
    
    for day_idx, day in enumerate(result):
        body += '\nDAY = {}\n'.format(day_idx + 1)
        vehicles_day =  len(day)
        vehicles = max(vehicles, vehicles_day)

        body += 'NUMBER_OF_VEHICLES = {}\n'.format(vehicles_day)
        vehicle_days += vehicles_day

        for vehicle_idx, vehicle in enumerate(day):
            distance += vehicle[0]

            body += '{} R'.format(vehicle_idx + 1)
            for stop in range(1, len(vehicle)):
                body += ' {}'.format(vehicle[stop])
            body += '\n'       
        
    'Calculate costs'
    cost = data['tool_costs'] 
    cost += data['vehicle_cost'] * vehicles
    cost += data['vehicle_day_cost'] * vehicle_days 
    cost += data['distance_cost'] * distance

    returnvalue = 'DATASET = ' + data['dataset'] + '\n'
    returnvalue += 'NAME = ' + data['name'] + '\n\n'
    returnvalue += 'MAX_NUMBER_OF_VEHICLES = {}\n'.format(vehicles)
    returnvalue += 'NUMBER_OF_VEHICLE_DAYS = {}\n'.format(vehicle_days)
    returnvalue += 'TOOL_USE = '

    for i, tool_used in enumerate(data['tools_used']):
        returnvalue +=' {}'.format(tool_used)
            
    returnvalue += '\nDISTANCE = {}\n'.format(distance)
    returnvalue += 'COST = {}\n'.format(cost)
    returnvalue += body

    return returnvalue

def main(global_dict, distance_matrix, schedule, scheduled_tools, print_output = False):
    local_dict = {}
    local_dict['distance_matrix'] = distance_matrix
    
    tools_used = []
    tool_costs = 0
    for tool in range(len(scheduled_tools)):
        tool_bought = scheduled_tools[tool][1]
        tools_used.append(tool_bought)
        tool_costs += tool_costs * scheduled_tools[tool][3]
        
    local_dict['tools_used'] = tools_used
    local_dict['tool_costs'] = tool_costs

    result = []

    for day in range(1, global_dict['DAYS']+1):
        #print('DAY {}'.format(day))
        
        local_dict['day'] = day
        day_result = []

        for tool in range(len(scheduled_tools)):
            #print('TOOL_INDEX {}'.format(tool))    
            local_dict['tool'] = scheduled_tools[tool][0]
            local_dict['tool_size'] = scheduled_tools[tool][4]
            local_dict['bought_tool'] = tools_used[tool]
        
            dayschedule, tools_at_farms = filter_requests(schedule, global_dict, local_dict)
   
            local_dict['schedule'] = dayschedule
            local_dict['tools_at_farms'] = tools_at_farms
            local_dict['num_vehicles'] = len(dayschedule)
    
            datamodel = create_data_model(global_dict, local_dict)
            day_result += solver(datamodel)
        
        result.append(day_result)

    #geberate output
    output = generate_output(datamodel, result)
    
    #save
    text_file = open("output.txt", "w")
    text_file.write(output)
    text_file.close()
    
    if print_output:
        print(output)