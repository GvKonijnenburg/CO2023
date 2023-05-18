import os
import pandas as pd
import global_schedule
import file_parser
import instances
import order_functions
import distance_functions
import inventory_management
import savings_algorithm
import vehicle_functions
from dataclasses import field

def flatten_list(my_list):
	returnvalue = []
	for i in range(len(my_list)):
		if isinstance(my_list[i], list):
			returnvalue += (flatten_list(my_list[i]))
		else:
			returnvalue.append(my_list[i])
	return returnvalue

# import file_parser
# import Instance_test
####
# import savings_algo
# import depot_inventory
# import depot_inventory

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
    cases = files_in_folder(folder)
    # cases = ['challenge_r100d10_1.txt']
    #challenge_r200d15_1.txt
    # replace cases with single file if you only want to test a single file
    # cases = ['challenge_r100d10_1.txt']
    # challenge_r500d25_5

    for case in cases:
        global_dict, tools, coordinates, requests = file_parser.new_file_parser(folder + "/" + case)
        # Variables From Parser
        dataset = global_dict['DATASET']
        name = global_dict['NAME']
        depot_loc = global_dict['DEPOT_COORDINATE']
        vehicle_capacity = global_dict['CAPACITY']
        max_distance = global_dict['MAX_TRIP_DISTANCE']
        # Variables for Cost
        vehicle_cost = global_dict['VEHICLE_COST']
        salary_cost = global_dict['VEHICLE_DAY_COST']
        distance_cost = global_dict['DISTANCE_COST']
        vehicle_operation_cost = vehicle_cost+salary_cost
        # Data for Algo & ILPS
        simulation = instances.Instance(folder + "/"+case)
        sche = global_schedule.make_schedule_ILP(simulation,True)
        scheduled_requests = sche.schedulePerDay
        master_order_list = order_functions.master_order_list(requests)
        distance_mat = distance_functions.distance_matrix(coordinates)
        ## Initialize Depot & Default Values for Vehicle
        tool_list = [inventory_management.Tool(**tool_info) for tool_info in tools.values()]
        init_depot = inventory_management.Depot(tools={tool.id: tool for tool in tool_list}, loc=depot_loc)
        vehicle_functions.Vehicle.distance_cost = field(default=distance_cost)
        vehicle_functions.Vehicle.vehicle_operation_cost = field(default=distance_cost)
        order_vehicle_information = order_functions.order_vehicle_information(master_order_list, init_depot,distance_mat)
        savings_algo_routes = savings_algorithm.savings_algo(order_vehicle_information, distance_mat, init_depot,
                                                        vehicle_capacity, max_distance,
                                                        vehicle_operation_cost, distance_cost,scheduled_requests)        # print('check here')

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        # print(savings_algo_routes)
        answer = savings_algo_routes[0]
        for key in answer:
            for vehicle in answer[key]:
                vehicle.request_fullfilled = flatten_list([vehicle.request_fullfilled])
        print_solution(dataset, name, answer, case)
        break
