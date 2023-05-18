from itertools import combinations

import delivery_only_algorithm
import routing_functions
import vehicle_functions
import constraint_checkers
import distance_functions
def vehicle_locator(vehicle_list,loc_i,loc_j):
    vehicle_i,vehicle_j = None,None
    for vehicle in vehicle_list:
        if vehicle.farms_visited[1]==loc_i:
            vehicle_i = vehicle
        if vehicle.farms_visited[-2]==loc_j:
            vehicle_j = vehicle
        if vehicle_i and vehicle_j is not None:
            break
    return vehicle_i,vehicle_j
def dispatched_vehicle_locator(dispatch_list,farm):
    for vehicle in dispatch_list:
        if farm in vehicle.farms_visited:
            return vehicle

def compute_savings_matrix(distance_matrix, vehicle_list,distance_cost):
    savings_list = []
    locations_to_visit = list(set([vehicle.farms_visited[1] for vehicle in vehicle_list]))
    location_pairs = list(combinations(locations_to_visit, 2))
    for pair in location_pairs:
        loc_i = pair[0]
        loc_j = pair[1]
        vehicle_i = next(vehicle for vehicle in vehicle_list if vehicle.farms_visited[1] == loc_i)
        vehicle_j = next(vehicle for vehicle in vehicle_list if vehicle.farms_visited[1] == loc_j)
        tools_i = vehicle_i.tools_in_vehicle
        tools_j = vehicle_j.tools_in_vehicle
        k = 1
        if any(value < 0 for value in tools_i.values()):
            k = 1.25
        for tool_id, v_i_amount in tools_i.items():
            v_j_amount = tools_j.get(tool_id, 0)
            if v_i_amount != 0 and v_j_amount != 0:
                k = 1.5
                if (v_i_amount > 0 and v_j_amount < 0) or (v_i_amount < 0 and v_j_amount > 0):
                    k = 2
                    if v_i_amount + v_j_amount < 0:
                        k = 2.5
        savings = (k * (distance_matrix[0][loc_i] + distance_matrix[0][loc_j] -
                                   distance_matrix[loc_i][loc_j]) )*distance_cost
        savings_list.append((loc_i, loc_j, savings))
    savings_list.sort(key=lambda x: x[2], reverse=True)
    savings_cutoff = savings_list[len(savings_list) // 2][2]
    cut_off_pairs = [(loc_i, loc_j, savings) for loc_i, loc_j, savings in savings_list if savings >= savings_cutoff]
    return cut_off_pairs


def inventory_savings_by_combining_large_pd_del_request(vehicle_list, distance_matrix, depot):
    tool_types = {tool_id: [] for tool_id in depot.tools.keys()}
    for vehicle in vehicle_list:
        for tool_type, amount_requested in vehicle.tools_in_vehicle.items():
            if amount_requested < 0:
                tool_types[tool_type].append((vehicle, 'P'))
            elif amount_requested > 0:
                tool_types[tool_type].append((vehicle, 'D'))
    best_pairs = []
    for tool_type, vehicles in tool_types.items():
        pickups = [v for v in vehicles if v[1] == 'P']
        deliveries = [v for v in vehicles if v[1] == 'D']
        for p in pickups:
            for d in deliveries:
                distance = distance_functions.calculate_distance_between_points(distance_matrix, p[0].farms_visited[1], d[0].farms_visited[1])
                savings = -distance
                best_pairs.append((savings, (p[0], d[0])))
    best_pairs.sort(reverse=True)
    best_pairs = [pair for _, pair in best_pairs]
    return best_pairs

def savings_algo(order_vehicle_information, distance_matrix, init_depot, vehicle_capacity, max_trip_distance,
                                     vehicle_operation_cost,distance_cost,scheduled_request):
    init_depot.start_new_day()
    master_order_list = order_vehicle_information
    requests_for_day_one = scheduled_request[1]
    final_vehicles = {}
    init_depot.start_new_day()
    # Day 1 Has its own function due to the fact that there are only deliveries. Therefore, there are less checks to do.
    orders_for_day_one = master_order_list[master_order_list['route_id'].isin(requests_for_day_one)]
    routes_for_day_one,master_depot,smallest_tool = delivery_only_algorithm.first_day_algo(orders_for_day_one,init_depot,distance_cost,
        vehicle_operation_cost,vehicle_capacity,distance_matrix,max_trip_distance)
    final_vehicles[1] = routes_for_day_one
    for day in range(2, max(master_order_list['order_day']) + 1):
        master_depot.start_new_day()
        print(master_depot)
        daily_requests = scheduled_request[day]
        daily_orders_to_complete = master_order_list[master_order_list['route_id'].isin(daily_requests)]
        initial_routes = routing_functions.initial_pick_up_and_delivery_routes(daily_orders_to_complete, master_depot,distance_cost,vehicle_operation_cost)
        multi_request_routes = vehicle_functions.multi_request_vehicles(initial_routes)
        multi_request_vehicles = {}
        if len(multi_request_routes) > 0:
            for vehicle in multi_request_routes:
                farm_location = vehicle.farms_visited[1]
                if farm_location in multi_request_vehicles:
                    multi_request_vehicles[farm_location].append(vehicle)
                else:
                    multi_request_vehicles[farm_location] = [vehicle]
            for farm, matching_vehicles in multi_request_vehicles.items():
                for i in range(len(matching_vehicles) - 1): ### Probable redundand code, if a triple never occurs
                    vehicle_i = matching_vehicles[i]
                    for j in range(i + 1, len(matching_vehicles)):
                        vehicle_j= matching_vehicles[j]
                        can_these_two_be_merged,new_vehicle_load = constraint_checkers.can_two_request_become_one(vehicle_i, vehicle_j, vehicle_capacity)
                        if can_these_two_be_merged:
                            new_vehicle = routing_functions.dispatch_vehicle(vehicle_i, vehicle_j,vehicle_i.distance_traveled,
                                                                             new_vehicle_load, vehicle_i.farms_visited,distance_cost)
                            initial_routes.remove(vehicle_i)
                            initial_routes.remove(vehicle_j)
                            initial_routes.append(new_vehicle) # if there duplicates in solution check here first.

        vehicle_list, large_requests, smallest_tool = vehicle_functions.large_vehicles(initial_routes, init_depot,
                                                                                       vehicle_capacity)
        pick_up_and_delivery_combinations_to_merge = inventory_savings_by_combining_large_pd_del_request(large_requests,distance_matrix,master_depot)
        already_paired = []
        too_large_to_be_combined = []
        for pair in pick_up_and_delivery_combinations_to_merge:
            pick_up,delivery = pair[0],pair[1]
            can_delivery_and_pick_up_be_merged,new_distance,new_tools_in_vehicle  = constraint_checkers.can_a_pick_up_and_delivery_be_paired(pick_up, delivery, vehicle_capacity,max_trip_distance,master_depot,daily_orders_to_complete,distance_matrix, master_depot)
            if can_delivery_and_pick_up_be_merged:
                new_route = [master_depot.loc,pick_up.farms_visited[1], delivery.farms_visited[1],master_depot.loc]
                request_fullfilled = [pick_up.request_fullfilled] + [delivery.request_fullfilled]
                route_cost = new_distance*distance_cost
                order_list = pick_up.order_history+delivery.order_history
                new_vehicle = vehicle_functions.Vehicle(v_id=pick_up.v_id,distance_traveled=new_distance,vehicle_cumalative_load=0,
                                                        farms_visited=new_route,request_fullfilled=request_fullfilled,vehicle_operation_cost=pick_up.vehicle_operation_cost,route_cost=route_cost,
                                                        tools_in_vehicle=new_tools_in_vehicle, tools_picked_up={},tools_delivered={},order_history=order_list,load_history=pick_up.load_history)

                already_paired.append(new_vehicle)
                large_requests.remove(pick_up)
                large_requests.remove(delivery)
                for tool_id, amount_requested in new_vehicle.tools_in_vehicle.items():
                    master_depot.tool_reserved_for_delivery(tool_id, amount_requested)
        for vehicle in large_requests:
            if vehicle.request_fullfilled >0:
                too_large_to_be_combined.append(vehicle)
                for tool_id, amount_requested in vehicle.tools_in_vehicle.items():
                    master_depot.tool_reserved_for_delivery(tool_id, amount_requested)
            else:
                vehicle_list.append(vehicle)
        cut_off_pairs = compute_savings_matrix(distance_matrix, vehicle_list, distance_cost)
        dispatch_list = already_paired
        for pair in cut_off_pairs:
            loc_i, loc_j = pair[0], pair[1]
            vehicle_i, vehicle_j = vehicle_locator(vehicle_list, loc_i, loc_j)
            dispatched_i = dispatched_vehicle_locator(dispatch_list, loc_i)
            dispatched_j = dispatched_vehicle_locator(dispatch_list, loc_j)
            if vehicle_i is not None and vehicle_j is not None:
                if len(vehicle_i.farms_visited) == 3 and len(vehicle_j.farms_visited) == 3:  ### This is Case 3a from Step 2 in the link I send, because single routes only have length of 3's
                    can_pair_be_merged, new_distance,vehicle_load_tracker,new_tools_in_vehicle,order_list = constraint_checkers.initial_dispatch_checker(
                        vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, vehicle_capacity,
                        max_trip_distance,master_depot,daily_orders_to_complete)
                    if can_pair_be_merged:
                        new_route = [master_depot.loc,loc_i,loc_j,master_depot.loc]
                        new_vehicle = routing_functions.dispatch_vehicle_pd(vehicle_i, vehicle_j,new_distance, vehicle_load_tracker, new_route,distance_cost,new_tools_in_vehicle,master_depot)
                        vehicle_list.remove(vehicle_i)
                        vehicle_list.remove(vehicle_j)
                        linkage_requirement = vehicle_capacity - new_vehicle.vehicle_cumalative_load
                        existing_vehicle = delivery_only_algorithm.vehicle_with_sufficient_capacity_locator(dispatch_list,
                                                                                    linkage_requirement)
                        if existing_vehicle is not None:
                            can_pair_be_merged, long_distance, long_capacity, long_road,order_history = constraint_checkers.pd_exted_route_checker(
                                existing_vehicle, new_vehicle, distance_matrix, loc_i, loc_j, vehicle_capacity,max_trip_distance, '2B', init_depot)
                            if can_pair_be_merged:
                                linked_vehicle = routing_functions.dispatch_vehicle_pd(vehicle_i, vehicle_j,new_distance, vehicle_load_tracker, new_route,distance_cost,new_tools_in_vehicle,master_depot)
                                dispatch_list.append(linked_vehicle) # maybe double tools removed.
                        else:
                            dispatch_list.append(new_vehicle)
            if dispatched_i is not None and vehicle_j is not None:  ## 3b- with loc_i in an existing route
                if not delivery_only_algorithm.is_farm_next_to_depot(dispatched_i,loc_i):  # If time makes this faster since looping is inneffcient.
                    can_pair_be_merged, long_distance, long_capacity, long_road = constraint_checkers.pd_exted_route_checker(
                        vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j,
                        vehicle_capacity,
                        max_trip_distance, '3bi', init_depot)
                    if can_pair_be_merged:
                        linked_vehicle = routing_functions.dispatch_vehicle(dispatched_i, vehicle_j,
                                                                            long_distance,
                                                                            long_capacity,
                                                                            long_road, distance_cost)
                        dispatch_list.append(linked_vehicle)
            if dispatched_i is not None and dispatched_j is not None:  # 3c where both i and j have been included
                if dispatched_i.farms_visited[-2] == loc_i and dispatched_j.farms_visited == [1]:
                    can_pair_be_merged, long_distance, long_capacity, long_road = constraint_checkers.can_delivery_be_added_to_existing_route(
                        vehicle_i, dispatched_j, distance_matrix, loc_i, loc_j, vehicle_capacity,
                        max_trip_distance, '3both',
                        init_depot)  ## If there is a mistake it is with distance functions
                    if can_pair_be_merged:
                        linked_vehicle = routing_functions.dispatch_vehicle(vehicle_i, dispatched_j,
                                                                            long_distance,
                                                                            long_capacity,
                                                                            long_road, distance_cost)
                        dispatch_list.append(linked_vehicle)

        single_location_list = vehicle_list
        for vehicle in single_location_list:
            for tool_id, amount_requested in vehicle.tools_in_vehicle.items():
                master_depot.tool_reserved_for_delivery(tool_id, amount_requested)

        final_vehicles[day] = too_large_to_be_combined + dispatch_list + single_location_list
    return final_vehicles, init_depot, smallest_tool