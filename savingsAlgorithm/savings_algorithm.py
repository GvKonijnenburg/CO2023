import delivery_only_algorithm
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
    print(final_vehicles)