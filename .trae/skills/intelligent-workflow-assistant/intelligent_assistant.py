#!/usr/bin/env python3
"""
智能工作流助手 - 完全兼容Trae IDE的Skill实现
像OpenWork一样主动推荐工作流，但100%兼容现有系统
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 确保可以导入现有的workflow_runner
sys.path.insert(0, str(Path(__file__).parent.parent / 'workflow-runner'))
try:
    from workflow_runner import list_workflows, run_workflow, find_workflow_by_trigger
except ImportError:
    # 如果导入失败，提供备用实现
    list_workflows = None
    run_workflow = None
    find_workflow_by_trigger = None


class IntelligentWorkflowAssistant:
    """
    智能工作流助手
    
    设计原则：
    1. 完全兼容 - 不修改任何现有代码
    2. 零侵入 - 作为独立Skill运行
    3. 可回退 - 随时可切换回传统模式
    4. 渐进增强 - 智能功能可选启用
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path or os.getcwd())
        self.skill_dir = Path(__file__).parent
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载Skill配置"""
        config_file = self.skill_dir / 'skill.yaml'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _get_workflow_manager_path(self) -> Path:
        """获取workflow_manager.py路径（兼容全局和项目级）"""
        # 优先项目级
        project_manager = self.project_path / '.trae' / 'workflows' / 'workflow_manager.py'
        if project_manager.exists():
            return project_manager
        
        # 全局级
        global_manager = Path("C:/Users/Administrator/.trae-cn/workflows/workflow_manager.py")
        if global_manager.exists():
            return global_manager
        
        # 当前研发目录
        dev_manager = Path("e:/traework/00 ai助手研发/.trae/workflows/workflow_manager.py")
        if dev_manager.exists():
            return dev_manager
        
        return None
    
    def _get_all_workflows(self) -> List[Dict]:
        """获取所有可用工作流（复用现有逻辑）"""
        if list_workflows:
            return list_workflows()
        
        # 备用实现：直接读取YAML
        workflows = []
        workflow_dirs = [
            self.project_path / '.trae' / 'workflows',
            Path("C:/Users/Administrator/.trae-cn/workflows"),
            Path("e:/traework/00 ai助手研发/.trae/workflows")
        ]
        
        for workflow_dir in workflow_dirs:
            if workflow_dir.exists():
                for yaml_file in workflow_dir.glob("*.yaml"):
                    try:
                        with open(yaml_file, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            workflows.append({
                                "name": data.get('name', yaml_file.stem),
                                "description": data.get('description', ''),
                                "file": str(yaml_file),
                                "triggers": data.get('triggers', [])
                            })
                    except:
                        pass
        
        return workflows
    
    def analyze_context(self) -> Dict:
        """
        分析项目上下文
        这是智能推荐的核心，完全独立于现有系统
        """
        context = {
            'project_type': None,
            'files': {},
            'git_status': {},
            'recent_changes': [],
            'detected_patterns': []
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
        elif (self.project_path / 'pom.xml').exists():
            context['project_type'] = 'java'
        
        # 扫描关键文件
        key_files = [
            'requirements.txt', 'package.json', 'Cargo.toml', 'go.mod', 'pom.xml',
            'README.md', 'CHANGELOG.md', 'LICENSE',
            '.gitignore', '.dockerignore'
        ]
        
        for filename in key_files:
            file_path = self.project_path / filename
            context['files'][filename] = {
                'exists': file_path.exists(),
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'mtime': file_path.stat().st_mtime if file_path.exists() else 0
            }
        
        # 检测代码模式
        code_patterns = {
            'api_files': list(self.project_path.rglob("*api*.py"))[:5],
            'test_files': list(self.project_path.rglob("test_*.py"))[:5],
            'doc_files': list(self.project_path.rglob("*.md"))[:5],
        }
        context['files'].update(code_patterns)
        
        return context
    
    def recommend_workflows(self, context: Dict = None) -> List[Dict]:
        """
        智能推荐工作流
        基于上下文分析，而非简单关键词匹配
        """
        if context is None:
            context = self.analyze_context()
        
        recommendations = []
        intelligence_config = self.config.get('intelligence', {})
        rules = intelligence_config.get('context_rules', [])
        
        # 应用规则
        for rule in rules:
            if self._match_rule(rule, context):
                recommendations.append({
                    'workflow': rule.get('workflow'),
                    'name': rule.get('name'),
                    'priority': rule.get('priority', 'medium'),
                    'message': rule.get('message', ''),
                    'auto_run': rule.get('auto_run', False),
                    'reason': self._generate_reason(rule, context)
                })
        
        # 去重并排序
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['workflow'] not in seen:
                seen.add(rec['workflow'])
                unique_recommendations.append(rec)
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return unique_recommendations
    
    def _match_rule(self, rule: Dict, context: Dict) -> bool:
        """检查规则是否匹配上下文"""
        patterns = rule.get('patterns', [])
        
        # 检查文件模式
        for pattern in patterns:
            if '*' in pattern:
                # 通配符匹配
                matching_files = list(self.project_path.rglob(pattern))
                if matching_files:
                    return True
            else:
                # 精确匹配
                if (self.project_path / pattern).exists():
                    return True
        
        return False
    
    def _generate_reason(self, rule: Dict, context: Dict) -> str:
        """生成推荐理由"""
        patterns = rule.get('patterns', [])
        existing_files = []
        
        for pattern in patterns:
            if '*' in pattern:
                files = list(self.project_path.rglob(pattern))
                existing_files.extend([f.name for f in files[:2]])
            else:
                if (self.project_path / pattern).exists():
                    existing_files.append(pattern)
        
        if existing_files:
            return f"检测到文件: {', '.join(existing_files[:2])}"
        
        return rule.get('message', '基于项目分析')
    
    def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
        """
        执行工作流
        完全复用现有workflow_manager，确保兼容性
        """
        manager_path = self._get_workflow_manager_path()
        
        if not manager_path:
            return {
                'status': 'error',
                'message': '未找到workflow_manager.py'
            }
        
        try:
            # 使用现有Skill执行
            if run_workflow:
                return run_workflow(workflow_name, context)
            
            # 备用：直接调用
            import subprocess
            result = subprocess.run(
                [sys.executable, str(manager_path), 'run', workflow_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    'status': 'error',
                    'message': result.stderr
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def display_recommendations(self, recommendations: List[Dict]):
        """显示推荐结果（交互式）"""
        if not recommendations:
            print("\n✅ 项目状态良好，暂无推荐的工作流")
            return
        
        print("\n" + "="*70)
        print("🤖 智能工作流推荐")
        print("="*70)
        print(f"\n项目路径: {self.project_path}")
        print(f"项目类型: {self.analyze_context().get('project_type', '未知')}")
        print()
        
        # 分组显示
        groups = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for rec in recommendations:
            groups.get(rec['priority'], []).append(rec)
        
        # 高优先级
        if groups['high']:
            print("🔴 高优先级 (建议立即处理):\n")
            for i, rec in enumerate(groups['high'], 1):
                print(f"  {i}. 【{rec['workflow']}】")
                print(f"     💡 {rec['message']}")
                print(f"     📋 {rec['reason']}")
                if rec['auto_run']:
                    print(f"     ⚡ 将自动执行")
                print()
        
        # 中优先级
        if groups['medium']:
            print("🟡 中优先级 (建议今天处理):\n")
            for i, rec in enumerate(groups['medium'], 1):
                print(f"  {i}. 【{rec['workflow']}】")
                print(f"     💡 {rec['message']}")
                print()
        
        # 低优先级
        if groups['low']:
            print("🟢 低优先级 (可选):\n")
            for i, rec in enumerate(groups['low'], 1):
                print(f"  {i}. 【{rec['workflow']}】")
                print(f"     💡 {rec['message']}")
                print()
        
        print("="*70)
        print("💡 使用方式:")
        print("   • 说 '运行 {工作流名}' 执行特定工作流")
        print("   • 说 '全部运行' 执行所有推荐")
        print("   • 说 '忽略' 跳过本次推荐")
        print("="*70 + "\n")
    
    def run_interactive(self):
        """交互式运行"""
        context = self.analyze_context()
        recommendations = self.recommend_workflows(context)
        
        self.display_recommendations(recommendations)
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'context': context
        }


def main():
    """主函数 - 作为Skill入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='智能工作流助手 - 像OpenWork一样主动推荐'
    )
    parser.add_argument('--path', default='.', help='项目路径')
    parser.add_argument('--run', help='直接运行指定工作流')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    assistant = IntelligentWorkflowAssistant(args.path)
    
    if args.run:
        # 直接执行工作流
        result = assistant.execute_workflow(args.run)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n执行结果: {result.get('status', 'unknown')}")
            if result.get('message'):
                print(f"消息: {result['message']}")
    else:
        # 交互式推荐
        result = assistant.run_interactive()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
