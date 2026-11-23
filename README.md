# hinai

我的 AI 档案库，收录日常工作中可复用的 AI skills。

## Skills

| Skill | 用途 |
| --- | --- |
| [meegle-task-plan](skills/meegle-task-plan/SKILL.md) | 读取飞书项目工作项和关联资料，结合代码仓库生成 Markdown 技术方案。 |
| [review-pr](skills/review-pr/SKILL.md) | 评审 PR 或本地差异，给出可验证的发现。 |
| [address-pr-feedback](skills/address-pr-feedback/SKILL.md) | 核实评审意见，按要求修复、推送或逐线程回复。 |
| [watch-pr-checks](skills/watch-pr-checks/SKILL.md) | 只读跟踪 PR 的 CI 检查，定位失败原因。 |
| [resolve-pr-conflicts](skills/resolve-pr-conflicts/SKILL.md) | 处理 PR 合并冲突并验证两侧行为。 |
| [simplify-code](skills/simplify-code/SKILL.md) | 在保留外部行为的前提下简化代码。 |
| [review-tech-spec](skills/review-tech-spec/SKILL.md) | 评审已有技术方案，核对设计风险和验收条件。 |
| [design-test-strategy](skills/design-test-strategy/SKILL.md) | 将验收点映射到测试层、运行环境和 CI。 |
| [analyze-go-profile](skills/analyze-go-profile/SKILL.md) | 结合 Go pprof 与源码诊断性能和并发问题。 |
| [quick-retro](skills/quick-retro/SKILL.md) | 简短复盘一次事件，确定下次可验证的改进动作。 |

把对应的 skill 目录复制到 Codex 的个人 skills 目录（通常为 `~/.codex/skills/`），再在待分析的代码仓库中调用。

```text
$meegle-task-plan 12345 --project-key example
```

调用 `meegle-task-plan` 时也可以直接传飞书项目工作项链接。它需要能够读取对应工作项，以及访问要分析的代码仓库。
