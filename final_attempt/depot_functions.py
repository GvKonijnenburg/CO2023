from dataclasses import dataclass, field
@dataclass
class Tool:
    id: int
    size: int
    max_available: int
    cost: int
@dataclass
class Depot:
    loc: int
    tools: dict[int, 'Tool'] = field(default_factory=dict)
    max_available_inventory: dict[int, int] = field(default_factory=dict, init=True)
    inventory_available_start_of_day: dict[int, int] = field(default_factory=dict, init=False)
    inventory_current: dict[int, int] = field(default_factory=dict, init=False)
    def __post_init__(self):
        self.max_available_inventory = {tool_id: tool.max_available for tool_id, tool in self.tools.items()}
        self.inventory_available_start_of_day = self.max_available_inventory.copy()
        self.inventory_current = self.inventory_available_start_of_day.copy()
    def inventory_check(self, tool_id, amount):
        return self.inventory_current.get(tool_id, 0) >= amount
    def pick_up_tools(self, tool_id, amount):
        self.inventory_current[tool_id] -= amount
    def return_tools(self, tool_id, amount):
        self.inventory_current[tool_id] += amount
    def start_new_day(self):
        self.inventory_available_start_of_day = self.inventory_current.copy()
    def add_tools_to_inventory(self, tools):
        for tool_id, amount in tools.items():
            self.inventory_available_start_of_day[tool_id] += amount
            self.inventory_current[tool_id] += amount
def check_inventory(depot, requests):
    for tool_id, amount in requests.items():
        if not depot.inventory_check(tool_id, amount):
            return False
    return True
def process_tools(depot, tools_in_vehicle):
    for tool_id, amount in tools_in_vehicle.items():
        if amount > 0:
            depot.pick_up_tools(tool_id, amount)


