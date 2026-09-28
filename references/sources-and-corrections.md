# 来源、可信度与纠错范围

本技能参考 [atjiu/dstmod-tutorial](https://github.com/atjiu/dstmod-tutorial) 等开发资料，并对相关原版接口和工具进行核验。旧教程不等同于当前游戏 API 规范。

测试工具的历史来源包括 [dst-modtest](https://github.com/Zechariah0121/dst-modtest) 与 [dst-ai-scripting](https://github.com/lw-0x4eb1a/dst-ai-scripting)。当前辅助脚本实现直接 ZIP 读取、AST 声明检查与隔离专服测试；这些来源说明不代替运行验证。

技术事实优先核对合法安装的游戏与官方 Mod Tools；本仓库不分发它们的源码、资源或二进制。工具与参数的公开参考包括 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)、[Klei 专服命令行说明](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/) 和 [FFmpeg 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)。具体调用以当前安装版本的帮助和相关游戏实现为准。

## 材料如何进入新规则

| 分类 | 采用方式 | 例子 |
|---|---|---|
| 仍可用 | 保留概念，更新检索入口与边界 | Component/Replica 分工、WorldGen 的 room/task/layout |
| 需要修正 | 更正签名/端别/时序并提供原版定位 | Client RPC 没有隐式 player；实体与组件 OnSave 不同 |
| 有更合适做法 | 说明适用条件，以维护成本和实测结果选择 | 局部控件拖拽替代全局 FollowMouse 覆盖；源码直读替代旧缓存 |
| 暂未验证 | 不写成执行要求，记录验证入口 | 旧附件工具运行兼容、部分引擎接口、真实客户端画面/听感 |

资料读过不等于其全部行为已在游戏中运行。教程中的 API 列表只用于定位，未能从当前 Lua/工具文档确认的引擎绑定不直接标为不存在。教程截图作为历史步骤示意，不冒充本次实机截图；不逐张重新验收其画面。压缩包只检查清单、相关文本/结构和 Lua 语法，没有运行附带旧 EXE/DLL。

## 高影响纠错索引

| 旧说法/做法 | 新规则的维护位置 |
|---|---|
| env 代理必须、pcall 全禁、scripts 下 GLOBAL 一律错 | core-lua-hooks.md |
| modinfo 赋值末尾逗号、GetModConfigData 第二参是默认值 | core-lua-hooks.md |
| PrefabFiles/文件/prefab 名三者必须相等 | entities-components.md |
| 主组件与 replica 方法混查、net_string 可以 set table | networking-rpc.md |
| Client RPC 回调首参 player、namespace 必然等于目录 | networking-rpc.md |
| 保存固定组件顺序、所有 OnSave 签名一样 | lifecycle-save.md |
| Widget 无 inst、吞全部 ESC、全局修改 FollowMouse | ui-actions-controls.md |
| aoespell 一定放两端、任意隐形 FX 能当 spellbook 载体 | ui-actions-controls.md |
| 伤害 bonus 的 1.0 表示 +100%、planardamage:DoDelta | combat-buffs-containers.md |
| bank=build=symbol、anim ZIP 必须三件齐全 | assets-animation.md |
| 64×64 atlas 必坏、149 帧必崩、任何动画不超过60帧 | assets-animation.md |
| ktech 不能生成 XML、autocompiler 全面禁用 | assets-animation.md |
| 固定采样率/声道/压缩才兼容、FSB5 一定不能用 | audio-particles.md |
| 同名 Mod 可直接复用、脚本 return 就可判成功 | testing-release.md、三个 scripts |
| 离线端口永远10999、用猜测端口配置后杀别的进程 | environment-tools.md |
| PushEvent 全部下一帧、GetAttacked 传 electric 自动加倍率 | spells-and-custom-stats.md |
| 每隔 1 世界单位灌溉即每格加一次、睡眠原函数后无条件恢复 | spells-and-custom-stats.md |
| 自定义属性必须使用 Class setter、构造中从 components 取回自身 | spells-and-custom-stats.md |
| 项目料理 helper 当原版 API、AddCookerRecipe 自动建实体和调味 | cooker-dishes.md |
| 17 个台词表等于全部角色、强制三目录或固定图集 | cooker-dishes.md |
| 手持必须 BUILD_90s_90s、整包搜哈希就证明符号存在 | character-and-equipment-art.md |
| 固定模板帧数/画布适合所有角色、删除整个 anim 强制编译 | character-and-equipment-art.md |
| 多图集必须正方形、所有素材可用同一抠图与锚点算法 | animation-recipes.md |
| 专服打印即音效通过、全部 GUID 可无差别替换 | audio-particles.md |

公开的检查范围、工具回归结果及未覆盖内容见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。各专题保留相关源码文件/函数定位、适用条件与验证边界，供读者在自己的合法安装中复核。

主参考引用当前源码的相对文件名和函数名，行号是该次快照的定位辅助；源码哈希见 [environment-tools.md](environment-tools.md)。安装更新后重新查证，不能把本技能的新结论变成永不过期的铁律。

## 后续使用范围

统一入口按需加载内部专题，不再维护旧专项技能的独立规则。核验范围是两份通用技能、七份专项技能及列明材料，没有覆盖所有社区技能，也未证明任意游戏版本都适用。新的游戏数值和美术决策仍由项目作者决定，不能从旧项目例子自动继承。
