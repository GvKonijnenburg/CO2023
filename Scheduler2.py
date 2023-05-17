import numpy as np
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
class Schedule:
    def __init__(self, instance):
        self.scheduledRequests = [] # list of tuple (req, delivery day, pickup day)
        self.scheduleDaily = {}
        self.max_daily_use = np.zeros(len(instance.tools), dtype=int)

    def calculate_inventory_used(self, instance):
        daily_inventory_used = np.zeros((len(instance.tools), instance.DAYS))
        for (req, deliveryDay,pickupDay) in self.scheduledRequests:
            daily_inventory_used[req.toolID - 1][deliveryDay -1 : pickupDay-1] += req.toolCount

        print(daily_inventory_used)
        for t, tool in enumerate(daily_inventory_used):
            self.max_daily_use[t] = max(tool)

    def make_day_schedule(self):
        self.scheduleDaily = {}
        for (req,deliveryDay,pickupDay) in self.scheduledRequests:
            if deliveryDay in self.scheduleDaily:
                self.scheduleDaily[deliveryDay].append(req.ID)
            else:
                self.scheduleDaily[deliveryDay] = [req.ID]

            if pickupDay in self.scheduleDaily:
                self.scheduleDaily[pickupDay].append(-req.ID)
            else:
                self.scheduleDaily[pickupDay] = [-req.ID]

def create_model(days, toolAmount, requestsDf):
    model = pyo.ConcreteModel()

    model.i = pyo.Set(initialize=requestsDf.index.array) # request indexer
    model.j = pyo.Set(initialize=range(1, days+1)) # day indexer

    model.fromDay = pyo.Param(model.i, initialize=requestsDf['fromDay'], within=pyo.PositiveIntegers)
    model.toDay = pyo.Param(model.i, initialize=requestsDf['toDay'], within=pyo.PositiveIntegers)
    model.toolAmountRequest = pyo.Param(model.i, initialize=requestsDf['toolCount'], within=pyo.PositiveIntegers)
    model.numDays = pyo.Param(model.i, initialize=requestsDf['numDays'], within=pyo.PositiveIntegers)

    # decision variables
    model.x = pyo.Var(model.i, model.j, domain=pyo.Binary) # delivery req i on day j
    model.y = pyo.Var(model.i, model.j, domain=pyo.Binary)  # pickup req i on day j

    # helper variables
    def delivery_interval(model, i):
        return (model.fromDay[i], model.toDay[i])
    model.deliveryDay = pyo.Var(model.i, domain=pyo.NonNegativeIntegers,
                            bounds=delivery_interval)
    model.toolEndOfDay = pyo.Var(range(days+1), domain=pyo.NonNegativeIntegers, bounds=(0, toolAmount))

    # for each req delivery only once
    def delivery_once(model, i):
        return sum(model.x[i, j] for j in model.j) == 1
    model.deliveryOnce = pyo.Constraint(model.i, rule=delivery_once)

    # for each req pickup only once
    def pickup_once(model, i):
        return sum(model.y[i, j] for j in model.j) == 1
    model.pickupOnce = pyo.Constraint(model.i, rule=pickup_once)

    def delivery_on_right_day(model,i):
        return model.deliveryDay[i] == sum(j*model.x[i,j] for j in model.j)
    model.rightDeliveryDay = pyo.Constraint(model.i, rule=delivery_on_right_day)

    # def delivery_lb(model,i):
    #     return model.fromDay[i] <= sum(j*model.x[i,j] for j in model.j)
    # model.rightDeliveryDay = pyo.Constraint(model.i, rule=delivery_lb)
    #
    # def delivery_ub(model,i):
    #     return model.toDay[i] >= sum(j*model.x[i,j] for j in model.j)
    # model.rightDeliveryDay = pyo.Constraint(model.i, rule=delivery_lb)

    def pickup_on_right_day(model,i):
        return model.deliveryDay[i] + model.numDays[i] == sum(j*model.y[i,j] for j in model.j)
    model.rightPickUpDay = pyo.Constraint(model.i, rule=pickup_on_right_day)

    # maintain inventory
    def inventoryDay(model, j):
        return model.toolEndOfDay[j] == \
            model.toolEndOfDay[j-1]-sum(model.toolAmountRequest[i]*(model.x[i,j]-model.y[i,j]) for i in model.i)
    model.inventory = pyo.Constraint(model.j, rule=inventoryDay)

    def maxdeli(model, j):
        return sum(model.toolAmountRequest[i]*(model.x[i,j]) for i in model.i) <= model.toolEndOfDay[j-1]
    model.maxdeli = pyo.Constraint(model.j, rule=maxdeli)

    model.objective = pyo.Objective(expr=model.toolEndOfDay[0], sense=pyo.minimize)
    return model

def make_schedule_ILP(instance, log=False):
    instance.requestsDf['deliveryDay'] = None

    solver = pyo.SolverFactory('gurobi')
    days = instance.DAYS

    schedule = Schedule(instance)
    schedule.scheduledRequests = []
    for tool in instance.tools:
        toolAmount = tool.amount
        requestsOfTool = instance.requestsDf[instance.requestsDf['toolID'] == tool.ID]
        model = create_model(days, toolAmount, requestsOfTool)
        result = solver.solve(model)

        if result.solver.termination_condition == pyo.TerminationCondition.optimal:
            if log:
                print("toolID:", tool.ID)
                for d in range(days+1):
                    print("day:", d, "maxTools:", toolAmount, "toolUsed:", model.toolEndOfDay[d].value)
                print("total tool used:", pyo.value(model.objective))
            for i in model.i:
                # deliveryDay = int(sum(j*model.x[i,j].value for j in model.j))
                deliveryDay = int(model.deliveryDay[i].value)
                request = instance.requests[i - 1]
                schedule.scheduledRequests.append((request, deliveryDay, deliveryDay+request.numDays))
                instance.requestsDf.loc[i, 'deliveryDay'] = deliveryDay
        else:
            print("Stopcondition:", result.solver.termination_condition)

    instance.requestsDf['pickupDay'] = instance.requestsDf.deliveryDay + instance.requestsDf.numDays
    schedule.calculate_inventory_used(instance)
    schedule.make_day_schedule()

    return schedule
