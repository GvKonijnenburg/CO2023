import os
import pandas as pd
import numpy as np
import file_parser
import depot_functions
import distance_functions
import order_functions
import savings_algo

####
# import savings_algo
# import depot_inventory
# import depot_inventory

def files_in_folder(folder):
    returnvalue = []
    # Iterate directory
    for path in os.listdir(folder):
        # check if current path is a file
        if os.path.isfile(os.path.join(folder, path)):
            returnvalue.append(path)
    return returnvalue

if __name__ == "__main__":
    pd.set_option('display.width', 400)
    folder = '/Users/alibenchemsi/Documents/GitHub/CO2023/instances'
    instances = files_in_folder(folder)
    # folder = '/Users/alibenchemsi/Documents/GitHub/CO2023/instances/'
    # instances = ['challenge_r100d10_1.txt']
    #challenge_r200d15_1.txt
    # replace instances with single file if you only want to test a single file
    # instances = ['challenge_r100d10_1.txt']
    # challenge_r500d25_5
def print_solution(dataset, instance_name, vehicles_dict,instance):
    with open(f"{instance}_solution.txt", "w") as file:
        file.write(f"DATASET = {dataset}\n")
        file.write(f"NAME = {instance_name}\n\n")

        for day, vehicles in vehicles_dict.items():
            file.write(f"DAY = {day}\n")
            file.write(f"NUMBER_OF_VEHICLES = {len(vehicles)}\n")

            for i, vehicle in enumerate(vehicles, start=1):
                route = ' '.join(map(str, [0] + vehicle.request_fullfilled + [0]))
                file.write(f"{i} R {route}\n")
            file.write("\n")
def flatten(nested_list):
    result = []
    for i in nested_list:
        if isinstance(i, list):
            result.extend(flatten(i))
        else:
            result.append(i)
    return result

for instance in instances:
    print(instance)
    global_dict, tools, coordinates, requests = file_parser.new_file_parser(folder + "/" + instance)
    # Variables From Parser
    dataset = global_dict['DATASET']
    name = global_dict['NAME']
    depot_loc = global_dict['DEPOT_COORDINATE']
    vehicle_capacity = global_dict['CAPACITY']
    print(vehicle_capacity)
    max_distance = global_dict['MAX_TRIP_DISTANCE']
    # Variables for Cost
    vehicle_cost = global_dict['VEHICLE_COST']
    salary_cost = global_dict['VEHICLE_DAY_COST']
    distance_cost = global_dict['DISTANCE_COST']
    vehicle_operation_cost = vehicle_cost+salary_cost
    # Data for Savings Algo
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    master_order_list = order_functions.master_order_list(requests)
    tool_list = [depot_functions.Tool(**tool_info) for tool_info in tools.values()]
    init_depot = depot_functions.Depot(tools={tool.id: tool for tool in tool_list}, loc=depot_loc)
    distance_mat = distance_functions.distance_matrix(coordinates)
    # #Savings Algo
    order_vehicle_information = order_functions.order_vehicle_information(master_order_list, init_depot, distance_mat)
    savings_algo_routes = savings_algo.savings_algo(order_vehicle_information, distance_mat, init_depot, vehicle_capacity, max_distance,
                                     vehicle_operation_cost,distance_cost)
    print(savings_algo_routes)
    for key in savings_algo_routes:
        for vehicle in savings_algo_routes[key]:
            vehicle.request_fullfilled = flatten(vehicle.request_fullfilled)
    print_solution(dataset, name, savings_algo_routes, instance)
    print(vehicle_capacity)
    print('cap')

    break
    #

