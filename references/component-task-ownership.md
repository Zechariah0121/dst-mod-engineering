# 组件、任务与清理的设计参考

这是冻结 game762172/build26474873 的静态研究参考，关联 EXP-LIFE-005..007。research/restricted/hold 保持不变；登记及独立审阅状态以 [FAMILY-REGISTRY](../knowledge/FAMILY-REGISTRY.json) 为准。不修改 canonical、历史 Scope 或 HOLD，runtime_verified=false。精确行号、文件及范围 SHA256 见 [登记研究](../knowledge/research/native-mechanisms/component_task_lifecycle-5f01617bcbb0.json)；本文不附 Lua 全文。

## 安装完成要按阶段理解

AddComponent 的顺序为：重复检查 → 加载类 → ReplicateComponent → 组件构造 → 公布 components 槽与小写 shadow → ComponentPostInit → 动作登记 → 返回局部实例。构造期间，本次组件不在安装槽；PostInit 中则已存在。重复名字按小写判定，直接返回旧实例；加载路径和实际槽键仍保留传入值。RemoveComponent 按精确槽键读取，大小写行为与判重不同。（CTL-S01..S08）

PostInit 的原 mod 回调被 runmodfn 的 xpcall 包装，失败会进入禁用坏 mod/显示错误路径；不能笼统说回调错误会原样抛出，也不能据此承诺整段安装有回滚。构造、replica、动作关联或错误处理自身抛错时，要检查已完成的阶段。PostInit 若移除组件再正常返回，外层没有重新核对槽位，仍会登记动作并返回原局部实例。（CTL-S02/S03/S05/S06/S08）

RemoveComponent 先提交更新停止、清 wall 更新，再清槽和 shadow，随后直接执行 OnRemoveFromEntity，最后注销 replica 标签与动作索引。清理钩子中同名重新安装，外层旧卸载仍会继续做后置注销，不能当成原子替换；钩子抛错也会跳过后置步骤。底层 replica 对象与公开标签可用性是不同资源，UnreplicateComponent 不在此处删除底层对象。（CTL-S03/S04/S07/S08/S10/S11）

## 更新登记与任务调度分开持有

StartUpdatingComponent 按 cmp 对象身份登记；不要求构造时已公布槽位，找不到名字时仅使用 component 作诊断名。StopUpdatingComponent 写停止标记，调用点不会立即清表。正常 Update 在调用前跳过标记对象，遍历后合并新实体，再延迟删键；暂停时 StaticUpdate 也消费同一停止表。同宿主对同对象 Start 可在消费前撤销停止。false/nil 的 do_static_update 不会删除已有 static 登记。（CTL-S09/S10/S12/S13/S14）

这不保证所有新增组件统一在下一帧首次更新：新宿主先排到 NewUpdatingEnts，原本就在更新集合的宿主则直接改变对象表。停止也不会中断已经进入的 OnUpdate，不会取消 DoTaskInTime/DoPeriodicTask；wall 更新有自己的立即删除路径。（CTL-S09..S13）

| 资源 | 所有者/身份 | 退出入口 | 不会代办的事 |
|---|---|---|---|
| 安装槽与 shadow | EntityScript + 原 name / 小写名 | RemoveComponent | 不全量取消宿主任务或监听 |
| 普通/static 更新键 | cmp 对象，宿主更新表 | StopUpdatingComponent → 更新循环 Deferred | 不停止当前 Lua 栈，不取消任务 |
| 调度句柄 | 创建任务的宿主 pendingtasks[handle] | handle:Cancel 或正常完成 | 不清组件自己的字段 |
| 组件句柄字段 | 业务组件 | 业务 Stop/清理函数取消后置 nil | 不自动停止由别处持有的任务 |
| Timer 名字 | 宿主 timer 组件的记录 | StopTimer；完成先释放名字再发布 timerdone | 与整个宿主任务集合不同 |
| 事件监听 | listener/source/event/fn 组合 | 精确 RemoveEventCallback | 不撤回已形成的同步调用快照 |

任务包装把宿主放到回调首参，以 GUID 作调度 id，同时登记句柄及 task_finish。普通/static 任务共享 pendingtasks。一次性任务的成功完成在回调返回后，因此回调正在运行时它仍在集合里；在其中 Cancel 自己只改变后续调度和清理，不会中断当前函数。Periodic 回调返回 true 也不会自动停止，退出需要 Cancel。（CTL-S15..S20）

CancelAllPendingTasks 是整个宿主集合的操作。组件拆除应先确认自己持有哪些句柄，避免顺手取消其他业务的任务。宿主 Remove 会在组件 OnRemoveEntity 前取消一次 pendingtasks；清理后重新创建任务仍需独立追踪。若任务建在另一个存活实体上，删除当前组件/实体不扫描那个实体的集合。（CTL-S03/S15..S21）

## SaltLicker 的具体闭环

SaltLicker 构造要求 timer 已安装。SetUp 先 Stop 旧配置，保存 uses_per_lick，非 nil 才登记八组业务事件并立即尝试恢复；false 也属于非 nil，不是合法数值的证明。未找到盐碱时建立周期句柄与 saltlick_placed 监听。找到目标后，当前周期回调启动 salt 计时，然后取消自身、清 _task 和监听，最后继续设置 salted。这里的继续执行来自普通 Lua 调用栈，调度退出来自 Cancel，而非回调返回 true。（CTL-S15/S16/S18/S19/S22..S25/S27）

Timer 到期先 StopTimer，删除旧名字并取消旧句柄，再同步发 timerdone。SaltLicker 消费本轮并重查目标；若仍可找到，会在同一事件调用栈中创建新的同名 salt 计时。旧 OnTick 结尾只清理旧句柄，不会再次按名字删除新计时。这是具体生产者与消费者共同形成的顺序，不能泛化为任意事件回调都可以安全重入。（CTL-S15/S18/S19/S23/S27/S29）

暂停停止计时与搜索；Stop 解除业务监听、停止名字、取消周期句柄并清配置；OnRemoveFromEntity 调 Stop 后再去 tag。LoadPostPass 仅消费已存在的 Timer 状态。SetSalted 会同步发 saltchange，所以 Stop 具有可观察副作用，也没有通用防重入锁。（CTL-S23..S29）

项目实施时可以沿用现有组件和清理方法，只需列清这些资源及匹配退出动作。本研究不要求新增 Bus/Installer，也不设定玩法数值、死亡/换角/读档的产品政策。所有结论只到所列 Lua 静态路径；原生调度、异常恢复、实际舔盐行为与任意 mod 覆盖兼容尚未运行验证。
