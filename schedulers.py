import numpy as np

def tools_to_arr(tools):
	returnValue = np.zeros((len(tools), 4), dtype = 'int')
		
	for tool in tools:
		id = tool.id
		returnValue[id -1, ] = [tool.id, tool.amount, tool.cost, tool.weight]
	return returnValue

def requests_to_arr(requests):
	returnValue = np.zeros((len(requests), 7), dtype = 'int')
		
	for request in requests:
		id = request.id
		returnValue[id -1, ] = [request.id, request.locid, request.fromDay, request.toDay, request.numDays, request.toolid, request.toolCount]
	return returnValue

def naive(tools, requests, num_days):
	arr_requests = requests_to_arr(requests)
	arr_tools = tools_to_arr(tools)

	tools = np.zeros((len(arr_tools), 5), dtype = 'int')
	schedule = np.zeros((len(arr_requests), 6), dtype = 'int')
	tools_per_day = np.zeros((len(arr_tools), num_days), dtype = 'int')

	ind_requests = np.lexsort((-arr_requests[:, 6], arr_requests[:, 2]))

	for i in ind_requests:
		arrivalDay = arr_requests[i, 2]
		toolId = arr_requests[i, 5]
		toolCount = arr_requests[i, 6]
		toDay = arr_requests[i, 3]
		numTools = arr_tools[toolId - 1, 1]

		while arrivalDay <= toDay:
			used_tools = tools_per_day[toolId - 1, arrivalDay - 1]
			if (used_tools + toolCount) <= numTools:
				departureDay = arrivalDay + arr_requests[i, 4]
				schedule[i, ] = [arr_requests[i, 0], arr_requests[i, 1], arrivalDay, departureDay, toolId, toolCount]
		
				for day in range(arrivalDay, departureDay):
					tools_per_day[toolId - 1, day -1] += toolCount
				break

			arrivalDay += 1

		if arrivalDay > toDay:
			raise Exception('Naive scheduling failed, needs more tools than available')

	usedTools = np.amax(tools_per_day, axis = 1)

	for j in range(len(arr_tools)):
		tools[j, 0] = arr_tools[j, 0] 
		tools[j, 1] = arr_tools[j, 1] 
		tools[j, 2] = usedTools[j] 
		tools[j, 3] = arr_tools[j, 2] 
		tools[j, 4] = arr_tools[j, 3] 

	return tools, schedule