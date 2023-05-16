from itertools import combinations
import route_functions
import vehicle_functions
import depot_functions
def compute_savings_matrix_for_vehicles(distance_matrix, vehicle_list,distance_cost):
    # When we only have to deal with deliveries, the pair {a,b} and {b,a} is not important
    # since the vehicle has to load the tools to make that delivery anyways (because there are no pick ups)
    savings_list = []
    locations_to_visit = list(set([vehicle.farms_visited[1] for vehicle in vehicle_list]))
    location_pairs = list(combinations(locations_to_visit, 2))
    for pair in location_pairs:
        loc_i = pair[0]
        loc_j = pair[1]
        vehicle_i = next(vehicle for vehicle in vehicle_list if vehicle.farms_visited[1] == loc_i)
        vehicle_j = next(vehicle for vehicle in vehicle_list if vehicle.farms_visited[1] == loc_j)
        tools_i = set(vehicle_i.tools_in_vehicle.keys())
        tools_j = set(vehicle_j.tools_in_vehicle.keys())
        k = 0
        # according to google & finds the intersection, this is to deal with the solution file
        # since now in some cases, i have a vehicle with multiple tools.
        if tools_i & tools_j:
            k = 1.5
        else:
            k = 1
        savings = (k * (distance_matrix[0][loc_i] + distance_matrix[0][loc_j] -
                                   distance_matrix[loc_i][loc_j]) )*distance_cost
        savings_list.append((loc_i, loc_j, savings))
    # median or q=0.5 equivalant, only lists are a little faster, for large operations
    savings_list.sort(key=lambda x: x[2], reverse=True)
    savings_cutoff = savings_list[len(savings_list) // 2][2]
    cut_off_pairs = [(loc_i, loc_j, savings) for loc_i, loc_j, savings in savings_list if savings >= savings_cutoff]
    # savings_matrix = pd.DataFrame(savings_list,columns=['Loc_i', 'Loc_j', 'Savings'])
    # savings_matrix = savings_matrix.sort_values(by=['Savings', ], ascending=False)
    # savings_cutoff = savings_matrix['Savings'].quantile(q=0.5)
    # cut_off_pairs = savings_matrix[savings_matrix['Savings'] >= savings_cutoff].reset_index(drop=True)
    return cut_off_pairs

def initial_delivery_routes(order_information, depot, distance_cost, vehicle_operation_cost):
    initial_routes = []
    for order in order_information.itertuples():
        tool_id = order[6]
        amount_requested = order[7]
        if depot.inventory_check(tool_id, amount_requested):
            v_id = order[1]
            distance_traveled = order[-2]
            vehicle_load = order[-3]
            vehicle_route = [depot.loc, order[3], depot.loc]
            request_fullfilled = [order[-1]]
            tool_id = order[6]
            amount_requested = order[7]
            tools_in_vehicle = {tool_id: amount_requested}
            vehicle_i = vehicle_functions.init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route,
                                                   request_fullfilled, tools_in_vehicle, distance_cost,
                                                   vehicle_operation_cost)
            depot_functions.process_tools(depot,tools_in_vehicle)
            initial_routes.append(vehicle_i)
        else:
            raise ValueError(f"Function:initial_delivery_routes day 1")
    return initial_routes,depot

def first_day_algo(orders_day_1,depot,distance_cost,vehicle_operation_cost,master_order_list,vehicle_capacity,distance_matrix,max_trip_distance):
    initial_routes,depot = initial_delivery_routes(orders_day_1,depot,distance_cost,vehicle_operation_cost)
    single_dispatch_vehicles,orders_to_check_end_of_day = vehicle_functions.multi_delivery_requests(initial_routes,vehicle_capacity,distance_cost)
    if len(orders_to_check_end_of_day) > 0:
        raise ValueError("Implement orders left day 1")
    vehicle_list, large_requests,smallest_tool = vehicle_functions.large_vehicles(single_dispatch_vehicles, depot, vehicle_capacity)
    cut_off_pairs = compute_savings_matrix_for_vehicles(distance_matrix, vehicle_list,distance_cost)
    locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
    for pair in cut_off_pairs:
        loc_i, loc_j,savings = pair[0], pair[1],pair[2]
        vehicle_i = locations_in_cut_off_pairs[loc_i]
        vehicle_j = locations_in_cut_off_pairs[loc_j]
        route_i = vehicle_i.farms_visited
        route_j = vehicle_j.farms_visited
        if len(route_i) == 3 and len(route_j) == 3:
            can_we_merge, new_distance, new_load = route_functions.can_first_day_deliveries_be_merged(vehicle_i,
                                                                                                        vehicle_j,
                                                                                                        distance_matrix,
                                                                                                        loc_i, loc_j,
                                                                                                        vehicle_capacity,
                                                                                                        max_trip_distance)
            if can_we_merge:
                new_vehicle = route_functions.dispatch_vehicle(vehicle_i, vehicle_j,
                                                                     new_distance, new_load, loc_i, loc_j,
                                                                     distance_cost)
                if route_functions.is_it_word_merging_routes:
                    vehicle_list.remove(vehicle_i)
                    vehicle_list.remove(vehicle_j)
                    vehicle_list.append(new_vehicle)
                    locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
                    continue
        if route_i[-2] == loc_i and route_j[1] == loc_j:
            can_we_add_a_delivery, new_distance, new_load, new_route = route_functions.can_a_delivery_be_added_on_the_first_day(
                vehicle_i, vehicle_j, distance_matrix, vehicle_capacity, max_trip_distance, depot)
            if can_we_add_a_delivery:
                new_vehicle = route_functions.extend_route_merger(vehicle_i, vehicle_j, new_distance, new_load, distance_cost)
                if route_functions.is_it_word_merging_routes:
                    vehicle_list.remove(vehicle_i)
                    vehicle_list.remove(vehicle_j)
                    vehicle_list.append(new_vehicle)
                    locations_in_cut_off_pairs = vehicle_functions.location_mapper(vehicle_list)
                    continue
    daily_routes = vehicle_list + large_requests
    #### Implement the rest of the code later after having a feasible solution.
    return daily_routes,depot,master_order_list,smallest_tool
