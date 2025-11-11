"""
测试报告生成功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试...")

try:
    from app import app, db
    print("✓ 导入app成功")
    
    from models.user import User
    print("✓ 导入User成功")
    
    from services.zhipu_service import ZhipuAiService
    print("✓ 导入ZhipuAiService成功")
    
    from datetime import date, timedelta
    import json
    print("✓ 导入基础库成功")
    
except Exception as e:
    import traceback
    print(f"\n✗ 导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

def test_report_generation():
    with app.app_context():
        # 获取第一个用户
        user = User.query.first()
        if not user:
            print("错误: 没有找到用户")
            return
        
        print(f"使用用户: {user.username} (ID: {user.id})")
        
        # 检查API Token
        api_token = user.get_aliyun_api_token()
        if not api_token:
            print("错误: 用户未配置API Token")
            return
        
        print(f"API Token已配置 (长度: {len(api_token)})")
        
        # 测试数据准备
        try:
            today = date.today()
            start_date = today - timedelta(days=7)
            end_date = today
            
            print(f"\n开始测试报告生成...")
            print(f"时间范围: {start_date} 至 {end_date}")
            
            service = ZhipuAiService(api_token)
            
            # 第一阶段：数据查询
            print("\n=== 第一阶段：数据查询 ===")
            asset_data = service.prepare_asset_data(user.id, start_date, end_date)
            print(f"固定资产数量: {asset_data['fixed_assets']['total_assets']}")
            print(f"虚拟资产项目数: {asset_data['virtual_assets']['total_projects']}")
            
            # 第二阶段：AI预处理
            print("\n=== 第二阶段：AI数据预处理 ===")
            structured_data = service._preprocess_data_with_ai(asset_data)
            print("结构化数据:")
            print(json.dumps(structured_data, ensure_ascii=False, indent=2))
            
            # 第三阶段：报告生成
            print("\n=== 第三阶段：生成周报 ===")
            content = service.generate_weekly_report(user.id, start_date, end_date)
            print("报告内容(前500字符):")
            print(content[:500])
            
            # 解析报告内容
            try:
                report_json = json.loads(content)
                print("\n报告JSON结构:")
                print(f"- executive_summary: {len(report_json.get('executive_summary', ''))} 字符")
                print(f"- 包含字段: {list(report_json.keys())}")
            except Exception as parse_error:
                print(f"\n报告内容解析失败: {parse_error}")
                print(f"原始内容: {content}")
            
            print("\n✅ 测试成功!")
            
        except Exception as e:
            import traceback
            print(f"\n❌ 测试失败!")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            print(f"\n详细堆栈:")
            traceback.print_exc()

if __name__ == '__main__':
    test_report_generation()
