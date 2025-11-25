"""检查工作流数据"""
from app import create_app
from models.ai_report import AIReport
import json

app = create_app()

with app.app_context():
    # 获取最新报告
    report = AIReport.query.order_by(AIReport.id.desc()).first()
    
    if not report:
        print("没有找到报告")
        exit()
    
    print(f"\n{'='*80}")
    print(f"报告ID: {report.id}")
    print(f"标题: {report.title}")
    print(f"状态: {report.status}")
    print(f"创建时间: {report.created_at}")
    print(f"{'='*80}\n")
    
    # 检查工作流数据
    if report.execution_path:
        ep = json.loads(report.execution_path)
        print(f"执行节点数: {len(ep)}")
        print("\n执行路径:")
        for i, node in enumerate(ep, 1):
            status_icon = {'completed': '✅', 'failed': '❌', 'skipped': '⏭️'}.get(node.get('status'), '❓')
            print(f"  {i}. {status_icon} {node.get('node')} - {node.get('status')}")
        print()
    else:
        print("❌ execution_path 为空\n")
    
    if report.workflow_metadata:
        wm = json.loads(report.workflow_metadata)
        print(f"工作流元数据:")
        print(f"  - 重试次数: {wm.get('retry_count', 0)}")
        print(f"  - 开始时间: {wm.get('start_time')}")
        print(f"  - 结束时间: {wm.get('end_time')}")
        if wm.get('quality_score'):
            print(f"  - 质量评分: {wm['quality_score'].get('total_score', 0):.1f}/100")
        print()
    else:
        print("❌ workflow_metadata 为空\n")
