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
    inventory_in_holding_for_next_day: dict[int, int] = field(default_factory=dict, init=False)
    def __post_init__(self):
        self.max_available_inventory = {tool_id: tool.max_available for tool_id, tool in self.tools.items()}
        self.inventory_available_start_of_day = self.max_available_inventory.copy()
        self.inventory_current = self.inventory_available_start_of_day.copy()
        self.max_available_inventory = {tool_id: 0 for tool_id, tool in self.tools.items()}
    def start_new_day(self):
        self.inventory_available_start_of_day = self.inventory_current.copy()
    def inventory_check(self, tool_id, amount):
        return self.inventory_current.get(tool_id, 0) >= amount
    def tool_reserved_for_delivery(self, tool_id, amount):
            self.inventory_current[tool_id] -= amount


