# hinai

我的 AI 档案库，收录日常工作中可复用的 AI skills、模板和经验。

## 目录

| 目录 | 用途 |
| --- | --- |
| [skills/](#skills) | 可直接调用的 AI 工作流程。 |
| [policies/](policies/README.md) | 可跨项目采用的工程规则、评审判据和检查入口。 |
| [templates/](templates/README.md) | 可复制填写的交付模板。 |
| [examples/](examples/README.md) | 展示如何调用 AI，以及预期输出长什么样。 |
| [evals/](evals/README.md) | 可重复运行或检查的 AI 验收用例。 |
| [playbooks/](playbooks/README.md) | 串联多个步骤或 skills 的工作手册。 |
| [scripts/](scripts/README.md) | 可独立运行的辅助脚本。 |
| [preferences/](preferences/README.md) | 个人写作、沟通和工作偏好。 |
| [notes/](notes/README.md) | 实践记录、踩坑经验和改进想法。 |

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
| [design-go-tests](skills/design-go-tests/SKILL.md) | 设计 Go 测试用例，选择 HTTP API、外部服务和函数依赖的 mock 边界。 |
| [analyze-go-profile](skills/analyze-go-profile/SKILL.md) | 结合 Go pprof 与源码诊断性能和并发问题。 |
| [quick-retro](skills/quick-retro/SKILL.md) | 简短复盘一次事件，确定下次可验证的改进动作。 |
| [learn-from-review](skills/learn-from-review/SKILL.md) | 从已核实的 PR 评论提炼可复用的检视方法。 |
| [refine-skill-from-runs](skills/refine-skill-from-runs/SKILL.md) | 用实际使用反馈改进 skill 并验证行为。 |
| [check-requirement-consistency](skills/check-requirement-consistency/SKILL.md) | 对照需求、方案、代码和测试，定位规则的差异或遗漏。 |
| [plan-user-facing-change](skills/plan-user-facing-change/SKILL.md) | 从用户视角写清目标行为、流程和验收场景。 |
| [edit-technical-chinese](skills/edit-technical-chinese/SKILL.md) | 润色中文技术文档，保留事实和约束。 |
| [split-large-pr](skills/split-large-pr/SKILL.md) | 将大 PR 拆成可评审和验证的改动。 |
| [organize-technical-docs](skills/organize-technical-docs/SKILL.md) | 为总览、操作手册和参考资料建立清晰的阅读路径。 |

把对应的 skill 目录复制到 Codex 的个人 skills 目录（通常为 `~/.codex/skills/`），再在待分析的代码仓库中调用。

```text
$meegle-task-plan 12345 --project-key example
```

调用 `meegle-task-plan` 时也可以直接传飞书项目工作项链接。它需要能够读取对应工作项，以及访问要分析的代码仓库。
