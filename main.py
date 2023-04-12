
import file_parsers as fp
import os
import distance_functions as distance_functions
import schedulers as schedulers

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
    # instances = ['challenge_r100d10_1.txt']
    
    for instance in instances:
        print(instance)
        global_dict, tools, coordinates, requests = fp.file_parser(folder + instance)
        distance_mat = distance_functions.distance_matrix(coordinates)
        scheduled_tools, scheduled_requests = schedulers.naive(tools, requests, global_dict['DAYS'])