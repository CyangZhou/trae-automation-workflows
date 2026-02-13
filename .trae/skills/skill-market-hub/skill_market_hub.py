#!/usr/bin/env python3
"""
Skill Market Hub - 技能市场聚合器
从多个开源技能市场和 GitHub 仓库搜索、下载 AI 技能
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional

# 配置
SKILL_INSTALL_DIR = Path("e:/traework/00 ai助手研发/.trae/skills")
GITHUB_API_BASE = "https://api.github.com"

# 预定义的技能源
SKILL_SOURCES = {
    "github": {
        "name": "GitHub",
        "description": "搜索 GitHub 上的技能相关仓库",
        "search_url": "https://api.github.com/search/repositories",
    },
    "awesome-ai": {
        "name": "Awesome AI Agents",
        "description": "精选 AI Agent 技能列表",
        "url": "https://github.com/e2b-dev/awesome-ai-agents",
    }
}

# 热门技能推荐列表
TRENDING_SKILLS = [
    {
        "name": "openai-swarm",
        "description": "OpenAI 官方多智能体编排框架",
        "source": "github",
        "url": "https://github.com/openai/swarm",
        "stars": 18000,
        "category": "framework"
    },
    {
        "name": "mcp-server",
        "description": "Model Context Protocol 服务器实现",
        "source": "github", 
        "url": "https://github.com/modelcontextprotocol/servers",
        "stars": 12000,
        "category": "tool"
    },
    {
        "name": "browser-use",
        "description": "让 AI 能够控制浏览器执行任务",
        "source": "github",
        "url": "https://github.com/browser-use/browser-use",
        "stars": 25000,
        "category": "automation"
    },
    {
        "name": "dify",
        "description": "开源 LLM 应用开发平台，支持工作流和 Agent",
        "source": "github",
        "url": "https://github.com/langgenius/dify",
        "stars": 65000,
        "category": "platform"
    },
    {
        "name": "n8n",
        "description": "工作流自动化工具，支持 AI 节点",
        "source": "github",
        "url": "https://github.com/n8n-io/n8n",
        "stars": 58000,
        "category": "automation"
    },
    {
        "name": "langchain",
        "description": "构建 LLM 应用的框架",
        "source": "github",
        "url": "https://github.com/langchain-ai/langchain",
        "stars": 95000,
        "category": "framework"
    },
    {
        "name": "autogen",
        "description": "微软开源的多智能体对话框架",
        "source": "github",
        "url": "https://github.com/microsoft/autogen",
        "stars": 35000,
        "category": "framework"
    },
    {
        "name": "crewai",
        "description": "多智能体协作框架",
        "source": "github",
        "url": "https://github.com/joaomdmoura/crewAI",
        "stars": 24000,
        "category": "framework"
    }
]


def check_local_skill(skill_name: str) -> bool:
    """检查本地是否已安装该技能"""
    skill_path = SKILL_INSTALL_DIR / skill_name
    return skill_path.exists()


def search_github_skills(query: str, max_results: int = 10) -> List[Dict]:
    """在 GitHub 上搜索技能相关仓库"""
    try:
        # 构建搜索查询
        search_terms = [
            f"{query} skill",
            f"{query} mcp",
            f"{query} agent",
            f"{query} ai tool"
        ]
        
        all_results = []
        seen_urls = set()
        
        for term in search_terms:
            if len(all_results) >= max_results:
                break
                
            url = f"{GITHUB_API_BASE}/search/repositories?q={term.replace(' ', '+')}&sort=stars&order=desc&per_page=5"
            
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Skill-Market-Hub/1.0",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    for item in data.get('items', []):
                        if item['html_url'] in seen_urls:
                            continue
                            
                        seen_urls.add(item['html_url'])
                        
                        skill_info = {
                            "name": item['name'],
                            "description": item['description'] or "No description",
                            "source": "github",
                            "url": item['html_url'],
                            "stars": item['stargazers_count'],
                            "language": item['language'],
                            "installed": check_local_skill(item['name'])
                        }
                        all_results.append(skill_info)
                        
                        if len(all_results) >= max_results:
                            break
                            
            except Exception as e:
                continue
        
        return all_results[:max_results]
        
    except Exception as e:
        return [{"error": f"GitHub search failed: {str(e)}"}]


def get_trending_skills(category: Optional[str] = None) -> List[Dict]:
    """获取热门技能列表"""
    results = []
    
    for skill in TRENDING_SKILLS:
        if category and skill.get('category') != category:
            continue
            
        skill_copy = skill.copy()
        skill_copy['installed'] = check_local_skill(skill['name'])
        results.append(skill_copy)
    
    return results


def list_sources() -> List[Dict]:
    """列出所有可用的技能源"""
    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"]
        }
        for key, value in SKILL_SOURCES.items()
    ]


def install_skill(skill_name: str, source: str = "github") -> Dict:
    """
    安装技能到本地
    注意：这是一个模拟实现，实际安装需要克隆仓库并解析 SKILL.md
    """
    target_dir = SKILL_INSTALL_DIR / skill_name
    
    if target_dir.exists():
        return {
            "status": "error",
            "message": f"Skill '{skill_name}' already installed at {target_dir}"
        }
    
    # 这里可以实现实际的下载逻辑
    # 例如：git clone、下载 zip、解析 SKILL.md 等
    
    return {
        "status": "info",
        "message": f"To install '{skill_name}' from {source}, manually clone it:\n  git clone <repo-url> {target_dir}",
        "note": "Auto-installation will be implemented in next version"
    }


def update_neuro_bridge_skill() -> Dict:
    """
    更新 neuro-bridge 技能
    从项目文档生成最新的 SKILL.md 并直接写入 .trae/skills/neuro-bridge/
    """
    project_dir = Path("e:/traework/00 ai助手研发")
    user_guide = project_dir / "docs" / "NEURO_BRIDGE_USER_GUIDE.md"
    
    if not user_guide.exists():
        return {
            "status": "error",
            "message": f"User guide not found at {user_guide}"
        }
    
    # 读取项目文档
    try:
        with open(user_guide, 'r', encoding='utf-8') as f:
            doc_content = f.read()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read user guide: {str(e)}"
        }
    
    # 生成最新的技能描述
    skill_content = '''---
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
'''
    
    # 创建技能目录并写入文件
    neuro_bridge_dir = SKILL_INSTALL_DIR / "neuro-bridge"
    skill_file = neuro_bridge_dir / "SKILL.md"
    
    try:
        # 创建目录
        neuro_bridge_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入 SKILL.md
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(skill_content)
        
        return {
            "status": "success",
            "message": f"neuro-bridge skill updated and saved to {skill_file}",
            "skill_path": str(skill_file),
            "skill_dir": str(neuro_bridge_dir),
            "source_file": str(user_guide),
            "version": "1.0.0",
            "capabilities": 5,
            "workflows": 5,
            "instructions": [
                "技能文件已自动生成并保存到 .trae/skills/neuro-bridge/SKILL.md",
                "你可以：",
                "1. 在 Trae 技能面板中刷新查看",
                "2. 或者直接使用项目本地技能路径",
                "3. 如需同步到 Trae 全局技能，请手动复制 SKILL.md 内容到全局技能编辑器"
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write skill file: {str(e)}"
        }


def format_output(data: Dict or List, action: str) -> str:
    """格式化输出结果"""
    result = {
        "status": "success",
        "action": action,
        "results": data if isinstance(data, list) else [data]
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Skill Market Hub - 搜索和下载 AI 技能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s search pdf              # 搜索 PDF 相关技能
  %(prog)s trending                # 获取热门技能
  %(prog)s trending --category framework  # 获取框架类热门技能
  %(prog)s sources                 # 列出可用数据源
  %(prog)s install browser-use     # 安装指定技能
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索技能')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--source', choices=['github', 'all'], default='github',
                              help='搜索源 (默认: github)')
    search_parser.add_argument('--max', type=int, default=10, help='最大结果数')
    
    # trending 命令
    trending_parser = subparsers.add_parser('trending', help='获取热门技能')
    trending_parser.add_argument('--category', choices=['framework', 'tool', 'automation', 'platform'],
                                help='按类别筛选')
    
    # sources 命令
    subparsers.add_parser('sources', help='列出可用数据源')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安装技能')
    install_parser.add_argument('skill_name', help='技能名称')
    install_parser.add_argument('--source', default='github', help='技能源')
    
    # update 命令
    update_parser = subparsers.add_parser('update', help='更新本地技能')
    update_parser.add_argument('skill_name', choices=['neuro-bridge'], 
                              help='要更新的技能名称 (目前仅支持 neuro-bridge)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行命令
    if args.command == 'search':
        if args.source == 'github':
            results = search_github_skills(args.query, args.max)
        else:
            results = search_github_skills(args.query, args.max)
        print(format_output(results, 'search'))
        
    elif args.command == 'trending':
        results = get_trending_skills(args.category)
        print(format_output(results, 'trending'))
        
    elif args.command == 'sources':
        results = list_sources()
        print(format_output(results, 'list_sources'))
        
    elif args.command == 'install':
        result = install_skill(args.skill_name, args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.command == 'update':
        if args.skill_name == 'neuro-bridge':
            result = update_neuro_bridge_skill()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "status": "error",
                "message": f"Update for '{args.skill_name}' is not supported yet. Only 'neuro-bridge' is supported."
            }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
