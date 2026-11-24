# CAM AI Review（1token-bot）常见雷区与应对 — 2026-11-24

> 来源：PR #76080（hyperliquid 下载对账）12 条 findings 逐条处理的全过程，
> 兼及 PR #76078 一条 [P1] 的核实。两轮 review 均由 1token-bot（gpt-6.2-sol, codex engine）产出。

## bot 行为特征（workflow 相关）

- push 后约 14 分钟出结果：**每条 finding 一个独立 review（COMMENTED、body 空）+ 行级评论**，
  另有一条 issue 评论形式的总结（含全部 findings 索引、规则匹配度、耗时的 `<details>`）。
- 总结评论尾部有 `cam-ai-review-state:v1 <base64>` 状态 blob，用于增量 review（seen/active 列表）。
- 行级回复用 `gh api repos/<org>/<repo>/pulls/<n>/comments/<id>/replies -f body=...`；
  summary-only 的 finding 没有行级锚点，用 issue 评论统一回复并 @bot。
- 单条 finding 质量不均：**policy 类几乎全中，"设计类"偶有过度设计或与平台约束冲突的建议**，
  逐条核实后采纳/微调/反驳比全盘接受好。

## Policy 铁律类（几乎每条都命中，写码时就该避开）

1. **错误信息不携带原始记录/响应体**（policy/error.md#6 铁律）。成交 JSON、事件行、
   上游响应体都可能带客户资金明细或服务端诊断信息，一旦进错误消息就会落库 + 进 Sentry。
   本次命中 3 处（count 解析、misc 事件转换、fill 反序列化——后两处是存量问题被"改动行"扫出）。
   正确姿势：只带记录序号 + `%w` 错误链。
2. **业务代码禁 `fmt.Errorf`/`errors.New` 新增错误**（policy/error.md#1 铁律）。
   必须用 code error（`code.<Module>.Xxx.WithError(fmt.Errorf(...))`，fmt.Errorf 作被包装的
   cause 是允许的，也是存量惯例）。本次命中 2 处。
3. **测试里丢弃 Write 返回的 err 不行**（error.md#4/testing.md#4 铁律）。
   `_, _ = w.Write(...)` 会被扫出；用同包已有的断言式 helper（如 writeMockResponse）。
4. **资源打开后紧跟 defer/Cleanup 关闭**（resource.md#1 铁律），测试也不例外。
5. **错误匹配用 `errors.Is`/`errors.As`，不用字符串包含**（error.md#9 约定，测试断言同样适用）。

## 代码设计类 findings（有真货，需逐条评估）

6. **确定性文件名 + 失败路径 = 覆盖旧归档**：合并文件名不含任务 ID 时，重提同区间先截断旧文件
   再逐分片写，中途失败会让旧任务 FilePath 指向半成品。修复模式：写 `.part` 临时文件，
   全部成功后 `os.Rename` 原子发布。⚠️ 连带效应：mock 掉 combineZipFiles 的存量测试要遵守
   契约（成功时真的创建文件），否则 rename 必挂。
7. **传输错误 ≠ 配置错误**：`doRequest` 把建连/超时/读响应和 host 未配置全塞进
   `ErrShouldNotHappen`，如果重试只认 `ExgApiUnavailable`，瞬时断连会直接判死任务。
   在接口封装层把传输故障重映射为可重试码，配置类错误由重试上限兜底。
8. **闭区间分片的单毫秒尾片**：[start, end] 切 365 天窗口，长度 ≡ 1 (mod window) 时尾片
   start == end。下游接口若要求 start 严格小于 end（如 hlds count），这类分片无法走同一条
   校验路径——跳过并注释盲区比盲查吃 400 更合理。
9. **mock 路径要跟着主流程一起审视**：给主流程加前置查询（如 GetUserAddress）会顺手
   打断 mock 账户——它没有签名配置。条件里先判 mock 直接返回，保持 mock 行为不变。

## 测试工程踩坑（本次真实踩到）

10. **helper 里 `defer Close` 是在 helper 返回时执行的**——`newTestZipWriter` 内 defer 关闭
    zip writer，返回后测试体拿到的是已关闭的 writer。正确做法：`t.Cleanup` 注册
    （LIFO 保证先关 writer 再关文件），需要中途读取内容的场景给幂等显式 close 函数，
    读完再读文件。
11. **zip 中央目录在 Close 时才写入**：没关 writer 就 `zip.OpenReader` 会得到
    "not a valid zip file"。
12. **mock 函数要守住被 mock 函数的契约**：mock 成功路径却不产生输出文件，下游新增的
    rename 步骤就会挂——改 mock 比改生产代码迁就测试正确。

## PR #76078 [P1] 跨批次回放顺序（核实结论，供 follow-up）

- blotter 迭代器分批键 (OccurTimeStamp, DB Id)（lessRecordIdAndTime）vs 回放排序键
  (DealtTime, ExchangeTID, ExchangeOID)（sortServiceDBTrans）不一致；同时间戳且两序相反的
  成交对撞上批次边界时，回放顺序随批大小变化。
- **master 1e4 批次时代同样存在，非 recon 并行 PR 引入**；5000 只挪动了边界位置。
- 已在 PR 回复中留 follow-up 方案（a：迭代器键对齐，共享服务需单独评估；b：批尾同时间戳
  延迟到下一批合并回放，影响面小）。

## 修复提交

- PR #76080: commit 312459fad79（12/12 findings 闭环，三包本地测试全绿）
- PR #76078: 跨批次 finding 已由分支会话核实并回复（follow-up 跟踪中）

## 第二轮 review 追加（commit 312459f → 4c95dde，6 条新 finding + 4 条旧确认）

13. **清理路径的 `_ = os.Remove` 也是"丢弃错误"**：删除失败（权限等）要记日志并注明
    "NotExist 视为已清理"，不能裸 `_ =`。
14. **`url.Error` 的文本内嵌完整请求 URL**——把 doRequest 的传输错误文本透传进错误消息，
    等于把客户钱包地址和查询区间写进 ErrInfo/Sentry。传输类错误用固定文案，不带底层错误。
15. **提交时解析的数据要随分片/任务持久化**：账户可编辑换地址（不改账户名），
    下游用"当前地址"校验"提交时地址"的文件是真实竞态。存进 Param，回退兼容存量。
16. **共享串行 MQ 消费者里的内联重试要算预算**：timeout × attempts + 间隔的总和要与
    既有阻塞先例（pending 路径 1 分钟 sleep 重排队）同量级；专用短超时比全局超时更合适。
    彻底方案（独立执行路径）动消费模型，标 follow-up 而不是顺手改。
17. **AI 生成污染自检**：长会话疲劳期工具调用参数可能被注入垃圾标识符（如 UnPointError、
    "syscalled false"），出现"不可能存在的代码"立即 `git restore <file>` 回滚到已提交版本，
    改用小步编辑（≤3 行 old_string）或整文件 Write，不要继续长 Edit。
