import numpy as np
def distance_matrix(coordinate_list):
    farm_ids = sorted(coordinate_list.keys())
    farm_coordinate_list = [coordinate_list[farm] for farm in farm_ids]
    farm_coordinates = np.array([[farm['x_co'], farm['y_co']] for farm in farm_coordinate_list])
    x_co,y_co = farm_coordinates[:, 0].reshape(-1, 1),farm_coordinates[:, 1].reshape(-1, 1)
    dist = np.sqrt((x_co - x_co.T)**2 + (y_co - y_co.T)**2).astype(np.int)
    dist_matrix = dict(zip(farm_ids, dist))
    return dist_matrix
def distance_to_depot(vehicle,order_list):
    route_id = list(vehicle.order_history.keys())[0]
    distance = order_list.loc[order_list['route_id'] == route_id, 'distance_to_depot'].values[0]
    return distance

def calculate_distance_between_points(distance_matrix,loc_i,loc_j):
    distance_between_farms = distance_matrix[loc_i][loc_j]
    return distance_between_farms

def calculate_distance_between_farms(distance_matrix,route_i,route_j,depot):
    loc_i_locations = route_i.farms_visited[1:-1]
    loc_j_locations = route_j.farms_visited[1:-1]
    merged_points = loc_i_locations + loc_j_locations
    merged_points.insert(0,depot.loc)
    merged_points.insert(len(merged_points),depot.loc)
    new_distance = 0
    for i in range(len(merged_points)-1):
        current = merged_points[i]
        next = merged_points[i + 1]
        new_distance += distance_matrix[current][next]
    return new_distance,merged_points
def calculate_distance_between_routes(distance_matrix,route):
    new_distance = 0
    for i in range(len(route)-1):
        current = route[i]
        next = route[i + 1]
        new_distance += distance_matrix[current][next]
    return new_distance
