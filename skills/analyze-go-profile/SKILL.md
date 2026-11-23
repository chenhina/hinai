---
name: analyze-go-profile
description: 分析已有 Go pprof 文件或 goroutine 栈，结合源码定位 CPU 热点、内存保留、分配压力、锁竞争和并发阻塞。适用于 Go 性能排查。
---

# 分析 Go 性能剖析数据

先核对样本类型、采集时间、构建版本、进程和采集时的负载。用对应版本的源码和可用的匹配二进制解释符号。资料只支持局部结论时，说明该结论适用的采样窗口和条件。

用 `go tool pprof -top <profile>` 查看热点，或使用已安装的独立 `pprof -top <profile>`。必要时加 `-cum` 按累计调用成本排序，或用 `-traces` 读完整栈。已有文本 goroutine dump 时，按完整调用链和等待状态归组。

- **CPU** 对照 flat 和 cumulative 值，沿热点的调用路径区分函数本身的消耗与调用频次。CPU 样本可以解释活跃计算时间，等待需要其他证据。
- **堆与分配** 用 `-sample_index=inuse_space` 查采样时的内存保留，用 `-sample_index=alloc_space` 查累计分配。结合对象数、负载和采集窗口判断体积大与频繁分配的原因。
- **goroutine** 沿重复调用栈核对创建点、退出条件、context、channel 持有者及对端。用多个时间点在相近负载下的增长和回落判断是否疑似泄漏。
- **block 或 mutex** 先确认采集配置和关注的样本指标，再沿同步等待或持锁栈检查临界区、下游 I/O 及调用量。

保留主要调用链、样本值与单位、对应源码、可支持的结论和待验证的假设。提出最小补充采样或验证方法。采集线上数据需要用户授权及环境访问。

[Go 性能诊断文档](https://go.dev/doc/diagnostics) · [独立 pprof](https://github.com/google/pprof)
