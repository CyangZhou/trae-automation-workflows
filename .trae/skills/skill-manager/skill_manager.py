#!/usr/bin/env python3
"""
Trae Skill Manager - 技能管理器
安装、更新、卸载和管理 AI 技能
"""

import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

SKILL_DIR = Path("e:/traework/00 ai助手研发/.trae/skills")
REGISTRY_FILE = Path("e:/traework/00 ai助手研发/.trae/skill-registry.json")


class SkillManager:
    def __init__(self):
        self.skill_dir = SKILL_DIR
        self.registry_file = REGISTRY_FILE
        self.skill_dir.mkdir(parents=True, exist_ok=True)
        self._init_registry()
    
    def _init_registry(self):
        """初始化注册表"""
        if not self.registry_file.exists():
            default_registry = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "installed_skills": [],
                "skill_sources": [
                    {"name": "github", "url": "https://github.com", "type": "git"},
                    {"name": "local", "url": "local", "type": "local"}
                ]
            }
            self._save_registry(default_registry)
    
    def _load_registry(self) -> Dict:
        """加载注册表"""
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict):
        """保存注册表"""
        registry['last_updated'] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def list_skills(self, show_all: bool = False) -> List[Dict]:
        """列出已安装技能"""
        registry = self._load_registry()
        skills = registry.get('installed_skills', [])
        
        if not show_all:
            skills = [s for s in skills if s.get('enabled', True)]
        
        # 添加本地检测信息
        for skill in skills:
            skill_path = self.skill_dir / skill['name']
            skill['exists'] = skill_path.exists()
            skill['path'] = str(skill_path)
            if skill_path.exists():
                skill_md = skill_path / 'SKILL.md'
                skill['has_skill_md'] = skill_md.exists()
        
        return skills
    
    def install_skill(self, skill_name: str, source: str = "local", 
                     repo_url: Optional[str] = None) -> Dict:
        """安装技能"""
        registry = self._load_registry()
        
        # 检查是否已安装
        existing = next(
            (s for s in registry['installed_skills'] if s['name'] == skill_name),
            None
        )
        if existing:
            return {
                "status": "error",
                "message": f"技能 '{skill_name}' 已安装",
                "path": existing['path']
            }
        
        # 安装路径
        install_path = self.skill_dir / skill_name
        
        if source == "github" and repo_url:
            # 从 GitHub 克隆
            result = self._install_from_git(repo_url, install_path)
            if result['status'] != 'success':
                return result
        elif source == "local":
            # 本地技能（已存在）
            if not install_path.exists():
                return {
                    "status": "error",
                    "message": f"本地技能 '{skill_name}' 不存在"
                }
        else:
            return {
                "status": "error",
                "message": f"不支持的安装源: {source}"
            }
        
        # 验证技能结构
        skill_md = install_path / 'SKILL.md'
        if not skill_md.exists():
            # 清理
            if source == "github":
                shutil.rmtree(install_path, ignore_errors=True)
            return {
                "status": "error",
                "message": f"技能结构不完整，缺少 SKILL.md"
            }
        
        # 解析 SKILL.md 获取版本
        version = self._parse_skill_version(skill_md)
        
        # 注册技能
        skill_info = {
            "name": skill_name,
            "version": version,
            "path": str(install_path),
            "source": source,
            "enabled": True,
            "installed_at": datetime.now().isoformat()
        }
        
        registry['installed_skills'].append(skill_info)
        self._save_registry(registry)
        
        return {
            "status": "success",
            "message": f"技能 '{skill_name}' 安装成功",
            "skill": skill_info
        }
    
    def uninstall_skill(self, skill_name: str) -> Dict:
        """卸载技能"""
        registry = self._load_registry()
        
        skill = next(
            (s for s in registry['installed_skills'] if s['name'] == skill_name),
            None
        )
        if not skill:
            return {
                "status": "error",
                "message": f"技能 '{skill_name}' 未安装"
            }
        
        # 删除文件
        skill_path = Path(skill['path'])
        if skill_path.exists() and skill['source'] == 'github':
            shutil.rmtree(skill_path, ignore_errors=True)
        
        # 从注册表移除
        registry['installed_skills'] = [
            s for s in registry['installed_skills'] 
            if s['name'] != skill_name
        ]
        self._save_registry(registry)
        
        return {
            "status": "success",
            "message": f"技能 '{skill_name}' 已卸载"
        }
    
    def update_skill(self, skill_name: str) -> Dict:
        """更新技能"""
        registry = self._load_registry()
        
        skill = next(
            (s for s in registry['installed_skills'] if s['name'] == skill_name),
            None
        )
        if not skill:
            return {
                "status": "error",
                "message": f"技能 '{skill_name}' 未安装"
            }
        
        # 对于 neuro-bridge，调用特殊更新逻辑
        if skill_name == 'neuro-bridge':
            return self._update_neuro_bridge_skill()
        
        # 其他技能：重新安装
        if skill['source'] == 'github':
            skill_path = Path(skill['path'])
            if skill_path.exists():
                shutil.rmtree(skill_path, ignore_errors=True)
            
            # 重新克隆
            return {
                "status": "info",
                "message": f"请使用 install 命令重新安装 '{skill_name}' 以更新"
            }
        
        return {
            "status": "info",
            "message": f"技能 '{skill_name}' 无需更新"
        }
    
    def _update_neuro_bridge_skill(self) -> Dict:
        """更新 neuro-bridge 技能"""
        project_dir = Path("e:/traework/00 ai助手研发")
        user_guide = project_dir / "docs" / "NEURO_BRIDGE_USER_GUIDE.md"
        
        if not user_guide.exists():
            return {
                "status": "error",
                "message": f"User guide not found at {user_guide}"
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
        neuro_bridge_dir = self.skill_dir / "neuro-bridge"
        skill_file = neuro_bridge_dir / "SKILL.md"
        
        try:
            neuro_bridge_dir.mkdir(parents=True, exist_ok=True)
            
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(skill_content)
            
            # 更新注册表
            registry = self._load_registry()
            skill = next(
                (s for s in registry['installed_skills'] if s['name'] == 'neuro-bridge'),
                None
            )
            if skill:
                skill['version'] = "1.0.0"
                skill['updated_at'] = datetime.now().isoformat()
                self._save_registry(registry)
            
            return {
                "status": "success",
                "message": f"neuro-bridge skill updated and saved to {skill_file}",
                "skill_path": str(skill_file),
                "version": "1.0.0"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write skill file: {str(e)}"
            }
    
    def enable_skill(self, skill_name: str, enabled: bool = True) -> Dict:
        """启用/禁用技能"""
        registry = self._load_registry()
        
        skill = next(
            (s for s in registry['installed_skills'] if s['name'] == skill_name),
            None
        )
        if not skill:
            return {
                "status": "error",
                "message": f"技能 '{skill_name}' 未安装"
            }
        
        skill['enabled'] = enabled
        self._save_registry(registry)
        
        action = "启用" if enabled else "禁用"
        return {
            "status": "success",
            "message": f"技能 '{skill_name}' 已{action}"
        }
    
    def search_skills(self, query: str) -> List[Dict]:
        """搜索技能（从 skill-market-hub）"""
        try:
            # 导入并调用 skill-market-hub 的搜索功能
            sys.path.insert(0, str(self.skill_dir / 'skill-market-hub'))
            from skill_market_hub import search_github_skills
            return search_github_skills(query)
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]
    
    def _install_from_git(self, repo_url: str, install_path: Path) -> Dict:
        """从 Git 仓库安装"""
        try:
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, str(install_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Git clone 失败: {result.stderr}"
                }
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _parse_skill_version(self, skill_md: Path) -> str:
        """从 SKILL.md 解析版本"""
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            # 简单解析，查找 version 字段
            for line in content.split('\n'):
                if 'version:' in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        return parts[1].strip().strip('"\'')
        except:
            pass
        return "1.0.0"
    
    def scan_local_skills(self) -> Dict:
        """扫描本地技能目录，同步到注册表"""
        registry = self._load_registry()
        existing_names = {s['name'] for s in registry['installed_skills']}
        
        new_skills = []
        for skill_dir in self.skill_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name not in existing_names:
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    version = self._parse_skill_version(skill_md)
                    skill_info = {
                        "name": skill_dir.name,
                        "version": version,
                        "path": str(skill_dir),
                        "source": "local",
                        "enabled": True,
                        "installed_at": datetime.now().isoformat()
                    }
                    registry['installed_skills'].append(skill_info)
                    new_skills.append(skill_dir.name)
        
        if new_skills:
            self._save_registry(registry)
        
        return {
            "status": "success",
            "message": f"扫描完成，发现 {len(new_skills)} 个新技能",
            "new_skills": new_skills
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Trae Skill Manager - 技能管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s list                          # 列出已安装技能
  %(prog)s scan                          # 扫描本地技能
  %(prog)s search pdf                    # 搜索技能
  %(prog)s install browser-use --repo https://github.com/...
  %(prog)s update neuro-bridge           # 更新技能
  %(prog)s uninstall old-skill           # 卸载技能
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出已安装技能')
    list_parser.add_argument('--all', action='store_true', help='显示所有技能（包括禁用）')
    
    # scan 命令
    subparsers.add_parser('scan', help='扫描本地技能目录')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安装技能')
    install_parser.add_argument('skill_name', help='技能名称')
    install_parser.add_argument('--source', default='local', help='安装源 (local/github)')
    install_parser.add_argument('--repo', help='GitHub 仓库 URL')
    
    # uninstall 命令
    uninstall_parser = subparsers.add_parser('uninstall', help='卸载技能')
    uninstall_parser.add_argument('skill_name', help='技能名称')
    
    # update 命令
    update_parser = subparsers.add_parser('update', help='更新技能')
    update_parser.add_argument('skill_name', help='技能名称')
    
    # enable/disable 命令
    enable_parser = subparsers.add_parser('enable', help='启用技能')
    enable_parser.add_argument('skill_name', help='技能名称')
    
    disable_parser = subparsers.add_parser('disable', help='禁用技能')
    disable_parser.add_argument('skill_name', help='技能名称')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索技能')
    search_parser.add_argument('query', help='搜索关键词')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = SkillManager()
    
    if args.command == 'list':
        skills = manager.list_skills(show_all=args.all)
        print(json.dumps(skills, ensure_ascii=False, indent=2))
    elif args.command == 'scan':
        result = manager.scan_local_skills()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'install':
        result = manager.install_skill(args.skill_name, args.source, args.repo)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'uninstall':
        result = manager.uninstall_skill(args.skill_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'update':
        result = manager.update_skill(args.skill_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'enable':
        result = manager.enable_skill(args.skill_name, True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'disable':
        result = manager.enable_skill(args.skill_name, False)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'search':
        results = manager.search_skills(args.query)
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
