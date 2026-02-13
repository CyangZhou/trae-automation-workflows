# Swarm Worker 模板

---

## Researcher Worker（调研员）

**职责**：知识调研、信息收集、文档阅读

**能力**：
- 联网搜索
- 文档阅读
- 知识提取
- 摘要生成

**输入格式**：
```json
{
  "task_id": "task_xxx",
  "description": "调研认证方案",
  "input_data": {
    "topic": "调研主题",
    "keywords": ["关键词1", "关键词2"],
    "depth": "shallow|medium|deep"
  }
}
```

**输出格式**：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "output": {
    "summary": "调研结果摘要",
    "findings": [
      {"title": "发现1", "content": "..."},
      {"title": "发现2", "content": "..."}
    ],
    "recommendations": ["建议1", "建议2"],
    "sources": ["url1", "url2"]
  }
}
```

---

## Coder Worker（程序员）

**职责**：代码编写、重构、Bug 修复

**能力**：
- 代码编写
- 代码重构
- Bug 修复
- 性能优化

**输入格式**：
```json
{
  "task_id": "task_xxx",
  "description": "实现认证 API",
  "input_data": {
    "requirements": "功能需求描述",
    "tech_stack": ["Python", "FastAPI"],
    "constraints": ["约束条件"],
    "reference_files": ["file1.py", "file2.py"]
  }
}
```

**输出格式**：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "output": {
    "summary": "实现摘要",
    "files_created": ["new_file.py"],
    "files_modified": ["existing_file.py"],
    "key_changes": [
      {"file": "xxx.py", "change": "新增认证函数"}
    ],
    "notes": "注意事项"
  }
}
```

---

## Tester Worker（测试员）

**职责**：测试验证、质量检查

**能力**：
- 单元测试
- 集成测试
- 边界测试
- 性能测试

**输入格式**：
```json
{
  "task_id": "task_xxx",
  "description": "编写单元测试",
  "input_data": {
    "target_files": ["auth.py"],
    "test_type": "unit|integration|e2e",
    "coverage_target": 80
  }
}
```

**输出格式**：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "output": {
    "summary": "测试摘要",
    "tests_created": ["test_auth.py"],
    "test_results": {
      "passed": 10,
      "failed": 0,
      "coverage": 85
    },
    "issues_found": []
  }
}
```

---

## Writer Worker（文档员）

**职责**：文档编写、注释添加

**能力**：
- API 文档
- 用户手册
- 技术博客
- README

**输入格式**：
```json
{
  "task_id": "task_xxx",
  "description": "编写 API 文档",
  "input_data": {
    "doc_type": "api|readme|guide",
    "target_files": ["api.py"],
    "format": "markdown|html"
  }
}
```

**输出格式**：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "output": {
    "summary": "文档摘要",
    "files_created": ["docs/api.md"],
    "files_modified": ["README.md"],
    "sections": ["安装", "使用", "API 参考"]
  }
}
```

---

## Reviewer Worker（审查员）

**职责**：代码审查、安全检查

**能力**：
- 代码质量检查
- 安全漏洞扫描
- 最佳实践建议
- 重构建议

**输入格式**：
```json
{
  "task_id": "task_xxx",
  "description": "代码审查",
  "input_data": {
    "target_files": ["auth.py", "user.py"],
    "check_types": ["quality", "security", "performance"]
  }
}
```

**输出格式**：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "output": {
    "summary": "审查摘要",
    "issues": [
      {
        "file": "auth.py",
        "line": 42,
        "severity": "high|medium|low",
        "type": "security",
        "message": "潜在 SQL 注入风险",
        "suggestion": "使用参数化查询"
      }
    ],
    "score": 85,
    "recommendations": ["建议1", "建议2"]
  }
}
```

---

## Worker 通用协议

### 1. 启动流程

```
1. 读取队列文件 (.trae/swarm/queue.json)
2. 查找 status=pending 且依赖已完成的任务
3. 更新任务状态为 running
4. 执行任务
5. 保存结果到 results/{task_id}.json
6. 更新任务状态为 completed
```

### 2. 错误处理

```
任务执行失败
    ↓
1. 记录错误信息
2. 更新状态为 failed
3. 如果可重试 → 状态改为 retrying
4. 通知 Orchestrator
```

### 3. 心跳机制

```json
{
  "worker_id": "researcher_001",
  "worker_type": "researcher",
  "current_task": "task_xxx",
  "status": "running",
  "last_heartbeat": "2026-02-13T10:00:00Z",
  "progress": 60
}
```

### 4. 上下文隔离

每个 Worker 维护独立的上下文文件：

```
.trae/swarm/workers/
├── researcher_001/
│   └── context.json
├── coder_001/
│   └── context.json
└── tester_001/
    └── context.json
```
