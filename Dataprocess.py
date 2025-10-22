import pandas as pd
from collections import defaultdict
import datetime
import pickle

# 定义你的 GTFS 数据文件夹路径
# 注意末尾的正斜杠 /
gtfs_path = 'C:/Users/Funzhou/Downloads/gtfs_subway/' # 根据你的实际路径修改

# 加载我们需要的文件
try:
    stops = pd.read_csv(f'{gtfs_path}stops.txt')
    stop_times = pd.read_csv(f'{gtfs_path}stop_times.txt')
    transfers = pd.read_csv(f'{gtfs_path}transfers.txt')
except FileNotFoundError as e:
    print(f"文件未找到: {e}. 请确保 GTFS 文件在正确的路径下。")
    exit()

print("数据加载成功！")
print(f"总共有 {len(stops)} 个站台。")
print(f"总共有 {len(stop_times)} 条停靠记录。")
print(f"总共有 {len(transfers)} 条换乘规则。")
graph = defaultdict(list)
for stop_id in stops['stop_id']:
    graph[stop_id] = []
# 时间字符串（HH:MM:SS）转为秒的辅助函数
def time_to_seconds(time_str):
    try:
        # 有些GTFS数据时间会超过24:00:00，例如 25:10:00
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except (ValueError, TypeError):
        return 0

print("开始构建乘车边...")

# 对 stop_times 按 trip_id 分组，并按 stop_sequence 排序
# 这样可以保证我们处理的是同一趟车、并且是按顺序的站点
stop_times_sorted = stop_times.sort_values(by=['trip_id', 'stop_sequence'])

# 使用 groupby 来高效处理每一趟行程
for trip_id, trip_group in stop_times_sorted.groupby('trip_id'):
    # 将每一趟行程的停靠点转换为列表
    trip_stops = trip_group.to_dict('records')
    
    # 遍历行程中的每一站，除了最后一站
    for i in range(len(trip_stops) - 1):
        from_stop = trip_stops[i]
        to_stop = trip_stops[i+1]
        
        # 获取出发和到达站的 ID
        from_stop_id = from_stop['stop_id']
        to_stop_id = to_stop['stop_id']
        
        # 计算权重（时间）
        departure_time_sec = time_to_seconds(from_stop['departure_time'])
        arrival_time_sec = time_to_seconds(to_stop['arrival_time'])
        
        # 处理跨天的情况
        if arrival_time_sec < departure_time_sec:
            # 这种情况在实际数据中较少，但最好处理
            # 简单处理，可以假设是隔夜，但更精确的需要日历数据
            # 这里我们先假设不会出现或差异极小
            pass

        travel_time = arrival_time_sec - departure_time_sec
        
        # 确保旅行时间是正数
        if travel_time > 0:
            # 添加边到图中
            graph[from_stop_id].append((to_stop_id, travel_time))

print(f"乘车边构建完成！图中添加了大量连接。")
print("开始构建换乘边...")

# 1. 处理 transfers.txt 中的显式换乘
for index, row in transfers.iterrows():
    from_stop_id = row['from_stop_id']
    to_stop_id = row['to_stop_id']
    
    # 我们只关心可以换乘的情况 (transfer_type != 3)
    if row['transfer_type'] != 3:
        # 权重是 min_transfer_time
        # 如果没有提供时间，给一个默认值，比如2分钟 (120秒)
        transfer_time = row['min_transfer_time'] if pd.notna(row['min_transfer_time']) else 120
        graph[from_stop_id].append((to_stop_id, transfer_time))

# 2. 处理基于 parent_station 的隐式换乘 (非常重要！)
# 首先，筛选出有 parent_station 的站台
stops_with_parent = stops[stops['parent_station'].notna()]
# 按 parent_station 分组
for parent_station_id, group in stops_with_parent.groupby('parent_station'):
    station_stop_ids = group['stop_id'].tolist()
    
    # 在同一个父站下的所有站台之间，创建双向的换乘边
    if len(station_stop_ids) > 1:
        for i in range(len(station_stop_ids)):
            for j in range(i + 1, len(station_stop_ids)):
                from_stop_id = station_stop_ids[i]
                to_stop_id = station_stop_ids[j]
                
                # 给一个默认的站内步行换乘时间，比如3分钟 (180秒)
                transfer_time = 180 
                
                # 添加双向边
                graph[from_stop_id].append((to_stop_id, transfer_time))
                graph[to_stop_id].append((from_stop_id, transfer_time))

print("换乘边构建完成！")
total_nodes = len(graph)
total_edges = sum(len(edges) for edges in graph.values())
print(f"\n图构建完成！")
print(f"总节点数: {total_nodes}")
print(f"总边数: {total_edges}")

# 定义要保存的文件名
graph_filename = 'metro_graph.pkl'

# 开始保存 graph 对象
print(f"\n正在将构建好的图保存到文件: {graph_filename} ...")

# 使用 'wb' 模式打开文件，'w' 代表写入, 'b' 代表二进制模式
with open(graph_filename, 'wb') as f:
    # 使用 pickle.dump 将 graph 对象写入文件 f
    pickle.dump(graph, f)

print("保存成功！")