#!/usr/bin/env python3
"""
NYC Metro Route Planner - 交互式命令行版本
Interactive Command-Line Version
"""

import pickle
import os
from Dijkstra import dijkstra
from datetime import datetime


class MetroRoutePlannerCLI:
    def __init__(self):
        self.graph = None
        self.station_names = {}
        self.history = []
        self.load_graph()
    
    def load_graph(self):
        """加载图数据"""
        try:
            with open('metro_graph.pkl', 'rb') as f:
                self.graph = pickle.load(f)
            print(f"✓ 图加载成功！共 {len(self.graph)} 个站点\n")
        except FileNotFoundError:
            print("✗ 错误：找不到 metro_graph.pkl")
            print("请先运行 Dataprocess.py 生成图文件\n")
            exit(1)
        
        # 加载站点名称
        try:
            with open('station_names.pkl', 'rb') as f:
                self.station_names = pickle.load(f)
        except:
            self.station_names = {sid: sid for sid in self.graph.keys()}
    
    def display_banner(self):
        """显示欢迎横幅"""
        print("\n" + "=" * 60)
        print("    NYC Metro Route Planner - 纽约地铁线路规划器")
        print("    Interactive Command-Line Version (交互式版)")
        print("=" * 60 + "\n")
    
    def list_stations(self, search_term=None):
        """列出所有站点"""
        stations = sorted(self.graph.keys())
        
        if search_term:
            search_term = search_term.lower()
            stations = [
                s for s in stations 
                if search_term in s.lower() or 
                   search_term in self.station_names.get(s, '').lower()
            ]
        
        if not stations:
            print("✗ 没有找到匹配的站点\n")
            return
        
        print(f"\n找到 {len(stations)} 个站点:\n")
        for i, sid in enumerate(stations[:50], 1):  # 最多显示50个
            name = self.station_names.get(sid, sid)
            if name != sid:
                print(f"{i:3d}. {sid:10s} - {name}")
            else:
                print(f"{i:3d}. {sid}")
        
        if len(stations) > 50:
            print(f"\n... 还有 {len(stations) - 50} 个站点")
        print()
    
    def search_route(self, start, end):
        """搜索路线"""
        if start not in self.graph or end not in self.graph:
            print(f"\n✗ 错误：无效的站点ID")
            return
        
        if start == end:
            print(f"\n✗ 错误：起点和终点不能相同")
            return
        
        print(f"\n⏳ 正在计算从 {start} 到 {end} 的最短路线...\n")
        
        total_time, path = dijkstra(self.graph, start, end)
        
        if total_time is None or path is None:
            print(f"✗ 无法找到从 {start} 到 {end} 的路线\n")
            return
        
        # 显示结果
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        print("✓ 找到最短路线！\n")
        print("=" * 70)
        print(f"起点: {start} - {self.station_names.get(start, start)}")
        print(f"终点: {end} - {self.station_names.get(end, end)}")
        print(f"总耗时: {total_time:.0f} 秒 (约 {minutes} 分 {seconds} 秒)")
        print(f"站点数: {len(path)}")
        print("=" * 70)
        
        print("\n完整路线:\n")
        for i, station_id in enumerate(path, 1):
            name = self.station_names.get(station_id, station_id)
            if name != station_id:
                print(f"{i:3d}. {station_id:10s} - {name}")
            else:
                print(f"{i:3d}. {station_id}")
        
        print("\n" + "=" * 70 + "\n")
        
        # 保存到历史
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            'time': timestamp,
            'start': start,
            'end': end,
            'duration': total_time,
            'path': path
        }
        self.history.append(history_entry)
    
    def show_history(self):
        """显示查询历史"""
        if not self.history:
            print("\n✗ 没有查询历史\n")
            return
        
        print(f"\n查询历史 (共 {len(self.history)} 条):\n")
        print("=" * 70)
        
        for i, entry in enumerate(self.history[-20:], 1):  # 显示最后20条
            minutes = int(entry['duration'] // 60)
            seconds = int(entry['duration'] % 60)
            print(f"{i}. [{entry['time']}]")
            print(f"   {entry['start']} → {entry['end']}")
            print(f"   耗时: {minutes}分{seconds}秒, 站点数: {len(entry['path'])}\n")
        
        print("=" * 70 + "\n")
    
    def export_route(self, index):
        """导出指定的查询结果"""
        if not self.history or index < 1 or index > len(self.history):
            print("\n✗ 无效的查询编号\n")
            return
        
        entry = self.history[index - 1]
        filename = f"route_{index}_{entry['start']}_{entry['end']}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"NYC Metro Route - {entry['time']}\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"起点: {entry['start']} - {self.station_names.get(entry['start'], entry['start'])}\n")
                f.write(f"终点: {entry['end']} - {self.station_names.get(entry['end'], entry['end'])}\n")
                f.write(f"总耗时: {entry['duration']:.0f} 秒\n")
                f.write(f"站点数: {len(entry['path'])}\n\n")
                f.write("完整路线:\n")
                f.write("-" * 70 + "\n")
                
                for i, sid in enumerate(entry['path'], 1):
                    name = self.station_names.get(sid, sid)
                    if name != sid:
                        f.write(f"{i:3d}. {sid:10s} - {name}\n")
                    else:
                        f.write(f"{i:3d}. {sid}\n")
            
            print(f"\n✓ 结果已导出到: {filename}\n")
        except Exception as e:
            print(f"\n✗ 导出失败: {e}\n")
    
    def show_help(self):
        """显示帮助"""
        print("""
┌─────────────────────────────────────────────────────────────────┐
│                    命令帮助                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. 查询路线                                                     │
│     输入起点和终点站点ID，计算最短路线                           │
│                                                                   │
│  2. 搜索站点                                                     │
│     输入关键词搜索站点 (支持ID和名称搜索)                       │
│                                                                   │
│  3. 查看历史                                                     │
│     显示所有之前的查询记录                                       │
│                                                                   │
│  4. 导出结果                                                     │
│     将查询结果导出为文本文件                                     │
│                                                                   │
│  5. 显示帮助                                                     │
│     显示此帮助信息                                               │
│                                                                   │
│  0. 退出                                                          │
│     退出程序                                                     │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  示例: 从 127S (Rector St) 到 137S (86th St)                     │
│  输入起点: 127S                                                  │
│  输入终点: 137S                                                  │
└─────────────────────────────────────────────────────────────────┘
""")
    
    def run(self):
        """主交互循环"""
        self.display_banner()
        self.show_help()
        
        while True:
            try:
                print("\n选择操作:")
                print("  1. 查询路线")
                print("  2. 搜索站点")
                print("  3. 查看历史")
                print("  4. 导出结果")
                print("  5. 显示帮助")
                print("  0. 退出")
                print()
                
                choice = input("请输入选项 (0-5): ").strip()
                
                if choice == '1':
                    start = input("\n输入起点站点ID: ").strip().upper()
                    end = input("输入终点站点ID: ").strip().upper()
                    self.search_route(start, end)
                
                elif choice == '2':
                    keyword = input("\n输入搜索关键词: ").strip()
                    self.list_stations(keyword)
                
                elif choice == '3':
                    self.show_history()
                
                elif choice == '4':
                    if self.history:
                        self.show_history()
                        try:
                            idx = int(input("输入要导出的查询编号: ").strip())
                            self.export_route(idx)
                        except ValueError:
                            print("\n✗ 无效的编号\n")
                    else:
                        print("\n✗ 没有查询历史\n")
                
                elif choice == '5':
                    self.show_help()
                
                elif choice == '0':
                    print("\n👋 再见！祝您旅途愉快!\n")
                    break
                
                else:
                    print("\n✗ 无效选项，请输入 0-5\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 程序已中断，再见!\n")
                break
            except Exception as e:
                print(f"\n✗ 发生错误: {e}\n")


def main():
    planner = MetroRoutePlannerCLI()
    planner.run()


if __name__ == "__main__":
    main()
