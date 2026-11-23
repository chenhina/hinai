---
name: watch-pr-checks
description: 只读跟踪 GitHub PR 的 CI 状态，等待指定检查结束或定位失败。适用于查看检查、等待 required checks、分析失败日志。
---

# 跟踪 PR 检查

把目标解析为明确的仓库和 PR 编号，记录 PR URL 与当前 head SHA。用户指定检查时使用该范围，否则关注 required checks。后续查询都使用同一个仓库和编号。

使用现有 GitHub 连接或 GitHub CLI。CLI 查询示例使用已解析的 `repo` 和 `pr`。

```bash
gh pr view "$pr" --repo "$repo" --json url,headRefOid,statusCheckRollup
gh pr checks "$pr" --repo "$repo" --required --json name,bucket,state,link
```

用户要求等待时，持续轮询至所需检查进入终态、到达用户给出的截止时间，或遇到权限和环境阻塞。每次判断终态前核对 head。若跟踪目标是 PR 最新版本，发现新 head 时重新开始观察并说明版本变化。若目标是特定提交，按 SHA 查询检查和提交状态。区分 API 错误、检查尚未登记和已确认没有配置所需检查的情况。

失败时查看对应检查的相关日志，区分变更引入的问题、已有失败、基础设施异常和证据不足。报告 PR、提交、检查结论及失败链接。这个流程只读取状态和日志。

[GitHub CLI 检查命令](https://cli.github.com/manual/gh_pr_checks)
