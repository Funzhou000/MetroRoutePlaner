import pickle
import heapq

# --- Dijkstra 算法实现 ---
# (这就是你将要专注于编写的部分)

def reconstruct_path(previous_nodes, start_node, end_node):
    path=[]
    current_node=end_node
    while current_node is not None:
        path.append(current_node)
        current_node=previous_nodes.get(current_node)
    path.reverse()
    if path and path[0] == start_node:
        return path


def dijkstra(graph,start_node,end_node):
    distance={node:float('inf')for node in graph}
    distance[start_node]=0
    previous_node={node:None for node in graph}#字典推导式，遍历graph所有键传到node，再将node对应的值赋值为None
    pq=[(0,start_node)]
    while pq:
        current_distance,current_node=heapq.heappop(pq)
        if current_distance>distance[current_node]:
            continue
        if current_node==end_node:#end while
            break
        if current_node in graph:
            for neighbor, weight in graph[current_node]:
                newtime=weight+current_distance
                if newtime<distance[neighbor]:
                    distance[neighbor]=newtime
                    previous_node[neighbor]=current_node
                    heapq.heappush(pq(newtime,neighbor))  
    path=reconstruct_path(previous_node,start_node,end_node)          
    if distance[end_node] == float('infinity'):
        return None, None  
    return distance[end_node],path

# --- 主程序逻辑 ---
def main():
    graph_filename = 'metro_graph.pkl'
    
    print(f"正在从 {graph_filename} 加载地铁网络图...")
    try:
        # 使用 'rb' 模式打开文件, 'r' 代表读取, 'b' 代表二进制
        with open(graph_filename, 'rb') as f:
            # 使用 pickle.load 从文件 f 中读取并恢复 graph 对象
            graph = pickle.load(f)
        print("图加载成功！")
        print(f"总节点数: {len(graph)}")
    except FileNotFoundError:
        print(f"错误: 找不到图文件 '{graph_filename}'。")
        print("请先运行 Dataprocess.py 来生成该文件。")
        return # 退出程序

    # --- 在这里，你可以调用你的 Dijkstra 算法 ---
    # 示例：找一个起点和终点 (你需要从 stops.txt 中找到有效的 stop_id)
    start_station = '127S' # 示例: Rector St, 1号线
    end_station = '137S'   # 示例: 86th St, 4/5/6号线
    
    print(f"\n正在计算从 {start_station} 到 {end_station} 的最短路径...")
    
    total_time, path = dijkstra(graph, start_station, end_station)
    
    # 这里可以添加代码来打印结果
    if total_time is None:
    # 如果 total_time 是 None，说明路径没找到或者输入有误
        print(f"无法从 {start_station} 找到到达 {end_station} 的路径。")
    else:
        # 只有当 total_time 不是 None 的时候，我们才能安全地使用它
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        print(f"找到最短路径！")
        print(f"  -> 最短时间: {total_time} 秒 (大约 {minutes} 分 {seconds} 秒)")
        print(f"  -> 路径 (部分站点): {' -> '.join(path[:5])}...{' -> '.join(path[-3:])}")
        # 如果想看完整路径，可以 print(f"  -> 完整路径: {path}")


# 当直接运行这个脚本时，执行 main 函数
if __name__ == "__main__":
    main()