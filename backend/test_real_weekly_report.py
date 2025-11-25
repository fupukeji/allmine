"""
测试真实的周报生成流程
在Flask应用上下文中运行，使用真实数据
"""

import asyncio
from datetime import date, timedelta
from app import create_app
from workflows.service import get_workflow_service


async def test_real_weekly_report():
    """测试真实周报生成"""
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("📊 测试真实周报生成")
        print("="*80 + "\n")
        
        # 计算本周的时间范围（ISO周）
        today = date.today()
        # 获取本周一
        monday = today - timedelta(days=today.weekday())
        # 获取本周日
        sunday = monday + timedelta(days=6)
        
        print(f"📅 本周时间范围: {monday} 至 {sunday}")
        print(f"   ({monday.strftime('%Y年%m月%d日')} - {sunday.strftime('%m月%d日')})")
        print()
        
        # 构建真实的任务上下文
        task_context = {
            "report_id": 9999,  # 测试报告ID
            "user_id": 1,  # 假设用户ID为1
            "api_key": "14151791ef28494ab6b30f0964675334.ttwJa0Wtep6Q1Hx7",  # 真实的智谱AI Key
            "model": "glm-4-flash",
            "report_type": "weekly",
            "start_date": monday,
            "end_date": sunday,
            "focus_areas": [],
            "enable_ai_insights": False  # 禁用AI预分析以节省API调用
        }
        
        print("📋 任务配置:")
        print(f"  - 用户ID: {task_context['user_id']}")
        print(f"  - 报告类型: {task_context['report_type']}")
        print(f"  - 模型: {task_context['model']}")
        print(f"  - AI预分析: {'启用' if task_context.get('enable_ai_insights') else '禁用'}")
        print()
        
        # 获取工作流服务
        workflow_service = get_workflow_service()
        
        print("🚀 开始执行工作流...")
        print("-" * 80)
        
        try:
            # 执行工作流
            final_state = await workflow_service.execute_workflow(task_context)
            
            print("-" * 80)
            print()
            
            # 输出执行结果
            print("📊 执行结果:")
            print("="*80)
            
            # 检查是否有错误
            if final_state.get("error_message"):
                print(f"❌ 执行失败: {final_state['error_message']}")
            else:
                print(f"✅ 执行成功")
            
            print()
            
            # 输出统计信息
            print("📈 统计信息:")
            print(f"  - 重试次数: {final_state.get('retry_count', 0)}")
            print(f"  - 执行节点数: {len(final_state.get('execution_path', []))}")
            print(f"  - 开始时间: {final_state.get('start_time', 'N/A')}")
            print(f"  - 结束时间: {final_state.get('end_time', 'N/A')}")
            print()
            
            # 输出执行路径
            print("🔍 执行路径:")
            execution_path = final_state.get('execution_path', [])
            for i, node in enumerate(execution_path, 1):
                status_icon = {
                    'completed': '✅',
                    'failed': '❌',
                    'skipped': '⏭️'
                }.get(node.get('status'), '❓')
                
                print(f"  {i}. {status_icon} {node.get('node')} - {node.get('status')}")
                
                # 显示额外信息
                if node.get('data_summary'):
                    ds = node['data_summary']
                    print(f"      数据: 固定资产{ds.get('fixed_assets_count', 0)}项, 虚拟资产{ds.get('virtual_assets_count', 0)}项")
                
                if node.get('text_length'):
                    print(f"      文本长度: {node['text_length']} 字符")
                
                if node.get('decision'):
                    print(f"      决策: {node['decision'].get('reason', 'N/A')}")
                
                if node.get('quality_score'):
                    qs = node['quality_score']
                    print(f"      质量评分: {qs.get('total_score', 0):.1f}/100")
                
                if node.get('error'):
                    print(f"      错误: {node['error'][:100]}")
            
            print()
            
            # 输出数据查询结果
            if final_state.get('raw_data'):
                print("📦 数据查询结果:")
                raw_data = final_state['raw_data']
                
                # 固定资产
                if 'fixed_assets' in raw_data:
                    fa = raw_data['fixed_assets']
                    print(f"\n  固定资产:")
                    print(f"    - 总数: {fa.get('total_assets', 0)}项")
                    print(f"    - 原始总值: ¥{fa.get('total_original_value', 0):,.2f}")
                    print(f"    - 当前总值: ¥{fa.get('total_current_value', 0):,.2f}")
                    print(f"    - 累计折旧: ¥{fa.get('total_depreciation', 0):,.2f}")
                    print(f"    - 期间收入: ¥{fa.get('total_income', 0):,.2f}")
                    
                    if fa.get('category_stats'):
                        print(f"    - 分类数: {len(fa['category_stats'])}个")
                        for cat_name, cat_data in list(fa['category_stats'].items())[:5]:
                            print(f"      * {cat_name}: {cat_data['count']}项, ¥{cat_data['total_value']:,.2f}")
                
                # 虚拟资产
                if 'virtual_assets' in raw_data:
                    va = raw_data['virtual_assets']
                    print(f"\n  虚拟资产:")
                    print(f"    - 项目总数: {va.get('total_projects', 0)}项")
                    print(f"    - 总投入: ¥{va.get('total_amount', 0):,.2f}")
                    print(f"    - 活跃项目: {va.get('active_count', 0)}项")
                    print(f"    - 过期项目: {va.get('expired_count', 0)}项")
                    print(f"    - 利用率: {va.get('utilization_rate', 0):.1f}%")
                    print(f"    - 浪费率: {va.get('waste_rate', 0):.1f}%")
                    
                    if va.get('category_stats'):
                        print(f"    - 分类数: {len(va['category_stats'])}个")
                        for cat_name, cat_data in list(va['category_stats'].items())[:5]:
                            print(f"      * {cat_name}: {cat_data['count']}项, ¥{cat_data['total_amount']:,.2f}")
                
                print()
            
            # 输出压缩文本预览
            if final_state.get('compressed_text'):
                print("📝 压缩文本预览 (前500字符):")
                print("-" * 80)
                print(final_state['compressed_text'][:500])
                print("..." if len(final_state['compressed_text']) > 500 else "")
                print("-" * 80)
                print()
            
            # 输出上期对比数据
            if final_state.get('comparison_text'):
                print("📊 上期对比数据:")
                print("-" * 80)
                print(final_state['comparison_text'][:300])
                print("..." if len(final_state['comparison_text']) > 300 else "")
                print("-" * 80)
                print()
            
            # 输出Agent决策
            if final_state.get('agent_decisions'):
                print("🤖 Agent决策历史:")
                for i, decision in enumerate(final_state['agent_decisions'], 1):
                    print(f"  {i}. {decision.get('node', 'N/A')}")
                    if decision.get('decision'):
                        d = decision['decision']
                        print(f"     决策: {d.get('next_node', 'N/A')}")
                        print(f"     原因: {d.get('reason', 'N/A')}")
                print()
            
            # 输出报告内容（如果有）
            if final_state.get('report_content'):
                print("📄 报告内容预览 (前500字符):")
                print("-" * 80)
                content = final_state['report_content']
                print(content[:500])
                print("..." if len(content) > 500 else "")
                print("-" * 80)
                print()
            
            print("="*80)
            print("✅ 测试完成！")
            print("="*80 + "\n")
            
            return final_state
            
        except Exception as e:
            print("-" * 80)
            print()
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == '__main__':
    # 运行测试
    result = asyncio.run(test_real_weekly_report())
    
    if result:
        print("\n" + "🎉"*40)
        print("测试执行完成！查看上方输出了解详细信息")
        print("🎉"*40 + "\n")
