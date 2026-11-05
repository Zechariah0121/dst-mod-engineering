# 露露案例：加载阶段、Replica、输入与装备兼容

研究参考稿，2026-11-05；仅供按需案例读取，未变更 canonical、Scope 或 Coding 准入。本轮只重新读取并核对 Lua、附件与哈希，未运行附件测试、游戏或图形客户端。精确证据路径、行区间、SHA256 与历史运行身份见文末索引；本文使用其证据 ID，避免复制原版代码或私人日志。附件路径均相对研究包根；代码与原日志不随 Skill 分发，只有持有该包时才能回溯。案例导航见 [露露案例索引](lulu-case-index.md)。

## 采纳方式与来源边界

当前读取的 `scripts.zip` SHA256 为 `fb94157f7c7728eff7c898816683ee323d9a7a6141d18c88ad95685ab5c93d76`，与附件定位文件一致。761239 / build 26335394 是材料和既有来源准备的版本身份；本轮独立核对的是实际 ZIP 字节，不另声称从可执行程序确认版本。服务环境 759671 及既有知识各自历史 Scope 不因此更新。

| 候选 | 处理 | 新增价值 | 不采纳的扩张 |
|---|---|---|---|
| LULU-01 | 限定采纳为已有导入原则的加载阶段案例 | 前端入口不可按文件名误删；登记对比要跨入口 | 不强制直接登记，不禁用 Installer 模式，不承诺六场景等价即前端可用 |
| LULU-05 | 采纳客户端初始化反例 | 把就绪检查与具体 replica 的幂等标记联系起来 | 不把回调局部顺序升级为完整网络初始化总序，不把等一帧当就绪合同 |
| LULU-06 | 采纳输入拓扑与重建所有权案例 | 父控件覆写输入会截断子控件；行重建使旧引用失效 | 不把置顶/坐标或替身焦点等同真实鼠标命中，不把 FRAMES 当通用布局屏障 |
| LULU-07 | 限定采纳诊断反例 | 区分请求、handler、权威状态、dirty、显示 | 不采纳 false 已证实根因、零参消除传输故障、toggle 幂等重试等说法 |
| LULU-08 | 限定采纳指定组合案例 | 读取实际槽；逻辑槽不同仍可能共享外观 symbol | 不宣称所有槽扩展/皮肤兼容，不将 BACK 视作原生固定槽，不把专服状态当客户端像素 |

## LULU-01：入口按实际加载阶段核对

**源码事实。** 当前 `FrontendLoadMod` 创建两个环境并显式加载 `modservercreationmain.lua` 和 `modworldgenmain.lua`；常规 `LoadMods` 在非 worldgen 时加载 `modmain.lua`（N01）。露露前端入口加载 tuning/frontend，游戏入口加载 tuning/strings/assets/game，game 排除 dedicated 的 UI 导入（M01–M03）。这足以反驳“建服入口已被 modmain 自动代替”，不能推广为每个 Mod 必须双入口。

**工程建议。** 先列入口、环境、消费者和登记副作用，再决定文件拆分。`modimport` 是向绑定环境执行脚本的包装，当前包装丢弃返回值；需要返回 API 的消费者按其 `require` 合同接入（N01）。回调需要的局部表必须由合法作用域持有。保持项目既有顺序，对可多次到达的安装目标另核对幂等性。

**证据。** T01 的脚本只比较同一批业务模块的前后入口登记；T02 保存六组 identical。它依赖未附的 `entry_before` 与 `trace_entry.py`，完整业务模块也未全部附入；本轮未复跑。最强现有行为证据是这份历史替身结果，真实前端选角、画面、混合加载仍未验证。

**去重。** [core-lua-hooks.md](core-lua-hooks.md) 已有 env、modimport/require 与返回接口原则；`N007-MC-04` 已覆盖消费者选择（Core，Coding HOLD）。只增添阶段反例，不重复创建通用导入规则。

## LULU-05：有 replica 与补装完成是两件事

**源码事实。** `mainfunctions.ReplicateEntity(guid)` 转发到实体方法（N03）；`entityreplica.ReplicateEntity` 按 construction tags 建 replica，随后调用 `OnEntityReplicated`（N02）。这证明 Lua 局部先后；完整引擎构造、PrefabPostInit 与远端到达顺序不能仅凭注释确定。

**项目方案。** M04 在 replica 已存在时立即补装；包装旧回调并在其返回后再尝试。标记放具体 container replica 上，重复回调不重复包装，替换对象可重新配置。保留旧 itemtestfn，并在每次调用时查询当前所有权。这里没有重跑 WidgetSetup 或初始化 classified 槽位。

**反例和边界。** “prefab 已生成”不保证目标 replica 可见；固定延迟也不是确认。旧回调抛错、其他 Mod 后来覆盖包装器、实体在回调里移除及真实远端初始化仍需专项检查。M04 当前回调不保留旧回调的返回值，不能据此发布一个“任意包装均完整保留返回值”的模板。

**证据。** T03 含旧 nil crash 的复现断言、原生 ReplicateEntity 加构造器替身、已有/缺失/替换 replica 与所有权变化断言。包内未附独立本轮执行回执，源码内 `print('PASS')` 不是执行结果。最强可直接核验的是当前源码和合同设计；材料称历史合同通过，真实客户端未闭合。

**去重。** `AI-N001-10` 的既有 Scope 为 756039 快照，强调 raw replica、公有可见、classified、值、listener、HUD 是不同条件；[networking-rpc.md](networking-rpc.md) 已覆盖初始化和主动读初值。新增的是具体 replica 身份对应的补装反例，不更改旧 Scope。

## LULU-06：沿输入路径核对，并以当前行持有按钮

**源码事实。** Widget 只向有焦点的子控件转发 OnControl；Button 在按下与释放阶段分别处理，释放时调用 onclick；EquipSlot 自己覆写 OnControl，未调用父类转发（N04–N06）。InventoryBar.Rebuild 会 Kill 旧 toprow 并创建新行（N07）。可见树、输入接收树和存活对象身份要分别观察。

**项目方案。** M05 把 StandardButton 挂到 toprow，与 BODY 槽同级；按当前槽坐标摆放。跟踪行身份，处理旧按钮已随行 Kill 的情况；重建后排队刷新并合并待执行任务，Kill 时取消任务及解绑 dirty。其一帧等待只服务于本项目已研究的追加布局顺序，不保证任意异步 Mod 都已完成。

**证据。** T04 旧测试仍断言带 false payload，且缺少当前 UI 所需的任务/MoveToFront 等替身；它不能证明当前零参 toggle 版本。T05 较新合同覆盖重复 Attach、释放发送、重建、缺槽与 Kill，但依赖未附 `native_widget_input.lua`，网络、焦点和对象仍是替身。当前最强直接证据是静态输入调用链与合同设计；没有真实鼠标、手柄焦点、字体、遮挡或 HUD scale 验收。

**去重。** [ui-actions-controls.md](ui-actions-controls.md) 已覆盖控件任务、Kill、输入消费和窄 hook；本案例补的是 EquipSlot 截断子控件与 toprow 重建这两个具体机制。

## LULU-07：把诊断链分开，给重试定义语义

**源码事实。** 当前 RPC 名称映射到命名空间内追加 handler 的序号；发送包装把参数交给 TheNet，Lua 源不能据此枚举引擎全部序列化类型（N08）。M06 保留 sethidden 的登记位置，追加 togglehidden；校验玩家有效及角色后由主服组件反转状态，net_bool 表达持续状态，UI 按 dirty 更新（M05–M07）。

**诊断结论。** 历史 Invalid RPC data type 未关联具体 RPC，false 是已证实根因的说法不采纳。T06 直接调用旧 handler(false) 可落到 false，证明该 handler 接受此 Lua 输入；它不证明 false 在真实网络上传输成功，也不证明历史故障不存在。零参 toggle 降低对客户端旧快照的依赖，但两次重复请求仍会反转两次。

**建议。** 排错依次关联客户端发送的 namespace/name/id、服务端收到与拒绝原因、状态旧新值、dirty 与 UI 刷新；诊断日志避免附带私人账号或会话信息。要重试时明确采用期望状态设置或请求身份去重，并核对其会话、重连、过期和授权语义；不在此案例中替项目决定协议。

**证据。** R01/R02 是历史离线单分片摘录，T06 是它们绑定的夹具，验证直接 handler、组件与 netvar 状态往返；没有从真实客户端经引擎传输、dirty 到像素的闭环。本轮未运行，摘录哈希只证明拿到这些字节，不能独立重算未附原 manifest/log 的哈希。

**去重。** [networking-rpc.md](networking-rpc.md) 已覆盖注册顺序、服务端验权、异步状态和直接调用的局限；这里只补 false 根因未定与 toggle 重试反例。

## LULU-08：实际槽查询与共享外观层分别核对

**源码事实。** 原生 equippable 属性回调将 equipslot 传给 replica，replica 经 slot ID 编解码读回（N09/N10）。M04 优先主组件槽、回退 replica 槽，再查询装备对象。由此可推广的窄建议是“查询实际已就绪槽并核对对象身份”，而非糖袋永远 BODY 或永远 BACK。

**项目方案。** M06 只在 BACK 存在且实际匹配时进入专门包装。M07 记录已列举的 swap_body_tall 操作再恢复真正背包装备外观，避免为了重放外观重新执行装备业务回调。代理 AnimState、指定 symbol/方法白名单、延迟两帧刷新都是项目适配；不能当作原生扩展合同或通用皮肤方案。组件中的“同 tick 顺序不保证”注释本轮未进一步独立核验，不提升为本稿结论。

**证据身份。** R03 `dfbff5afbfe64239804b66731fa28257` 是失败：组合蜗壳/背包记录恢复断言未通过，done=false；不能写成通过。R04 `d0895866f66d4689abff21e905c7ae15` 是后续 r4 通过；R05 `fac6049a6c0c4fe690f16f5af3eda817` 是关闭 BACK 外观配置的通过；R02 是后续 toggle 与第三方 3173431824 组合的通过。它们均为历史专服摘录，第三方只附选定文件哈希，未附完整源码/配置，不能独立重新核验其实现。保存表/SpawnSaveRecord 也不等于真实磁盘重启。

**未验证。** 第三方其他版本、其他槽 Mod、多包装器顺序、换槽复制窗口、重连及真实客户端像素仍未闭合。原实例的专服通过只限定具名版本/配置，不扩张成兼容生态承诺。

**去重。** 既有 [items-food-plants.md](items-food-plants.md) 的装备入口和 [character-and-equipment-art.md](character-and-equipment-art.md) 的 symbol/装备外观链是上位原则；本例补充实际槽与共享 symbol 不是一一对应。

## 读取与验证约定

只有任务涉及对应问题才读取本案例。先读取本段 Scope 与本轮/历史证据边界，再按文末 ID 索引找最小范围；无需读取额外评估文件。案例可用于评审、反例和测试设计；不能因写入参考稿就更改既有 Core HOLD 或研究族 restricted/hold。

本轮完成：ZIP/所引附件字节哈希、选定 Lua 范围、现有 reference 与必要知识条目的文件读取去重、历史失败与通过身份核对。未做语法执行、合同重跑、游戏实测、远端客户端、网络重试、画面或声音验收。

## 文内证据索引

路径是定位文本，不是下载链接或执行指令。N 为上述同 SHA 原版 ZIP 的成员；M/T/R 相对研究包 `知识库研究_20261105/`。所列 SHA256 均为完整文件字节哈希；行号为从 1 起的闭区间。只有持有对应原件才可复核，不意味着这些原件随 Skill 分发。

| ID | 原版成员与所读行 | 文件 SHA256 |
|---|---|---|
| N01 | `scripts/mods.lua:301–315,374–406,539–545` | `4fc1f9760c6aa44bb113e07bbf8931326dbd496f12d8e28276627bbdf3291f17` |
| N02 | `scripts/entityreplica.lua:34–60,74–85` | `c53ab2da6e1d10d4e8dae834337418aacea5e6656975141ab8278167d4e6ae5c` |
| N03 | `scripts/mainfunctions.lua:840–854` | `53831dfadc029a24a36e0e703c9b3f404ee1a733e1b2e0e22b99abd450642a51` |
| N04 | `scripts/widgets/widget.lua:56–62,124–138,291–309,325–334` | `6e2206ab42c04a1a1f0978f3347bcd3a02acd1a4306da73210662d9a8444b9f5` |
| N05 | `scripts/widgets/button.lua:56–93` | `723b1ab3b21edef123d09decb266c378d0c23af40cc46de6039d99f7f5a028be` |
| N06 | `scripts/widgets/equipslot.lua:27–73` | `2dcd0923937fdbc99978348974b68487d5d16302e2e22227dc05ccd72cb14b4a` |
| N07 | `scripts/widgets/inventorybar.lua:398–447` | `0218e8d4f7e4ab3f5a84644ec43d4c9224f85e1c93dc910f1f3befc146cff27f` |
| N08 | `scripts/networkclientrpc.lua:1838–1853,1885–1888` | `2cd54f3524cad4892232fb4a41c05d34a41314a3a65e606356ba243d770163c0` |
| N09 | `scripts/components/equippable.lua:1–3,25–53` | `afa5d4d0c26c216a20834bcd844660fbefc45517360e6150076660556fcdcf52` |
| N10 | `scripts/components/equippable_replica.lua:1–20` | `3326daa0b1e0528b4fc2e72dd56293aefa52f13573150c70c35ef7072acbe0ea` |

M 路径前缀为 `代码与测试/Iluneth/`；T 路径前缀为 `代码与测试/重构记录/`。T 的断言是测试设计，只有 T02 自带历史结果；其余运行与缺失依赖限制见正文。

| ID | 前缀后的包内路径与行 | 文件 SHA256 |
|---|---|---|
| M01 | `modmain.lua:1–12` | `bc2fa5b15881f52c23f1653901e37f72348ab79fdaeb4fea5d13dfc11cf10cff` |
| M02 | `modservercreationmain.lua:1–9` | `8a297378279ade4cf18ad9b45af5179818c471106040b9cd90e60c165ecbc007` |
| M03 | `main/iluneth_game.lua:1–37,61–69` | `3c98086e2cd5449e76a3eabfa570b872ae3985abe6aa27c25ba5d32dfe31724f` |
| M04 | `scripts/iluneth/reset/candybag.lua:23–35,172–185,230–239` | `73b75c997a5e838bd1d374422a3413efe3192dcd5a937a33c000643a4acd7298` |
| M05 | `scripts/iluneth/armor_visibility_ui.lua:1–74` | `412eaee2af9159be663533c53e47dc174d7750da5993cc0acdab48b9ee504a82` |
| M06 | `scripts/postinit/iluneth_armor_visibility.lua:1–95` | `a49655a24470e8325666e9d6b1c67512aeb7e4dd916d3de1d6cccc92a6fcc3bb` |
| M07 | `scripts/components/iluneth_armorvisibility.lua:1–139` | `29f6e3fb94a4e397d02bf063aa7e950c5c0e7a7947cf3e5e1d8008c48e4a433d` |
| T01 | `20261104_入口与外观恢复/entry/test_entry.py:1–61` | `4eb055a3c6d520954a9d6900748b3d41baacb7bb14ce7e8080b45278d1339916` |
| T02 | `20261104_入口与外观恢复/entry/result.json:1–57` | `0193d526627a3398540eec22a0de803a6dbbffd0b3e60731333f807257eb5781` |
| T03 | `20261102_糖袋客户端崩溃/test_client_replication.py:1–110` | `e27e3a93fd216951130d63eab9c85e1d7879769aa70dafc6c91330f6cf37e524` |
| T04 | `20261104_实机反馈修复/button/test_button.py:1–55` | `714b051443d4097435f45eb4d42733a279f18bef67094904bb1d134f425a770c` |
| T05 | `20261104_入口与外观恢复/armor/ui_toggle_contract.lua:1–123` | `5dfce9d748e000469a321e569896e40955ff849ce5961fa4490b56e572024f04` |
| T06 | `20261104_入口与外观恢复/armor/native_toggle_restore.lua:1–53` | `2db5788a8ed39131964f53b09121d3662329bed887730aa483103920394887e7` |

R 的包内路径统一为 `运行证据摘录/<运行ID>.json`。下列原日志行号来自摘录的定位声明，完整 manifest/log 未附，本轮未独立核验原件或重跑。摘录文件 SHA 与运行身份分别保留；成功不能覆盖另一运行的失败。

| ID | 运行ID；摘录报告结果；原日志选行 | 摘录文件 SHA256 |
|---|---|---|
| R01 | `e719faa6d571496e9f90da85be3c9415`；通过；757,758,763 | `04e4729d649ba221227eecb2b5385a87b5fa28f570512e311335bc77bbdb6bee` |
| R02 | `ecb49790b2614b5d9cb4b72197a4cf5a`；通过；806,807,808,813 | `361986f0d5bc818e664862a57deeae6b456452810eb2227494c1cd16cf99205f` |
| R03 | `dfbff5afbfe64239804b66731fa28257`；失败（done=false）；886,887,888,890 | `a33e7ef3974638999fec4e476f0822ba0848f8a24b5d66569281a8e61bce9c56` |
| R04 | `d0895866f66d4689abff21e905c7ae15`；通过；797,798,799,802 | `3dad1b58df9fdbe887463f38e71bab2a54050fb22ce88ac9e1f4f7f3b9b706ce` |
| R05 | `fac6049a6c0c4fe690f16f5af3eda817`；通过；894,895,896,897 | `abda7f089e710126b6d096eed33186509150ce9d44707e77cd78838ce48cc9a7` |
