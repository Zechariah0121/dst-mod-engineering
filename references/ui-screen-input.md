# 小型 HUD 面板的接入选择

需要临时打开、关闭并返回游戏的窗口，可用 `PopupDialogScreen` 配合 `PushScreen` / `PopScreen(instance)`。需要长期显示在 HUD 里的信息块，可挂到本次 `Controls` 的缩放节点，通过自己的刷新函数更新内容。下面的选择与示例属于工程建议。来源事实与具体合同见 [EXP-UI-001～003](../knowledge/research/native-mechanisms/ui_screen_input-57f6e507338a.json)，依据 762172 的静态 Lua。

## 临时窗口用现成 Screen

`PushScreen` 会停用原栈顶、保存它的焦点，再把弹窗挂到 FrontEnd。`PopScreen(instance)` 同时处理栈项、销毁和新栈顶激活。保存焦点有效时，Screen 会恢复它，否则尝试 `default_focus`。因此关闭按钮使用具体实例，窗口字段在 `OnDestroy` 清理，新的默认焦点跟随本次窗口构造。来源 `UI-S01`、`UI-S02`、`UI-S03`、`UI-S06`。

一个按钮的 `PopupDialogScreen` 可明确配置 `controller_control = CONTROL_CANCEL`。模板仅在多个按钮全部未配置映射时，才默认给最后一个按钮添加取消映射。取消闭包在释放时执行，窗口原有 `OnControl` 会先给焦点子控件处理。来源 `UI-S13`、`UI-S14`。

### HUD 鼠标入口的最小示例

这是原创接入示例，可放入 Mod 的客户端呈现初始化部分。示例采用可点击文字打开一个临时窗口，内容与位置均为占位。入口坐标 `(0, -60)` 需要按目标 HUD 布局调整。手柄打开入口的 focus flow 需要结合现有 HUD 导航接线，弹窗本身配置了取消操作。示例引用原版 UI 资源，未执行游戏验证。依赖 `UI-S01`、`UI-S02`、`UI-S05`、`UI-S13`、`UI-S14`、`UI-S23`、`UI-S28`、`UI-S30`、`UI-S31`。

```lua
local G = GLOBAL

if not G.TheNet:IsDedicated() then
    local TextButton = G.require("widgets/textbutton")
    local PopupDialog = G.require("screens/redux/popupdialog")

    AddClassPostConstruct("widgets/controls", function(controls, owner)
        if owner ~= G.ThePlayer then
            return
        end

        local function ClosePanel()
            if controls.example_panel then
                G.TheFrontEnd:PopScreen(controls.example_panel)
            end
        end

        local entry = controls.top_root:AddChild(TextButton())
        entry:SetText("信息")
        entry:SetControl(G.CONTROL_PRIMARY)
        entry:SetPosition(0, -60)
        entry:SetOnClick(function()
            if controls.example_panel then
                return
            end

            local panel = PopupDialog("信息", "在这里显示功能内容。", {
                {
                    text = "关闭",
                    controller_control = G.CONTROL_CANCEL,
                    cb = ClosePanel,
                },
            })
            controls.example_panel = panel

            local previous_destroy = panel.OnDestroy
            function panel:OnDestroy(...)
                controls.example_panel = nil
                return previous_destroy(self, ...)
            end

            G.TheFrontEnd:PushScreen(panel)
        end)

        local previous_kill = controls.Kill
        function controls:Kill(...)
            ClosePanel()
            return previous_kill(self, ...)
        end
    end)
end
```

窗口实例存放在当前 Controls 上，重复点击保留这次已打开窗口。弹窗属于 FrontEnd 的 Screen 树，Controls 销毁入口负责关闭自己打开的弹窗。原版或其他流程通过 `OnDestroy` 关闭窗口时，该字段同样会被清空。普通 HUD 按钮继续由 Controls 子树的 Kill 收尾。这个例子只需一个实例字段、一个关闭函数和原有生命周期包装。来源 `UI-S01`、`UI-S02`、`UI-S04`、`UI-S05`、`UI-S07`。

## 保留 Button 的按下与释放

Button 首先分发基类 control，再核对焦点、enabled、selected 与 control 映射。首次按下记录点击状态，匹配释放且此前已按下才调用 `onclick`，失焦或禁用会撤销尚未完成的点击。业务动作放到 `SetOnClick`，可以直接复用这些约定。覆写上层 `OnControl` 时先保留原实现返回的消费结果，自有分支处理完成后返回 true。来源 `UI-S10`、`UI-S11`、`UI-S12`、`UI-S31`、`UI-S32`。

Input 只在 FrontEnd 没有消费 control 时才交给后续 control 处理器，普通 FrontEnd 栈路径把 PRIMARY 映射为 ACCEPT。raw key 通过另一条事件广播路径分发，回调返回值由该事件处理器忽略。快捷键若需要消费控制，应接入适合的 Screen/control 分支，并按当前文字输入与焦点条件处理。已有总线知识可继续复用 `N005-UI-C04`，本轮补充 Button 与模板取消闭包的具体合同。来源 `UI-S08`、`UI-S09`、`UI-S15`、`UI-S16`、`UI-S17`。

Screen 的 control 消费针对本次事件。HUD 的 `HasInputFocus` 还会影响 PlayerController 的玩法门禁。选择模态 Screen 时应验收该窗口打开期间允许的玩法操作，按功能需求确定是否需要更窄的常驻 HUD 面板。来源 `UI-S08`、`UI-S18`，以及既有 `N005-UI-C04`。

## 常驻内容复用现成 HUD 节点

资源数值需要从服务器同步时，参阅[技能资源与 HUD](chain-skill-resource-hud.md)的首次快照、后续变化和 Controls 重建路径。

本地 HUD 的正常创建路径会生成新的 PlayerHud，随后 `SetMainCharacter` 创建新的 Controls。`AddClassPostConstruct("widgets/controls", ...)` 在原构造后取得本次实例及 owner，可把一个小 Widget 挂到 `top_root`、`topright_root` 等适合的节点。对应字段已指向现成 HUD 缩放子节点，原版构造和屏幕尺寸变化会走 `SetHUDSize`。通常只需设置自己的相对位置。来源 `UI-S19`、`UI-S20`、`UI-S21` 至 `UI-S26`、`UI-S28`、`UI-S35`、`UI-S36`。

hook 内直接使用传入的 `controls`。`owner.HUD.controls` 的赋值发生在整个 Controls 构造返回之后，postconstruct 执行时这个字段可能仍为空或仍保留旧对象。这是由当前赋值与包装顺序得到的静态推断。来源 `UI-S20`、`UI-S28`。

每个 Controls 实例创建自己的控件，数据更新直接调用这个控件的刷新函数。订阅事件与首帧 getter 根据实际显示数据选择，现有 `ui-actions-controls.md` 中的 owner/replica/classified 规则继续适用。静态文字可直接设置，只有明确需要逐帧效果时才增加更新逻辑。来源 `UI-S20`、`UI-S28`，以及既有 UI 参考。

需要保留对象的面板可以在关闭入口调用 `ClearFocus` 和 `Hide`，再把焦点交给当前有效的入口控件，重开时按导航设计重新设置焦点。Hide 的显示变化与 Widget 的 focus 状态独立，原版 Controls 隐藏 mapcontrols 时也显式清除已有焦点。来源 `UI-S06`、`UI-S10`、`UI-S12`、`UI-S32`、`UI-S33`、`UI-S35`。

HUD 内容刷新使用功能自己的刷新入口。`SetMainCharacter` 会创建 Controls、添加 owner 监听、初始化覆盖层并可能 Close/Open overflow，它的正常调用方传入刚创建的 HUD。需要同一个 HUD 更换 owner 时，项目应明确旧订阅、旧控件与新绑定的交接。来源 `UI-S19`、`UI-S20`、`UI-S27`。

## 接入后的定向验收

临时窗口或按钮改动，检查开关、按放和焦点交接；常驻内容按实际修改检查刷新或布局。Controls 重建或 owner 交接有变化时，再核对玩家交换或重连后的入口。控制器、文字编辑和自定义快捷键各按项目使用情况检查导航、取消和事件消费。沿用已有证据，检查本次改变的行为即可。本文示例尚未在目标 Mod 中运行。
