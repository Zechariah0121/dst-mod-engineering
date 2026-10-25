"""Bounded task scope: exclusions, implementation guards and rejected inferences."""
import json
import re

if __package__:
    from .request_analysis import analyzed_request, memoized_analysis
    from .relevance_frames import (data_consumption, literal_source_relations,
                                   observer_registration_identity_request, registration_state_request,
                                   request_relations, engineering_relations,
                                   _data_quote_view,
                                   literal_recipient_delivery, literal_recipient_subject)
    from .predicate_grammar import refine_operations, literal_relations, is_factual_absence
else:
    # 文件路径加载也只使用同目录的实现，不借用已安装 Service 或其他候选。
    import importlib.util
    from pathlib import Path
    _analysis_spec = importlib.util.spec_from_file_location(
        '_dst_kb_request_analysis', Path(__file__).with_name('request_analysis.py'))
    _analysis_module = importlib.util.module_from_spec(_analysis_spec)
    _analysis_spec.loader.exec_module(_analysis_module)
    analyzed_request = _analysis_module.analyzed_request
    memoized_analysis = _analysis_module.memoized_analysis
    _frames_spec = importlib.util.spec_from_file_location(
        '_dst_kb_relevance_frames', Path(__file__).with_name('relevance_frames.py'))
    _frames_module = importlib.util.module_from_spec(_frames_spec)
    _frames_spec.loader.exec_module(_frames_module)
    data_consumption = _frames_module.data_consumption
    literal_source_relations = _frames_module.literal_source_relations
    observer_registration_identity_request = _frames_module.observer_registration_identity_request
    registration_state_request = _frames_module.registration_state_request
    request_relations = _frames_module.request_relations
    engineering_relations = _frames_module.engineering_relations
    _data_quote_view = _frames_module._data_quote_view
    literal_recipient_delivery = _frames_module.literal_recipient_delivery
    literal_recipient_subject = _frames_module.literal_recipient_subject
    _predicate_module = _frames_module._predicate_module
    refine_operations = _predicate_module.refine_operations
    literal_relations = _predicate_module.literal_relations
    is_factual_absence = _predicate_module.is_factual_absence


NEGATIVE_MARKER = re.compile(
    r'不要|不需要|不研究|不展开|不涉及|不讨论|不改变|不做|不看|不查|排除|无需|先不(?:查|看|研究|讨论|展开)?|不是'
    r'|禁止|不能|不可|不允许|不保证|别'
    r"|\b(?:not interested in|do not need|must not|do not|don['’]t|cannot|can['’]t|excluding|exclude|without|never|no|not)\b", re.I)
TOPIC_EXCLUSION = re.compile(
    r'不需要|不研究|不展开|不涉及|不讨论|不看|不查|排除|无需|先不|不是'
    r'|\b(?:not interested in|do not need|excluding|exclude|without|no)\b', re.I)
REENTRY = re.compile(
    r'\b(?:but|instead|however|please|repair|debug|review|implement|initialize|investigate)\b'
    r'|但(?:是)?|而是|只(?:修|查|看|要|需)|需要|请|修复|排查|审查|实现'
    r'|[，,]\s*(?:普通|通用|常规|一般契约|ordinary\b|generic\b|general\b)', re.I)
REVIEW_PROHIBITION = re.compile(
    r'^\s*(?:(?:擅自|替我|给我)\s*)?(?:新增|跳过|调用|当作|假定|重置|使用|用|把|将|改|重建|认为|宣称|保证'
    r'|add\b|skip\b|call\b|use\b|using\b|assum(?:e|es|ed|ing)\b|treat\b|reset\b|change\b|claim(?:s|ed|ing)?\b|infer(?:s|red|ring)?\b|replay\b)'
    r'|(?:就能|能认为|可以认为|意味着|代表|等于|证明|\bmeans?\b|\bprove\b|\bimplies\b)', re.I)
INFERENCE = re.compile(
    r'证明|保证|当作|视为|推断|意味着|代表|等于'
    r'|\b(?:to\s+prove|as\s+(?:proof|evidence)\s+(?:of|for)|proves?|guarantees?|implies|means?|as)\b', re.I)
SPECIAL_LIFECYCLE = re.compile(
    r'迁移|分片|跨洞穴|死亡|幽灵|换角|角色重选|重新选择角色|回档|\b(?:migration|migrate|shards?|death|ghost|reroll|seamless|character reselection)\b'
    r'|RestoreSnapshotUserSession|快照恢复|snapshot\s+(?:restore|restoration|recovery|rollback)', re.I | re.ASCII)
DEEP = re.compile(r'深入|精确源码|源码解剖|深层|\b(?:deep|anatomy)\b', re.I)
ORDINARY = re.compile(r'普通|通用|一般契约|\b(?:ordinary|normal|generic|general)\b', re.I)
DEEP_EXCLUSION = re.compile(r'深入|解剖|深层|具体.*prefab|\b(?:deep|anatomy|sample.specific)\b', re.I)
CHINESE_POLAR_QUESTION = re.compile(
    r'能不能|会不会|是不是|要不要|可不可以|可以不可以|需不需要|需要不需要'
    r'|允不允许|允许不允许|应不应该|应该不应该|该不该|行不行|有没有|是否|能否|可否')
QUESTION_SCOPE_BREAK = re.compile(r'[，,。；;！？!?\n]|但是|但|然而|不过|并且|同时')

# 英中任务词义共用一份导航词表，不对应条目 ID 或评测答案。
SEMANTIC_PATTERNS={
 'display':r'\b(?:hud|ui|panel|badge|widget|display|overlay)\b|界面|面板|显示|血条',
 'initial_read':r'\b(?:initial (?:value|state|read|data)|current (?:snapshot|state|value|getter|render)|getter snapshot|first (?:read|render|display|open)|read.*?initial)\b|初读|初值|初始值|读取初|当前(?:可读)?状态|当前值|初始数据|(?:首次|第一次).{0,8}(?:打开|显示|加入)|(?:首次|第一次)\s*读取'
     r'|先\s*(?:从(?:(?!读取|调用|执行|乘|写入|设置|更新|创建|保存|加载|扣除|注册|绑定|检查|验证|计算|清理|删除|再|然后|随后|之后|才|就|\b(?:then|before|after|calls?|sets?|writes?|updates?|saves?|loads?|computes?|checks?)\b)(?:[^，,。；;！？.!?\n]|(?<=[A-Za-z0-9_])\.(?=[A-Za-z_]))){1,48}?)?读取',
 'subscription':r'\b(?:dirty|[a-z_]*dirty|subscrib\w*|listenforevent|removeeventcallback|observers?|watchers?|unregister\w*|change (?:notifications?|events?|listeners?)|state changes?|updates?)\b|\blistens?\s+to\b|\b(?:register|registration|detach|remove|bind|unbind|manage|attach)\w*.{0,20}\blisteners?\b|listener.{0,5}(?:登记|注册|解绑|索引)|监听|观察器|订阅|事件边|事件解绑|更新通知|后续更新|后续dirty|属性.{0,5}变化|首次dirty',
 'readiness':r'\b(?:ready|readiness|available|availability|dependencies|depend\w*|initializ\w*)\b|可用|依赖|初始化|已到达|已抵达',
 'replicated_view':r'\b(?:replica|classified|netvars?|replicated|replication|networked|getter)\b|复制|公有.*?接口|公开.*?接口',
 'identity':r'\b(?:userid|guid|identity|identifiers?|accounts?|cross.session|progression)\b|身份|标识|账号|永久.*?id|长期.*?键',
 'reconnect':r'\b(?:reconnect\w*|rejoin\w*|disconnect\w*|despawn|playerexited)\b|重连|断线|离场|离开|退出重进',
 'rebind':r'\b(?:rebind\w*|stale|old (?:entity|reference|listener)|invalid references?)\b|重新.{0,4}(?:绑定|关联|取得)|重绑定|旧(?:实体|引用|订阅|监听)|运行关联',
 'cleanup':r'\b(?:cleanup|clean up|detach|cancel\w*|remov\w*|unload\w*|leak\w*)\b|清理|解绑|卸载|残留|移除|取消',
 'persistence':r'\b(?:persist\w*|onload|onsave|load\w*|save\w*|restor\w*|serializ\w*|setpersistdata)\b|持久|存档|保存|读档|恢复|加载',
 'missing_key':r'\b(?:(?:missing|absent|no)\s+(?:[a-z_]\w*\s+){0,2}(?:key|field|data|payload)|defaults?)\b|缺键|缺值|默认|字段缺|数据缺',
 'construction':r'\b(?:construct\w*|factory|postinit|common_postinit|master_postinit|newspawn|new.spawn)\b|构造|出生|初次(?:生成|出生|创建)|首次给予|postinit',
 'authority':r'\b(?:authority|authoritative|server.only|server|client|remote|host|dedicated|rpc)\b|权威|端别|服务端|客户端|专服',
 'action_result':r'\b(?:success|succeed\w*|failure|fail\w*|results?|callbacks?|bufferedaction)\b|成功|失败|结果|回调',
 'material':r'\b(?:ingredients?|materials?|providers?|resources?|consume\w*|costs?|budgets?)\b|材料|资源|扣费|扣料|消费|预算',
 'cooldown':r'\b(?:cooldowns?|timer|timeleft|remaining time|recharg\w*)\b|冷却|定时器|剩余时间|充能',
 'ownership':r'\b(?:owners?|ownership|sources?|sourcekey|modifiers?)\b|所有权|来源|归属|贡献|撤销|修饰器',
 'boundary':r'\b(?:boundar\w*|guarantee\w*|proof|prove\w*|infer\w*|limitations?)\b|边界|证明|保证|不能推|不等于|不代表',
 'local_player':r'\b(?:local (?:player|input|control)|locality|theplayer|onsetowner)\b|本地(?:玩家|输入|控制)|本地玩家上下文',
 'authority_gate':r'\b(?:ismastersim|ismastershard|setpristine|master_postinit|server.only|authoritative (?:state|mutation|component))\b|权威(?:状态|组件|写入)|master/server|master尾部|remote返回',
 'display_authority_gate':r'(?:\b(?:dedicated|theplayer|local player|locality)\b|本地玩家).{0,60}(?:\b(?:hud|ui|input|controls)\b|界面|本地输入)|(?:\b(?:hud|ui|input|controls)\b|界面).{0,60}(?:\b(?:dedicated|theplayer|local player|locality)\b|本地玩家)',
 'resource_consumption':r'\b(?:consum\w*|removeingredients|removeingredient|deduct\w*|spend\w*|drain\w*|ingredient (?:removal|consumption)|resource (?:cost|consumption))\b|扣(?:费|料|量|材料)|材料.{0,6}(?:扣除|消费|消耗)|消耗.{0,6}(?:资源|材料)|消费|消耗',
 'action_execution':r'\b(?:bufferedaction|performbufferedaction|performpreviewbufferedaction|doaction|action (?:execution|dispatch|validity)|succeed|fail)\b|动作(?:执行|分派|有效性)|执行动作|action\.fn',
 'state_transition':r'\b(?:stategraph|gotostate|updatestate|statemem|onexit|eventhandler|timeline)\b|状态图|状态切换|状态退出|旧state|新state',
 'modifier_contribution':r'\b(?:modifierlist|sourcekey|modifiers?|setspeedmultiplier|setchargetimemod)\b|修饰器|来源贡献|乘区|贡献.{0,6}(?:撤销|归属)|同源.*替换',
 'scheduled_task':r'\b(?:do(task|periodictask)intime|pendingtasks|task handles?|scheduled (?:task|work)|periodic tasks?|cancel\w* (?:task|handle)|cleanup tasks?|task cancellation)\b|\btasks?\b(?=.{0,30}\b(?:owned|owners?|ownership|created|scheduled|captures?|cleanup)\b)|任务句柄|定时任务|周期任务|延迟(?:任务|效果|工作)|任务(?=.{0,16}(?:由|创建|归属|捕获|所有权|清理))|实体task|task捕获|task helpers|(?:清理|取消|收尾).{0,6}(?:任务|task)|旧handle',
 'reference_binding':r'\b(?:entity references?|runtime references?|cross.entity (?:relations?|references?)|rebinding|rebind\w*|newents|postpass|refs)\b|实体引用|跨实体关系|重新建立运行关联|重新(?:绑定|关联|取得)|旧GUID|旧(?:实体|引用)',
 'recipe_transaction':r'\b(?:builder|dobuild|makerecipe\w*|recipes?|ingredients?|craft\w*)\b|制作|配方|造物|材料供应',
 'fuel_consumption':r'\b(?:fueled|fuel|startconsuming|stopconsuming|initializefuellevel|depleted)\b|燃料|耗油|耗燃料',
 'perish_progress':r'\b(?:perishable|perish\w*|rott?\w*)\b|腐烂|腐败|保鲜',
 'work_progress':r'\b(?:workable|workedby|workleft|dotoolwork|onwork|onfinish|chop|mine)\b|砍伐|敲击|工作量|采矿',
 'pick_regrowth':r'\b(?:pickable|onpicked|spawnproductloot|finishgrowing|consumecycles|regrowth)\b|采摘|再生|生长周期',
 'container_slots':r'\b(?:containers?|widgetsetup|setnumslots|maxitemslots|slots?|capacity)\b|容器|槽位|容量',
 'spatial_search':r'\b(?:findentities|findwalkableoffset|findvalidpositionbyfan|findentity|findpickupableitem|spatial|walkable|nearest|closest|coordinates?|offsets?)\b|空间查询|落点|附近.{0,4}(?:实体|目标)|坐标|偏移|最近|同距',
 'damage_pipeline':r'\b(?:combat|doattack|getattacked|canhittarget|doareaattack|damage|redirect\w*|onhitother|health:dodelta)\b|伤害|攻击|命中|战斗|伤害重定向',
 'projectile_delivery':r'\b(?:projectiles?|complexprojectile|onhit|onmiss|throw|launch)\b|弹体|投射物|投掷|投射',
 'burn_progress':r'\b(?:burnable|propagator|ignite|extinguish|smolder\w*|burnt|burning)\b|燃烧|点燃|烧毁|熄灭|阴燃',
 'repair_transaction':r'\b(?:repairable|boatleak|hullhealth|boatpatch|boat repair|repair amount|repair materials?|patches)\b|修船|维修|堵漏|漏点|修复量',
 'healing_transaction':r'\b(?:healer|onheal|healing|sethealthamount|canheal)\b|治疗|治疗量|回血',
 'eat_transaction':r'\b(?:eater|oneaten|oneat|edible|eating|eat)\b|食用|进食|可食',
 'upgrade_progress':r'\b(?:upgradeable|upgrader|upgrad\w*|advancestage)\b|升级|阶段推进',
 'deploy_transaction':r'\b(?:deployable|candeploy|ondeploy|deploy\w*|planting)\b|部署|种植',
 'durability':r'\b(?:finiteuses|setuses|onfinished|durability|wear)\b|耐久|磨损|使用次数',
 'configuration':r'\b(?:getmodconfigdata|config\w*|settings?|options?)\b|配置|设置项|缺省',
 'module_loading':r'\b(?:modimport|require|modules?|imports?|exports?|global)\b|模块|导入|导出',
 'world_observation':r'\b(?:world[ -]?state|watchworldstate|stopwatchingworldstate|seasons?)\b|世界状态|世界事件|季节',
 'special_lifecycle':SPECIAL_LIFECYCLE.pattern,
 'shard_migration':r'\b(?:shards?|migration|migrate|migrating)\b|迁移|分片|跨洞穴',
 'death_transition':r'\b(?:death|ghost|resurrect\w*|reviv\w*)\b|死亡|幽灵|复活',
 'character_reroll':r'\b(?:reroll|seamless|character reselection)\b|换角|角色重选|重新选择角色',
 'snapshot_restore':r'\b(?:restoresnapshotusersession|snapshot (?:restore|restoration|recovery|rollback))\b|快照恢复|快照回档',
 'return_false':r'(?:\b(?:return\w*|results?|gates?|rollback|reject\w*)\b|返回|结果|拒绝).{0,30}\bfalse\b|\bfalse\b.{0,30}(?:\b(?:return\w*|results?|gates?|rollback|reject\w*)\b|返回|结果|拒绝)',
 'return_nil':r'(?:\b(?:return(?:s|ed|ing)?|results?)\b|返回|结果)[^。；;!?！？\n]{0,30}\bnil\b|\bnil\b[^。；;!?！？\n]{0,30}(?:\b(?:return(?:s|ed|ing)?|results?)\b|返回|结果)',
 'partial_effects':r'\b(?:partial effects?|side effects?|rollback|atomic\w*)\b|部分效果|副作用|回滚|原子性',
 'caller_responsibility':r'\b(?:callers?|call.site|calling code|caller responsibility)\b|调用方|调用者负责|上层负责',
 'callback_dispatch':r'\b(?:success callbacks?|failure callbacks?|callback (?:dispatch|invocation|execution)|addsuccessaction|addfailaction|succeed|fail)\b|成功回调|失败回调|回调.{0,5}(?:登记|调用|执行)|(?:调用|执行).{0,5}回调',
 'resource_allocation':r'\b(?:remaining budgets?|resource allocation|allocated amounts?|entity.(?:amount|count|quantity)|provider\w*.{0,30}(?:identity|budget|allocation))\b|剩余预算|重复预算|已分配数量|按实体身份|实体.{0,14}(?:数量|计数|去重|重计)|(?:数量|内表).{0,10}实体|已出现的实体键|多个资源\s*Provider|多个\s*Entity.amount',
}
SEMANTIC_REGEX={name:re.compile(pattern,re.I | re.ASCII) for name,pattern in SEMANTIC_PATTERNS.items()}
SEMANTIC_NAVIGATION={
 'display':'HUD 界面 面板 显示',
 'initial_read':'初读 初值 当前状态 initial value current snapshot',
 'subscription':'监听 订阅 后续更新 dirty change listener',
 'replicated_view':'replica classified 复制视图 公开复制接口',
 'identity':'userid GUID 账号 身份',
 'reconnect':'重连 断线 离场 reconnect',
 'rebind':'重新绑定 重新关联 旧引用 运行关联',
 'missing_key':'缺键 缺值 默认字段 missing key',
 'construction':'构造 postinit OnNewSpawn',
 'material':'材料 消费 预算 provider',
 'cooldown':'冷却 剩余时间 timeleft cooldown',
 'ownership':'归属 所有权 来源贡献 sourcekey',
 'local_player':'本地玩家 本地输入 ThePlayer',
 'authority_gate':'ismastersim SetPristine 权威状态',
 'display_authority_gate':'HUD 本地玩家 locality',
 'resource_consumption':'消费 消耗 扣料 resource consumption',
 'action_execution':'BufferedAction 动作执行',
 'state_transition':'StateGraph 状态图 状态退出',
 'modifier_contribution':'修饰器 modifier sourcekey 来源贡献',
 'scheduled_task':'任务句柄 定时任务 pendingtasks',
 'reference_binding':'实体引用 重新绑定 运行关联',
 'recipe_transaction':'Builder 制作 配方 ingredients',
 'fuel_consumption':'Fueled 燃料 消耗',
 'perish_progress':'Perishable 腐烂 腐败',
 'work_progress':'Workable 工作量 砍伐',
 'pick_regrowth':'Pickable 采摘 生长周期',
 'container_slots':'Container 容器 槽位 容量',
 'spatial_search':'空间查询 坐标 偏移 落点',
 'damage_pipeline':'Combat 伤害 攻击 命中',
 'projectile_delivery':'Projectile 弹体 投射物',
 'burn_progress':'Burnable 燃烧 点燃 熄灭',
 'repair_transaction':'Repairable 维修 修船 堵漏',
 'healing_transaction':'Healer 治疗 治疗量',
 'eat_transaction':'Eater 食用 进食',
 'upgrade_progress':'Upgradeable 升级 阶段推进',
 'deploy_transaction':'Deployable 部署 种植',
 'durability':'FiniteUses 耐久 磨损',
 'configuration':'GetModConfigData 配置 缺省',
 'module_loading':'ModImport Require 模块 导入',
 'world_observation':'WatchWorldState 世界状态 季节',
 'shard_migration':'迁移 分片 跨洞穴 migration shard',
 'death_transition':'死亡 幽灵 复活 death ghost',
 'character_reroll':'换角 reroll seamless',
 'snapshot_restore':'快照恢复 RestoreSnapshotUserSession',
 'partial_effects':'部分效果 副作用 回滚',
 'caller_responsibility':'调用方 调用者 caller',
 'callback_dispatch':'成功回调 失败回调 回调执行',
 'resource_allocation':'剩余预算 实体身份 已分配数量 resource allocation',
}

# 端别、资源名和清理动词可描述环境，不能独立成为某张卡的任务依据。
BROAD_CONCEPTS = frozenset(('display', 'readiness', 'authority', 'action_result',
                            'material', 'ownership', 'cleanup', 'boundary', 'special_lifecycle'))
SUBJECT_PATTERNS = {
 'display': SEMANTIC_PATTERNS['display'] + r'|\b(?:playerhud|statusdisplays)\b',
 'identity': SEMANTIC_PATTERNS['identity'] + '|' + SEMANTIC_PATTERNS['rebind'],
 'replicated_view': SEMANTIC_PATTERNS['replicated_view'] + r'|\b(?:player_classified|net_[a-z_]+|health_replica|hunger_replica|sanity_replica)\b',
 'subscription': r'\b(?:listenforevent|removeeventcallback|listeners?|observers?|watchers?|subscrib\w*)\b|\blistens?\s+to\b|监听|观察器|订阅|事件边',
 'task': SEMANTIC_PATTERNS['scheduled_task'],
 'action': r'\b(?:bufferedaction|actions?|doaction|performbufferedaction|playercontroller|playeractionpicker|addcomponentaction|collectactions)\b|动作(?:执行|结果|预测|分派)|执行动作',
 'stategraph': SEMANTIC_PATTERNS['state_transition'] + r'|\b(?:stategraphinstance|timeevent|frameevent)\b',
 'combat': SEMANTIC_PATTERNS['damage_pipeline'] + r'|\b(?:spdamageutil|planardamage|planardefense)\b',
 'projectile': SEMANTIC_PATTERNS['projectile_delivery'],
 'modifier': SEMANTIC_PATTERNS['modifier_contribution'] + r'|\b(?:sourcemodifierlist|playerspeedmult|damagetypebonus|damagetyperesist|electricattacks|moistureimmunity)\b',
 'buff': r'\b(?:debuff|buffs?|adddebuff)\b|增益|减益',
 'timer': r'\b(?:timer|timers|timeleft|timerdone|worldsettingstimer|cooldowns?|spellbookcooldowns)\b|冷却|定时器',
 'recharge': r'\b(?:rechargeable|recharg\w*|discharge|ischarged)\b|充能|充电',
 'builder': SEMANTIC_PATTERNS['recipe_transaction'],
 'fuel': SEMANTIC_PATTERNS['fuel_consumption'],
 'perish': SEMANTIC_PATTERNS['perish_progress'],
 'work': SEMANTIC_PATTERNS['work_progress'],
 'pick': SEMANTIC_PATTERNS['pick_regrowth'],
 'container': SEMANTIC_PATTERNS['container_slots'],
 'spatial': SEMANTIC_PATTERNS['spatial_search'],
 'burn': SEMANTIC_PATTERNS['burn_progress'],
 'boat': SEMANTIC_PATTERNS['repair_transaction'],
 'healer': SEMANTIC_PATTERNS['healing_transaction'],
 'eater': SEMANTIC_PATTERNS['eat_transaction'],
 'upgrade': SEMANTIC_PATTERNS['upgrade_progress'],
 'deploy': SEMANTIC_PATTERNS['deploy_transaction'],
 'uses': SEMANTIC_PATTERNS['durability'],
 'config': SEMANTIC_PATTERNS['configuration'],
 'module': SEMANTIC_PATTERNS['module_loading'],
 'worldstate': SEMANTIC_PATTERNS['world_observation'] + r'|\b(?:addwatcher|removewatcher|setvariable)\b',
 'shard': SEMANTIC_PATTERNS['shard_migration'],
 'death': SEMANTIC_PATTERNS['death_transition'],
 'reroll': SEMANTIC_PATTERNS['character_reroll'],
 'snapshot': SEMANTIC_PATTERNS['snapshot_restore'],
 'return_contract':SEMANTIC_PATTERNS['return_false']+'|'+SEMANTIC_PATTERNS['return_nil']+'|'+SEMANTIC_PATTERNS['caller_responsibility'],
 'allocation':SEMANTIC_PATTERNS['resource_allocation'],
 'health': r'\b(?:health|health_replica)\b|生命值|血量',
 'hunger': r'\b(?:hunger|hunger_replica)\b|饥饿值|饥饿',
 'sanity': r'\b(?:sanity|sanity_replica)\b|精神值|理智值',
 'inventory': r'\b(?:inventory|inventoryitem|giveactiveitem|giveordropitem|stackable|ondestack)\b|背包|库存|堆叠|拆堆',
 'equipment': r'\b(?:equippable|equipslots?|onequipfn|onunequipfn|onpocketfn|equip|unequip)\b|装备|卸下|入袋',
 'trader': r'\b(?:trader|acceptgift|abletoaccept|wantsaccept|onaccept|trade|give)\b|交易|赠予|接受物品',
 'class': r'\b(?:class|addsetter|removesetter|makereadonly|readonly|metamethods?)\b|属性回调|只读属性|类字段|实例字段|继承',
 'skilltree': r'\b(?:skilltree\w*|skill_tree|skilltree_defs|playerinfopopup|resolvecharacter|bigportraits|skill\s+(?:tree|ui|panel))\b|技能树|技能\s*(?:UI|界面|面板)',
 'rpc': r'\b(?:rpc|handlerpcqueue|handlemodrpc|callrpc|addmodrpchandler|sendmodrpctoserver|checknumber|checkentity|checkbool)\b|RPC',
 'input': r'\b(?:input|oncontrol|controls?|controllers?|playercontroller|clicks?|hasinputfocus|setmodfocus|modfocus|thefrontend)\b|输入|控制焦点|点击|控制器',
 'prediction': r'\b(?:prediction|previewing|predict\w*|canlocomote|canpredictmovement|pausepredict|nopredict|clearcachedserverstate|set_local)\b|预测|预演',
 'world': r'\b(?:theworld|world|worldmapsetsize|populateworld|makeworld|simpostinit)\b|世界|世界状态',
}
SUBJECT_REGEX = {name: re.compile(pattern, re.I | re.ASCII) for name, pattern in SUBJECT_PATTERNS.items()}


def _text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


STORAGE_DURABILITY = re.compile(
    r'\b(?:disk|storage|filesystem|database|transaction|write)(?:[ /-]+(?:write|storage))?[ /-]+durability\b'
    r'|(?:磁盘|文件系统|数据库|事务|落盘|存储)[ /-]*(?:durability|耐久性?)', re.I)


@memoized_analysis
def _semantic_text(value):
    text = STORAGE_DURABILITY.sub(' ', _text(value))
    # CamelCase 只提供词形导航；不把字段名或接收者变成已证实行为。
    separated = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    return text if separated == text else text + ' ' + separated


@memoized_analysis
def task_subjects(text):
    value = _semantic_text(text)
    subjects = {name for name, pattern in SUBJECT_REGEX.items()
                if pattern.search(_return_contract_text(value) if name == 'return_contract' else value)}
    if observer_registration_identity_request(value) and not _ACCOUNT_IDENTITY.search(value):
        subjects.discard('identity')
    return subjects


_ACCOUNT_IDENTITY = re.compile(r'\b(?:accounts?|userid|guid|cross[ -]session|progression)\b|账号|账户|长期进度', re.I)


@memoized_analysis
def _return_contract_text(text):
    """A nil call operand is not a return value, even beside callback prose."""
    if not re.search(r'\bnil\b', text, re.I | re.ASCII):
        return text
    syntax = _data_quote_view(text, literal_names=False)
    visible = list(syntax)
    stack = []
    for match in re.finditer(r'\(|\)|\bnil\b', syntax, re.I | re.ASCII):
        token = match.group().lower()
        if token == '(':
            head = re.search(r'([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)\s*$', syntax[:match.start()])
            call = bool(head and head.group(1).lower() not in {'return', 'returns', 'returned', 'result', 'results'})
            stack.append(call or bool(stack and stack[-1]))
        elif token == ')':
            if stack:
                stack.pop()
        elif stack and stack[-1]:
            visible[match.start():match.end()] = ' ' * (match.end() - match.start())
    return ''.join(visible)


@memoized_analysis
def _precise_symbols(text):
    pattern = r'(?<![A-Za-z0-9_])(?:[A-Za-z_]\w*[.:][A-Za-z_]\w*|[a-z]+_[a-z_]+|[A-Z][A-Z0-9_]{2,}|(?:[A-Z][a-z0-9]+){2,}[A-Za-z0-9_]*)(?![A-Za-z0-9_])'
    return {value.lower() for value in re.findall(pattern, text, re.ASCII)
            if value.lower() not in ('hud', 'rpc', 'api', 'ready', 'onload', 'onsave', 'onremove', 'remove', 'update', 'get', 'set', 'fn')}


@memoized_analysis
def structured_record_ids(text):
    """Lexical ID candidates; only a canonical registry can resolve them.

    Prefixes allow an ordinary suffix on a cited identity (for example -based),
    without fuzzy matching or inventing an identity from a topic word.
    """
    result = set()
    for value in re.findall(r'(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z0-9_]+)+(?![A-Za-z0-9_])', text, re.ASCII):
        parts = value.upper().split('-')
        result.update('-'.join(parts[:end]) for end in range(2, len(parts) + 1))
    return result


LEXICAL_STOP = frozenset('a an the and or to of for with from this that how what when which is are be as in on at by can could should would must do does not only please need review debug research implement repair fix build source native knowledge evidence code coding task contract ordinary general generic server client host remote dedicated authority cleanup material materials resource resources provider providers callback callbacks result results success failure owner state value values entity player world object component components method methods function functions current initial read update updates lua runtime using use return returns'.split())
HAN_LEXICAL_STOP = frozenset(('原版', '源码', '状态', '当前', '对象', '实体', '玩家', '组件', '方法', '函数',
                              '物品', '普通', '通用', '相关', '材料', '资源', '清理', '权威', '需要', '可以',
                              '什么', '如何', '是否', '返回', '调用', '执行', '显示'))


@memoized_analysis
def _lexical_tokens(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).lower()
    result = {token for token in re.findall(r'[a-z_][a-z0-9_]*', text) if token not in LEXICAL_STOP}
    for phrase in re.findall(r'[\u3400-\u9fff]+', text):
        result.update(phrase[index:index + 2] for index in range(len(phrase) - 1)
                      if phrase[index:index + 2] not in HAN_LEXICAL_STOP)
    return result


DOMAIN_SUBJECTS = frozenset(('combat', 'projectile', 'modifier', 'buff', 'timer', 'recharge',
                            'builder', 'fuel', 'perish', 'work', 'pick', 'container', 'spatial',
                            'burn', 'boat', 'healer', 'eater', 'upgrade', 'deploy', 'uses',
                            'config', 'module', 'worldstate', 'shard', 'death', 'reroll',
                            'snapshot', 'health', 'hunger', 'sanity', 'inventory', 'equipment',
                            'trader', 'class', 'skilltree', 'rpc', 'input', 'prediction', 'world'))
# These concepts navigate to a subject; the noun alone does not describe a mechanism.
SUBJECT_CONCEPTS = frozenset(('replicated_view', 'identity', 'recipe_transaction', 'fuel_consumption',
                             'perish_progress', 'work_progress', 'pick_regrowth', 'container_slots',
                             'damage_pipeline', 'projectile_delivery', 'burn_progress',
                             'repair_transaction', 'healing_transaction', 'eat_transaction',
                             'upgrade_progress', 'deploy_transaction', 'durability',
                             'configuration', 'module_loading', 'world_observation', 'spatial_search', 'cooldown',
                             'shard_migration', 'death_transition', 'character_reroll', 'snapshot_restore'))
CONCRETE_BEHAVIOR = re.compile(
    r'\b(?:reads?|writes?|sets?|stores?|records?|saves?|loads?|restores?|returns?|rejects?|accepts?'
    r'|checks?|tests?|calls?|invokes?|registers?|subscribes?|binds?|rebinds?|indexes?|rebuilds?'
    r'|cancels?|removes?|deletes?|detaches?|clears?|consumes?|deducts?|allocates?|dispatches?|forwards?'
    r'|updates?|initializes?|creates?|constructs?|replaces?|retains?|preserves?|captures?|resumes?'
    r'|leaves?|remains?|proves?|guarantees?|implies|means|clamps?|limits?|multiplies|receives?|supplies?|exists?|implements?'
    r'|evaluates?|evaluated|runs?|passes?|short-circuits?|installs?|listens?|selects?|precedes?|sorts?|computes?|queries?)\b'
    r'|读取|读回|读出|写入|赋值|只赋|保存|存储|加载|恢复|返回|拒绝|接受|检查|核验|测试|调用'
    r'|登记|注册|监听|订阅|绑定|关联|索引|重建|取消|清理|解绑|移除|撤销|消费|消耗|扣除|分配'
    r'|分派|转发|更新|初始化|创建|构造|替换|保留|捕获|继续|暂停|留给|证明|保证|意味着|钳|限制|乘|接收|收到|提供|请求|交接|延续|删除|遍历|匹配|合并|去重|重计|赋值'
    r'|校验|清键|清空|浅拷贝|推进|安排|豁免|拆出|推送|交付|短路|触发|忽略|折叠|转交'
    r'|(?:以|用|通过)\s*[A-Za-z_]\w*(?:[.:]\w+)*\s*记录(?=\s*(?:[，,。.;；\n]|$))'
    r'|连接|选择|排序|计算|设置|重设|重启|停止|同步', re.I)
# Literal field values are an original relation, even without a prose verb.
# Metadata labels and wrappers cannot turn such text into a deliverable behavior.
FIELD_VALUE_RELATION = re.compile(
    r'(?<![A-Za-z0-9_])(?:[A-Za-z_]\w*[.:])*[A-Za-z_]\w*\s*=(?!=)\s*'
    r'(?:true|false|nil|[-+]?\d+(?:\.\d+)?)\b', re.I | re.ASCII)
SOURCE_METADATA_LABEL = re.compile(
    r'^\s*(?:title(?:_zh|_en)?|metadata|navigation|topic|tags?|aliases|retrieval(?:_triggers)?|task_keywords|scope'
    r'|标题|元数据|导航|主题|标签|别名|检索词|任务关键词|范围)\s*[:：]'
    r'|^\s*(?:(?:the|this|that|an?)\s+)?(?:labels?|titles?|keywords?|metadata)\s+'
    r'(?:stores?|contains?|lists?|quotes?)\s+(?:(?:the|these|those|some)\s+)?(?:words?|text|phrases?|tokens?)\b'
    r'|^\s*(?:标签|标题|元数据|关键词)(?:中)?(?:保存|存储|包含|列出|引用)(?:了)?(?:文字|文本|词语|短语)', re.I)
SOURCE_METADATA_KEYS = frozenset(('owner', 'id', 'title', 'title_zh', 'title_en', 'tags', 'aliases',
                                  'retrieval_triggers', 'task_keywords', 'scope', 'entry_type',
                                  'claim_type', 'kind', 'record_pointer', 'artifact_path', 'sha256',
                                  'pointer', 'classification', 'source_refs', 'evidence_refs'))


def _original_atom(context):
    return isinstance(context, dict) and context.get('atom_kind') == 'NSF' and bool(context.get('record_pointer'))


ENTITY_LIFETIME_WORD = re.compile(r'\b(?:remov\w*|delet\w*|destroy\w*|destruction|retire\w*)\b|删除|销毁|移除', re.I)
TASK_RETIREMENT = re.compile(
    r'\b(?:remov\w*|delet\w*|cancel\w*|clean(?:s|ed|ing)?\s+up)\s+'
    r'(?:(?:the|an?|its|their|registered|pending|scheduled|owned|old)\s+){0,4}'
    r'(?:tasks?|(?:task\s+)?handles?)\b', re.I)
NON_ENTITY_RETIREMENT = re.compile(
    r'\b(?:tasks?|listeners?|callbacks?|components?|fields?|entries|watchers?)\s+(?:removal|deletion|cleanup)\b'
    r'|\b(?:remove|delete|cancel)\w*\s+(?:the\s+|a\s+|its\s+)?(?:tasks?|listeners?|callbacks?|components?|fields?|entries|watchers?)\b'
    r'|(?:删除|移除|取消|清理).{0,6}(?:任务|监听|回调|组件|字段)|(?:任务|监听|回调|组件|字段).{0,6}(?:删除|移除|清理)', re.I)
ENTITY_REMOVE_CALL = re.compile(r'\b(?:self\.inst|inst|entity|item|target|projectile|invitem|ent|obj):Remove\s*\(', re.ASCII)
ENTITY_REMOVAL_RELATION = re.compile(
    r'\b(?:removes?|deletes?|destroys?)\s+(?:(?:the|an?|its|this|that)\s+){0,2}(?:entit(?:y|ies)|objects?|items?|projectiles?)\b'
    r'|(?:删除|销毁|移除).{0,4}(?:实体|物品|主体|弹体|对象)', re.I)
CALLBACK_IDENTIFIER = r'(?:on[A-Za-z_]\w*|[A-Za-z_]\w*fn|fn|callback)'
CALLBACK_INVOCATION = re.compile(
    r'(?:\b(?:calls?|invokes?)\s+(?:the\s+)?|调用\s*)(?:(?:self|inst)[.:])?'
    + CALLBACK_IDENTIFIER + r'\b', re.I | re.ASCII)
ARGUMENT_USE = re.compile(
    r'\b(?:arguments?|parameters?)\b.{0,45}\b(?:used|passed|supplied|received|forwarded)\b'
    r'|\buses?\b.{0,35}\b(?:arguments?|parameters?)\b'
    r'|(?:第[一二三四五六七八九0-9]+(?:个)?(?:实|形)?参|参数|实参|形参).{0,35}(?:用于|用作|传给|传入|收到|接收)', re.I)
CONDITION_DISTINCTION = re.compile(
    r'\b(?:different|distinct|separate|independent)\s+(?:conditions?|prerequisites?)\b'
    r'|(?:不同|独立|各自)(?:的)?(?:条件|前提)', re.I)
CONDITION_INSUFFICIENCY = re.compile(
    r'\b(?:does?\s+not\s+(?:prove|imply|guarantee)|cannot\s+(?:prove|infer|guarantee)'
    r'|not\s+(?:equivalent|sufficient)|insufficient\s+(?:evidence|proof))\b'
    r'|不能(?:推得|推出|证明)|不足以(?:证明|推断)|不(?:等价|等于|代表)', re.I)


@memoized_analysis
def _requested_entity_lifetime(text):
    if NON_ENTITY_RETIREMENT.search(text) or TASK_RETIREMENT.search(text):
        return False
    return bool(ENTITY_LIFETIME_WORD.search(text) or (
        re.search(r'\bcleanup\b|清理|收尾', text, re.I) and
        re.search(r'\b(?:entity|object|item|projectile)\b|实体|物品|主体|弹体|对象', text, re.I)))


def _information_relations(text, context):
    """Literal relations in an original NSF, never maturity inferred from metadata."""
    if not _original_atom(context) or SOURCE_METADATA_LABEL.search(text):
        return set()
    result = set()
    if re.search(r'\b[A-Za-z_]\w*\s+has\s+the\s+(?:Lua\s+)?signature\s+[A-Za-z_]\w*\s*,', text, re.I):
        result.add('argument_binding')
    if re.search(r'\bcoordinates?\b.{0,100}\b(?:plus|adding)\b.{0,80}\b(?:offset|origin)\b', text, re.I):
        result.add('coordinate_binding')
    if re.search(r'\bCancel\s*/\s*nil\s+(?:self\.)?[A-Za-z_]\w*|\bRemoveEventCallback\s*\(', text):
        result.add('task_cancellation')
    # 只由原NSF中的实际谓词/调用建立关系；Stop或回调名称本身不证明删除/调用。
    if ENTITY_REMOVE_CALL.search(text) or ENTITY_REMOVAL_RELATION.search(text):
        result.add('entity_lifetime')
    if CALLBACK_INVOCATION.search(text):
        result.add('callback_binding')
    if ARGUMENT_USE.search(text):
        result.add('argument_binding')
    if re.search(r'(?:收到|接收|接受)\s*第[一二三四五六七八九0-9]+(?:个)?参\s+[A-Za-z_]\w*', text, re.ASCII):
        result.add('argument_binding')
    if CONDITION_DISTINCTION.search(text) or (
            CONDITION_INSUFFICIENCY.search(text) and SEMANTIC_REGEX['readiness'].search(text)):
        result.add('condition_dependency')
    result.update(literal_source_relations(text))
    result.update(literal_relations(text))
    return result


def _concrete_behavior(text, context=''):
    return _source_relation_witness(text, context)['concrete_behavior']


EVIDENCE_BOUNDARY = re.compile(
    r'\b(?:unknown|unverified|unproven|not (?:proved|proven|verified|tested|established)|no (?:evidence|guarantee)|'
    r'does not (?:prove|guarantee|imply)|cannot (?:prove|guarantee|infer)|has no|not available|absent|not implemented|pending)\b'
    r'|未知|未验证|未证明|未确认|未测试|尚无|不能证明|不证明|不保证|不代表|不等于|没有.{0,18}(?:证据|路径|入口|接口|方法)|不提供', re.I)


def _behavior_evidence_boundary(text, context):
    """A missing runtime object in a guard is not missing research evidence."""
    for match in EVIDENCE_BOUNDARY.finditer(text):
        if _original_atom(context) and (is_factual_absence(text, match.start(), match.end()) or
                match.group().lower() in {'has no', '不提供'} and
                'result_behavior' in literal_relations(text)):
            continue
        if _original_atom(context) and match.group().lower() in {'尚无', 'has no', 'absent'}:
            before, after = text[:match.start()], text[match.end():]
            guarded = re.search(r'\b(?:if|when|unless|while)\b|仅|当|若|且|在', before, re.I)
            object_head = re.match(
                r'\s*(?:(?:existing|saved|registered|pending)\s+)?'
                r'(?:handlers?|handles?|listeners?|callbacks?|tasks?|fields?|keys?|slots?|data|values?)\b'
                r'|\s*(?:句柄|回调|监听|任务|字段|键|槽|数据|值)', after, re.I)
            absent_subject = (match.group().lower() == 'absent' and re.search(
                r'\b(?:slot|field|key|handle|handler|callback|task|listener|reference|value|data)\s+(?:is|was)\s*$',
                before, re.I))
            remainder = after[object_head.end():] if object_head else after
            object_clause = re.split(r'[，,；;。]', remainder, maxsplit=1)[0]
            knowledge_object = re.search(
                r'\b(?:evidence|proof|contract|interface|method|path|guarantee|documentation)\b'
                r'|证据|证明|合同|契约|接口|方法|路径|保证|文档', object_clause, re.I)
            if (guarded and (object_head or absent_subject) and not knowledge_object
                    and _concrete_behavior(remainder, context)):
                continue
        return match
    return None

# Operation words describe the requested relation. Component/API names remain
# navigation and cannot, on their own, stand in for these operations.
OPERATION_PATTERNS = {
    'save_state': r'\b(?:onsave|getsaverecord|getpersistdata|saves?|saving|serialize\w*)\b|存档|保存|序列化',
    'load_state': r'\b(?:onload|load\w*|restor\w*|setpersistdata|resume)\b|读档|加载|载入|恢复',
    'update_state': r'\b(?:updates?|updating)\b|更新',
    'consume_resource': r'\b(?:consum\w*|deduct\w*|removeingredients|spend\w*)\b|消费|消耗|扣除|扣料|扣费',
    'allocate_resource': r'\b(?:allocat\w*|budgets?|deduplicat\w*)\b|分配|预算|去重|重计',
    'initial_value': SEMANTIC_PATTERNS['initial_read'],
    'subscribe_event': SEMANTIC_PATTERNS['subscription'],
    'bind_reference': SEMANTIC_PATTERNS['rebind'] + '|' + SEMANTIC_PATTERNS['reference_binding'],
    'schedule_task': r'\b(?:schedul(?:e(?:s|d)?|ing)|do(?:periodic)?taskintime|startupdating|periodic(?:ally)?)\b|安排.{0,10}(?:任务|更新)|周期(?:更新|任务)',
    'cancel_task': r'\b(?:cancel\w*|stopupdating|detach\w*|removeeventcallback)\b|取消|清理.{0,8}任务|解绑',
    'pause_progress': r'\b(?:pause\w*|stopconsuming|stopperishing)\b|暂停|停止.{0,6}(?:消费|腐败|腐烂)',
    'resume_progress': r'\b(?:resum\w*|startconsuming|startperishing|restart\w*)\b|重启|继续.{0,6}(?:消费|腐败|腐烂)|恢复运行',
}
OPERATION_REGEX = {name: re.compile(pattern, re.I | re.ASCII) for name, pattern in OPERATION_PATTERNS.items()}
SCHEDULING_BEHAVIOR = re.compile(
    r'\b(?:schedules?|reschedules?|arranges?)\b.{0,70}\b(?:tasks?|updates?|callbacks?|work)\b'
    r'|\b(?:do(?:periodic)?taskintime|startupdating)\s*\('
    r'|\b(?:updates?|runs?|calls?|ticks?)\b.{0,30}\bperiodically\b'
    r'|(?:安排|创建|登记|启动).{0,20}(?:周期任务|定时任务|更新任务|周期更新)'
    r'|周期(?:性)?(?:地)?(?:调用|执行|更新)', re.I)

_ABILITY_DATA_TAIL_EN = (
    r'(?!\s*(?:(?:[\'’]s?|of)\s*)?'
    r'(?:fields?|data|records?|tables?|values?|caches?|states?|status|attributes?|properties)\b)')
_ABILITY_DATA_TAIL_ZH = r'(?!\s*(?:的\s*)?(?:字段|数据|记录|表|值|缓存|状态|属性))'
ABILITY_RESTORATION = re.compile(
    r'\babilit(?:y|ies)\s+(?:recovery|restoration)\b' + _ABILITY_DATA_TAIL_EN +
    r'|\b(?:business|gameplay)\s+continuity\s+(?:recovery|restoration)\b' + _ABILITY_DATA_TAIL_EN +
    r'|\brestor(?:e[sd]?|ing|ation)\s+(?:of\s+)?'
    r'(?:(?:the|an?|its|their|his|her|our|your|player(?:[\'’]s)?|character(?:[\'’]s)?)\s+){0,3}'
    r'(?:abilit(?:y|ies)|(?:business|gameplay)\s+continuity)\b' + _ABILITY_DATA_TAIL_EN +
    r'|(?:能力|业务连续性)(?:的)?恢复(?!\s*(?:了)?(?:字段|数据|记录|表|值|缓存|状态|属性))'
    r'|恢复(?:(?:玩家|角色|业务)(?:的)?)?(?:原有|既有|自身)?能力' + _ABILITY_DATA_TAIL_ZH +
    r'|恢复业务连续性' + _ABILITY_DATA_TAIL_ZH, re.I | re.ASCII)


@memoized_analysis
def _persistence_text(text):
    # 连续性恢复只遮蔽自身短语；同句其它字段恢复或显式读档仍保留操作约束。
    explicit = re.compile(r'\b(?:persist\w*|onload|onsave|load\w*|save\w*|serializ\w*|setpersistdata|resume)\b'
                          r'|持久|存档|保存|读档|加载|载入', re.I)
    health = re.compile(r'\b(?:heal|health)\b|生命值|血量', re.I)
    parts = re.split(r'([。；;\n!?！？]+)', text)
    for index in range(0, len(parts), 2):
        value = parts[index]
        if not explicit.search(value):
            value = ABILITY_RESTORATION.sub(lambda match: re.sub(
                r'\brestor\w*\b|恢复', lambda word: ' ' * len(word.group()),
                match.group(), flags=re.I | re.ASCII), value)
            if (SEMANTIC_REGEX['healing_transaction'].search(value) or
                    SEMANTIC_REGEX['eat_transaction'].search(value) or health.search(value)):
                value = value.replace('恢复', '  ')
            parts[index] = value
    return ''.join(parts)


@memoized_analysis
def _operations(text, source=False):
    persistence = _persistence_text(text)
    result = {name for name, pattern in OPERATION_REGEX.items()
              if pattern.search(persistence if name in ('save_state', 'load_state') else text)}
    if data_consumption(text):
        result.discard('consume_resource')
    if TASK_RETIREMENT.search(text) or re.search(r'\b(?:tasks?|handles?)\s+(?:removal|cleanup|cancellation)\b'
                 r'|(?:任务|句柄).{0,4}(?:移除|清理|取消)', text, re.I):
        result.add('cancel_task')
    if source and not EVIDENCE_BOUNDARY.search(text):
        if 'subscribe_event' in result and not MECHANISM_BEHAVIOR['subscription'].search(text):
            result.discard('subscribe_event')
        if 'consume_resource' in result and not re.search(
                r'\b(?:consumes?|consumed|consuming|consumecycles|removeingredients?|deduct\w*|spend\w*|startconsuming|stopconsuming)\b'
                r'|消费|消耗|扣除|扣料|扣费', text, re.I):
            result.discard('consume_resource')
        if 'schedule_task' in result and not SCHEDULING_BEHAVIOR.search(text):
            result.discard('schedule_task')
    if source and 'save_state' in result:
        # 字段赋值/记住实参不等于存档；只有原文中的序列化关系提供保存操作。
        serialization = re.search(
            r'\b(?:onsave|getsaverecord|getpersistdata|serialize\w*|persist\w*)\b'
            r'|存档|序列化|持久化|保存.{0,24}(?:data|record|table|schema|timeleft|数据|记录|档案)'
            r'|\bsaves?\b.{0,40}\b(?:data|records?|tables?|schema|timeleft)\b', text, re.I)
        field_assignment = re.search(r'\bsaves?\b.{0,60}\b(?:in|into)\s+(?:self|inst)\.', text, re.I)
        if not serialization or field_assignment and not re.search(
                r'\b(?:onsave|getsaverecord|getpersistdata|serialize\w*)\b|存档|序列化', text, re.I):
            result.discard('save_state')
    result = refine_operations(text, result, source)
    # A request may name the operation as a noun. Source evidence still needs
    # the literal resource-retirement predicate checked by refine_operations.
    if not source and re.search(r'\b(?:tasks?|(?:task\s+)?handles?)\s+(?:removal|deletion|cleanup|cancellation|retirement)\b'
                                r'|(?:任务|句柄)(?:的)?(?:移除|删除|清理|取消)', text, re.I):
        result.add('cancel_task')
    return result
RELATION_PATTERNS = {
    'evaluation_order': r'\b(?:order|sequence|short-circuit\w*|preced\w*)\b|顺序|依次|按顺|早于|晚于|先.{0,60}再',
    'argument_binding': r'\b(?:arguments?|parameters?|actual (?:inputs?|values?))\b|实参|形参|参数|传入',
    'callback_binding': r'\bcallbacks?\b|回调',
    'field_mutation': r'\b(?:assign\w*|setters?|set\w*|writes?|stor\w*|replace\w*|fields?|tracked|properties)\b|赋值|写入|字段|属性|单一slot|替换',
    'event_delivery': r'\b(?:events?|messages?|push\w*event|notif\w*|listeners?)\b|事件|通知|消息|监听',
    'result_behavior': r'\b(?:return\w*|reject\w*|accept\w*|rollback|side.effects?|success|failure|results?|fallback|falls?\s+back)\b|返回|结果|拒绝|接受|回滚|副作用|回退',
    'boundary_relation': r'\b(?:proof|prove(?:s|d)?|proving|guarantee\w*|infer\w*|implies|means|boundar\w*)\b|证明|保证|推断|意味着|边界|不等于|不代表',
    'progress_suspension': r'\b(?:pause\w*|resum\w*|retain\w*.{0,16}(?:time|progress))\b|暂停|保留.{0,10}(?:time|进度)',
    'data_handoff': r'\b(?:continuity|data (?:handoff|transfer))\b|业务数据延续|数据交接|显式数据|显式.{0,6}交接'
                    + '|' + ABILITY_RESTORATION.pattern,
    'coordinate_binding': r'\b(?:coordinates?|offsets?)\b|坐标|偏移',
    'numeric_value': r'\b(?:amounts?|multipliers?|factors?|quantit\w*|scalars?|scaling|formulas?)\b'
                     r'|数值|倍率|基础量|基础值|无量纲|乘法|并乘|计算.{0,12}(?:值|量)',
}
RELATION_REGEX = {name: re.compile(pattern, re.I | re.ASCII) for name, pattern in RELATION_PATTERNS.items()}
EVENT_DISPATCH_RELATION = re.compile(
    r'\b(?:events?|messages?|notifications?)\s+(?:dispatch|delivery)\b'
    r'|\bdispatch(?:es|ed|ing)?\s+(?:(?:an?|the|its|their|named)\s+){0,4}'
    r'(?:events?|messages?|notifications?)\b'
    r'|(?:事件|消息|通知)(?:的)?(?:分派|派发|发送)'
    r'|(?:分派|派发|发送).{0,12}(?:事件|消息|通知)', re.I | re.ASCII)
COORDINATE_ORIGIN = re.compile(r'\borigins?\b|原点', re.I | re.ASCII)
COORDINATE_ORIGIN_CONTEXT = re.compile(SEMANTIC_PATTERNS['spatial_search'] +
    r'|\b(?:nearby|positions?|points?|vectors?)\b|空间|位置|原点', re.I | re.ASCII)
NONCOORDINATE_ORIGIN = re.compile(
    r'\b(?:events?|sources?|claims?|messages?|evidence|reports?|data)[ -]+origins?\b'
    r'|\borigins?\s+(?:of|for)\s+(?:(?:the|this|that|an?|these|those)\s+)?'
    r'(?:events?|sources?|claims?|messages?|evidence|reports?|data)\b', re.I | re.ASCII)
MECHANISM_BEHAVIOR = {
    'initial_read': re.compile(r'\b(?:reads?|getters?|snapshot|initial (?:value|state|read)|first (?:read|render))\b|读取|初读|初值|初始值', re.I),
    'subscription': re.compile(r'\b(?:listenforevent|removeeventcallback|subscrib\w*|(?:register|bind|attach|remove|detach)\w*.{0,24}listeners?)\b|\blistens?\s+to\b'
                               r'|监听|订阅|解绑|(?:绑定|登记|注册).{0,24}(?:listener|dirty)|listener.{0,16}(?:绑定|登记|注册|解绑)', re.I),
    'return_false': re.compile(r'\b(?:return\w*|reject\w*|false.{0,20}(?:rollback|side.effects?))\b|返回|拒绝|回滚|副作用', re.I),
    'return_nil': re.compile(r'\b(?:return\w*|leaves?|callers?)\b|返回|调用方|留给', re.I),
}


def _relations(text, query=False, context=''):
    result = {name for name, pattern in RELATION_REGEX.items()
              if pattern.search(_semantic_text(text) if name == 'numeric_value' else text)}
    result |= _information_relations(text, context)
    # dispatch 的宾语可能是 Hook/方法；真实事件谓词仍由原有字面语法识别。
    literal_event = literal_relations(text) & {'event_delivery'}
    if literal_recipient_delivery(text):
        literal_event.add('event_delivery')
    result |= literal_event
    if COORDINATE_ORIGIN.search(text):
        for unit in re.split(r'[。；;\n!?！？]+|(?<=[.!?])\s+', text):
            if (COORDINATE_ORIGIN.search(unit) and COORDINATE_ORIGIN_CONTEXT.search(unit)
                    and not NONCOORDINATE_ORIGIN.search(unit)):
                result.add('coordinate_binding')
                break
    if (query and SEMANTIC_REGEX['readiness'].search(text) and not _operations(text)
            and not (result - {'boundary_relation'}) and not _unknown_condition_owner(text)):
        result.add('condition_dependency')
    if query and _requested_entity_lifetime(text):
        result.add('entity_lifetime')
    if FIELD_VALUE_RELATION.search(text):
        result.add('field_mutation')
    # A callback argument question is more specific than a generic callback mention.
    if query and 'argument_binding' in result:
        result.discard('callback_binding')
    if (query and 'subscription' in semantic_concepts(text)
            and not (literal_event or EVENT_DISPATCH_RELATION.search(text))):
        result.discard('event_delivery')
    return result


PREDICATE_LABEL_WORDS = frozenset(
    'is are was were be been being has have had contain contains include includes list lists '
    'name names label labels mention mentions describe describes document documents support supports '
    'status data metadata field fields property properties argument arguments callback callbacks '
    'notification notifications event events interface interfaces method methods signature signatures '
    'value values state states key keys record records payload payloads'.split())
PREDICATE_HEAD = re.compile(
    r'^\s*(?:(?:the|an?)\s+)?(?P<head>[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*'
    r'(?:\([^()\n]*\))?)(?:\s+(?:component|object))?\s+'
    r'(?:(?:(?:does?|did|can|will|must|should)\s+(?:not\s+)?)|(?:is|are|was|were)\s+)?'
    r'(?P<predicate>[A-Za-z]+)\b(?P<operand>.*)', re.I | re.ASCII)


def _predicate_relation_witness(text, operations, relations):
    """Original predicate syntax plus an existing relation, never a noun hit."""
    head = PREDICATE_HEAD.match(text)
    if head:
        subject = head.group('head')
        bounded = bool(task_subjects(subject) & (DOMAIN_SUBJECTS | {'display'}) or
                       subject.lower() in {'it', 'its', 'self', 'inst'})
        predicate, operand = head.group('predicate'), head.group('operand')
    else:
        command = re.match(r'^\s*([A-Za-z]+)\b(.*)', text, re.ASCII)
        bounded = bool(command)
        predicate, operand = (command.groups() if command else ('', ''))
    lower = predicate.lower()
    nominal = (lower in PREDICATE_LABEL_WORDS or lower.endswith(
               ('tion', 'tions', 'ment', 'ments', 'ity', 'ities', 'ness')) or
               bool(re.search(r'[a-z][A-Z]', predicate)) or
               bool(re.fullmatch(r'on[a-z_]\w*|[A-Za-z_]\w*fn', predicate, re.I | re.ASCII)))
    if bounded and not nominal:
        operation_predicate = any(OPERATION_REGEX[name].fullmatch(predicate) for name in operations)
        # 未收录动词只提供原关系的语法证据；不推断这个动词的 API 或肯定极性。
        relation_operand = bool(head and relations & _relations(operand) and
                                lower.endswith(('s', 'ed', 'ing')))
        if operation_predicate or relation_operand:
            return True
    for name in operations:
        for match in OPERATION_REGEX[name].finditer(text):
            predicate = match.group()
            if not re.fullmatch(r'[\u3400-\u9fff]{2,}', predicate):
                continue
            prefix, operand = text[:match.start()].strip(), text[match.end():].strip(' 。；;,.')
            prefix = re.sub(r'(?:会|将|并|随后|不|未)$', '', prefix)
            if operand and task_subjects(prefix) & (DOMAIN_SUBJECTS | {'display'}):
                return True
    return False


def _source_relation_witness(text, context=''):
    operations = _operations(text, source=True)
    relations = _relations(text, context=context)
    metadata = bool(SOURCE_METADATA_LABEL.search(text))
    behavior = not metadata and bool(
        CONCRETE_BEHAVIOR.search(text) or FIELD_VALUE_RELATION.search(text) or
        literal_recipient_delivery(text) or
        _information_relations(text, context) or _bounded_hud_construction(text, context) or
        _predicate_relation_witness(text, operations, relations))
    return {'operations': operations, 'relations': relations, 'concrete_behavior': behavior}


@memoized_analysis
def _browse_residual(text):
    value = DEEP.sub(' ', text)
    for symbol in sorted(_precise_symbols(text), key=len, reverse=True):
        value = re.sub(r'(?<![A-Za-z0-9_])' + re.escape(symbol) + r'(?![A-Za-z0-9_])',
                       ' ', value, flags=re.I | re.ASCII)
    for name in DOMAIN_SUBJECTS | {'display', 'identity', 'replicated_view', 'subscription', 'task'}:
        value = SUBJECT_REGEX[name].sub(' ', value)
    value = re.sub(
        r'\b(?:review|debug|research|implement|repair|check|explain|describe|identify|assess|clarify|sketch'
        r'|give|state|tell|me|about|how|what|which|whether|why|please|works?|behaviou?rs?|mechanisms?'
        r'|contracts?|overview|basics|introduction|lifecycle)\b'
        r'|帮我|给我|请|研究|审查|审计|排查|检查|说明|解释|介绍|描述|看看|如何|怎么|什么|是否'
        r'|机制|行为|契约|概览|基础|普通|通用|相关|组件|对象', ' ', value, flags=re.I)
    for name in BROAD_CONCEPTS:
        value = SEMANTIC_REGEX[name].sub(' ', value)
    return value


@memoized_analysis
def _pure_subject_browse(text):
    value = _browse_residual(text)
    return not _lexical_tokens(value) and not re.search(r'[\u3400-\u9fff]', value)


KNOWLEDGE_CONTENT = re.compile(
    r'\b(?:conclusions?|knowledge|constraints?|recommendations?|guidance|findings?)\b'
    r'|结论|知识|约束|建议', re.I)
KNOWLEDGE_APPLICATION = re.compile(
    r'\b(?:reus(?:e[sd]?|able)|appl(?:y|ies|icable|icability)|inform(?:s|ing)?)\b'
    r'|复用|沿用|适用|参考|借鉴|用于|应用', re.I)
KNOWLEDGE_SCAFFOLD = re.compile(
    KNOWLEDGE_CONTENT.pattern + '|' + KNOWLEDGE_APPLICATION.pattern +
    r'|\b(?:existing|known|established|available|prior|earlier|future|later|designs?|planning'
    r'|implementation|can|could|would|be|is|are|for|to|of|in|across|these|those|our|my|new)\b'
    r'|\bcharacter[ -]+changes?\b'
    r'|角色变化|未来|后续|今后|设计|开发|方案|已有|已知|现有|既有|哪些|哪种|什么|可以|能够'
    r'|能|可|的|或|与|和|及|为|对|于|跨|中|到|上', re.I)
KNOWLEDGE_SOURCE_LABEL = re.compile(
    r'^\s*(?:(?:the|this|that|an?)\s+)?'
    r'(?:labels?|metadata|titles?|tags?|keywords?|navigation|lists?|text|entries|entry)\b'
    r'|^\s*(?:本条|该条|条目|标签|标题|元数据|导航词|列表|文本)', re.I)
KNOWLEDGE_ADVICE = re.compile(
    r'应|需要|必须|避免|不要|不得|不能|不把|不假定|建议|推荐|优先|列清|列明|核验|核对|区分|明确|保留|保持'
    r'|\b(?:should|must|choose|avoid|preserve|keep|separate|never|do not|list)\b', re.I)


@memoized_analysis
def _bounded_knowledge_consultation(text):
    """Recognize consultation wording without inventing an operation or relation."""
    if not KNOWLEDGE_CONTENT.search(text) or not KNOWLEDGE_APPLICATION.search(text):
        return False
    residual = KNOWLEDGE_SCAFFOLD.sub(' ', _browse_residual(text))
    return not _lexical_tokens(residual) and not re.search(r'[\u3400-\u9fff]', residual)


@memoized_analysis
def _literal_content_match(request, original_unit):
    """Unknown subject matter can match original words, never owner-only grams."""
    if _precise_symbols(request):
        return False

    def spans(text):
        value = _browse_residual(text)
        value = CONCRETE_BEHAVIOR.sub(' ', value)
        for word in HAN_LEXICAL_STOP:
            value = value.replace(word, ' ')
        value = re.sub(r'[的与和及或而并但则把将让在对由为以却且是有无其这那它我你他只]', ' ', value)
        latin = {word.lower() for word in re.findall(r'(?<![A-Za-z0-9_])[a-z][a-z]+(?![A-Za-z0-9_])', value)
                 if word.lower() not in LEXICAL_STOP}
        han = set(re.findall(r'[\u3400-\u9fff]{2,}', value))
        return latin, han

    request_latin, request_han = spans(request)
    source_latin, source_han = spans(original_unit)
    # 中文只用完整请求残余片段对齐原句的片段起点，不按滑动双字 gram 凑命中。
    return bool(request_latin & source_latin or any(
        source.startswith(anchor) for anchor in request_han for source in source_han))


def _narrow_context(context):
    """Only original narrow scope or verified receivers may supply an omitted owner."""
    if isinstance(context, dict):
        receivers = context.get('receivers', [])
        if isinstance(receivers, str):
            receivers = [receivers]
        texts = [(_text(value), True) for value in receivers]
        texts.append((_text(context.get('scope', '')), False))
    else:
        texts = [(_text(context), False)]
    owners = set()
    for text, receiver in texts:
        if not receiver and re.search(r'\b(?:lifecycle|manager|side|environment|networking|all)\b|生命周期|端别|全部|所有|管理器', text, re.I):
            continue
        positive = query_scope(text)['positive_query']
        subjects = task_subjects(positive) - {'return_contract', 'allocation'}
        if not receiver and subjects & {'shard', 'death', 'reroll', 'snapshot'}:
            continue
        if len(subjects) == 1:
            owners.update(subjects)
    return owners if len(owners) == 1 else set()


def _literal_delivery_named_subject(unit):
    subject = literal_recipient_subject(unit)
    if subject and subject.lower() not in {'it', 'its', 'self', 'this', 'that', 'they',
                                          '它', '其', '该方法', '该函数', '该对象', '该组件', '该实体'}:
        return subject
    return ''


def _source_units(statement):
    if isinstance(statement, str):
        if SOURCE_METADATA_LABEL.search(statement):
            return []
        # Split only the support analysis; delivery retains the whole atom and
        # its original branch conditions. A new named owner cannot borrow the
        # operation of the preceding conjunct.
        units = re.split(r'[。；;\n]+|(?<=[.!?])\s+', statement)
        result = []
        for unit in units:
            cursor = 0
            for marker in re.finditer(r'\s+(?:and|while|but|whereas)\s+|[，,]\s*(?:而|但|while\s+|whereas\s+)?|(?:而|但|同时)', unit, re.I):
                tail = unit[marker.end():]
                head = re.split(r'[，,。；;]|\s+(?:and|while|but|whereas)\s+', tail, maxsplit=1, flags=re.I)[0]
                before = unit[cursor:marker.start()]
                relation_roles = {'display', 'replicated_view', 'subscription', 'task'}
                before_owners = task_subjects(before) & (DOMAIN_SUBJECTS | relation_roles)
                after_owners = task_subjects(head) & DOMAIN_SUBJECTS
                # 角色名也可为并列宾语；新主体必须带自己的谓语，不能截掉 display setter。
                new_head = re.match(r'\s*(?:(?:the|an?)\s+)?([A-Za-z_]\w*)', head, re.I | re.ASCII)
                if new_head:
                    predicate = re.sub(r'^\s*(?:(?:can|could|should|must|may|will|does|do|not|then|also)\s+)*',
                                       '', head[new_head.end():], flags=re.I)
                    if CONCRETE_BEHAVIOR.match(predicate):
                        after_owners |= task_subjects(new_head.group(1)) & relation_roles
                delivery_subject = _literal_delivery_named_subject(head)
                delivery_owners = task_subjects(delivery_subject) & (DOMAIN_SUBJECTS | relation_roles)
                competing_delivery = bool(delivery_subject and not delivery_owners)
                after_owners |= delivery_owners
                if before_owners and (competing_delivery or
                        after_owners and not before_owners & after_owners):
                    result.append(before)
                    cursor = marker.end()
            result.append(unit[cursor:])
        return result
    if isinstance(statement, list):
        return [unit for value in statement for unit in _source_units(value)]
    if isinstance(statement, dict):
        return [unit for key, value in statement.items() if key not in SOURCE_METADATA_KEYS
                for unit in _source_units(value)]
    return []


def _structured_owner(value):
    """A structured owner must declare one identifiable object, including unknowns."""
    if isinstance(value, list):
        if len(value) != 1:
            return None
        value = value[0]
    if not isinstance(value, str) or re.search(r'和|与|以及|同时|并且|、', value):
        return None
    if not re.fullmatch(r'\s*(?:[A-Za-z_]\w*(?:\s+(?:component|object))?'
                        r'|[\u3400-\u9fff]{1,16})\s*', value, re.I | re.ASCII):
        return None
    literal = re.sub(r'\s+(?:component|object)\s*$', '', value.strip(), flags=re.I)
    owners = {name for name in DOMAIN_SUBJECTS | {'display'}
              if SUBJECT_REGEX[name].fullmatch(literal)}
    return frozenset(owners) if len(owners) == 1 else None


@memoized_analysis
def _structured_competing_head(unit):
    """A lower-case named subject is still a new object before a predicate."""
    delivery_subject = _literal_delivery_named_subject(unit)
    if delivery_subject and not task_subjects(delivery_subject) & DOMAIN_SUBJECTS:
        return True
    head = re.match(r'\s*(?:(?:the|an?)\s+)?([A-Za-z_]\w*)\s+', unit, re.I | re.ASCII)
    if head and head.group(1).lower() not in {'it', 'its', 'self', 'this', 'that', 'they'}:
        name = head.group(1)
        if (not task_subjects(name) & DOMAIN_SUBJECTS and not _operations(name)
                and not CONCRETE_BEHAVIOR.fullmatch(name)
                and CONCRETE_BEHAVIOR.match(unit[head.end():])):
            return True
    return any(not task_subjects(name) & DOMAIN_SUBJECTS
               for name in _business_component_names(unit))


def _structured_source_units(statement, owner=frozenset(), lane=None, path=()):
    """Carry only an original dictionary's owner-to-steps relationship."""
    if isinstance(statement, str):
        return [(unit, owner, lane) for unit in _source_units(statement)]
    if isinstance(statement, list):
        return [item for index, value in enumerate(statement)
                for item in _structured_source_units(value, owner, lane, path + (index,))]
    if isinstance(statement, dict):
        result = []
        for key, value in statement.items():
            if key in SOURCE_METADATA_KEYS:
                continue
            child_owner, child_lane = owner, lane
            if 'owner' in statement:
                child_lane = path + (key,)
                child_owner = _structured_owner(statement['owner']) if key == 'steps' else frozenset()
            result.extend(_structured_source_units(value, child_owner, child_lane, path + (key,)))
        return result
    return []


@memoized_analysis
def _source_owner_identity(name):
    known = task_subjects(name) & DOMAIN_SUBJECTS
    return known or {'component:' + name.lower()}


@memoized_analysis
def _original_source_owner_keys(unit):
    delivery_subject = _literal_delivery_named_subject(unit)
    if delivery_subject:
        return _source_owner_identity(delivery_subject)
    owners = set(_explicit_task_owners(unit))
    for name in _business_component_names(unit):
        owners |= _source_owner_identity(name)
    for match in re.finditer(r'\b([A-Za-z_]\w*)[.:]([A-Za-z_]\w*)', unit, re.ASCII):
        name, member = match.groups()
        if (name.lower() not in {'self', 'inst', 'target', 'doer', 'item', 'act', 'data', 'source', 'entity'}
                and not (name.isupper() and member.isupper())):
            owners |= _source_owner_identity(name)
    for clause in re.split(r'\s+(?:and|while|but|whereas)\s+|[，,]', unit, flags=re.I):
        head = re.match(r'\s*(?:(?:the|an?)\s+)?([A-Za-z_]\w*)\s+', clause, re.I | re.ASCII)
        if not head or head.group(1).lower() in {'it', 'its', 'self', 'this', 'that', 'they'}:
            continue
        name = head.group(1)
        predicate = re.sub(r'^(?:(?:can|could|should|must|may|will|does|do|not|then|also)\s+)*',
                           '', clause[head.end():], flags=re.I)
        if (not CONCRETE_BEHAVIOR.fullmatch(name) and not _operations(name)
                and (CONCRETE_BEHAVIOR.match(predicate) or _precise_symbols(name))):
            owners |= _source_owner_identity(name)
    return owners


def _source_unknown_owner_frames(statement):
    """Only original atom-local identities continue; sibling structures do not."""
    def units(value, declared=frozenset(), lane=None, path=()):
        if isinstance(value, str):
            return [(unit, declared, lane) for unit in _source_units(value)]
        if isinstance(value, list):
            return [item for index, child in enumerate(value) for item in units(
                child, declared, lane if lane is not None else path + (index,), path + (index,))]
        if isinstance(value, dict):
            result = []
            for key, child in value.items():
                if key in SOURCE_METADATA_KEYS:
                    continue
                owner = frozenset()
                if key == 'steps' and 'owner' in value:
                    literal = value['owner']
                    if isinstance(literal, list) and len(literal) == 1:
                        literal = literal[0]
                    if (isinstance(literal, str) and re.fullmatch(
                            r'\s*(?:[A-Za-z_]\w*|[\u3400-\u9fff]{1,16})(?:\s+component)?\s*', literal, re.I | re.ASCII)
                            and not re.search(r'和|与|以及|同时|并且|、', literal)):
                        name = re.sub(r'\s+component\s*$', '', literal.strip(), flags=re.I)
                        owner = frozenset(_source_owner_identity(name))
                result.extend(units(child, owner, path + (key,), path + (key,)))
            return result
        return []

    active, previous_lane = frozenset(), object()
    frames = []
    for unit, declared, lane in units(statement):
        if lane != previous_lane:
            active, previous_lane = declared, lane
        named = _original_source_owner_keys(unit)
        if named:
            active = frozenset(named) if len(named) == 1 else frozenset()
        elif _structured_competing_head(unit):
            active = frozenset()
        frames.append(frozenset(value.split(':', 1)[1] for value in active
                                if value.startswith('component:')) if len(active) == 1 else frozenset())
    return frames


def _query_units(positive):
    units = re.split(r'[。；;！？\n]+|(?<=[.!?])\s+', positive)
    result = []
    for unit in units:
        # A renewed task verb marks an independent subquestion, without splitting
        # "initial read and subscribe" into unrelated requests.
        parts = re.split(r'\b(?:and|but)\s+(?=(?:review|debug|research|implement|repair|check|compare|distinguish|explain|describe)\b)'
                         r'|[，,]\s*(?:并且|同时|以及|并)?(?=(?:review|debug|research|implement|repair|check|compare|distinguish|explain|describe)\b|审查|排查|修复|检查|比较|区分|解释|说明)'
                         r'|(?:并且|同时|以及|并)(?=(?:审查|排查|修复|检查|比较|区分|解释|说明))', unit, flags=re.I)
        for part in parts:
            candidate = re.split(r'(\s+and\s+|以及|同时)', part, flags=re.I)
            # Ownerless conjuncts ("and subscription") stay with the preceding
            # task; a later explicit different owner starts its own task.
            current = candidate[0]
            current_subjects = task_subjects(current) - {'subscription', 'return_contract', 'allocation', 'task'}
            for index in range(2, len(candidate), 2):
                separator, value = candidate[index - 1], candidate[index]
                subjects = task_subjects(value) - {'subscription', 'return_contract', 'allocation', 'task'}
                if 'display' in current_subjects and not _precise_symbols(value):
                    subjects -= _displayed_data_subjects(value) - _explicit_task_owners(value)
                    if not _explicit_task_owners(value):
                        subjects.discard('spatial')
                continuation = re.match(r'\s*(?:(?:its?|the)\s+)?(?:author\s+)?'
                    r'(?:assum\w*|expect\w*|claim\w*|conclud\w*|believ\w*|say\w*)\b', value, re.I)
                continuation = continuation or (CONCRETE_BEHAVIOR.match(value.lstrip())
                    and not REQUEST_COMMAND.match(value.lstrip()))
                if current_subjects and subjects and not current_subjects & subjects and not continuation:
                    result.append(current)
                    current, current_subjects = value, subjects
                else:
                    current += separator + value
                    current_subjects |= subjects
            result.append(current)
    return [unit for unit in result if unit.strip()]


REQUEST_INTENT = re.compile(
    r'\b(?:review|debug|research|implement|repair|check|explain|describe|identify|assess|evaluate|clarify|sketch|compare|distinguish)\b'
    r'|\b(?:how|what|which|whether|why)\b|^\s*(?:give|state)\b'
    r'|审查|排查|修复|检查|说明|解释|比较|区分|请|如何|怎么|怎样|是什么|为什么|是否|能否|会不会|哪(?:个|条|些)'
    r'|\bhelp\s+me\b|\b(?:i|we)\s+(?:only\s+)?(?:need|want)\b', re.I)
REQUEST_REFERENCE = re.compile(
    r'\b(?:it|its|this (?:component|object|item|feature)|that (?:component|object|item|feature)|'
    r'the (?:same )?(?:component|object|item|feature))\b|它|该(?:组件|对象|物品|功能)|其(?:字段|数据|更新|保存|加载)', re.I)
DEICTIC_REQUEST = re.compile(
    r'\b(?:this|that|here|the (?:above|preceding) (?:problem|behavior|judgment|logic))\b'
    r'|这里|此处|上述|前述|这(?:条|个|段|处)(?:判断|逻辑|问题|行为|代码)?|该(?:判断|逻辑|问题)', re.I)
TYPED_REQUEST_REFERENCE = re.compile(
    r'\b(?:this|that|the (?:above|preceding))\s+'
    r'(?:claim|assumption|inference|assertion|statement|judgment|helper|function|method)\b'
    r'|这(?:条|个|处)(?:断言|假设|判断|结论|函数|方法)|该(?:断言|假设|判断|结论|函数|方法)', re.I)
REQUEST_CONTEXT_SUBJECTS = DOMAIN_SUBJECTS | {'display'}
REQUEST_COMMAND = re.compile(
    r'^\s*(?:read|write|save|load|restore|update|subscribe|bind|rebind|detach|cancel|remove'
    r'|consume|deduct|allocate|schedule|register|initialize|create|construct|return|check)\b'
    r'|^\s*(?:读取|写入|保存|加载|读档|恢复|更新|订阅|绑定|解绑|取消|移除|消费|扣除|分配|安排|登记|初始化|创建|构造)', re.I)
REQUEST_CONJUNCTION = re.compile(r'^\s*(?:and|but|以及|同时|并且|[,，;；])\s*$', re.I)
PROBLEM_PREMISE = re.compile(
    r'\b(?:assum\w*|expect\w*|claim\w*|conclud\w*|believ\w*|stale|missing|fails?|wrong|incorrect|problem|'
    r'too\s+(?:late|early)|author|patch|integration|unavailable|not\s+(?:ready|available))\b'
    r'|假定|假设|认定|认为|期待|声称|断言|作者|补丁|被当成|旧存档|缺(?:少|失|键)|报错|不产物|自动补跑|(?:还没|尚未|未)(?:有)?可用'
    r'|(?:把|将)[^。；;\n]{1,120}(?:当作|当成|视为)|\b(?:treat|regard)\w*\b[^.;\n]{1,120}\bas\b'
    r'|(?:出现|可见|可用|生成|选中|候选)[^。；;\n]{0,24}(?:却|然而|但是)[^。；;\n]{0,16}(?:拒|失败|不|未|没有)'
    r'|\b(?:appears?|visible|available|selected|candidates?)\b[^.;\n]{0,60}'
    r'\b(?:but|yet|however)\b[^.;\n]{0,60}\b(?:fail\w*|reject\w*|not|cannot)\b', re.I)
COLLECTIVE_REFERENCE = re.compile(
    r'\b(?:both|these|those|the (?:above|preceding)|those initializations)\b'
    r'|这(?:两|几|些)|上述|前述|各(?:自|放)', re.I)
COMPARISON_REQUEST = re.compile(
    r'\b(?:compare|comparison|distinguish|equivalent)\b|是否等价|比较|区分', re.I)


@memoized_analysis
def _comparison_navigation_text(text):
    # 先保留整段引号/括号状态，避免切分后的指令文字借用外层请求。
    quotes = {'"': '"', "'": "'", '`': '`', '“': '”', '‘': '’', '「': '」', '『': '』'}
    pairs = {'(': ')', '[': ']', '{': '}', '（': '）', '【': '】'}
    result, quote, escaped, stack, comment = [], None, False, [], False
    for index, char in enumerate(text):
        if comment:
            result.append(' ')
            if char == '\n':
                comment = False
        elif quote:
            result.append(' ')
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in quotes and not (char == "'" and index and index + 1 < len(text)
                                     and text[index - 1].isalnum() and text[index + 1].isalnum()):
            result.append(' ')
            quote = quotes[char]
        elif text.startswith('--', index):
            result.append(' ')
            comment = True
        elif char in pairs:
            result.append(' ')
            stack.append(pairs[char])
        elif char in pairs.values():
            result.append(' ')
            if not stack or stack.pop() != char:
                return None
        else:
            result.append(' ' if stack else char)
    return None if quote or stack else ''.join(result)


@memoized_analysis
def _visible_comparison_request(text, at=None):
    value = _comparison_navigation_text(text)
    if value is None:
        return False
    for marker in COMPARISON_REQUEST.finditer(value):
        if at is not None and marker.start() != at:
            continue
        boundaries = list(re.finditer(r'[。；;!?！？\n]|(?<=[.])\s+', value[:marker.start()]))
        prefix = value[boundaries[-1].end() if boundaries else 0:marker.start()]
        # 待审前提可含假设；只有比较指令自身的显式假设/背景语境阻止导航。
        if not re.search(r'\b(?:hypothesis|background)\s*[:：]|'
                         r'\b(?:hypothetical|hypothetically|suppose|supposing|assuming)\b|'
                         r'(?:假设|假定|假如|假想|背景)\s*[:：]', prefix, re.I):
            return True
    return False


SUMMARY_REQUEST = re.compile(
    r'\b(?:responsibilit\w*|scope|boundar\w*|independent pieces|actually follows|inference|defaults?|'
    r'initializations?|integration|equivalent|same fallback|layout)\b'
    r'|职责|责任|边界|假设|契约|默认值|是否等价|各放什么|初始化限制|资格|时点|布局|数量', re.I)
FOCUS_BOUNDARY = re.compile(
    r'\b(?:now\s+(?:only\s+)?(?:review|check|debug|research|focus|work)|'
    r'(?:i am|we are)\s+now\s+working)\b|现在(?:只|仅)|本次只|当前只', re.I)
BACKGROUND_BOUNDARY = re.compile(r'^\s*(?:background\s*:|背景\s*[:：])', re.I)


@memoized_analysis
def focused_task_query(query):
    """An explicit change of current work ends the previous problem paragraph."""
    match = FOCUS_BOUNDARY.search(query)
    if not match:
        return query
    start = max(query.rfind(mark, 0, match.start()) for mark in ('。', ';', '；', '\n')) + 1
    sentence = list(re.finditer(r'(?<=[.!?])\s+', query[:match.start()]))
    if sentence:
        start = max(start, sentence[-1].end())
    focused = query[start:].lstrip()
    # 切换当前对象不撤销已明确的全局排除或推断限制。
    prior_scope = query_scope(query[:start])
    constraints = ['Exclude ' + value for value in prior_scope['negative_clauses']]
    constraints += [value['clause'] for value in prior_scope['guard_clauses']]
    return focused + ('; ' + '; '.join(constraints) if constraints else '')


@memoized_analysis
def _request_is_question(unit):
    # “the review says”是待审断言，不是一次新的review指令。
    value = re.sub(r'\bthe\s+review\s+(?:says?|claims?|assumes?)\b', 'the author says', unit, flags=re.I)
    return bool(REQUEST_INTENT.search(value))


@memoized_analysis
def _request_context_owners(text):
    explicit = _explicit_task_owners(text)
    owners = explicit or (task_subjects(text) & REQUEST_CONTEXT_SUBJECTS)
    owners |= {'component:' + name for name in _business_component_names(text)
               if not task_subjects(name) & DOMAIN_SUBJECTS}
    # UI 的坐标是关系描述；明确具名的空间提供方仍是可请求的对象。
    if 'display' in owners and 'spatial' not in explicit:
        owners.discard('spatial')
    if 'display' in owners:
        owners -= _display_qualifier_subjects(text) - explicit
    return owners


@memoized_analysis
def _display_qualifier_subjects(text):
    """A domain modifying UI names that consumer, not a second owner."""
    phrases = re.findall(r'(?:[A-Za-z_]\w*(?:[ -]+[A-Za-z_]\w*)?|[\u3400-\u9fff]{1,8})\s*'
        r'(?:\b(?:hud|ui|panel|badge|widget|display|overlay)\b|界面|面板)', text, re.I | re.ASCII)
    return set().union(*(task_subjects(phrase) & DOMAIN_SUBJECTS for phrase in phrases
        if not re.search(r'\b(?:and|or)\b|和|与|及', phrase, re.I))) if phrases else set()


@memoized_analysis
def _premise_clauses(text):
    predicate = re.compile(CONCRETE_BEHAVIOR.pattern +
        r'|\b(?:assum\w*|expect\w*|claim\w*|conclud\w*|believ\w*|says?)\b'
        r'|假定|假设|认定|认为|期待|声称|断言|作者说|被用于|被当成', re.I)
    parts = re.split(r'([，,])', text)
    current, result = parts[0], []
    for index in range(2, len(parts), 2):
        separator, value = parts[index - 1], parts[index]
        conditional = re.search(r'\b(?:if|when|unless|while)\b|如果|仅当|若', current, re.I)
        current_predicate = bool(predicate.search(current) or PROBLEM_PREMISE.search(current) or
            _relations(current, query=True) & {'field_mutation', 'result_behavior'})
        next_predicate = bool(predicate.search(value) or PROBLEM_PREMISE.search(value) or
            _relations(value, query=True) & {'field_mutation', 'result_behavior'})
        if current_predicate and next_predicate and not conditional:
            result.append(current.strip())
            current = value
        else:
            current += separator + value
    if current.strip():
        result.append(current.strip())
    return result


@memoized_analysis
def task_requests(query):
    """Original subquestions and uniquely established request-side owner context.

    Bindings only navigate task relevance; they never add a source relation or a
    method identity. Multiple named owners prohibit ownerless pronoun binding.
    """
    positive = query_scope(focused_task_query(query))['positive_user_query']
    units = _query_units(positive)
    declared = set()
    frame = set()
    generic_component = False
    rows = []
    requested_rows = []
    unit_spans = []
    request_flags, nominal_flags, connectors = [], [], []
    cursor = 0
    previous_request = False
    for unit in units:
        start = positive.find(unit.strip(), cursor)
        connector = positive[cursor:start] if start >= cursor else ''
        if start >= cursor:
            cursor = start + len(unit.strip())
        unit_spans.append((start, cursor))
        explicit = _explicit_task_owners(unit)
        subjects = task_subjects(unit)
        domains = subjects & DOMAIN_SUBJECTS
        named_components = _business_component_names(unit)
        component_context = bool(COMPONENT_KEYS.search(unit) and not named_components
                                 and not explicit and not re.search(r'\bcomponents\b|多个组件', unit, re.I))
        objects = explicit or (domains if not component_context else set())
        typed_reference = bool(TYPED_REQUEST_REFERENCE.search(unit))
        reference_subject = typed_reference and not explicit and not named_components
        if reference_subject:
            objects = set()
        if not component_context and 'display' in subjects:
            displayed_data = _displayed_data_subjects(unit) - explicit
            objects = (objects - displayed_data - (_display_qualifier_subjects(unit) - explicit)) | {'display'}
            if 'spatial' not in explicit:
                objects.discard('spatial')
        # 一个未知命名组件不能借已知组件名或前句主体解释。
        unknown_objects = {'component:' + name for name in named_components
                           if not task_subjects(name) & DOMAIN_SUBJECTS}
        unit_objects = objects | unknown_objects
        if component_context and not (REQUEST_REFERENCE.search(unit) and len(frame) == 1):
            declared.add('entity_component')
            unit_objects.add('entity_component')
            generic_component = True
        declared.update(unit_objects)
        if unit_objects:
            # 新句明确重新声明当前对象；同句并列对象仍共享一个多 owner 框架。
            new_sentence = bool(rows and (re.search(r'[。；;！？\n]', connector) or
                                         re.search(r'[.!?]\s*$', rows[-1]['text'])))
            frame = set(unit_objects) if new_sentence else frame | unit_objects
        inherited = set()
        inherited_owner_context = set()
        reference = bool(REQUEST_REFERENCE.search(unit) or DEICTIC_REQUEST.search(unit) or typed_reference)
        question = _request_is_question(unit)
        relation_request = bool(_operations(unit) or (_relations(unit, query=True) - {'condition_dependency'}) or
                                semantic_concepts(unit) - BROAD_CONCEPTS - SUBJECT_CONCEPTS)
        # A governing task verb also selects a nominal conjunct whose vocabulary
        # has no predefined relation label. A new finite assertion stays background.
        predicate_head = re.match(r'\s*(?:(?:the|an?)\s+)?[A-Za-z_]\w*\s+', unit, re.I | re.ASCII)
        finite_assertion = bool(predicate_head and
            CONCRETE_BEHAVIOR.match(unit[predicate_head.end():]))
        continued_request = bool(previous_request and REQUEST_CONJUNCTION.fullmatch(connector)
                                 and (relation_request or not finite_assertion))
        requested = question or bool(REQUEST_COMMAND.search(unit)) or continued_request
        nominal = relation_request and not (predicate_head and
            CONCRETE_BEHAVIOR.match(unit[predicate_head.end():]))
        request_flags.append(requested)
        nominal_flags.append(nominal)
        connectors.append(connector)
        previous_request = requested
        if (not explicit and not named_components and (not domains or reference_subject)
                and (reference or question) and len(frame) == 1):
            inherited_owner_context = set(frame)
            inherited = frame & REQUEST_CONTEXT_SUBJECTS
        paths = _bounded_path_subjects(unit)
        operations = _operations(unit)
        if (generic_component and declared == {'entity_component'} and not named_components and not explicit
                and PERSIST_DETAIL.search(unit)
                and (operations & {'save_state', 'load_state', 'bind_reference'}
                     or semantic_concepts(unit) & {'missing_key', 'reference_binding'})):
            paths.add('entity_persistence_control_path')
        rows.append({'text': unit, 'explicit_question': question,
                     'inherited_subjects': sorted(inherited), 'request_paths': sorted(paths),
                      'inherited_owner_context': sorted(inherited_owner_context),
                     'owner_context_unique': len(frame) == 1,
                     'ambiguous_owner_reference': bool(reference and not objects and len(frame) > 1),
                     'effective_text': unit, 'context_units': [],
                     'requires_context_relation': bool(reference and not relation_request)})
        if requested:
            requested_rows.append(rows[-1])
    if not requested_rows:
        return rows
    # 前置名词任务须与后续请求明确并列；独立背景句不因后面出现命令而准入。
    selected = {index for index, requested in enumerate(request_flags) if requested}
    for index in range(len(rows) - 2, -1, -1):
        if (index + 1 in selected and nominal_flags[index]
                and REQUEST_CONJUNCTION.fullmatch(connectors[index + 1])):
            selected.add(index)
    for index in sorted(selected):
        row = rows[index]
        request_owners = set(row['inherited_subjects']) | (task_subjects(row['text']) & REQUEST_CONTEXT_SUBJECTS)
        if not (index and row['requires_context_relation'] and row['owner_context_unique']
                and request_owners and not row['ambiguous_owner_reference']):
            continue
        previous = rows[index - 1]['text']
        # 指回的问题只补当前请求；机制无法匹配时仍由 concrete_relation 拒绝。
        row['context_units'] = [previous]
        row['effective_text'] = previous + ' ' + row['text']
    # A definite nominal reference selects its original local object, not the
    # owner of an intervening sentence. Do not guess among repeated antecedents.
    for index in sorted(selected):
        row = rows[index]
        reference = re.search(r'\b(?:this|that|the\s+same)\s+([A-Za-z_]\w*)\b', row['text'], re.I)
        if (not index or not reference or row['context_units']
                or _explicit_task_owners(row['text']) or _business_component_names(row['text'])
                or _precise_symbols(row['text'])):
            continue
        noun = reference.group(1)
        antecedents = []
        for prior in range(index - 1, -1, -1):
            candidate = rows[prior]
            if BACKGROUND_BOUNDARY.search(candidate['text']) or prior in selected:
                break
            occurrences = list(re.finditer(r'\b' + re.escape(noun) + r's?\b', candidate['text'], re.I))
            antecedents.extend([candidate] * len(occurrences))
        if len(antecedents) != 1:
            continue
        candidate = antecedents[0]
        owners = _request_context_owners(candidate['text'])
        if len(owners) != 1:
            continue
        row.update(context_units=[candidate['text']],
                   effective_text=candidate['text'] + ' ' + row['text'],
                   inherited_subjects=sorted(owners & REQUEST_CONTEXT_SUBJECTS),
                   inherited_owner_context=sorted(owners), owner_context_unique=True,
                   ambiguous_owner_reference=False, context_role='REFERENT_ONLY')
    # 同一问题的待审假设可以跨句连续；普通背景操作仍不能成为新请求。
    for index in sorted(selected):
        row = rows[index]
        if not index or row['ambiguous_owner_reference'] or row['context_units']:
            continue
        text = row['text']
        collective = bool(COMPARISON_REQUEST.search(text) or
                          COLLECTIVE_REFERENCE.search(text) and not TYPED_REQUEST_REFERENCE.search(text))
        summary = bool(SUMMARY_REQUEST.search(text))
        typed_reference = bool(TYPED_REQUEST_REFERENCE.search(text))
        own = _request_context_owners(text)
        if (typed_reference and not _explicit_task_owners(text)
                and not _business_component_names(text)):
            own = set(row['inherited_owner_context'])
        elif not collective and not own:
            # 单数回指只沿最近的确定对象追溯；明确的复数/比较才可以跨对象回接。
            own |= set(row['inherited_owner_context'])
        previous = rows[index - 1]
        previous_owners = _request_context_owners(previous['text'])
        if own and previous_owners and not own & previous_owners:
            continue
        # An explicit review of a preceding assertion's relation (rather than a
        # newly named operation) points back even when it is not a summary noun.
        local_relation_review = bool(
            re.match(r'\s*(?:(?:please|请)\s*)?(?:review|check|assess|evaluate|审查|检查)', text, re.I)
            and not (_operations(text) or _precise_symbols(text) or _business_component_names(text))
            and not (_explicit_task_owners(text) or CONCRETE_BEHAVIOR.search(text)))
        if not (collective or summary or typed_reference or local_relation_review
                or not (_operations(text) or _relations(text, query=True))):
            continue
        # A declarative continuation in the same sentence belongs to its original
        # premise; do not borrow assertions across a sentence or background boundary.
        premise_start = index - 1
        while (premise_start and not PROBLEM_PREMISE.search(rows[premise_start]['text'])
               and REQUEST_CONJUNCTION.fullmatch(connectors[premise_start])
               and premise_start - 1 not in selected):
            premise_start -= 1
        linked_premise = bool(PROBLEM_PREMISE.search(rows[premise_start]['text']))
        if not (linked_premise or collective or typed_reference):
            continue
        context_indices = []
        for prior in range(index - 1, -1, -1):
            candidate = rows[prior]
            if BACKGROUND_BOUNDARY.search(candidate['text']):
                break
            if prior in selected and candidate['explicit_question']:
                break
            owners = _request_context_owners(candidate['text'])
            if own and owners and not own & owners:
                break
            if context_indices and not (PROBLEM_PREMISE.search(candidate['text']) or collective
                                        or prior >= premise_start):
                break
            context_indices.append(prior)
        if context_indices:
            row['context_units'] = [rows[prior]['text'] for prior in reversed(context_indices)]
            row['effective_text'] = ' '.join(row['context_units'] + [text])
    # 同句续接比较只保存导航来源；子问原文、操作和前提仍各自独立。
    for index in range(1, len(rows)):
        previous, current = rows[index - 1], rows[index]
        if (index not in selected or index - 1 not in selected or
                previous['ambiguous_owner_reference'] or current['ambiguous_owner_reference'] or
                not previous['owner_context_unique'] or not current['owner_context_unique'] or
                not re.match(r'\s*(?:(?:please|请)\s*)?(?:compare\b|distinguish\b|比较|区分)',
                             current['text'], re.I)):
            continue
        start, end = unit_spans[index - 1][0], unit_spans[index][1]
        compare_start = unit_spans[index][0]
        if (min(start, compare_start) < 0 or re.search(
                r'[。；;!?！？\n]|(?<=[.])\s+', positive[start:compare_start])):
            continue
        original = positive[start:end]
        marker = COMPARISON_REQUEST.search(current['text'])
        offset = compare_start - start + marker.start()
        # 原句之外开始的引号/括号也必须约束本句；重复原句不猜测其位置。
        if (query.count(original) != 1 or
                not _visible_comparison_request(query, at=query.find(original) + offset) or
                not _visible_comparison_request(original, at=offset)):
            continue
        before_owners = _request_context_owners(previous['effective_text'])
        after_owners = _request_context_owners(current['text'])
        if not before_owners or (after_owners and not after_owners <= before_owners):
            continue
        previous['comparison_navigation'] = {
            'schema': 'same-sentence-comparison-navigation/1',
            'original_sentence': original, 'request_text': previous['text'].strip(),
            'comparison_text': current['text'].strip(), 'comparison_marker_offset': offset}
    result = []
    for index, row in enumerate(rows):
        if index not in selected:
            continue
        text = row['text']
        if (index and re.search(r'\b(?:recorded\s+example|record|case|correction)\b|已有修正|原修正|案例|原记录', text, re.I)
                and any(structured_record_ids(prior['text']) for prior in rows[:index])):
            # A reference to the record is not a pronoun selecting one of the
            # components described inside that record.
            row['ambiguous_owner_reference'] = False
        # A following registration-identity question refers to the observer
        # just described, rather than switching to an account identity task.
        if (index and not row['context_units'] and
                re.search(r'\bregistration\s+identity\b|注册身份', text, re.I)
                and not _ACCOUNT_IDENTITY.search(text)
                and observer_registration_identity_request(rows[index - 1]['effective_text'])):
            row['context_units'] = [rows[index - 1]['effective_text']]
            row['effective_text'] = rows[index - 1]['effective_text'] + ' ' + text
        elif (index and not row['context_units'] and registration_state_request(text)
                and not task_subjects(text) & DOMAIN_SUBJECTS
                and not (_explicit_task_owners(text) or _business_component_names(text) or _precise_symbols(text))
                and not re.search(r'\b(?:other|another|different|instead)\b|另一个|其他|其它|改为', text, re.I)
                and registration_state_request(rows[index - 1]['effective_text'])):
            row['context_units'] = [rows[index - 1]['effective_text']]
            row['effective_text'] = rows[index - 1]['effective_text'] + ' ' + text
        collective = bool(COMPARISON_REQUEST.search(text) or
                          COLLECTIVE_REFERENCE.search(text) and not TYPED_REQUEST_REFERENCE.search(text))
        bare_review = not (_operations(text) or _relations(text, query=True))
        summary_review = bool(SUMMARY_REQUEST.search(text))
        premises = [part for unit in row['context_units'] for part in _premise_clauses(unit)]
        if len(premises) <= 1 or not (collective or bare_review or summary_review):
            result.append(row)
            continue
        if summary_review and not bare_review:
            # The summary's explicit subquestions remain requests in their own
            # right; selecting prior assertions must not replace them.
            result.append({**row, 'effective_text': text, 'context_units': []})
        # 合集审查只把每条原命题变成被请求的子框架，不混合彼此操作。
        for premise in premises:
            # A domain noun such as recipe/material is not a literal Builder
            # receiver. Only an identifiable object can be an inherited owner.
            owners = _explicit_task_owners(premise) | {
                'component:' + name for name in _business_component_names(premise)
                if not task_subjects(name) & DOMAIN_SUBJECTS}
            result.append({**row, 'text': premise, 'request_origin_text': text,
                'premise_origin_text': next(unit for unit in row['context_units'] if premise in unit),
                'effective_text': premise, 'context_units': [premise],
                'inherited_subjects': sorted(owners & REQUEST_CONTEXT_SUBJECTS),
                'inherited_owner_context': sorted(owners), 'owner_context_unique': len(owners) == 1,
                'ambiguous_owner_reference': False, 'requires_context_relation': False})
    separated = []
    strict_relations = {'operation_order', 'mechanism_distinction', 'observer_registration_identity',
                        'reference_binding_phase'}
    for row in result:
        # A literal API selector may govern several nominal attributes. Preserve
        # that selector for identity, while each attribute supplies its own
        # requested predicate; a name like RemoveX is not an imperative to remove.
        nominal = re.match(r'^(.*?的)([^。；;\n]+)$', row['text'])
        if nominal and _precise_symbols(nominal.group(1)):
            attributes = re.split(r'、|与|及|和', nominal.group(2))
            if (len(attributes) > 1 and all(value.strip() for value in attributes)
                    and not any(_operations(value) or CONCRETE_BEHAVIOR.search(value)
                                or _explicit_task_owners(value) or _business_component_names(value)
                                for value in attributes)):
                for value in attributes:
                    request = nominal.group(1) + value.strip()
                    separated.append({**row, 'text': request, 'effective_text': request,
                                      'context_units': [], 'predicate_text': value.strip(),
                                      'request_origin_text': row['text']})
                continue
        parts = re.split(r'、|,\s+and\s+', row['text'], flags=re.I)
        frames = [request_relations(part) & strict_relations for part in parts]
        independent = (len(parts) > 1 and not row['context_units'] and
                       all(frames) and len(set().union(*frames)) > 1 and
                       not set.intersection(*(set(frame) for frame in frames)))
        if not independent:
            separated.append(row)
            continue
        # Independent nominal subquestions keep the same established owner,
        # while each relation earns its own original-atom support.
        for part in parts:
            separated.append({**row, 'text': part.strip(), 'effective_text': part.strip(),
                              'request_origin_text': row['text']})
    return separated


@memoized_analysis
def effective_task_query(query):
    """Original requested frames with only their explicitly linked problem text."""
    return '; '.join(row['effective_text'] for row in task_requests(query))


@memoized_analysis
def _explicit_task_owners(text):
    """Component selectors and named receivers outrank resource/input nouns."""
    delivery_subject = _literal_delivery_named_subject(text)
    if delivery_subject:
        return _source_owner_identity(delivery_subject)
    names = (re.findall(r'([A-Za-z_]\w*|[\u3400-\u9fff]{1,16})\s*(?:组件|component\b)', text, re.I)
             if re.search(r'组件|component\b', text, re.I) else [])
    names += re.findall(r'\b(?:AddComponentPostInit|AddComponent)\s*\(\s*[\'\"]([A-Za-z_]\w*)[\'\"]', text, re.ASCII)
    names += re.findall(r'\.components\.([A-Za-z_]\w*)', text, re.ASCII)
    names += re.findall(r'\b(?:healer|eater|fueled|perishable|workable|pickable|burnable|rechargeable|finiteuses'
                        r'|deployable|upgradeable|repairable|builder|timer|cooldown)\b', text, re.I)
    names += [match.group(1) or match.group() for match in re.finditer(
        r'\b([A-Za-z_]\w*)(?:[.:][A-Za-z_]\w*)+|\b[A-Z][A-Za-z0-9_]*\b', text, re.ASCII)]
    def owners(name):
        # Prefer the literal identifier's domain to a parent noun introduced
        # only by CamelCase separation (a callback name is not a second owner).
        literal = {domain for domain in DOMAIN_SUBJECTS if SUBJECT_REGEX[domain].search(name)}
        return literal or (task_subjects(name) & DOMAIN_SUBJECTS)
    return set().union(*(owners(name) for name in names if name)) if names else set()


@memoized_analysis
def _displayed_data_subjects(text):
    values = re.findall(r'(?:显示|展示|\b(?:show\w*|display\w*|render\w*)\b)'
                        r'([^，,。；;\n!?！？]{1,48})', text, re.I)
    return set().union(*(task_subjects(value) & DOMAIN_SUBJECTS for value in values)) if values else set()


def _bound_method_head(unit, context):
    """Existing METHOD_SUBJECT roles can bind a local head, never a callee."""
    if not _original_atom(context):
        return set()
    bindings = [binding for binding in context.get('role_bindings', [])
                if isinstance(binding, dict) and binding.get('role') == 'METHOD_SUBJECT'
                and binding.get('receiver') and binding.get('symbol')]
    # A preceding branch condition does not change the named method subject.
    head = re.sub(r'^\s*[^，,。；;\n]*后[，,]\s*', '', unit)
    owners = set()
    for binding in bindings:
        symbol = binding['symbol']
        bare = symbol.rsplit(':', 1)[-1].rsplit('.', 1)[-1]
        for spelling in (symbol, bare):
            if not re.match(r'\s*' + re.escape(spelling) + r'(?![A-Za-z0-9_])', head, re.ASCII):
                continue
            peers = [other for other in bindings if other['symbol'].rsplit(':', 1)[-1].rsplit('.', 1)[-1] == bare]
            if spelling == bare and len({other['receiver'] for other in peers}) != 1:
                continue
            owners |= task_subjects(binding['receiver']) & DOMAIN_SUBJECTS
    return owners if len(owners) == 1 else set()


def _named_relation_owner(unit):
    delivery_subject = _literal_delivery_named_subject(unit)
    if delivery_subject:
        return _source_owner_identity(delivery_subject)
    # Uppercase action/constants and lowercase field paths are not new owners.
    names = (re.findall(r'([A-Za-z_]\w*|[\u3400-\u9fff]{1,16})\s*(?:组件|component\b)', unit, re.I)
             if re.search(r'组件|component\b', unit, re.I) else [])
    owner_text = re.sub(r'\b([A-Za-z_]\w*)(?:[.:][A-Za-z_]\w*)+', r'\1', unit, flags=re.ASCII)
    names += [name for name in re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', owner_text, re.ASCII) if not name.isupper()]
    return set().union(*(task_subjects(name) & DOMAIN_SUBJECTS for name in names)) if names else set()


PLAYER_OWNER = re.compile(r'\b(?:players?|theplayer)\b|玩家', re.I | re.ASCII)
PLAYER_PHASE = re.compile(r'\b(?:onnewspawn|new[ -]?spawn|resume(?:existingusersession)?|makeplayercharacter'
                          r'|common_postinit|master_postinit|construct\w*)\b|出生|新生|构造', re.I | re.ASCII)
PLAYER_PHASE_RELATIONS = {
    'new_spawn': re.compile(r'\b(?:onnewspawn|new[ -]?spawn)\b|出生|新生', re.I | re.ASCII),
    'construct': re.compile(r'\b(?:makeplayercharacter|common_postinit|master_postinit|construct\w*)\b|构造', re.I | re.ASCII),
    'resume': re.compile(r'\bresume(?:existingusersession)?\b|(?:已有|既有|旧)玩家.{0,16}(?:读档|恢复)', re.I | re.ASCII),
}
PERSIST_FRAMEWORK = re.compile(r'\b(?:getpersistdata|setpersistdata|getsaverecord'
                               r'|serializeusersession|resumeexistingusersession)\b', re.I | re.ASCII)
PERSIST_DETAIL = re.compile(r'\b(?:keys?|payload|data|records?|refs|newents|postpass|loadpostpass)\b'
                            r'|键|字段|数据|引用|存档', re.I | re.ASCII)
COMPONENT_KEYS = re.compile(r'\b(?:components?|cmp)\b|组件', re.I | re.ASCII)


@memoized_analysis
def _business_component_names(text):
    names = (re.findall(r'([A-Za-z_]\w*|[\u3400-\u9fff]{1,16})\s*(?:组件|component\b)', text, re.I | re.ASCII)
             if re.search(r'组件|component\b', text, re.I | re.ASCII) else [])
    # 中文请求动词是语法前缀；去掉后仍有名字时，未知组件照常阻断继承。
    prefix = r'^(?:(?:帮我|我(?=给|为|将|把)|我需要|我准备|我要|我想|请|需要|应该|先|再|只|也|给|为|对|替|将|把|和|与|及|跨|检查|审查|排查|修复|说明|解释|初始化|构造|创建|加载|恢复|保存|移除|删除|实现|读取|写入|更新))+'
    names = [re.sub(prefix, '', name) if re.fullmatch(r'[\u3400-\u9fff]+', name) else name
             for name in names]
    possessive = r'^(?:我们|你们|他们|她们|它们|我|你|您|他|她|它)(?:自己)?的'
    names = [re.sub(possessive, '', name) for name in names]
    generic = {'player', 'entity', 'custom', 'matching', 'each', 'gameplay', 'server', 'client',
               'local', 'input', 'item', '对应', '匹配', '玩家', '实体', '物品',
               '自定义', '自定义玩家', '自定义实体', '该', '某', '所有', '保存', '缺少',
               '跨', '多', '多个', '多种', '不同', '各个', '各类', '若干', '其他', '其它', '别的',
               'cross', 'multiple', 'several', 'various', 'other', 'another', 'either', 'neither',
               'any', 'every', 'different', 'all', 'some',
               '以', '按', '把', '只把', '将', '各', '其', 'traverses', 'collects', 'dispatches',
               'missing', 'saved', 'corresponding', 'no', 'a', 'an', 'the',
               'this', 'that', 'these', 'those', 'its', 'my', 'our', 'your',
               '本', '此', '这个', '那个', '一个', '每个', '当前', '现有', '已有', '原有', '旧', '新'}
    # 谓词后的完整泛指称呼不声明业务名；“旧法力”等仍有名字的对象不匹配。
    generic_reference = (r'(?:(?:才|就|也|仍|还|在|不|会|能|要|重新|让|使|留|使用|持有)|(?:'
                         + CONCRETE_BEHAVIOR.pattern + r'))+(?:着|了|过)?'
                         r'(?:本|此|该|其|这个|那个|一个|每个|当前|现有|已有|原有|旧|新)')
    # A determiner at the end of a Chinese predicate selects an unnamed component;
    # the preceding sentence fragment is not its business identifier.
    generic_tail = re.compile(r'(?:跨|(?:这|那|每|某|一|多|各)(?:一)?(?:个|种|类)'
                              r'(?:(?:服务端|客户端|本地|自定义))?|(?:另|这|那)一)$')
    return {name.lower() for name in names if name and name.lower() not in generic
            and not (re.fullmatch(r'[\u3400-\u9fff]+', name) and generic_tail.search(name))
            and not re.fullmatch(generic_reference, name, re.I | re.ASCII)
            and not CONCRETE_BEHAVIOR.fullmatch(name)
            and not re.search(r'(?:和|与|及|后|时|再|然后)(?:' + CONCRETE_BEHAVIOR.pattern + r')$', name, re.I)
            and not re.search(r'(?:将|把|以|按|的|其|各|该|某|对应|匹配|哪个|哪些|某个|各个|保存|缺少|所有|全部|每个|任意|任何)$', name)}


@memoized_analysis
def _unknown_condition_owner(text):
    # 就绪关系不能借 HUD 等已知消费者绕过请求中的未知业务主体。
    names = _business_component_names(text)
    names |= {match.group(1).lower() for match in re.finditer(
        r'\b([A-Za-z_]\w*)[.:][A-Za-z_]\w*', text, re.ASCII)
        if match.group(1).lower() not in {'self', 'inst', 'item', 'entity', 'target', 'doer'}}
    return any(not task_subjects(name) for name in names)


def _verified_method_head(unit, context):
    if not _original_atom(context):
        return set(), set()
    bindings = [binding for binding in context.get('role_bindings', [])
                if isinstance(binding, dict) and binding.get('role') == 'METHOD_SUBJECT'
                and isinstance(binding.get('symbol'), str)
                and re.fullmatch(r'[A-Za-z_]\w*[.:][A-Za-z_]\w*', binding.get('symbol', ''), re.ASCII)
                and isinstance(binding.get('receiver'), str) and binding.get('receiver')]
    symbols, owners = set(), set()
    head = re.sub(r'^\s*[^，,。；;\n]*后[，,]\s*', '', unit)
    for binding in bindings:
        symbol = binding['symbol']
        bare = re.split(r'[.:]', symbol)[-1]
        peers = [other for other in bindings if re.split(r'[.:]', other['symbol'])[-1] == bare]
        for spelling in (symbol, bare):
            if spelling == bare and len({other['receiver'] for other in peers}) != 1:
                continue
            if re.match(r'\s*' + re.escape(spelling) + r'(?![A-Za-z0-9_])', head, re.ASCII):
                symbols |= _precise_symbols(symbol) | _precise_symbols(bare)
                owners |= task_subjects(binding['receiver']) & DOMAIN_SUBJECTS
    return symbols, owners


def _bounded_path_subjects(text, source=False, context=''):
    """Original framework relations and explicit task paths, never mechanism owners."""
    if SOURCE_METADATA_LABEL.search(text) or (source and not _original_atom(context)):
        return set()
    result = set()
    framework = bool(PERSIST_FRAMEWORK.search(text))
    concrete_component = bool(_business_component_names(text) or _explicit_task_owners(text))
    operations = _operations(text, source=source)
    details = bool(PERSIST_DETAIL.search(text))
    entity_owner = bool(PLAYER_OWNER.search(text) or re.search(r'\bentity\b|实体', text, re.I)
                        or (not source and re.search(r'角色', text) and PLAYER_PHASE.search(text)))
    generic_component = bool(COMPONENT_KEYS.search(text) and not concrete_component)
    if source:
        relation = bool(_concrete_behavior(text, context) or EVIDENCE_BOUNDARY.search(text))
        key_relation = generic_component and bool(re.search(r'\b(?:keys?|pairs|matching|table|onsave|onload)\b'
                                                           r'|键|遍历|非空|派发|分派', text, re.I | re.ASCII))
        record_relation = bool(re.search(r'\b(?:record|refs|newents|loadpostpass)\b', text, re.I | re.ASCII))
        if framework and relation and not concrete_component and (key_relation or record_relation):
            result.add('entity_persistence_control_path')
        verified, _ = _verified_method_head(text, context)
        verified_player = any(isinstance(binding, dict) and binding.get('role') == 'METHOD_SUBJECT'
                              and isinstance(binding.get('receiver'), str)
                              and PLAYER_OWNER.search(binding['receiver'])
                              and isinstance(binding.get('symbol'), str)
                              and binding.get('symbol', '').lower() in verified
                              for binding in context.get('role_bindings', []))
        if PLAYER_PHASE.search(text) and relation and (entity_owner and PLAYER_OWNER.search(text) or verified_player):
            result.add('player_lifecycle_path')
    else:
        exact_relation = bool(operations & {'save_state', 'load_state', 'bind_reference'}
                              or semantic_concepts(text) & {'missing_key', 'reference_binding'})
        if not concrete_component and details and exact_relation and (framework or entity_owner or generic_component):
            result.add('entity_persistence_control_path')
        player_task = bool(PLAYER_OWNER.search(text) or re.search(r'角色', text))
        if not concrete_component and player_task and PLAYER_PHASE.search(text):
            result.add('player_lifecycle_path')
    return result


def _bounded_hud_construction(text, context):
    if not _original_atom(context) or SOURCE_METADATA_LABEL.search(text):
        return False
    return bool(re.search(r'\b(?:onsetowner|theplayer|playerhud)\b|本地玩家', text, re.I)
                and re.search(r'\b(?:master|theplayer)\b|本地玩家|分支|条件', text, re.I)
                and re.search(r'建立\s*(?:HUD|控制资源)(?![A-Za-z0-9_]|文件|目录|文档|资料|方案|计划)', text, re.I))


def _bounded_path_hits(query, unit, context):
    paths = _bounded_path_subjects(query) & _bounded_path_subjects(unit, source=True, context=context)
    if 'bind_reference' in _operations(query) and 'bind_reference' not in _operations(unit, source=True):
        paths.discard('entity_persistence_control_path')
    return paths


def _embedded_condition_call(unit, context):
    if not _original_atom(context):
        return False
    calls = list(re.finditer(r'\b([A-Za-z_]\w*[.:][A-Za-z_]\w*)\s*\(', unit, re.ASCII))
    if len(calls) != 1 or calls[0].start() == 0:
        return False
    call = calls[0]
    prefix, suffix = unit[:call.start()], unit[call.end():]
    identities = {binding.get('symbol', '').lower() for binding in context.get('role_bindings', [])
                  if isinstance(binding, dict) and binding.get('role') in (
                      'METHOD_SUBJECT', 'BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL',
                      'BOUNDED_CALLEE_RELATION_UNDETERMINED')}
    return bool(call.group(1).lower() in identities
                and len(task_subjects(re.split(r'[.:]', call.group(1))[0]) & DOMAIN_SUBJECTS) == 1
                and re.search(r'(?:且|若|如果|当|除非|\b(?:if|unless|when|and|or))\s*$', prefix, re.I)
                and not _concrete_behavior(prefix, context)
                and not task_subjects(prefix) & DOMAIN_SUBJECTS
                and not _named_relation_owner(prefix)
                and not _structured_competing_head(prefix)
                and not _explicit_task_owners(suffix)
                and not _named_relation_owner(suffix)
                and not _structured_competing_head(suffix))


@memoized_analysis
def _task_request_analysis(query, _request_frames=None):
    """Query-only features; source owner state stays inside task_support."""
    scope = query_scope(query)
    # 子问分解保留原请求的主体绑定；重新解析省略主语的字符串会丢失唯一 owner。
    requests = task_requests(query) if _request_frames is None else _request_frames
    positive = '; '.join(row['effective_text'] for row in requests)
    requested_subjects = task_subjects(positive) | _bounded_path_subjects(positive)
    excluded_subjects = set().union(*(task_subjects(value) | _bounded_path_subjects(value)
                                    for value in scope['negative_clauses'])) if scope['negative_clauses'] else set()
    excluded_subjects -= _explicit_task_owners(positive)
    if _relations(positive, query=True) or _operations(positive):
        excluded_subjects -= requested_subjects
    # 请求特征只依赖本次输入；可变路径、命中和关系集合仍在每个源分句独立创建。
    unknown_condition_owner = _unknown_condition_owner(scope['positive_user_query'])
    multiple_query_domains = len(task_subjects(scope['positive_user_query']) & DOMAIN_SUBJECTS) > 1
    request_features = []
    for request_info in requests:
        request = request_info['effective_text']
        predicate = request_info.get('predicate_text', request)
        concepts = frozenset(semantic_concepts(request))
        operations = frozenset(_operations(predicate))
        relations = frozenset(_relations(predicate, query=True))
        symbols = frozenset(_precise_symbols(request))
        explicit_owners = frozenset(_explicit_task_owners(request))
        unknown_owners = frozenset(value.split(':', 1)[1]
            for value in request_info.get('inherited_owner_context', []) if value.startswith('component:'))
        unknown_owners |= frozenset(name for name in _business_component_names(request)
                                    if not task_subjects(name) & DOMAIN_SUBJECTS)
        condition_reference_ambiguous = bool(
            REQUEST_REFERENCE.search(request_info['text']) and multiple_query_domains
            and not _explicit_task_owners(request_info['text']))
        local_unknown_condition_owner = unknown_condition_owner
        if _request_frames is not None:
            condition_reference_ambiguous = request_info['ambiguous_owner_reference']
            local_unknown_condition_owner = _unknown_condition_owner(request) or bool(unknown_owners)
        request_features.append({
            'info': request_info, 'concepts': concepts, 'operations': operations,
            'relations': relations, 'symbols': symbols, 'explicit_owners': explicit_owners,
            'inherited_unknown_owners': unknown_owners,
            'subjects': frozenset(task_subjects(request) | set(request_info['inherited_subjects'])),
            'paths': frozenset(request_info['request_paths']),
            'displayed_data': frozenset(_displayed_data_subjects(request) - explicit_owners)
                              if not symbols else frozenset(),
            'lexical': frozenset(_lexical_tokens(request)),
            'pure_subject_browse': (not relations and not operations
                                    and not (concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS)
                                    and _pure_subject_browse(request)),
            'knowledge_consultation': (request_info['explicit_question']
                and not symbols and not operations and not relations
                and not (concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS)
                and _bounded_knowledge_consultation(request)),
            'player_phases': frozenset(name for name, pattern in PLAYER_PHASE_RELATIONS.items()
                                      if pattern.search(request)),
            'block_condition_dependency': local_unknown_condition_owner or condition_reference_ambiguous,
            'callee_contract_request': bool('argument_binding' in relations or
                concepts & {'return_false', 'return_nil', 'return_contract'} or
                re.search(r'\breturns?\b|返回|返回值', request, re.I)),
        })
    return scope, requested_subjects, excluded_subjects, request_features


@analyzed_request
def task_support(query, statement, context='', _request_frames=None):
    """Match a concrete original relation to one bounded task subquestion.

    context accepts original scope text, or {'scope': text, 'receivers': [owner]}.
    It supplies only a narrow omitted subject, never the requested mechanism.
    """
    scope, requested_subjects, excluded_subjects, request_features = _task_request_analysis(
        query, _request_frames)
    inherited = _narrow_context(context)
    matches = []
    previous_owner = set()
    previous_owner_seen = False
    active_method_symbols = set()
    typed_ellipsis = _original_atom(context)
    role_owner = set()
    excluded_relation_owners = set()
    previous_lane = object()
    structured_owner_blocked = False
    unknown_source_frames = (iter(_source_unknown_owner_frames(statement))
        if any(features['inherited_unknown_owners'] for features in request_features) else None)
    for unit, structured_owner, lane in _structured_source_units(statement):
        unknown_source_owners = next(unknown_source_frames) if unknown_source_frames is not None else frozenset()
        if lane != previous_lane:
            previous_owner, previous_owner_seen = set(), False
            active_method_symbols, role_owner = set(), set()
            structured_owner_blocked = False
            previous_lane = lane
        if not unit.strip():
            continue
        condition_frame = ((set(previous_owner), previous_owner_seen,
                            set(active_method_symbols), set(role_owner))
                           if len(previous_owner) == 1 and active_method_symbols
                           and _embedded_condition_call(unit, context) else None)
        # 具名方法头里的成员词不能伪造另一 owner（例如 Timer:Launch 的 Launch）。
        delivery_subject = _literal_delivery_named_subject(unit)
        subject_text = delivery_subject or re.sub(
            r'^(\s*[A-Z][A-Za-z0-9_]*)[.:][A-Za-z_]\w*', r'\1', unit, flags=re.ASCII)
        local_subjects = task_subjects(subject_text)
        if delivery_subject:
            local_subjects |= _source_owner_identity(delivery_subject)
        path_subjects = _bounded_path_subjects(unit, source=True, context=context)
        local_subjects |= path_subjects
        local_role_owner = _bound_method_head(unit, context)
        named_owner = _named_relation_owner(unit)
        macro_subjects = set().union(*(task_subjects(name) & DOMAIN_SUBJECTS
                                      for name in re.findall(r'\b[A-Z][A-Z0-9_]{2,}\b', unit, re.ASCII)))
        argument_macro_subjects = set().union(*(task_subjects(name) & DOMAIN_SUBJECTS
                                               for name in re.findall(r'\b[A-Z][A-Z0-9_]*\.([A-Z][A-Z0-9_]*)\b', unit, re.ASCII)))
        named_calls = re.findall(r'\b([A-Za-z_]\w*)(:)([A-Za-z_]\w*)', unit, re.ASCII)
        named_calls += re.findall(r'\b([A-Za-z_]\w*)(\.)([A-Za-z_]\w*)\s*\(', unit, re.ASCII)
        bound_calls = {binding.get('symbol') for binding in context.get('role_bindings', [])
                       if isinstance(binding, dict) and binding.get('role') in
                       ('BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')} if isinstance(context, dict) else set()
        unknown_call_owner = any(owner not in {'self', 'inst', 'target', 'doer', 'item', 'act', 'data', 'source'}
                                 and owner + separator + member not in bound_calls
                                 for owner, separator, member in named_calls)
        if local_role_owner:
            role_owner = local_role_owner
        elif unknown_call_owner or (named_owner and role_owner and not named_owner & role_owner):
            role_owner = set()
        relation_subjects = ((local_subjects - DOMAIN_SUBJECTS) | role_owner) if role_owner else local_subjects
        if typed_ellipsis and (_concrete_behavior(unit, context) or EVIDENCE_BOUNDARY.search(unit)):
            # Only a proved relation owner creates a whole-atom delivery conflict.
            proved_owners = role_owner or named_owner or (_explicit_task_owners(unit) - macro_subjects)
            excluded_relation_owners |= proved_owners & excluded_subjects
            excluded_relation_owners |= path_subjects & excluded_subjects
        local_owners = relation_subjects - {'return_contract', 'allocation'} - (argument_macro_subjects - role_owner - named_owner)
        explicit_domains = local_owners & DOMAIN_SUBJECTS
        # A competing concrete component always beats scope/receiver context.
        receivers = re.findall(r'\b([A-Za-z_]\w*)[.:]([A-Za-z_]\w*)', unit, re.ASCII)
        explicit_receiver = any(owner.lower() not in {'self', 'inst', 'target', 'doer', 'item', 'act', 'data', 'source'}
                                and not (owner.isupper() and member.isupper()) for owner, member in receivers)
        head_symbols, _ = _verified_method_head(unit, context)
        method_head = re.match(r'\s*(?:[A-Za-z_]\w*[.:][A-Za-z_]\w*|[A-Z][A-Za-z0-9_]*)(?=\(|\s|[\u3400-\u9fff])', unit, re.ASCII)
        new_head = bool(method_head and method_head.group().strip().lower() not in {'it', 'its', 'self'})
        if (structured_owner and new_head and not explicit_domains and not head_symbols
                and not CONCRETE_BEHAVIOR.match(unit.lstrip())
                and not _operations(method_head.group())):
            structured_owner_blocked = True
            previous_owner, previous_owner_seen = set(), True
        if _structured_competing_head(unit):
            structured_owner_blocked = True
            previous_owner, previous_owner_seen = set(), True
        explicit_continuation = bool(re.search(r'\b(?:it|its|self)\b|此函数|该方法', unit, re.I))
        if head_symbols:
            active_method_symbols = head_symbols
        elif new_head or unknown_call_owner or explicit_receiver or named_owner:
            active_method_symbols = set()
        continuation_behavior = bool(active_method_symbols and explicit_continuation
                                     and not SOURCE_METADATA_LABEL.search(unit)
                                     and re.search(CONCRETE_BEHAVIOR.pattern, unit, re.I | re.ASCII))
        inherited_symbols = (active_method_symbols if not head_symbols and explicit_continuation
                             and (_concrete_behavior(unit, context) or continuation_behavior
                                  or EVIDENCE_BOUNDARY.search(unit)) else set())
        omitted_self = bool(re.search(r'\b(?:self|inst|it|this (?:component|object|method))\b|它|其(?:字段|回调|返回|对象|任务)|该(?:对象|组件|实体|方法)', unit, re.I))
        context_owner = inherited if not previous_owner_seen and not local_owners else set()
        if omitted_self:
            context_owner = previous_owner if previous_owner_seen else inherited
        elif typed_ellipsis and previous_owner_seen and not local_owners and not explicit_receiver:
            context_owner = previous_owner
        if structured_owner is None and not previous_owner_seen:
            context_owner = set()
        if (structured_owner and not structured_owner_blocked and not local_owners
                and (not previous_owner_seen or previous_owner == structured_owner)):
            context_owner |= structured_owner
        if explicit_domains or explicit_receiver:
            context_owner = set()
        source_subjects = relation_subjects | context_owner
        if len(local_owners) == 1:
            previous_owner = local_owners
            previous_owner_seen = True
        elif typed_ellipsis and len(explicit_domains) == 1:
            # Display/replica labels can describe one concrete component owner.
            previous_owner = explicit_domains
            previous_owner_seen = True
        elif explicit_domains:
            previous_owner = set()
            previous_owner_seen = True
        elif explicit_receiver:
            # An unrecognized named receiver is a new owner, not an omitted
            # pronoun referring to the preceding known component.
            previous_owner = set()
            previous_owner_seen = True
        source_concepts = semantic_concepts(unit)
        metadata_source = bool(SOURCE_METADATA_LABEL.search(unit))
        boundary_marker = _behavior_evidence_boundary(unit, context)
        evidence_boundary = not metadata_source and bool(boundary_marker)
        # 未证明/未验收本身不是所请求机制的行为；普通工程问题不由通用免责声明准入。
        boundary_only = evidence_boundary and (
            isinstance(context, dict) and context.get('atom_kind') in ('UNK', 'BOUNDARY') or
            not _concrete_behavior(unit[:boundary_marker.start()], context))
        source_witness = _source_relation_witness(unit, context)
        behavior = (source_witness['concrete_behavior'] or continuation_behavior) and not boundary_only
        original_kinds = (set(context.get('atom_kind', '').replace(' ', '').split('/'))
                          if isinstance(context, dict) else set())
        consultation_original = bool(original_kinds and original_kinds <= {'NSF', 'REC', 'EI'}
            and context.get('record_pointer')) if isinstance(context, dict) else False
        consultation_advice = bool(original_kinds & {'REC', 'EI'} and KNOWLEDGE_ADVICE.search(unit))
        source_operations = source_witness['operations']
        source_domains = source_subjects & DOMAIN_SUBJECTS
        source_symbols = _precise_symbols(unit) | head_symbols | inherited_symbols
        source_lexical = _lexical_tokens(unit)
        for features in request_features:
            request_info = features['info']
            request = request_info['effective_text']
            query_concepts = features['concepts']
            query_paths = set(features['paths'])
            persistence_match = ('entity_persistence_control_path' in query_paths and
                                 'entity_persistence_control_path' in path_subjects and
                                 not ('bind_reference' in features['operations'] and
                                      'bind_reference' not in source_operations))
            if not persistence_match:
                query_paths.discard('entity_persistence_control_path')
            query_subjects = features['subjects'] | query_paths
            subject_hits = query_subjects & source_subjects
            query_domains = query_subjects & DOMAIN_SUBJECTS
            symbols = features['symbols'] & source_symbols
            requested_operations = features['operations']
            operation_hits = set(requested_operations & source_operations)
            periodic_update = {'schedule_task', 'update_state'} <= requested_operations
            if periodic_update and 'schedule_task' not in source_operations:
                operation_hits.discard('update_state')
            explicit_query_owners = features['explicit_owners']
            consumer_relations = {name for name in query_concepts & source_concepts & {'initial_read', 'subscription'}
                                  if MECHANISM_BEHAVIOR[name].search(unit)}
            display_consumer = bool('display' in query_subjects & source_subjects and consumer_relations)
            # 展示的数据不是初读/订阅操作的 owner；精确方法和显式组件仍保留原门禁。
            displayed_data = features['displayed_data'] if display_consumer else set()
            operation_domains = query_domains - displayed_data
            if 'entity_persistence_control_path' in subject_hits and not explicit_query_owners:
                operation_domains = set()
            mismatch = bool(operation_domains and not operation_domains & source_domains and not symbols)
            mismatch |= bool(query_subjects and not subject_hits and not symbols)
            mismatch |= bool(explicit_query_owners and not explicit_query_owners & source_domains and not symbols)
            if features['inherited_unknown_owners']:
                mismatch |= not bool(features['inherited_unknown_owners'] & unknown_source_owners)
            # Initial UI reads require a display consumer in the fact, rather
            # than an arbitrary component that happens to register an event.
            mismatch |= bool('display' in query_subjects and 'initial_read' in query_concepts
                             and 'display' not in source_subjects and not symbols)
            mechanisms = (query_concepts & source_concepts) - BROAD_CONCEPTS - SUBJECT_CONCEPTS
            mechanisms = {name for name in mechanisms
                          if name not in MECHANISM_BEHAVIOR or MECHANISM_BEHAVIOR[name].search(unit)}
            if 'player_lifecycle_path' in subject_hits:
                mechanisms |= {'player_phase:' + name for name in features['player_phases']
                               if PLAYER_PHASE_RELATIONS[name].search(unit)}
            relations = set(features['relations'] & source_witness['relations'])
            if features['block_condition_dependency']:
                relations.discard('condition_dependency')
            if periodic_update and 'schedule_task' not in source_operations:
                mechanisms.discard('scheduled_task')
                relations.discard('field_mutation')
            # Generic "persistence/result/callback" mentions cannot replace an
            # explicitly requested load branch, argument list, or false/nil result.
            if requested_operations & {'save_state', 'load_state'}:
                mechanisms.discard('persistence')
                relations.discard('field_mutation')
                relations.discard('callback_binding')
            if requested_operations & {'consume_resource', 'allocate_resource'}:
                mechanisms -= {'resource_consumption', 'resource_allocation'}
                relations.discard('field_mutation')
            if query_concepts & {'return_false', 'return_nil'}:
                relations.discard('result_behavior')
            if 'argument_binding' in features['relations']:
                relations.discard('callback_binding')
                if 'argument_binding' not in source_witness['relations']:
                    relations.discard('numeric_value')
            scoped_cleanup = ('cleanup' in query_concepts & source_concepts and
                              bool(subject_hits & {'subscription', 'task', 'stategraph', 'modifier', 'buff', 'display'}) and
                              bool(re.search(r'(?:cancel\w*|remove\w*|detach\w*|clear\w*|clean\w*).{0,24}(?:listener|task|handle|state|modifier|buff|hud)'
                                             r'|(?:listener|task|handle|state|modifier|buff|hud).{0,32}(?:cancel\w*|remove\w*|detach\w*|clear\w*|clean\w*)'
                                             r'|(?:取消|清理|解绑|移除|撤销).{0,18}(?:任务|监听|订阅|状态|贡献|修饰|增益|界面)'
                                             r'|(?:任务|监听|订阅|状态|贡献|修饰|增益|界面).{0,22}(?:取消|清理|解绑|移除|撤销)', unit, re.I)))
            lexical = features['lexical'] & source_lexical
            # Unknown vocabulary must still describe a concrete original behavior.
            lexical_anchor = (not query_subjects and not (query_concepts - BROAD_CONCEPTS)
                              and not requested_operations and not features['relations']
                              and len(lexical) >= 2 and behavior)
            subject_only = bool(subject_hits and not (query_concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS)
                                and not features['relations'] and not requested_operations and behavior
                                and features['pure_subject_browse']
                                and not (subject_hits & macro_subjects - role_owner - named_owner))
            literal_content = bool(subject_hits and behavior and not requested_operations
                                   and not features['relations']
                                   and not (query_concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS)
                                   and not (subject_hits & macro_subjects - role_owner - named_owner)
                                   and _literal_content_match(request, unit))
            # 复用问题只获得原知识的相关性；同句真实主体和行为/原建议不能由元数据补出。
            knowledge_consultation = bool(features['knowledge_consultation'] and consultation_original
                and subject_hits & local_subjects - macro_subjects
                and not KNOWLEDGE_SOURCE_LABEL.search(unit) and not boundary_only
                and (behavior or consultation_advice))
            negative_scope = bool(source_subjects & excluded_subjects and not symbols)
            special_source = source_domains & {'shard', 'death', 'reroll', 'snapshot'}
            special_unrequested = bool(special_source and not query_subjects & special_source and
                                       scope['ordinary'] and not ORDINARY.search(unit))
            concrete_relation = mechanisms | relations | {'operation:' + name for name in operation_hits}
            boundary_relevant = evidence_boundary and bool(
                'boundary' in query_concepts or scope['guard_clauses'] or symbols or
                ('condition_dependency' in relations and subject_hits) or
                ((named_owner | role_owner) & query_domains and concrete_relation))
            # A symbol is an identity/navigation anchor. Natural tasks still need
            # an actual original behavior or an explicit evidence limitation.
            symbol_relation = bool(symbols and (behavior or boundary_relevant) and
                                   (concrete_relation or not (requested_operations or
                                    query_concepts - BROAD_CONCEPTS - SUBJECT_CONCEPTS or features['relations'])))
            supported = not (mismatch or negative_scope or special_unrequested or metadata_source) and bool(
                symbol_relation or (subject_hits and (behavior or boundary_relevant) and concrete_relation)
                or scoped_cleanup or lexical_anchor or subject_only or literal_content or knowledge_consultation)
            if request_info['requires_context_relation'] and not concrete_relation:
                supported = False
            if request_info['ambiguous_owner_reference']:
                supported = False
            # “supported”只表示任务相关。callee 的不调用证据不能借用同
            # atom 中 caller 的参数/返回行为；原 NSF 仍可用于反证检索。
            role_bindings = context.get('role_bindings', []) if isinstance(context, dict) else []
            matched_bindings = [binding for binding in role_bindings if isinstance(binding, dict)
                                and binding.get('symbol', '').lower() in features['symbols']]
            noncalling_callee_only = bool(matched_bindings) and all(binding.get('role') in
                ('BOUNDED_CALLEE_NONCALL', 'BOUNDED_CALLEE_RELATION_UNDETERMINED')
                for binding in matched_bindings)
            if noncalling_callee_only and features['callee_contract_request']:
                supported = False
            described_subjects = (query_concepts & source_concepts & SUBJECT_CONCEPTS) if supported and (concrete_relation or scoped_cleanup) else set()
            matches.append({'supported': supported, 'support_meaning': 'TASK_RELEVANCE_ONLY',
                            'query_assertion_verified': False,
                            'relation_evidence_roles': sorted({binding.get('role') for binding in matched_bindings if binding.get('role')}),
                            'mechanism_hits': sorted(concrete_relation | described_subjects),
                            'subject_hits': sorted(subject_hits), 'source_subjects': sorted(source_subjects),
                            'local_source_subjects': sorted(local_subjects), 'inherited_source_subjects': sorted(context_owner),
                            'inherited_source_symbols': sorted(inherited_symbols),
                            'requested_subjects': sorted(query_subjects), 'matched_symbols': sorted(symbols),
                            'displayed_data_subjects': sorted(displayed_data),
                            'requested_operation_subjects': sorted(operation_domains),
                            'display_consumer_relation': display_consumer,
                            'bounded_knowledge_consultation': knowledge_consultation,
                            'displayed_data_contract_verified': False,
                            'subject_mismatch': mismatch, 'scoped_cleanup': scoped_cleanup,
                            'excluded_source_scope': negative_scope or special_unrequested,
                            'operation_hits': sorted(operation_hits),
                            'requested_operations': sorted(requested_operations),
                            'support_type': 'evidence_boundary' if evidence_boundary else 'behavior' if behavior else 'none',
                            'concrete_behavior': behavior, 'lexical_hits': sorted(lexical),
                            'source_unit': unit, 'task_unit': request_info['text'],
                            'effective_task_unit': request, 'request_context_units': request_info['context_units'],
                            'relation_role_subjects': sorted(role_owner),
                             'bounded_source_paths': sorted(path_subjects),
                             'bounded_query_paths': sorted(query_paths),
                             'verified_method_head_symbols': sorted(head_symbols),
                            'anchors': sorted(symbols | subject_hits | mechanisms | relations | lexical)})
        if condition_frame is not None:
            # 条件里的已绑定调用保留本句关系，但不接管外层方法后续省略主语的分句。
            previous_owner, previous_owner_seen, active_method_symbols, role_owner = condition_frame
    if not matches:
        return {'supported': False, 'support_meaning': 'TASK_RELEVANCE_ONLY',
                'query_assertion_verified': False, 'whole_atom_delivery_allowed': False,
                'whole_atom_excluded_relation_owners': sorted(excluded_relation_owners),
                'mechanism_hits': [], 'subject_hits': [], 'source_subjects': [],
                'requested_subjects': sorted(requested_subjects), 'matched_symbols': [],
                'subject_mismatch': False, 'scoped_cleanup': False, 'lexical_hits': [], 'source_unit': '', 'anchors': [],
                'supported_task_units': []}
    result = max(matches, key=lambda item: (item['supported'], not item['subject_mismatch'],
                                         len(item['matched_symbols']), len(item['mechanism_hits']),
                                         len(item['subject_hits']), len(item['lexical_hits'])))
    result['whole_atom_excluded_relation_owners'] = sorted(excluded_relation_owners)
    result['whole_atom_delivery_allowed'] = bool(result['supported'] and not excluded_relation_owners)
    # 保留全部已成立的子问题相关性；它不证明请求闭合或事实断言。
    result['supported_task_units'] = list(dict.fromkeys(item['task_unit'] for item in matches if item['supported']))
    return result

@memoized_analysis
def semantic_concepts(text):
    value = _semantic_text(text)
    persistence = _persistence_text(value)
    found = {name for name,pattern in SEMANTIC_REGEX.items()
             if pattern.search(persistence if name == 'persistence' else
                               _return_contract_text(value) if name == 'return_nil' else value)}
    if observer_registration_identity_request(value) and not _ACCOUNT_IDENTITY.search(value):
        found.discard('identity')
    if data_consumption(value):
        found.difference_update(('material', 'resource_consumption'))
    if 'display' in found and _display_change_contrast(value):
        found.update(('initial_read', 'subscription'))
    return found


@memoized_analysis
def _display_change_contrast(text):
    """A first-display/change-update contrast is a task, not a proved cause."""
    entry = re.search(r'\b(?:first (?:open\w*|render\w*|display\w*|show\w*)|initial (?:render|display)'
                      r'|(?:enter|join|open|reopen)\w*)\b|首次|第一次|初次|进入|加入|打开|新建|重建', text, re.I)
    absent = re.search(r'\b(?:blank|empty|missing|not (?:shown|displayed|showing))\b'
                       r'|空白|为空|没有显示|不显示|未显示', text, re.I)
    if not entry or not absent or abs(entry.start() - absent.start()) > 100:
        return False
    if re.search(r'\bnot (?:blank|empty|missing)\b|不是空白|并非空白|并不为空', text, re.I):
        return False
    return bool(re.search(
        r'\bonly\b[^。；;\n!?]{0,60}\b(?:after|when|once)\b[^。；;\n!?]{0,60}'
        r'\b(?:updat\w*|refresh\w*|show\w*|display\w*|render\w*|appear\w*)\b'
        r'|\bonly\b[^。；;\n!?]{0,30}\b(?:updat\w*|refresh\w*|show\w*|display\w*|render\w*|appear\w*)\b'
        r'[^。；;\n!?]{0,30}\b(?:after|when|once)\b[^。；;\n!?]{1,60}'
        r'|\bafter\b[^。；;\n!?]{0,40}\b(?:change\w*|event\w*)\b[^。；;\n!?]{0,40}'
        r'\b(?:updat\w*|refresh\w*|show\w*|display\w*|render\w*|appear\w*)\b'
        r'|只有[^。；;\n!?]{1,40}(?:后|时|才)[^。；;\n!?]{0,16}(?:更新|显示|出现|刷新)'
        r'|变化[^。；;\n!?]{0,16}(?:后|时)[^。；;\n!?]{0,12}(?:更新|显示|出现|刷新)', text, re.I))

@memoized_analysis
def expand_semantic_query(query):
    positive=query_scope(query)['positive_query']
    found=semantic_concepts(positive)
    navigable=found-BROAD_CONCEPTS
    if 'display' in found and navigable & {'initial_read','subscription','construction','local_player',
                                         'authority_gate','display_authority_gate'}:
        navigable.add('display')
    extra=[SEMANTIC_NAVIGATION[c] for c in sorted(navigable) if c in SEMANTIC_NAVIGATION]
    return positive+' '+' '.join(extra)


def _guard(marker, content):
    inference = INFERENCE.search(content)
    inference_head = re.match(r'^\s*(?:假定|认为|宣称|assum(?:e|es|ed|ing)\b|claim(?:s|ed|ing)?\b|infer(?:s|red|ring)?\b)', content, re.I)
    if TOPIC_EXCLUSION.fullmatch(marker.strip()) and not (
            marker.strip().lower() == 'without' and (inference_head or inference)):
        return None
    # 不改变功能是范围排除；只有真实证据推断才保留该主题作边界审查。
    if marker == '不改变' and not inference:
        return None
    if not (REVIEW_PROHIBITION.search(content) or marker in ('不改变', '不保证')):
        return None
    subject = content[:inference.start()] if inference else content
    target = content[inference.end():].strip() if inference else ''
    subject = re.sub(r'^\s*(?:使用|用|把|将|拿|利用|use\b|using\b|treat\b)\s*', '', subject, flags=re.I)
    subject = re.sub(r'(?:来|去|\bto)\s*$', '', subject, flags=re.I).strip()
    # 无来源的 assume/claim 是被拒绝的结论，不是该结论所指主题的检索请求。
    if inference_head:
        subject, target = '', content.strip()
    if marker == '不保证':
        subject, target = '', content.strip()
    return {'subject': subject, 'rejected_inference': target, 'clause': marker + content}


def _negative_markers(value):
    for marker in NEGATIVE_MARKER.finditer(value):
        # A connected word is one lexical item, not an imperative exclusion.
        # Test the token boundary rather than listing particular compounds.
        if marker.group().isascii() and (
                re.search(r'[A-Za-z0-9_][\-\u2010-\u2015]\s*$', value[:marker.start()]) or
                re.match(r'[\-\u2010-\u2015][A-Za-z0-9_]', value[marker.end():])):
            continue
        # not only… 是正向并列，不能把首项当作主题排除。
        if marker.group().lower() == 'not' and re.match(r'\s+only\b', value[marker.end():], re.I):
            continue
        # 正反疑问及其中的否定命题仍是待审对象；新分句的真实排除不继承疑问保护。
        contrast_exclusion = (marker.group() == '不是' and
                              re.search(r'(?<!反)而\s*$', value[:marker.start()]))
        if not contrast_exclusion and any(question.start() <= marker.start() < question.end() or
               question.end() <= marker.start() and not QUESTION_SCOPE_BREAK.search(
                   value[question.end():marker.start()])
               for question in CHINESE_POLAR_QUESTION.finditer(value)):
            continue
        prefix = re.split(r'(?<=[.!?])\s+', value[:marker.start()])[-1]
        if (marker.group().lower() in {'no', 'not', 'without', 'never', 'cannot', "can't", 'can’t',
                                       'do not', "don't", 'don’t'} and
                re.search(r'\b(?:whether|if)\b', prefix, re.I) and
                (REQUEST_INTENT.search(prefix) or REQUEST_COMMAND.search(prefix))):
            # The negative proposition is being reviewed. A following explicit
            # exclude/ignore instruction is still a separate scope constraint.
            continue
        description_pattern = (
            r'\b(?:appears?|animates?|runs?|works?|loads?|starts?|exists?|continues?|returns?|'
            r'assumes?|expects?|has|have|had|contains?|there (?:is|are|was|were))\b')
        descriptive = re.search(description_pattern, prefix, re.I)
        request_head = bool(REQUEST_INTENT.match(prefix.lstrip()) or REQUEST_COMMAND.match(prefix.lstrip()))
        relative_parts = re.split(r'\b(?:that|which|who|whose)\b', prefix, flags=re.I)
        relative_description = len(relative_parts) > 1 and re.search(description_pattern, relative_parts[-1], re.I)
        if marker.group().lower() in {'no', 'without'} and (not request_head or relative_description) and (
                re.search(r'\bwith\s*$', prefix, re.I) or descriptive) and not re.match(
                r'\s*(?:interest|need|intention|wish|desire)\b', value[marker.end():], re.I):
            continue
        if marker.group().lower() in {'do not', "don't", 'don’t'} and re.search(
                r'\b(?:it|they|players?|objects?|components?|servers?|clients?)\s*$', prefix, re.I):
            continue
        if marker.group().lower() == 'no' and re.search(
                r'\b(?:has|have|had|contains?|there (?:is|are|was|were))\s*$', value[:marker.start()], re.I) and not re.match(
                r'\s*(?:interest|need|intention|wish|desire)\b', value[marker.end():], re.I):
            continue
        if marker.group().lower() == 'not' and re.search(
                r'\b(?:is|are|was|were|does|did|has|have|will|would|could|can)\s*$', value[:marker.start()], re.I):
            continue
        if marker.group() == '别':
            prefix, content = value[:marker.start()], value[marker.end():]
            # 词内字符不是祈使否定；请/也等短前缀仍可引出真实祈使。
            boundary = not prefix or not re.search(r'\w$', prefix) or re.search(r'(?:请|也|先|务必|千万|你(?:们)?|您|咱们|我们|大家)$', prefix)
            # 独立“别”不限定后续动词，避免漏掉“别碰”等真实禁止；别名是词内形式。
            if not boundary or content.startswith('名'):
                continue
        yield marker


_POSITIVE_FOCUS = re.compile(
    r'(?:只|仅)(?:核对|评审|审查|检查|查验|研究|讨论|关注|考虑|看|查)\s*'
    r'|\b(?:only|solely|exclusively)\s+(?:review|check|audit|inspect|research|examine|consider|focus\s+on)\s+'
    r'|\b(?:review|check|audit|inspect|research|examine|consider)\s+(?:only|solely|exclusively)\s+', re.I)


def _exact_owner_path_focus(query, visible):
    """Resolve an exact path's unique preceding call as task identity only."""
    name = r'[A-Za-z_][A-Za-z0-9_]*(?:[.:][A-Za-z_][A-Za-z0-9_]*)*'
    commands = list(re.finditer(r'\b(?:review|check|audit|inspect|research|examine|consider|'
                               r'explain|describe|debug|implement)\b', visible, re.I))
    exact = list(re.finditer(
        r'\b(?:review|check|audit|inspect|research|examine|consider)\s+'
        r'(?:this|that)\s+exact\s+(?P<owner>' + name + r')\s+path\b', visible, re.I))
    if len(exact) != 1 or len(commands) != 1:
        return None
    match = exact[0]
    if re.search(r'\bnot\s*$|不$', visible[:match.start()], re.I):
        return None
    owner = match.group('owner')
    if owner.lower() in LEXICAL_STOP | {'object', 'item', 'component', 'same', 'current'}:
        return None
    # An additional broad object is a separate requested scope, even when it
    # shares the review verb. Do not silently turn that task into one method.
    if re.search(r'\b(?:other|all|every|any|broader)\s+(?:\w+\s+){0,3}'
                 r'(?:paths?|components?|methods?|functions?|systems?)\b',
                 visible[match.end():], re.I):
        return None
    prefix = visible[:match.start()]
    calls = list(re.finditer(r'\b(?:calls?|invokes?)\s+(?:the\s+)?'
                            r'(?P<name>' + name + r')(?![A-Za-z0-9_])', prefix, re.I))
    targets = set()
    for call in calls:
        if re.search(r'\b(?:not|never|without)\s*$', prefix[:call.start()], re.I):
            continue
        target = call.group('name')
        if target.lower() in LEXICAL_STOP | {'method', 'function', 'callback', 'it', 'them'}:
            continue
        # An unparsed call-object list is ambiguous, not an invitation to pick
        # its first callable. A later independent calls/invokes is counted too.
        if re.match(r'\s*(?:\([^()]*\)\s*)?(?:/|,|\band\b|\bor\b|\bthen\b)', prefix[call.end():], re.I):
            return None
        targets.add(target.lower().replace('.', ':'))
    if len(targets) != 1:
        return None
    target = next(iter(targets))
    if ':' in target:
        call_owner, method = target.rsplit(':', 1)
        if call_owner != owner.lower().replace('.', ':'):
            return None
    else:
        method = target
    return {'exclusive': True, 'symbols': [owner.lower().replace('.', ':') + ':' + method],
            'subjects': sorted(task_subjects(owner)), 'clause': query[match.start():].strip()}


@memoized_analysis
def _positive_focus(query):
    """An explicit exclusive task object, kept separate from negative clauses."""
    visible = _data_quote_view(query, literal_names=True)
    matches = [match for match in _POSITIVE_FOCUS.finditer(visible)
               if not re.search(r'\bnot\s*$|不$', visible[:match.start()], re.I)]
    if not matches:
        return (_exact_owner_path_focus(query, visible) or
                {'exclusive': False, 'symbols': [], 'subjects': [], 'clause': ''})
    match = matches[-1]
    end = re.search(r'[。；;!?！？\n]|(?<=\.)\s+', visible[match.end():])
    tail = visible[match.end():match.end() + end.start()] if end else visible[match.end():]
    # The exclusive object precedes its requested predicates. Other APIs in the
    # predicate or background must not become additional permitted objects.
    target = re.match(r'\s*(?:(?:the|function|method|component)\s+)*'
                      r'([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)(?![A-Za-z0-9_])', tail, re.I | re.ASCII)
    symbols = []
    record_object = bool(target and target.group(1).lower() in {
        'recorded', 'documented', 'existing', 'record', 'records', 'example', 'case', 'cases',
        'correction', 'corrections', 'rule', 'rules'} and structured_record_ids(tail))
    if target and target.group(1).lower() not in LEXICAL_STOP | {
            'callbacks', 'callback', 'behavior', 'behaviour', 'ordering', 'events', 'event',
            'scope', 'body', 'methods', 'functions', 'components', 'if', 'whether', 'why',
            'recorded', 'documented', 'existing', 'record', 'records', 'example', 'case', 'cases',
            'correction', 'corrections', 'rule', 'rules'}:
        symbols = [target.group(1).lower().replace('.', ':')]
    subjects = set() if record_object else task_subjects(target.group(1) if symbols else tail)
    return {'exclusive': True, 'symbols': symbols, 'subjects': sorted(subjects),
            'clause': query[match.start():match.end() + len(tail)].strip()}


def positive_focus_support(query, statement, context=''):
    """Check exclusive object identity; this never supplies a source relation.

    Use original atom context (METHOD_SUBJECT bindings, original narrow scope),
    not a title or navigation match. A callee occurrence cannot stand for its
    caller's subject. The caller should apply its ordinary eligibility gates too.
    """
    parsed = query_scope(query)
    focus = parsed['positive_focus']
    result = {'allowed': True, 'reason': 'NO_EXCLUSIVE_OBJECT', 'positive_focus': focus}
    # Keep the requested callback object through both task selection and later
    # context additions. A field-change callback cannot witness another named
    # callback merely because both belong to the same component.
    from .relevance_frames import callback_object_scope_conflict
    if callback_object_scope_conflict(parsed['positive_user_query'], _text(statement), context):
        return {**result, 'allowed': False, 'reason': 'CALLBACK_OBJECT_SCOPE_MISMATCH'}
    excluded_relations = set().union(*(engineering_relations(clause, source=False)
                                       for clause in parsed['negative_clauses'])) if parsed['negative_clauses'] else set()
    excluded_relations &= engineering_relations(_text(statement), source=True)
    if excluded_relations:
        return {**result, 'allowed': False, 'reason': 'SOURCE_RELATION_EXPLICITLY_EXCLUDED',
                'excluded_relations': sorted(excluded_relations)}
    identity = context.get('original_record_identity', {}) if isinstance(context, dict) else {}
    negative_ids = set().union(*(structured_record_ids(clause) for clause in parsed['negative_clauses'])) if parsed['negative_clauses'] else set()
    if isinstance(identity.get('id'), str) and identity['id'].upper() in negative_ids:
        return {**result, 'allowed': False, 'reason': 'ORIGINAL_RECORD_EXPLICITLY_EXCLUDED'}
    if not focus['exclusive'] or not (focus['symbols'] or focus['subjects']):
        return result
    wanted = set(focus['symbols'])
    def matches(name):
        # A constant field such as REGISTRY.OPERATION is an identity in another
        # namespace, not the bare CamelCase method named in an exclusive task.
        parts = re.split(r'[.:]', name)
        if len(parts) > 1 and parts[0].isupper() and parts[1].isupper():
            return name.lower().replace('.', ':') in wanted
        name = name.lower().replace('.', ':')
        return any(name == goal or ':' not in goal and name.rsplit(':', 1)[-1] == goal
                   for goal in wanted)
    bindings = context.get('role_bindings', []) if isinstance(context, dict) else []
    bound = {row.get('symbol', '') for row in bindings
             if row.get('role') == 'METHOD_SUBJECT' and row.get('symbol')}
    qualified_bound = {name for name in bound if ':' in name or '.' in name}
    if qualified_bound:
        bare_aliases = {re.split(r'[.:]', name)[-1].lower() for name in qualified_bound}
        bound = qualified_bound | {name for name in bound if name.lower() not in bare_aliases}
    if wanted and bound:
        result.update(allowed=all(matches(name) for name in bound),
                      reason='EXCLUSIVE_METHOD_SUBJECT_MATCH' if all(matches(name) for name in bound)
                      else 'EXCLUSIVE_METHOD_SUBJECT_MISMATCH')
        return result
    original_index = context.get('original_content_index', {}) if isinstance(context, dict) else {}
    indexed = original_index.get('original_method_subjects', {}).get(context.get('record_pointer')) if isinstance(context, dict) else None
    if wanted and indexed:
        allowed = all(matches(name) for name in indexed)
        result.update(allowed=allowed, reason='EXCLUSIVE_ORIGINAL_SUBJECT_MATCH' if allowed
                      else 'EXCLUSIVE_ORIGINAL_SUBJECT_MISMATCH')
        return result
    heads = set()
    for unit in _source_units(statement):
        head = re.match(r'\s*(?:function\s+)?([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)', unit, re.ASCII)
        if head:
            name = head.group(1)
            if matches(name) or re.search(r'[.:_]|[a-z][A-Z]', name):
                heads.add(name)
    if wanted and heads:
        allowed = all(matches(name) for name in heads)
        result.update(allowed=allowed, reason='EXCLUSIVE_LITERAL_SUBJECT_MATCH' if allowed
                      else 'EXCLUSIVE_LITERAL_SUBJECT_MISMATCH')
        return result
    if wanted:
        # Only an original narrow, uniquely named scope can identify an omitted
        # subject. Role bindings naming another callee cannot do this.
        original_scope = context.get('scope', '') if isinstance(context, dict) else context
        scope_names = _precise_symbols(_text(original_scope))
        scope_names |= {name for name in wanted if re.search(
            r'(?<![A-Za-z0-9_:.])' + re.escape(name) + r'(?![A-Za-z0-9_])',
            _text(original_scope), re.I | re.ASCII)}
        allowed = bool(scope_names) and all(matches(name) for name in scope_names)
        result.update(allowed=allowed, reason='EXCLUSIVE_ORIGINAL_SCOPE_MATCH' if allowed
                      else 'EXCLUSIVE_SUBJECT_NOT_ESTABLISHED')
        return result
    method_rows = [row for row in bindings if row.get('role') == 'METHOD_SUBJECT' and row.get('symbol') in bound]
    method_owners = set()
    unresolved_method_owner = False
    for row in method_rows:
        owner = row.get('receiver') or re.split(r'[.:]', row.get('symbol', ''))[0]
        domains = task_subjects(owner) & DOMAIN_SUBJECTS
        method_owners |= domains
        unresolved_method_owner |= not bool(domains)
    if unresolved_method_owner:
        return {**result, 'allowed': False, 'reason': 'EXCLUSIVE_BEHAVIOR_SUBJECT_UNRESOLVED'}
    if method_owners:
        # Original behavior subjects survive their own callee gates and local
        # configuration words. A second physical subject is still an owner.
        callee_owners = set().union(*(task_subjects(row.get('receiver') or row.get('symbol', '').split(':')[0].split('.')[0])
                                     for row in bindings if row.get('role') in ('BOUNDED_CALLEE_CALLSITE', 'BOUNDED_CALLEE_NONCALL'))) & DOMAIN_SUBJECTS
        literal_owners = set()
        for unit in _source_units(statement):
            head = re.match(r'\s*(?:The\s+)?([A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*)', unit, re.ASCII)
            if head:
                name = head.group(1)
                literal_owners |= task_subjects(name) & DOMAIN_SUBJECTS
                if (':' in name and re.split(r'[.:]', name)[0].lower() not in {'self', 'inst', 'target', 'act', 'data'}
                        and not any(row.get('symbol', '').lower().replace('.', ':') == name.lower().replace('.', ':')
                                    for row in bindings)):
                    return {**result, 'allowed': False, 'reason': 'EXCLUSIVE_BEHAVIOR_SUBJECT_UNRESOLVED'}
        owners = method_owners | (literal_owners - callee_owners)
    else:
        owners = task_subjects(_text(statement)) & DOMAIN_SUBJECTS
    owners = owners or (_narrow_context(context) & DOMAIN_SUBJECTS)
    wanted_owners = set(focus['subjects']) & DOMAIN_SUBJECTS
    allowed = not wanted_owners or bool(owners) and owners <= wanted_owners
    result.update(allowed=allowed, reason='EXCLUSIVE_DOMAIN_MATCH' if allowed else 'EXCLUSIVE_DOMAIN_MISMATCH')
    return result


@memoized_analysis
def query_scope(query):
    negative, replacements, user_replacements, guards = [], [], [], []
    # 逗号可以连接排除列表；句号/分号终止排除，明确的任务动词可重新进入正向范围。
    for clause in re.finditer(r'[^。；;\n!?！？]+', query):
        value = clause.group()
        markers = list(_negative_markers(value))
        for index, marker in enumerate(markers):
            end = markers[index + 1].start() if index + 1 < len(markers) else len(value)
            content = value[marker.end():end]
            sentence_end = re.search(r'\.(?=\s+[A-Za-z])', content)
            if sentence_end:
                content = content[:sentence_end.end()]
            guard = _guard(marker.group(), content)
            boundary = REENTRY.search(content)
            # The excluded object's first word may itself be a task/API noun
            # ("exclude REPAIR sample"); it cannot reopen positive intent.
            if (boundary and (not guard or boundary.start() > 0)
                    and content[:boundary.start()].strip(' ，,')):
                content = content[:boundary.start()]
                guard = _guard(marker.group(), content)
            if not content.strip():
                continue
            start = clause.start() + marker.start()
            finish = clause.start() + marker.end() + len(content)
            if guard:
                guards.append(guard)
                replacements.append((start, finish, guard['subject'] + ' boundary review '))
                user_replacements.append((start, finish, guard['subject'] + ' '))
            else:
                negative.append(content.strip(' ，,'))
                replacements.append((start, finish, ' '))
                user_replacements.append((start, finish, ' '))
    positive = query
    for start, end, replacement in sorted(replacements, reverse=True):
        positive = positive[:start] + replacement + positive[end:]
    positive_user = query
    for start, end, replacement in sorted(user_replacements, reverse=True):
        positive_user = positive_user[:start] + replacement + positive_user[end:]
    deep = bool(DEEP.search(positive))
    ordinary = bool(ORDINARY.search(positive))
    exclusive_query = re.sub(r'\bnot\s+only\b', 'both', positive, flags=re.I)
    only_ordinary = bool(re.search(r'(?:只(?:看|修|查|要)|\bonly\b).*?(?:普通|通用|ordinary|normal|generic|general)', exclusive_query, re.I))
    role = None
    for name, pattern in [('debug', r'排错|排查|报错|崩溃|\b(?:debug|troubleshoot)\b'),
                          ('review', r'审查|审计|\b(?:review|audit)\b'),
                          ('research', r'研究|深入|\b(?:research|anatomy)\b'),
                          ('implement', r'实现|修复|怎么写|\b(?:implement|fix|repair|build)\b')]:
        if re.search(pattern, positive, re.I):
            role = name
            break
    return {'positive_query': positive, 'positive_user_query': positive_user,
            'negative_clauses': negative, 'guard_clauses': guards,
            'positive_focus': _positive_focus(positive_user),
            'record_references': sorted(structured_record_ids(positive_user)),
            'ordinary': ordinary, 'generic': bool(re.search(r'通用|一般契约|\b(?:generic|general)\b', positive, re.I)),
            'deep_requested': deep,
            'deep_forbidden': any(DEEP_EXCLUSION.search(c) for c in negative) or (only_ordinary and not deep),
            'special_lifecycle_requested': bool(SPECIAL_LIFECYCLE.search(positive)),
            'task_role': role}
