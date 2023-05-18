import distance_functions
import vehicle_functions
import pandas as pd
def flatten_list(my_list):
	returnvalue = []
	for i in range(len(my_list)):
		if isinstance(my_list[i], list):
			returnvalue += (flatten_list(my_list[i]))
		else:
			returnvalue.append(my_list[i])
	return returnvalue

def check_arcs(vehicle_i,vehicle_j,depot):
    order_list = [vehicle_i.order_history] + [vehicle_j.order_history]
    request_problem_because_we_cant_track_farms = [item for sublist in order_list for item in(sublist if isinstance(sublist, list) else [sublist])]
    request_problem_because_we_cant_track_farms = flatten_list(request_problem_because_we_cant_track_farms)
    tool_needed = {}
    vehicle_load_tracker = 0

    for i in range(len(request_problem_because_we_cant_track_farms) - 1):
        visit_1 = request_problem_because_we_cant_track_farms[i]
        visit_2 = request_problem_because_we_cant_track_farms[i + 1]
        tool_type_v1 = visit_1[1]
        tool_type_v2 = visit_2[1]
        tool_amount_v1 = visit_1[2]
        tool_amount_v2 = visit_2[2]
        tool_type_v1_size = depot.tools[tool_type_v1].size
        tool_type_v2_size = depot.tools[tool_type_v2].size
        
        if tool_type_v1 == tool_type_v2:
            if tool_amount_v1 < 0 and tool_type_v2 > 0:
                difference = tool_amount_v1 + tool_amount_v2
                if tool_type_v1 in tool_needed:
                    vehicle_load_tracker += abs(difference * tool_type_v1_size)
                    tool_needed[tool_type_v1] += difference
                else:
                    tool_needed[tool_type_v1] = difference
                    vehicle_load_tracker += abs(difference * tool_type_v1_size)

        if tool_type_v1 in tool_needed:
            tool_needed[tool_type_v1] += tool_amount_v1
            vehicle_load_tracker += abs(tool_amount_v1 * tool_type_v1_size)
        else:
            tool_needed[tool_type_v1] = tool_amount_v1
            vehicle_load_tracker += abs(tool_amount_v1 * tool_type_v1_size)
        
        if tool_type_v2 in tool_needed:
            tool_needed[tool_type_v2] += tool_amount_v2
            vehicle_load_tracker += abs(tool_amount_v2 * tool_type_v2_size)
        else:
            tool_needed[tool_type_v2] = tool_amount_v2
            vehicle_load_tracker += abs(tool_amount_v2 * tool_type_v2_size)
    return tool_needed, vehicle_load_tracker, order_list



def can_two_deliveries_be_merged(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, max_capacity, max_distance):
    vehicle_i_current_load = vehicle_i.vehicle_cumalative_load
    vehicle_j_current_load = vehicle_j.vehicle_cumalative_load
    new_vehicle_load = vehicle_i_current_load + vehicle_j_current_load
    if new_vehicle_load > max_capacity:
        return False, None, None
    distance_traveled_i = distance_matrix[0][loc_i]
    distance_traveled_j = distance_matrix[0][loc_j]
    distance_between_farms = distance_matrix[loc_i][loc_j]
    new_distance = distance_traveled_i + distance_traveled_j + distance_between_farms
    if new_distance > max_distance:
        return False, None, None
    return True, new_distance, new_vehicle_load
def can_two_request_become_one(vehicle_i, vehicle_j, vehicle_capacity):
    vehicle_i_current_load = vehicle_i.vehicle_cumalative_load
    vehicle_j_current_load = vehicle_j.vehicle_cumalative_load
    new_vehicle_load = vehicle_i_current_load + vehicle_j_current_load ### Maybe later add this to vehicle_functions
    
    if new_vehicle_load > vehicle_capacity:
        return False,None
    else:
        return True,new_vehicle_load

def can_delivery_be_added_to_existing_route(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, vehicle_capacity,
                                            max_trip_distance, merge_type, depot):
    vehicle_capacity_after_merge = vehicle_i.vehicle_cumalative_load + vehicle_j.vehicle_cumalative_load
    if vehicle_capacity_after_merge > vehicle_capacity:
        return False, None, None, None
    if merge_type == "3bi":
        locations_to_add = vehicle_j.farms_visited[1:-2]
        index_i = vehicle_i.farms_visited.index(loc_i)
        vehicle_i.farms_visited.insert(index_i + 1, locations_to_add)
        new_route = vehicle_i.farms_visited
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix, new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None
        else:
            return True, new_distance, vehicle_capacity_after_merge, new_route
    if merge_type == "3bj":
        locations_to_add = vehicle_i.farms_visited[1:-2]
        index_j = vehicle_j.farms_visited.index(loc_j)
        vehicle_j.farms_visited.insert(index_j - 1, locations_to_add)
        new_route = vehicle_j.farms_visited
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix, new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None
        else:
            return True, new_distance, vehicle_capacity_after_merge, new_route

    if merge_type == "2B":
        new_distance, new_route = distance_functions.calculate_distance_between_farms(distance_matrix, vehicle_i,
                                                                                       vehicle_j, depot)

        if new_distance > max_trip_distance:
            return False, None, None, None
        else:
            return True, new_distance, vehicle_capacity_after_merge, new_route
    if merge_type == '3both':
        vehicle_i_current_load = vehicle_i.vehicle_current_load
        vehicle_j_current_load = vehicle_j.vehicle_current_load
        new_vehicle_load = vehicle_i_current_load + vehicle_j_current_load
        if new_vehicle_load > vehicle_capacity:
            return False, None, None

        locations_to_add_i = vehicle_j.farms_visited[:-2]
        locations_to_add_j = vehicle_j.farms_visited[1:]
        new_route = locations_to_add_i + locations_to_add_j
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix,new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None
        else:
            return True, new_distance, vehicle_capacity_after_merge, new_route
def can_a_pick_up_and_delivery_be_paired(vehicle_i, vehicle_j, vehicle_capacity,max_distance,depot,daily_order_data_frame,distance_matrix,master_depot):
    requests_instead_of_farms = []
    for vehicle in [vehicle_i, vehicle_j]:
        requests_instead_of_farms.append(vehicle.tools_in_vehicle)
    max_amount_of_tools_required = get_max_positive_change(requests_instead_of_farms)
    extra_load = 0
    if len(max_amount_of_tools_required) > 0:
        for tool_id, tool_amount in max_amount_of_tools_required.items():
            if tool_id in depot.tools:
                tool_size = depot.tools[tool_id].size
                extra_load += tool_size*tool_amount
    tool_needed,vehicle_load_tracker,order_list = check_arcs(vehicle_i,vehicle_j,depot)
    if vehicle_load_tracker > vehicle_capacity:
        return False,None,None
    distance_traveled_i = distance_matrix[0][vehicle_i.farms_visited[1]]
    distance_traveled_j = distance_matrix[0][vehicle_j.farms_visited[1]]
    distance_between_farms = distance_matrix[vehicle_i.farms_visited[1]][vehicle_j.farms_visited[1]]
    new_distance = distance_traveled_i + distance_traveled_j + distance_between_farms
    if new_distance > max_distance:
        return False, None,None
    new_tools_in_vehicle = vehicle_functions.update_tools_in_vehicle([vehicle_i,vehicle_j])
    for tool_id, amount_requested in new_tools_in_vehicle.items():
        if not master_depot.inventory_check(tool_id, amount_requested):
            return False, None,None
    return True, new_distance,new_tools_in_vehicle

def initial_dispatch_checker(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j,
                                                 vehicle_capacity,max_trip_distance,depot,daily_order_list):
    order_list = [vehicle_i.order_history] +[vehicle_j.order_history]
    request_problem_because_we_cant_track_farms = [item for sublist in order_list for item in (sublist if isinstance(sublist, list) else [sublist])]
    tool_needed = {}
    vehicle_load_tracker = 0
    tool_needed, vehicle_load_tracker, order_list = check_arcs(vehicle_i, vehicle_j, depot)
    if vehicle_load_tracker > vehicle_capacity:
        return False, None, None,None,None
    distance_traveled_i = distance_matrix[0][vehicle_i.farms_visited[1]]
    distance_traveled_j = distance_matrix[0][vehicle_j.farms_visited[1]]
    distance_between_farms = distance_matrix[vehicle_i.farms_visited[1]][vehicle_j.farms_visited[1]]
    new_distance = distance_traveled_i + distance_traveled_j + distance_between_farms
    if new_distance > max_trip_distance:
        return False, None, None,None,None
    new_tools_in_vehicle = vehicle_functions.update_tools_in_vehicle([vehicle_i, vehicle_j])
    # ISSUE HERE: we do not check if the new_tools_in_vehicle is over capacity

    for tool_id, amount_requested in new_tools_in_vehicle.items():
        if not depot.inventory_check(tool_id, amount_requested):
            return False, None, None,None,None
    return True,new_distance,vehicle_load_tracker,new_tools_in_vehicle,order_list

def pd_exted_route_checker(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, vehicle_capacity,
                                            max_trip_distance, merge_type, depot):
    tools_needed,vehicle_capacity_after_merge,order_history = check_arcs(vehicle_i,vehicle_j,depot)
    if vehicle_capacity_after_merge > vehicle_capacity:
        return False, None, None, None,None
    if merge_type == "3bi":
        locations_to_add = vehicle_j.farms_visited[1:-2]
        index_i = vehicle_i.farms_visited.index(loc_i)
        vehicle_i.farms_visited.insert(index_i + 1, locations_to_add)
        new_route = vehicle_i.farms_visited
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix, new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None,None
        else:
            for tool_id, amount_requested in tools_needed.items():
                if not depot.inventory_check(tool_id, amount_requested):
                    return False, None, None,None,None
                depot.tool_reserved_for_delivery(tool_id)
            return True, new_distance, vehicle_capacity_after_merge, new_route.order,order_history
    if merge_type == "3bj":
        locations_to_add = vehicle_i.farms_visited[1:-2]
        index_j = vehicle_j.farms_visited.index(loc_j)
        vehicle_j.farms_visited.insert(index_j - 1, locations_to_add)
        new_route = vehicle_j.farms_visited
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix, new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None,None
        else:
            for tool_id, amount_requested in tools_needed.items():
                if not depot.inventory_check(tool_id, amount_requested):
                    return False, None, None,None,None
                depot.tool_reserved_for_delivery(tool_id)
            return True, new_distance, vehicle_capacity_after_merge, new_route,order_history
    if merge_type == "2B":
        new_distance, new_route = distance_functions.calculate_distance_between_farms(distance_matrix, vehicle_i,
                                                                                       vehicle_j, depot)
        if new_distance > max_trip_distance:
            return False, None, None, None,None
        else:
            return True, new_distance, vehicle_capacity_after_merge, new_route,order_history
    if merge_type == '3both':
        vehicle_i_current_load = vehicle_i.vehicle_current_load
        vehicle_j_current_load = vehicle_j.vehicle_current_load
        new_vehicle_load = vehicle_i_current_load + vehicle_j_current_load
        if new_vehicle_load > vehicle_capacity:
            return False, None, None,None,None
        locations_to_add_i = vehicle_j.farms_visited[:-2]
        locations_to_add_j = vehicle_j.farms_visited[1:]
        new_route = locations_to_add_i + locations_to_add_j
        new_distance = distance_functions.calculate_distance_between_vehicles(distance_matrix,new_route)
        if new_distance > max_trip_distance:
            return False, None, None, None,None
        else:
            for tool_id, amount_requested in tools_needed.items():
                if not depot.inventory_check(tool_id, amount_requested):
                    return False, None, None,None,None
                depot.tool_reserved_for_delivery(tool_id)
            return True, new_distance, vehicle_capacity_after_merge, new_route,order_history
def get_max_positive_change(amount_requested):
    totals = {}
    max_totals = {}
    for d in amount_requested:
        for key, value in d.items():
            totals[key] = totals.get(key, 0) + value
            if totals[key] > max_totals.get(key, 0):
                max_totals[key] = totals[key]
    return max_totals



