#!/usr/bin/env python3
"""
Workflow Market - 工作流市场索引系统
索引、搜索和管理工作流资源
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib
import urllib.request
import urllib.error

MARKET_DIR = Path("e:/traework/00 ai助手研发/.trae/skills/workflow-market")
INDEX_FILE = MARKET_DIR / "workflow-index.json"
SOURCES_FILE = MARKET_DIR / "sources.json"
LOCAL_WORKFLOW_DIR = Path("e:/traework/00 ai助手研发/.trae/workflows")


class WorkflowMarket:
    """工作流市场主类"""
    
    # 预定义的工作流来源
    DEFAULT_SOURCES = {
        "github": [
            {
                "name": "Awesome GitHub Actions",
                "url": "https://github.com/sdras/awesome-actions",
                "type": "awesome-list",
                "category": "ci-cd"
            },
            {
                "name": "GitHub Actions Workflows",
                "url": "https://github.com/actions/starter-workflows",
                "type": "official",
                "category": "ci-cd"
            }
        ],
        "articles": [
            {
                "name": "CSDN Workflow教程",
                "url": "https://blog.csdn.net",
                "type": "blog",
                "search_query": "GitHub Actions workflow"
            }
        ],
        "local": [
            {
                "name": "本地工作流",
                "path": str(LOCAL_WORKFLOW_DIR),
                "type": "local"
            }
        ]
    }
    
    # 工作流分类
    CATEGORIES = {
        "ci-cd": "持续集成/部署",
        "documentation": "文档生成",
        "project-mgmt": "项目管理",
        "code-quality": "代码质量",
        "automation": "通用自动化",
        "ai-ml": "AI/ML工作流",
        "security": "安全扫描",
        "monitoring": "监控告警",
        "deployment": "部署发布",
        "testing": "测试",
        "other": "其他"
    }
    
    def __init__(self):
        self.market_dir = MARKET_DIR
        self.index_file = INDEX_FILE
        self.sources_file = SOURCES_FILE
        self.market_dir.mkdir(parents=True, exist_ok=True)
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        if not self.index_file.exists():
            self._save_index({
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": 0,
                "workflows": []
            })
        
        if not self.sources_file.exists():
            self._save_sources(self.DEFAULT_SOURCES)
    
    def _load_index(self) -> Dict:
        """加载索引"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """保存索引"""
        index['last_updated'] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def _load_sources(self) -> Dict:
        """加载来源配置"""
        with open(self.sources_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_sources(self, sources: Dict):
        """保存来源配置"""
        with open(self.sources_file, 'w', encoding='utf-8') as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, name: str, source: str) -> str:
        """生成唯一ID"""
        content = f"{source}:{name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _categorize_workflow(self, name: str, description: str, tags: List[str]) -> str:
        """根据名称和描述自动分类"""
        text = f"{name} {description} {' '.join(tags)}".lower()
        
        category_keywords = {
            "ci-cd": ["ci", "cd", "build", "deploy", "pipeline", "action"],
            "documentation": ["doc", "readme", "wiki", "markdown", "note"],
            "project-mgmt": ["project", "management", "standup", "meeting", "report"],
            "code-quality": ["lint", "format", "review", "quality", "check"],
            "automation": ["auto", "backup", "sync", "schedule", "cron"],
            "ai-ml": ["ai", "ml", "model", "train", "predict", "llm"],
            "security": ["security", "scan", "vulnerability", "audit"],
            "monitoring": ["monitor", "alert", "log", "metric"],
            "deployment": ["deploy", "release", "publish", "ship"],
            "testing": ["test", "pytest", "unittest", "jest", "mocha"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "other"
    
    def sync(self) -> Dict:
        """同步工作流市场数据"""
        print("开始同步工作流市场数据...")
        
        # 1. 扫描本地工作流
        local_workflows = self._scan_local_workflows()
        print(f"发现 {len(local_workflows)} 个本地工作流")
        
        # 2. 从来源收集（模拟，实际需要从网络获取）
        remote_workflows = self._collect_from_sources()
        print(f"从远程来源收集到 {len(remote_workflows)} 个工作流")
        
        # 3. 合并索引
        all_workflows = local_workflows + remote_workflows
        
        # 4. 去重
        seen_ids = set()
        unique_workflows = []
        for wf in all_workflows:
            if wf['id'] not in seen_ids:
                seen_ids.add(wf['id'])
                unique_workflows.append(wf)
        
        # 5. 保存索引
        index = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_count": len(unique_workflows),
            "workflows": unique_workflows
        }
        self._save_index(index)
        
        return {
            "status": "success",
            "message": f"同步完成，共 {len(unique_workflows)} 个工作流",
            "local_count": len(local_workflows),
            "remote_count": len(remote_workflows),
            "total_count": len(unique_workflows)
        }
    
    def _scan_local_workflows(self) -> List[Dict]:
        """扫描本地工作流"""
        workflows = []
        
        if not LOCAL_WORKFLOW_DIR.exists():
            return workflows
        
        for yaml_file in LOCAL_WORKFLOW_DIR.glob("*.yaml"):
            try:
                import yaml
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                name = data.get('name', yaml_file.stem)
                description = data.get('description', '')
                triggers = data.get('triggers', [])
                
                workflow = {
                    "id": self._generate_id(name, "local"),
                    "name": name,
                    "description": description,
                    "source": "local",
                    "category": self._categorize_workflow(name, description, []),
                    "url": str(yaml_file),
                    "stars": 0,
                    "tags": triggers,
                    "local_path": str(yaml_file),
                    "installed": True,
                    "installed_at": datetime.now().isoformat()
                }
                workflows.append(workflow)
            except Exception as e:
                print(f"解析 {yaml_file} 失败: {e}")
        
        return workflows
    
    def _collect_from_sources(self) -> List[Dict]:
        """从远程来源收集工作流"""
        workflows = []
        
        # 这里模拟一些常见的工作流模板
        # 实际实现中应该从GitHub API、网页抓取等获取
        
        preset_workflows = [
            {
                "name": "Python CI",
                "description": "Python项目的持续集成工作流，包含测试、lint、类型检查",
                "source": "github",
                "category": "ci-cd",
                "url": "https://github.com/actions/starter-workflows/tree/main/ci/python.yml",
                "stars": 15200,
                "tags": ["python", "ci", "pytest", "flake8"]
            },
            {
                "name": "Docker Build and Push",
                "description": "自动构建Docker镜像并推送到仓库",
                "source": "github",
                "category": "deployment",
                "url": "https://github.com/docker/build-push-action",
                "stars": 8900,
                "tags": ["docker", "container", "deployment"]
            },
            {
                "name": "Auto Labeler",
                "description": "根据文件路径自动为PR添加标签",
                "source": "github",
                "category": "project-mgmt",
                "url": "https://github.com/actions/labeler",
                "stars": 3200,
                "tags": ["github", "pr", "automation"]
            },
            {
                "name": "Code Coverage",
                "description": "生成代码覆盖率报告并上传到Codecov",
                "source": "github",
                "category": "code-quality",
                "url": "https://github.com/codecov/codecov-action",
                "stars": 5600,
                "tags": ["coverage", "testing", "quality"]
            },
            {
                "name": "Dependabot Auto-merge",
                "description": "自动合并Dependabot的依赖更新PR",
                "source": "github",
                "category": "automation",
                "url": "https://github.com/ahmadnassri/action-dependabot-auto-merge",
                "stars": 1800,
                "tags": ["dependencies", "automation", "security"]
            },
            {
                "name": "Release Drafter",
                "description": "根据合并的PR自动生成发布说明草稿",
                "source": "github",
                "category": "documentation",
                "url": "https://github.com/release-drafter/release-drafter",
                "stars": 4200,
                "tags": ["release", "changelog", "documentation"]
            },
            {
                "name": "Stale Issue Handler",
                "description": "自动标记和关闭长期未活动的Issue和PR",
                "source": "github",
                "category": "project-mgmt",
                "url": "https://github.com/actions/stale",
                "stars": 2800,
                "tags": ["issue", "maintenance", "automation"]
            },
            {
                "name": "Security Scan",
                "description": "使用CodeQL进行安全漏洞扫描",
                "source": "github",
                "category": "security",
                "url": "https://github.com/github/codeql-action",
                "stars": 7500,
                "tags": ["security", "scanning", "codeql"]
            },
            {
                "name": "Notify Slack",
                "description": "将工作流状态通知发送到Slack",
                "source": "github",
                "category": "monitoring",
                "url": "https://github.com/8398a7/action-slack",
                "stars": 2100,
                "tags": ["slack", "notification", "alert"]
            },
            {
                "name": "Deploy to AWS",
                "description": "部署应用到AWS服务（ECS/Lambda/S3）",
                "source": "github",
                "category": "deployment",
                "url": "https://github.com/aws-actions",
                "stars": 4500,
                "tags": ["aws", "cloud", "deployment"]
            }
        ]
        
        for preset in preset_workflows:
            workflow = {
                "id": self._generate_id(preset['name'], preset['source']),
                "name": preset['name'],
                "description": preset['description'],
                "source": preset['source'],
                "category": preset['category'],
                "url": preset['url'],
                "stars": preset['stars'],
                "tags": preset['tags'],
                "installed": False
            }
            workflows.append(workflow)
        
        return workflows
    
    def search(self, query: str, category: str = None, source: str = None) -> List[Dict]:
        """搜索工作流"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        query_lower = query.lower()
        results = []
        
        for wf in workflows:
            # 文本匹配
            text = f"{wf['name']} {wf['description']} {' '.join(wf.get('tags', []))}"
            match_score = 0
            
            if query_lower in text.lower():
                match_score += 10
            
            # 分词匹配
            query_words = query_lower.split()
            for word in query_words:
                if word in text.lower():
                    match_score += 5
            
            if match_score == 0:
                continue
            
            # 分类过滤
            if category and wf.get('category') != category:
                continue
            
            # 来源过滤
            if source and wf.get('source') != source:
                continue
            
            wf['match_score'] = match_score
            results.append(wf)
        
        # 按匹配度和stars排序
        results.sort(key=lambda x: (x['match_score'], x.get('stars', 0)), reverse=True)
        
        return results[:20]  # 最多返回20个
    
    def browse(self, category: str = None, sort_by: str = "stars") -> List[Dict]:
        """浏览工作流"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        # 分类过滤
        if category:
            workflows = [wf for wf in workflows if wf.get('category') == category]
        
        # 排序
        if sort_by == "stars":
            workflows.sort(key=lambda x: x.get('stars', 0), reverse=True)
        elif sort_by == "name":
            workflows.sort(key=lambda x: x['name'])
        elif sort_by == "installed":
            workflows.sort(key=lambda x: x.get('installed', False), reverse=True)
        
        return workflows
    
    def get_categories(self) -> Dict[str, int]:
        """获取分类统计"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        categories = {}
        for wf in workflows:
            cat = wf.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories
    
    def get_stats(self) -> Dict:
        """获取市场统计"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        total = len(workflows)
        installed = sum(1 for wf in workflows if wf.get('installed'))
        local = sum(1 for wf in workflows if wf.get('source') == 'local')
        remote = total - local
        
        categories = self.get_categories()
        
        return {
            "total_workflows": total,
            "installed_workflows": installed,
            "local_workflows": local,
            "remote_workflows": remote,
            "categories": categories,
            "last_updated": index.get('last_updated', 'never')
        }
    
    def info(self, workflow_id: str) -> Optional[Dict]:
        """获取工作流详情"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        for wf in workflows:
            if wf['id'] == workflow_id:
                return wf
        
        return None
    
    def install(self, workflow_id: str) -> Dict:
        """安装工作流到本地"""
        wf = self.info(workflow_id)
        if not wf:
            return {"status": "error", "message": "工作流不存在"}
        
        if wf.get('installed'):
            return {"status": "info", "message": "工作流已安装"}
        
        # 对于远程工作流，需要下载
        if wf['source'] != 'local':
            # 这里简化处理，实际应该下载YAML内容
            return {
                "status": "info",
                "message": f"远程工作流 '{wf['name']}' 需要手动下载",
                "url": wf['url']
            }
        
        return {"status": "success", "message": f"工作流 '{wf['name']}' 已安装"}
    
    def get_recommended(self) -> List[Dict]:
        """获取推荐工作流"""
        index = self._load_index()
        workflows = index.get('workflows', [])
        
        # 推荐逻辑：高stars + 未安装
        candidates = [wf for wf in workflows if not wf.get('installed')]
        candidates.sort(key=lambda x: x.get('stars', 0), reverse=True)
        
        return candidates[:5]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow Market - 工作流市场',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s sync                          # 同步市场数据
  %(prog)s search "python ci"            # 搜索工作流
  %(prog)s browse --category ci-cd       # 按分类浏览
  %(prog)s info <workflow-id>            # 查看详情
  %(prog)s stats                         # 显示统计
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # sync 命令
    subparsers.add_parser('sync', help='同步市场数据')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索工作流')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--category', help='分类过滤')
    search_parser.add_argument('--source', help='来源过滤')
    
    # browse 命令
    browse_parser = subparsers.add_parser('browse', help='浏览工作流')
    browse_parser.add_argument('--category', help='分类过滤')
    browse_parser.add_argument('--sort', default='stars', choices=['stars', 'name', 'installed'])
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看工作流详情')
    info_parser.add_argument('workflow_id', help='工作流ID')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安装工作流')
    install_parser.add_argument('workflow_id', help='工作流ID')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示市场统计')
    
    # recommend 命令
    subparsers.add_parser('recommend', help='获取推荐工作流')
    
    # categories 命令
    subparsers.add_parser('categories', help='列出所有分类')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    market = WorkflowMarket()
    
    if args.command == 'sync':
        result = market.sync()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'search':
        results = market.search(args.query, args.category, args.source)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.command == 'browse':
        results = market.browse(args.category, args.sort)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.command == 'info':
        info = market.info(args.workflow_id)
        if info:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": "工作流不存在"}, ensure_ascii=False))
    
    elif args.command == 'install':
        result = market.install(args.workflow_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'stats':
        stats = market.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.command == 'recommend':
        recommendations = market.get_recommended()
        print(json.dumps(recommendations, ensure_ascii=False, indent=2))
    
    elif args.command == 'categories':
        categories = market.get_categories()
        result = {
            "categories": [
                {"id": cat, "name": WorkflowMarket.CATEGORIES.get(cat, cat), "count": count}
                for cat, count in categories.items()
            ]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
