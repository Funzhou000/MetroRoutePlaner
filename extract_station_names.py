"""
辅助脚本：从GTFS数据中提取和保存站点名称映射
Run this after Dataprocess.py to create station_names.pkl for better display in GUI
"""

import pandas as pd
import pickle

def create_station_names_mapping():
    """从stops.txt创建stop_id到stop_name的映射"""
    
    # 修改为你的GTFS数据路径
    gtfs_path = 'C:/Users/Funzhou/Downloads/gtfs_subway/'
    
    try:
        # 加载stops.txt
        stops = pd.read_csv(f'{gtfs_path}stops.txt')
        
        # 创建映射字典
        station_names = {}
        for idx, row in stops.iterrows():
            stop_id = row['stop_id']
            stop_name = row['stop_name']
            station_names[stop_id] = stop_name
        
        # 保存到pickle文件
        with open('station_names.pkl', 'wb') as f:
            pickle.dump(station_names, f)
        
        print(f"✓ 成功创建站点名称映射！")
        print(f"  总站点数: {len(station_names)}")
        print(f"  已保存到: station_names.pkl")
        
        # 显示一些示例
        print(f"\n示例站点:")
        for i, (stop_id, stop_name) in enumerate(list(station_names.items())[:5]):
            print(f"  {stop_id}: {stop_name}")
        print(f"  ...")
        
        return True
        
    except FileNotFoundError as e:
        print(f"✗ 错误: {e}")
        print(f"  请确保GTFS文件在正确的路径: {gtfs_path}")
        return False


if __name__ == "__main__":
    create_station_names_mapping()
