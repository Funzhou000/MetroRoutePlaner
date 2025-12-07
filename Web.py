#!/usr/bin/env python3
"""
NYC Metro Route Planner - 简易Web界面版本
Simple Web Interface Version (无需GUI库)
使用http.server创建简单的Web服务
"""

import pickle
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from Dijkstra import dijkstra
import threading
import sys


class RouteHandler(BaseHTTPRequestHandler):
    # 类变量，所有实例共享
    graph = None
    station_names = {}
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_home_page().encode('utf-8'))
        
        elif self.path.startswith('/api/stations'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            # 获取查询参数
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            search = params.get('search', [''])[0].lower()
            
            stations = sorted(self.graph.keys())
            if search:
                stations = [s for s in stations if search in s.lower()]
            
            response = {
                'stations': [
                    {
                        'id': sid,
                        'name': self.station_names.get(sid, sid)
                    }
                    for sid in stations[:100]  # 限制返回100个
                ]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        elif self.path.startswith('/api/route'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            start = params.get('start', [''])[0].upper()
            end = params.get('end', [''])[0].upper()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            if not start or not end:
                response = {'error': '起点和终点不能为空'}
            elif start == end:
                response = {'error': '起点和终点不能相同'}
            elif start not in self.graph or end not in self.graph:
                response = {'error': '无效的站点ID'}
            else:
                total_time, path = dijkstra(self.graph, start, end)
                
                if total_time is None or path is None:
                    response = {'error': '无法找到路线'}
                else:
                    minutes = int(total_time // 60)
                    seconds = int(total_time % 60)
                    response = {
                        'success': True,
                        'start': start,
                        'end': end,
                        'duration': total_time,
                        'duration_text': f'{minutes}分{seconds}秒',
                        'stations': len(path),
                        'path': [
                            {
                                'id': sid,
                                'name': self.station_names.get(sid, sid),
                                'order': i + 1
                            }
                            for i, sid in enumerate(path)
                        ]
                    }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Not Found</h1>')
    
    def get_home_page(self):
        """返回主页HTML"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC Metro Route Planner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            margin-top: 10px;
        }
        
        .result {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        
        .result h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .result-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .info-box {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        
        .info-box strong {
            color: #667eea;
        }
        
        .route-list {
            background: white;
            padding: 15px;
            border-radius: 6px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .route-item {
            padding: 8px;
            border-bottom: 1px solid #eee;
            font-size: 13px;
        }
        
        .route-item:last-child {
            border-bottom: none;
        }
        
        .station-id {
            font-weight: 600;
            color: #667eea;
        }
        
        .error {
            color: #d32f2f;
            padding: 15px;
            background: #ffebee;
            border-radius: 6px;
            margin-top: 15px;
            display: none;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 24px;
            }
            
            .result-info {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚇 NYC Metro Route Planner</h1>
        <p class="subtitle">纽约地铁线路规划器</p>
        
        <form id="routeForm">
            <div class="form-group">
                <label for="start">起点站点ID:</label>
                <input 
                    type="text" 
                    id="start" 
                    placeholder="输入起点站点ID (如: 127S)"
                    autocomplete="off"
                    list="startSuggestions"
                    required
                />
                <datalist id="startSuggestions"></datalist>
            </div>
            
            <div class="form-group">
                <label for="end">终点站点ID:</label>
                <input 
                    type="text" 
                    id="end" 
                    placeholder="输入终点站点ID (如: 137S)"
                    autocomplete="off"
                    list="endSuggestions"
                    required
                />
                <datalist id="endSuggestions"></datalist>
            </div>
            
            <button type="submit">查询最短路线</button>
        </form>
        
        <div class="loading" id="loading">
            ⏳ 正在计算...
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="result" id="result">
            <h3>✓ 查询结果</h3>
            <div class="result-info">
                <div class="info-box">
                    <strong>总耗时:</strong><br>
                    <span id="duration"></span>
                </div>
                <div class="info-box">
                    <strong>站点数:</strong><br>
                    <span id="stations"></span>
                </div>
            </div>
            <div class="route-list" id="routeList"></div>
        </div>
    </div>
    
    <script>
        // 自动补全功能
        const startInput = document.getElementById('start');
        const endInput = document.getElementById('end');
        
        async function fetchStations(query) {
            const response = await fetch(`/api/stations?search=${encodeURIComponent(query)}`);
            const data = await response.json();
            return data.stations;
        }
        
        function updateSuggestions(input, datalistId) {
            input.addEventListener('input', async (e) => {
                const query = e.target.value;
                if (query.length < 1) return;
                
                const stations = await fetchStations(query);
                const datalist = document.getElementById(datalistId);
                datalist.innerHTML = '';
                
                stations.forEach(station => {
                    const option = document.createElement('option');
                    option.value = station.id;
                    option.textContent = `${station.id} - ${station.name}`;
                    datalist.appendChild(option);
                });
            });
        }
        
        updateSuggestions(startInput, 'startSuggestions');
        updateSuggestions(endInput, 'endSuggestions');
        
        // 表单提交
        document.getElementById('routeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const start = document.getElementById('start').value.toUpperCase();
            const end = document.getElementById('end').value.toUpperCase();
            
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const result = document.getElementById('result');
            
            loading.style.display = 'block';
            error.style.display = 'none';
            result.style.display = 'none';
            
            try {
                const response = await fetch(`/api/route?start=${start}&end=${end}`);
                const data = await response.json();
                
                loading.style.display = 'none';
                
                if (data.error) {
                    error.textContent = '✗ ' + data.error;
                    error.style.display = 'block';
                } else {
                    document.getElementById('duration').textContent = data.duration_text;
                    document.getElementById('stations').textContent = data.stations;
                    
                    const routeList = document.getElementById('routeList');
                    routeList.innerHTML = data.path.map(station => `
                        <div class="route-item">
                            <span class="station-id">${station.order}. ${station.id}</span> - ${station.name}
                        </div>
                    `).join('');
                    
                    result.style.display = 'block';
                }
            } catch (err) {
                loading.style.display = 'none';
                error.textContent = '✗ 请求失败: ' + err.message;
                error.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''
    
    def log_message(self, format, *args):
        """禁用默认日志"""
        pass


def load_data():
    """加载图数据"""
    try:
        with open('metro_graph.pkl', 'rb') as f:
            graph = pickle.load(f)
    except FileNotFoundError:
        print("错误：找不到 metro_graph.pkl")
        print("请先运行 Dataprocess.py")
        sys.exit(1)
    
    try:
        with open('station_names.pkl', 'rb') as f:
            station_names = pickle.load(f)
    except:
        station_names = {sid: sid for sid in graph.keys()}
    
    return graph, station_names


def main():
    # 加载数据
    print("正在加载数据...")
    RouteHandler.graph, RouteHandler.station_names = load_data()
    print(f"✓ 已加载 {len(RouteHandler.graph)} 个站点\n")
    
    # 启动Web服务器
    port = 8888
    server = HTTPServer(('localhost', port), RouteHandler)
    
    print("=" * 60)
    print("🚀 NYC Metro Route Planner - Web 版本")
    print("=" * 60)
    print(f"\n✓ 服务器已启动")
    print(f"✓ 请在浏览器中打开: http://localhost:{port}\n")
    print("按 Ctrl+C 停止服务器\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


if __name__ == '__main__':
    main()
