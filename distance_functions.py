import math
import numpy as np

def distance_matrix(coordinate_list):
    n = len(coordinate_list)
    calcDistance = np.zeros((n,n), dtype = 'int')
    for i in range(n):
        loc_i = coordinate_list[i]
        for j in range(i+1, n):
            loc_j = coordinate_list[j]
            dist = math.floor(math.sqrt(pow(loc_i.x_co - loc_j.x_co, 2) + pow(loc_i.y_co - loc_j.y_co, 2)))
            calcDistance[i][j] = calcDistance[j][i] = int(dist)
    return calcDistance


