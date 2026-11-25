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
