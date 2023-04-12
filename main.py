
import file_parsers as fp
import distance_functions as df
import schedulers as schedulers

if __name__ == "__main__":
    global_dict, tools, coordinates, requests = fp.file_parser("C:/Git/Combinatorial Optimization/instances/challenge_r100d10_1.txt")
    distance_mat = df.distance_matrix(coordinates)
    scheduled_tools, scheduled_requests = schedulers.naive(tools, requests, global_dict['DAYS'])