# Knowledge Base Index

此目录存储 Autonomous Agent 执行任务时产生的知识调研报告。

## 目录结构

```
knowledge/
├── README.md                    # 本文件
├── index.json                   # 知识索引（自动维护）
├── {技术名}/                    # 按技术分类
│   ├── {任务名}-research.md     # 调研报告
│   └── {任务名}-summary.md      # 知识摘要
└── _templates/                  # 模板文件
    └── research-template.md     # 调研报告模板
```

## 知识索引格式 (index.json)

```json
{
  "version": "1.0",
  "entries": [
    {
      "id": "react18-collab-editor",
      "title": "React 18 实时协作编辑器",
      "technologies": ["React 18", "Yjs", "WebSocket"],
      "created_at": "2026-02-12",
      "updated_at": "2026-02-12",
      "research_file": "react/react18-collab-editor-research.md",
      "summary_file": "react/react18-collab-editor-summary.md",
      "keywords": ["并发渲染", "CRDT", "实时协作"]
    }
  ]
}
```

## 使用方式

1. **存储知识**：Autonomous Agent 完成知识调研后自动保存
2. **复用知识**：执行新任务时先检查是否有相关知识点
3. **更新知识**：当技术版本更新时，更新对应知识条目

## 知识时效性

- 每条知识记录创建时间
- 超过 12 个月的知识标记为"可能过时"
- 执行任务时自动检查知识时效性
