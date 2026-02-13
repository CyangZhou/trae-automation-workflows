# 🚀 自动化工作流系统

> 一句话完成项目 - 从需求到交付的全自动化解决方案

## 📖 简介

这是一个基于 Trae IDE 的自动化工作流系统，通过智能调度、蜂群执行、知识沉淀实现"一句话完成项目"的目标。

## ✨ 核心特性

- **🎯 自主执行**: 输入一句话，自动完成从规划到交付的全流程
- **🐝 蜂群模式**: 复杂任务自动分解，多Worker并行执行
- **🧠 智能推荐**: 自动分析项目，推荐最优工作流
- **📚 知识沉淀**: 执行经验自动保存，持续优化
- **🔄 工作流市场**: 45+ 预定义工作流，一键安装使用

## 🏗️ 系统架构

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                 autonomous-agent (总调度器)                  │
│                                                             │
│  [步骤1] 初始化检查 ──── 执行 Python 命令                     │
│  [步骤2] 任务解析 ─────── 计算复杂度分数                      │
│  [步骤3] 智能推荐 ───────► intelligent-workflow-assistant    │
│  [步骤4] 执行模式选择:                                       │
│         swarm ──────────► swarm-orchestrator                │
│         single_agent ───► workflow-runner                   │
│  [步骤5] 验证验收                                           │
│  [步骤6] 知识沉淀                                           │
└─────────────────────────────────────────────────────────────┘
```

## 📦 组件列表

### 核心技能

| 技能 | 触发词 | 说明 |
|------|--------|------|
| autonomous-agent | 开始、继续、autonomous | 总调度器 |
| intelligent-workflow-assistant | 智能工作流、推荐工作流 | 智能推荐 |
| swarm-orchestrator | 蜂群、swarm、并行执行 | 蜂群调度 |

### 工作流分类

- **代码质量**: code-review, code-refactor, code-coverage-report
- **文档生成**: api-documentation, create-readme, release-notes
- **CI/CD**: python-ci-local, docker-build-local, security-scan-local
- **数据处理**: data-processing, log-anomaly-detection
- **自动化**: email-automation, support-ticket-automation
- **项目管理**: daily-standup, meeting-minutes, project-stats

## 🚀 快速开始

### 1. 安装

将 `.trae` 目录复制到你的项目根目录：

```bash
cp -r 自动化工作流/.trae /your/project/
```

### 2. 使用

在 Trae IDE 中输入触发词：

```
开始，开发一个用户认证系统
```

系统将自动：
1. 解析任务复杂度
2. 推荐最优工作流
3. 执行开发任务
4. 验证交付质量
5. 沉淀执行经验

### 3. 自定义工作流

在 `.trae/workflows/` 目录创建 YAML 文件：

```yaml
name: my-custom-workflow
description: 自定义工作流描述
trigger: 自定义触发词
steps:
  - name: 步骤1
    action: 执行动作
  - name: 步骤2
    action: 执行动作
```

## 📁 目录结构

```
.trae/
├── knowledge/          # 知识库
├── rules/              # 规则配置
├── skills/             # 技能模块
├── swarm/              # 蜂群运行时
├── templates/          # 工作流模板
├── workflows/          # 工作流定义
└── skill-registry.json # 技能注册表
```

详细结构请查看 [STRUCTURE.md](./STRUCTURE.md)

## 🔧 配置说明

### 复杂度评分规则

| 关键词类型 | 分数 | 示例 |
|-----------|------|------|
| 复杂关键词 | 3分 | 系统、架构、重构、开发、实现、构建、设计 |
| 中等关键词 | 2分 | 优化、集成、扩展、模块 |
| 简单关键词 | 1分 | 修复、修改、添加、更新、删除 |

- **分数 >= 6**: 蜂群模式 (swarm)
- **分数 < 6**: 单Agent模式 (single_agent)

### Worker 类型

| Worker | 职责 | 超时 |
|--------|------|------|
| Researcher | 调研、搜索、知识提取 | 180s |
| Coder | 代码编写、重构、修复 | 600s |
| Tester | 测试、验证、检查 | 300s |
| Writer | 文档、README、API文档 | 180s |
| Reviewer | 代码审查、安全检查 | 180s |

## 📊 统计信息

- **总文件数**: 102
- **技能数量**: 10
- **工作流数量**: 45+
- **模板数量**: 18

## 📝 更新日志

### v6.1 (2026-02-13)
- 新增步骤6知识沉淀验证机制
- 优化冲突解决流程
- 完善文档结构

### v6.0
- 重构自主执行调度器
- 新增蜂群模式
- 集成智能推荐

## 📄 许可证

MIT License

---

**Made with ❤️ by LO & Little Code Sauce**
