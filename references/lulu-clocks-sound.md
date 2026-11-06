# 露露案例：动作时钟、同步重入与声音尾段

适用于角色主端 SG 的动作时长、消费回调和声音退出研究。案例范围见[露露索引](lulu-case-index.md)；基础机制见[StateGraph](characters-brains-stategraphs.md)、[生命周期](lifecycle-save.md)、[音频](audio-particles.md)与[测试](testing-release.md)。

## 来源与验证身份

研究包 SHA256：`fc24353695f876b43f341497a698efc6f3dc24532817276e17f1432de218e3eb`。本轮研究于 2026-11-05 **自行读取当前 scripts.zip 并重算 SHA256**：`fb94157f7c7728eff7c898816683ee323d9a7a6141d18c88ad95685ab5c93d76`，所引原生文件及报告已有范围哈希均匹配。761239 / build 26335394 的版本身份由研究包及 MCP 来源准备信息支持，本轮研究未启动游戏。

本轮只做源码与身份静态核验、读取派生运行摘录；未执行附件脚本或重跑历史测试。下文“历史专服”表示研究包所报单分片、无真实客户端运行。原 manifest/log 只有哈希与选行摘录，完整原件未在本轮研究重新读取；发布 source/release 对应来自证据索引与研究报告，未重跑发布核验。代码与私人日志不随本参考稿分发；包内相对路径供持有研究包者定位，不能当成已附带依赖。

## LULU-02：先分清时钟消费者，再决定如何变速

**源码事实。** `scripts/stategraph.lua:661–704` 用传入 dt 推进 timeinstate、timeout、timeline 与 onupdate；`:733–758` 的外层 Update 用 GetTime 差量，且无 onupdate 时可能按下一事件/timeout 请求睡眠。仅替换 UpdateState 的 dt，不能据此认定动态资源变化会逐帧反映。

**项目方案。** `代码与测试/Iluneth/scripts/iluneth/reset/cast_recovery.lua:9–56` 每次以魔力得到时长倍率 m，转发一次旧 UpdateState(dt/m)，保留含 nil 的多返回值，同时让人物与明确字段中的 FX 以 1/m 推进动画；timeline 扣费后仍处原 statemem 才刷新倍率。`fortune_casting.lua:38–67` 保留并转发 onupdate，让这些状态持续更新。适用对象由角色、法典和状态条件限定。基础倍率、魔力曲线及 FX 列表属于项目设计。

| 消费者 | 本案例归属与边界 |
| --- | --- |
| SG timeline、timeout、timeinstate | 经本实例包装的局部 dt |
| 人物动画、列举且仍有效的 FX | 分别设置动画倍率；不是任意 FX 自动覆盖 |
| 绝对冷却截止 | 世界 GetTime；动作加快不自动缩短冷却 |
| DoTaskInTime / soundtask | 另一个调度域，不能因 SG 变速便假设它同步缩放 |
| animover | 原生 book/book2 的收尾依赖它；本方案保留自然动画推进路径 |

**反例。** 历史 `代码与测试/重构记录/20261104_实机反馈修复/cast/fortune_casting.lua:79–94` 把 timeline 另延后为任务；同目录旧 `cast_recovery.lua:15–21,36–71` 用 SetTime 补推动画。旧注释关于跨末帧事件的说法不能升级为已验证引擎契约。当前原版 `SGwilson.lua:10146–10159` 自有 layer sound task，`:10369–10372` 独立清理，也说明“整段所有效果同速”需要逐项查证。

**证据与限制。** 历史运行 `15311c480b054aea98abffe255079106` 的摘录原日志827行记录 DONE/4249断言；匹配 SHA 的 `cast/native_full_cast.lua:10–28` 列17组，`:94–98` 明示 repeatcast 由测试开启，生产法典不默认启用。引导运行 `8b44419a91234c3694fa5ed259b0dcca` 摘录870行记录630断言。整段场景逐项结果未包含在摘录，不声称本轮研究读过完整日志。无远端预测/平滑画面证据；Stop 中函数恢复有身份判断，但人物/FX倍率恢复1仍依赖项目默认值，多 Mod 动态倍率合成未验证。

**处理：限定采纳。** 新增时钟归属和外层调度反例，复用已有 SG/所有权原则，不推广具体曲线、帧数或包装器方案。

## LULU-03：业务成功返回后，复核旧状态是否仍有执行权

**源码事实。** `components/eater.lua:270–284` 依次 PushEvent(oneat)、oneatfn、OnEaten、HandleEatRemove，最后成功返回。`entityscript.lua:1312–1345` 直接调用 EntityScript 监听函数，但 SG 事件另有立即处理/入队分支，不能写成“一切 PushEvent 都同步”。`stategraph.lua:529–599` 有效切态先 onexit，再新建 statemem，后 onenter；同名重入也不复用该表。

**反例与项目方案。** oneat 监听在同一调用栈切到 hit，旧 onexit 已清理；EatOne 随后仍可成功返回。若此时无条件 PlaySound，就会在清理之后重新发声。`代码与测试/Iluneth/scripts/stategraphs/iluneth_candybag.lua:143–155` 在消费前保存 mem，成功返回后确认实体有效且 statemem 仍是 mem，才标记消费并启动表现。`fortune_casting.lua:43–54` 对旧 onenter 同样复核；原生 book 的 repeat 分支可在 onenter 内直接转 book2，仅比较状态名不能辨认同名新一轮。

历史运行 `554214d286484bb4a2852e99d1ca4a38` 摘录原日志967行记录 oneat_interrupt 消费1、Play0，与匹配夹具真实 Eater 加监听切 hit 的断言一致。这里业务消费成功仍然成立，不能因旧状态失权而重试消费。

**处理：采纳为条件化反例。** statemem 身份用于这类同步生命周期边界；它不是线程锁、回滚或异步 RPC 去重协议。实体移除、回调抛错、第三方复用 mem 等未实测。

## LULU-04：下一轮准入与已提交一口的尾段分开

**项目事实。** 糖袋第37帧消费，第71帧 timeout；手动 >=100% 停止、自动启动 <75% 且停止 >90%，均是项目需求。旧 `代码与测试/重构记录/20261104_主动糖声与前端入口/candy/iluneth_candybag.before.lua:73–78` 每次达到阈值便退出，消费导致跨阈值后可能立刻 KillSound。

当前 SG `:73–80,139–167` 分开三个条件：咬前满足阈值可结束；成功消费并保持状态执行权后允许现有 timeout 尾段自然完成，再决定是否开下一口；移动、受击、死亡、失袋等硬中断仍走退出清理，不为了尾音延迟它们。`:32–46` 清理具名声音句柄。具名句柄并不能证明 FMOD 事件是循环事件，原版 layer sound 的具名管理也有明确非循环注释。

历史 `554214d286484bb4a2852e99d1ca4a38` 摘录985/994行分别记录 manual_final/automatic_final 消费1、Play1；995行 DONE 明写 no audio claim。匹配的 `代码与测试/重构记录/20261104_主动糖声与前端入口/candy/native_fixture.lua:24–55,79–92` 使用真实糖跨阈值，审计并转发 Play/Kill。其 active 是夹具布尔：只能证明调用窗口与配对，不能证明原生声音持续、音频解码、银行加载、波形、扬声器听感或远端同步。automatic_final 直接进入晚期自动一轮，不证明完整自动起手链；75% 边界另属源码及替身合约。

**处理：采纳生命周期案例。** 保留“提交前取消／提交后自然尾段／硬中断清理”的判断，不把37/71帧、阈值或听感写成通用规范。

## 相关 LULU-12：先核验夹具触发了什么

糖声失败运行 `3a0cab1b64a645fbb03e267be21c3f11` 摘录原日志815行保留 sound leaked after move，不能改写为通过。其匹配旧夹具 `代码与测试/重构记录/20261104_入口与外观恢复/candy_sound/native_fixture.before_move_fix.lua:76–84` 使用 WalkForward() 再 PushEvent。当前原版 locomotor `:741–752,1116–1146,1174–1176` 表明未带 direct 的 WalkForward 不设置前进意图，RunInDirection 才经 WalkInDirection 设置意图并发事件；生产判断读的是该意图。修正夹具 SHA 匹配 `8e8f0e29a0c8495e860ec7db0f4070f6`，摘录928行 move通过、987行DONE。两次是不同运行，后者不抹去前者失败。

引导失败 `48e407e039a94adfbbdf66272a1289ac` 摘录765行报 cancel consumed cast。当前 `entityscript.lua:1588–1595` 清动作会调 Fail，`bufferedaction.lua:104–110` 调失败回调后清表；修正夹具 `cast/native_full_channel.lua:101–106` 应断言失败回调一次、零扣费、不改冷却、不复活。旧失败夹具字节未提供，不能仅凭错误文本确认唯一根因。报告另称旧施法夹具漏 SetCanSleep(false)，但旧日志没有休眠诊断，本轮研究未获得该失败运行完整证据，故休眠唯一根因仍未证实。当前夹具有禁止睡眠及 awake 断言；设置不能替代观测。

上述成功与失败摘录均报告进程退出码1；结合各自 loaded、READY、同 runID DONE/FAIL、passed 与8秒观察窗判断，退出码不能单独裁定。完整测试准则复用 [测试与发布](testing-release.md)，其他夹具与发布案例见 [夹具专题](lulu-fixtures-release.md)。

## 去重与采纳范围

本轮研究通过 MCP Reviewer 读取相关条目的全部投影原子与 Scope：`NC-N003-INT-04` 已有执行、回调与确认分层，且重入安全保持未知；`NC-N003-INT-07` 已有每次入态 statemem 新表；`NC-N004-FINAL-05` 已有按来源撤销与共享标量恢复边界。它们保留各自历史来源、coding_status=hold，本案例不将未知整体改成保证。四个相关 Skill reference 已覆盖对称清理、前提断言和 nosound 局限；新增价值是具名触发顺序、混用时钟和失败夹具，不能宣称全库首次发现。

## 引用身份

原生路径均为 scripts.zip 成员。以下整文件 SHA256 由本轮研究重算；包内代码与运行摘录可按文中相对路径、运行 ID 和原日志行号定位；未随包提供的原件保留缺口。

| 文件 | SHA256 |
| --- | --- |
| `scripts/stategraph.lua` | `714a86523d5f0855ce00884f009053fc64392a4a86edd0c0b515e0e42ea8ecc8` |
| `scripts/entityscript.lua` | `9dce0787ffeacefc3c7017ae041ba8408b25ca9344aea25d979945feef6b4cac` |
| `scripts/components/eater.lua` | `d8de9b5c73274deb42198f8cc937915ff6b1bbb42eb908d72a84cc24bde688b4` |
| `scripts/stategraphs/SGwilson.lua` | `7b381c15992c5001e6d84329ee8e961b6f5f9db573e0f24ab3b7a61d859270a6` |
| `scripts/components/locomotor.lua` | `b8e383d9cdf24db51b1bdb554ae8c68f6bc501522232219724a0200114148fdc` |
| `scripts/bufferedaction.lua` | `82514b46f1fd771094ca41c17645dc98c871a5de998df6b83251db7be67e9f34` |

包内关键源码快照（整文件SHA256；不随公开稿分发）：

- `代码与测试/Iluneth/scripts/iluneth/reset/cast_recovery.lua`：`bfb04344c63b8ed1aefa009ac94653e0020272bb3f57e5b7933bf0ba554bb916`。
- `代码与测试/Iluneth/scripts/iluneth/reset/fortune_casting.lua`：`eb450b2e7b61ab431409cc99430296d161ea2b28e4145bec9903f96045445aa8`。
- `代码与测试/Iluneth/scripts/stategraphs/iluneth_candybag.lua`：`7b721b98e00104aa243e7b1e89a2b58c22e1a6f14e78e7756c982e12c9c1e314`。
- `代码与测试/Iluneth/scripts/iluneth/reset/candybag.lua`：`73b75c997a5e838bd1d374422a3413efe3192dcd5a937a33c000643a4acd7298`。
