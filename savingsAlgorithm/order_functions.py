import pandas as pd
def order_vehicle_information(request,depot,distance_matrix):
    temp = request.copy()
    temp.loc[:, 'delivery_day'] = temp['pick_up_day']
    temp['tool_Count'] = -temp['tool_Count']
    order_request = pd.concat([request, temp], ignore_index=True)
    order_request['order_type'] = order_request['tool_Count'].apply(
        lambda x: 'D' if x > 0 else 'P')
    order_request = order_request.drop(['pick_up_day'],axis=1)
    order_request['vehicle_load'] = abs(order_request.apply(lambda x: depot.tools[x['tool_id']].size * x['tool_Count'], axis=1))
    order_request['distance_to_depot'] = order_request['loc_id'].apply(lambda x: distance_matrix[0][x])
    order_request = order_request.reset_index(drop=False)
    order_request = order_request.rename(columns={'index': 'order_id','delivery_day':'order_day'})
    order_request['order_id'] += 1
    order_request['route_id'] = order_request.apply(lambda request: request['req_id'] if request['order_type'] == 'D' else -request['req_id'], axis=1)
    return order_request
def master_order_list (global_schedule):
    master_order_list = pd.DataFrame.from_dict(global_schedule, orient='index')
    master_order_list = master_order_list.rename(columns={'id': 'req_id','locid':'loc_id', 'fromDay': 'delivery_day', 'toDay': 'max_delivery_day',
                             'toolid':'tool_id','toolCount':'tool_Count'})
    master_order_list['pick_up_day'] = master_order_list['delivery_day'] + master_order_list['numDays']
    index_delivery_day = master_order_list.columns.get_loc('delivery_day')
    master_order_list.insert(index_delivery_day + 1, 'pick_up_day', master_order_list.pop('pick_up_day'))
    master_order_list = master_order_list.drop('numDays', axis=1)
    return master_order_list