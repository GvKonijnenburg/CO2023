import distance_functions
def can_two_deliveries_be_merged(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, max_capacity, max_distance):
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
        return False, None, None
    return True, new_distance, new_vehicle_load


def can_delivery_be_added_to_existing_route(vehicle_i, vehicle_j, distance_matrix, loc_i, loc_j, vehicle_capacity,
                                            max_trip_distance, merge_type, depot):
    vehicle_capacity_after_merge = vehicle_i.vehicle_current_load + vehicle_j.vehicle_current_load
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
        print(new_route)
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

