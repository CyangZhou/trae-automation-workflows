#!/usr/bin/env python3
"""
Workflow Runner - 工作流执行器
支持全局工作流和项目工作流两种模式
"""

import json
import subprocess
import sys
from pathlib import Path

# 全局工作流目录（所有项目通用）
GLOBAL_WORKFLOW_DIR = Path.home() / ".trae-cn" / "workflows"

# 项目工作流目录（相对路径，基于当前工作目录）
PROJECT_WORKFLOW_DIR = Path(".trae/workflows")


def get_workflow_dirs() -> list[Path]:
    """获取所有工作流目录（项目级优先）"""
    dirs = []
    
    # 项目级工作流（如果存在）
    project_dir = Path.cwd() / PROJECT_WORKFLOW_DIR
    if project_dir.exists():
        dirs.append(project_dir)
    
    # 全局工作流
    if GLOBAL_WORKFLOW_DIR.exists():
        dirs.append(GLOBAL_WORKFLOW_DIR)
    
    return dirs


def find_workflow_manager() -> Path | None:
    """查找可用的 workflow_manager.py"""
    for dir_path in get_workflow_dirs():
        manager = dir_path / "workflow_manager.py"
        if manager.exists():
            return manager
    return None


def list_workflows() -> list:
    """列出所有可用工作流（合并全局和项目）"""
    all_workflows = []
    seen_names = set()
    
    for dir_path in get_workflow_dirs():
        try:
            result = subprocess.run(
                [sys.executable, str(dir_path / "workflow_manager.py"), "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                workflows = json.loads(result.stdout)
                for wf in workflows:
                    if isinstance(wf, dict) and "name" in wf:
                        if wf["name"] not in seen_names:
                            seen_names.add(wf["name"])
                            wf["source"] = "project" if dir_path == Path.cwd() / PROJECT_WORKFLOW_DIR else "global"
                            all_workflows.append(wf)
                    elif isinstance(wf, dict) and "error" not in wf:
                        all_workflows.append(wf)
        except Exception as e:
            all_workflows.append({"error": f"{dir_path}: {str(e)}"})
    
    return all_workflows


def find_workflow_location(workflow_name: str) -> Path | None:
    """查找工作流所在的目录（项目级优先）"""
    for dir_path in get_workflow_dirs():
        workflow_file = dir_path / f"{workflow_name}.yaml"
        if workflow_file.exists():
            return dir_path
    return None


def run_workflow(workflow_name: str, context: dict = None) -> dict:
    """执行指定工作流"""
    workflow_dir = find_workflow_location(workflow_name)
    
    if not workflow_dir:
        return {"status": "error", "message": f"工作流 '{workflow_name}' 未找到"}
    
    try:
        cmd = [sys.executable, str(workflow_dir / "workflow_manager.py"), "run", workflow_name]
        
        if context:
            for key, value in context.items():
                cmd.extend(["--var", f"{key}={value}"])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def find_workflow_by_trigger(text: str) -> str | None:
    """根据用户输入查找匹配的工作流"""
    triggers = {
        "git-commit-summary": ["提交摘要", "git summary", "周报", "commit", "提交记录"],
        "project-stats": ["统计项目", "project stats", "代码统计", "统计", "代码量"]
    }
    
    text_lower = text.lower()
    for workflow, keywords in triggers.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                if find_workflow_location(workflow):
                    return workflow
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow Runner")
    parser.add_argument("action", choices=["list", "run", "detect"])
    parser.add_argument("--workflow", help="工作流名称")
    parser.add_argument("--text", help="用户输入文本（用于检测）")
    
    args = parser.parse_args()
    
    if args.action == "list":
        workflows = list_workflows()
        print(json.dumps(workflows, ensure_ascii=False, indent=2))
    elif args.action == "run":
        if not args.workflow:
            print(json.dumps({"error": "请指定工作流名称"}, ensure_ascii=False))
        else:
            result = run_workflow(args.workflow)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == "detect":
        if not args.text:
            print(json.dumps({"error": "请提供文本"}, ensure_ascii=False))
        else:
            workflow = find_workflow_by_trigger(args.text)
            print(json.dumps({
                "detected": workflow is not None,
                "workflow": workflow,
                "text": args.text
            }, ensure_ascii=False))