---
name: workflow-runner
description: 执行 Trae 工作流模板系统。当用户需要运行预定义工作流、自动化重复任务、生成周报/会议纪要/项目统计时调用。支持 git-commit-summary、project-stats 等工作流。
---

# Workflow Runner - 工作流执行器

## 功能

自动检测并执行 `.trae/workflows/` 目录下的工作流模板。

## 可用工作流

### 1. git-commit-summary
**触发词**: "生成提交摘要", "git summary", "周报"
**功能**: 获取最近Git提交记录并生成摘要文档

### 2. project-stats
**触发词**: "统计项目", "project stats", "代码统计"
**功能**: 统计项目代码量、文件数等信息

## 使用方法

当用户提到工作流相关需求时，自动调用：

```python
from workflow_runner import run_workflow

# 执行工作流
result = run_workflow("git-commit-summary")
```

## 工作流列表

运行以下命令查看所有工作流：
```bash
python .trae/workflows/workflow_manager.py list
```

## 执行工作流

```bash
python .trae/workflows/workflow_manager.py run <workflow-name>
```