# HUD、输入、动作与状态图

适用：徽章、面板、快捷键、拖拽、法术轮盘、角色动作和预测。专服无客户端 UI；组件的权威执行与客户端展示分别核验。保存/清理见 [lifecycle-save.md](lifecycle-save.md)，RPC 见 [networking-rpc.md](networking-rpc.md)。

## 复用 Widget 与 Screen

基础类由 `require("widgets/widget")` 等返回；继承后调用父类构造。Screen、Widget、TextEdit、ImageButton 都显式引入需要的模块，不依赖教程省略的全局。面板优先检索 `widgets/redux/templates.lua` 的 `RectangleWindow/ScrollingGrid/StandardButton`，核对当前参数与原版调用者。

`Widget` **有 `self.inst`**，构造时创建带 UITransform 的 EntityScript。`self.inst:DoPeriodicTask` 可以使用；Widget 默认把这些任务切到静态时间，暂停时是否更新由 `UpdateWhilePaused` 控制，游戏逻辑计时则用其 `DoSimTaskInTime/DoSimPeriodicTask` 或适当的玩法实体。

教程为了更新时钟单独 `CreateEntity()` 且不保存/移除，不适合可重建 HUD。任务挂所属 Widget 的 inst，并在功能提前停用时取消；Widget `Kill` 会停止更新、移除子控件和自己的实体。挂在 player 上的任务不能靠 `img.parent == nil` 判断已 Kill：当前 Kill 不保证将 parent 字段置 nil。

面板打开保持单例，重复打开先聚焦或复用；关闭走自己的 Close/PopScreen 路径，清空 HUD 引用、输入 handle、拖拽及监听。不要通过覆盖整个 `CreateOverlays/OnControl` 抹掉原版；窄包装并保留参数、原函数返回值和事件是否已消费的含义。

颜色常用 0–1 分量；不要照抄 `{255,0,0,1}` 当成标准 UI 色值。资源 XML/tex 路径先结构校验，再实机看字形、缩放和布局。

## 徽章初次同步、死亡与复活

绑定数据源时主动刷新一次，再监听 dirty。owner、Replica、classified 或网络引用可能分阶段就绪，按其实际初始化事件补绑定；不默认用每帧轮询隐藏初始化错误。`Badge:SetPercent(percent, max)` 传入实际最大值，核对数字显示与百分比。

幽灵 HUD 走原版链：`player_classified.isghostmode` → `OnGhostModeDirty` → 玩家 `SetGhostMode` → Controls/StatusDisplays。自定义三维条可以窄包装 `StatusDisplays:SetGhostMode`，在调用旧方法后按 `self.isghostmode` 切换，再补初次刷新。不能只在远端监听服务端 `ms_becameghost/respawnfromghost` 就期待自动收到事件。

初始快照还有一个时序细节：StatusDisplays 构造时先 `SetGhostMode(false)`，而 PostConstruct hook 在构造后才安装。首次刷新不能盲信这个临时 false；从本地 owner 已就绪的 `player_classified.isghostmode:value()` 读当前复制值，再结合自己的业务状态显示。classified 尚未就绪时按原版实际就绪链补绑定，避免永久误显示。这里指远端客户端上的本地玩家 HUD；观察其他玩家时，不能假设他们的私有 classified 对观察者同样可读，需要另查可见数据来源。

`respawnfromghost` 是复活请求/流程入口，不是死亡事件。复活按钮涉及双方代码，不能称“只服务端安装就有客户端按钮”；还必须校验玩家状态、可用次数/消耗/权限，并处理 HUD 尚未建立和服务器拒绝。不需要为原版已经同步的 ghost 状态再另造一套广播 RPC。

区分请求与完成：当前 `player_common_extensions.lua:427-430` 的成功流程写入 ghost 状态并发 `ms_respawnedfromghost`。需要“复活完成后”结算时追这条服务端链；完成事件仍不自动跨网，客户端显示继续读复制状态。

## 快捷键和控制器

- 使用当前 `constants.lua` 的 `KEY_*`、`CONTROL_*`，避免维护一份裸数字表。
- 客户端注册前排除 dedicated；回调检查本地玩家、HUD、有效玩法 Screen、聊天/输入框/控制禁用和角色状态，按功能决定是否吞键。
- ESC/取消仅在自己面板或瞄准状态活跃时消费，其他情况交回原版；未按下与抬起两阶段不能混淆。
- 保存 `TheInput:AddKey*Handler/AddControlHandler` 返回值，按所属 HUD/功能生命周期移除；反复激活不叠加注册。
- 键盘外还有手柄焦点流、确认/返回、断开手柄和鼠标拖拽，涉及这些入口时须实测。
- 输入限制不替代服务端 RPC/动作校验。

## 坐标与拖拽

先记录 Screen 像素坐标、Widget 父级局部坐标、anchor、比例缩放、父级变换与 HUD scale。`GetScale()` 返回累计缩放的 **Vector3**；`GetLooseScale()` 返回自身三个数值。

当前 `Widget:FollowMouse` 直接把屏幕坐标喂给 `UpdatePosition`，只适用于坐标系匹配的挂载方式。嵌套且缩放的控件需在自己的控件里做坐标变换，不能全局替换所有 Widget 的 FollowMouse/anchor 方法。简单未另设 anchor 的子控件可从“屏幕点减父级原点，再除父级累计缩放”推导；有其他锚点、变换时另验，不宣称一个公式通用。

`widget.OnMouseButton = function(self, button, down, x, y)` 中第一参是 self，不是 StandardButton 额外传入的文本。只处理自己消费的拖拽按键，其余调用旧处理；在松键、失焦、关闭与 Kill 时结束拖拽。保持按下时的鼠标偏移，避免控件突然跳中心；按要求保存归一化/局部位置，换分辨率时夹回可视区。

`TheSim:GetScreenPos` 的输出能否直接 SetPosition 取决于挂载层坐标。旧 skill 断言“任何情况下都无需换算”和“原版减半屏一定错”均不成立。不同 anchor 的原版公式可能各自正确；实测窗口比例、HUD scale、镜头/实体移动和边缘位置。

## 动作完整调用链

组件动作收集 → BufferedAction → 角色 ActionHandler → SG 状态 → 客户端 `PerformPreviewBufferedAction`/服务器 `PerformBufferedAction` → Action.fn → 组件业务。逐段查源，不只改菜单或 Action.fn。

客户端用 tag、Replica、公共组件决定显示/预测；服务端在真正执行帧检查目标、距离、资源、冷却和持有关系并结算一次。进入预测状态前不能清空仍需发往服务器的 buffered action。主机同进程能执行不代表远端路径已走通。

`busy` 是供调用者查询的状态标签，不是不可被打断的绝对屏障。SG 事件、死亡、取消、强制切状态都可能中断；`onexit` 只能撤销本状态拥有的物理、控制、模型、音效和临时 tag，不能把刚恢复的人形又改回旧 Boss build。

## 轮盘与 CASTAOE

以当前 `prefabs/abigail_flower.lua`、`prefabs/pocketwatch.lua` 等最近似物品为起点：`spellbook` 与 `aoetargeting` 在公共区；花的 `aoespell` 在服务器区。客户端组件动作由引擎复制注册信息，不要求在客户端构造服务器业务组件。

`aoespell:SetSpellFn` 签名是 **`function(item, doer, pos)`**。当前 `CanCast` 对有 spellbook 的载体检查：inventoryitem 的 GrandOwner；或 isplayer 且自身就是 doer；其余无物品、非玩家的 spellbook 载体返回 unsupported。不能照旧 skill 声称任意隐形 FX 法典原生可用。

`spellbook:SelectSpell` 的 onselect 参数是书/载体本身，不是玩家；客户端从合法本地 owner 上下文取玩家，服务器按请求者/持有关系取，不在共享服务端代码里盲用 ThePlayer。

当前 `GetGroundUseAction` 对 reticule.inst 是否为玩家有特殊分支。先追传入 position、鼠标/手柄分支和 BufferedAction 创建点，再设计载体；“reticule 必须永远挂非玩家”不是完整规则。

施法距离跟踪 aoetargeting 的 range 与 picker 传给 BufferedAction 的实际 distance，不只改 `ACTIONS.CASTAOE.distance`。圈合法性、海面/平台、落点、业务范围应一致；`SetAlwaysValid(true)` 只是原版地图检查参数之一，不代表资源/权限或最终技能目标总合法。

## 窄 hook 与上值

优先公开回调、组件属性/方法或限定 prefab 的 postinit。包装时保留 self、全部参数、全部返回值及原副作用的先后顺序；同一实例/树重建要有正确幂等依据，不永久布尔挡住新对象。

upvalue 是函数捕获的词法局部变量，可能是数据而不只是函数。仅当公开扩展点不足且当前源码可证时使用 `debug.getupvalue/setupvalue`；查找循环遇到 name=nil 必须结束，找不到则禁用该补丁并报告。不得无限查找一个原版可能改名的上值，也不按固定索引盲改共享闭包。

## 当前源码检索入口与验证

- `widgets/widget.lua:1-44,56-62,325-342,530-558`：inst、时间、Kill、跟随鼠标和缩放。
- `widgets/statusdisplays.lua:SetGhostMode`；`prefabs/player_classified.lua:OnGhostModeDirty`；`prefabs/player_common.lua:SetGhostMode`：ghost HUD。
- `input.lua:AddKeyDownHandler/AddControlHandler`；`widgets/redux/templates.lua`：输入与模板。
- `entityscript.lua:PerformPreviewBufferedAction/PerformBufferedAction`；`components/playercontroller.lua:GetGroundUseAction/RemoteBufferedAction`；`stategraphs/SGwilson_client.lua`：预测链。
- `prefabs/abigail_flower.lua:311-358`；`components/aoespell.lua:11-70`；`components/spellbook.lua:80-105`；`componentactions.lua:1990-2017`：轮盘、权限和动作注册。

Lua 契约测试可验证调用顺序、清理和 preview 回调次数；不能证明实际传输或动画。发布前按改动覆盖主机/远端、预测开关、重连/幽灵进入、鼠标/手柄、窗口与 HUD scale、目标在动画中被删、服务器拒绝和重复打开关闭。
