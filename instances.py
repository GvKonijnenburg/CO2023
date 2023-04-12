from dataclasses import dataclass,field
import math
@dataclass
class Tool:
    id: int
    weight: int
    amount: int
    cost: int
@dataclass
class Coordinates:
    id: int
    x_co: int
    y_co: int

@dataclass
class Request:
    id:int
    locid: int
    fromDay: int
    toDay: int
    numDays: int
    toolid: int
    toolCount: int
@dataclass
class Vehicle:
    capacity: int
    max_trip_distance: int
    vehicle_cost: int
    vehicle_day_cost: int
    distance_cost: int
@dataclass
class Fixed:
    days: str
    capacity: str
    maxTripDistance: str
    depot: str
    vehicleCost: str
    vehicleDayCost: str
    distanceCost: str
    tools: str
    coordinates: str
    requests: str

#May not be integer?
    # depot
    # tool kinds by their IDs
    # location id



