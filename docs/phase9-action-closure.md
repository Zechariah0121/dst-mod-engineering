# 动作执行、生命周期与接入收口

`v2026.11.06.2` 共 **244 条登记知识：64 + 13 + 110 + 57**。本轮接续[复杂架构](phase7-architecture-native.md)与[事件、任务、恢复](phase8-lifecycle-persistence.md)，让 AI 更容易从完整调用链判断执行、取消与清理责任。

- **检索与实体移除**：补齐 `EntityScript:Remove` 的完整合同与退出阶段，新增 `EXP-LIFE-008`，并改善跨记录检索和原子读取。
- **动作执行链**：新增 `EXP-ACT-001～003`，以普通 PICK 为样例串起鼠标输入、预测/非预测发送、服务器候选重建、执行点和回调槽位交接。
- **复杂 Mod 接入**：[可取消交互指南](../references/action-lifecycle-architecture.md)贯穿输入、权威写入、业务结果、表现与退出；优先复用原版机制。
- **来源与使用说明**：适配当前热修来源，按任务[准备来源](source-compatibility.md)，合并重复政策，按问题导航。

## 运行观察的范围

真实 762172 离线单分片专服完成具名事件/任务检查，并在独立进程恢复数值、false、同 shard GUID 引用和具名 Timer。原读进程在完成恢复断言后关闭异常；同一快照字节副本上的恢复复验干净退出，两个结果分别保留。

客户端输入、预测、RPC 到达、复制与画面尚未验证，调谐台文稿示例也未运行。上述观察仅支持具名服务器与恢复路径，研究条目仍为 `research/restricted/hold`。按[检索策略](../references/kb-retrieval.md)读取完整条件，目标 Mod 的验收见[测试与交付](../references/testing-release.md)。
