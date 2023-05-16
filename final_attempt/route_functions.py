import vehicle_functions
import order_functions
import distance_functions
import delivery_only_algorithm
import depot_functions

#### Functions relevant for with and w/o pick_ups.
def dispatch_vehicle(vehicle_i, vehicle_j,new_distance, vehicle_current_load, loc_i, loc_j,distance_cost):
    v_id = vehicle_i.v_id
    vehicle_operation_cost = vehicle_i.vehicle_operation_cost
    tools_in_vehicle = vehicle_functions.update_tools_in_vehicle([vehicle_i,vehicle_j])
    new_route = [0,loc_i,loc_j,0]
    request_fullfilled = vehicle_i.request_fullfilled+vehicle_j.request_fullfilled
    new_vehicle = vehicle_functions.init_vehicle(v_id,new_distance,vehicle_current_load,new_route,request_fullfilled,
                 tools_in_vehicle,distance_cost,vehicle_operation_cost)
    new_delivered_tools,new_pick_up_tools = vehicle_functions.update_pd_delvehicle(vehicle_i,vehicle_j)
    new_vehicle.tools_delivered.update(new_delivered_tools)
    new_vehicle.tools_delivered.update(new_pick_up_tools)
    return new_vehicle
def extend_route_merger(vehicle_i, vehicle_j,new_distance,new_load,distance_cost):
    v_id = vehicle_i.v_id
    operation_cost = vehicle_i.vehicle_operation_cost
    tools_in_vehicle = vehicle_functions.update_tools_in_vehicle([vehicle_i, vehicle_j])
    request_fullfilled = vehicle_i.request_fullfilled + vehicle_j.request_fullfilled
    new_route = vehicle_i.farms_visited[:-1] + vehicle_j.farms_visited[1:]
    new_vehicle = vehicle_functions.init_vehicle(v_id, new_distance, new_load, new_route,request_fullfilled,
                                                 tools_in_vehicle, distance_cost, operation_cost)
    return new_vehicle
def can_a_large_pick_up_and_large_delivery_be_combined(large_order_list,updated_order_list,max_distance,distance_matrix,depot,vehicle_operation_cost,distance_cost):
    order_list_to_combine = order_functions.get_best_combinations(large_order_list,distance_matrix)
    order_ids_fullfilled= []
    new_vehicle_list = []
    large_delivery_list = []
    for delivery, pickup in order_list_to_combine:
        pickup_loc = pickup[2]
        delivery_loc = delivery[2]
        distance_between_points = distance_functions.calculate_distance_between_points(distance_matrix, delivery_loc, pickup_loc)
        distance_pick_up_to_depot = distance_functions.calculate_distance_between_points(distance_matrix, depot.loc, pickup_loc)
        distance_delivery_to_depot = distance_functions.calculate_distance_between_points(distance_matrix, depot.loc, delivery_loc)
        new_distance = distance_pick_up_to_depot + distance_between_points + distance_delivery_to_depot
        if new_distance <= max_distance:
            v_id = pickup[1]
            tool_id_pick_up = pickup[5]
            tool_count_pick_up = pickup[6]
            tool_id_delivery = delivery[5]
            tool_count_delivery = delivery[6]
            distance_traveled = new_distance
            tools_in_vehicle = {}
            tools_in_vehicle[tool_id_pick_up] = tools_in_vehicle.get(tool_id_pick_up, 0) + tool_count_pick_up
            tools_in_vehicle[tool_id_delivery] = tools_in_vehicle.get(tool_id_delivery, 0) + tool_count_delivery
            vehicle_load = sum(depot.tools[tool_id].size * tool_count for tool_id, tool_count in tools_in_vehicle.items())
            vehicle_route = [depot.loc, pickup[2],delivery[2], depot.loc]
            request_fullfilled = [pickup[-1],delivery[-1]]
            vehicle_operation_cost = vehicle_operation_cost
            new_vehicle = vehicle_functions.init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route, request_fullfilled,
                             tools_in_vehicle, distance_cost, vehicle_operation_cost)
            new_vehicle.large_pick_ups()
            new_vehicle_list.append(new_vehicle)
            order_ids_fullfilled.append(pickup[-1])
            order_ids_fullfilled.append(delivery[-1])
        else:
            print('if initial distance to high implement or else all the large request are fullfilled ')

    orders_left_to_complete = updated_order_list[~updated_order_list['order_id'].isin(order_ids_fullfilled)]
    large_orders_left = large_order_list[~large_order_list['order_id'].isin(order_ids_fullfilled)]
    large_deliveries_left = large_orders_left[large_orders_left['order_type'] == 'D']
    large_pick_ups_left = large_orders_left[large_orders_left['order_type'] == 'P']
    # if len(large_deliveries_left) >0:
    #     large_delivery_list,depot = delivery_only_algorithm.initial_delivery_routes(large_deliveries_left, depot, distance_cost, vehicle_operation_cost)
    # if len(large_pick_ups_left)>0:
    #     for order in large_pick_ups_left.itertuples():
    #         tool_id = order[6]
    #         amount_requested = order[7]
    #         v_id = order[1]
    #         distance_traveled = order[-2]
    #         vehicle_load = order[-3]
    #         vehicle_route = [depot.loc, order[3], depot.loc]
    #         request_fullfilled = [order[-1]]
    #         tools_in_vehicle = {tool_id: amount_requested}
    #         vehicle_i = vehicle_functions.init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route,
    #                                                        request_fullfilled, tools_in_vehicle, distance_cost,
    #                                                        vehicle_operation_cost)
    #         vehicle_i.pick_up_tools(tool_id, amount_requested)
    #         new_vehicle_list.append(vehicle_i)
    return new_vehicle_list,large_delivery_list,depot,orders_left_to_complete

#### Only Deliveries
def can_first_day_deliveries_be_merged(vehicle_i,vehicle_j,distance_matrix,loc_i,loc_j,max_capacity,max_distance):
    vehicle_i_current_load = vehicle_i.vehicle_current_load
    vehicle_j_current_load = vehicle_j.vehicle_current_load
    new_vehicle_load = vehicle_i_current_load + vehicle_j_current_load
    if new_vehicle_load > max_capacity:
        return False, None, None
    distance_traveled_i = distance_matrix[0][loc_i]
    distance_traveled_j = distance_matrix[0][loc_j]
    distance_between_farms = distance_matrix[loc_i][loc_j]
    new_distance = distance_traveled_i + distance_traveled_j + distance_between_farms
    if new_distance > max_distance:
        return False,None,None
    return True, new_distance, new_vehicle_load
def can_a_delivery_be_added_on_the_first_day(vehicle_i, vehicle_j, distance_matrix, max_capacity, max_trip_distance, depot):
    vehicle_capacity_after_merge = vehicle_i.vehicle_current_load + vehicle_j.vehicle_current_load
    if vehicle_capacity_after_merge > max_capacity:
        return False,None,None,None
    loc_i_locations = vehicle_i.farms_visited[1:-1]
    loc_j_locations = vehicle_j.farms_visited[1:-1]
    merged_points = loc_i_locations + loc_j_locations
    merged_points.insert(0,depot.loc)
    merged_points.insert(len(merged_points),depot.loc)
    new_distance = 0
    for i in range(len(merged_points)-1):
        current = merged_points[i]
        next = merged_points[i + 1]
        new_distance += distance_matrix[current][next]
    if new_distance > max_trip_distance:
        return False,None,None,None


    return True, new_distance,vehicle_capacity_after_merge,merged_points

###### Only pick_ups:
def can_two_routes_be_merged(vehicle_i,vehicle_j,distance_matrix,loc_i,loc_j,max_capacity,max_distance,depot):
    new_tools_in_vehicle = vehicle_functions.merge_tools_in_vehicle(vehicle_i,vehicle_j)
    new_vehicle_load = vehicle_functions.calculate_vehicle_load(new_tools_in_vehicle,depot)
    if new_vehicle_load > max_capacity:
        return False, None, None,None
    if not depot_functions.check_inventory(depot,new_tools_in_vehicle):
        return False,None,None,None
    distance_traveled_i = distance_matrix[0][loc_i]
    distance_traveled_j = distance_matrix[0][loc_j]
    distance_between_farms = distance_matrix[loc_i][loc_j]
    new_distance = distance_traveled_i + distance_traveled_j + distance_between_farms
    if new_distance > max_distance:
        return False,None,None,None
    return True, new_distance, new_vehicle_load,new_tools_in_vehicle
def dispatch_vehicle_pd(vehicle_i, vehicle_j,new_distance, vehicle_current_load, loc_i, loc_j,distance_cost,tools_in_vehicle,depot):
    v_id = vehicle_i.v_id
    vehicle_operation_cost = vehicle_i.vehicle_operation_cost
    new_route = [0,loc_i,loc_j,0]
    request_fullfilled = vehicle_i.request_fullfilled+vehicle_j.request_fullfilled
    new_vehicle = vehicle_functions.init_vehicle(v_id,new_distance,vehicle_current_load,new_route,request_fullfilled,
                 tools_in_vehicle,distance_cost,vehicle_operation_cost)
    depot_functions.process_tools(depot, tools_in_vehicle)
    return new_vehicle,depot

def can_we_add_a_location(vehicle_i, vehicle_j, distance_matrix,max_capacity, max_trip_distance, depot):
    new_tools_in_vehicle = vehicle_functions.merge_tools_in_vehicle(vehicle_i,vehicle_j)
    new_vehicle_load = vehicle_functions.calculate_vehicle_load(new_tools_in_vehicle,depot)
    if new_vehicle_load > max_capacity:
        return False,None,None,None,None
    if not depot_functions.check_inventory(depot,new_tools_in_vehicle):
        return False,None,None,None,None
    loc_i_locations = vehicle_i.farms_visited[1:-1]
    loc_j_locations = vehicle_j.farms_visited[1:-1]
    merged_points = loc_i_locations + loc_j_locations
    merged_points.insert(0,depot.loc)
    merged_points.insert(len(merged_points),depot.loc)
    new_distance = 0
    for i in range(len(merged_points)-1):
        current = merged_points[i]
        next = merged_points[i + 1]
        new_distance += distance_matrix[current][next]
    if new_distance > max_trip_distance:
        return False,None,None,None,None
    if new_vehicle_load <= max_capacity and new_distance <=max_trip_distance and depot_functions.check_inventory(depot,new_tools_in_vehicle):
        return True, new_distance,new_vehicle_load,merged_points,new_tools_in_vehicle

def extend_route_merger_pd(vehicle_i, vehicle_j,new_distance,new_load,distance_cost,tools_in_vehicle,depot,new_vehicle_route):
    v_id = vehicle_i.v_id
    operation_cost = vehicle_i.vehicle_operation_cost
    request_fullfilled = vehicle_i.request_fullfilled + vehicle_j.request_fullfilled
    new_vehicle = vehicle_functions.init_vehicle(v_id, new_distance, new_load, new_vehicle_route,request_fullfilled,
                                                 tools_in_vehicle, distance_cost, operation_cost)
    depot_functions.process_tools(depot, tools_in_vehicle)
    return new_vehicle,depot

#### Other Relevant Functions
def is_it_word_merging_routes(vehicle_i, vehicle_j, new_vehicle):
    combined_cost = vehicle_i.route_cost + vehicle_j.route_cost
    if combined_cost > new_vehicle.route_cost:
        return True
    else:
        return False

