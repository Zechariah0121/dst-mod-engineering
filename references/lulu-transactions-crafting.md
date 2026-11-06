# 露露案例：唯一物品事务与原物品升级

适用于稀缺物品生成失败、跨分片重试、恢复时无法判断实体存在，以及配料选取/扣除范围不一致。关联 LULU-09、10 与 12，案例范围见[露露索引](lulu-case-index.md)。

2026-11-05 只做源码、哈希和历史产物复核，未执行附件脚本、未运行游戏。原版 ZIP SHA-256 为 `fb94157f7c7728eff7c898816683ee323d9a7a6141d18c88ad95685ab5c93d76`，本轮直接读取核对下列范围；761239/build 26335394 是来源准备身份，不由文件名推定。代码、测试和私人日志不随 Skill 分发，下文“研究包”路径是输入包内定位，不是公开下载链接。

## 预约、生成与交付要分别判断

旧基线先 claim 再生成，SpawnPrefab 返回 nil 时直接返回，账本仍占用；后续重试被拒绝（研究包 `代码与测试/重构记录/20261102_发放事务修复/0.9.12_核对基线/scripts/iluneth/sword/bond.lua:83–104`）。这个反例支持检查提交边界，不支持给所有生成流程统一套用一份事务模板。

当前项目将 owner/token/generation 与 request/reservation ID 分开，主分片管理账本，请求分片管理 journal/outbox。只有 waiting 持有活生成回调；主侧先记 materialize_started，再允许请求侧生成。实体存在后提交占用，随后尝试 GiveItem。这里的“提交”表示唯一名额已被实体占用，**不表示玩家背包已收到物品**。

| 观察到的结果 | 本案例处理 | 不能推出 |
|---|---|---|
| 活调用方尚未生成，或 SpawnPrefab 正常返回 nil | 取消对应预约，后续可按明确入口重试 | 任意异常均可证明零实体 |
| 已返回实体，随后 GiveItem 抛错或背包满落地 | 保留占用，不重新生成 | 已交付、物品一定可取回 |
| 恢复旧 waiting，主侧已有 materialize_started | 转 uncertain，保守占用 | 本地旧快照没有实体，所以其他分片也没有 |
| 已确认销毁先于 commit | 记销毁及匹配完成墓碑；迟到 commit 仅结束旧请求 | 旧 ACK 可以更新新世代 |
| 没有账本/没有回应/超时 | UNKNOWN，不自动释放名额 | 不存在、可以补发 |

实现定位：研究包 `代码与测试/Iluneth/scripts/components/iluneth_sword_registry.lua:40–77,119–212,234–267,269–317,319–420`；`代码与测试/Iluneth/scripts/iluneth/sword/bond.lua:92–114,159–190`。这些状态名、ID 组合、墓碑和保守可用性取舍都是本项目方案。durable outbox 的含义是被 OnSave 纳入保存数据并按相同 ID 重试，不能据此声称每条内存变更已经落盘。

独立反例推演（未执行）：请求分片保存了新世代实体，主账本却单独回滚到旧 destroyed 世代；再次 reserve 可分配同一后继世代并生成第二实体。generation 也是存档数据，不能跨独立回滚充当单调时钟。因此不采纳真实双分片 exactly-once、跨分片原子持久化或“加世代号即可保证唯一”的结论。原版 `scripts/networkclientrpc.lua:1895–1897,1947–1957` 只展示发送委托引擎和接收入队，没有给出重启持久投递或共同原子快照保证。

另外，生成函数内部产生副作用后抛错时，调用方可能拿不到实体；当前 generating 保守占用可以阻止自动补发，却没有证明最终可恢复。墓碑裁剪、未知预约人工恢复、第三方删除路径和双分片乱序/迁移仍需分别设计与验证。

## 身份恢复提供正证据，普通移除不证明销毁

实体 OnSave 保存身份，OnLoad 恢复后延迟 Observe；缺账本而有序列化身份时建立已发放记录，冲突时保守占用。该身份钩子在旧基线已存在，不能称为本次新机制。玩家、物品、世界分别保存自己的状态；程序生成角色的 local owner 不等于真实账号持久化。见研究包 `代码与测试/Iluneth/scripts/iluneth/sword/bond.lua:270–324` 及 registry `:119–164`。

普通 Remove 可能来自卸载或玩家 session teardown。项目只在受控 DestroyEntity/绿杖路径执行后确认实体失效，或受控永久销毁意图后由世界任务确认。原版 `scripts/physics.lua:177–219` 的 DestroyEntity 还可进入采摘等保留实体的分支，方法被调用也不等于真的删除。跨实体确认任务归属与保存顺序沿用 [lifecycle-save.md](lifecycle-save.md)，不要复制已有原则。原版 `scripts/entityscript.lua:1979–2013` 确认 OnPreLoad → pairs 加载组件 → prefab OnLoad，没有固定组件加载顺序。

## 配料发现、拟态检查与扣料必须对齐输入域

原版范围核对：`scripts/components/inventory.lua:623–636` 的 FindItem 搜物品栏、active、overflow；`:1697–1753` 的 GetCraftingIngredient 先搜允许制作的打开容器，再搜携带物品；`:1507–1549,1624–1683` 的 Has/GetItemByName 只有显式 checkallcontainers 才扩大范围；`:1772–1799` 的 ConsumeByName 默认扣携带物品。携带不自动包含装备槽。打开容器符合原版制作规则，不能把箱子材料称为原版非法输入。

旧项目用制作查询选剑/宝石，却以持有权校验和携带范围扣料。反例是身上材料足够、打开箱子也有宝石时，先选到箱子宝石再被持有权拒绝；拟态检查也可能检查最终不会消耗的物品。当前菜单升级专门从携带域选一级非 nocrafting 的剑，用 GetItemByName 形成携带材料映射，检查这份映射，再升级原剑。其他配方仍委托原 DoBuild。见研究包 `代码与测试/Iluneth/scripts/iluneth/sword/items.lua:75–157`。

**同一输入域不等于材料已经预留。** 材料映射与 ConsumeByName 仍是两次查询，消费也按名称重新选择。原版 `scripts/components/builder.lua:500–531,546–565,918–942` 同样区分检查、分配和消费，拟态检查还可能调用 TurnEvil；不能把查询当成无副作用预约。当前代码先多次扣料再 SetSwordStage，没有回滚日志；Hook、同步事件或 SetSwordStage 内部异常可留下部分扣料或部分更新。此处补充具体反例，沿用既有 `FACT-DST-003` 的非事务边界，不重复登记事实。`BTR-P02` 是修船消费合同，不能移用成此制作入口的依据；Core HOLD 保持。

原剑升级保持 GUID/token/generation；玩家冷却仍归玩家组件，阶段更新再通知账本最高阶。SetSwordStage 同时更新 net stage、耐久、图像和标签，二级加 nocrafting 防止再次作为一级制作材料。见研究包 `代码与测试/Iluneth/scripts/prefabs/iluneth_magic_sword.lua:100–129,199–208`。这是本物品的身份连续性方案，不是原版 Upgrade 组件合同，也不要求所有物品都原地升级。仅携带材料、具体费用和天体站点门槛是玩法决定；更一般的配方接入读 [items-food-plants.md](items-food-plants.md)。

## 历史证据与来源不足

| 历史身份 | 包内可查材料 | 最强可采用表述 |
|---|---|---|
| 49 断言、3 文件语法 | `代码与测试/重构记录/20261102_发放事务修复/sword/result.json:1–6`、`cases.lua:17–208` | 历史 Lua5.1 替身结果声明；结果无输入 SHA，所需 native761239 切片未入包，不能绑定当前快照；网络与人工快照不是磁盘重启 |
| 独立 6 组 | 同目录 `sword-review/independent_result.json:1–30`、`independent_protocol.py` | 历史独立替身结果；结果内 registry hash 与本包 raw hash 不同，不能声称当前代码已运行通过 |
| `1ff283c943e2463a872aba6b8026dcb8` | `运行证据摘录/<runID>.json`；`server_integration.lua:20–76` | 历史离线单分片结果摘录报告 passed；本包没有完整日志，摘录只有704/705/707行，缺少所引706魔剑专用 PASS，707 DONE为书本悬浮测试；不称完整魔剑日志复验；runner 脚本同 SHA 原件未入包，server_integration.lua 仅供设计对照 |
| `6e92312064db49148e4c52c661a65bfe` | `运行证据摘录/<runID>.json`；`代码与测试/重构记录/20261104_实机反馈修复/sword/native_fixture.lua:22–126` | 历史单分片936行具体升级 DONE：OnNewSpawn→MakeRecipeFromMenu/BUILD，检查身份、冷却、两站点、携带扣料、箱子不动；非真实远端点击/画面 |
| `b0226008afa642f584bf3b7f58551dea` | `运行证据摘录/<runID>.json`，原日志802行失败 | nil注入未达到零生成断言；当前夹具改GLOBAL.SpawnPrefab。旧夹具完整快照及专题所引修正说明未提供，环境作用域原因保留为历史归因，不能仅凭摘要确认唯一根因 |
| `6c122f9007304e6cbc78719e3268e21f` | `运行证据摘录/<runID>.json`，原日志842行失败 | normal initial sword断言失败；当前夹具显式OnNewSpawn。缺完整旧夹具，不能把这一失败泛化为升级逻辑错误 |

历史 staged 是发布转换产物，研究包保留注释源码，两者 raw SHA 不同不能单独证明语义变化，也不能称字节一致；索引声明的转换对应未在本轮重放。尤其 1ff283 的历史 bond staged hash 与后来映射的 staged hash 也不同，不把历史运行泛化到当前完整版本。本文所有 PASS 均为历史材料身份，不是本轮重跑。验证层次沿用 [testing-release.md](testing-release.md)；联网边界见 [networking-rpc.md](networking-rpc.md)。

本轮已核对的研究包字节身份：

| 包内文件 | SHA-256 |
|---|---|
| `代码与测试/Iluneth/scripts/components/iluneth_sword_registry.lua` | `3c10abb47b30d0d38be107cafcdca8942515001a6abff66b3a1dcebc134c7fff` |
| `代码与测试/Iluneth/scripts/iluneth/sword/bond.lua` | `7563760cb21bd07917985776e83c2e489e0edf14246d1d01a42e394024d528bc` |
| `代码与测试/Iluneth/scripts/iluneth/sword/items.lua` | `067bd900db6acdab0c87b10b5a0efb1068a19115b16da8282900081aece19261` |
| `运行证据摘录/1ff283c943e2463a872aba6b8026dcb8.json` | `e35eeb620c5228a08ae2ff5a71738856162dc604379726c1d4f6a527db5fa27b` |
| `运行证据摘录/6e92312064db49148e4c52c661a65bfe.json` | `95429bb3633a73fe4bb9098007b4a1b1d237adc907edaae04dd3b26dde15a5f4` |

研究包不可得时，只使用上述条件化判断，不声称已读取其代码或重现历史结果。真实双分片、磁盘重启、同账号重连、独立回滚与第三方组合均仍待验证。
