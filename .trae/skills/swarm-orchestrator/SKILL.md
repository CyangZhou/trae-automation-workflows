---
name: swarm-orchestrator
description: 智能体蜂群调度器 v6.0 - 任务分解、DAG构建、Worker分发、并行执行。触发词：蜂群、并行执行、多智能体、swarm、/swarm、启动蜂群
---

# Swarm Orchestrator - 智能体蜂群调度器 v6.0

## 🎯 核心定位

**蜂群总指挥官**：接收复杂任务、分解为子任务、分发给专业 Worker、监控执行进度、整合最终结果。

---

## 🚨 执行协议（CRITICAL - 必须执行）

**当此 Skill 被调用后，Agent 必须按照以下步骤执行：**

### 步骤 1：创建任务队列

```python
python -c "
import json
import uuid
from pathlib import Path
from datetime import datetime

# 确保目录存在
swarm_dir = Path('.trae/swarm')
swarm_dir.mkdir(parents=True, exist_ok=True)
(swarm_dir / 'results').mkdir(exist_ok=True)

# 创建队列文件
queue = {
    'version': '1.0',
    'created_at': datetime.now().isoformat(),
    'main_task_id': f'main_{uuid.uuid4().hex[:8]}',
    'tasks': {},
    'dag': {},
    'execution_order': []
}

queue_file = swarm_dir / 'queue.json'
queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2))

print(f'[OK] 队列文件已创建: {queue_file}')
print(f'[OK] 主任务ID: {queue[\"main_task_id\"]}')
"
```

### 步骤 2：任务分解

根据任务类型分解为子任务：

| 任务类型 | 子任务分解 |
|---------|-----------|
| development | Researcher调研 → Coder设计 → Coder实现 → Tester测试 → Writer文档 → Reviewer审查 |
| refactor | Researcher分析 → Coder设计 → Coder重构 → Tester验证 |
| test | Researcher分析 → Tester编写 → Tester执行 |
| docs | Researcher收集 → Writer编写 → Reviewer审查 |
| web | Researcher调研 → Coder实现 → Tester验证 |

### 步骤 3：构建 DAG

```python
# DAG 格式
dag = {
    "task_001": [],                    # 无依赖
    "task_002": ["task_001"],          # 依赖 task_001
    "task_003": ["task_001"],          # 依赖 task_001 (可与 task_002 并行)
    "task_004": ["task_002", "task_003"]  # 依赖多个任务
}
```

### 步骤 4：更新队列文件

```python
python -c "
import json
from pathlib import Path

queue_file = Path('.trae/swarm/queue.json')
queue = json.loads(queue_file.read_text())

# 添加子任务
tasks = [
    {'task_id': 'task_001', 'description': '调研技术方案', 'worker_type': 'researcher', 'dependencies': [], 'status': 'pending'},
    {'task_id': 'task_002', 'description': '设计架构', 'worker_type': 'coder', 'dependencies': ['task_001'], 'status': 'pending'},
    {'task_id': 'task_003', 'description': '实现核心功能', 'worker_type': 'coder', 'dependencies': ['task_002'], 'status': 'pending'},
    {'task_id': 'task_004', 'description': '编写测试', 'worker_type': 'tester', 'dependencies': ['task_003'], 'status': 'pending'},
    {'task_id': 'task_005', 'description': '编写文档', 'worker_type': 'writer', 'dependencies': ['task_003'], 'status': 'pending'},
]

for task in tasks:
    queue['tasks'][task['task_id']] = task
    queue['dag'][task['task_id']] = task['dependencies']

# 计算执行顺序（按层级）
queue['execution_order'] = [['task_001'], ['task_002'], ['task_003'], ['task_004', 'task_005']]

queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2))
print('[OK] 任务队列已更新')
print(f'[INFO] 共 {len(tasks)} 个子任务')
"
```

### 步骤 5：返回执行计划

**必须返回以下格式**：

```json
{
  "status": "ready",
  "main_task_id": "main_xxxxxxxx",
  "queue_file": ".trae/swarm/queue.json",
  "tasks": [
    {"task_id": "task_001", "description": "...", "worker_type": "researcher", "dependencies": []},
    ...
  ],
  "execution_order": [
    ["task_001"],
    ["task_002"],
    ["task_003"],
    ["task_004", "task_005"]
  ],
  "message": "任务已分解，等待执行"
}
```

---

## 📐 系统架构

```
用户复杂任务
      ↓
┌─────────────────────────────────────┐
│       Swarm Orchestrator            │
│  ┌─────────────────────────────┐    │
│  │ [步骤1] 创建任务队列         │    │
│  │ [步骤2] 任务分解             │    │
│  │ [步骤3] 构建DAG              │    │
│  │ [步骤4] 更新队列文件         │    │
│  │ [步骤5] 返回执行计划         │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
      ↓
  执行计划 (JSON)
```

---

## 👷 Worker 类型

| Worker | 职责 | 超时 | 适用任务 |
|--------|------|------|---------|
| Researcher | 调研、搜索、知识提取 | 180s | 所有复杂任务 |
| Coder | 代码编写、重构、修复 | 600s | development, refactor |
| Tester | 测试、验证、检查 | 300s | development, test |
| Writer | 文档、README、API文档 | 180s | development, docs |
| Reviewer | 代码审查、安全检查 | 180s | development, refactor |

---

## 📋 执行示例

### 示例：重构马年网页

```
autonomous-agent 调用:
  task = "重构马年网页"
  mode = "swarm"

执行流程:

[步骤1] 创建任务队列
> [OK] 队列文件已创建: .trae/swarm/queue.json
> [OK] 主任务ID: main_a1b2c3d4

[步骤2] 任务分解
> 任务类型: web
> 分解为 4 个子任务

[步骤3] 构建 DAG
> 层级1: task_001 (researcher) - 调研马年创意设计
> 层级2: task_002 (coder) - 实现马年网页
> 层级3: task_003 (tester) - 验证页面效果
> 层级3: task_004 (writer) - 编写说明文档 (并行)

[步骤4] 更新队列文件
> [OK] 任务队列已更新
> [INFO] 共 4 个子任务

[步骤5] 返回执行计划
{
  "status": "ready",
  "main_task_id": "main_a1b2c3d4",
  "queue_file": ".trae/swarm/queue.json",
  "tasks": [...],
  "execution_order": [["task_001"], ["task_002"], ["task_003", "task_004"]],
  "message": "任务已分解，等待执行"
}
```

---

## 📁 文件结构

```
.trae/swarm/
├── queue.json          # 任务队列
├── status.json         # 执行状态（可选）
└── results/            # 结果存储
    ├── task_001.json
    ├── task_002.json
    └── ...
```

---

## 🔒 强制规则

1. **必须创建队列文件**：每次调用必须创建 `.trae/swarm/queue.json`
2. **必须返回执行计划**：返回 JSON 格式的执行计划
3. **DAG 必须正确**：依赖关系不能有环
4. **Worker 类型必须匹配**：根据任务类型分配合适的 Worker
