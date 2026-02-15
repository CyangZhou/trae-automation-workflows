# 自动化工作流系统 - Unified Engine v8.1

> 一句话完成项目：任务解析 → 智能推荐 → 并行蜂群 → 验证验收 → 知识沉淀

---

## 🎯 项目简介

这是一套基于 Trae IDE 构建的 **生产级自动化开发平台**，采用 Unified Engine v8.1 (Parallel Swarm Edition) 架构。

**核心特性：**
- 🚀 **真正的并行蜂群**：基于 Trae Task 工具实现真正的并发执行
- 🧠 **智能记忆系统**：参考 Anthropic "Claude Plays Pokémon" 设计
- 🔄 **完整闭环**：需求 → 执行 → 验证 → 沉淀，全自动化
- ⚡ **效率提升 3-5x**：复杂任务并行处理，而非顺序轮询

**GitHub 仓库**：[https://github.com/CyangZhou/trae-automation-workflows](https://github.com/CyangZhou/trae-automation-workflows)

---

## 🏗️ 系统架构

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AUTONOMOUS AGENT v8.1 总调度器                          │
│                  (Parallel Swarm Edition)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第1层：任务解析层 [Intelligence]                                      │   │
│  │ • 识别任务类型                                                        │   │
│  │ • 计算复杂度                                                          │   │
│  │ • 生成子任务列表（Swarm 模式）                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第2层：智能推荐层 [Planning]                                          │   │
│  │ • 推荐工作流                                                          │   │
│  │ • 推荐技能                                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                    ┌───────────────┴───────────────┐                       │
│                    ▼                               ▼                       │
│  ┌──────────────────────────┐    ┌──────────────────────────────────┐     │
│  │ Solo 模式                │    │ Swarm 模式 (并行执行)              │     │
│  │ • 顺序执行工作流         │    │ • 创建蜂群会话                    │     │
│  │                          │    │ • 并行调用 Task 工具              │     │
│  │                          │    │ • 聚合结果                        │     │
│  └──────────────────────────┘    └──────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第5层：验证层 [Validation]                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第6层：反思与进化 [Reflexion]                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 第7层：工作流沉淀 [Sedimentation]                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
.trae/
├── skills/              # 技能中心
│   └── autonomous-agent/     # 核心调度器 v8.1
│       ├── core/
│       │   ├── intelligence.py    # 智能分析引擎
│       │   ├── swarm.py           # 蜂群编排器
│       │   ├── memory.py          # 记忆系统
│       │   ├── reflexion.py       # 反思与进化
│       │   └── workflow.py        # 工作流执行器
│       └── agent.py               # 主入口
├── workflows/           # 工作流库（50+个预定义流程）
├── memory/              # 记忆系统（4层存储）
│   ├── sessions/           # 会话级笔记
│   ├── tasks/              # 任务级笔记
│   ├── errors/             # 错误修复笔记
│   └── global/             # 全局知识
├── knowledge/           # 知识沉淀库
├── swarm/               # 蜂群数据库
│   ├── swarm_core.db        # SQLite 数据库
│   └── swarm.log            # 日志
└── rules/               # 项目规则
```

---

## 🚀 快速开始

### 触发词（自动启动）

在 Trae IDE 中输入以下关键词即可触发：

| 触发词 | 功能 |
|--------|------|
| `开始`、`继续`、`自主执行`、`autonomous` | 启动 autonomous-agent 总调度器 |
| `智能工作流`、`帮我看看项目` | 启动 Intelligence 分析模块 |
| `蜂群`、`并行执行`、`swarm` | 强制启动 Swarm 模式 |
| `验证`、`测试`、`质量检查` | 启动验证模块 |

### 示例使用

```
用户：开始，构建一个高并发的数据分析系统

执行流程：
1. 初始化检查
2. 任务解析（复杂度=9 → Swarm模式）
3. 智能推荐（工作流+技能）
4. 并行执行（4个子任务同时跑）
5. 验证验收
6. 反思进化
7. 知识沉淀
✅ 交付
```

---

## 🤖 智能体角色（Worker Roles）

> ⚠️ **重要说明**：这些智能体角色需要用户在 Trae IDE 中手动创建和配置。本系统提供了智能体的角色定义和推荐机制，但具体的智能体实现需要通过 Trae 的 Agent 工具进行创建。

### 如何创建智能体

1. **打开 Trae IDE**
2. **使用 Agent 创建工具**：根据本系统推荐的 `subagent_type` 创建对应的智能体
3. **配置智能体能力**：设置智能体的专业技能、触发词和参数
4. **系统自动识别**：智能体创建完成后，系统会自动识别并使用

### 基础角色 - 开发类

| 角色 | subagent_type | 职责 |
|------|--------------|------|
| **Researcher** | search | Active Research 和验证标准制定 |
| **Coder** | backend-architect | 代码实现 |
| **Frontend** | frontend-implementation-expert | 前端界面实现 |
| **Tester** | testing-validation-expert | 编写和运行验证脚本 |
| **Architect** | architect-design-expert | 架构设计 |
| **DevOps** | release-ops-expert | 部署和发布 |

### 扩展角色 - 量化交易类

| 角色 | subagent_type | 职责 |
|------|--------------|------|
| **Alpha Picker** | alpha-picker | A股选股智能体 |
| **Factor Validator** | factor-validator | 因子验证智能体 |
| **Market Analyzer** | a-share-market-analyzer | 市场分析智能体 |
| **Stock Ranker** | stock-ranker | 股票排序智能体 |

### 扩展角色 - 内容创作类

| 角色 | subagent_type | 职责 |
|------|--------------|------|
| **Novel Architect** | priest-style-architect | 小说架构智能体 |
| **Prompt Crafter** | prompt-crafter | 提示词工匠智能体 |

### 扩展角色 - 技能开发类

| 角色 | subagent_type | 职责 |
|------|--------------|------|
| **Skill Forge** | trae-skill-forge | 技能锻造智能体 |
| **Agent Forge** | agent-forge-master | 智能体锻造大师 |

### 扩展角色 - 专业领域类

| 角色 | subagent_type | 职责 |
|------|--------------|------|
| **TCM Master** | tcm-master-brain | 中医大脑智能体 |
| **Laozi Sage** | laozi-sage | 老子智慧智能体 |
| **Pattern Miner** | symbolic-pattern-miner | 符号模式挖掘智能体 |

---

## 📦 预定义工作流（共 50+ 个）

### 热门工作流

| 工作流 | 描述 |
|--------|------|
| `static-webpage-development.yaml` | 完整网页开发 + GitHub Pages 部署 |
| `android-bookkeeping.yaml` | Android 记账应用开发 |
| `api-documentation.yaml` | API 文档自动生成 |
| `code-review.yaml` | 代码审查 |
| `security-scan-local.yaml` | 安全扫描 |
| `swarm-execution.yaml` | 蜂群模式执行 |
| `test-automation.yaml` | 测试自动化 |
| `release-notes.yaml` | 发布说明生成 |

### 工作流分类

| 分类 | 工作流示例 |
|------|-----------|
| **代码质量** | code-review, code-refactor, code-coverage-report |
| **文档生成** | api-documentation, create-readme, release-notes |
| **CI/CD** | python-ci-local, docker-build-local, security-scan-local |
| **数据处理** | data-processing, log-anomaly-detection |
| **自动化** | email-automation, support-ticket-automation |
| **项目管理** | daily-standup, meeting-minutes, project-stats |

---

## 🧠 记忆系统（Memory）

参考 Anthropic "Claude Plays Pokémon" 方案设计。

### 四层存储结构

| 存储层 | 路径 | 用途 |
|--------|------|------|
| `sessions/` | `.trae/memory/sessions/` | 单次任务会话 |
| `tasks/` | `.trae/memory/tasks/` | 跨会话复用的任务经验 |
| `errors/` | `.trae/memory/errors/` | 错误签名+修复方案 |
| `global/` | `.trae/memory/global/` | 全局模式 |

### 写笔记时机（自动触发）

| 触发点 | 触发条件 |
|--------|---------|
| **TASK_START** | 任务开始时（复杂度 >= 3） |
| **KEY_DECISION** | 做出重要技术决策时 |
| **SUBTASK_COMPLETE** | 子任务完成时 |
| **ERROR_OCCURRED** | 错误发生时 |
| **ERROR_FIXED** | 错误修复后 |
| **TASK_COMPLETE** | 任务完成时 |

### 读笔记时机（智能判断）

| 触发点 | 读取条件 |
|--------|---------|
| **TASK_START** | 继续任务或有相关历史 |
| **ERROR_ENCOUNTERED** | 遇到错误时 |
| **SIMILAR_TASK** | 任务类型匹配时 |
| **PLANNING_PHASE** | 规划阶段 |

---

## 🐝 蜂群模式详解

### 并行执行架构

```
┌─────────────────────────────────────────────────────────────┐
│            真正的并行蜂群 (Task-Based Swarm)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          主 Agent (Orchestrator)                     │   │
│  │  1. 分析任务 → 拆分成 N 个独立子任务                   │   │
│  │  2. 并行调用 Task 工具                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│     ┌───────────────────┼───────────────────┐              │
│     │                   │                   │              │
│     ▼                   ▼                   ▼              │
│  ┌────────┐        ┌────────┐        ┌────────┐           │
│  │ Task 1 │        │ Task 2 │        │ Task 3 │           │
│  │独立上下文│      │独立上下文│      │独立上下文│         │
│  └────────┘        └────────┘        └────────┘           │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          结果聚合 + 集成验证                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 效率对比

| 方案 | 执行方式 | 时间复杂度 | 效率提升 |
|------|---------|-----------|---------|
| **旧方案：轮询** | 顺序执行 | O(n) | 基准 |
| **新方案：Task并行** | 并发执行 | O(1)* | **3-5x** |

*假设有 n 个独立子任务，并行执行时间接近最长子任务的时间

---

## 🔧 核心模块

### 1. Intelligence（智能分析引擎）

**文件**：`.trae/skills/autonomous-agent/core/intelligence.py`

功能：
- 任务类型识别（9种预设类型）
- 复杂度评估（1-10分）
- 智能体推荐
- 任务拆分（Swarm模式）

### 2. Swarm（蜂群编排器）

**文件**：`.trae/skills/autonomous-agent/core/swarm.py`

功能：
- SQLite 会话管理
- 并行子任务调度
- 结果聚合
- 集成 Memory 笔记系统

### 3. Memory（记忆系统）

**文件**：`.trae/skills/autonomous-agent/core/memory.py`

功能：
- 四层存储管理
- 智能读写时机判断
- 错误修复方案检索
- 关键词索引

### 4. Reflexion（反思与进化）

**文件**：`.trae/skills/autonomous-agent/core/reflexion.py`

功能：
- 错误自动修复循环
- 验证失败 → 查找历史方案 → 修复 → 重试

### 5. Workflow Runner（工作流执行器）

**文件**：`.trae/skills/autonomous-agent/core/workflow.py`

功能：
- YAML 工作流解析
- 顺序执行
- 错误处理

---

## 📝 执行协议

### 7个强制检查点

执行过程中必须输出以下检查点：

```
[检查点1] ✅ 初始化完成 - Kernel 启动, 数据库连接正常
[检查点2] ✅ 任务解析完成 - 核心目标: xxx, 复杂度: x, 置信度: x, 推荐智能体: [xxx, xxx]
[检查点3] ✅ 智能推荐完成 - 工作流: xxx, 技能: xxx
[检查点4] ✅ 执行模式选择完成 - 模式: Swarm/Solo
[检查点5] ✅ 验证完成 - Research-Driven Validation 通过
[检查点6] ✅ 反思与进化完成 - 错误数: x, 新增记忆: x
[检查点7] ✅ 工作流沉淀完成 - 经验已归档
```

---

## ⚠️ 重要说明

### 智能体角色创建

本系统提供了智能体的角色定义和推荐机制，但**具体的智能体实现需要用户在 Trae IDE 中手动创建**：

1. 使用 Trae 的 Agent 工具
2. 根据本系统推荐的 `subagent_type` 创建对应的智能体
3. 配置智能体的能力和参数
4. 智能体创建完成后，系统会自动识别并使用

### 数据库

- SQLite 数据库位置：`.trae/swarm/swarm_core.db`
- 日志位置：`.trae/swarm/swarm.log`

---

## 📊 统计信息

- **总文件数**: 100+
- **技能数量**: 6
- **工作流数量**: 50+
- **模板数量**: 18

---

## 📝 更新日志

### v8.1 (2026-02-15)
- 升级为真正的并行蜂群模式
- 新增智能体自动推荐机制
- 完善记忆系统读写时机
- 添加智能体创建说明文档

### v6.1 (2026-02-13)
- 新增步骤6知识沉淀验证机制
- 优化冲突解决流程
- 完善文档结构

### v6.0
- 重构自主执行调度器
- 新增蜂群模式
- 集成智能推荐

---

## 📄 许可证

MIT License

---

## 🤝 联系方式

- **GitHub**: [https://github.com/CyangZhou/trae-automation-workflows](https://github.com/CyangZhou/trae-automation-workflows)
- **作者**: LO & Little Code Sauce

---

**版本**：v8.1 (Parallel Swarm Edition)  
**更新日期**：2026-02-15