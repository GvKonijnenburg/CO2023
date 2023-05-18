from itertools import combinations
import routing_functions
import vehicle_functions
import constraint_checkers
def is_farm_next_to_depot(vehicle,farm): # If time makes this faster since looping is inneffcient.
    if vehicle.farms_visited[1] == farm:
        return True
    if vehicle.farms_visited[-2]== farm:
        return True
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
def vehicle_with_sufficient_capacity_locator(dispatch_list,merge_capacity_required):
    for vehicle in dispatch_list:
        if vehicle.vehicle_cumalative_load >= merge_capacity_required:
            return vehicle


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
        # since now in some cases, i has a vehicle with multiple tools.
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
def first_day_algo(orders_day_1,init_depot,distance_cost,
        vehicle_operation_cost,vehicle_capacity,distance_matrix,max_trip_distance):
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    initial_routes = routing_functions.initial_delivery_routes(orders_day_1, init_depot, distance_cost, vehicle_operation_cost)
    multi_request_routes = vehicle_functions.multi_request_vehicles(initial_routes)
    if len(multi_request_routes) >0:
        print('implement this when it arises d1 multi requests')
    vehicle_list, large_requests,smallest_tool = vehicle_functions.large_vehicles(initial_routes, init_depot, vehicle_capacity)
    cut_off_pairs = compute_savings_matrix_for_vehicles(distance_matrix, vehicle_list,distance_cost)
    dispatch_list = []
    for pair in cut_off_pairs:
        loc_i, loc_j = pair[0],pair[1]
        vehicle_i,vehicle_j= vehicle_locator(vehicle_list, loc_i,loc_j)
        dispatched_i = dispatched_vehicle_locator(dispatch_list, loc_i)
        dispatched_j = dispatched_vehicle_locator(dispatch_list, loc_j)
        if vehicle_i is not None and vehicle_j is not None:
            if len(vehicle_i.farms_visited) == 3 and len(vehicle_j.farms_visited) == 3: ### This is Case 3a from Step 2 in the link I send, because single routes only have length of 3's
                can_pair_be_merged, new_distance, new_load = constraint_checkers.can_two_deliveries_be_merged(vehicle_i,vehicle_j,distance_matrix,loc_i, loc_j,vehicle_capacity,max_trip_distance)
                if can_pair_be_merged:
                    new_route = [0, loc_i, loc_j, 0]
                    new_vehicle = routing_functions.dispatch_vehicle(vehicle_i, vehicle_j,new_distance, new_load, new_route,distance_cost)
                    vehicle_list.remove(vehicle_i)
                    vehicle_list.remove(vehicle_j)
                    linkage_requirement = vehicle_capacity-new_vehicle.vehicle_cumalative_load
                    existing_vehicle = vehicle_with_sufficient_capacity_locator(dispatch_list,linkage_requirement)
                    if existing_vehicle is not None:
                        can_pair_be_merged, long_distance,long_capacity, long_road = constraint_checkers.can_delivery_be_added_to_existing_route(existing_vehicle, new_vehicle, distance_matrix, loc_i, loc_j, vehicle_capacity, max_trip_distance,'2B',init_depot)
                        if can_pair_be_merged:
                            linked_vehicle = routing_functions.dispatch_vehicle(existing_vehicle, new_vehicle, long_distance, long_capacity,
                                                                       long_road, distance_cost)
                            dispatch_list.append(linked_vehicle)
                    else:
                        dispatch_list.append(new_vehicle)
        if dispatched_i is not None and vehicle_j is not None: ## 3b- with loc_i in an existing route
            if not is_farm_next_to_depot(dispatched_i, loc_i):  # If time makes this faster since looping is inneffcient.
                can_pair_be_merged, long_distance,long_capacity, long_road = constraint_checkers.can_delivery_be_added_to_existing_route(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j,
                                                        vehicle_capacity,
                                                        max_trip_distance, '3bi', init_depot)
                if can_pair_be_merged:
                    linked_vehicle = routing_functions.dispatch_vehicle(dispatched_i, vehicle_j, long_distance,
                                                                      long_capacity,
                                                                      long_road, distance_cost)
                    dispatch_list.append(linked_vehicle)
        if dispatched_j is not None and vehicle_i is not None: ## 3b- with loc_j in an existing route
            if not is_farm_next_to_depot(dispatched_j, loc_j):
                can_pair_be_merged, long_distance,long_capacity, long_road = constraint_checkers.can_delivery_be_added_to_existing_route(vehicle_i, dispatched_j, distance_matrix, loc_i, loc_j,
                                                        vehicle_capacity,
                                                        max_trip_distance, '3bj', init_depot)
                if can_pair_be_merged:
                    linked_vehicle = routing_functions.dispatch_vehicle(vehicle_i,dispatched_j, long_distance,
                                                                      long_capacity,
                                                                      long_road, distance_cost)
                    dispatch_list.append(linked_vehicle)
        if dispatched_i is not None and dispatched_j is not None:# 3c where both i and j have been included
            if dispatched_i.farms_visited[-2] == loc_i and dispatched_j.farms_visited == [1]:
                can_pair_be_merged, long_distance,long_capacity, long_road = constraint_checkers.can_delivery_be_added_to_existing_route(vehicle_i, dispatched_j, distance_matrix, loc_i, loc_j,vehicle_capacity,
                    max_trip_distance, '3both', init_depot) ## If there is a mistake it is with distance functions
                if can_pair_be_merged:
                    linked_vehicle = routing_functions.dispatch_vehicle(vehicle_i,dispatched_j, long_distance,
                                                                      long_capacity,
                                                                      long_road, distance_cost)

                    dispatch_list.append(linked_vehicle)




    #### Dealing with left over pairs. I assume that the distance is never equal
    # if distance_cost > vehicle_operation_cost: ## Implement this later, since this requires more thinking than just merging by load
    #     for vehicle in vehicle_list:
    #         test = distance_functions.distance_to_depot(vehicle,master_order_list)
    # if vehicle_operation_cost > distance_cost:
    #     print('implement this when you arive at the instance')

    ### to test this for now I give the remaining vehicles their own route as suggested by the MIT implementation


    final_daily_route_list = large_requests + dispatch_list

    print(large_requests)
    print(dispatch_list)
    print(vehicle_list)

    return final_daily_route_list, init_depot, smallest_tool