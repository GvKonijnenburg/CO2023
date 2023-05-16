from itertools import combinations
import pandas as pd
import order_functions
import delivery_only_algorithm
import route_functions
import vehicle_functions
# import capacity_checkers

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
def savings_algo(order_vehicle_information, distance_matrix, init_depot, vehicle_capacity, max_trip_distance,
                                     vehicle_operation_cost,distance_cost):
    init_depot.start_new_day()
    master_order_list = order_vehicle_information
    final_vehicles = {}
    # print('start of day')
    # print(init_depot)
    # Since Day 1 has only deliveries there are less checks to do, so I do this day seperately to speed up computation.
    orders_day_1 = master_order_list[master_order_list['order_day'] == 1].sort_values(by='tool_Count', ascending=False)
    routes_for_day_one,master_depot,master_order_list,smallest_tool = delivery_only_algorithm.first_day_algo(orders_day_1,init_depot,distance_cost,
        vehicle_operation_cost,master_order_list,vehicle_capacity,distance_matrix,max_trip_distance)
    final_vehicles[1] = routes_for_day_one

    for day in range(2, max(master_order_list['order_day']) + 1):
        daily_routes = []
        master_depot.start_new_day()
        orders_to_complete = master_order_list[master_order_list['order_day'] == day].sort_values(by=['tool_id','tool_Count','max_delivery_day'],
                                                                                          ascending=[True, False, False])
        updated_orders_to_complete, master_order_list,was_an_order_moved,order_must_be_completed_list= order_functions.order_mover(orders_to_complete, master_depot, distance_cost,
                                                                           vehicle_operation_cost, master_order_list,
                                                                           vehicle_capacity,day)

        # Since tools are expensive, lets see if a large_pick_up can fullfill a large delivery.
        initial_merge_threshold = vehicle_capacity-smallest_tool
        large_orders = updated_orders_to_complete[updated_orders_to_complete['vehicle_load'] > (initial_merge_threshold)]
        large_orders.sort_values(by=['tool_id', 'tool_Count','max_delivery_day'],ascending=[True,False,False])
        pick_up_del_merges,too_large_to_be_combined,master_depot,updated_orders_to_complete = route_functions.can_a_large_pick_up_and_large_delivery_be_combined(large_orders,updated_orders_to_complete,max_trip_distance,distance_matrix,master_depot,vehicle_operation_cost,distance_cost)
        one_stop_list = vehicle_functions.one_stop_vehicles(updated_orders_to_complete, master_depot, distance_cost, vehicle_operation_cost)
        single_dispatch_vehicles,request_to_check_end_of_day = vehicle_functions.multi_delivery_requests(one_stop_list, vehicle_capacity, distance_cost)
        vehicle_list = pick_up_del_merges + single_dispatch_vehicles
        cut_off_pairs = compute_savings_matrix(distance_matrix,vehicle_list,distance_cost)
        locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
        for pair in cut_off_pairs:
            loc_i, loc_j, savings = pair[0], pair[1], pair[2]
            vehicle_i = locations_in_cut_off_pairs[loc_i]
            vehicle_j = locations_in_cut_off_pairs[loc_j]
            route_i = vehicle_i.farms_visited
            route_j = vehicle_j.farms_visited
            if len(route_i) == 3 and len(route_j) == 3:
                can_we_merge, new_distance, new_load,new_tools_in_vehicle = route_functions.can_two_routes_be_merged(vehicle_i,
                    vehicle_j,distance_matrix,loc_i,loc_j,vehicle_capacity,max_trip_distance,master_depot)
                if can_we_merge:
                    new_vehicle,master_depot = route_functions.dispatch_vehicle_pd(vehicle_i, vehicle_j,
                                                                   new_distance, new_load, loc_i, loc_j,
                                                                   distance_cost,new_tools_in_vehicle,master_depot)
                    if route_functions.is_it_word_merging_routes:
                        vehicle_list.remove(vehicle_i)
                        vehicle_list.remove(vehicle_j)
                        vehicle_list.append(new_vehicle)
                        locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
            elif route_i[-2] == loc_i and route_j[1] == loc_j:
                can_we_add_a_farm, new_distance, new_load,new_vehicle_route,new_tools_in_vehicle = route_functions.can_we_add_a_location(vehicle_i,
                    vehicle_j,distance_matrix,vehicle_capacity,max_trip_distance,master_depot,updated_orders_to_complete)
                if can_we_add_a_farm:
                    new_vehicle,master_depot = route_functions.extend_route_merger_pd(vehicle_i, vehicle_j, new_distance, new_load,
                                                                      distance_cost,new_tools_in_vehicle,master_depot,new_vehicle_route)
                    if route_functions.is_it_word_merging_routes:
                        vehicle_list.remove(vehicle_i)
                        vehicle_list.remove(vehicle_j)
                        vehicle_list.append(new_vehicle)
                        locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
        daily_routes = vehicle_list + too_large_to_be_combined
        for vehicle in daily_routes:
            leftover_tools = vehicle.get_leftover_tools()
            master_depot.add_tools_to_inventory(leftover_tools)
        final_vehicles[day] = daily_routes

    return final_vehicles