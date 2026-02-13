#!/usr/bin/env python3
"""
智能工作流监控系统
像OpenWork一样主动感知上下文并推荐工作流
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 尝试导入watchdog，如果没有则使用轮询模式
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ watchdog未安装，使用轮询模式 (pip install watchdog)")


class WorkflowRecommender:
    """工作流推荐引擎"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.recommendations: List[Dict] = []
        self.last_check = {}
        
    def analyze_context(self) -> Dict:
        """分析项目上下文"""
        context = {
            'files_changed': [],
            'git_status': {},
            'project_type': None,
            'issues': [],
            'test_coverage': None,
        }
        
        # 检测项目类型
        if (self.project_path / 'requirements.txt').exists():
            context['project_type'] = 'python'
        elif (self.project_path / 'package.json').exists():
            context['project_type'] = 'nodejs'
        elif (self.project_path / 'Cargo.toml').exists():
            context['project_type'] = 'rust'
        elif (self.project_path / 'go.mod').exists():
            context['project_type'] = 'go'
            
        # 检测文件变更
        for pattern in ['*.py', '*.js', '*.md', 'requirements.txt', 'package.json']:
            files = list(self.project_path.rglob(pattern))
            for f in files:
                if f.is_file():
                    mtime = f.stat().st_mtime
                    if pattern not in self.last_check or mtime > self.last_check.get(pattern, 0):
                        context['files_changed'].append(str(f.relative_to(self.project_path)))
                        self.last_check[pattern] = mtime
        
        return context
    
    def recommend_workflows(self, context: Dict) -> List[Dict]:
        """根据上下文推荐工作流"""
        recommendations = []
        
        # 规则1：依赖文件变更
        if any('requirements.txt' in f or 'package.json' in f for f in context['files_changed']):
            recommendations.append({
                'workflow': 'dependency-auto-update',
                'reason': '检测到依赖文件变更',
                'priority': 'high',
                'auto_run': False,
                'action': '检查依赖更新和安全漏洞'
            })
        
        # 规则2：API代码变更
        api_files = [f for f in context['files_changed'] if 'api' in f.lower() or 'route' in f.lower()]
        if api_files:
            recommendations.append({
                'workflow': 'doc-sync-check',
                'reason': f'检测到API代码变更: {", ".join(api_files[:2])}',
                'priority': 'medium',
                'auto_run': False,
                'action': '检查API文档同步'
            })
        
        # 规则3：测试文件变更
        test_files = [f for f in context['files_changed'] if 'test' in f.lower()]
        if test_files:
            recommendations.append({
                'workflow': 'code-coverage-report',
                'reason': f'检测到测试代码变更: {", ".join(test_files[:2])}',
                'priority': 'medium',
                'auto_run': False,
                'action': '运行覆盖率检查'
            })
        
        # 规则4：README或文档变更
        doc_files = [f for f in context['files_changed'] if f.endswith('.md') or f.endswith('.rst')]
        if doc_files:
            recommendations.append({
                'workflow': 'create-readme',
                'reason': '检测到文档变更',
                'priority': 'low',
                'auto_run': False,
                'action': '更新文档'
            })
        
        # 规则5：定期安全检查 (每天一次)
        security_check_file = self.project_path / '.trae' / '.last_security_check'
        if not security_check_file.exists() or \
           (datetime.now() - datetime.fromtimestamp(security_check_file.stat().st_mtime)).days >= 1:
            recommendations.append({
                'workflow': 'security-scan-local',
                'reason': '超过24小时未进行安全检查',
                'priority': 'high',
                'auto_run': True,
                'action': '自动运行安全扫描'
            })
            security_check_file.touch()
        
        return recommendations
    
    def display_recommendations(self, recommendations: List[Dict]):
        """显示推荐结果"""
        if not recommendations:
            return
        
        print("\n" + "="*60)
        print("🤖 智能工作流推荐")
        print("="*60)
        
        # 按优先级分组
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        low_priority = [r for r in recommendations if r['priority'] == 'low']
        
        if high_priority:
            print("\n🔴 高优先级 (建议立即处理):")
            for i, rec in enumerate(high_priority, 1):
                print(f"\n  {i}. [{rec['workflow']}]")
                print(f"     原因: {rec['reason']}")
                print(f"     操作: {rec['action']}")
                if rec['auto_run']:
                    print(f"     ⚡ 将自动执行")
                else:
                    print(f"     💡 运行: workflow run {rec['workflow']}")
        
        if medium_priority:
            print("\n🟡 中优先级 (建议今天处理):")
            for i, rec in enumerate(medium_priority, 1):
                print(f"\n  {i}. [{rec['workflow']}]")
                print(f"     原因: {rec['reason']}")
        
        if low_priority:
            print("\n🟢 低优先级 (可选):")
            for i, rec in enumerate(low_priority, 1):
                print(f"\n  {i}. [{rec['workflow']}]")
                print(f"     原因: {rec['reason']}")
        
        print("\n" + "="*60)
        print("💡 提示: 说 '帮我看看项目' 或 '智能工作流' 可随时获取推荐")
        print("="*60 + "\n")


class IntelligentFileHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """文件变更处理器"""
    
    def __init__(self, recommender: WorkflowRecommender):
        self.recommender = recommender
        self.last_recommendation_time = 0
        self.cooldown = 30  # 30秒冷却时间
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # 忽略特定文件
        ignored_patterns = ['.pyc', '__pycache__', '.git', '.trae', 'node_modules']
        if any(pattern in str(event.src_path) for pattern in ignored_patterns):
            return
        
        current_time = time.time()
        if current_time - self.last_recommendation_time < self.cooldown:
            return
        
        self.last_recommendation_time = current_time
        
        # 分析并推荐
        context = self.recommender.analyze_context()
        recommendations = self.recommender.recommend_workflows(context)
        
        if recommendations:
            self.recommender.display_recommendations(recommendations)


class IntelligentWorkflowDaemon:
    """智能工作流守护进程"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.recommender = WorkflowRecommender(project_path)
        self.observer = None
        self.running = False
        
    def start(self):
        """启动监控"""
        print(f"🚀 启动智能工作流监控: {self.project_path}")
        print("📁 正在监听文件变化...")
        print("⏹️  按 Ctrl+C 停止\n")
        
        if WATCHDOG_AVAILABLE:
            # 使用watchdog监控
            event_handler = IntelligentFileHandler(self.recommender)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.project_path, recursive=True)
            self.observer.start()
        
        self.running = True
        
        try:
            while self.running:
                if not WATCHDOG_AVAILABLE:
                    # 轮询模式
                    context = self.recommender.analyze_context()
                    recommendations = self.recommender.recommend_workflows(context)
                    if recommendations:
                        self.recommender.display_recommendations(recommendations)
                
                time.sleep(5)  # 每5秒检查一次
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止监控"""
        print("\n🛑 停止智能工作流监控")
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def check_now(self):
        """立即检查一次"""
        context = self.recommender.analyze_context()
        recommendations = self.recommender.recommend_workflows(context)
        self.recommender.display_recommendations(recommendations)
        return recommendations


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能工作流监控系统')
    parser.add_argument('--path', default='.', help='项目路径')
    parser.add_argument('--check', action='store_true', help='立即检查一次')
    parser.add_argument('--daemon', action='store_true', help='启动守护进程')
    
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    
    if not os.path.exists(project_path):
        print(f"❌ 路径不存在: {project_path}")
        sys.exit(1)
    
    daemon = IntelligentWorkflowDaemon(project_path)
    
    if args.check:
        # 立即检查一次
        recommendations = daemon.check_now()
        
        # 询问是否执行
        if recommendations:
            print("\n是否执行推荐的工作流？")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec['workflow']} - {rec['action']}")
            print("  a. 全部执行")
            print("  n. 跳过")
            
    elif args.daemon:
        # 启动守护进程
        daemon.start()
    else:
        # 默认：立即检查一次
        daemon.check_now()


if __name__ == '__main__':
    main()
