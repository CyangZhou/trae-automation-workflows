#!/usr/bin/env python3
"""
Trae Workflow Manager - 工作流模板系统
保存、管理和执行自动化工作流
"""

import yaml
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess

WORKFLOW_DIR = Path("e:/traework/00 ai助手研发/.trae/workflows")
TEMPLATE_DIR = Path("e:/traework/00 ai助手研发/.trae/templates")


class WorkflowManager:
    def __init__(self):
        self.workflow_dir = WORKFLOW_DIR
        self.template_dir = TEMPLATE_DIR
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
    def list_workflows(self) -> List[Dict]:
        """列出所有可用工作流"""
        workflows = []
        for yaml_file in self.workflow_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    workflows.append({
                        "name": data.get('name', yaml_file.stem),
                        "description": data.get('description', ''),
                        "file": str(yaml_file),
                        "version": data.get('version', '1.0.0'),
                        "steps_count": len(data.get('steps', []))
                    })
            except Exception as e:
                workflows.append({
                    "name": yaml_file.stem,
                    "error": str(e),
                    "file": str(yaml_file)
                })
        return workflows
    
    def save_workflow(self, name: str, description: str, steps: List[Dict], triggers: List[str] = None) -> Dict:
        """保存新工作流"""
        workflow_data = {
            "name": name,
            "description": description,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "triggers": triggers or [],
            "steps": steps
        }
        
        file_path = self.workflow_dir / f"{name}.yaml"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(workflow_data, f, allow_unicode=True, sort_keys=False)
                
            return {
                "status": "success",
                "message": f"工作流 '{name}' 已保存",
                "path": str(file_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存失败: {str(e)}"
            }
    
    def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
        """执行工作流"""
        workflow_file = self.workflow_dir / f"{workflow_name}.yaml"
        if not workflow_file.exists():
            return {"status": "error", "message": f"工作流 '{workflow_name}' 不存在"}
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
        except Exception as e:
            return {"status": "error", "message": f"读取工作流失败: {str(e)}"}
        
        results = []
        variables = context or {}
        variables['current_date'] = datetime.now().strftime('%Y-%m-%d')
        variables['current_time'] = datetime.now().strftime('%H:%M:%S')
        
        for i, step in enumerate(workflow.get('steps', [])):
            step_result = self._execute_step(step, variables)
            step_result['step_id'] = step.get('id', i + 1)
            step_result['step_name'] = step.get('name', f'Step {i + 1}')
            results.append(step_result)
            
            if step_result.get('status') == 'error':
                return {
                    "status": "error",
                    "message": f"步骤 {step.get('name', i+1)} 执行失败",
                    "step_results": results
                }
            
            # 保存变量
            if step_result.get('save_as'):
                variables[step_result['save_as']] = step_result.get('output', '')
        
        return {
            "status": "success",
            "workflow": workflow_name,
            "results": results
        }
    
    def _execute_step(self, step: Dict, variables: Dict) -> Dict:
        """执行单个步骤"""
        action = step.get('action')
        params = step.get('params', {})
        
        # 替换变量
        params = self._substitute_variables(params, variables)
        
        if action == 'run_command':
            return self._run_command_step(params)
        elif action == 'generate_document':
            return self._generate_document_step(params)
        elif action == 'open_file':
            return self._open_file_step(params)
        elif action == 'notify':
            return self._notify_step(params)
        else:
            return {"status": "error", "message": f"未知动作: {action}"}
    
    def _substitute_variables(self, obj: Any, variables: Dict) -> Any:
        """替换对象中的变量占位符"""
        if isinstance(obj, str):
            pattern = r'\{\{(\w+)\}\}'
            def replace_var(match):
                var_name = match.group(1)
                return str(variables.get(var_name, match.group(0)))
            return re.sub(pattern, replace_var, obj)
        elif isinstance(obj, dict):
            return {k: self._substitute_variables(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_variables(item, variables) for item in obj]
        return obj
    
    def _run_command_step(self, params: Dict) -> Dict:
        """执行命令步骤"""
        command = params.get('command')
        if not command:
            return {"status": "error", "message": "未指定命令"}
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=params.get('timeout', 30)
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
                "save_as": params.get('save_as')
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "命令执行超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _generate_document_step(self, params: Dict) -> Dict:
        """生成文档步骤"""
        template_name = params.get('template')
        variables = params.get('variables', {})
        output_path = params.get('output')
        
        if not template_name or not output_path:
            return {"status": "error", "message": "缺少模板或输出路径"}
        
        template_file = self.template_dir / template_name
        if not template_file.exists():
            # 尝试使用默认模板
            default_content = self._create_default_template(template_name)
            if default_content:
                template_content = default_content
            else:
                return {"status": "error", "message": f"模板 '{template_name}' 不存在"}
        else:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        # 替换模板变量
        for key, value in variables.items():
            template_content = template_content.replace(f'{{{{{key}}}}}', str(value))
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return {
            "status": "success",
            "output": str(output_file),
            "save_as": params.get('save_as')
        }
    
    def _open_file_step(self, params: Dict) -> Dict:
        """打开文件步骤"""
        file_path = params.get('path')
        if not file_path:
            return {"status": "error", "message": "未指定文件路径"}
        
        file_path = Path(file_path)
        if not file_path.exists():
            return {"status": "error", "message": f"文件不存在: {file_path}"}
        
        try:
            # 使用系统默认程序打开
            os.startfile(str(file_path))
            return {
                "status": "success",
                "message": f"已打开: {file_path}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _notify_step(self, params: Dict) -> Dict:
        """通知步骤"""
        message = params.get('message', '工作流执行完成')
        print(f"[通知] {message}")
        return {
            "status": "success",
            "message": message
        }
    
    def _create_default_template(self, template_name: str) -> Optional[str]:
        """创建默认模板"""
        templates = {
            'weekly-report.md': '''# {{title}} - 周报

**日期**: {{date}}  
**作者**: {{author}}

## 本周工作内容

{{work_content}}

## 下周计划

{{next_week_plan}}

## 遇到的问题

{{issues}}

---
*由 AI 自动生成*
''',
            'meeting-notes.md': '''# 会议纪要

**会议主题**: {{topic}}  
**时间**: {{date}} {{time}}  
**参会人员**: {{attendees}}

## 会议内容

{{content}}

## 待办事项

{{action_items}}

---
*由 AI 自动生成*
'''
        }
        return templates.get(template_name)


def main():
    parser = argparse.ArgumentParser(
        description='Trae Workflow Manager - 工作流管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s list                          # 列出所有工作流
  %(prog)s run weekly-report             # 执行周报工作流
  %(prog)s run weekly-report --var date=2026-02-11
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有工作流')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='执行工作流')
    run_parser.add_argument('workflow', help='工作流名称')
    run_parser.add_argument('--var', action='append', help='变量 (key=value)')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看工作流详情')
    info_parser.add_argument('workflow', help='工作流名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = WorkflowManager()
    
    if args.command == 'list':
        workflows = manager.list_workflows()
        print(json.dumps(workflows, ensure_ascii=False, indent=2))
        
    elif args.command == 'run':
        context = {}
        if args.var:
            for var in args.var:
                if '=' in var:
                    key, value = var.split('=', 1)
                    context[key] = value
        result = manager.execute_workflow(args.workflow, context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.command == 'info':
        workflow_file = WORKFLOW_DIR / f"{args.workflow}.yaml"
        if workflow_file.exists():
            with open(workflow_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": f"工作流 '{args.workflow}' 不存在"}, ensure_ascii=False))


if __name__ == '__main__':
    import argparse
    main()
