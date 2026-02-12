# 工作流模板规范

本文档定义了 Trae 工作流的标准模板，供大模型生成新工作流时参考。

## 基础结构

```yaml
name: 工作流名称
description: 简短描述
version: "1.0.0"
triggers:
  - "触发词1"
  - "触发词2"

steps:
  - id: 1
    name: 步骤名称
    action: run_command | verify | notify | generate_document
    params:
      command: "具体命令"
    on_failure: continue | stop | retry

output:
  files: ["输出文件列表"]
  format: json | markdown | txt
```

## 步骤类型

| 动作类型 | 说明 | 必要参数 |
|---------|------|---------|
| `run_command` | 执行 Shell 命令 | `command` |
| `verify` | 验证结果 | `type`, `path` |
| `notify` | 通知用户 | `message` |
| `generate_document` | 生成文档 | `output`, `content` |

## 验证类型

| 类型 | 说明 | 参数 |
|------|------|------|
| `file_exists` | 检查文件是否存在 | `path` |
| `command_success` | 检查命令执行成功 | `command` |

## 完整示例

```yaml
name: Git提交摘要
description: 自动获取最近git提交记录并生成摘要文档
version: "2.0.0"
triggers:
  - "生成提交摘要"
  - "git summary"
  - "周报"

steps:
  - id: 1
    name: 创建输出目录
    action: run_command
    params:
      command: "mkdir -p output"
      timeout: 5

  - id: 2
    name: 获取Git提交记录
    action: run_command
    params:
      command: "git log --since='1 week ago' --pretty=format:'%h - %s' -20"
      save_as: git_commits
      timeout: 10

  - id: 3
    name: 生成摘要文档
    action: generate_document
    params:
      output: "output/git-summary-{{current_date}}.md"
      content: |
        # Git提交摘要
        **生成时间**: {{current_date}}
        
        ## 最近提交
        {{git_commits}}

  - id: 4
    name: 完成通知
    action: notify
    params:
      message: "✅ Git摘要已生成"
```

## 命名规范

- 文件名：小写字母 + 连字符，如 `git-commit-summary.yaml`
- 工作流名称：中文，简洁明了，如 "Git提交摘要"
- 步骤名称：动词开头，如 "创建目录"、"获取记录"

## 注意事项

1. 每个工作流必须有至少一个验证步骤
2. 命令执行应设置合理的超时时间
3. 失败处理应明确（stop/continue/retry）
4. 输出文件应放在 `output/` 目录