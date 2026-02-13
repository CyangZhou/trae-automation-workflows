---
name: neuro-bridge
description: 通过本地模型（Neuro-Core）直接控制 Windows 操作系统。当需要执行键鼠模拟、截图分析、OS 级命令行或绕过沙箱限制的操作时调用。支持深度推理、记忆管理、MCP 服务器管理、代码搜索与理解、文件修改与验证、浏览器自动化等能力。
---

# Neuro-Bridge 技能

## 功能概述

Neuro-Bridge 是一个基于 FastMCP 的本地 AI 助手系统，通过本地模型（Neuro-Core）直接控制 Windows 操作系统。

## 核心能力

### 1. 深度推理 (deep_reasoning)
- 复杂分析、架构设计、根因分析
- 支持 P1_RESEARCH、P2_OPTIMIZATION、P3_GENERAL 三种思维协议

### 2. 记忆管理 (manage_memory)
- 存储/检索项目知识
- 基于 BM25 + Mem0 风格的混合召回

### 3. MCP 服务器管理
- 配置、启用与验证 MCP Server
- 工具：Read、RunCommand、SearchCodebase

### 4. 代码搜索与理解
- 定位关键实现并生成结构化理解摘要
- 工具：SearchCodebase、Read、Grep

### 5. 文件修改与验证
- 安全编辑文件并验证改动生效
- 工具：Read、apply_patch、RunCommand、GetDiagnostics

### 6. 浏览器自动化
- 按步骤完成网页操作并获取结果
- 工具：WebFetch、WebSearch、OpenPreview

## 工作流模板

1. **需求到改动** - 把需求变成可执行修改
2. **问题定位与修复** - 快速定位问题根因
3. **批量改名/替换** - 跨文件一致性修改
4. **网页信息提取** - 抽取结构化要点
5. **知识沉淀** - 把结论写入长期记忆

## 使用方法

```python
from neuro_mcp_server import deep_reasoning, manage_memory, self_check

# 深度推理
result = deep_reasoning(
    intent="分析代码架构缺陷",
    context="[代码片段]",
    protocol="P1_RESEARCH"
)

# 记忆管理
manage_memory(
    operation="store",
    content="项目使用 FastMCP 框架",
    tags=["architecture"]
)

# 系统自检
status = self_check()
```

## 环境要求

- Ollama 服务运行在 http://localhost:11434/v1
- 模型名称: neuro-core
- Python 依赖: mcp[cli], requests

## 项目结构

```
src/
├── neuro_mcp_server.py    # FastMCP 服务器
└── neuro_memory.py        # 记忆系统
```

## 更新日志

- v1.0.0 (2026-02-11): 初始版本，包含 5 个能力蓝图和 5 个工作流模板
