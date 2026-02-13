# GitHub Pages 部署指南

## 执行日期
2026-02-13

## 任务概述
将静态网页上传到GitHub并部署到GitHub Pages

## 执行步骤

### 1. 检查Git状态
```powershell
Set-Location "项目目录"
git status
git remote -v
```

### 2. 提交更改
```powershell
git add -A
git commit -m "更新说明"
```

### 3. 处理冲突（如有）
```powershell
# 拉取远程更新
git pull origin main

# 如果有冲突，选择保留版本
git checkout --ours index.html  # 保留本地版本
git checkout --theirs index.html  # 保留远程版本

# 解决后提交
git add .
git commit -m "解决冲突"
```

### 4. 推送到GitHub
```powershell
git push origin main
```

### 5. GitHub Pages配置
- 确保 `.nojekyll` 文件存在于仓库根目录
- GitHub Pages会自动从main分支部署
- 访问地址格式：`https://用户名.github.io/仓库名/`

## 常见问题

### Q: 推送被拒绝
**原因**: 远程有更新，本地落后
**解决**: 先 `git pull origin main` 再推送

### Q: 冲突解决
**原因**: 同一文件被不同人修改
**解决**: 手动编辑冲突文件，删除冲突标记后提交

### Q: Pages未更新
**原因**: GitHub Pages部署需要时间
**解决**: 等待1-2分钟后刷新页面

## 本次执行结果
- 仓库: `CyangZhou/nianhua-fortune`
- 部署地址: https://cyangzhou.github.io/nianhua-fortune/
- 状态: ✅ 部署成功

## 标签
`github` `pages` `deploy` `git` `static-webpage`
