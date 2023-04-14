from ortools.linear_solver import pywraplp

tools = [
    {'ID': 1, 'Size': 1, 'number_used': 0, 'max_available': 10, 'unitcost': 1},
    {'ID': 2, 'Size': 2, 'number_used': 0, 'max_available': 5, 'unitcost': 2},
    # Add data for the remaining tools
]

schedule = [
    {'ID': 1, 'Location': 1, 'delivery_day': 1, 'pickup_day': 2, 'tool_id': 1, 'number_required_tools': 1},
    {'ID': 2, 'Location': 2, 'delivery_day': 2, 'pickup_day': 3, 'tool_id': 2, 'number_required_tools': 2},
    # Add data for the remaining schedule entries
]

calc_distance = [
    [0, 10, 20, 30],
    [10, 0, 15, 25],
    [20, 15, 0, 14],
    [30, 25, 14, 0]
]

vehicle_cost = 100
vehicle_capacity = 5

locations = list(set([x['Location'] for x in schedule]))

solver = pywraplp.Solver.CreateSolver('Gurobi')


tool = {}
for i in range(len(tools)):
    tool[i] = solver.IntVar(0, tools[i]['max_available'], 'tool_%i' % i)

visit = {}
day = {}
order = {}
for j in locations:
    visit[j] = solver.IntVar(0, 1, 'visit_%i' % j)
    day[j] = solver.IntVar(0, max([x['delivery_day'] for x in schedule]), 'day_%i' % j)
    order[j] = solver.IntVar(0, len(locations), 'order_%i' % j)

travel = {}
for i in locations:
    for j in locations:
        if i != j:
            travel[i,j] = solver.IntVar(0, 1, 'travel_%i_%i' % (i,j))
#The dicision variables



# The constraints
# Tool constraints
for i in range(len(tools)):
    # The number of tools assigned to a vehicle cannot exceed the maximum available
    solver.Add(tool[i] <= tools[i]['max_available'])
    # The number of tools assigned to a location cannot be less than the number of required tools for that location
    solver.Add(tool[i] >= sum([x['number_required_tools'] for x in schedule if x['Location'] == j and x['tool_id'] == i]) for j in locations)
    # The number of tools assigned to a tool type cannot be less than the total number of required tools across all locations
    solver.Add(tool[i] >= sum([x['number_required_tools'] for x in schedule if x['tool_id'] == i]))

# Visit and day constraints
for j in locations:
    # The sum of the number of tools assigned to a location cannot exceed the vehicle capacity times the number of days visited
    solver.Add(sum([tool[x['tool_id']] * x['number_required_tools'] for x in schedule if x['Location'] == j]) <= vehicle_capacity * day[j] * visit[j])
    # The sum of the number of days visited cannot exceed 1 (i.e., the vehicle must visit all locations exactly once)
    solver.Add(sum([visit[i] * day[i] for i in locations]) <= 1)
    # The order of visited locations is determined by the day they are visited (i.e., order[j] = day[j])
    solver.Add(sum([visit[i] * day[i] for i in locations]) >= order[j])
    # The visit must happen within the customer's time window
    solver.Add(day[j] >= customer_time_window[j]['start'])
    solver.Add(day[j] <= customer_time_window[j]['end'])

# Travel constraints
for i in locations:
    for j in locations:
        if i != j:
            # If a vehicle travels from i to j, then the corresponding travel variable must be 1
            solver.Add(travel[i,j] + travel[j,i] <= 1)
            # If a vehicle travels from i to j, then it must visit j after visiting i
            solver.Add(order[i] + 1 - len(locations) * (1 - travel[i,j]) <= order[j])
            # The sum of the distances between visited locations cannot exceed the maximum travel distance of the vehicle
            solver.Add(sum([calc_distance[i][j] * travel[i,j] for i in locations for j in locations]) <= vehicle_cost)

# Tool pickup and delivery constraints
for i in range(len(tools)):
    for j in locations:
        # A tool can be loaded at the depot and unloaded at a customer
        solver.Add(tool[i] >= sum([x['number_required_tools'] for x in schedule if x['Location'] == j and x['tool_id'] == i and x['task_type'] == 'delivery']) - sum([x['number_required_tools'] for x in schedule if x['Location'] == j and x['tool_id'] == i and x['task_type'] == 'pickup']))
        # Each request asks for a number of tools of one kind to be present at the customer for a given number of consecutive days
        for k in range(customer_time_window[j]['start'], customer_time_window[j]['end'] + 1):
            solver.Add(sum([x['number_required_tools'] for x in schedule if x['Location'] == j and x['tool_id'] == i and x['task_type'] == 'delivery' and x['day'] == l]) == sum([x['number_required_tools']]))


# Define the objective function
# Define objective function
objective = solver.Objective()

# Add distance cost
# Calculate the distance between locations i and j, multiply it by the decision variable travel[i,j], and sum over all i and j
# This gives us the total distance traveled by the vehicles in the solution
distance_cost = solver.Sum([calc_distance[i][j] * travel[i,j] for i in locations for j in locations])
# Set the coefficient of the distance cost in the objective function to be the distance cost coefficient specified
objective.SetCoefficient(distance_cost, distance_cost_coefficient)

# Add day cost
# Sum over the decision variable day[i] for all locations i
# This gives us the total number of days used by the vehicles in the solution
day_cost = solver.Sum([day[i] for i in locations])
# Set the coefficient of the day cost in the objective function to be the day cost coefficient specified
objective.SetCoefficient(day_cost, day_cost_coefficient)

# Add vehicle fixed cost
# Sum over the decision variable visit[i] for all locations i
# This gives us the total number of vehicles used in the solution
vehicle_cost = solver.Sum([visit[i] for i in locations])
# Set the coefficient of the vehicle fixed cost in the objective function to be the vehicle cost coefficient specified
objective.SetCoefficient(vehicle_cost, vehicle_cost_coefficient)

# Add tool holding cost
# Sum over the decision variable tool[i] for all tools i
# This gives us the total number of tools held in the solution
tool_holding_cost = solver.Sum([tool[i] for i in range(len(tools))])
# Set the coefficient of the tool holding cost in the objective function to be the tool holding cost coefficient specified
objective.SetCoefficient(tool_holding_cost, tool_holding_cost_coefficient)

# Add tool request cost
# Sum over all schedules x, where x is a dictionary containing the tool ID and the number of required tools
# For each schedule, subtract the decision variable tool[x['tool_id']] from the number of required tools
# This gives us the total number of unfulfilled tool requests in the solution
tool_request_cost = solver.Sum([x['number_required_tools'] - tool[x['tool_id']] for x in schedule])
# Set the coefficient of the tool request cost in the objective function to be the tool request cost coefficient specified
objective.SetCoefficient(tool_request_cost, tool_request_cost_coefficient)

# Set optimization direction (minimization)
# Specify that we want to minimize the objective function
objective.SetMinimization()


# Solve the problem
status = solver.Solve()

# Print the status of the solver
if status == pywraplp.Solver.OPTIMAL:
    print('Optimal solution found!')
elif status == pywraplp.Solver.FEASIBLE:
    print('Feasible solution found.')
elif status == pywraplp.Solver.INFEASIBLE:
    print('The problem is infeasible.')
elif status == pywraplp.Solver.UNBOUNDED:
    print('The problem is unbounded.')
else:
    print('The solver could not find a feasible solution.')

# Print the objective value
print('Objective value:', solver.Objective().Value())