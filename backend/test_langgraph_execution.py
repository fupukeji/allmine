"""
测试 LangGraph 是否真正被调用
"""

import asyncio
from datetime import date, timedelta
from workflows.service import get_workflow_service
from workflows.graph import get_report_workflow


async def test_langgraph_invocation():
    """测试 LangGraph 是否被调用"""
    
    print("\n" + "="*80)
    print("测试 LangGraph 调用")
    print("="*80 + "\n")
    
    # 1. 检查 LangGraph 应用是否存在
    print("【步骤1】检查 LangGraph 应用")
    workflow_app = get_report_workflow()
    print(f"  - 工作流应用: {workflow_app}")
    print(f"  - 类型: {type(workflow_app)}")
    print(f"  - 是否为None: {workflow_app is None}")
    print()
    
    # 2. 创建测试任务
    task_context = {
        "report_id": 888,
        "user_id": 1,
        "api_key": "test_key",
        "model": "glm-4-flash",
        "report_type": "weekly",
        "start_date": date.today() - timedelta(days=7),
        "end_date": date.today(),
        "focus_areas": []
    }
    
    print("【步骤2】执行工作流")
    print(f"  - 报告ID: {task_context['report_id']}")
    print()
    
    # 3. 获取工作流服务并执行
    workflow_service = get_workflow_service()
    
    # 打印详细日志
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("【步骤3】开始执行（观察日志中的 'LangGraph' 关键字）")
    print("-" * 80)
    
    final_state = await workflow_service.execute_workflow(task_context)
    
    print("-" * 80)
    print()
    
    # 4. 分析执行路径
    print("【步骤4】分析执行路径")
    execution_path = final_state.get('execution_path', [])
    print(f"  - 执行节点数: {len(execution_path)}")
    
    if len(execution_path) > 0:
        print(f"  - 第一个节点: {execution_path[0].get('node')}")
        print(f"  - 最后一个节点: {execution_path[-1].get('node')}")
    
    print()
    
    # 5. 结论
    print("="*80)
    if workflow_app is not None:
        print("✅ LangGraph 应用已成功创建并编译")
        print("✅ 工作流执行应该使用了 LangGraph 驱动")
    else:
        print("❌ LangGraph 应用为 None，使用了降级模式")
    print("="*80 + "\n")


if __name__ == '__main__':
    asyncio.run(test_langgraph_invocation())
