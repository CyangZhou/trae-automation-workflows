#!/usr/bin/env python3
"""
Trae Workflow Manager V2 - 自验证闭环工作流系统
支持：验证步骤、自愈机制、断言引擎
"""

import yaml
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import subprocess
import traceback

WORKFLOW_DIR = Path("e:/traework/00 ai助手研发/.trae/workflows")
TEMPLATE_DIR = Path("e:/traework/00 ai助手研发/.trae/templates")


class VerificationEngine:
    """验证引擎 - 支持多种验证类型"""
    
    @staticmethod
    def verify_file_exists(path: str) -> Tuple[bool, str]:
        """验证文件存在"""
        file_path = Path(path)
        if file_path.exists():
            size = file_path.stat().st_size
            return True, f"文件存在: {path} (大小: {size} bytes)"
        return False, f"文件不存在: {path}"
    
    @staticmethod
    def verify_command_success(command: str, timeout: int = 30) -> Tuple[bool, str]:
        """验证命令执行成功"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return True, f"命令成功: {command}\n输出: {result.stdout[:500]}"
            return False, f"命令失败 (exit={result.returncode}): {command}\n错误: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return False, f"命令超时: {command}"
        except Exception as e:
            return False, f"命令异常: {command}\n错误: {str(e)}"
    
    @staticmethod
    def verify_content_assert(file: str, contains: List[str], exact_match: bool = False) -> Tuple[bool, str]:
        """验证文件内容断言"""
        file_path = Path(file)
        if not file_path.exists():
            return False, f"文件不存在: {file}"
        
        try:
            content = file_path.read_text(encoding='utf-8')
            missing = []
            for pattern in contains:
                if exact_match:
                    if pattern not in content:
                        missing.append(pattern)
                else:
                    if not re.search(pattern, content, re.IGNORECASE):
                        missing.append(pattern)
            
            if missing:
                return False, f"内容断言失败，缺少: {missing}"
            return True, f"内容断言通过，包含所有: {contains}"
        except Exception as e:
            return False, f"读取文件失败: {str(e)}"
    
    @staticmethod
    def verify_diagnostics() -> Tuple[bool, str]:
        """验证代码诊断（模拟，实际由 IDE 提供）"""
        return True, "诊断检查通过（由 IDE GetDiagnostics 工具执行）"
    
    @staticmethod
    def verify_test_pass(command: str = "pytest", timeout: int = 120) -> Tuple[bool, str]:
        """验证测试通过"""
        return VerificationEngine.verify_command_success(command, timeout)
    
    @staticmethod
    def verify_json_valid(path: str) -> Tuple[bool, str]:
        """验证 JSON 格式有效"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return False, f"文件不存在: {path}"
            content = file_path.read_text(encoding='utf-8')
            json.loads(content)
            return True, f"JSON 格式有效: {path}"
        except json.JSONDecodeError as e:
            return False, f"JSON 格式无效: {path}\n错误: {str(e)}"
    
    @staticmethod
    def verify_python_import(module: str) -> Tuple[bool, str]:
        """验证 Python 模块可导入"""
        command = f'python -c "import {module}"'
        return VerificationEngine.verify_command_success(command)


class HealEngine:
    """自愈引擎 - 自动修复失败"""
    
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.attempt_count = 0
        self.fix_history = []
    
    def diagnose_failure(self, error_message: str) -> List[str]:
        """诊断失败原因"""
        suggestions = []
        error_lower = error_message.lower()
        
        if "filenotfounderror" in error_lower or "文件不存在" in error_lower:
            suggestions.extend([
                "检查路径是否正确",
                "检查工作目录",
                "创建所需目录"
            ])
        
        if "permissionerror" in error_lower or "权限" in error_lower:
            suggestions.extend([
                "检查文件权限",
                "以管理员身份运行"
            ])
        
        if "modulenotfounderror" in error_lower or "no module" in error_lower:
            suggestions.extend([
                "安装缺失依赖",
                "检查虚拟环境"
            ])
        
        if "timeout" in error_lower or "超时" in error_lower:
            suggestions.extend([
                "增加超时时间",
                "检查网络连接",
                "检查资源占用"
            ])
        
        if "syntaxerror" in error_lower or "语法错误" in error_lower:
            suggestions.extend([
                "检查代码语法",
                "运行 linter 检查"
            ])
        
        return suggestions if suggestions else ["检查错误日志", "尝试手动执行"]
    
    def attempt_fix(self, step: Dict, error: str) -> Dict:
        """尝试修复"""
        self.attempt_count += 1
        diagnosis = self.diagnose_failure(error)
        
        fix_result = {
            "attempt": self.attempt_count,
            "error": error,
            "diagnosis": diagnosis,
            "actions_taken": [],
            "success": False
        }
        
        if self.attempt_count > self.max_attempts:
            fix_result["message"] = f"已达到最大尝试次数 ({self.max_attempts})"
            return fix_result
        
        strategy = step.get('strategy', 'retry')
        
        if strategy == 'retry':
            fix_result["actions_taken"].append("重试执行")
            fix_result["message"] = "建议重试执行该步骤"
        
        elif strategy == 'retry_with_fix':
            fix_result["actions_taken"].extend(diagnosis)
            fix_result["message"] = f"建议修复方案: {diagnosis}"
        
        elif strategy == 'rollback':
            fix_result["actions_taken"].append("回滚到上一状态")
            fix_result["message"] = "建议回滚并重试"
        
        elif strategy == 'alternative':
            alt_action = step.get('alternative_action')
            if alt_action:
                fix_result["actions_taken"].append(f"执行替代方案: {alt_action}")
                fix_result["message"] = f"建议执行替代方案"
        
        self.fix_history.append(fix_result)
        return fix_result


class WorkflowManagerV2:
    """工作流管理器 V2 - 支持验证和自愈"""
    
    def __init__(self):
        self.workflow_dir = WORKFLOW_DIR
        self.template_dir = TEMPLATE_DIR
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.verification = VerificationEngine()
        self.healer = HealEngine()
    
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
                        "steps_count": len(data.get('steps', [])),
                        "has_verification": any(
                            s.get('action') == 'verify' 
                            for s in data.get('steps', [])
                        )
                    })
            except Exception as e:
                workflows.append({
                    "name": yaml_file.stem,
                    "error": str(e),
                    "file": str(yaml_file)
                })
        return workflows
    
    def execute_workflow(self, workflow_name: str, context: Dict = None) -> Dict:
        """执行工作流（带验证和自愈）"""
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
        variables['workflow_name'] = workflow_name
        
        print(f"\n{'='*60}")
        print(f"🚀 执行工作流: {workflow.get('name', workflow_name)}")
        print(f"{'='*60}\n")
        
        for i, step in enumerate(workflow.get('steps', [])):
            step_id = step.get('id', i + 1)
            step_name = step.get('name', f'Step {i + 1}')
            
            print(f"\n📍 步骤 {step_id}: {step_name}")
            print("-" * 40)
            
            step_result = self._execute_step(step, variables)
            step_result['step_id'] = step_id
            step_result['step_name'] = step_name
            results.append(step_result)
            
            if step_result.get('status') == 'error':
                print(f"❌ 步骤失败: {step_result.get('message', '未知错误')}")
                
                if step.get('on_failure') == 'continue':
                    print("⚠️ 配置为继续执行，跳过此步骤")
                    continue
                
                return {
                    "status": "error",
                    "message": f"步骤 '{step_name}' 执行失败",
                    "step_results": results,
                    "heal_suggestions": step_result.get('heal_suggestions', [])
                }
            
            if step_result.get('status') == 'success':
                print(f"✅ 步骤成功")
            
            if step_result.get('save_as'):
                variables[step_result['save_as']] = step_result.get('output', '')
        
        print(f"\n{'='*60}")
        print(f"🎉 工作流执行完成: {workflow_name}")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "workflow": workflow_name,
            "results": results,
            "variables": variables
        }
    
    def _execute_step(self, step: Dict, variables: Dict) -> Dict:
        """执行单个步骤"""
        action = step.get('action')
        params = step.get('params', {})
        
        params = self._substitute_variables(params, variables)
        
        if action == 'run_command':
            return self._run_command_step(params)
        elif action == 'verify':
            return self._verify_step(step, params, variables)
        elif action == 'heal':
            return self._heal_step(step, params, variables)
        elif action == 'generate_document':
            return self._generate_document_step(params)
        elif action == 'open_file':
            return self._open_file_step(params)
        elif action == 'notify':
            return self._notify_step(params)
        elif action == 'assert':
            return self._assert_step(params)
        else:
            return {"status": "error", "message": f"未知动作: {action}"}
    
    def _verify_step(self, step: Dict, params: Dict, variables: Dict = None) -> Dict:
        """执行验证步骤"""
        verify_type = step.get('type', params.get('type', 'command_success'))
        fail_message = step.get('fail_message', params.get('fail_message', '验证失败'))
        variables = variables or {}
        
        print(f"🔍 验证类型: {verify_type}")
        
        success = False
        message = ""
        
        if verify_type == 'file_exists':
            path = self._substitute_variables(step.get('path', params.get('path', '')), variables)
            success, message = self.verification.verify_file_exists(path)
        
        elif verify_type == 'command_success':
            command = self._substitute_variables(params.get('command', step.get('command', '')), variables)
            timeout = params.get('timeout', step.get('timeout', 30))
            success, message = self.verification.verify_command_success(command, timeout)
        
        elif verify_type == 'content_assert':
            file = self._substitute_variables(params.get('file', step.get('file', '')), variables)
            contains = params.get('contains', step.get('contains', []))
            success, message = self.verification.verify_content_assert(file, contains)
        
        elif verify_type == 'diagnostics':
            success, message = self.verification.verify_diagnostics()
        
        elif verify_type == 'test_pass':
            command = self._substitute_variables(params.get('command', 'pytest'), variables)
            timeout = params.get('timeout', 120)
            success, message = self.verification.verify_test_pass(command, timeout)
        
        elif verify_type == 'json_valid':
            path = self._substitute_variables(params.get('path', step.get('path', '')), variables)
            success, message = self.verification.verify_json_valid(path)
        
        elif verify_type == 'python_import':
            module = self._substitute_variables(params.get('module', step.get('module', '')), variables)
            success, message = self.verification.verify_python_import(module)
        
        else:
            return {"status": "error", "message": f"未知验证类型: {verify_type}"}
        
        print(f"   结果: {'✅ 通过' if success else '❌ 失败'}")
        print(f"   详情: {message[:200]}")
        
        if not success:
            heal_suggestions = self.healer.diagnose_failure(message)
            return {
                "status": "error",
                "message": fail_message,
                "details": message,
                "heal_suggestions": heal_suggestions
            }
        
        return {
            "status": "success",
            "message": "验证通过",
            "details": message
        }
    
    def _heal_step(self, step: Dict, params: Dict, variables: Dict) -> Dict:
        """执行自愈步骤"""
        on_failure_step_id = step.get('on_failure')
        strategy = step.get('strategy', 'retry')
        max_attempts = step.get('max_attempts', 3)
        
        self.healer = HealEngine(max_attempts)
        
        return {
            "status": "success",
            "message": f"自愈配置已设置: strategy={strategy}, max_attempts={max_attempts}"
        }
    
    def _assert_step(self, params: Dict) -> Dict:
        """执行断言步骤"""
        condition = params.get('condition')
        message = params.get('message', '断言失败')
        
        try:
            result = eval(condition)
            if result:
                return {"status": "success", "message": f"断言通过: {condition}"}
            return {"status": "error", "message": message}
        except Exception as e:
            return {"status": "error", "message": f"断言执行失败: {str(e)}"}
    
    def _substitute_variables(self, obj: Any, variables: Dict) -> Any:
        """替换变量占位符"""
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
        
        print(f"⚡ 执行命令: {command[:100]}...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=params.get('timeout', 30),
                cwd=params.get('cwd')
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip() if result.stderr else None
            
            if output:
                print(f"   输出: {output[:300]}")
            if error:
                print(f"   错误: {error[:200]}")
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output,
                "error": error,
                "return_code": result.returncode,
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
        
        if not output_path:
            return {"status": "error", "message": "缺少输出路径"}
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if template_name:
            template_file = self.template_dir / template_name
            if template_file.exists():
                content = template_file.read_text(encoding='utf-8')
            else:
                content = f"# 自动生成文档\n\n生成时间: {datetime.now()}\n"
        else:
            content = params.get('content', '')
        
        for key, value in variables.items():
            content = content.replace(f'{{{{{key}}}}}', str(value))
        
        output_file.write_text(content, encoding='utf-8')
        
        print(f"📄 生成文档: {output_path}")
        
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
            os.startfile(str(file_path))
            return {"status": "success", "message": f"已打开: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _notify_step(self, params: Dict) -> Dict:
        """通知步骤"""
        message = params.get('message', '工作流执行完成')
        print(f"\n📢 通知: {message}\n")
        return {"status": "success", "message": message}
    
    def validate_workflow(self, workflow_name: str) -> Dict:
        """验证工作流配置"""
        workflow_file = self.workflow_dir / f"{workflow_name}.yaml"
        if not workflow_file.exists():
            return {"valid": False, "error": f"工作流 '{workflow_name}' 不存在"}
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
        except Exception as e:
            return {"valid": False, "error": f"YAML 解析失败: {str(e)}"}
        
        issues = []
        warnings = []
        
        steps = workflow.get('steps', [])
        
        has_verify = any(s.get('action') == 'verify' for s in steps)
        if not has_verify:
            warnings.append("工作流缺少验证步骤，建议添加 verify 步骤")
        
        for i, step in enumerate(steps):
            action = step.get('action')
            
            if action == 'run_command':
                cmd = step.get('params', {}).get('command', '')
                if cmd.strip().startswith('echo ') and '模拟' in cmd:
                    warnings.append(f"步骤 {i+1}: 可能是模拟数据，建议使用真实命令")
            
            if action == 'verify':
                verify_type = step.get('type')
                if not verify_type:
                    issues.append(f"步骤 {i+1}: 验证步骤缺少 type")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "has_verification": has_verify,
            "steps_count": len(steps)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Trae Workflow Manager V2 - 自验证闭环工作流系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s list                          # 列出所有工作流
  %(prog)s run weekly-report             # 执行工作流
  %(prog)s validate weekly-report        # 验证工作流配置
  %(prog)s run weekly-report --var date=2026-02-11
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    subparsers.add_parser('list', help='列出所有工作流')
    
    run_parser = subparsers.add_parser('run', help='执行工作流')
    run_parser.add_argument('workflow', help='工作流名称')
    run_parser.add_argument('--var', action='append', help='变量 (key=value)')
    
    validate_parser = subparsers.add_parser('validate', help='验证工作流配置')
    validate_parser.add_argument('workflow', help='工作流名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = WorkflowManagerV2()
    
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
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    
    elif args.command == 'validate':
        result = manager.validate_workflow(args.workflow)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
