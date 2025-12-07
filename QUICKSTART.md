# 快速开始指南 (Quick Start Guide)

## 📋 项目文件说明

| 文件 | 功能说明 |
|------|---------|
| `Dataprocess.py` | 数据处理脚本 - 从GTFS数据生成图 |
| `Dijkstra.py` | 算法实现 - Dijkstra最短路径算法 |
| `GUI.py` | 图形界面 - 用户友好的GUI应用 |
| `extract_station_names.py` | 辅助脚本 - 提取站点名称映射 |
| `metro_graph.pkl` | 图数据文件（自动生成） |
| `station_names.pkl` | 站点名称映射文件（自动生成） |

## 🚀 快速启动步骤

### 第一步：准备GTFS数据
1. 从 [MTA官网](http://new.mta.info/developers) 下载纽约地铁GTFS数据
2. 解压到一个文件夹（如 `gtfs_subway/`）
3. 确保包含以下文件：
   - `stops.txt` - 站点信息
   - `stop_times.txt` - 停靠时间表
   - `transfers.txt` - 换乘规则
   - `trips.txt` - 行程信息

### 第二步：修改数据路径
编辑 `Dataprocess.py`，修改第6行的 `gtfs_path`：
```python
gtfs_path = '/你的实际GTFS文件夹路径/'
```

### 第三步：生成图数据（仅需一次）
```bash
python3 Dataprocess.py
```
等待处理完成，会生成 `metro_graph.pkl` 文件（可能耗时5-10分钟）。

### 第四步：提取站点名称（可选，推荐）
```bash
python3 extract_station_names.py
```
这会生成 `station_names.pkl` 文件，使GUI显示更友好的站点名称。

### 第五步：启动图形界面
```bash
python3 GUI.py
```

## 💡 使用示例

### 命令行查询（Dijkstra.py）
编辑 `Dijkstra.py` 中的查询参数：
```python
start_station = '127S'  # 起点
end_station = '137S'    # 终点
```

然后运行：
```bash
python3 Dijkstra.py
```

### 图形界面查询（GUI.py）
1. 从下拉菜单选择起点和终点
2. 点击"查询最短路线"按钮
3. 查看详细的路线和耗时信息

## 📊 数据处理流程

```
GTFS数据文件
    ↓
Dataprocess.py (数据预处理)
    ↓
metro_graph.pkl (图数据)
    ↓
Dijkstra.py / GUI.py (查询)
    ↓
最短路径结果
```

## ⚙️ 依赖库

```bash
pip install pandas
```

其他库都是Python内置的：
- `pickle` - 序列化数据
- `heapq` - 优先队列
- `tkinter` - GUI框架
- `threading` - 多线程

## 🔍 常见问题排查

### 问题1：FileNotFoundError - metro_graph.pkl
**解决方案：** 运行 `Dataprocess.py` 生成图数据文件

### 问题2：找不到GTFS文件
**解决方案：** 
- 检查 `gtfs_path` 的路径是否正确
- Windows用户使用反斜杠或原始字符串：`r'C:\path\to\gtfs\'`
- macOS/Linux用户使用正斜杠：`'/path/to/gtfs/'`

### 问题3：处理速度很慢
**解决方案：** 这是正常的，大规模GTFS数据处理确实需要时间
- 如果超过30分钟仍未完成，检查磁盘空间和内存
- Dataprocess.py 只需运行一次

### 问题4：GUI没有显示站点名称
**解决方案：** 运行 `extract_station_names.py` 生成站点名称文件

### 问题5：查询返回"无法到达"
**解决方案：**
- 确认站点ID是正确的（来自stops.txt）
- 检查这两个站点是否确实有连接路径
- 查看Dijkstra.py示例中使用的站点ID

## 📈 性能指标

以纽约地铁数据为例：
- 总站点数：约400+
- 总边数：约10000+
- 单次查询时间：通常 < 1秒
- 图数据文件大小：约5-10MB

## 🛠️ 代码结构

### Dijkstra.py
```python
def dijkstra(graph, start_node, end_node):
    # 返回: (最短时间, 路径列表)
    return distance[end_node], path
```

### GUI.py
- `MetroRoutePlannerGUI` - 主窗口类
- `load_graph()` - 加载图和站点数据
- `search_route()` - 路线查询逻辑
- `_perform_search()` - 后台计算（线程）

## 🎯 下一步扩展

1. **地图可视化** - 使用folium或plotly显示路线地图
2. **多路线选择** - 除最短时间外，显示替代路线
3. **实时数据** - 集成MTA实时API显示列车位置
4. **收藏功能** - 保存常用路线
5. **数据导出** - 将查询结果导出为PDF/CSV
6. **主题定制** - 添加暗黑主题等UI定制选项

## 📝 许可证

MIT License - 详见项目README.md

## 📧 问题反馈

如有问题或建议，欢迎提交Issue或Pull Request！
