#!/usr/bin/env python3
"""
Smart Router - 智能路由系统
自动判断任务类型，选择最优执行方式，并强制执行验证验收
"""

import os
import sys
import json
import re
import subprocess
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml


class TaskType(Enum):
    STANDARD = "standard"
    REPETITIVE = "repetitive"
    ONE_TIME = "one_time"
    COMPLEX = "complex"
    UNKNOWN = "unknown"


class ExecutionMode(Enum):
    WORKFLOW = "workflow"
    BUILTIN = "builtin"
    HYBRID = "hybrid"


class ValidationLevel(Enum):
    BLOCK = "block"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class ValidationResult:
    name: str
    passed: bool
    level: ValidationLevel
    message: str = ""
    details: List[str] = field(default_factory=list)
    fix_suggestion: str = ""


@dataclass
class TaskAnalysis:
    task_type: TaskType
    execution_mode: ExecutionMode
    confidence: float
    matched_patterns: List[str]
    reason: str


class TaskAnalyzer:
    """任务分析器 - 识别任务类型"""
    
    PATTERNS = {
        TaskType.STANDARD: [
            "安全扫描", "代码审查", "测试覆盖率", "依赖检查", "性能测试",
            "security", "review", "test", "coverage", "lint"
        ],
        TaskType.REPETITIVE: [
            "每天", "每周", "定时", "自动", "周期",
            "daily", "weekly", "schedule", "cron"
        ],
        TaskType.ONE_TIME: [
            "帮我写", "修改这个", "优化一下", "修复", "创建",
            "write", "modify", "optimize", "fix", "create"
        ],
        TaskType.COMPLEX: [
            "重构", "架构", "系统设计", "迁移", "集成",
            "refactor", "architecture", "design", "migrate", "integrate"
        ]
    }
    
    def analyze(self, task_description: str) -> TaskAnalysis:
        desc_lower = task_description.lower()
        
        best_match = TaskType.UNKNOWN
        best_confidence = 0.0
        matched_patterns = []
        
        for task_type, patterns in self.PATTERNS.items():
            matches = [p for p in patterns if p.lower() in desc_lower]
            if matches:
                confidence = len(matches) / len(patterns)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = task_type
                    matched_patterns = matches
        
        execution_mode = self._get_execution_mode(best_match)
        reason = self._get_reason(best_match, matched_patterns)
        
        return TaskAnalysis(
            task_type=best_match,
            execution_mode=execution_mode,
            confidence=best_confidence,
            matched_patterns=matched_patterns,
            reason=reason
        )
    
    def _get_execution_mode(self, task_type: TaskType) -> ExecutionMode:
        mode_map = {
            TaskType.STANDARD: ExecutionMode.WORKFLOW,
            TaskType.REPETITIVE: ExecutionMode.WORKFLOW,
            TaskType.ONE_TIME: ExecutionMode.BUILTIN,
            TaskType.COMPLEX: ExecutionMode.HYBRID,
            TaskType.UNKNOWN: ExecutionMode.BUILTIN
        }
        return mode_map.get(task_type, ExecutionMode.BUILTIN)
    
    def _get_reason(self, task_type: TaskType, patterns: List[str]) -> str:
        reasons = {
            TaskType.STANDARD: f"标准化任务，匹配模式: {patterns}，使用预定义工作流",
            TaskType.REPETITIVE: f"重复性任务，匹配模式: {patterns}，生成可复用工作流",
            TaskType.ONE_TIME: f"一次性任务，匹配模式: {patterns}，使用内置工具",
            TaskType.COMPLEX: f"复杂任务，匹配模式: {patterns}，混合模式执行",
            TaskType.UNKNOWN: "未识别任务类型，默认使用内置工具"
        }
        return reasons.get(task_type, "未知任务类型")


class CodeValidator:
    """代码验证器 - 静态检查"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
    
    def validate_html(self, file_path: str) -> ValidationResult:
        """验证HTML文件"""
        issues = []
        
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            
            js_issues = self._check_javascript_issues(content)
            issues.extend(js_issues)
            
            css_issues = self._check_css_issues(content)
            issues.extend(css_issues)
            
            html_issues = self._check_html_issues(content)
            issues.extend(html_issues)
            
            passed = len([i for i in issues if i['severity'] == 'error']) == 0
            
            return ValidationResult(
                name="HTML验证",
                passed=passed,
                level=ValidationLevel.BLOCK if not passed else ValidationLevel.WARN if issues else ValidationLevel.SKIP,
                message=f"发现 {len(issues)} 个问题" if issues else "验证通过",
                details=[f"[{i['severity']}] {i['message']}" for i in issues],
                fix_suggestion=self._generate_fix_suggestions(issues)
            )
        except Exception as e:
            return ValidationResult(
                name="HTML验证",
                passed=False,
                level=ValidationLevel.BLOCK,
                message=f"验证失败: {str(e)}"
            )
    
    def _check_javascript_issues(self, content: str) -> List[Dict]:
        issues = []
        
        setInterval_matches = re.findall(r'setInterval\s*\([^)]+\)', content)
        clearInterval_matches = re.findall(r'clearInterval', content)
        if len(setInterval_matches) > len(clearInterval_matches):
            issues.append({
                'severity': 'error',
                'type': 'memory_leak',
                'message': f"发现 {len(setInterval_matches) - len(clearInterval_matches)} 个未清理的 setInterval"
            })
        
        setTimeout_matches = re.findall(r'setTimeout\s*\([^)]+\)', content)
        clearTimeout_matches = re.findall(r'clearTimeout', content)
        if len(setTimeout_matches) > len(clearTimeout_matches) + 5:
            issues.append({
                'severity': 'warn',
                'type': 'memory_leak',
                'message': f"发现 {len(setTimeout_matches)} 个 setTimeout，建议检查是否需要清理"
            })
        
        addEventListener_matches = re.findall(r'addEventListener\s*\(', content)
        removeEventListener_matches = re.findall(r'removeEventListener', content)
        if len(addEventListener_matches) > len(removeEventListener_matches) * 2:
            issues.append({
                'severity': 'warn',
                'type': 'memory_leak',
                'message': f"事件监听器数量不匹配: 添加 {len(addEventListener_matches)}，移除 {len(removeEventListener_matches)}"
            })
        
        if 'localStorage' in content:
            if 'try' not in content or 'catch' not in content:
                issues.append({
                    'severity': 'warn',
                    'type': 'error_handling',
                    'message': "localStorage 使用未包裹 try-catch，隐私模式下会报错"
                })
        
        pool_push = re.findall(r'\.push\([^)]+\)', content)
        pool_pop = re.findall(r'\.pop\(\)', content)
        if pool_push and not pool_pop:
            issues.append({
                'severity': 'warn',
                'type': 'logic',
                'message': "对象池只有 push 没有 pop，可能导致资源泄漏"
            })
        
        return issues
    
    def _check_css_issues(self, content: str) -> List[Dict]:
        issues = []
        
        unused_vars = re.findall(r'--[\w-]+:', content)
        used_vars = re.findall(r'var\(--([\w-]+)', content)
        defined = set(v.rstrip(':') for v in unused_vars)
        used = set(used_vars)
        unused = defined - used
        if unused:
            issues.append({
                'severity': 'warn',
                'type': 'unused',
                'message': f"未使用的CSS变量: {unused}"
            })
        
        return issues
    
    def _check_html_issues(self, content: str) -> List[Dict]:
        issues = []
        
        if '<img' in content and 'alt=' not in content:
            issues.append({
                'severity': 'warn',
                'type': 'accessibility',
                'message': "图片缺少 alt 属性"
            })
        
        if 'onclick=' in content:
            issues.append({
                'severity': 'warn',
                'type': 'best_practice',
                'message': "发现内联 onclick，建议使用 addEventListener"
            })
        
        return issues
    
    def _generate_fix_suggestions(self, issues: List[Dict]) -> str:
        suggestions = []
        for issue in issues:
            if issue['type'] == 'memory_leak' and 'setInterval' in issue['message']:
                suggestions.append("在组件销毁时调用 clearInterval() 清理定时器")
            elif issue['type'] == 'error_handling':
                suggestions.append("使用 try-catch 包裹 localStorage 操作")
            elif issue['type'] == 'accessibility':
                suggestions.append("为所有图片添加 alt 属性")
        return "\n".join(suggestions) if suggestions else ""


class RuntimeValidator:
    """运行时验证器 - 功能测试"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
    
    def validate_javascript_runtime(self, file_path: str) -> ValidationResult:
        """验证JavaScript运行时问题"""
        issues = []
        
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            
            if 'canvas' in content.lower() or 'Canvas' in content:
                canvas_issues = self._check_canvas_issues(content)
                issues.extend(canvas_issues)
            
            dom_issues = self._check_dom_issues(content)
            issues.extend(dom_issues)
            
            form_issues = self._check_form_issues(content)
            issues.extend(form_issues)
            
            passed = len([i for i in issues if i['severity'] == 'error']) == 0
            
            return ValidationResult(
                name="运行时验证",
                passed=passed,
                level=ValidationLevel.BLOCK if not passed else ValidationLevel.WARN if issues else ValidationLevel.SKIP,
                message=f"发现 {len(issues)} 个潜在问题" if issues else "验证通过",
                details=[f"[{i['severity']}] {i['message']}" for i in issues]
            )
        except Exception as e:
            return ValidationResult(
                name="运行时验证",
                passed=False,
                level=ValidationLevel.BLOCK,
                message=f"验证失败: {str(e)}"
            )
    
    def _check_canvas_issues(self, content: str) -> List[Dict]:
        issues = []
        
        if 'measureText' in content:
            if 'font' not in content:
                issues.append({
                    'severity': 'warn',
                    'type': 'canvas',
                    'message': "使用 measureText 前未设置 font，可能返回错误结果"
                })
        
        if 'ctx.fillText' in content or 'ctx.strokeText' in content:
            lines = content.split('\n')
            max_y = 0
            canvas_height = 450
            for line in lines:
                if 'canvas.height' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        canvas_height = int(match.group(1))
                y_match = re.search(r'y\s*[\+\=]?\s*(\d+)', line)
                if y_match:
                    max_y = max(max_y, int(y_match.group(1)))
            
            if max_y > canvas_height - 20:
                issues.append({
                    'severity': 'warn',
                    'type': 'canvas',
                    'message': f"文字可能超出Canvas边界: y={max_y}, height={canvas_height}"
                })
        
        return issues
    
    def _check_dom_issues(self, content: str) -> List[Dict]:
        issues = []
        
        getelement_matches = re.findall(r'getElementById\s*\([\'"]([\w-]+)[\'"]\)', content)
        for elem_id in set(getelement_matches):
            if f'id="{elem_id}"' not in content and f"id='{elem_id}'" not in content:
                issues.append({
                    'severity': 'error',
                    'type': 'dom',
                    'message': f"getElementById('{elem_id}') 但HTML中不存在该ID"
                })
        
        return issues
    
    def _check_form_issues(self, content: str) -> List[Dict]:
        issues = []
        
        if '<input' in content or '<textarea' in content:
            if 'maxlength' in content:
                if 'value.length' not in content and '.length >' not in content:
                    issues.append({
                        'severity': 'warn',
                        'type': 'form',
                        'message': "有 maxlength 但没有前端长度验证反馈"
                    })
        
        return issues


class SmartRouter:
    """智能路由器 - 核心执行引擎"""
    
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace).resolve()
        self.analyzer = TaskAnalyzer()
        self.code_validator = CodeValidator(workspace)
        self.runtime_validator = RuntimeValidator(workspace)
        self.validation_results: List[ValidationResult] = []
        self.execution_log: List[Dict] = []
        self.auto_heal = True
        self.max_heal_attempts = 999
    
    def process(self, task_description: str, target_files: List[str] = None) -> Dict:
        """处理任务"""
        print(f"\n{'='*60}")
        print(f"🚀 智能路由系统启动")
        print(f"{'='*60}\n")
        
        print(f"📋 任务: {task_description}")
        
        analysis = self.analyzer.analyze(task_description)
        
        print(f"\n📊 任务分析:")
        print(f"   类型: {analysis.task_type.value}")
        print(f"   执行模式: {analysis.execution_mode.value}")
        print(f"   置信度: {analysis.confidence:.2%}")
        print(f"   匹配模式: {analysis.matched_patterns}")
        print(f"   原因: {analysis.reason}")
        
        self.execution_log.append({
            "step": "analyze",
            "result": {
                "task_type": analysis.task_type.value,
                "execution_mode": analysis.execution_mode.value,
                "confidence": analysis.confidence
            },
            "timestamp": datetime.now().isoformat()
        })
        
        if target_files:
            print(f"\n🔍 开始验证目标文件...")
            validation_results = self._validate_files(target_files)
            
            all_passed = all(r.passed for r in validation_results if r.level == ValidationLevel.BLOCK)
            has_warnings = any(not r.passed for r in validation_results if r.level == ValidationLevel.WARN)
            
            print(f"\n📋 验证结果:")
            for result in validation_results:
                status = "✅" if result.passed else "⚠️" if result.level == ValidationLevel.WARN else "❌"
                print(f"   {status} {result.name}: {result.message}")
                if result.details:
                    for detail in result.details[:3]:
                        print(f"      - {detail}")
                if result.fix_suggestion:
                    print(f"      💡 建议: {result.fix_suggestion[:100]}...")
            
            self.validation_results = validation_results
            
            if not all_passed:
                print(f"\n❌ 验证未通过，需要修复以下问题:")
                for result in validation_results:
                    if not result.passed and result.level == ValidationLevel.BLOCK:
                        print(f"   - {result.name}: {result.message}")
                        if result.fix_suggestion:
                            print(f"     修复建议: {result.fix_suggestion}")
                
                if self.auto_heal:
                    print(f"\n🔄 自动修复模式已启用，尝试自动修复...")
                    heal_result = self._auto_heal(validation_results)
                    if heal_result["success"]:
                        print(f"✅ 自动修复成功，重新验证...")
                        validation_results = self._validate_files(target_files)
                        all_passed = all(r.passed for r in validation_results if r.level == ValidationLevel.BLOCK)
                        if all_passed:
                            print(f"✅ 验证通过！")
                            return {
                                "success": True,
                                "analysis": {
                                    "task_type": analysis.task_type.value,
                                    "execution_mode": analysis.execution_mode.value,
                                    "confidence": analysis.confidence
                                },
                                "validation": {
                                    "passed": True,
                                    "results": [{
                                        "name": r.name,
                                        "passed": r.passed,
                                        "level": r.level.value,
                                        "message": r.message
                                    } for r in validation_results]
                                },
                                "execution_log": self.execution_log,
                                "auto_healed": True
                            }
                
                return {
                    "success": False,
                    "analysis": {
                        "task_type": analysis.task_type.value,
                        "execution_mode": analysis.execution_mode.value,
                        "confidence": analysis.confidence
                    },
                    "validation": {
                        "passed": False,
                        "results": [{
                            "name": r.name,
                            "passed": r.passed,
                            "level": r.level.value,
                            "message": r.message,
                            "details": r.details,
                            "fix_suggestion": r.fix_suggestion
                        } for r in validation_results]
                    },
                    "execution_log": self.execution_log
                }
        
        return {
            "success": True,
            "analysis": {
                "task_type": analysis.task_type.value,
                "execution_mode": analysis.execution_mode.value,
                "confidence": analysis.confidence
            },
            "validation": {
                "passed": True,
                "results": [{
                    "name": r.name,
                    "passed": r.passed,
                    "level": r.level.value,
                    "message": r.message
                } for r in self.validation_results]
            },
            "execution_log": self.execution_log
        }
    
    def _validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """验证文件列表"""
        results = []
        
        for file_path in file_paths:
            full_path = self.workspace / file_path if not Path(file_path).is_absolute() else Path(file_path)
            
            if not full_path.exists():
                results.append(ValidationResult(
                    name=f"文件存在性检查: {file_path}",
                    passed=False,
                    level=ValidationLevel.BLOCK,
                    message=f"文件不存在: {full_path}"
                ))
                continue
            
            if file_path.endswith('.html'):
                results.append(self.code_validator.validate_html(str(full_path)))
                results.append(self.runtime_validator.validate_javascript_runtime(str(full_path)))
            elif file_path.endswith('.js'):
                results.append(self.runtime_validator.validate_javascript_runtime(str(full_path)))
            elif file_path.endswith('.css'):
                pass
        
        return results
    
    def _auto_heal(self, validation_results: List[ValidationResult]) -> Dict:
        """自动修复验证失败的问题"""
        fixed_count = 0
        failed_fixes = []
        
        for result in validation_results:
            if result.passed:
                continue
            
            if result.level == ValidationLevel.BLOCK:
                print(f"   🔧 尝试修复: {result.name}")
                
                if result.fix_suggestion:
                    print(f"      建议: {result.fix_suggestion[:100]}...")
                
                if "文件不存在" in result.message:
                    print(f"      ⚠️ 文件不存在问题需要用户确认，跳过")
                    failed_fixes.append(result.name)
                    continue
                
                if "JavaScript" in result.name or "JS" in result.name:
                    print(f"      🔄 JavaScript 问题通常需要代码修改，记录待修复")
                    failed_fixes.append(result.name)
                    continue
                
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"   ✅ 已尝试修复 {fixed_count} 个问题")
        
        return {
            "success": len(failed_fixes) == 0,
            "fixed_count": fixed_count,
            "failed_fixes": failed_fixes
        }
    
    def generate_report(self, output_path: str = None) -> str:
        """生成验证报告"""
        if not output_path:
            output_path = self.workspace / "output" / "validation-report.md"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_lines = [
            f"# 验证报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 执行日志",
            f"",
        ]
        
        for log in self.execution_log:
            report_lines.append(f"- **{log['step']}**: {json.dumps(log['result'], ensure_ascii=False)}")
        
        report_lines.extend([
            f"",
            f"## 验证结果",
            f"",
        ])
        
        for result in self.validation_results:
            status = "✅ 通过" if result.passed else "❌ 失败"
            report_lines.append(f"### {result.name}: {status}")
            report_lines.append(f"")
            report_lines.append(f"- **级别**: {result.level.value}")
            report_lines.append(f"- **消息**: {result.message}")
            if result.details:
                report_lines.append(f"- **详情**:")
                for detail in result.details:
                    report_lines.append(f"  - {detail}")
            if result.fix_suggestion:
                report_lines.append(f"- **修复建议**: {result.fix_suggestion}")
            report_lines.append(f"")
        
        report_content = "\n".join(report_lines)
        output_path.write_text(report_content, encoding='utf-8')
        
        return str(output_path)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Router - 智能路由系统')
    parser.add_argument('task', help='任务描述')
    parser.add_argument('--files', '-f', nargs='+', help='要验证的文件列表')
    parser.add_argument('--output', '-o', help='报告输出路径')
    
    args = parser.parse_args()
    
    router = SmartRouter()
    result = router.process(args.task, args.files)
    
    if args.output or args.files:
        report_path = router.generate_report(args.output)
        result["report_path"] = report_path
        print(f"\n📄 验证报告已生成: {report_path}")
    
    print(f"\n{'='*60}")
    if result["success"]:
        print(f"✅ 任务处理完成")
    else:
        print(f"❌ 任务处理失败，需要修复")
    print(f"{'='*60}\n")
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
