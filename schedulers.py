import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

def tools_to_df(tools):
	ids = []
	amount = []
	cost = []
	weight = []
		
	for tool in tools:
		ids.append(tool.id)
		amount.append(tool.amount)
		cost.append(tool.cost) 
		weight.append(tool.weight)

	df = pd.DataFrame({
		'id': ids,
		'amount': amount,
		'cost': cost,
		'weight': weight,
		})
	return df

def requests_to_df(requests):
	ids = []
	locid = []
	fromDay = []
	toDay = []
	numDays = []
	toolCount = []
	toolid = []
		
	for request in requests:
		ids.append(request.id)
		locid.append(request.locid)
		fromDay.append(request.fromDay) 
		toDay.append(request.toDay)
		numDays.append(request.numDays)
		toolid.append(request.toolid) 
		toolCount.append(request.toolCount)

	df = pd.DataFrame({
		'id': ids,
		'locid': locid,
		'fromDay': fromDay,
		'toDay': toDay,
		'numDays': numDays,
		'toDay': toDay,
		'toolid': toolid, 
		'toolCount': toolCount, 
		})
	df['arrivalDay'] = np.nan
	df['departureDay'] = np.nan
	return df

def calc_tools_per_day(df_tools, df_requests):
	latest_departure = max(df_requests['departureDay'])
	num_tools = len(df_tools)
	
	returnvalue = np.zeros((num_tools, latest_departure), dtype = 'int')

	for index, row in df_requests.iterrows():
		arrivalDay = row['arrivalDay']
		departureDay = row['departureDay']
		toolId = row['toolid']
		toolCount = row['toolCount']

		for day in range(arrivalDay, departureDay):
			returnvalue[toolId - 1, day -1] += toolCount

	return returnvalue

def plan(tool, requests, num_days):
	tools_per_day = np.zeros(num_days, dtype = 'int')
	
	num_tools = tool['amount']
	requests.sort_values(by = ['fromDay', 'toolCount'], ascending = [True, False], inplace = True)
	returnValue = pd.DataFrame()

	for index, row in requests.iterrows():
		arrivalDay = int(row['fromDay'])
		departureDay = arrivalDay + int(row['numDays'])
		toolCount = int(row['toolCount'])
		
		while arrivalDay <= int(row['toDay']):
			used_tools = tools_per_day[arrivalDay - 1]
			if (used_tools + toolCount) <= num_tools:
				row['arrivalDay'] = arrivalDay
				row['departureDay'] = arrivalDay + row['numDays']
		
				for day in range(arrivalDay, departureDay):
					tools_per_day[day -1] += toolCount

				returnValue.append(row)
				break

			arrivalDay += 1

		if arrivalDay > int(row['toDay']):
			print('scheduling not succesfull!')

	usedTools = max(tools_per_day)
	print('Tools used (id: ' + str(tool['id']) + ') = ' + str(usedTools) + ' of allowed ' + str(num_tools))
	print(returnValue)
	return returnValue

def naive(tools, requests, num_days):
	df_tools = tools_to_df(tools)	
	df_requests = requests_to_df(requests)	

	for index, row in df_tools.iterrows():
		toolid = row['id']
		selected = df_requests[df_requests['toolid'] == toolid]
		plan(row, selected, num_days)
	
	return df_tools, df_requests