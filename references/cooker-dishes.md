# 新增与维护锅料理

用于完成一道料理从设计、注册、调味、图像到验证的全过程。先读当前 `cooking.lua`、相近配方和 `prefabs/preparedfoods.lua`；料理判定基础见 [物品与料理](items-food-plants.md)，实体骨架见 [Prefab 与组件](entities-components.md)。本页不规定料理数值、画风、项目目录或角色台词数量。

## 1. 建立料理合同与变更清单

一次确认未决定的项目：内部名称与显示名；允许的锅；原料数量及生/熟/干替代；优先级与同档竞争；三维、食物主/副类型、特殊食用效果；烹饪和腐烂时间；是否支持调味；语言与图像表现。已有明确需求不重复询问。

先列正例、反例和应保留的竞争配方，分别在普通锅与便携锅判断。`names` 使用 `cooking.lua` 规范化后的食材名，`tags` 是累计值；具体食材个数与标签值不是同一个条件。未出现的字段可能为 nil。`AddIngredientValues` 会替换已有食材标签，不能为了新料理顺手清掉原版属性。

盘点项目实际模块，不要求创建固定的 `recipes.lua`、`atlas.lua`、`strings_cn.lua` 或调味文件。旧项目中的 `AddModCookerRecipe`、`MOD_FOOD_RECIPES`、`MOD_FOODS`、`SHARED_ANIM_DISHES`、`MOD_DISH_QUOTES` 都是项目封装/数据表，**不是原版公共接口**；遇到它们先读定义、调用方和初始化顺序，不能搬名称就假定可用。

尽量以一份已确认的数据定义基础料理，供配方和 prefab 构造读取，再派生调味数据。既有项目必须多表维护时，逐字段核对并记录映射，避免只改配方提示而没有改变实体数值。生成变体时复制所需嵌套表，避免意外修改基础数据。

## 2. 配方注册与实际消费者

在 Mod 环境中调用 `AddCookerRecipe(cooker_name, recipe)`。这个包装已传入 mod 标记；不要绕过它，把料理伪装成官方食物。按需求分别注册 `cookpot`、`portablecookpot` 等真实锅名；是否参与 `archive_cookpot` 需明确。注册配方不会替你创建产品 prefab。

| 数据 | 必须核对的行为 |
|---|---|
| `name` | 与实际注册的产品 prefab 对应；只有项目 helper 明确处理时，表键才能代替此字段 |
| `test(cooker, names, tags)` | 返回此配方是否进入候选；读懂原料别名、缺失字段、准确数量和排除条件 |
| `priority`、`weight` | 先保留最高 priority，再按 weight 抽取；明确给正数 weight，不能靠缺省分支兜底 |
| `cooktime` | 是 `TUNING.BASE_COOK_TIME` 的倍率，实际还乘锅的 `cooktimemult`，不是直接秒数 |
| `perishtime` | 配方影响烹饪的新鲜度计算和锅内变质；实体的 perishable 也必须读取相应设计 |
| `cookpot_perishtime` | 锅中成品变质时间的可选覆盖；不自动改变取出后实体的保鲜时长 |
| `health`、`hunger`、`sanity`、`foodtype` 等 | 配方与图鉴数据不会自动写入任意自定义 prefab，需由该 prefab 构造实际应用 |
| `overridebuild`、`overridesymbolname`、`potlevel` | 供锅内成品显示；独立检查拾取后实体的 bank/build/symbol，不能以锅内显示正常代替 |
| `cookbook_atlas`、`cookbook_tex`、`no_cookbook` | 按实际图鉴需求配置；默认图像名为产品名加 `.tex`，图集可回退库存注册 |

原版数据文件最后会补齐 `name`、`weight` 等字段；`AddCookerRecipe` 本身没有替任意 Mod 配方做同样的补齐。当前抽取分支直接使用 `candidate.weight`，省略它可能运行时报错。

腐烂时长按已批准的天数使用当前 `TUNING.TOTAL_DAY_TIME` 或适当的 TUNING 常量，别从旧样例继承 `10 * 480`。当前 `FOODTYPE` 不只有 VEGGIE/MEAT/GOODIES，也没有 FISH；食材 `fish` 标签不等于可食组件枚举。怪物副类型是否保留属于饮食设计，不能为消除某角色限制擅自改掉。

## 3. 产品实体与资源接线

以当前 `prefabs/preparedfoods.lua` 的构造顺序为参照：公共动画、必要 tag、网络与浮水设置 → `SetPristine()` → 主客端分离 → 权威端的 edible、inventoryitem、stackable、perishable 等。实际用途决定是否保留可燃、交易、诱饵等原版行为。`MakePreparedFood` 是该文件内部局部函数，不能当成可从 Mod 直接调用的导出接口。

`PrefabFiles` 填实际 prefab 模块路径；一个模块也可返回多个 prefab，不必强制每道菜及每种调味各建一个文件。声明并加载新增动画、图集与 TEX；沿引用检查依赖，不机械要求所有资源同时在 `modmain.Assets` 与 prefab 中重复声明。

**独立图集是资源组织选择，不是新增料理的引擎要求。** 保留“不要破坏已发布共享资源”的经验：先识别该资源的使用者，保留可重编源工程；选择扩展共享 build 或新增 build 后，验证受影响的旧菜。只有项目明确冻结共享包时才保留该项目限制。

- 复用原版 `cook_pot_food` 的 bank/idle 与换符号路径时，新资源可只提供 build 和图集；不强行制造 `anim.bin`。如果料理确实有独立动作，则检查相应 bank、animation 与完整依赖。
- 普通锅/便携锅使用 `recipe.overridebuild` 和 `recipe.overridesymbolname or product` 覆盖 `swap_cooked`。用自定义 symbol 名时，这个字段只解决锅的调用；自己 prefab 的 `OverrideSymbol` 仍要对应真实符号。原版食物构造默认使用 `basename or name`，没有自动消费该覆盖字段。
- 库存图标链条为 TEX/XML Element → `RegisterInventoryItemAtlas(atlas, image_with_tex)` → inventoryitem/replica 查询；XML Texture 文件名不必等于 Element 名。图鉴默认也查询此注册，避免只给实例设置 atlas 而遗漏静态图鉴路径。
- 64×64 库存源图可作常见起点，200×132 地面图、固定内容范围、固定缩放和颜色倍率都是旧项目美术参数，不是通用标准。保持 alpha，不能直接按白色阈值删除白色主体与高光。

图像处理、当前工具发现、DMT 预览和 ZIP 校验沿 [图像与动画](assets-animation.md)、[DMT 工作流](dst-mod-tool.md)、[工具安装](tool-bootstrap.md) 执行。没有强制的 ComfyUI 模型、端口或出图后处理流水线。官方编译器报缺少 `animation.xml` 时，应定位输入工程、导出日志与当前工具契约；旧文档“第一次故意失败→手写固定矩阵 XML→再编译”的补丁不作为通用流程。也不要为了改变时间戳或压缩算法无条件重写已有效的 ZIP。

## 4. 调味是单独的完整链路

需要支持调味时，同时完成：调味站接受食物 → 变体配方 → 变体 prefab → 食用效果 → 图像和名称。只添加 `preparedfood` tag 不足以完成这条链；当前调味站以该 tag 和非 `spicedfood` 判断基础菜准入。

对照 `spicedfoods.lua` 与 `prefabs/preparedfoods.lua` 的分工：

1. 为所支持的香料派生变体数据，包含独立 `name`、基础菜 `basename`、香料 `spice` 与判定；注册到 `portablespicer`，并确保产品 prefab 已存在。默认原版生成循环仅处理其列出的基础表，不会自动扫描任意 Mod 菜。
2. 保留基础菜数值、食用回调、依赖和图像引用，再按相应香料语义叠加。蒜/糖/辣椒的 buff、辣椒温度变化及盐的读取链以当前原版为准；不能把所有香料都当成直接乘三维，也不能用香料回调覆盖基础菜效果。
3. 变体沿原版添加 `spicedfood`，设置 edible 的 `spice`，使用基础菜标识处理检查描述和食谱记录。需要餐桌等显示兼容时同时追踪 `food_basename`、`food_symbol_build` 的消费者。
4. 图像通常复用基础菜库存图作为 `inv_image_bg`，叠加香料图标；地面表现复用 `plate_food`、`spices` 和基础菜符号。注册基础图集并在两端检查，不能为每个变体盲目复制一份相同 TEX。
5. 名称沿原版香料名称模板组合基础菜显示名；验证各语言的组合结果和基础菜台词回退。

`GenerateSpicedFoods` 虽在原版模块中定义，但会写入该模块持有的全局调味结果表，且生成过程带官方数据假设；它不是 `modutil` 暴露的独立注册工厂。读清副作用后再决定项目接入方式，不靠改原版表、全局函数或硬编码“料理总数”完成新增。

## 5. 名称、描述与语言

- 显示名使用 `STRINGS.NAMES[upper_prefab]`。
- 检查台词使用 `STRINGS.CHARACTERS.<角色表>.DESCRIBE[upper_prefab]`，默认回退 `GENERIC`。`STRINGS.DESCRIBE` 不是这条原版检查链的入口；若旧项目通过 helper 转写它，要保留实际转写证据。
- `STRINGS.RECIPE_DESC` 服务制作配方说明；只有锅料理并不因此必须新增制作菜单描述。本篇“图鉴”指食谱图鉴（Cookbook）；先确认项目所指系统，若还要求 Scrapbook，另查其注册与发现链，不能把食谱图鉴接通当作所有图鉴都已支持。图鉴消费的数据应沿其 UI 查证。
- 2026-09-27 基线中 `DST_CHARACTERLIST` 有 19 项（含隐藏 `wonkey`），而 `STRINGS.CHARACTERS` 有 17 个基础台词表（GENERIC 加 16 专属）。GENERIC 来自 Wilson 台词，Wes 走哑剧特殊处理；**台词表项数不是角色总数**。
- 按当前版本的已加载台词表、项目支持范围和实际语言补齐。不要为凑固定数量造不存在的表，不覆盖第三方角色自己的台词；补缺失项时保留已有值。中英双语是支持范围选择，不能仅因旧案例写过就改动项目语言策略。

## 6. 按链路验证并交付

| 层次 | 本次改菜后需要证明的事项 |
|---|---|
| 静态 | Lua 可解析；调用与字段真实存在；所有配方产品可注册；基础/调味数据一致；名称、XML、图像、build/symbol 引用完整 |
| 判定与服务端 | 各锅的正反例、边界食材数量和优先级竞争；同档候选/权重符合设计；真正烹饪、取出、食用、堆叠、腐烂与保存重载 |
| 调味 | 每种承诺支持的香料都能产出实体；基础效果和香料效果各按原版链结算；调味后不会继续作为未调味食物重复进入 |
| 客户端 | 主机与真实远端看到锅内成品、地面、库存、图鉴、名称与台词；有相关行为时检查浮水、餐桌和饮食限制 |
| 发布与同步 | 比较已授权的源码/运行副本，保留用户改动并逐文件核对哈希；版本与变更说明按项目发布策略更新 |

概率判定的测试检查候选与权重本身，单次抽到预期菜不能证明同档竞争正确。语法检查、构造 prefab 成功或无头运行都不能代替客户端画面与远端图鉴验收。完整命令和证据分级见 [测试与交付](testing-release.md)。

同步目标由当前项目与用户授权确定；不预设固定三份目录，不默认覆盖 Workshop 下载副本。交付列出料理合同、改动文件、资源、实际同步目标、验证证据和未验边界，审查结论按项目约定写 `.txt`。没有发生实际发布时，不声称已经更新玩家订阅内容。

## 核验依据

以下为 2026-09-27 当前安装版源码定位；相应文件已逐字节核对安装包，基线见 [环境与源码](environment-tools.md)。后续版本仍需重查定义与消费者。

| 主题 | 源码入口 |
|---|---|
| 配方注册、食材别名、候选 | `modutil.lua:636-653`；`cooking.lua:9-29,46-68,178-228,238-287`；`preparedfoods.lua:1098-1104` |
| 时间、新鲜度、保存与产出 | `components/stewer.lua:75-99,130-177,203-261,276`；`tuning.lua` 的 `BASE_COOK_TIME` / `TOTAL_DAY_TIME` |
| prefab 与调味 | `prefabs/preparedfoods.lua:7-179`；`spicedfoods.lua:17-83`；`containers.lua:425-429` |
| 香料与基础食用效果 | `components/edible.lua:88-142,184-197`；`tuning.lua` 的 `SPICE_MULTIPLIERS`；`prefabs/player_common_extensions.lua:919` |
| 锅内符号、调味站符号 | `prefabs/cookpot.lua:105-125`；`prefabs/portablecookpot.lua:120-139`；`prefabs/portablespicer.lua:135-156` |
| 图集与图鉴 | `simutil.lua:658-699`；`modutil.lua:954-957`；`widgets/redux/cookbookpage_crockpot.lua:497-522` |
| 台词与角色范围 | `strings.lua:15579-15598`；`stringutil.lua:364-413`；`constants.lua:442-463,2022-2043` |

本次整合核实的是文档和源码合同，没有制作新料理、美术编译或实际开服验收。具体新增料理仍按上表执行其真实验证。
