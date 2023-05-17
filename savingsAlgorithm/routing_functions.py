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
            order_history= {request_fullfilled:(tool_id,amount_requested)}
            route_cost = distance_cost*distance_traveled + vehicle_operation_cost
            vehicle_i = vehicle_functions.Vehicle(v_id=v_id,distance_traveled=distance_traveled,vehicle_current_load=vehicle_load,
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
    new_vehicle = vehicle_functions.Vehicle(v_id = vehicle_i.v_id,vehicle_operation_cost=vehicle_i.vehicle_operation_cost,
                          tools_in_vehicle=tools_in_vehicle,farms_visited=new_route,request_fullfilled=request_fullfilled,
                          distance_traveled=new_distance,vehicle_current_load=vehicle_current_load,route_cost=total_costs,
                                            tools_delivered=tools_in_vehicle,tools_picked_up={},order_history={})
    return new_vehicle
def is_it_word_merging_routes(vehicle_i, vehicle_j, new_vehicle):
    combined_cost = vehicle_i.route_cost + vehicle_j.route_cost
    if combined_cost > new_vehicle.route_cost:
        return True
    else:
        return False