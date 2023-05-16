import numpy as np
def distance_matrix(coordinate_list):
    farm_ids = sorted(coordinate_list.keys())
    farm_coordinate_list = [coordinate_list[farm] for farm in farm_ids]
    farm_coordinates = np.array([[farm['x_co'], farm['y_co']] for farm in farm_coordinate_list])
    x_co,y_co = farm_coordinates[:, 0].reshape(-1, 1),farm_coordinates[:, 1].reshape(-1, 1)
    dist = np.sqrt((x_co - x_co.T)**2 + (y_co - y_co.T)**2).astype(np.int)
    dist_matrix = dict(zip(farm_ids, dist))
    return dist_matrix
def calculate_distance_between_points(distance_matrix,loc_i,loc_j):
    distance_between_farms = distance_matrix[loc_i][loc_j]
    return distance_between_farms
