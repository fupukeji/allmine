"""
工作流端到端测试
测试完整的报告生成流程
"""

import asyncio
import json
from datetime import datetime, date, timedelta
from workflows.service import get_workflow_service


async def test_workflow_e2e():
    """测试完整工作流"""
    print("\n" + "="*80)
    print("开始端到端工作流测试")
    print("="*80 + "\n")
    
    # 模拟任务上下文（测试用，不需要真实API Key）
    task_context = {
        "report_id": 999,  # 测试报告ID
        "user_id": 1,  # 测试用户ID
        "api_key": "test_dummy_key",  # 测试用Key
        "model": "glm-4-flash",
        "report_type": "weekly",
        "start_date": date.today() - timedelta(days=7),
        "end_date": date.today(),
        "focus_areas": []
    }
    
    print("📋 测试任务上下文:")
    print(f"  - 报告ID: {task_context['report_id']}")
    print(f"  - 用户ID: {task_context['user_id']}")
    print(f"  - 报告类型: {task_context['report_type']}")
    print(f"  - 时间范围: {task_context['start_date']} 至 {task_context['end_date']}")
    print()
    
    try:
        # 获取工作流服务
        workflow_service = get_workflow_service()
        
        # 执行工作流
        print("🚀 开始执行工作流...\n")
        final_state = await workflow_service.execute_workflow(task_context)
        
        print("\n" + "="*80)
        print("工作流执行完成！")
        print("="*80 + "\n")
        
        # 输出结果
        print("📊 执行结果:")
        print(f"  - 状态: {final_state.get('error_message') or '成功'}")
        print(f"  - 重试次数: {final_state.get('retry_count', 0)}")
        print(f"  - 执行路径长度: {len(final_state.get('execution_path', []))}")
        print()
        
        # 输出执行路径
        print("🔍 执行路径详情:")
        for i, node in enumerate(final_state.get('execution_path', []), 1):
            status_icon = "✅" if node['status'] == 'completed' else "❌"
            print(f"  {i}. {status_icon} {node['node']} - {node['status']}")
            if 'timestamp' in node:
                print(f"     时间: {node['timestamp']}")
        print()
        
        # 输出Agent决策
        if final_state.get('agent_decisions'):
            print("🤖 Agent决策:")
            for i, decision in enumerate(final_state['agent_decisions'], 1):
                print(f"  {i}. {decision['node']}")
                if 'decision' in decision:
                    print(f"     决策: {decision['decision']}")
        print()
        
        # 输出质量评分
        if final_state.get('quality_score'):
            print("⭐ 质量评分:")
            score = final_state['quality_score']
            print(f"  - 总分: {score.get('total_score', 0):.1f}/100")
            print(f"  - JSON有效性: {score.get('json_validity', 0)}")
            print(f"  - 完整性: {score.get('completeness', 0):.1f}")
            print(f"  - 数据准确性: {score.get('data_accuracy', 0)}")
        print()
        
        print("="*80)
        print("✅ 测试完成！")
        print("="*80 + "\n")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_workflow_visualization():
    """测试工作流可视化"""
    print("\n" + "="*80)
    print("测试工作流可视化")
    print("="*80 + "\n")
    
    workflow_service = get_workflow_service()
    viz_data = workflow_service.get_workflow_visualization()
    
    print("📊 可视化数据:")
    print(f"  - 格式: {viz_data['format']}")
    print(f"  - 节点数量: {len(viz_data['nodes'])}")
    print(f"  - 边数量: {len(viz_data['edges'])}")
    print()
    
    print("节点列表:")
    for node in viz_data['nodes']:
        print(f"  - {node['id']}: {node['name']} ({node['type']})")
    print()
    
    print("Mermaid图定义:")
    print(viz_data['graph'])
    
    print("✅ 可视化测试完成\n")


async def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*80)
    print("测试错误处理")
    print("="*80 + "\n")
    
    # 测试无效的任务上下文
    invalid_context = {
        "report_id": 998,
        "user_id": 99999,  # 不存在的用户
        "api_key": "invalid_key",
        "model": "glm-4-flash",
        "report_type": "weekly",
        "start_date": date.today(),
        "end_date": date.today(),
        "focus_areas": []
    }
    
    print("测试场景: 不存在的用户")
    workflow_service = get_workflow_service()
    final_state = await workflow_service.execute_workflow(invalid_context)
    
    if final_state.get('error_message'):
        print(f"✅ 正确捕获错误: {final_state['error_message'][:100]}")
    else:
        print("⚠️ 未捕获到预期错误")
    
    print("\n✅ 错误处理测试完成\n")


async def main():
    """主测试函数"""
    print("\n" + "🔬"*40)
    print(" "*30 + "工作流测试套件")
    print("🔬"*40 + "\n")
    
    # 1. 端到端测试
    print("【测试1】端到端工作流测试")
    # 注意：由于没有真实API Key，会在generate_report节点失败
    # 但可以测试到该节点之前的所有流程
    await test_workflow_e2e()
    
    # 2. 可视化测试
    print("\n【测试2】工作流可视化测试")
    await test_workflow_visualization()
    
    # 3. 错误处理测试
    print("\n【测试3】错误处理测试")
    await test_error_handling()
    
    print("\n" + "🎉"*40)
    print(" "*30 + "所有测试完成！")
    print("🎉"*40 + "\n")


if __name__ == '__main__':
    # 运行异步测试
    asyncio.run(main())
