# 工作流模板规范

本文档定义了 Trae 工作流的标准模板，供大模型生成新工作流时参考。

## 基础结构

```yaml
name: 工作流名称
description: 简短描述
trigger:
  type: manual | auto | schedule
  keywords: [关键词列表]
  
steps:
  - id: 1
    name: 步骤名称
    action: run_command | verify | notify
    params:
      command: "具体命令"
    on_failure: continue | stop | retry
    
  - id: 2
    name: 验证步骤
    action: verify
    type: file_exists | command_success | diagnostics
    params:
      path: "文件路径"
      
output:
  files: [输出文件列表]
  format: json | markdown | txt
```

## 步骤类型

### 1. run_command - 执行命令

```yaml
- id: 1
  name: 安装依赖
  action: run_command
  params:
    command: "pip install -r requirements.txt"
    timeout: 120
  on_failure: stop
```

### 2. verify - 验证结果

```yaml
- id: 2
  name: 验证文件生成
  action: verify
  type: file_exists
  params:
    path: "output/result.json"
  fail_message: "输出文件未生成"
```

### 3. notify - 通知用户

```yaml
- id: 3
  name: 报告结果
  action: notify
  params:
    message: "✅ 任务完成"
```

### 4. search_web - 联网搜索

```yaml
- id: 1
  name: 搜索相关项目
  action: search_web
  params:
    query: "Python 数据处理最佳实践"
    max_results: 5
```

### 5. generate_workflow - 生成工作流

```yaml
- id: 2
  name: 生成工作流文件
  action: generate_workflow
  params:
    name: "新工作流名称"
    description: "描述"
    steps: [步骤列表]
```

## 验证类型

| 类型 | 说明 | 参数 |
|------|------|------|
| `file_exists` | 检查文件是否存在 | `path` |
| `command_success` | 检查命令执行成功 | `command` |
| `diagnostics` | 检查代码诊断无错误 | 无 |
| `content_assert` | 检查文件内容 | `path`, `contains` |
| `test_pass` | 检查测试通过 | `command` |

## 完整示例

### 示例1：代码安全扫描

```yaml
name: 安全扫描
description: 扫描代码安全漏洞
trigger:
  type: manual
  keywords: [安全, 扫描, security, bandit]

steps:
  - id: 1
    name: 安装安全工具
    action: run_command
    params:
      command: "pip install bandit safety -q"
    on_failure: stop
    
  - id: 2
    name: 创建输出目录
    action: run_command
    params:
      command: "python -c \"import os; os.makedirs('output', exist_ok=True)\""
      
  - id: 3
    name: 运行Bandit扫描
    action: run_command
    params:
      command: "bandit -r . -f json -o output/bandit-report.json -x ./venv,./.git"
      
  - id: 4
    name: 验证报告生成
    action: verify
    type: file_exists
    params:
      path: "output/bandit-report.json"
      
output:
  files: ["output/bandit-report.json"]
  format: json
```

### 示例2：自动生成工作流

```yaml
name: 智能工作流生成
description: 根据任务描述自动生成工作流
trigger:
  type: manual
  keywords: [生成工作流, 创建工作流, generate workflow]

steps:
  - id: 1
    name: 搜索相关项目
    action: search_web
    params:
      query: "{task_description} 最佳实践"
      max_results: 5
      
  - id: 2
    name: 分析搜索结果
    action: analyze_results
    params:
      extract_steps: true
      
  - id: 3
    name: 生成工作流文件
    action: generate_workflow
    params:
      name: "{workflow_name}"
      description: "{task_description}"
      save_path: ".trae/workflows/{workflow_name}.yaml"
      
  - id: 4
    name: 验证工作流文件
    action: verify
    type: file_exists
    params:
      path: ".trae/workflows/{workflow_name}.yaml"
      
output:
  files: [".trae/workflows/{workflow_name}.yaml"]
  format: yaml
```

## 命名规范

- 文件名：小写字母 + 连字符，如 `security-scan.yaml`
- 工作流名称：中文，简洁明了，如 "安全扫描"
- 步骤名称：动词开头，如 "安装依赖"、"运行扫描"

## 注意事项

1. 每个工作流必须有至少一个验证步骤
2. 命令执行应设置合理的超时时间
3. 失败处理应明确（stop/continue/retry）
4. 输出文件应放在 `output/` 目录
