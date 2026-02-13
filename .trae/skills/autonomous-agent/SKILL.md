---
name: autonomous-agent
description: 自主执行总调度器 v6.1。一句话完成项目：任务解析 → 智能推荐 → 蜂群/单Agent执行 → 验证验收 → 知识沉淀。触发词：开始、继续、自主执行、自动规划、autonomous。深度集成 intelligent-workflow-assistant、swarm-orchestrator、workflow-runner。
---

# Autonomous Agent - 自主执行总调度器 v6.1

## 🎯 核心目标

**一句话完成项目**：从用户输入到交付可用成果，全程自动化，零中断。

---

## 🚨🚨🚨 超级强制规则（CRITICAL）

### ⛔ 绝对禁止

1. **禁止跳过任何步骤** - 每个步骤都必须执行
2. **禁止直接写代码** - 在完成步骤1-4之前，禁止开始编码
3. **禁止忽略返回结果** - 必须解析并使用 intelligent-workflow-assistant 的返回
4. **禁止省略检查点** - 必须输出所有6个检查点

### ✅ 强制检查点输出

执行过程中必须输出以下检查点：

```
[检查点1] ✅ 初始化完成
[检查点2] ✅ 任务解析完成 - 核心目标: xxx, 复杂度: x, 模式: xxx
[检查点3] ✅ 智能推荐完成 - 工作流: xxx
[检查点4] ✅ 执行模式选择完成 - 已调用: xxx
[检查点5] ✅ 验证完成
[检查点6] ✅ 知识沉淀完成
```

---

## 🚨 执行协议（CRITICAL - 必须执行）

**当此 Skill 被触发后，Agent 必须按照以下步骤执行：**

### 步骤 1：初始化检查

```
必须执行的命令:
python -c "
import os
from pathlib import Path

dirs = [
    '.trae/knowledge',
    '.trae/knowledge/_templates',
    '.trae/swarm',
    '.trae/swarm/results',
    '.trae/swarm/workers'
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)
    print(f'[OK] {d}')

index_file = Path('.trae/knowledge/index.json')
if not index_file.exists():
    import json
    index_file.write_text(json.dumps({'version': '1.0', 'entries': []}, ensure_ascii=False, indent=2))
    print('[OK] index.json created')

print('[INIT] 初始化完成')
"
```

### 步骤 2：任务解析

分析用户输入，提取：
- `core_goal`: 核心目标
- `tech_domains`: 技术领域
- `complexity`: 复杂度（simple/medium/complex）
- `execution_mode`: 执行模式（single_agent/swarm）

**复杂度评分规则**：
- 复杂关键词（系统、架构、重构、开发、实现、构建、设计）：3分
- 中等关键词（优化、集成、扩展、模块）：2分
- 简单关键词（修复、修改、添加、更新、删除）：1分
- **分数 >= 6 → swarm 模式**
- **分数 < 6 → single_agent 模式**

### 步骤 3：智能推荐（调用 intelligent-workflow-assistant）

**必须执行**：
```
调用 Skill: intelligent-workflow-assistant
```

等待返回后，解析结果中的：
- `execution_mode`: 执行模式
- `recommended_workflows`: 推荐工作流列表
- `project_context`: 项目上下文

### 步骤 4：执行模式选择

**如果是 swarm 模式**：
```
调用 Skill: swarm-orchestrator
```

**如果是 single_agent 模式**：
```
调用 Skill: workflow-runner
```

### 步骤 5：验证验收

执行完成后必须验证：
- 语法检查（如有代码变更）
- 功能测试（如有功能实现）
- 目标达成验证

### 步骤 6：知识沉淀（CRITICAL - 必须执行）

**⛔ 禁止跳过此步骤**

执行完成后，必须将经验保存到知识库：

```python
必须执行的命令:
python -c "
import os
import json
from pathlib import Path
from datetime import datetime

# 1. 确定知识分类
task_category = '{task_category}'  # 根据任务类型确定
task_id = datetime.now().strftime('%Y%m%d%H%M%S')

# 2. 创建知识目录
knowledge_dir = Path(f'.trae/knowledge/{task_category}')
knowledge_dir.mkdir(parents=True, exist_ok=True)

# 3. 生成知识文件
knowledge_file = knowledge_dir / f'{task_id}-summary.md'

# 4. 写入知识内容（必须包含以下字段）
knowledge_content = '''# {任务标题}

## 执行日期
{日期}

## 任务概述
{任务描述}

## 执行步骤
{详细步骤}

## 关键发现/踩坑经验
{发现的问题和解决方案}

## 执行结果
{结果状态和交付物}

## 标签
{相关标签}
'''

knowledge_file.write_text(knowledge_content, encoding='utf-8')
print(f'[KNOWLEDGE] 已保存: {knowledge_file}')

# 5. 更新索引
index_file = Path('.trae/knowledge/index.json')
if index_file.exists():
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
else:
    index_data = {'version': '1.0', 'entries': []}

index_data['entries'].append({
    'id': f'{task_category}-{task_id}',
    'title': '{任务标题}',
    'category': task_category,
    'file': f'{task_category}/{task_id}-summary.md',
    'created_at': datetime.now().strftime('%Y-%m-%d'),
    'tags': {标签列表},
    'summary': '{简短摘要}'
})

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print('[KNOWLEDGE] 索引已更新')
print('[CHECKPOINT-6] ✅ 知识沉淀完成')
"
```

**必须输出**：
```
[检查点6] ✅ 知识沉淀完成
  - 保存路径: .trae/knowledge/{category}/
  - 知识文件: {task_id}-summary.md
  - 索引状态: 已更新
```

---

## 📐 系统架构

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AUTONOMOUS AGENT v6.0 总调度器                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第0层：初始化检查层 [自动执行]                                        │   │
│  │ • 检查 .trae/knowledge/ 目录                                         │   │
│  │ • 检查 .trae/swarm/ 目录                                             │   │
│  │ • 初始化知识索引                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第1层：任务解析层 [自动执行]                                          │   │
│  │ • 提取核心目标                                                        │   │
│  │ • 识别技术领域                                                        │   │
│  │ • 判断复杂度（简单/中等/复杂）                                         │   │
│  │ • 决定执行模式                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第2层：智能推荐层 [调用 Skill: intelligent-workflow-assistant]        │   │
│  │ • 分析项目上下文                                                      │   │
│  │ • 匹配本地工作流                                                      │   │
│  │ • 推荐最优执行方案                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                    ┌───────────────┴───────────────┐                       │
│                    ▼                               ▼                       │
│  ┌──────────────────────────┐    ┌──────────────────────────────────┐     │
│  │ 单Agent模式              │    │ 蜂群模式                          │     │
│  │ [调用 Skill:             │    │ [调用 Skill: swarm-orchestrator]  │     │
│  │  workflow-runner]        │    │ • 任务分解                        │     │
│  │ • 直接执行工作流         │    │ • DAG 构建                        │     │
│  │                          │    │ • Worker 分发                     │     │
│  └──────────────────────────┘    └──────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第5层：验证层 [强制执行]                                              │   │
│  │ • 语法检查 (block)                                                    │   │
│  │ • 功能测试 (block)                                                    │   │
│  │ • 目标达成验证                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第6层：知识沉淀层 [自动执行]                                          │   │
│  │ • 保存执行经验                                                        │   │
│  │ • 记录踩坑经验                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 组件调用链

```
autonomous-agent 触发
    │
    ├── [步骤1] 执行初始化命令
    │
    ├── [步骤2] 分析任务复杂度
    │
    ├── [步骤3] 调用 Skill: intelligent-workflow-assistant
    │         │
    │         └── 返回：execution_mode, recommended_workflows
    │
    ├── [步骤4] 根据模式选择执行路径
    │         │
    │         ├── swarm 模式 → 调用 Skill: swarm-orchestrator
    │         │
    │         └── single_agent 模式 → 调用 Skill: workflow-runner
    │
    ├── [步骤5] 验证结果
    │
    └── [步骤6] 保存知识
```

---

## 📋 执行示例

### 示例：重构马年网页

```
用户: 开始，重构马年网页

Agent 执行流程:

[步骤1] 初始化检查
> 执行 Python 初始化命令
> [OK] .trae/knowledge
> [OK] .trae/swarm
> [INIT] 初始化完成

[步骤2] 任务解析
> 核心目标: 重构马年网页
> 技术领域: 前端开发
> 复杂度评分: 6 (重构3分 + 设计3分)
> 执行模式: swarm

[步骤3] 智能推荐
> 调用 Skill: intelligent-workflow-assistant
> 返回: execution_mode=swarm, workflows=[static-webpage-development]

[步骤4] 蜂群执行
> 调用 Skill: swarm-orchestrator
> 任务分解: [Researcher调研, Coder实现, Tester验证, Writer文档]

[步骤5] 验证
> 语法检查: ✓
> 功能测试: ✓
> 目标达成: ✓

[步骤6] 知识沉淀
> 保存到 .trae/knowledge/web-development/
```

---

## ⚙️ 配置

```yaml
autonomous_agent:
  version: "6.0"
  
  execution:
    default_mode: "auto"
    max_retries: 3
    timeout: 600
    auto_heal: true
    
  swarm:
    enabled: true
    max_workers: 5
    complexity_threshold: 6
    
  validation:
    syntax_check: "block"
    functional_test: "block"
    auto_fix: true
```

---

## 🔒 强制规则

1. **初始化必须执行**：每次触发必须先执行初始化命令
2. **智能推荐必须调用**：必须调用 intelligent-workflow-assistant
3. **验证必须执行**：所有代码变更必须通过验证
4. **知识必须沉淀**：执行完成后必须保存经验，并验证文件已创建
5. **失败必须修复**：验证失败时必须自动修复
6. **检查点必须完整**：必须输出全部6个检查点，缺一不可

---

## 🚨 步骤6验证清单

在输出 `[检查点6] ✅ 知识沉淀完成` 之前，必须确认：

- [ ] 知识文件已创建于 `.trae/knowledge/{category}/`
- [ ] 知识内容包含：执行日期、任务概述、执行步骤、关键发现、执行结果、标签
- [ ] `index.json` 已更新，包含新条目
- [ ] 文件路径可访问

**如果以上任一项未完成，则检查点6未通过，必须补充执行。**
