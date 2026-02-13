"""
Swarm Orchestrator - 智能体蜂群调度器核心实现

职责：
1. 任务解析 - 理解用户意图，提取核心目标
2. 任务分解 - 将复杂任务拆解为可并行执行的子任务
3. 依赖分析 - 识别任务间的依赖关系，构建 DAG
4. 任务分发 - 将任务分发给合适的 Worker
5. 进度监控 - 实时追踪所有 Worker 执行状态
6. 结果整合 - 收集并整合所有 Worker 输出
"""

import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pathlib import Path


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkerType(Enum):
    RESEARCHER = "researcher"
    CODER = "coder"
    TESTER = "tester"
    WRITER = "writer"
    REVIEWER = "reviewer"


@dataclass
class SubTask:
    task_id: str
    description: str
    worker_type: str
    dependencies: list[str]
    priority: str
    status: str = "pending"
    worker_id: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_file: Optional[str] = None
    error: Optional[str] = None
    input_data: dict = None
    expected_output: dict = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.input_data is None:
            self.input_data = {}
        if self.expected_output is None:
            self.expected_output = {}


@dataclass
class TaskAnalysis:
    core_goal: str
    task_type: str
    complexity: str
    swarm_mode: bool
    reasoning: str


class SwarmOrchestrator:
    SWARM_DIR = ".trae/swarm"
    QUEUE_FILE = "queue.json"
    STATUS_FILE = "status.json"
    RESULTS_DIR = "results"

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.swarm_path = self.project_path / self.SWARM_DIR
        self.queue_path = self.swarm_path / self.QUEUE_FILE
        self.status_path = self.swarm_path / self.STATUS_FILE
        self.results_path = self.swarm_path / self.RESULTS_DIR
        
        self._ensure_directories()

    def _ensure_directories(self):
        self.swarm_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)

    def _generate_task_id(self) -> str:
        return f"task_{uuid.uuid4().hex[:8]}"

    def _generate_main_task_id(self) -> str:
        return f"main_{uuid.uuid4().hex[:8]}"

    def analyze_task(self, user_request: str) -> TaskAnalysis:
        keywords_complex = [
            "系统", "架构", "重构", "开发", "实现",
            "集成", "部署", "测试套件", "文档系统"
        ]
        keywords_simple = [
            "修改", "修复", "优化", "添加", "更新"
        ]
        
        complexity_score = 0
        for kw in keywords_complex:
            if kw in user_request:
                complexity_score += 2
        
        for kw in keywords_simple:
            if kw in user_request:
                complexity_score += 1
        
        if complexity_score >= 4:
            complexity = "complex"
            swarm_mode = True
        elif complexity_score >= 2:
            complexity = "medium"
            swarm_mode = "并行" in user_request or "同时" in user_request
        else:
            complexity = "simple"
            swarm_mode = False

        task_type = "development"
        if "测试" in user_request:
            task_type = "test"
        elif "文档" in user_request:
            task_type = "docs"
        elif "调研" in user_request or "研究" in user_request:
            task_type = "research"
        elif "重构" in user_request:
            task_type = "refactor"

        return TaskAnalysis(
            core_goal=user_request,
            task_type=task_type,
            complexity=complexity,
            swarm_mode=swarm_mode,
            reasoning=f"复杂度评分: {complexity_score}, 任务类型: {task_type}"
        )

    def decompose_task(self, analysis: TaskAnalysis) -> list[SubTask]:
        tasks = []
        
        if analysis.task_type == "development":
            tasks = [
                SubTask(
                    task_id=self._generate_task_id(),
                    description="调研技术方案和最佳实践",
                    worker_type=WorkerType.RESEARCHER.value,
                    dependencies=[],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="设计系统架构和数据模型",
                    worker_type=WorkerType.CODER.value,
                    dependencies=[tasks[0].task_id] if tasks else [],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="实现核心功能代码",
                    worker_type=WorkerType.CODER.value,
                    dependencies=[tasks[1].task_id] if len(tasks) > 1 else [],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="编写单元测试和集成测试",
                    worker_type=WorkerType.TESTER.value,
                    dependencies=[tasks[2].task_id] if len(tasks) > 2 else [],
                    priority=TaskPriority.MEDIUM.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="编写 API 文档和使用说明",
                    worker_type=WorkerType.WRITER.value,
                    dependencies=[tasks[2].task_id] if len(tasks) > 2 else [],
                    priority=TaskPriority.MEDIUM.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="代码审查和质量检查",
                    worker_type=WorkerType.REVIEWER.value,
                    dependencies=[t.task_id for t in tasks[2:4]] if len(tasks) > 3 else [],
                    priority=TaskPriority.MEDIUM.value
                ),
            ]
        
        elif analysis.task_type == "refactor":
            tasks = [
                SubTask(
                    task_id=self._generate_task_id(),
                    description="分析现有代码结构",
                    worker_type=WorkerType.RESEARCHER.value,
                    dependencies=[],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="设计重构方案",
                    worker_type=WorkerType.CODER.value,
                    dependencies=[tasks[0].task_id],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="执行代码重构",
                    worker_type=WorkerType.CODER.value,
                    dependencies=[tasks[1].task_id],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="验证重构结果",
                    worker_type=WorkerType.TESTER.value,
                    dependencies=[tasks[2].task_id],
                    priority=TaskPriority.MEDIUM.value
                ),
            ]
        
        elif analysis.task_type == "test":
            tasks = [
                SubTask(
                    task_id=self._generate_task_id(),
                    description="分析测试需求",
                    worker_type=WorkerType.RESEARCHER.value,
                    dependencies=[],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="编写测试用例",
                    worker_type=WorkerType.TESTER.value,
                    dependencies=[tasks[0].task_id],
                    priority=TaskPriority.HIGH.value
                ),
                SubTask(
                    task_id=self._generate_task_id(),
                    description="执行测试并生成报告",
                    worker_type=WorkerType.TESTER.value,
                    dependencies=[tasks[1].task_id],
                    priority=TaskPriority.MEDIUM.value
                ),
            ]
        
        else:
            tasks = [
                SubTask(
                    task_id=self._generate_task_id(),
                    description=f"执行任务: {analysis.core_goal}",
                    worker_type=WorkerType.CODER.value,
                    dependencies=[],
                    priority=TaskPriority.MEDIUM.value
                ),
            ]
        
        return tasks

    def build_dag(self, tasks: list[SubTask]) -> dict[str, list[str]]:
        dag = {}
        for task in tasks:
            dag[task.task_id] = task.dependencies
        return dag

    def get_execution_order(self, dag: dict[str, list[str]]) -> list[list[str]]:
        in_degree = {node: 0 for node in dag}
        for node, deps in dag.items():
            for dep in deps:
                if dep in in_degree:
                    pass
        
        for node, deps in dag.items():
            in_degree[node] = len([d for d in deps if d in dag])
        
        levels = []
        remaining = set(dag.keys())
        
        while remaining:
            ready = [n for n in remaining if in_degree[n] == 0]
            if not ready:
                break
            
            levels.append(ready)
            remaining -= set(ready)
            
            for node in remaining:
                in_degree[node] = len([d for d in dag[node] if d in remaining])
        
        return levels

    def create_queue(self, main_task_id: str, tasks: list[SubTask], dag: dict[str, list[str]]) -> dict:
        queue_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "main_task_id": main_task_id,
            "tasks": {task.task_id: asdict(task) for task in tasks},
            "dag": dag,
            "execution_order": self.get_execution_order(dag)
        }
        
        with open(self.queue_path, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, ensure_ascii=False, indent=2)
        
        return queue_data

    def read_queue(self) -> dict:
        if not self.queue_path.exists():
            return {}
        
        with open(self.queue_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_task_status(self, task_id: str, status: str, **kwargs):
        queue = self.read_queue()
        if task_id in queue.get("tasks", {}):
            queue["tasks"][task_id]["status"] = status
            queue["tasks"][task_id].update(kwargs)
            
            with open(self.queue_path, 'w', encoding='utf-8') as f:
                json.dump(queue, f, ensure_ascii=False, indent=2)

    def get_ready_tasks(self) -> list[dict]:
        queue = self.read_queue()
        if not queue:
            return []
        
        ready_tasks = []
        completed_tasks = {
            tid for tid, t in queue["tasks"].items() 
            if t["status"] == "completed"
        }
        
        for task_id, task in queue["tasks"].items():
            if task["status"] != "pending":
                continue
            
            deps = task.get("dependencies", [])
            if all(d in completed_tasks for d in deps):
                ready_tasks.append(task)
        
        return ready_tasks

    def get_progress(self) -> dict:
        queue = self.read_queue()
        if not queue:
            return {"total": 0, "completed": 0, "running": 0, "pending": 0, "failed": 0}
        
        tasks = queue.get("tasks", {})
        status_counts = {"total": len(tasks)}
        
        for status in ["completed", "running", "pending", "failed"]:
            status_counts[status] = sum(1 for t in tasks.values() if t.get("status") == status)
        
        status_counts["progress_percent"] = (
            status_counts["completed"] / status_counts["total"] * 100 
            if status_counts["total"] > 0 else 0
        )
        
        return status_counts

    def save_result(self, task_id: str, worker_id: str, output: dict, 
                    execution_time: float, tokens_used: int = 0):
        result = {
            "task_id": task_id,
            "worker_id": worker_id,
            "status": "completed",
            "output": output,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "completed_at": datetime.now().isoformat()
        }
        
        result_file = self.results_path / f"{task_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.update_task_status(
            task_id, 
            "completed",
            worker_id=worker_id,
            result_file=str(result_file),
            completed_at=datetime.now().isoformat()
        )

    def aggregate_results(self) -> dict:
        queue = self.read_queue()
        if not queue:
            return {"status": "no_tasks", "results": {}}
        
        results = {}
        for task_id, task in queue["tasks"].items():
            if task["status"] == "completed" and task.get("result_file"):
                result_path = Path(task["result_file"])
                if result_path.exists():
                    with open(result_path, 'r', encoding='utf-8') as f:
                        results[task_id] = json.load(f)
        
        progress = self.get_progress()
        
        final_status = "success"
        if progress["failed"] > 0:
            final_status = "partial" if progress["completed"] > 0 else "failed"
        
        return {
            "status": final_status,
            "main_task_id": queue.get("main_task_id"),
            "progress": progress,
            "results": results,
            "summary": self._generate_summary(results)
        }

    def _generate_summary(self, results: dict) -> str:
        if not results:
            return "无执行结果"
        
        summary_parts = []
        for task_id, result in results.items():
            output = result.get("output", {})
            summary = output.get("summary", "已完成")
            summary_parts.append(f"- {task_id}: {summary}")
        
        return "\n".join(summary_parts)

    def execute(self, user_request: str) -> dict:
        print(f"🔍 任务分析中...")
        analysis = self.analyze_task(user_request)
        print(f"   核心目标: {analysis.core_goal}")
        print(f"   复杂度: {analysis.complexity}")
        print(f"   蜂群模式: {analysis.swarm_mode}")
        
        if not analysis.swarm_mode:
            print(f"   ⏭️ 简单任务，跳过蜂群模式")
            return {
                "status": "simple_task",
                "analysis": asdict(analysis),
                "message": "任务简单，建议直接执行"
            }
        
        print(f"\n📋 任务分解中...")
        tasks = self.decompose_task(analysis)
        print(f"   分解为 {len(tasks)} 个子任务:")
        for i, task in enumerate(tasks, 1):
            deps = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"   {i}. [{task.worker_type}] {task.description}{deps}")
        
        print(f"\n🔗 构建依赖图...")
        dag = self.build_dag(tasks)
        execution_order = self.get_execution_order(dag)
        print(f"   执行层级: {len(execution_order)} 层")
        for i, level in enumerate(execution_order, 1):
            print(f"   层级 {i}: {len(level)} 个任务可并行")
        
        main_task_id = self._generate_main_task_id()
        print(f"\n📝 创建任务队列...")
        queue = self.create_queue(main_task_id, tasks, dag)
        print(f"   主任务 ID: {main_task_id}")
        print(f"   队列文件: {self.queue_path}")
        
        return {
            "status": "ready",
            "main_task_id": main_task_id,
            "analysis": asdict(analysis),
            "tasks": [asdict(t) for t in tasks],
            "dag": dag,
            "execution_order": execution_order,
            "queue_file": str(self.queue_path),
            "message": "任务已分解，等待 Worker 执行"
        }


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python orchestrator.py <用户请求>")
        print("示例: python orchestrator.py '开发一个用户认证系统'")
        return
    
    user_request = " ".join(sys.argv[1:])
    
    orchestrator = SwarmOrchestrator()
    result = orchestrator.execute(user_request)
    
    print(f"\n{'='*50}")
    print(f"执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
