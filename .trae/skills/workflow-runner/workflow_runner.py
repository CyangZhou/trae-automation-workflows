#!/usr/bin/env python3
"""
Workflow Runner v2.0 - 工作流执行器
支持全局工作流和项目工作流两种模式
🆕 支持蜂群模式并行执行
"""

import json
import subprocess
import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from enum import Enum

GLOBAL_WORKFLOW_DIR = Path("C:/Users/Administrator/.trae-cn/workflows")
PROJECT_WORKFLOW_DIR = Path(".trae/workflows")
SWARM_DIR = Path(".trae/swarm")


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SwarmTask:
    task_id: str
    description: str
    worker_type: str
    dependencies: List[str]
    status: str = "pending"
    result: Optional[dict] = None


class SwarmOrchestrator:
    """蜂群调度器 - 管理并行任务执行"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.swarm_path = self.project_path / SWARM_DIR
        self.queue_path = self.swarm_path / "queue.json"
        self.results_path = self.swarm_path / "results"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        self.swarm_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
    
    def analyze_complexity(self, task_description: str) -> dict:
        """分析任务复杂度"""
        complex_keywords = ["系统", "架构", "重构", "开发", "实现", "构建", "设计"]
        simple_keywords = ["修改", "修复", "优化", "添加", "更新"]
        
        complexity_score = sum(2 for kw in complex_keywords if kw in task_description)
        complexity_score += sum(1 for kw in simple_keywords if kw in task_description)
        
        if complexity_score >= 4:
            return {"complexity": "complex", "swarm_mode": True}
        elif complexity_score >= 2:
            return {"complexity": "medium", "swarm_mode": False}
        else:
            return {"complexity": "simple", "swarm_mode": False}
    
    def decompose_task(self, task_description: str) -> List[SwarmTask]:
        """将复杂任务分解为子任务"""
        tasks = [
            SwarmTask(
                task_id="task_001",
                description="调研技术方案",
                worker_type="researcher",
                dependencies=[]
            ),
            SwarmTask(
                task_id="task_002",
                description="设计系统架构",
                worker_type="coder",
                dependencies=["task_001"]
            ),
            SwarmTask(
                task_id="task_003",
                description="实现核心功能",
                worker_type="coder",
                dependencies=["task_002"]
            ),
            SwarmTask(
                task_id="task_004",
                description="编写测试用例",
                worker_type="tester",
                dependencies=["task_003"]
            ),
            SwarmTask(
                task_id="task_005",
                description="编写文档",
                worker_type="writer",
                dependencies=["task_003"]
            ),
            SwarmTask(
                task_id="task_006",
                description="代码审查",
                worker_type="reviewer",
                dependencies=["task_003", "task_004", "task_005"]
            )
        ]
        return tasks
    
    def build_execution_order(self, tasks: List[SwarmTask]) -> List[List[SwarmTask]]:
        """构建执行层级（DAG调度）"""
        task_map = {t.task_id: t for t in tasks}
        completed = set()
        levels = []
        remaining = set(t.task_id for t in tasks)
        
        while remaining:
            ready = []
            for tid in remaining:
                task = task_map[tid]
                if all(d in completed for d in task.dependencies):
                    ready.append(task)
            
            if not ready:
                break
            
            levels.append(ready)
            for t in ready:
                completed.add(t.task_id)
                remaining.discard(t.task_id)
        
        return levels
    
    def execute_parallel(self, tasks: List[SwarmTask], max_workers: int = 3) -> dict:
        """并行执行任务"""
        levels = self.build_execution_order(tasks)
        all_results = {}
        
        for level_idx, level_tasks in enumerate(levels):
            print(f"\n=== 执行层级 {level_idx + 1}/{len(levels)} ===")
            print(f"并行任务数: {len(level_tasks)}")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for task in level_tasks:
                    future = executor.submit(self._execute_single_task, task)
                    futures[future] = task
                
                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        result = future.result()
                        all_results[task.task_id] = result
                        task.status = "completed"
                        print(f"✅ {task.task_id}: {task.description}")
                    except Exception as e:
                        task.status = "failed"
                        all_results[task.task_id] = {"error": str(e)}
                        print(f"❌ {task.task_id}: {str(e)}")
        
        return {
            "status": "completed",
            "total_tasks": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
            "results": all_results
        }
    
    def _execute_single_task(self, task: SwarmTask) -> dict:
        """执行单个任务"""
        task.status = "running"
        time.sleep(0.5)  # 模拟执行
        return {
            "task_id": task.task_id,
            "worker": task.worker_type,
            "status": "completed",
            "output": f"完成: {task.description}"
        }


def get_workflow_dirs() -> list[Path]:
    """获取所有工作流目录（项目级优先）"""
    dirs = []
    
    project_dir = Path.cwd() / PROJECT_WORKFLOW_DIR
    if project_dir.exists():
        dirs.append(project_dir)
    
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


def run_swarm_workflow(task_description: str, max_workers: int = 3) -> dict:
    """🆕 运行蜂群工作流"""
    print(f"\n🐝 启动蜂群模式...")
    print(f"任务描述: {task_description}")
    
    orchestrator = SwarmOrchestrator()
    
    print(f"\n📊 分析任务复杂度...")
    analysis = orchestrator.analyze_complexity(task_description)
    print(f"复杂度: {analysis['complexity']}")
    print(f"蜂群模式: {analysis['swarm_mode']}")
    
    if not analysis['swarm_mode']:
        print(f"\n⏭️ 任务简单，跳过蜂群模式")
        return {"status": "simple", "message": "任务简单，建议单Agent执行"}
    
    print(f"\n📋 分解任务...")
    tasks = orchestrator.decompose_task(task_description)
    print(f"分解为 {len(tasks)} 个子任务:")
    for i, task in enumerate(tasks, 1):
        deps = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"  {i}. [{task.worker_type}] {task.description}{deps}")
    
    print(f"\n🚀 开始并行执行...")
    result = orchestrator.execute_parallel(tasks, max_workers)
    
    print(f"\n📊 执行完成!")
    print(f"总任务: {result['total_tasks']}")
    print(f"完成: {result['completed']}")
    print(f"失败: {result['failed']}")
    
    return result


def find_workflow_by_trigger(text: str) -> str | None:
    """根据用户输入查找匹配的工作流"""
    triggers = {
        "git-commit-summary": ["提交摘要", "git summary", "周报", "commit", "提交记录"],
        "project-stats": ["统计项目", "project stats", "代码统计", "统计", "代码量"],
        "swarm-execution": ["蜂群", "并行执行", "swarm", "/swarm", "启动蜂群"]
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
    
    parser = argparse.ArgumentParser(description="Workflow Runner v2.0")
    parser.add_argument("action", choices=["list", "run", "detect", "swarm"])
    parser.add_argument("--workflow", help="工作流名称")
    parser.add_argument("--text", help="用户输入文本（用于检测）")
    parser.add_argument("--task", help="任务描述（用于蜂群模式）")
    parser.add_argument("--workers", type=int, default=3, help="最大并行Worker数")
    
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
    elif args.action == "swarm":
        if not args.task:
            print(json.dumps({"error": "请提供任务描述"}, ensure_ascii=False))
        else:
            result = run_swarm_workflow(args.task, args.workers)
            print(json.dumps(result, ensure_ascii=False, indent=2))
