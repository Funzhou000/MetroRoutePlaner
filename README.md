# 纽约地铁最短路径规划器 (NYC Metro Route Planner)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个基于 Dijkstra 算法实现的命令行工具，用于计算纽约市地铁网络中任意两个站台之间的最快（时间最短）路线。

## 项目的诞生

这个项目的想法源于我刚学完 **Dijkstra（戴克斯特拉）算法**，渴望能将其应用于解决一个真实世界的问题。在 AI 的帮助下，我了解到“计算地铁最优路径”是一个绝佳的实践机会，于是这个项目便应运而生。

在数据源的选择上，我最初考虑使用新加坡地铁的数据，但在一番调研后，发现 **纽约 MTA (Metropolitan Transportation Authority)** 提供的 **GTFS (General Transit Feed Specification)** 数据不仅信息详尽、结构标准，而且更新非常及时。这为构建一个精确的地铁网络模型提供了坚实的基础。

## 核心设计思路

面对从 MTA 下载的大量且结构复杂的 GTFS 数据，我意识到如果每次查询都重新处理一遍数据，将会非常低效。因为我的核心目标是实践 Dijkstra 算法，所以在 AI 的辅助下，我决定采用**两步走**的架构，将数据预处理与算法查询彻底分离：

1.  **数据预处理 (`Dataprocess.py`)**:
    *   **目的**: 将原始、分散的 GTFS 文本文件（`stops.txt`, `stop_times.txt` 等）转换成一个为 Dijkstra 算法量身定做的**图数据结构（邻接表）**。
    *   **实现**: 使用强大的 `pandas` 库高效地读取和处理数据，构建图的节点（站台）、边（乘车/换乘）和权重（时间）。
    *   **输出**: 将构建好的、巨大的图对象通过 `pickle` 库序列化，保存为一个二进制文件 (`metro_graph.pkl`)。这个过程耗时较长，但**只需执行一次**。

2.  **算法查询 (`Dijkstra.py`)**:
    *   **目的**: 快速响应用户的查询请求，计算最短路径。
    *   **实现**: 程序启动时，直接从 `metro_graph.pkl` 文件中反序列化加载已经处理好的图数据。然后，以用户指定的起/终点站台ID为输入，运行 Dijkstra 算法。
    *   **优势**: 这种方式极大地提升了查询效率，使得算法的执行和调试可以**瞬间**完成，无需等待漫长的数据处理过程。

## 技术栈与依赖库

*   **[Python 3](https://www.python.org/)**: 项目的主要编程语言。
*   **[Pandas](https://pandas.pydata.org/)**: 用于高效地读取、清洗和处理 GTFS 的 CSV 格式数据。
*   **[Pickle](https://docs.python.org/3/library/pickle.html)**: Python 内置库，用于序列化和反序列化 `graph` 对象，实现数据处理与算法的分离。
*   **[Heapq](https://docs.python.org/3/library/heapq.html)**: Python 内置库，用于实现 Dijkstra 算法中的优先队列，确保算法效率。

## 如何使用

#### 1. 环境准备

确保你已经安装了 Python 3 和 pip。

```bash
# 克隆本项目
git clone [你的项目仓库地址]
cd [项目目录]

# 安装依赖
pip install pandas
```

#### 2. 数据准备

1.  前往 [MTA GTFS 数据开发者页面](https://new.mta.info/developers/gtfs/google-transit-feed-specifications) 下载最新的 "Subway" 数据。
2.  解压下载的文件，并将所有 `.txt` 文件放入项目根目录下的 `gtfs_subway` 文件夹内。

#### 3. 运行项目

1.  **第一步：处理数据（只需运行一次）**
    ```bash
    python Dataprocess.py
    ```
    运行结束后，项目目录下会生成一个 `metro_graph.pkl` 文件。

2.  **第二步：查询路径**
    *   打开 `Dijkstra.py` 文件。
    *   参考 `stops.txt` 文件，修改 `main` 函数中的 `start_station` 和 `end_station` 变量为你想要查询的站台ID（注意区分方向，如 '127S' 代表南行站台）。
    *   运行查询脚本：
    ```bash
    python Dijkstra.py
    ```
    终端将会输出计算出的最短时间和路径。

## 学习与反思

这次的实践让我对 Dijkstra 算法的理解从理论层面深入到了实际应用层面，尤其是在处理真实世界中充满约束（如方向、换乘）的复杂网络时。

同时，我也初次体验到了一个现代化的软件开发流程雏形：**数据处理 -> 核心算法 -> 前端交互 -> 运维部署**。虽然这只是我的第一个项目，但这种分层、解耦的架构思想让我受益匪浅。

## 当前局限与未来展望

作为我的第一个个人项目，目前的功能还比较基础：
*   用户交互不友好，需要手动在代码中修改站台ID。
*   输出结果为站台ID，不够直观。

未来，我希望有机会对这个项目进行完善：
*   [ ] **构建一个简单的用户界面**（Web 或桌面应用），让用户可以通过输入站名来查询。
*   [ ] **实现站名到站台ID的自动转换**，并将结果以站名形式友好地展示出来。
*   [ ] **考虑实时数据**，将 GTFS-realtime 信息整合进来，提供更动态的路径规划。

---
感谢您的关注！