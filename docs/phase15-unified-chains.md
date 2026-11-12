# 统一读取与四条有限功能链

`v2026.11.12.4` 增加统一ID/API审阅与完整对象续读，并新增4条具名功能链、16项机制API合同。登记总数为300条，分为64基础、13 Native AI、110 Core、113机制研究；机制族共420项 `api_contracts`。数量的范围见[登记说明](native-mechanisms.md)，全库API盘点与源码覆盖率仍需独立确定。

## 通过ID或API读取完整对象

完整九工具中，`get_entry(id=..., projection="reviewer", purpose="review")` 按ID识别四族，`lookup_api(symbol=..., projection="reviewer", family="all")` 统一导航并返回 `results[].followup`。调用方可以从任务或精确符号进入，再读实际合同与来源导航。

命令行入口在包根运行，需要已准备的完整来源环境。

```text
python -B -X utf8 run_kb.py review EXP-CHAIN-SPELL-001
python -B -X utf8 run_kb.py review --api "SpellCaster:CanCast" --max-bytes 24000
python -B -X utf8 run_kb.py review EXP-CHAIN-SPELL-001 --pointer /api_contracts/0 --max-bytes 64000
```

响应中 `objects` 保存完整对象，`complete` 表示所选对象流读取进度，`whole_value_delivered` 表示所选根对象一次交付情况。对象过大时原样执行 `continuation.tool` 与 `continuation.arguments`，其中的cursor绑定记录、原选择和来源环境；也可直接指定pointer选择对象。每页按完整UTF-8 JSON响应计费，`max_bytes` 为1000–64000。必需Scope或完整owner无法交付时保留withheld，上限仍不足时转文件阅读。具体续读、消歧和证据展开见[检索策略](../references/kb-retrieval.md#四族完整对象审阅)。

`review ID` 与 `review --api` 均要求完整来源服务。仅需公开目录导航或公开材料审阅时，可直接使用原有 `find/read`，无需来源准备。公开目录的24000字节上限、局部指针与来源未核验状态继续适用。命令参数见[知识读取](knowledge-integration.md)，来源准备与公开版更新助手见[源码维护](source-compatibility.md)。

## 四条功能链如何使用

从[任务地图](../references/task-map.md)选择本题相近链，再按指南核对已有合同、实际消费者与项目依赖。四条新链均绑定762172冻结源码，保留各自Scope、来源引用、未知和 `research/restricted/hold`。其中最小示例为独立编写，示例数值、失败处理和恢复政策由目标项目确认。

| 功能与登记 ID | 本次接通的有限范围 | 继续核查与验证 |
|---|---|---|
| 主动技能 `EXP-CHAIN-SPELL-001` | 普通yellowstaff鼠标地面空点CASTSPELL，从候选/预测发送到权威执行帧、消费、stafflight退出与组件恢复 | 手柄、轮盘、CASTAOE、地图选点及效果公式另查；重点验证执行前中断、末次移除和磁盘恢复。[主动技能链](../references/chain-active-skill.md) |
| 装备效果 `EXP-CHAIN-GEAR-001` | 普通molehat HEAD成员到classified/PlayerVision/表现提交，连接耗能、卸下、耗尽和正燃料记录恢复 | 异常零燃料记录、全部视野组合、死亡/换角/session及原生画面另验。[装备效果链](../references/chain-equipment.md) |
| 可收起建筑 `EXP-CHAIN-DEPLOY-001` | portabletent_item与portabletent的普通DEPLOY/DISMANTLE、HAMMER、uses交接和稳定形态保存 | 原版收起动画中缺少恢复续行字段；额外状态迁移、生成失败归属、睡眠/燃烧/动画并发及真实返还另验。[可收起建筑链](../references/chain-deployable.md) |
| 阶段生物 `EXP-CHAIN-STAGE-001` | 普通pigman normal/werepig的输入、WereBeast、属性、Brain/SG、回退、卸载和恢复字段 | transform到期、死亡至移除间任务、受伤形态加载顺序待验；特殊猪、玩家变形、技能树和完整Boss另研。[阶段生物链](../references/chain-creature-stage.md) |

新增链复用历史记录时保留原ID、版本与更正。目标Mod实施前，继续独立核对当前源码定义、实际调用方、端别与生命周期，再落实项目数值和政策。具体衔接见[研究如何支持当前开发](../references/kb-retrieval.md#研究记录怎样支持当前开发)。

## 验证状态

四组候选的128处来源文件/范围哈希、38项论断、16项API和24个链路步骤已独立复核；57项Lua 5.1替身检查通过。阶段生物旧示例漏测Mod环境，直接读取TheWorld会失败；已改为回调中的GLOBAL.TheWorld，补入实际CreateEnvironment沙箱回归，撤回旧示例通过结论并登记新审阅绑定。候选源码研究字节未改变。

统一读取的14项适配测试覆盖最终300条ID，服务52项回归通过。根目录336项回归中，333项通过，另3项因并行更新知识文档导致清单暂不匹配，刷新后3项定向复验通过。上述测试集有重叠，不累加为独立测试总数。独立检查遍历300条规范对象流及71个续读页，旧Native AI的13份投影保持原值；6条历史对象流遇到超过64KB的不可分割对象时明确停止并指向文件读取。API导航仍受每条既有路径Top-K最大30和总预算限制，不保证遍历全部匹配。

实际来源数据的只读集成与可执行后续读取已通过，服务环境参数仍为759671，安装游戏来源归档与762172冻结SHA一致。最终新包的新进程CLI与MCP验收另由安装收据绑定，不将既有296条运行根的集成检查冒充新包测试。

| 自写示例 | 实际单分片专服检查 | 最终进程 |
|---|---|---|
| 主动技能模块 | 测试专用Action接实际SGwilson.castspell；提交前中断不扣费且清起手表现，两次提交正确扣费，末次删除装备，生成星体带timer | 1次，退出码0 |
| 装备prefab | 实际库存装备、周期耗能、卸装停耗、耗尽清槽与派生夜视，保留独立强制夜视来源；同一隔离存档重启恢复燃料30且未装备不消费 | 2次，均退出码0 |
| 建筑回调模块 | 测试prefab接实际DEPLOY与PortableStructure，部署/收起/再部署保留uses=5；同一隔离存档恢复唯一稳定结构并能继续收起 | 2次，均退出码0 |
| 阶段生物modmain | 原样修正版在真实Mod环境加载；普通pigman切换两态、重复事件守卫、卸载任务释放；同一隔离存档恢复were状态并能正常回退 | 2次，均退出码0 |

这7个最终进程均正常结束，临时Mod和测试实体已清理，用户存档未使用。早期脚手架及装备运行出现原生线程退出断言，行为断言与退出结果分别保留，未计为整项通过；调整仅限独立端口与测试脚手架的保存回调后等待3秒再关闭。最终结果不证明所有原生退出场景稳定。

测试使用合成服务器角色或具名普通猪，示例与内嵌Lua逐字绑定。原版黄杖完整鼠标/RPC/预测、星体磁盘持久化、原版帐篷收起动画中读档、受伤猪人所有组件加载顺序、真实客户端画面/声音/复制、跨分片和第三方组合仍待验。各指南保留具体排除项。研究正文继续 `runtime_verified=false` 与Coding HOLD；有限示例运行不能提升整条研究准入。公开包仍包含源码准备与更新助手，验证方法见[测试与交付](../references/testing-release.md)。
