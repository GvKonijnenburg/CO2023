import numpy as np

def tools_to_arr(tools):
	num_tools = len(tools)
	returnValue = np.zeros((num_tools, 4), dtype = 'int')
		
	for tool in tools:
		returnValue[tool.id -1, ] = [tool.id, tool.amount, tool.cost, tool.weight]
	return returnValue

def requests_to_arr(requests):
	num_requests = len(requests)
	returnValue = np.zeros((num_requests, 7), dtype = 'int')
		
	for request in requests:
		returnValue[request.id -1, ] = [request.id, request.locid, request.fromDay, request.toDay, request.numDays, request.toolid, request.toolCount]
	return returnValue

def naive(tools, requests, num_days):
	arr_requests = requests_to_arr(requests)
	arr_tools = tools_to_arr(tools)

	# Initialize arrays
	num_tools = len(arr_tools)
	num_reqs = len(arr_requests)
	tools = np.zeros((num_tools, 5), dtype = 'int')
	schedule_arr = np.zeros((num_reqs, 6), dtype = 'int')
	tools_per_day_arr = np.zeros((num_tools, num_days), dtype = 'int')

	# Sort requests by priority, on first possible arrival day (ascending) and on number of requested tools (descending)
	ind_requests = np.lexsort((-arr_requests[:, 6], arr_requests[:, 2]))

	# Process requests
	for i in ind_requests:
		req_arrival_day = arr_requests[i, 2]
		req_tool_id = arr_requests[i, 5]
		req_tool_count = arr_requests[i, 6]
		req_latest_arrival_day = arr_requests[i, 3]
		req_num_tools = arr_tools[req_tool_id - 1, 1]

		while req_arrival_day <= req_latest_arrival_day:
			tools_used = tools_per_day_arr[req_tool_id - 1, req_arrival_day - 1]

			if (tools_used + req_tool_count) <= req_num_tools:
				req_departure_day = req_arrival_day + arr_requests[i, 4]
				schedule_arr[i, ] = [arr_requests[i, 0], arr_requests[i, 1], req_arrival_day, req_departure_day, req_tool_id, req_tool_count]
		
				for day in range(req_arrival_day, req_departure_day):
					tools_per_day_arr[req_tool_id - 1, day -1] += req_tool_count
				break

			req_arrival_day += 1

		if req_arrival_day > req_latest_arrival_day:
			raise Exception('Naive scheduling failed, needs more tools than available')

	# Update tools array with usage stats
	tools[:, 0:2] = arr_tools[:, 0:2]
	tools[:, 2] = np.amax(tools_per_day_arr, axis = 1)
	tools[:, 3:5] = arr_tools[:, 2:4]

	return tools, schedule_arr