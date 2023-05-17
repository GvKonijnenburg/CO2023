import global_schedule
import pandas as pd
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
def makedf (instance):
    columns = ['ID','locID','fromDay', 'toDay', 'numDays', 'toolID', 'toolCount','weight']
    df = pd.DataFrame(data=None, columns=columns)
    for r in instance.requests:
        df.loc[r.ID] = [r.ID,r.locID, r.fromDay, r.toDay, r.numDays, r.toolID, r.toolCount,
                    instance.tools[r.toolID - 1].weight * r.toolCount]
    df.set_index('ID',inplace=True)
    return df


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
                    instance.coordinates[int(co_type[0])]=[int(co_type[1]), int(co_type[2])]
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
