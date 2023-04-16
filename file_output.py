import argparse

def write_output(global_dict, tools, coordinates, requests, solution, instance_file_name):
    output_str = ""

    output_str += 'DATASET = {}\n'.format(global_dict['DATASET'])
    output_str += 'NAME = {}\n\n'.format(global_dict['NAME'])

    for (day_idx, cars_day) in enumerate(solution.cars_on_day):
        ## keep track of:
        # each day: vehicle index + trip by that vehicle to which farm + rq id of that farm
        #### '- rq id' if pickup else delivery
        # each day: number of vehicles in used
        output_str += 'DAY = {}\n'.format(day_idx + 1) ## why is day a decision var
        output_str += 'NUMBER_OF_VEHICLES = {}\n'.format(len(cars_day)) ## number of cars in sol
        for (car_idx, car) in enumerate(cars_day):
            output_str += '{}\tR\t'.format(car_idx + 1)

            for (trip_idx, trip) in enumerate(solution.travel): # why is travel a dict
                for (stopover_idx, stopover) in enumerate(trip.stopovers):
                    if stopover_idx == 0 and trip_idx != 0:  # ignore the depot if this is not the first trip
                        continue
                    if stopover.num_tools < 0:
                        output_str += "-"
                    output_str += '{}\t'.format(stopover.request_id)

            output_str += "\n"
        output_str += "\n"

    # print(output_str)

    filename_input_split = instance_file_name.rsplit(".", 1)
    filename_output = filename_input_split[0] + "_solution.txt"

    f = open(filename_output, 'w')
    f.write(output_str)
    f.close()
