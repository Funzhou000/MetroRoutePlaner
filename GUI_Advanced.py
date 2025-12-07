"""
NYC Metro Route Planner - Advanced GUI Version
高级版本，包含更多功能和更好的用户体验
"""

import pickle
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from Dijkstra import dijkstra
import threading
from datetime import datetime
import csv


class MetroRoutePlannerAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("NYC Metro Route Planner - Advanced Edition")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # 数据
        self.graph = None
        self.station_names = {}
        self.search_history = []
        
        # 加载数据
        self.load_graph()
        
        # 创建notebook式多标签界面
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页1：主查询
        self.query_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.query_frame, text="路线查询")
        self.create_query_widgets()
        
        # 标签页2：搜索历史
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="查询历史")
        self.create_history_widgets()
        
        # 标签页3：站点浏览
        self.browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_frame, text="站点浏览")
        self.create_browser_widgets()
        
        # 标签页4：帮助和关于
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="帮助")
        self.create_about_widgets()
    
    def load_graph(self):
        """加载图数据"""
        try:
            with open('metro_graph.pkl', 'rb') as f:
                self.graph = pickle.load(f)
            print(f"✓ Graph loaded: {len(self.graph)} stations")
        except FileNotFoundError:
            messagebox.showerror("Error", "metro_graph.pkl not found.\nPlease run Dataprocess.py first.")
            self.root.destroy()
            return
        
        try:
            with open('station_names.pkl', 'rb') as f:
                self.station_names = pickle.load(f)
        except FileNotFoundError:
            self.station_names = {sid: sid for sid in self.graph.keys()}
    
    def get_sorted_stations(self):
        """获取排序的站点列表"""
        stations = []
        for stop_id in sorted(self.graph.keys()):
            name = self.station_names.get(stop_id, stop_id)
            if name != stop_id:
                display = f"{stop_id} - {name}"
            else:
                display = stop_id
            stations.append((display, stop_id))
        return stations
    
    def create_query_widgets(self):
        """创建主查询界面"""
        # 标题
        title = tk.Label(
            self.query_frame,
            text="NYC Metro Route Planner",
            font=("Arial", 20, "bold"),
            foreground="#0066cc"
        )
        title.pack(pady=10)
        
        # 输入框架
        input_frame = ttk.LabelFrame(self.query_frame, text="输入信息", padding=15)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # 起点
        ttk.Label(input_frame, text="起点站点:", font=("Arial", 11)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            input_frame,
            textvariable=self.start_var,
            values=[s[0] for s in self.get_sorted_stations()],
            state="readonly",
            width=50,
            font=("Arial", 10)
        )
        self.start_combo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # 终点
        ttk.Label(input_frame, text="终点站点:", font=("Arial", 11)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(
            input_frame,
            textvariable=self.end_var,
            values=[s[0] for s in self.get_sorted_stations()],
            state="readonly",
            width=50,
            font=("Arial", 10)
        )
        self.end_combo.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(self.query_frame)
        button_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(
            button_frame,
            text="查询路线",
            command=self.search_route,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="清空",
            command=self.clear_query,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="导出结果",
            command=self.export_result,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(button_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # 结果显示框架
        result_frame = ttk.LabelFrame(self.query_frame, text="查询结果", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # 统计信息
        info_frame = ttk.Frame(result_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.time_var = tk.StringVar(value="总耗时: --")
        self.stations_var = tk.StringVar(value="站点数: --")
        
        ttk.Label(info_frame, textvariable=self.time_var, font=("Arial", 12, "bold")).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Label(info_frame, textvariable=self.stations_var, font=("Arial", 12, "bold")).pack(
            side=tk.LEFT, padx=10
        )
        
        # 路线文本框
        self.route_text = tk.Text(
            result_frame,
            height=15,
            font=("Courier", 10),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.route_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(result_frame, command=self.route_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.route_text.config(yscrollcommand=scrollbar.set)
        
        self.last_result = None  # 保存最后一次的查询结果
    
    def create_history_widgets(self):
        """创建查询历史界面"""
        # 工具栏
        toolbar = ttk.Frame(self.history_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            toolbar,
            text="清空历史",
            command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="导出历史",
            command=self.export_history
        ).pack(side=tk.LEFT, padx=5)
        
        # 历史列表
        self.history_text = tk.Text(
            self.history_frame,
            height=25,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.history_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
    
    def create_browser_widgets(self):
        """创建站点浏览界面"""
        # 搜索框
        search_frame = ttk.Frame(self.browser_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="搜索站点:").pack(side=tk.LEFT)
        self.browser_search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.browser_search_var,
            font=("Arial", 10)
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(
            search_frame,
            text="搜索",
            command=self.browser_search
        ).pack(side=tk.LEFT)
        
        # 站点列表
        list_frame = ttk.Frame(self.browser_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.browser_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )
        self.browser_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.browser_listbox.yview)
        
        # 初始化站点列表
        self.refresh_station_list()
    
    def create_about_widgets(self):
        """创建帮助和关于界面"""
        about_text = """
NYC Metro Route Planner
=====================================

版本: 2.0 (Advanced Edition)

功能特性:
• 基于Dijkstra算法的最短路径计算
• 支持地铁换乘和直达路线
• 详细的路线和耗时显示
• 查询历史记录
• 结果导出功能

使用步骤:
1. 在"路线查询"标签页选择起点和终点
2. 点击"查询路线"按钮
3. 等待结果显示
4. 可选：导出或查看历史

技术栈:
• Python 3.9+
• Tkinter (GUI)
• Pandas (数据处理)
• Pickle (数据序列化)
• Heapq (优先队列)

性能指标（纽约地铁数据）:
• 总站点: 400+
• 总边数: 10000+
• 平均查询时间: < 1秒

联系方式:
项目主页: https://github.com/Funzhou000/MetroRoutePlaner

许可证: MIT License

=====================================
        """
        
        text_widget = tk.Text(
            self.about_frame,
            font=("Courier", 11),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
    
    def search_route(self):
        """搜索最短路线"""
        start_display = self.start_var.get()
        end_display = self.end_var.get()
        
        if not start_display or not end_display:
            messagebox.showwarning("提示", "请选择起点和终点")
            return
        
        # 提取站点ID
        stations = {s[0]: s[1] for s in self.get_sorted_stations()}
        start = stations.get(start_display)
        end = stations.get(end_display)
        
        if start == end:
            messagebox.showwarning("提示", "起点和终点不能相同")
            return
        
        self.status_var.set("正在计算...")
        self.root.update()
        
        thread = threading.Thread(
            target=self._perform_search,
            args=(start, end, start_display, end_display),
            daemon=True
        )
        thread.start()
    
    def _perform_search(self, start, end, start_disp, end_disp):
        """执行搜索（后台线程）"""
        try:
            total_time, path = dijkstra(self.graph, start, end)
            self.root.after(0, self._display_results, total_time, path, start_disp, end_disp)
            
            # 添加到历史
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if total_time:
                duration = f"{int(total_time//60)}分{int(total_time%60)}秒"
            else:
                duration = "无法到达"
            
            history_entry = f"[{timestamp}] {start_disp} → {end_disp} ({duration})"
            self.search_history.append(history_entry)
            self.update_history_display()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"查询失败: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.status_var.set("就绪"))
    
    def _display_results(self, total_time, path, start_disp, end_disp):
        """显示查询结果"""
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        
        if not path or total_time is None:
            self.route_text.insert(tk.END, f"无法从 {start_disp} 到达 {end_disp}")
            self.time_var.set("总耗时: 无法到达")
            self.stations_var.set("站点数: --")
            self.last_result = None
        else:
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            
            self.time_var.set(f"总耗时: {minutes}分{seconds}秒")
            self.stations_var.set(f"站点数: {len(path)}")
            
            result_text = f"从 {start_disp} 到 {end_disp}\n"
            result_text += "=" * 70 + "\n\n"
            
            for i, station_id in enumerate(path, 1):
                name = self.station_names.get(station_id, station_id)
                result_text += f"{i:3d}. {station_id:10s} - {name}\n"
            
            result_text += "\n" + "=" * 70 + "\n"
            result_text += f"总耗时: {total_time:.0f}秒 (约{minutes}分{seconds}秒)\n"
            result_text += f"总站点数: {len(path)}\n"
            
            self.route_text.insert(tk.END, result_text)
            self.last_result = {
                'start': start_disp,
                'end': end_disp,
                'time': total_time,
                'path': path
            }
        
        self.route_text.config(state=tk.DISABLED)
    
    def clear_query(self):
        """清空查询"""
        self.start_var.set("")
        self.end_var.set("")
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        self.route_text.config(state=tk.DISABLED)
        self.time_var.set("总耗时: --")
        self.stations_var.set("站点数: --")
    
    def export_result(self):
        """导出最后的查询结果"""
        if not self.last_result:
            messagebox.showwarning("提示", "没有可导出的结果")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if filepath.endswith('.csv'):
                    writer = csv.writer(f)
                    writer.writerow(['站号', '站点ID', '站点名称'])
                    for i, sid in enumerate(self.last_result['path'], 1):
                        name = self.station_names.get(sid, sid)
                        writer.writerow([i, sid, name])
                else:
                    f.write(f"路线: {self.last_result['start']} → {self.last_result['end']}\n")
                    f.write(f"总耗时: {self.last_result['time']:.0f}秒\n")
                    f.write(f"站点数: {len(self.last_result['path'])}\n\n")
                    for i, sid in enumerate(self.last_result['path'], 1):
                        name = self.station_names.get(sid, sid)
                        f.write(f"{i}. {sid} - {name}\n")
            
            messagebox.showinfo("成功", f"结果已导出到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def update_history_display(self):
        """更新历史显示"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, "查询历史:\n" + "=" * 60 + "\n\n")
        
        for entry in reversed(self.search_history[-50:]):  # 显示最后50条
            self.history_text.insert(tk.END, entry + "\n")
        
        self.history_text.config(state=tk.DISABLED)
    
    def clear_history(self):
        """清空历史记录"""
        self.search_history = []
        self.update_history_display()
    
    def export_history(self):
        """导出历史记录"""
        if not self.search_history:
            messagebox.showwarning("提示", "没有历史记录可导出")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                for entry in self.search_history:
                    f.write(entry + "\n")
            
            messagebox.showinfo("成功", f"历史已导出到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def refresh_station_list(self):
        """刷新站点列表"""
        self.browser_listbox.delete(0, tk.END)
        for display, _ in self.get_sorted_stations():
            self.browser_listbox.insert(tk.END, display)
    
    def browser_search(self):
        """在浏览器中搜索站点"""
        keyword = self.browser_search_var.get().lower()
        
        self.browser_listbox.delete(0, tk.END)
        
        for display, sid in self.get_sorted_stations():
            if keyword in display.lower():
                self.browser_listbox.insert(tk.END, display)


def main():
    root = tk.Tk()
    app = MetroRoutePlannerAdvanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()
