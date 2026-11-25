# OpenCodeReview 模块规则

在项目根目录和需要独立审查规则的模块里维护 `AGENTS.md` 或 `CLAUDE.md`。使用同步脚本在目标项目生成 `.opencodereview/rule.json`。该文件保存审查路径到文档的映射。

## 匹配顺序

- 同一目录优先选 `AGENTS.md`，只有 `CLAUDE.md` 时选它。
- 子模块排在父模块之前。若有根目录文档，`**/*` 放在最后兜底。OCR 按顺序取第一条命中的项目规则。
- 每条映射都启用 `merge_system_rule`，让命中的项目文档与 OCR 内置规则一起生效。父模块与根目录条目仍按首次命中顺序参与选择。需要沿用共同要求时，可在模块文档里指明共同规则的位置。

例如，项目有根目录 `AGENTS.md` 和 `src/catalog/CLAUDE.md` 时，会生成如下映射。

```json
{
  "rules": [
    {
      "path": "src/catalog/**",
      "merge_system_rule": true,
      "rule": "src/catalog/CLAUDE.md"
    },
    {
      "path": "**/*",
      "merge_system_rule": true,
      "rule": "AGENTS.md"
    }
  ]
}
```

## 维护与验证

规则正文在对应模块的文档里改。新增、删除、移动或改名文档后，用 `--write` 更新映射。CI 可用相同参数加 `--check` 替代 `--write`，只读检查生成内容是否同步。[生成脚本用法](../scripts/README.md#sync-opencodereview-rulespy)

生成器管理 `rules`，沿用已有的 `include`、`exclude` 和其他字段。需要控制源码审查范围时，按项目设置过滤条件。用 `--skip-dir` 可以跳过某个目录下的规则文档。若还要排除该目录下的代码审查，在 JSON 中设置 `exclude`。

安装 OCR 后，可以用 `ocr rules check src/catalog/handler.go` 查看指定文件命中的规则。把示例路径换成目标项目里的实际文件。[OpenCodeReview 官方规则文档](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/review-rules.md)

个人写作或审查偏好可复用 [模块文档与中文代码审查模板](../preferences/agents-module-and-review.md)，按需要并入目标项目的指引。
