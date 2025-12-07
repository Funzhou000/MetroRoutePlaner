#!/bin/bash
# 快速启动脚本 - Quick Launch Script
# 使用方法: bash launch.sh

echo "🚀 NYC Metro Route Planner"
echo "======================================"
echo ""
echo "选择要启动的版本:"
echo ""
echo "1) 标准版 (推荐) - 简洁易用"
echo "2) 高级版 - 功能完整"
echo "3) 检查环境"
echo "4) 退出"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "启动标准版 GUI..."
        python3 GUI.py
        ;;
    2)
        echo "启动高级版 GUI..."
        python3 GUI_Advanced.py
        ;;
    3)
        echo "检查环境..."
        python3 test_environment.py
        ;;
    4)
        echo "再见！👋"
        exit 0
        ;;
    *)
        echo "无效选项，再见！"
        exit 1
        ;;
esac
