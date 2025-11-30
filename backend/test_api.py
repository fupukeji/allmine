#!/usr/bin/env python3
"""
TimeValue API快速测试脚本
测试所有修复后的接口是否正常工作
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)


def test_login():
    """测试登录"""
    print_section("测试登录")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 登录成功")
            data = result.get('data', {})
            print(f"   用户: {data.get('user', {}).get('username')}")
            return data.get('access_token')
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def test_analytics_overview(token):
    """测试概览接口"""
    print_section("测试BI分析 - 概览接口")
    
    url = f"{BASE_URL}/analytics/overview"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 概览接口正常")
            data = result.get('data', {})
            print(f"   总项目数: {data.get('total_projects', 0)}")
            print(f"   总投入: ¥{data.get('total_amount', 0):.2f}")
            print(f"   已消耗: ¥{data.get('total_used_cost', 0):.2f}")
            print(f"   剩余价值: ¥{data.get('total_remaining_value', 0):.2f}")
            return True
        else:
            print(f"❌ 接口失败 [{response.status_code}]: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_analytics_trends(token):
    """测试趋势接口"""
    print_section("测试BI分析 - 趋势接口")
    
    url = f"{BASE_URL}/analytics/trends"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"period": "month"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 趋势接口正常")
            data = result.get('data', {})
            trends = data.get('trends', [])
            print(f"   时间周期: {data.get('period')}")
            print(f"   数据点数: {len(trends)}")
            if trends:
                print(f"   最近一期: {trends[-1].get('period')} - {trends[-1].get('projects_count')}个项目")
            return True
        else:
            print(f"❌ 接口失败 [{response.status_code}]: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_category_analysis(token):
    """测试分类分析接口"""
    print_section("测试BI分析 - 分类分析接口")
    
    url = f"{BASE_URL}/analytics/category-analysis"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 分类分析接口正常")
            data = result.get('data', [])
            print(f"   分类数量: {len(data)}")
            for cat in data[:3]:  # 显示前3个分类
                print(f"   - {cat.get('category_name')}: {cat.get('project_count')}个项目, ¥{cat.get('total_amount', 0):.2f}")
            return True
        else:
            print(f"❌ 接口失败 [{response.status_code}]: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_all():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 TimeValue API 测试套件")
    print("="*60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 登录获取token
    token = test_login()
    if not token:
        print("\n❌ 无法获取访问令牌，测试终止")
        return
    
    # 2. 测试各个接口
    results = {
        "概览接口": test_analytics_overview(token),
        "趋势接口": test_analytics_trends(token),
        "分类分析接口": test_category_analysis(token)
    }
    
    # 3. 总结
    print_section("测试总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！BI分析页面已修复")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    test_all()
