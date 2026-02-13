---
name: workflow-market
description: 支持搜索、分类、推荐和一键安装工作流到本地。当用户需要查找工作流、探索新工作流、管理工作流收藏时使用。
---

# Workflow Market - 工作流市场

## 功能概述

统一的工作流索引和发现平台，聚合多个来源的工作流资源。

## 数据来源

### 1. GitHub 开源项目
- Awesome 系列仓库
- 官方 Actions 工作流
- 社区贡献模板

### 2. 技能市场
- OpenPackage (OpenWork)
- Trae 技能市场
- MCP Server 集合

### 3. 技术文章
- CSDN/博客园教程
- GitHub Discussions
- 官方文档示例

## 核心功能

### 搜索 (search)
```python
from workflow_market import search_workflows

results = search_workflows(
    query="CI/CD",
    source="github",
    category="devops"
)
```

### 浏览 (browse)
```python
from workflow_market import list_workflows

workflows = list_workflows(
    category="documentation",
    sort_by="stars"
)
```

### 安装 (install)
```python
from workflow_market import install_workflow

install_workflow(
    workflow_id="github-actions-python-ci",
    target_dir=".trae/workflows/"
)
```

### 同步 (sync)
```python
from workflow_market import sync_market

# 更新索引
sync_market()
```

## 工作流分类

| 分类 | 说明 | 示例 |
|-----|------|------|
| ci-cd | 持续集成/部署 | 自动测试、构建、发布 |
| documentation | 文档生成 | README、API文档、博客 |
| project-mgmt | 项目管理 | 站会、看板、报告 |
| code-quality | 代码质量 | 审查、格式化、安全扫描 |
| automation | 通用自动化 | 备份、同步、通知 |
| ai-ml | AI/ML工作流 | 训练、推理、数据处理 |

## 使用方法

### 命令行
```bash
# 搜索工作流
python workflow_market.py search "python ci"

# 按分类浏览
python workflow_market.py browse --category ci-cd

# 查看详情
python workflow_market.py info <workflow-id>

# 安装到本地
python workflow_market.py install <workflow-id>

# 同步市场数据
python workflow_market.py sync

# 显示统计
python workflow_market.py stats
```

### Python API
```python
from workflow_market import WorkflowMarket

market = WorkflowMarket()

# 搜索
results = market.search("docker")

# 获取推荐
recommended = market.get_recommended()

# 安装
market.install("github-actions-docker-build")
```

## 索引结构

```json
{
  "workflows": [
    {
      "id": "unique-id",
      "name": "工作流名称",
      "description": "描述",
      "source": "github|openpackage|article",
      "category": "ci-cd",
      "url": "原始链接",
      "stars": 100,
      "tags": ["python", "docker"],
      "content": "YAML内容",
      "installed_count": 50
    }
  ]
}
```
