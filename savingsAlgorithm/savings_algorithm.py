import delivery_only_algorithm
import routing_functions
import vehicle_functions
from collections import defaultdict
import constraint_checkers
def savings_algo(order_vehicle_information, distance_matrix, init_depot, vehicle_capacity, max_trip_distance,
                                     vehicle_operation_cost,distance_cost,scheduled_request):
    init_depot.start_new_day()
    master_order_list = order_vehicle_information
    requests_for_day_one = scheduled_request[1]
    final_vehicles = {}
    init_depot.start_new_day()
    print(init_depot)

    # Day 1 Has its own function due to the fact that there are only deliveries. Therefore, there are less checks to do.
    orders_for_day_one = master_order_list[master_order_list['route_id'].isin(requests_for_day_one)]
    routes_for_day_one,master_depot,smallest_tool = delivery_only_algorithm.first_day_algo(orders_for_day_one,init_depot,distance_cost,
        vehicle_operation_cost,vehicle_capacity,distance_matrix,max_trip_distance)
    final_vehicles[1] = routes_for_day_one
    for day in range(2, max(master_order_list['order_day']) + 1):
        master_depot.start_new_day()
        daily_requests = scheduled_request[day]
        daily_orders_to_complete = master_order_list[master_order_list['route_id'].isin(daily_requests)]
        initial_routes = routing_functions.initial_pick_up_and_delivery_routes(daily_orders_to_complete, master_depot,distance_cost,vehicle_operation_cost)
        multi_request_routes = vehicle_functions.multi_request_vehicles(initial_routes)
        multi_request_vehicles = {}
        ### This part of the code is because we have to keep track of requests and not only farms
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
                    # print(vehicle1)
                    for j in range(i + 1, len(matching_vehicles)):
                        vehicle_j= matching_vehicles[j]
                        can_these_two_be_merged,new_vehicle_load = constraint_checkers.can_two_request_become_one(vehicle_i, vehicle_j, vehicle_capacity)
                        if can_these_two_be_merged:
                            new_vehicle = routing_functions.dispatch_vehicle(vehicle_i, vehicle_j,vehicle_i.distance_traveled,
                                                                             new_vehicle_load, vehicle_i.farms_visited,distance_cost)
                            initial_routes.remove(vehicle_i)
                            initial_routes.remove(vehicle_j)
                            initial_routes.append(new_vehicle) # if there duplicates in solution check here first.

            break
        # large_orders.sort_values(by=['tool_id', 'tool_Count','max_delivery_day'],ascending=[True,False,False])
