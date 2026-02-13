# 自动化工作流系统 - 目录结构说明

## 📁 项目结构

```
自动化工作流/
└── .trae/
    ├── knowledge/              # 知识库
    │   ├── index.json          # 知识索引
    │   ├── README.md           # 知识库说明
    │   ├── _templates/         # 知识模板
    │   │   ├── knowledge-template.md
    │   │   └── research-template.md
    │   ├── agent-swarm/        # 智能体蜂群相关
    │   │   ├── agent-swarm-research.md
    │   │   └── swarm-architecture-design.md
    │   ├── github-pages-deploy/ # GitHub Pages部署
    │   │   └── github-pages-deploy-guide.md
    │   ├── trae-solo/          # Trae Solo架构
    │   │   └── trae-solo-research.md
    │   └── web-development/    # Web开发相关
    │       └── horse-year-webpage-fix.md
    │
    ├── rules/                  # 规则配置
    │   └── project_rules.md    # 项目核心规则
    │
    ├── skills/                 # 技能模块
    │   ├── autonomous-agent/   # 自主执行调度器
    │   │   ├── SKILL.md
    │   │   └── skill.yaml
    │   ├── intelligent-workflow-assistant/  # 智能工作流助手
    │   │   ├── SKILL.md
    │   │   ├── intelligent_assistant.py
    │   │   └── skill.yaml
    │   ├── swarm-orchestrator/ # 蜂群调度器
    │   │   ├── SKILL.md
    │   │   ├── orchestrator.py
    │   │   ├── skill.yaml
    │   │   └── worker-templates.md
    │   ├── workflow-runner/    # 工作流执行器
    │   │   ├── SKILL.md
    │   │   └── workflow_runner.py
    │   ├── workflow-market/    # 工作流市场
    │   │   ├── SKILL.md
    │   │   ├── sources.json
    │   │   ├── workflow-index.json
    │   │   └── workflow_market.py
    │   ├── skill-market-hub/   # 技能市场
    │   │   ├── SKILL.md
    │   │   └── skill_market_hub.py
    │   ├── skill-manager/      # 技能管理器
    │   │   └── skill_manager.py
    │   ├── neuro-bridge/       # Neuro桥接
    │   │   └── SKILL.md
    │   └── static-webpage-dev/ # 静态网页开发
    │       └── SKILL.md
    │
    ├── swarm/                  # 蜂群运行时
    │   └── queue.json          # 任务队列
    │
    ├── templates/              # 工作流模板
    │   ├── api-documentation.md
    │   ├── code-refactor.md
    │   ├── content-publishing-plan.md
    │   ├── daily-standup.md
    │   ├── data-processing.md
    │   ├── email-summary.md
    │   ├── invoice-record.md
    │   ├── log-analysis.md
    │   ├── meeting-minutes.md
    │   ├── pr-review.md
    │   ├── release-notes.md
    │   ├── resume-screening.md
    │   ├── sales-email.md
    │   ├── slack-classification.md
    │   ├── support-response.md
    │   ├── test-report.md
    │   ├── workflow-template.md
    │   └── youtube-research.md
    │
    ├── workflows/              # 工作流定义
    │   ├── autonomous_agent.py
    │   ├── intelligent_monitor.py
    │   ├── smart_router.py
    │   ├── workflow_manager.py
    │   ├── workflow_manager_v2.py
    │   ├── api-documentation.yaml
    │   ├── auto-labeler.yaml
    │   ├── backup-project.yaml
    │   ├── changelog-generator.yaml
    │   ├── code-coverage-report.yaml
    │   ├── code-refactor.yaml
    │   ├── code-review.yaml
    │   ├── content-publisher.yaml
    │   ├── create-readme.yaml
    │   ├── daily-standup.yaml
    │   ├── data-processing.yaml
    │   ├── dependency-auto-update.yaml
    │   ├── dependency-check.yaml
    │   ├── doc-sync-check.yaml
    │   ├── docker-build-local.yaml
    │   ├── email-automation.yaml
    │   ├── git-commit-summary.yaml
    │   ├── hello-world.yaml
    │   ├── html.yaml
    │   ├── intelligent-trigger.yaml
    │   ├── invoice-processing.yaml
    │   ├── issue-stale-manager.yaml
    │   ├── license-compliance.yaml
    │   ├── log-anomaly-detection.yaml
    │   ├── meeting-minutes-auto.yaml
    │   ├── meeting-minutes.yaml
    │   ├── performance-benchmark.yaml
    │   ├── pr-review-assistant.yaml
    │   ├── pr-size-labeler.yaml
    │   ├── project-stats.yaml
    │   ├── python-ci-local.yaml
    │   ├── release-notes.yaml
    │   ├── resume-screening.yaml
    │   ├── sales-lead-nurturing.yaml
    │   ├── security-scan-local.yaml
    │   ├── slack-message-classifier.yaml
    │   ├── smart-release.yaml
    │   ├── smart-router.yaml
    │   ├── static-webpage-development.yaml
    │   ├── support-ticket-automation.yaml
    │   ├── swarm-execution.yaml
    │   ├── test-automation.yaml
    │   ├── true-automation-demo.yaml
    │   └── youtube-research.yaml
    │
    └── skill-registry.json     # 技能注册表
```

## 📊 统计信息

- **总文件数**: 102
- **总目录数**: 26
- **技能数量**: 10
- **工作流数量**: 45+
- **模板数量**: 18

## 🔧 核心组件说明

### 1. Skills（技能模块）

| 技能名称 | 功能描述 |
|---------|---------|
| autonomous-agent | 自主执行总调度器，一句话完成项目 |
| intelligent-workflow-assistant | 智能工作流推荐助手 |
| swarm-orchestrator | 蜂群调度器，并行任务执行 |
| workflow-runner | 工作流执行器 |
| workflow-market | 工作流市场，搜索安装工作流 |
| skill-market-hub | 技能市场，搜索安装技能 |
| skill-manager | 技能管理器 |
| neuro-bridge | Neuro桥接，本地模型控制 |
| static-webpage-dev | 静态网页开发工作流 |

### 2. Workflows（工作流）

工作流是预定义的自动化任务模板，支持：
- 代码审查、重构
- 文档生成
- 测试自动化
- CI/CD流程
- 数据处理
- 邮件自动化
- 等等...

### 3. Knowledge（知识库）

存储执行经验和调研报告，支持：
- 按技术领域分类
- 知识索引管理
- 模板化存储

### 4. Templates（模板）

提供各类工作流输出模板，确保格式一致性。

---

*最后更新: 2026-02-13*
