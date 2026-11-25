# 辅助脚本

存放可独立运行的工具，例如把 Git diff 整理成评审材料。随脚本记录依赖、运行方式和输出位置，方便以后复用。

## check-repo-policy.py

在目标 Git 仓库内运行。需要 Git 和 Python 3.9+，使用 Python 标准库。下列命令从本仓库运行时可直接使用。检查其他仓库时，在该仓库内用脚本的绝对路径调用。

```bash
python3 scripts/check-repo-policy.py --staged
python3 scripts/check-repo-policy.py --base origin/master
python3 scripts/check-repo-policy.py --staged --ascii-paths
```

`--staged` 只读暂存版本。`--base` 检查共同祖先与 `HEAD` 之间的提交差异，基线可换成目标分支或提交。脚本检查变更文件的完整内容，接受 LF、CRLF 和 Markdown 两个空格的显式换行。文本检查仅覆盖脚本中列出的文件类型，JSON 语法、重复键和非标准数值检查仅适用于 `.json`。按需要用 `--ascii-paths` 启用文件名和目录名检查。

退出码 `0` 表示通过，`1` 表示发现问题，`2` 表示参数、基线或读取错误。输出包含文件路径、规则编号和能定位的行号。

[仓库与 CI 检查规则](../policies/repository-checks.md)

## sync-opencodereview-rules.py

在目标 Git 仓库内运行。需要 Git 和 Python 3.9+。将示例中的脚本路径换成你本地的实际位置。

```bash
python3 /path/to/hinai/scripts/sync-opencodereview-rules.py --write
python3 /path/to/hinai/scripts/sync-opencodereview-rules.py --check
```

脚本从 Git 已跟踪文件和未被忽略的新文件中寻找 `AGENTS.md`、`CLAUDE.md`，按目录生成 `.opencodereview/rule.json` 的 `rules`。默认跳过工具缓存和依赖目录。可重复使用 `--skip-dir path/to/module` 忽略指定目录的文档，并在本地和 CI 使用同一组参数。

`--write` 将生成的 `rules` 与原配置的其他顶层字段一起写入文件。仓库已有手写规则时，可先审阅生成结果再提交。`--check` 只读比较映射。退出码 `0` 表示成功或已同步，`1` 表示配置缺失或映射过期，`2` 表示输入、读取或生成失败。

[OpenCodeReview 模块规则](../policies/opencodereview.md)
