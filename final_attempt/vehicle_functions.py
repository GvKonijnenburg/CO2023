from dataclasses import dataclass, field
import vehicle_functions
@dataclass
class Vehicle:
    v_id: int
    distance_traveled: int
    vehicle_current_load: int
    farms_visited: list
    request_fullfilled: list
    vehicle_operation_cost: int
    route_cost:int
    tools_in_vehicle: dict[int, int] = field(default_factory=dict)
    tools_picked_up: dict[int, int] = field(default_factory=dict)
    tools_delivered: dict[int, int] = field(default_factory=dict)
    def pick_up_tools(self, tool_id, amount):
        self.tools_in_vehicle[tool_id] += amount
        self.tools_picked_up[tool_id] = self.tools_picked_up.get(tool_id, 0) + amount
        self.vehicle_current_load += amount
    def large_pick_ups(self):
        for tool_id, amount in self.tools_in_vehicle.items():
            if amount < 0:
                self.tools_delivered[tool_id] = self.tools_delivered.get(tool_id, 0)
    def recalculate_vehicle_load(self, depot):
        new_load = 0
        for tool, amount in self.tools_in_vehicle.items():
            if tool in depot.tools:
                tool_size = depot.tools[tool].size
                new_load += abs(amount) * tool_size
        self.vehicle_current_load = new_load
    def get_leftover_tools(self):
        return {tool_id: -amount for tool_id, amount in self.tools_in_vehicle.items() if amount < 0}


def calculate_vehicle_load(newly_loaded_tools,depot):
    load = 0
    for tool_id, amount in newly_loaded_tools.items():
        if tool_id in depot.tools:
            tool = depot.tools[tool_id]
            load += abs(amount) * tool.size
    return load
def init_vehicle(v_id,distance_traveled,vehicle_current_load,farms_visited,request_fullfilled,
                 tools_in_vehicle,distance_cost,vehicle_operation_cost):
    travel_cost = distance_traveled*distance_cost
    total_cost = vehicle_operation_cost+travel_cost
    vehicle_i = Vehicle(v_id= v_id,distance_traveled=distance_traveled,vehicle_current_load=vehicle_current_load,
                        farms_visited=farms_visited,request_fullfilled=request_fullfilled,
                        vehicle_operation_cost=vehicle_operation_cost,route_cost=total_cost,
                        tools_in_vehicle=tools_in_vehicle)
    return vehicle_i
def update_tools_in_vehicle(vehicle_list):
    combined_tools = {}
    for vehicle in vehicle_list:
        for tool, amount in vehicle.tools_delivered.items():
            if tool in combined_tools:
                combined_tools[tool] += amount
            else:
                combined_tools[tool] = amount
    return combined_tools
def merge_tools_in_vehicle(vehicle1, vehicle2):
    merged_tools = {}
    for tool, amount in vehicle1.tools_in_vehicle.items():
        merged_tools[tool] = merged_tools.get(tool, 0) + amount
    for tool, amount in vehicle2.tools_in_vehicle.items():
        merged_tools[tool] = merged_tools.get(tool, 0) + amount
    return merged_tools
def update_pd_delvehicle(vehicle_i, vehicle_j):
    new_delivery_tracker = {}
    new_pick_up_tracker = {}
    for tool, count in vehicle_i.tools_delivered.items():
        new_delivery_tracker[tool] = new_delivery_tracker.get(tool, 0) + count
    for tool, count in vehicle_j.tools_delivered.items():
        new_delivery_tracker[tool] = new_delivery_tracker.get(tool, 0) + count
    for tool, count in vehicle_i.tools_picked_up.items():
        new_pick_up_tracker[tool] = new_pick_up_tracker.get(tool, 0) + count
    for tool, count in vehicle_j.tools_picked_up.items():
        new_pick_up_tracker[tool] = new_pick_up_tracker.get(tool, 0) + count
    return new_delivery_tracker,new_pick_up_tracker
def large_vehicles(vehicle_list, init_depot, vehicle_capacity):
    smallest_tool = min(init_depot.tools.values(), key=lambda tool: tool.size).size
    large_request_vehicle_load = vehicle_capacity - smallest_tool
    too_large_to_be_combined = [vehicle for vehicle in vehicle_list if vehicle.vehicle_current_load > large_request_vehicle_load]
    vehicle_list = [vehicle for vehicle in vehicle_list if vehicle not in too_large_to_be_combined]
    return vehicle_list, too_large_to_be_combined,smallest_tool


def multi_delivery_requests(vehicle_list, vehicle_capacity, distance_cost):
    farms_who_have_requested = {}
    request_to_check_end_of_day = []
    vehicles_to_remove = []
    for vehicle_to_combine in vehicle_list:
        farm_location = vehicle_to_combine.farms_visited[1]
        if farm_location in farms_who_have_requested:
            vehicle = farms_who_have_requested[farm_location]
            new_vehicle_load = vehicle.vehicle_current_load + vehicle_to_combine.vehicle_current_load
            if new_vehicle_load <= vehicle_capacity:
                new_tools = update_tools_in_vehicle(vehicle_list)
                new_request_fullfilled = [[vehicle.request_fullfilled, vehicle_to_combine.request_fullfilled]]
                new_vehicle = init_vehicle(vehicle.v_id, vehicle.distance_traveled, new_vehicle_load,
                                           vehicle.farms_visited, new_request_fullfilled,
                                           new_tools, distance_cost, vehicle.vehicle_operation_cost)
                vehicles_to_remove.append(vehicle_to_combine)
                vehicles_to_remove.append(vehicle)
                vehicle_list.append(new_vehicle)
            else:
                if len(vehicle_to_combine.request_fullfilled) < len(vehicle.request_fullfilled):
                    smallest_vehicle = vehicle_to_combine
                else:
                    smallest_vehicle = vehicle
                request_to_check_end_of_day.append(smallest_vehicle)
        farms_who_have_requested[farm_location] = vehicle_to_combine

    # Here we remove all vehicles_to_remove from vehicle_list, outside the loop
    for vehicle in vehicles_to_remove:
        if vehicle in vehicle_list:
            vehicle_list.remove(vehicle)
    return vehicle_list, request_to_check_end_of_day


def location_mapper(vehicle_list):
    location_maps = {}
    for vehicle in vehicle_list:
        for farm in vehicle.farms_visited[1:-1]:
            location_maps[farm] = vehicle
    return location_maps

def one_stop_vehicles(order_information, depot, distance_cost, vehicle_operation_cost):
    initial_routes = []
    for order in order_information.itertuples():
        tool_id = order[6]
        amount_requested = order[7]
        v_id = order[1]
        distance_traveled = order[-2]
        vehicle_load = order[-3]
        vehicle_route = [depot.loc, order[3], depot.loc]
        request_fullfilled = [order[-1]]
        tools_in_vehicle = {tool_id: amount_requested}
        vehicle_i = init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route,
                                               request_fullfilled, tools_in_vehicle, distance_cost,
                                               vehicle_operation_cost)
        initial_routes.append(vehicle_i)
    return initial_routes





# def init_vehicle(v_id, distance_traveled, vehicle_current_load, farms_visited, request_fullfilled,
#                  tools_in_vehicle, distance_cost, vehicle_operation_cost):
#     travel_cost = distance_traveled * distance_cost
#     total_cost = vehicle_operation_cost + travel_cost
#     vehicle_i = Vehicle(v_id = v_id, distance_traveled = distance_traveled,
#                         vehicle_current_load = vehicle_current_load, farms_visited = farms_visited,
#                         request_fullfilled = request_fullfilled, vehicle_operation_cost = vehicle_operation_cost,
#                         route_cost = total_cost, tools_in_vehicle = tools_in_vehicle)
#     return vehicle_i
