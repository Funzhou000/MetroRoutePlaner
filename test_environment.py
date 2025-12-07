#!/usr/bin/env python3
"""
GUI测试脚本 - 验证环境和依赖
Test script for GUI environment verification
"""

import sys
import os


def check_python_version():
    """检查Python版本"""
    print("=" * 60)
    print("🔍 Python版本检查")
    print("=" * 60)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python版本: {version_str}")
    
    if version.major >= 3 and version.minor >= 6:
        print("✅ Python版本符合要求 (3.6+)\n")
        return True
    else:
        print("❌ Python版本过低，需要3.6以上\n")
        return False


def check_dependencies():
    """检查依赖库"""
    print("=" * 60)
    print("🔍 依赖库检查")
    print("=" * 60)
    
    dependencies = {
        'tkinter': 'GUI框架',
        'pickle': '数据序列化',
        'heapq': '优先队列',
        'threading': '多线程',
        'csv': '数据导出',
        'datetime': '时间处理'
    }
    
    all_ok = True
    
    for lib, desc in dependencies.items():
        try:
            __import__(lib)
            print(f"✅ {lib:15s} - {desc}")
        except ImportError:
            print(f"❌ {lib:15s} - {desc} (缺失)")
            all_ok = False
    
    print()
    return all_ok


def check_optional_dependencies():
    """检查可选依赖"""
    print("=" * 60)
    print("🔍 可选依赖检查")
    print("=" * 60)
    
    optional = {
        'pandas': '数据处理（Dataprocess.py需要）',
    }
    
    for lib, desc in optional.items():
        try:
            __import__(lib)
            print(f"✅ {lib:15s} - {desc}")
        except ImportError:
            print(f"⚠️  {lib:15s} - {desc} (缺失，但非必需)")
    
    print()


def check_graph_files():
    """检查图数据文件"""
    print("=" * 60)
    print("🔍 数据文件检查")
    print("=" * 60)
    
    files_to_check = {
        'metro_graph.pkl': '地铁网络图',
        'station_names.pkl': '站点名称映射（可选）'
    }
    
    all_ok = True
    
    for filename, desc in files_to_check.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size > 1024:
                size_str = f"{size / (1024*1024):.1f}MB"
            else:
                size_str = f"{size}B"
            print(f"✅ {filename:20s} ({size_str}) - {desc}")
        else:
            print(f"❌ {filename:20s} - {desc} (缺失)")
            all_ok = False
    
    print()
    return all_ok


def check_dijkstra():
    """检查Dijkstra模块"""
    print("=" * 60)
    print("🔍 Dijkstra模块检查")
    print("=" * 60)
    
    try:
        from Dijkstra import dijkstra, reconstruct_path
        print("✅ Dijkstra.py - 可以正确导入")
        print("✅ dijkstra() 函数存在")
        print("✅ reconstruct_path() 函数存在")
        print()
        return True
    except ImportError as e:
        print(f"❌ 无法导入Dijkstra: {e}")
        print()
        return False


def check_gui():
    """检查GUI模块"""
    print("=" * 60)
    print("🔍 GUI模块检查")
    print("=" * 60)
    
    gui_files = [
        ('GUI.py', '标准版'),
        ('GUI_Advanced.py', '高级版')
    ]
    
    for filename, desc in gui_files:
        if os.path.exists(filename):
            print(f"✅ {filename:20s} - {desc}")
        else:
            print(f"❌ {filename:20s} - {desc} (缺失)")
    
    print()


def run_gui_test():
    """尝试启动GUI"""
    print("=" * 60)
    print("🔍 GUI启动测试")
    print("=" * 60)
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        root.destroy()
        print("✅ Tkinter可以正常工作")
        print()
        return True
    except Exception as e:
        print(f"❌ Tkinter测试失败: {e}")
        print()
        return False


def print_recommendations():
    """打印建议"""
    print("=" * 60)
    print("📋 建议和说明")
    print("=" * 60)
    
    print("""
1. 如果 metro_graph.pkl 缺失:
   运行: python3 Dataprocess.py
   （需要5-10分钟，只需运行一次）

2. 如果 station_names.pkl 缺失（可选）:
   运行: python3 extract_station_names.py
   （使GUI显示更友好的站点名称）

3. 启动标准版GUI:
   python3 GUI.py

4. 启动高级版GUI（推荐）:
   python3 GUI_Advanced.py

5. 如果遇到任何问题，查看文档:
   - GUI_GUIDE.md       - 完整功能说明
   - QUICKSTART.md      - 快速开始指南
   - GUI_README.md      - 基础使用说明
""")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("NYC Metro Route Planner - 环境检查工具")
    print("Environment Verification Tool")
    print("=" * 60 + "\n")
    
    results = {
        'Python版本': check_python_version(),
        '依赖库': check_dependencies(),
        '可选库': True,  # 可选，不计入
        '图数据文件': check_graph_files(),
        'Dijkstra模块': check_dijkstra(),
        'GUI文件': True,  # 文件检查
        'Tkinter': run_gui_test(),
    }
    
    check_gui()
    check_optional_dependencies()
    
    print_recommendations()
    
    # 汇总结果
    print("=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    critical_checks = {
        'Python版本': results['Python版本'],
        '依赖库': results['依赖库'],
        'Dijkstra模块': results['Dijkstra模块'],
        'Tkinter': results['Tkinter'],
    }
    
    if all(critical_checks.values()):
        print("✅ 所有关键检查均通过！")
        
        if results['图数据文件']:
            print("✅ 可以立即启动GUI")
            print("\n推荐命令:")
            print("  python3 GUI.py           (标准版)")
            print("  python3 GUI_Advanced.py  (高级版)")
        else:
            print("⚠️  需要先生成图数据文件")
            print("\n请先运行:")
            print("  python3 Dataprocess.py")
    else:
        print("❌ 存在需要解决的问题:")
        for check, result in critical_checks.items():
            if not result:
                print(f"  - {check}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
