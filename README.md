# hinai

我的 AI 档案库，收录日常工作中可复用的 AI skills。

## Skills

| Skill | 用途 |
| --- | --- |
| [meegle-task-plan](skills/meegle-task-plan/SKILL.md) | 读取飞书项目工作项和关联资料，结合代码仓库生成 Markdown 技术方案。 |

把对应的 skill 目录复制到 Codex 的个人 skills 目录（通常为 `~/.codex/skills/`），再在待分析的代码仓库中调用。

```text
$meegle-task-plan 12345 --project-key example
```

也可以直接传飞书项目工作项链接。运行时需要能够读取对应工作项，以及访问要分析的代码仓库。
