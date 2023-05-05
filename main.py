
import file_parsers
import os
import distance_functions
import schedulers
import route_scheduler_or

def files_in_folder(folder):
    returnvalue = []

    # Iterate directory
    for path in os.listdir(folder):
        # check if current path is a file
        if os.path.isfile(os.path.join(folder, path)):
            returnvalue.append(path)
    return returnvalue

if __name__ == "__main__":
    folder = 'C:/Git/Combinatorial Optimization/instances/'
    instances = files_in_folder(folder)
   
    # replace instances with single file if you only want to test a single file
    #instances = ['challenge_r100d10_1.txt']
    
    for instance in instances:
        print(instance)
        global_dict, tools, coordinates, requests = file_parsers.file_parser(folder + instance)
        distance_mat = distance_functions.distance_matrix(coordinates)
        scheduled_tools, scheduled_requests = schedulers.naive(tools, requests, global_dict['DAYS'])
        route_scheduler_or.main(global_dict, distance_mat, scheduled_requests, scheduled_tools, instance)
