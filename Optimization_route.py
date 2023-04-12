from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import numpy as np
import pandas as pd

schedule = pd.DataFrame({
    'id': [1, 2, 3],
    'location': ['A', 'B', 'C'],
    'delivery_day': ['2023-04-15', '2023-04-17', '2023-04-18'],
    'pickup_day': ['2023-04-14', '2023-04-16', '2023-04-17'],
    'tool_id': [101, 102, 103],
    'number_requested_tools': [5, 10, 3]
})

calcDistance = np.array([
    [0, 10, 20, 30],
    [10, 0, 15, 25],
    [20, 15, 0, 18],
    [30, 25, 18, 0]
])


def create_data_model(distance_matrix, schedule, num_vehicles):
    print(f"distance_matrix: {type(distance_matrix)}, shape: {distance_matrix.shape}")
    print(f"schedule: {type(schedule)}, shape: {schedule.shape}")
    print(f"num_vehicles: {num_vehicles, type(num_vehicles)}")

    data = {}
    data['distance_matrix'] = distance_matrix.tolist()
    print(data['distance_matrix'])
    data['num_locations'] = len(calcDistance)
    data['num_vehicles'] = num_vehicles
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)
    data['routing'] = routing
    data['requests'] = []
    for i in range(schedule.shape[0]):
        request = {
            'index': i + 1,
            'pickup_location': schedule.loc[i, 'location'],
            'delivery_location': schedule.loc[i, 'location'],
            'pickup_day': schedule.loc[i, 'pickup_day'],
            'delivery_day': schedule.loc[i, 'delivery_day'],
            'tool_id': schedule.loc[i, 'tool_id'],
            'num_tools': schedule.loc[i, 'number_requested_tools']
        }
        data['requests'].append(request)
    return data

def distance_callback(data, from_index, to_index):
    print("DISTANCE CALLBACK")
    print(data['distance_matrix'][from_index][to_index])
    print(type(data['distance_matrix'][from_index][to_index]))
    return data['distance_matrix'][from_index][to_index]


def demand_callback(data, from_index):
    return data['requests'][from_index - 1]['num_tools']


def create_routing_model(data, distance_callback, demand_callback, num_vehicles):
    print("CREATE ROUTING MODEL")
    print(f"num_locations: {data['num_locations'], type(data['num_locations'])}")
    print(f"distance_callback: {type(distance_callback)}")
    print(f"demand_callback: {type(demand_callback)}")
    print(f"num_vehicles: {type(num_vehicles)}")

    routing = pywrapcp.RoutingModel(pywrapcp.RoutingIndexManager(data['num_locations'], num_vehicles, 0))
    print(type(distance_callback))
   #routing.SetArcCostEvaluatorOfAllVehicles(calcDistance)
   # routing.AddDimensionWithVehicleCapacity(
   #     demand_callback, 0, [10] * data['num_locations'], True, 'Capacity')
    return routing


def add_pickup_delivery_constraints(data, routing, solution):
    print("ADD_PICKUP_DELIVERY CONSTRAINTS")
    print(f"requests: {type(data['requests'])}")
    print(f"routing: {type(routing)}")
    print(f"solution: {type(solution)}")
    manager = pywrapcp.RoutingIndexManager(
        data['num_locations'],
        data['num_vehicles'],
        data['starts'],
        data['ends']
    )
    for request in data['requests']:
        pickup_index = manager.NodeToIndex(request['pickup_location'])
        delivery_index = manager.NodeToIndex(request['delivery_location'])
        routing.AddPickupAndDelivery(
            pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(delivery_index) ==
            routing.VehicleVar(pickup_index))
        routing.solver().Add(
            solution.Value(routing.NextVar(pickup_index)) <=
            solution.Value(routing.NextVar(delivery_index)))


def print_solution(data, routing, solution):
    print("PRINT SOLUTION")
    print(f"num_vehicles: {type(data['num_vehicles'])}")
    print(f"distance_matrix: {type(data['distance_matrix'])}")
    print(f"routing: {type(routing)}")
    print(f"solution: {type(solution)}")

    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route = []
        while not routing.IsEnd(index):
            node_index = routing.IndexToNode(index)
            route.append(node_index)
            next_index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                index, next_index, vehicle_id)
            index = next_index
        route.append(0)
        total_distance += route_distance
        print(f"Route for vehicle {vehicle_id}: {route} - Distance: {route_distance}")
    print(f"Total distance: {total_distance}")


def optimize_routes(distance_matrix, schedule, num_vehicles):
    data = create_data_model(distance_matrix, schedule, num_vehicles)
    routing_model = create_routing_model(data, distance_callback, demand_callback, num_vehicles)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    solution = routing_model.SolveWithParameters(search_parameters)
    add_pickup_delivery_constraints(data, routing_model, solution)
    print_solution(data, routing_model, solution)

optimize_routes(calcDistance, schedule, 5)
