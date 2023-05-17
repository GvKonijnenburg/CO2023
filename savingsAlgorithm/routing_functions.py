import vehicle_functions
import inventory_management
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
            request_fullfilled = order[-1]
            tool_id = order[6]
            amount_requested = order[7]
            tools_in_vehicle = {tool_id: amount_requested}
            tools_picked_up = {}
            tools_delivered = {tool_id:amount_requested}
            order_history= (request_fullfilled,tool_id,amount_requested)
            route_cost = distance_cost*distance_traveled + vehicle_operation_cost
            vehicle_i = vehicle_functions.Vehicle(v_id=v_id,distance_traveled=distance_traveled,vehicle_cumalative_load=vehicle_load,
                                                  farms_visited=vehicle_route,request_fullfilled=request_fullfilled,
                                                  tools_in_vehicle=tools_in_vehicle,tools_picked_up=tools_picked_up,
                                                  tools_delivered=tools_delivered,
                                                  order_history=order_history,vehicle_operation_cost=vehicle_operation_cost,
                                                  route_cost=route_cost)
            depot.tool_reserved_for_delivery(tool_id,amount_requested)
            initial_routes.append(vehicle_i)
        else:
            raise ValueError(f"Function:initial_delivery_routes day 1")
    return initial_routes
def dispatch_vehicle(vehicle_i, vehicle_j,new_distance, vehicle_current_load, new_route,distance_cost):
    tools_in_vehicle = vehicle_functions.update_tools_in_vehicle([vehicle_i,vehicle_j])
    request_fullfilled = [vehicle_i.request_fullfilled]+[vehicle_j.request_fullfilled]
    total_costs = new_distance*distance_cost+vehicle_i.vehicle_operation_cost
    order_history = [vehicle_i.order_history] + [vehicle_j.order_history]

    new_vehicle = vehicle_functions.Vehicle(v_id = vehicle_i.v_id,vehicle_operation_cost=vehicle_i.vehicle_operation_cost,
                          tools_in_vehicle=tools_in_vehicle,farms_visited=new_route,request_fullfilled=request_fullfilled,
                          distance_traveled=new_distance,vehicle_cumalative_load=vehicle_current_load,route_cost=total_costs,
                                            tools_delivered=tools_in_vehicle,tools_picked_up={},order_history=order_history)
    return new_vehicle
def initial_pick_up_and_delivery_routes(order_information,depot, distance_cost, vehicle_operation_cost):
    initial_routes = []
    for order in order_information.itertuples():
        v_id = order[1]
        distance_traveled = order[-2]
        vehicle_load = order[-3]
        vehicle_route = [depot.loc, order[3], depot.loc]
        request_fullfilled = order[-1]
        tool_id = order[6]
        amount_requested = order[7]
        tools_in_vehicle = {tool_id: amount_requested}
        tools_picked_up = {}
        tools_delivered = {}
        order_history= (request_fullfilled,tool_id,amount_requested)
        route_cost = distance_cost*distance_traveled + vehicle_operation_cost
        load_history = {depot.loc:vehicle_load}

        vehicle_i = vehicle_functions.Vehicle(v_id=v_id,load_history=load_history,distance_traveled=distance_traveled,vehicle_cumalative_load=vehicle_load,
                                              farms_visited=vehicle_route,request_fullfilled=request_fullfilled,
                                              tools_in_vehicle=tools_in_vehicle,tools_picked_up=tools_picked_up,
                                              tools_delivered=tools_delivered,
                                              order_history=order_history,vehicle_operation_cost=vehicle_operation_cost,
                                              route_cost=route_cost)
        vehicle_i.process_order(tool_id,amount_requested)
        initial_routes.append(vehicle_i)
    return initial_routes

# def large_pick_up_and_delivery_matcher(large_order_list,max_distance,distance_matrix,depot,vehicle_operation_cost,distance_cost):
#     print(large_order_list)
#     # order_list_to_combine = order_functions.get_best_combinations(large_order_list,distance_matrix)
#     order_ids_fullfilled= []
#     new_vehicle_list = []
#     large_delivery_list = []
#     for delivery, pickup in order_list_to_combine:
#         pickup_loc = pickup[2]
#         delivery_loc = delivery[2]


        # distance_between_points = distance_functions.calculate_distance_between_points(distance_matrix, delivery_loc, pickup_loc)
        # distance_pick_up_to_depot = distance_functions.calculate_distance_between_points(distance_matrix, depot.loc, pickup_loc)
        # distance_delivery_to_depot = distance_functions.calculate_distance_between_points(distance_matrix, depot.loc, delivery_loc)
        # new_distance = distance_pick_up_to_depot + distance_between_points + distance_delivery_to_depot
        # if new_distance <= max_distance:
        #     v_id = pickup[1]
        #     tool_id_pick_up = pickup[5]
        #     tool_count_pick_up = pickup[6]
        #     tool_id_delivery = delivery[5]
        #     tool_count_delivery = delivery[6]
        #     distance_traveled = new_distance
        #     tools_in_vehicle = {}
        #     tools_in_vehicle[tool_id_pick_up] = tools_in_vehicle.get(tool_id_pick_up, 0) + tool_count_pick_up
        #     tools_in_vehicle[tool_id_delivery] = tools_in_vehicle.get(tool_id_delivery, 0) + tool_count_delivery
        #     vehicle_load = sum(depot.tools[tool_id].size * tool_count for tool_id, tool_count in tools_in_vehicle.items())
        #     vehicle_route = [depot.loc, pickup[2],delivery[2], depot.loc]
        #     request_fullfilled = [pickup[-1],delivery[-1]]
        #     vehicle_operation_cost = vehicle_operation_cost
        #     new_vehicle = vehicle_functions.init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route, request_fullfilled,
        #                      tools_in_vehicle, distance_cost, vehicle_operation_cost)
        #     new_vehicle.large_pick_ups()
        #     new_vehicle_list.append(new_vehicle)
        #     order_ids_fullfilled.append(pickup[-1])
        #     order_ids_fullfilled.append(delivery[-1])
        # else:
        #     print('if initial distance to high implement or else all the large request are fullfilled ')




def is_it_word_merging_routes(vehicle_i, vehicle_j, new_vehicle):
    combined_cost = vehicle_i.route_cost + vehicle_j.route_cost
    if combined_cost > new_vehicle.route_cost:
        return True
    else:
        return False