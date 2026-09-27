# DST Mod Tool：文档编辑、脚本接口与视觉验收

这是本技能的 DMT 工作流参考页。2026-09-27 核验环境中，`DST Mod Tool.exe` 的文件版本/产品版本为 **1.1.13**，`script --help` 返回完整 Lua Scripting API Guide。下述行为来自该版本帮助；更新后先重新核对，不能以本页代替未来版本文档。

适用：`.dmt` 工作区、SCML/ZIP 资源导入、符号和动作批量编辑、PNG/GIF 预览。不替代 DST Lua 行为、资源加载和实机联机验收。已知 CLI 不等于已执行全部导入、导出和编译能力；本次只读审查没有修改现有 DMT 工作区。

尚未安装 DMT 时，先按 [工具安装与首次验证](tool-bootstrap.md) 核对作者发布页、系统与安装授权，再回到本页使用当前程序的实际接口。不要把本页中的历史版本当作固定下载目标。

## 每次操作先获取接口与状态

```powershell
& $DmtExe script --help
& $DmtExe script --file $AbsoluteLuaFile
```

Windows GUI 子系统程序的输出可能需要重定向捕获。启动后台辅助进程时隐藏窗口；现有用户工作区不得擅自替换。`--file` / `--stdin` / `--text` 三种来源只选一种，复杂内容优先文件。文件路径用绝对路径，Lua Windows 路径用 `[[C:\path\file]]`。

先运行只读脚本：

```lua
print("revision", tool.document_revision)
print("path", tool.document_path)
print("builds", #doc.builds)
print("banks", #doc.banks)
for _, bank in ipairs(doc.banks) do
    print("bank", bank.name, "animations", #bank.animations)
end
local selected = tool.selection.animation
if selected then
    print("selected", selected.name, #selected.frames)
end
```

名称不确定时输出候选，确认目标后用 `find` 和 `assert`。不要凭文件名、集合位置或旧导入的 ID 猜对象。

## 文档与集合

```text
doc.builds → Build.symbols → Symbol.frames → SymbolFrame
doc.banks  → Bank.animations → Animation.frames → AnimFrame.elements → Element
```

- 集合是从 1 开始的只读有序视图，支持 `ipairs` 和 `#`，不支持 `pairs` 或 `collection[i]=...`。
- 结构修改走 `add`、`remove`、`move_to`、`move_to_parent`。名称 `find` 不区分大小写；symbol frame 的 `find(num)` 查帧编号，不是下标。
- 节点 ID 在当前 DMT 文档保存/加载、编辑、撤销中稳定；导出/重新导入 SCML/BIN 后不能当作同一 ID。
- 删除或移动集合项时用倒序索引；对象删除后不能再访问。
- Symbol 按名称、SymbolFrame 按 num 排序，重命名/改编号后位置可能改变。需要对象时保留 handle 或重新 `find`。

| 对象 | 例举操作 |
|---|---|
| Build | name、hidden、clone、move_to、remove_unused_symbols |
| Symbol | name、hidden、clone、move_to_parent、remove_unused_frames |
| SymbolFrame | num、duration、pivot_x/y、replace_image、export_png |
| Bank | name、clone、move_to、transform、anti_follow |
| Animation | name、frame_rate、clone、move_to、reverse、append、crop、transform |
| AnimFrame | set_bounds、clone、move_to、transform、export_png |
| Element | set_reference、set_layer、set_transform、绘制顺序方法 |

这里只列用途；参数/选项范围先查该版本帮助。Element 的 `draw_index==1` 是最前方，`place_above` / `place_below` 要求在同一 AnimFrame。

## 事务与失败处理

- 一次成功 Lua 运行中的 Document 修改作为一次撤销提交；语法/运行/资源/限额错误发生在提交前时不应用修改。
- `tool` 控制、保存、图片导出是延迟命令，在 Document 提交后按顺序执行。失败后停止后续命令，**不会回滚已经提交的文档和此前成功的命令**。
- `tool:undo()` / `redo()` 单独运行，不能与 Document 修改混合。
- `tool:open_document(path)` 替换工作区，是终止型命令，单独调用。它不是 `doc:import_resources`。
- `tool` 的部分字段在脚本里反映排队命令的本地投影；返回的 `report.final_tool_state` 存在时才代表这些命令执行后的真实 App 状态。只读运行通常没有该字段。
- 同时只运行一个请求。遇 `busy` 等待后重试；超时不代表操作未执行，不盲目重放会叠加的编辑。先读状态和报告。

所有外部请求至少检查：

1. `response.type == "script"`；否则是 IPC 层错误。
2. `report.ok`、`report.error`。
3. `report.output` 是否符合预期对象与数量。
4. `report.document.changed`、前后 revision。
5. 每条 `report.tool_results` 的 `ok`；必要时 `final_tool_state`。

不要仅凭退出码、revision 变化或一句“成功”断言保存/导出完成。

## 受控导入与编辑

```lua
local bank = assert(doc.banks:find("my_bank"), "Bank not found")
local animation = assert(bank.animations:find("idle"), "Animation not found")
doc:set_label("调整 idle 的播放速度")
animation.frame_rate = 24
```

该代码仅示范 API，24 不是默认设计值。修改动作时长、画面比例和循环方式需要依据用户要求。

`doc:import_resources({absolute_paths}, options)` 支持该版本帮助列出的 ZIP、DYN、BIN、SCML、GIF、PNG、Spine JSON、PSD，返回新建 build/bank handle。不扫描目录、不接收 `.dmt`。Spine 颜色采用 `spine_colors="bake"` 或 `"ignore"` 时要明确选择；不要依赖不可见弹窗。

需要覆盖 `SymbolFrame` 图像用 `replace_image`。批量替换符号/层用 `doc:search_replace_elements`，按 help 提供 scope/rule。正则模式需要的字段不同，不凭普通搜索示例扩展参数。

变换后的动画 bounds 可以通过 `doc:recalculate_collision` 重算；这里是动画文档中的边界数据，**不能当成已修改游戏实体 Physics 碰撞体**。实际碰撞仍需回到 prefab/Physics 核对。

DMT 脚本的 `doc`/`tool`、沙箱权限和 `pcall` 不属于 DST Mod 运行时。不要把 DMT 文件桥或环境用法复制到 modmain/prefab/widget；也不要从外部直接改 `.dmt` 或手改运行时二进制来替代受控工具。

## 预览与图像验收

```lua
local animation = assert(tool.selection.animation, "Select an Animation first")
local frame = assert(animation.frames[1], "Animation has no frames")
frame:export_png([[D:\preview\first.png]], { max_dimension = 1024 })
```

先导出一张限制尺寸的图并查看；运动连续性需要时再导出序列/GIF。`scale` 与 `max_dimension` 二选一；序列输出要求全新、尚不存在的目录。单帧导出可能原子替换同名文件，使用自有输出路径避免覆盖用户图。

```lua
tool:set_hide_layer("shadow", true)
tool:set_override_symbol("swap_object", "swap_spear")
tool:select_animation(animation)
tool:select_frame(animation.frames[1])
```

这些是预览状态，不是文档修改；DMT 的符号预览映射也不是 DST 三参数 `OverrideSymbol` 原样接口。`select_frame` 传 AnimFrame handle 并暂停；`tool.playback.frame_index` 从 0 开始，集合索引从 1 开始。

取得对应 `tool_results` 成功后，实际打开 PNG 检查朝向、pivot、透明边缘、层级与缩放。生成图像成功不等于画面正确；只看单帧不能声称全部动画连续性合格。

交付资源回到 [图像与动画检查](assets-animation.md)：按完整/build-only/animation-only 类型检查依赖，核对 Lua 中真实 bank/build/symbol/animation，再做客户端验收。DMT 能播放不能证明游戏加载、玩家输入或多人同步正确。
