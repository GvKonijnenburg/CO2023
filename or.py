"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import pandas as pd
from operator import itemgetter

import file_parsers
import distance_functions
import schedulers

folder = "G:/My Drive/VU Amsterdam/BA3/Combinarorial Optimization/CO2023/instances/"
instances = 'challenge_r100d10_1.txt'
global_dict, tools, coordinates, requests = file_parsers.file_parser(folder + instances)
distance_mat = distance_functions.distance_matrix(coordinates)
scheduled_tools, scheduled_requests = schedulers.naive(tools, requests, global_dict['DAYS'])

schedule = pd.DataFrame(scheduled_requests,
                        columns=['RequestID', 'Farm loc', 'Drop off',
                                 'Pick up', 'Tool type', 'Number of tools'])
day1 = schedule[(schedule['Drop off'] == 1)]
# print(requests)
request_df = pd.DataFrame(requests)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(request_df)
# print(request_df)
for i in request_df['locid']:
    print(request_df[request_df['locid'] == i]['fromDay'])

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_mat
    data['demands'] = [1]*len(distance_mat)
    # for i in day1['Farm loc'].values:
    #     data['demands'][i] = int(day1[day1['Farm loc'] == i]['Number of tools'].values)
    # data['time_windows'] = [0]*len(requests)
    # for i in range(data['time_windows']):
    #     data['time_windows'][i] = (int(request_df.sort_values(by = 'locid')[i]['fromDay'].values),
    #                             int(request_df.sort_values(by = 'locid')[i]['toDay'].values))
    data['vehicle_capacities'] = [global_dict['CAPACITY']]*10
    data['num_vehicles'] = 10
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # # Add Time Windows constraint.
    # time = 'Time'
    # routing.AddDimension(
    #     transit_callback_index,
    #     0,  # allow waiting time
    #     30,  # maximum time per vehicle
    #     False,  # Don't force start cumul to zero.
    #     time)
    # time_dimension = routing.GetDimensionOrDie(time)
    # # Add time window constraints for each location except depot.
    # for location_idx, time_window in enumerate(data['time_windows']):
    #     if location_idx == data['depot']:
    #         continue
    #     index = manager.NodeToIndex(location_idx)
    #     time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # # Add time window constraints for each vehicle start node.
    # depot_idx = data['depot']
    # for vehicle_id in range(data['num_vehicles']):
    #     index = routing.Start(vehicle_id)
    #     time_dimension.CumulVar(index).SetRange(
    #         data['time_windows'][depot_idx][0],
    #         data['time_windows'][depot_idx][1])

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    print(data['demands'])

if __name__ == '__main__':
    main()

