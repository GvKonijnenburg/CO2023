from Scheduler2 import*

class Trip:
    def __init__(self, request):
        self.trip = [0, request, 0]

def calculate_saving(k, loc_i, loc_j,distanceMatrix,distance_cost):
    saving = (k * (distanceMatrix[0][loc_i] + distanceMatrix[0][loc_j] -
                   distanceMatrix[loc_i][loc_j]))
    return saving

def calculate_saving_matrix(instance):
    saving_list = []
    k = 2
    for loc_i in instance.coordinates.keys():
        for loc_j in instance.coordinates.keys():
            if loc_i is loc_j or loc_j == 0 or loc_i == 0:
                continue
            saving_list.append((loc_i, loc_j, calculate_saving(k,loc_i,loc_j,instance.distanceMatrix,instance.DISTANCE_COST)))

    return sorted(saving_list, key=lambda tup: tup[2], reverse=True)

def make_route_on_saving(schedule):
    daily_trips = {}
    for day, s in schedule.scheduleDaily.items():
        daily_trips[day] = [Trip(req) for req in s]
    return daily_trips


