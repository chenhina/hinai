---
name: design-go-tests
description: 设计、编写或评审 Go 测试，选择表驱动用例，并为 HTTP API、外部 HTTP 服务和函数或方法依赖设置 mock。适用于新增测试、补回归或梳理已有 mock 时。
---

# 设计 Go 测试

先读被测模块的约定、真实入口和邻近测试。明确要保护的行为、可以观察的输出，以及哪些依赖需要控制。

## 设计用例

- 围绕一个行为选择正常输入、边界、已明确的业务规则和错误输入。优先覆盖会改变结果或副作用的分支。适合共享结构时，用表驱动测试和 `t.Run`，每行保留输入、预期结果以及相关错误或调用期望。
- 固定时间、随机性和测试数据。让每个子测试独立准备依赖及状态。检查返回结果、错误和关键副作用，用 `t.Cleanup` 或生命周期合适的 `defer` 释放资源。
- 保留本次要验证的路径。缺少必要依赖时，在最邻近的可控边界替换它。复杂响应可放进 `testdata/`，使用合成或脱敏数据。

## 选择 Mock 边界

| 要验证的行为 | 测试方式 |
| --- | --- |
| 本服务的 HTTP 接口 | 用真实的路由、handler 和适用的中间件，替换它们调用的业务依赖。通过仓库现有 HTTP helper 或 `httptest.NewRequest`、`httptest.NewRecorder` 发请求，断言状态码、必要响应头和响应体。 |
| 调用外部 HTTP 服务 | 用 `httptest.NewServer` 替代上游，把服务器地址注入真实客户端。核对 method、path、参数及必要的请求体，再模拟成功、上游错误或非法响应。只需要控制传输错误时，可注入 `http.RoundTripper` 或已有客户端接口。 |
| 函数、方法或时间 | 优先用参数、构造器或小接口注入。固定结果用简单 stub。需要按输入返回、检查调用参数或模拟多次响应时，再写能反映这些行为的 fake。 |

测试流式或长轮询接口时，普通 handler 测试可以验证业务结果。通过原入口验证连接、分帧或取消等协议行为。

仅当目标仓库已有约定且缺少注入点时使用运行时 patch。使用 gomonkey 时，固定结果优先用 `ApplyFuncReturn` / `ApplyMethodReturn`，需要按实参执行逻辑时用 `ApplyFunc` / `ApplyMethodFunc`。安装 patch 后立即登记 `Reset`，避免并行用例或后台 goroutine 在 patch 生效及恢复时经过被改写的函数。运行命令遵循仓库的版本和禁用内联配置。[gomonkey 说明](https://github.com/agiledragon/gomonkey#notes)

## 运行与交付

优先运行受影响的包和用例。Go 项目可从 `go test ./path/to/package -run '^TestName$' -count=1` 起步，按仓库约定扩大范围。SQL 交互用 `sqlmock` 核对语句、参数、事务和 `ExpectationsWereMet`，数据库方言、约束和实际持久化行为在隔离的集成测试中验证。[sqlmock 说明](https://github.com/DATA-DOG/go-sqlmock)

交付时记录覆盖场景、mock 的依赖和执行结果。需要标准库代码时，参考 [HTTP 和函数 Mock 示例](references/http-and-function-mocks.md)。
