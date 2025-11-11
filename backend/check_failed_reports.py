# -*- coding: utf-8 -*-
from app import app, db
from models.ai_report import AIReport

with app.app_context():
    failed_reports = AIReport.query.filter_by(status='failed').order_by(AIReport.created_at.desc()).limit(5).all()
    
    print(f"\n找到 {len(failed_reports)} 个失败的报告:\n")
    
    for r in failed_reports:
        print(f"=" * 80)
        print(f"ID: {r.id}")
        print(f"标题: {r.title}")
        print(f"类型: {r.report_type}")
        print(f"时间范围: {r.start_date} 至 {r.end_date}")
        print(f"创建时间: {r.created_at}")
        print(f"错误信息:")
        print(r.error_message)
        print()
