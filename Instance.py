from dataclasses import dataclass
from Scheduler2 import *
from Saving import *
import pandas as pd
import os,glob


class Instance:
    def __init__(self, inputFile):
        self.DATASET = None
        self.NAME = None
        self.DAYS = None
        self.CAPACITY = None
        self.MAX_TRIP_DISTANCE = None
        self.DEPOT_COORDINATE = None
        self.VEHICLE_COST = None
        self.VEHICLE_DAY_COST = None
        self.DISTANCE_COST = None

        self.tools = []
        self.requests = []
        self.coordinates = {}

        self.startInventory = {}

        fileParser(self, inputFile)

        for index, tool in enumerate(self.tools):
            self.startInventory[tool.ID] = self.tools[index].amount

        self.requestsDf = makedf(self)
        self.distanceMatrix = distance_matrix(self.coordinates)


def makedf(instance):
    columns = ['ID', 'locID', 'fromDay', 'toDay', 'numDays', 'toolID', 'toolCount', 'weight']
    df = pd.DataFrame(data=None, columns=columns)
    for r in instance.requests:
        df.loc[r.ID] = [r.ID, r.locID, r.fromDay, r.toDay, r.numDays, r.toolID, r.toolCount,
                        instance.tools[r.toolID - 1].weight * r.toolCount]
    df.set_index('ID', inplace=True)
    return df


def distance_matrix(coordinates):
    loc_ids = sorted(coordinates.keys())
    coordinate_list = np.array([coordinates[loc] for loc in loc_ids])
    # loc_coordinates = np.array([[farm[''], farm['y_co']] for loc in coordinate_list])
    x_co, y_co = coordinate_list[:, 0].reshape(-1, 1), coordinate_list[:, 1].reshape(-1, 1)
    dist = np.sqrt((x_co - x_co.T) ** 2 + (y_co - y_co.T) ** 2).astype(int)
    dist_matrix = dict(zip(loc_ids, dist))
    return dist


def fileParser(instance, inputFile):
    with open(inputFile, 'r') as f:
        for line in f:
            line.strip()
            if "DATASET" in line:
                instance.DATASET = str(line.split(" = ")[1])
                continue
            elif "NAME" in line:
                instance.NAME = str(line.split(" = ")[1])
                continue
            elif "DAYS" in line:
                instance.DAYS = int(line.split(" = ")[1])
                continue
            elif "CAPACITY" in line:
                instance.CAPACITY = int(line.split(" = ")[1])
                continue
            elif "MAX_TRIP_DISTANCE" in line:
                instance.MAX_TRIP_DISTANCE = int(line.split(" = ")[1])
                continue
            elif "DEPOT_COORDINATE" in line:
                instance.DEPOT_COORDINATE = int(line.split(" = ")[1])
                continue
            elif "VEHICLE_COST" in line:
                instance.VEHICLE_COST = int(line.split(" = ")[1])
                continue
            elif "VEHICLE_DAY_COST" in line:
                instance.VEHICLE_DAY_COST = int(line.split(" = ")[1])
                continue
            elif "DISTANCE_COST" in line:
                instance.DISTANCE_COST = int(line.split(" = ")[1])
                continue
            elif "TOOLS" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    tool_type = next(f).split()
                    instance.tools.append(Tool(ID=int(tool_type[0]), weight=int(tool_type[1]),
                                               amount=int(tool_type[2]), cost=int(tool_type[3])))
                continue
            elif "COORDINATES" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    co_type = next(f).split()
                    instance.coordinates[int(co_type[0])] = [int(co_type[1]), int(co_type[2])]
                continue

            elif "REQUESTS" in line:
                no_iter = int(line.split(" = ")[1])
                for i in range(no_iter):
                    req_type = next(f).strip().split()
                    instance.requests.append(Request(ID=int(req_type[0]), locID=int(req_type[1]),
                                                     fromDay=int(req_type[2]), toDay=int(req_type[3]),
                                                     numDays=int(req_type[4]), toolID=int(req_type[5]),
                                                     toolCount=int(req_type[6])))
                continue


class Request:
    def __init__(self, ID, locID, fromDay, toDay, numDays, toolID, toolCount):
        self.ID = ID
        self.locID = locID
        self.fromDay = fromDay
        self.toDay = toDay
        self.numDays = numDays
        self.toolID = toolID
        self.toolCount = toolCount

    def equals(self, request):
        if isinstance(request, int):
            return False
        else:
            return self.ID is request.ID


class Tool(object):
    def __init__(self, ID, weight, amount, cost):
        self.ID = ID
        self.weight = weight
        self.amount = amount
        self.cost = cost


# @dataclass
# class Tool:
#     ID: int
#     weight: int
#     amount: int
#     cost: int
# @dataclass
# class Coordinates:
#     ID: int
#     x_co: int
#     y_co: int
#
# @dataclass
# class Request:
#     ID: int
#     locID: int
#     fromDay: int
#     toDay: int
#     numDays: int
#     toolID: int
#     toolCount: int
# @dataclass
# class Vehicle:
#     capacity: int
#     max_trip_distance: int
#     vehicle_cost: int
#     vehicle_day_cost: int
#     distance_cost: int

def writeSolution(instance, daily_trips, solution_name):
    file = open(solution_name, 'w')
    file.write("DATASET = " + instance.DATASET + "\n")
    file.write("NAME = " + instance.NAME + "\n\n")

    for day, trips in sorted(daily_trips.items()):
        file.write("DAY = {}\n ".format(day))
        file.write("NUMBER_OF_VEHICLES = {}\n".format(len(trips)))
        for i, t in enumerate(trips):
            file.write('{}\tR\t'.format(i + 1) + '\t'.join(str(req) for req in t.trip) + '\n')
        file.write('\n')
    file.close()

if __name__ == "__main__":
    for filename in os.listdir('instances/'):
        instance = Instance(os.path.join(os.getcwd(), str("instances/" + filename)))
    #     instance = Instance("instances/challenge_r500d25_4.txt")
        # scheduler = Scheduler(instance)
        # for r in scheduler.schedule.scheduleDays[9].pickups:
        #     print(r.ID)
        sche = make_schedule_ILP(instance,True)
        for i in sorted(sche.scheduleDaily):
            print("day", i, "schedule:", sche.scheduleDaily[i])
        print(sche.max_daily_use)
        print(instance.requestsDf)
        print(instance.distanceMatrix)

        savinglist = calculate_saving_matrix(instance)
        daily_trips = make_route_on_saving(sche)
        # print(savinglist)
        for d,s in sorted(daily_trips.items()):
            print('DAY',d)
            for t in range(len(s)):
                print(s[t].trip)
        writeSolution(instance,daily_trips, str("solution_"+filename))