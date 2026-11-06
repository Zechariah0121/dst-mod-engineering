# 复杂 Mod 架构与原版执行链

阶段记录 `v2026.11.05.1`：231 条登记知识，其中 44 条机制研究。

- 新增[复杂 Mod 架构指南](../references/complex-mod-architecture.md)，帮助 AI 划分模块职责、明确状态写入者，设计接口、存档和失败恢复。
- 补充事件监听快照与 SG 重入研究，帮助 AI 识别解绑后仍会执行的回调、嵌套切态后仍继续的旧调用。
- 补充前端加载环境与容器 Replica 交接研究，帮助 AI 正确安排注册与初始化，避免把局部就绪当成全部就绪。

## 研究入口

| ID | 研究问题 |
|---|---|
| EXP-ARCH-001 | 普通监听、SG 缓冲和 Brain 接收的执行边界 |
| EXP-ARCH-002 | GoToState 重入后的外层续行与 newstate 观察 |
| EXP-ARCH-003 | 前端临时环境的登记归属与 safe 入口错误传播 |
| EXP-ARCH-004 | container replica / classified 双向补接与槽初始化窗口 |

通过 `get_entry(id="EXP-ARCH-001", projection="reviewer", pointer="/claims/0")` 读完整原子；API 用显式 `family="native_mechanism"` 的 `lookup_api` 查询。名称没有独立契约时按记录和引用继续研究，不从同名符号推断公共 API。参数、预算及准入见[机制研究族](native-mechanisms.md)。

架构指南是工程建议，露露材料是条件化案例；本次新增研究依据 `761239` 源码静态核读，保留 `research/restricted/hold`，未做游戏运行验证。历史知识正文及 Scope 不变。更新时按具体文件、引用和调用链复核，不增加整包版本白名单。
