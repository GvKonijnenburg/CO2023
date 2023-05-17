from dataclasses import dataclass, field
from collections import defaultdict
@dataclass
class Vehicle:
    v_id: int
    distance_traveled: int
    vehicle_current_load: int
    farms_visited: list
    request_fullfilled: list
    vehicle_operation_cost: int
    route_cost: int
    tools_in_vehicle: dict[int, int] = field(default_factory=dict)
    tools_picked_up: dict[int, int] = field(default_factory=dict)
    tools_delivered: dict[int, int] = field(default_factory=dict)
    order_history: dict[int, tuple[int, int]] = field(default_factory=dict)
def update_tools_in_vehicle(vehicle_list):
    new_tool_list = {}
    for vehicle in vehicle_list:
        for tool, amount in vehicle.tools_delivered.items():
            if tool in new_tool_list:
                new_tool_list[tool] += amount
            else:
                new_tool_list[tool] = amount
    return new_tool_list
def multi_request_vehicles(vehicle_list):
    visit_tracker = {}
    multi_request_vehicles = []
    for vehicle in vehicle_list:
        second_farm = vehicle.farms_visited[1]
        if second_farm in visit_tracker:
            visit_tracker[second_farm] += 1
        else:
            visit_tracker[second_farm] = 1
    for vehicle in vehicle_list:
        check_request = vehicle.farms_visited[1]
        if visit_tracker[check_request] > 1:
            multi_request_vehicles.append(vehicle)
    return multi_request_vehicles
def large_vehicles(vehicle_list, init_depot, vehicle_capacity):
    smallest_tool = min(init_depot.tools.values(), key=lambda tool: tool.size).size
    large_request_vehicle_load = vehicle_capacity - smallest_tool
    too_large_to_be_combined = [vehicle for vehicle in vehicle_list if vehicle.vehicle_current_load > large_request_vehicle_load]
    vehicle_list = [vehicle for vehicle in vehicle_list if vehicle not in too_large_to_be_combined]
    return vehicle_list, too_large_to_be_combined,smallest_tool