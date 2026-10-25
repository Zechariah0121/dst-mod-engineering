# 来源、可信度与纠错范围

开发资料参考 [atjiu/dstmod-tutorial](https://github.com/atjiu/dstmod-tutorial)；教程用于提供线索，接口与行为以当前游戏实现为准。

辅助脚本实现 ZIP 读取、AST 声明检查与隔离专服测试。当前专服测试工具入口为 [scripts/dst_modtest.py](../scripts/dst_modtest.py)，历史来源包括 [dst-ai-scripting](https://github.com/lw-0x4eb1a/dst-ai-scripting)。具体检查能力见 [测试与交付](testing-release.md)。

技术事实优先核对合法安装的游戏与官方 Mod Tools；本仓库不分发它们的源码、资源或二进制。工具与参数的公开参考包括 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)、[Klei 专服命令行说明](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/) 和 [FFmpeg 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)。具体调用以当前安装版本的帮助和相关游戏实现为准。

## 怎样判断资料

| 情况 | 采用方式 | 例子 |
|---|---|---|
| 概念仍适用 | 核对当前实现与适用边界 | Component/Replica 分工、WorldGen 的 room/task/layout |
| 签名、端别或时序有误 | 追查原版定义与调用方 | Client RPC 没有隐式 player；实体与组件 OnSave 不同 |
| 存在多种实现 | 按适用条件、维护成本与实测结果选择 | 局部控件拖拽与全局 FollowMouse 覆盖 |
| 尚无运行证据 | 保留待验证标记与验证方法 | 旧工具兼容、引擎接口、客户端画面与听感 |

Lua 源码或工具文档中未找到的引擎绑定，不能直接判为不存在。教程截图仅作步骤示意；附件的清单、结构或语法检查不能证明旧 EXE/DLL 可运行，也不能代替游戏验收。

## 高影响纠错索引

| 常见误区 | 参考专题 |
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

各专题提供源码文件/函数定位、适用条件和验证方法。行号仅对应引用快照，游戏更新后需重新核对相关实现；整体边界见 [能力与版本限制](../docs/public-limits.md)。

专题中的项目案例用于说明机制，数值与美术效果需由当前项目决定。

## 版本化技术说明

`759671` 的公共 `GetAttacked` 返回、内部攻击入口和 `from_doattack` 与旧快照存在差异；电伤仍需区分 `DoAttack` 与直接受击链。具体行为见 [战斗专题](combat-buffs-containers.md)。不同版本的证据保留各自范围，源码差异不能代替实际游戏验证。
