import heapq
import pandas as pd
import distance_functions
import copy
import depot_functions
import vehicle_functions

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
def can_order_be_moved(order,master_order_list,day):
    req_id = order[2]
    orders_to_update = master_order_list[master_order_list['req_id'] == req_id]
    delivery_can_be_moved,pick_up_can_be_moved = None,None
    for request, route_id in orders_to_update.iterrows():
        if route_id['order_type'] == "D":
            if route_id['max_delivery_day'] >= day +1:
                delivery_can_be_moved = True
        if route_id['order_type'] == "P":
            if route_id['order_day'] +1 <= 10:
                pick_up_can_be_moved = True
    if delivery_can_be_moved and pick_up_can_be_moved:
        master_order_list.loc[master_order_list['req_id'] == req_id, 'order_day'] += 1
    return delivery_can_be_moved,pick_up_can_be_moved,master_order_list

def order_mover(order_information, depot, distance_cost, vehicle_operation_cost,master_order_list,vehicle_capacity,day):
    was_an_order_moved = False
    dummy_depot = copy.deepcopy(depot)
    order_must_be_completed_list = []
    for order in order_information.itertuples():
        tool_id = order[6]
        amount_requested = order[7]
        dummy_dict = {tool_id:amount_requested}
        if dummy_depot.inventory_check(tool_id, amount_requested):
            depot_functions.process_tools(dummy_depot,dummy_dict)
        else:
            was_an_order_moved = True
            delivery_can_be_moved, pick_up_can_be_moved,master_order_list = can_order_be_moved(order,master_order_list,day)
            if delivery_can_be_moved and pick_up_can_be_moved:
                order_information = order_information.drop(order.Index)
            if not delivery_can_be_moved or not pick_up_can_be_moved:
                v_id = order[1]
                distance_traveled = order[-2]
                vehicle_load = order[-3]
                vehicle_route = [depot.loc, order[3], depot.loc]
                request_fullfilled = [order[-1]]
                tool_id = order[6]
                amount_requested = order[7]
                tools_in_vehicle = {tool_id: amount_requested}
                vehicle_i = vehicle_functions.init_vehicle(v_id, distance_traveled, vehicle_load, vehicle_route,
                                                           request_fullfilled, tools_in_vehicle, distance_cost,
                                                           vehicle_operation_cost)
                order_must_be_completed_list.append(vehicle_i)

    return order_information,master_order_list,was_an_order_moved,order_must_be_completed_list
def get_best_combinations(large_order_list, distance_matrix):
    best_combinations = {}
    for req_id, req_group in large_order_list.groupby('req_id'):
        for tool_id, tool_group in req_group.groupby('tool_id'):
            deliveries = tool_group[tool_group['order_type'] == 'D']
            pickups = tool_group[tool_group['order_type'] == 'P']
            best_combination = None
            min_distance = float('inf')
            for _, delivery in deliveries.iterrows():
                for _, pickup in pickups.iterrows():
                    if abs(pickup['tool_Count']) >= delivery['tool_Count']:
                        distance = distance_functions.calculate_distance_between_points(distance_matrix,
                                                                                        delivery['loc_id'],
                                                                                        pickup['loc_id'])
                        if distance < min_distance:
                            best_combination = (delivery, pickup)
                            min_distance = distance
            if best_combination:
                if req_id in best_combinations:
                    best_combinations[req_id].append(best_combination)
                else:
                    best_combinations[req_id] = [best_combination]
    return best_combinations
def net_inventory_required(orders_to_complete):
    delivery_requests = orders_to_complete[orders_to_complete['tool_Count'] > 0]
    pickup_requests = orders_to_complete[orders_to_complete['tool_Count'] < 0]
    delivery_counts = delivery_requests.groupby('tool_id')['tool_Count'].sum()
    pickup_counts = pickup_requests.groupby('tool_id')['tool_Count'].sum()
    net_inventory_required = delivery_counts.add(pickup_counts, fill_value=0)
    return net_inventory_required,delivery_requests,pickup_requests

