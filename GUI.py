import pickle
import tkinter as tk
from tkinter import ttk, messagebox
from Dijkstra import dijkstra
import threading
import sys
import os

# 禁用macOS的Metal渲染，使用OpenGL兼容模式
os.environ['TKINTER_MACOSX_ALLOW'] = '1'

class MetroRoutePlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NYC Metro Route Planner - 纽约地铁线路规划器")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 定义颜色主题
        self.bg_color = "#f0f0f0"
        self.primary_color = "#0066cc"
        self.success_color = "#28a745"
        self.danger_color = "#dc3545"
        
        # 初始化图数据
        self.graph = None
        self.station_names = {}  # 存储 stop_id -> stop_name 的映射
        
        # 加载数据
        self.load_graph()
        
        # 创建UI
        self.create_widgets()
    
    def load_graph(self):
        """加载地铁网络图和站点信息"""
        try:
            with open('metro_graph.pkl', 'rb') as f:
                self.graph = pickle.load(f)
            print(f"✓ 图加载成功！总节点数: {len(self.graph)}")
        except FileNotFoundError:
            messagebox.showerror(
                "错误",
                "找不到 metro_graph.pkl 文件。\n请先运行 Dataprocess.py 来生成该文件。"
            )
            self.root.destroy()
            return
        
        # 尝试加载站点信息映射
        try:
            with open('station_names.pkl', 'rb') as f:
                self.station_names = pickle.load(f)
        except FileNotFoundError:
            # 如果没有站点名称文件，使用站点ID作为显示名称
            self.station_names = {stop_id: stop_id for stop_id in self.graph.keys()}
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== 标题 =====
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="NYC Metro Route Planner",
            font=("Arial", 24, "bold"),
            foreground=self.primary_color
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_frame,
            text="纽约地铁最短路线规划器",
            font=("Arial", 12, "gray"),
            foreground="gray"
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # ===== 输入区域 =====
        input_frame = ttk.LabelFrame(main_frame, text="路线查询", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 起点选择
        start_label = ttk.Label(input_frame, text="起点 (Start Station):", font=("Arial", 11))
        start_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            input_frame,
            textvariable=self.start_var,
            values=self.get_sorted_stations(),
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.start_combo.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=(0, 10))
        self.start_combo.bind('<<ComboboxSelected>>', lambda e: self.on_station_selected())
        
        # 终点选择
        end_label = ttk.Label(input_frame, text="终点 (End Station):", font=("Arial", 11))
        end_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(
            input_frame,
            textvariable=self.end_var,
            values=self.get_sorted_stations(),
            state="readonly",
            width=40,
            font=("Arial", 10)
        )
        self.end_combo.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=(0, 10))
        self.end_combo.bind('<<ComboboxSelected>>', lambda e: self.on_station_selected())
        
        # 配置列权重
        input_frame.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))
        
        self.search_button = ttk.Button(
            button_frame,
            text="查询最短路线 (Search Route)",
            command=self.search_route
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(
            button_frame,
            text="清空 (Clear)",
            command=self.clear_results
        )
        self.clear_button.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(button_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT)
        
        # ===== 结果区域 =====
        result_frame = ttk.LabelFrame(main_frame, text="查询结果 (Results)", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 时间和距离显示
        info_frame = ttk.Frame(result_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.time_label = tk.Label(
            info_frame,
            text="总耗时: --",
            font=("Arial", 14, "bold"),
            foreground=self.success_color
        )
        self.time_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.stations_label = tk.Label(
            info_frame,
            text="站点数: --",
            font=("Arial", 14, "bold"),
            foreground=self.primary_color
        )
        self.stations_label.pack(side=tk.LEFT)
        
        # 路线显示（使用文本框）
        route_label = ttk.Label(result_frame, text="路线 (Route Path):")
        route_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.route_text = tk.Text(
            text_frame,
            height=15,
            width=100,
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.route_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.route_text.yview)
        
        # ===== 底部说明 =====
        info_text = """提示: 
• 从 Dataprocess.py 中的 stops.txt 选择有效的站点 ID
• 支持换乘和直达路线计算
• 结果显示最短时间路线"""
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            font=("Arial", 9),
            foreground="gray",
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W)
    
    def get_sorted_stations(self):
        """获取排序后的所有站点，包含名称显示"""
        if not self.graph:
            return []
        
        # 如果有站点名称，创建带名称的显示
        stations = []
        for stop_id in sorted(self.graph.keys()):
            if stop_id in self.station_names and self.station_names[stop_id] != stop_id:
                # 显示: ID - 名称
                display = f"{stop_id} - {self.station_names[stop_id]}"
            else:
                display = stop_id
            stations.append(display)
        
        return stations
    
    def on_station_selected(self):
        """当选择站点时的回调"""
        pass
    
    def search_route(self):
        """搜索最短路线"""
        start_display = self.start_var.get()
        end_display = self.end_var.get()
        
        # 从显示文本中提取站点ID
        start = self.extract_station_id(start_display)
        end = self.extract_station_id(end_display)
        
        if not start:
            messagebox.showwarning("提示", "请选择起点站")
            return
        
        if not end:
            messagebox.showwarning("提示", "请选择终点站")
            return
        
        if start == end:
            messagebox.showwarning("提示", "起点和终点不能相同")
            return
        
        # 在后台线程中运行搜索，避免UI冻结
        self.search_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在计算...", foreground="orange")
        self.root.update()
        
        thread = threading.Thread(
            target=self._perform_search,
            args=(start, end),
            daemon=True
        )
        thread.start()
    
    def extract_station_id(self, display_text):
        """从显示文本中提取站点ID"""
        if not display_text:
            return None
        
        # 如果包含 " - "，说明是ID - 名称格式
        if " - " in display_text:
            return display_text.split(" - ")[0].strip()
        
        return display_text.strip()
    
    def _perform_search(self, start, end):
        """执行路线搜索（在后台线程中）"""
        try:
            total_time, path = dijkstra(self.graph, start, end)
            
            # 在主线程中更新UI
            self.root.after(0, self._display_results, total_time, path, start, end)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"计算过程中出错: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_label.config(text=""))
    
    def _display_results(self, total_time, path, start, end):
        """显示查询结果"""
        # 启用文本框编辑
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        
        if total_time is None or path is None:
            self.route_text.insert(tk.END, f"抱歉，无法从 {start} 找到到达 {end} 的路线。")
            self.time_label.config(text="总耗时: 无法到达")
            self.stations_label.config(text="站点数: --")
        else:
            # 计算时间
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            
            # 显示摘要信息
            self.time_label.config(
                text=f"总耗时: {minutes} 分 {seconds} 秒 ({total_time:.0f} 秒)"
            )
            self.stations_label.config(text=f"站点数: {len(path)}")
            
            # 显示完整路线
            route_text = "完整路线:\n"
            route_text += "=" * 60 + "\n\n"
            
            for i, station_id in enumerate(path, 1):
                station_name = self.station_names.get(station_id, station_id)
                route_text += f"{i:3d}. {station_id:10s} - {station_name}\n"
            
            route_text += "\n" + "=" * 60 + "\n"
            route_text += f"\n总耗时: {total_time:.0f} 秒 (约 {minutes} 分 {seconds} 秒)\n"
            route_text += f"经过站点: {len(path)} 个\n"
            
            self.route_text.insert(tk.END, route_text)
        
        # 禁用文本框编辑
        self.route_text.config(state=tk.DISABLED)
    
    def clear_results(self):
        """清空结果"""
        self.start_var.set("")
        self.end_var.set("")
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        self.route_text.config(state=tk.DISABLED)
        self.time_label.config(text="总耗时: --")
        self.stations_label.config(text="站点数: --")
        self.status_label.config(text="")


def main():
    root = tk.Tk()
    app = MetroRoutePlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
