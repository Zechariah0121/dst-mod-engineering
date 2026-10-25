"""Compositional problem relations for retrieval, never inferred source facts."""
from functools import lru_cache
import re

if __package__:
    from . import predicate_grammar as _predicate_module
else:
    import importlib.util
    from pathlib import Path
    _predicate_spec = importlib.util.spec_from_file_location(
        '_dst_kb_predicate_grammar', Path(__file__).with_name('predicate_grammar.py'))
    _predicate_module = importlib.util.module_from_spec(_predicate_spec)
    _predicate_spec.loader.exec_module(_predicate_module)


def _pattern(value):
    return re.compile(value, re.I | re.ASCII)


_READ = _pattern(r'\b(?:read\w*|get|gets|getting|obtain\w*|fetch\w*|query\w*|render\w*|show\w*|display\w*|getters?)\b|读|获取|取得|获得|显示|展示|渲染')
_CURRENT_DATA = _pattern(r'\b(?:current|present|existing|initial|latest)\s+(?:\w+\s+){0,2}(?:values?|states?|data|snapshot)|\b(?:first read|initial read|getter snapshot)\b|(?:当前|现在|现有|已有|初始|最新)(?:的|可读)?(?:值|数值|状态|数据)|初读|初值')
_RESOURCE = _pattern(r'\b(?:tasks?|handles?|handlers?|listeners?|callbacks?|subscriptions?|observers?|watchers?|pendingtasks|modifiers?|eventlistener|eventlistening|do(?:periodic)?taskintime|listenforevent|removeeventcallback)\b|任务|延迟效果|句柄|监听|订阅|回调|观察器|修饰器|事件边')
_RESOURCE_CONTROL = _pattern(r'\b(?:own\w*|register\w*|unregister\w*|schedul\w*|capture\w*|cancel\w*|detach\w*|cleanup|clean up|remove\w*|retain\w*|release\w*|teardown|lifetime)\b|拥有|归属|所有权|登记|注册|捕获|取消|解绑|清理|卸载|释放|持有|寿命|收尾')
_RESOURCE_QUESTION = _pattern(r'\b(?:own\w*|capture\w*|cleanup|clean up|teardown|lifetime)\b|拥有|归属|所有权|捕获|清理|卸载|寿命|收尾')
_EXIT = _pattern(r'\b(?:leav\w*|left|exit\w*|clos\w*|disconnect\w*|remov\w*|destroy\w*|replac\w*|rebuild\w*)\b|离开|离场|退场|退出|关闭|断线|移除|销毁|替换|重建')
_CONTINUES = _pattern(r'\b(?:still|keeps?|continues?)\b.{0,35}\b(?:run\w*|execut\w*|fir\w*|activ\w*|call\w*|tick\w*|work\w*)\b|(?:仍|还|继续).{0,8}(?:执行|运行|触发|调用|工作|活动)')
_DELIVERY = _pattern(r'\b(?:events?|notifications?|effects?|fx|push\w*event|send\w*|dispatch\w*)\b|事件|通知|效果|特效|发送|发给|派发|分派')
_RECIPIENT_REQUEST = _pattern(r'\b(?:recipients?|receivers?)\b|\bwho\b.{0,30}\b(?:receiv\w*|get\w*)\b|\b(?:sent|send|deliver\w*|dispatch\w*)\b.{0,30}\b(?:whom|which|who)\b|发给谁|给谁|接收者|接收方|接收对象|接收实体')
_RECIPIENT_SOURCE = _pattern(
    r'\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:(?:PushEvent|ListenForEvent)\s*\('
    r'|\b(?:send\w*|sent|deliver\w*|dispatch\w*|forward\w*|attach\w*)\b.{0,60}\b(?:to|onto|on)\s+\w+'
    r'|\b(?:[A-Za-z_]\w*\s+){1,3}(?:receives?|received)\b.{0,40}\b(?:events?|effects?|notifications?)\b'
    r'|(?:发送给|发给|推给|派发给|通知给|附着到|作用于).{1,30}'
    r'|(?:向|在).{1,25}(?:推送|派发|发送|触发|PushEvent)')
_AUDIENCE = _pattern(r'\b(?:audience|recipients?|receivers?|peers?|clients?|owners?)\b|受众|接收方|指定玩家|全体.{0,6}玩家|所有玩家')
_CHANNEL = _pattern(r'\b(?:channels?|routes?|routing|broadcast|classified|network proxy)\b|通道|路由|定向传输|广播')
_ROUTE_CHOICE = _pattern(r'\b(?:choose|select|decide|distinguish|separate)\b|选择|选通道|决定|区分')
_ROUTE_RELATION = _pattern(r'\b(?:uses?|adopts?|routes?)\b|采用|路由不同|定向传输|广播')
_CLASSIFIED_TARGET = _pattern(r'\bclassified\s+target\b.{0,25}(?:\bis\b|\bto\b|=|为)|(?:set\w*|设置).{0,35}\bclassified\s+target\b')
_LOCAL_RENDER = _pattern(r'(?:\blocal\b|本地).{0,30}(?:\b(?:hud|ui|visual|sound|fx)\b|视觉|音效)|(?:\b(?:hud|ui|visual|sound|fx)\b|视觉|音效).{0,30}(?:\blocal\b|本地)')
_RENDER_RELATION = _pattern(r'\b(?:belong\w*|own\w*|creat\w*|build\w*|render\w*|play\w*)\b|归|建立|创建|播放|显示|走')
_RECEIVED_PROXY = _pattern(r'(?:\breceiv\w*\b|收到|接收).{0,25}\bproxy\b.{0,65}(?:\b(?:peer|client|visual)\b|视觉)')
_DATA_OBJECT = _pattern(r'\b(?:data|tables?|fields?|records?|metadata|declarations?|dependencies|dependency|config\w*|options?|settings?|sequences?|lists?)\b|数据|表|字段|记录|元数据|声明|依赖|配置|选项|序列|列表')
_DATA_READ = _pattern(r'\b(?:read\w*|load\w*|get\w*|return\w*|select\w*|choos\w*|pars\w*|process\w*|consum\w*|exports?)\b|读取|加载|取得|返回|选择|优先|解析|处理|消费|导出')
_DATA_SELECTION = _pattern(r'\b(?:if|when|unless|otherwise|else|in|select\w*|choos\w*|prefer\w*|from)\b|若|当|在|否则|其余|选择|优先|依次|从')
_DATA_QUESTION = _pattern(r'\b(?:which|what|where|source)\b|哪|什么|来源')
_DECLARATIVE_DATA = _pattern(r'\b(?:metadata|declarations?|dependencies|dependency|configuration|settings)\b|元数据|依赖|声明|配置')
_CONSUME = _pattern(r'\bconsum\w*\b|消费|消耗')
_MATERIAL_OPERAND = _pattern(r'\b(?:fuel\w*|ingredients?|materials?|resources?|items?|food|health|hunger|sanity|durability|cycles?|charges?|costs?|budgets?)\b|燃料|材料|资源|物品|食物|生命值|血量|饥饿|理智|耐久|次数|扣费|扣料')
_RETURN_DATA = _pattern(r'\b(?:return(?:ed)?\s+(?:values?|results?|data|objects?|functions?|tables?)|(?:api|function|method)\s+returns?)\b|返回(?:值|结果|数据|对象|函数|表|\s*API)')
_RETURN_VALUE_USE = _pattern(
    r'\b(?:uses?|using|consum\w*|invokes?|calls?|stores?|wraps?|applies)\s+(?:the\s+|a\s+|all\s+)?return(?:ed)?\s+(?:values?|results?|data|objects?|functions?|tables?)\b'
    r'|\breturn(?:ed)?\s+(?:values?|results?|data|objects?|functions?|tables?)\s+(?:(?:is|are|was|were|can\s+be)\s+)?(?:used|consumed|invoked|called|stored|wrapped|applied)\b'
    r'|(?:用|使用|消费|调用|保存|包装)(?:其|该|这个|所有)?返回(?:值|结果|对象|函数|表)'
    r'|(?:把|将)(?:所有|该|其)?返回(?:值|结果|对象|函数|表)(?:一起|分别|依次|直接|继续|全部|逐个|立即)?(?:包装|保存|传入|构造|调用)'
    r'|返回(?:值|结果|对象|函数|表)(?:被|用于|用来|会被)(?:直接|继续|立即|依次)?(?:消费|构造|调用|保存|包装|传入|计算)')
_QUESTION_NONDATA_HEAD = _pattern(r'\b(?:conditions?|prerequisites?|requirements?|constraints?|permissions?|times?|reasons?)\b|条件|前提|要求|限制|权限|时机|原因')
_VALUE_PHASE = _pattern(r'\b(?:launch|impact|hit|creation|construction|execution|completion)\b|发射|命中|碰撞|构造时|创建时|执行时|完成时')
_VALUE_CONTENT = _pattern(r'\b(?:values?|amounts?|damage|health|costs?|snapshots?)\b|数值|伤害|治疗量|费用|快照|取值|取用')
_VALUE_EVALUATION = _pattern(r'\b(?:comput\w*|calculat\w*|calc|recomput\w*|read\w*|snapshot\w*|cach\w*)\b|计算|重算|取值|取用|读取|快照|缓存')
_VALUE_PREDICATE = _pattern(r'\b(?:computes?|computed|calculates?|calculated|recomputes?|recomputed|reads?|read|snapshots|snapshotted|caches|cached)\b|计算|重算|取值|取用|读取|缓存')
_VALUE_TIMING_NOMINAL = _pattern(
    r'\b(?:damage|health|cost|value|amount)(?:[ -](?:state|value|amount))?\s+(?:timing|evaluation\s+(?:time|phase))\b'
    r'|(?:伤害|治疗量|费用|数值)(?:状态|取值|求值|计算)?(?:的)?(?:时机|时点|阶段)')
_OWNER_REQUEST = _pattern(r'\b(?:owners?|ownership)\b|所有权|归属')
_OWNER_FIELD = r'(?<![A-Za-z0-9_])(?:[A-Za-z_]\w*\.)*owner(?![A-Za-z0-9_])'
_OWNER_STATE_PREDICATE = _pattern(
    r'\b(?:captures?|captured|caches?|cached|stores?|stored|saves?|saved|clears?|cleared|'
    r'rereads?|re-reads?|selects?|sets?|updates?)\s+(?:(?:the|its|current|original|previous|old)\s+)*'
    + _OWNER_FIELD + r'|(?:缓存|捕获|保存|清空|清除|读取|重读|改取|重设|设置|更新)'
    r'(?:\s*(?:当前|原|该|其|旧|武器|这个))*\s*' + _OWNER_FIELD)
_OWNER_STATE_UNCERTAIN = _pattern(r'\b(?:whether|may|might|could|possibly)\b|是否|可能|(?:尚)?未(?:确认|证实)')


def _literal_owner_state(unit):
    visible = _data_quote_view(unit, literal_names=False)
    return bool(not _REFERENCE_METADATA.search(unit) and not _RESULT_EPISTEMIC.search(visible)
        and not _OWNER_STATE_UNCERTAIN.search(visible)
        and (_OWNER_STATE_PREDICATE.search(visible)
             or re.search(_OWNER_FIELD + r'\s*=(?!=)\s*\S', visible, re.I | re.ASCII)))


def _literal_value_phase(unit):
    # 名字拆词只用于导航；阶段关系必须来自名字外的原文谓词。
    prose = re.sub(r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b|\b[A-Za-z_]*[a-z][A-Z][A-Za-z_]*\b', ' ', unit)
    return bool(_VALUE_PHASE.search(prose) and _VALUE_CONTENT.search(prose) and
                _VALUE_PREDICATE.search(prose))


_REFERENCE_PHASE = _pattern(
    r'\b(?:before|after|later|prior|subsequent|subsequently|entry|initially)\b'
    r'|后续|随后|先前|进入前|调用点|之前|之后|后(?=[，,])')
_REFERENCE_OBJECT = _pattern(r'\b(?:references?|fields?|snapshots?|local\s+objects?)\b|引用|字段|快照|局部对象')
_REFERENCE_SELECTION = _pattern(r'\b(?:which|what|whether|reread\w*)\b|哪(?:份|部分|个|些)|是否|重读|重新读')
_REFERENCE_PREDICATE = _pattern(r'\b(?:captures?|captured|rereads?|reread|re-reads?)\b|捕获|重读|重新(?:读取|读|取)|再次(?:读取|读)')
_REFERENCE_METADATA = _pattern(r'^\s*(?:metadata|labels?|title|navigation|API names|元数据|标签|标题|导航)\s*[:：]')
_REFERENCE_FIELD = _pattern(r'\b(?:self|inst|target|doer|item)(?:\.[A-Za-z_]\w*)+\b')


def _reference_phase_request(text):
    prose = literal_data_prose(text, literal_names=False)
    return bool(not _REFERENCE_METADATA.search(text) and _REFERENCE_PHASE.search(prose)
                and _REFERENCE_OBJECT.search(prose) and _REFERENCE_SELECTION.search(prose))


def _literal_reference_phase(unit):
    # 引用阶段来自名字外的捕获/重读谓词；字符串与“尚未证明”不提供运行时关系。
    prose = literal_data_prose(unit, literal_names=False)
    unquoted = _data_quote_view(unit, literal_names=False)
    return bool(not _REFERENCE_METADATA.search(unit) and not _RESULT_EPISTEMIC.search(prose)
                and _REFERENCE_PHASE.search(prose) and _REFERENCE_PREDICATE.search(prose)
                and (_REFERENCE_OBJECT.search(prose) or _REFERENCE_FIELD.search(unquoted)))


_ORDER_REQUEST = _pattern(r'\b(?:order|ordering|sequence)\s+of\b|\b(?:call|execution|operation)\s+order\b|先后|顺序')
_ORDER_PREDICATE = _pattern(r'\b(?:before|after|first|then|followed\s+by)\b|先|随后|然后|之前|之后|早于|晚于')
_ORDER_ACTION = _pattern(r'\b(?:calls?|invokes?|clears?|removes?|cancels?|executes?|guards?|captures?|installs?|wraps?|constructs?|spawns?)\b|调用|清理|清除|执行|捕获|包装|构造|安装|装|发生|guard')
_PARAMETER_ORDER = _pattern(r'\b(?:parameters?|arguments?|signature)\b|参数|实参|形参|签名')
_DISTINCTION_REQUEST = _pattern(r'\b(?:compare|comparison|distinguish|equivalent)\b|区分|比较|是否等价')
_DISTINCTION_SOURCE = _pattern(
    r'\b(?:not|never)\s+(?:directly\s+)?(?:cancel|stop|call|invoke)\b'
    r'|(?:不|未|不会)(?:直接)?(?:Cancel|取消|停止|调用)'
    r'|\b(?:not\s+(?:simply\s+)?equivalent|does\s+not\s+mean)\b'
    r'|不是.{0,25}(?:等同|等价)|不(?:等同|等价)')


def operation_order_request(text):
    prose = literal_data_prose(text, literal_names=False)
    return bool(_ORDER_REQUEST.search(prose) and not _PARAMETER_ORDER.search(prose))


def _literal_operation_order(unit):
    prose = literal_data_prose(unit, literal_names=False)
    unquoted = _data_quote_view(unit, literal_names=False)
    return bool(not _REFERENCE_METADATA.search(unit) and not _RESULT_EPISTEMIC.search(prose)
        and _ORDER_PREDICATE.search(prose) and (_ORDER_ACTION.search(prose)
            or re.search(r'早于|晚于|\bprecedes?\b', prose, re.I)
            or re.search(r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*\s*\(', unquoted, re.ASCII)))


_OBSERVER = _pattern(r'\b(?:world[ -]?state|watchworldstate|stopwatchingworldstate|addwatcher|removewatcher|observers?|watchers?|listeners?|callbacks?)\b|世界状态|观察器|监听|回调')
_REGISTRATION = _pattern(r'\b(?:register\w*|unregister\w*|registrations?|subscrib\w*|unsubscrib\w*|watchworldstate|stopwatchingworldstate|addwatcher|removewatcher)\b|登记|注册|解绑|撤销')
_REGISTRATION_IDENTITY = _pattern(r'\b(?:targets?|receivers?|(?:registration|function|callback)\s+identity)\b|接收者|接收对象|注册身份|函数身份')


def observer_registration_identity_request(text):
    """Registration receiver identity is distinct from account identity."""
    return bool(_OBSERVER.search(text) and _REGISTRATION.search(text)
                and _REGISTRATION_IDENTITY.search(text))


def _literal_observer_registration_identity(unit):
    visible = _data_quote_view(unit, literal_names=False)
    if _REFERENCE_METADATA.search(visible) or _RESULT_EPISTEMIC.search(visible):
        return False
    # Names navigate to observers; an original registration/identity predicate
    # must also exist. A label naming target or an API name supplies no fact.
    return bool(_OBSERVER.search(visible) and _REGISTRATION.search(visible)
        and _REGISTRATION_IDENTITY.search(visible)
        and re.search(r'\b(?:registers?|registered|unregisters?|unregistered|preserves?|supplies?|matches?|requires?)\b'
            r'|登记|注册|传入|匹配|要求|保留|target\s*=', visible, re.I))


def registration_state_request(text):
    """Request registry effects explicitly; ordinary subscription is separate."""
    prose = literal_data_prose(text, literal_names=False)
    for clause in re.split(r'[。；;!?！？\n]|\.\s+', prose):
        registry = re.search(r'\b(?:registr(?:y|ies)|registration\s+tables?)\b|注册表|登记表', clause, re.I)
        effect = re.search(r'\b(?:writes?|stores?|appends?|inserts?|assigns?|records?|changes?|effects?|entries|contents?|state)\b'
                           r'|写入|保存|追加|分配|记录|变化|效果|内容|表项|状态', clause, re.I)
        registration = re.search(r'\b(?:register(?:s|ed|ing)?|registrations?)\b|注册|登记', clause, re.I)
        numbering = re.search(
            r'\b(?:assigns?|allocates?|generates?)\b.{0,50}\b(?:codes?|ids?|identifiers?|indices|indexes?|numbers?)\b'
            r'|\b(?:codes?|ids?|identifiers?|indices|indexes?|numbers?)\s+(?:assignments?|allocations?|generation)\b'
            r'|(?:编号|序号|代码|标识符).{0,16}(?:分配|生成|赋值|写入)'
            r'|(?:分配|生成|赋值).{0,16}(?:编号|序号|代码|标识符)', clause, re.I)
        if registry and effect or registration and numbering:
            return True
    return False


def _literal_registration_state(unit):
    visible = _data_quote_view(unit, literal_names=False)
    prose = literal_data_prose(unit, literal_names=False)
    if _REFERENCE_METADATA.search(visible) or _RESULT_EPISTEMIC.search(prose):
        return False
    write = re.search(r'\b(?:writes?|stores?|appends?|inserts?|assigns?|records?)\b|写入|保存|追加|填入|赋值', prose, re.I)
    if not write:
        return False
    # Codes/IDs, or an arbitrary indexed array, are not registration facts.
    # The source must name the registry destination or explicitly describe the
    # registration's table write; identity-keyed storage alone is insufficient.
    destination = re.search(
        r'\b(?:writes?|stores?|appends?|inserts?|assigns?|records?)\b[^。；;!?！？\n]{0,100}?'
        r'\b(?:into|to|in)\s+(?:the\s+)?(?:[A-Za-z_]\w*\.)*'
        r'(?:\w*registry|registries)\b'
        r'|(?:写入|保存到|填入|追加到|记录到)\s*(?:该|此|这个)?(?:注册表|登记表)',
        visible, re.I)
    indexed_object = re.search(r'\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*\[', visible, re.ASCII)
    explicit_registration = re.search(
        r'\b(?:registers|registered)\b|\b(?:registration|registering)\s+(?:function|routine|method|helper)\b'
        r'|(?:注册|登记)(?:函数|方法|过程|例程)|(?:注册|登记)(?:到|入|进|了)', prose, re.I)
    return bool(destination or explicit_registration and indexed_object)


_READINESS = _pattern(r'\b(?:ready|readiness|availability|available)\b|可用|就绪')


def readiness_dependency_request(text):
    return bool(_READINESS.search(text) and re.search(
        r'\b(?:depends?|dependencies|gates?|prerequisites?|boundar\w*|assum\w*|wait\w*|guarantees?)\b'
        r'|依赖|条件|边界|假设|保证|只等|等待|是否', text, re.I))


def _literal_readiness_dependency(unit):
    prose = literal_data_prose(unit, literal_names=False)
    if _REFERENCE_METADATA.search(unit) or _RESULT_EPISTEMIC.search(prose):
        return False
    return bool(_READINESS.search(prose) and re.search(
        r'\b(?:different|distinct|separate)\s+(?:conditions?|prerequisites?)\b'
        r'|\bspecific\s+(?:role|purpose|protocol)\b'
        r'|\b(?:does?\s+not|cannot)\s+(?:imply|prove|guarantee)\b'
        r'|\bnot\s+(?:equivalent|sufficient)\b'
        r'|不同条件|独立条件|特定作用|不能推得|不能推出|不(?:等于|等价|代表|证明|保证)', prose, re.I))


def _literal_mechanism_distinction(unit):
    prose = _data_quote_view(unit, literal_names=False)
    return bool(not _REFERENCE_METADATA.search(unit) and not _RESULT_EPISTEMIC.search(prose)
        and _DISTINCTION_SOURCE.search(prose)
        and 'cancel_task' in _predicate_module.refine_operations(prose, set(), source=True))


def _asks_data_source(text):
    # 疑问词必须限定数据或来源；“哪些条件下读数据”不产生来源选择合同。
    for clause in re.split(r'[。；;?!？！]|\band\b', text, flags=re.I):
        if re.search(r'\b(?:source\s+of|data\s+source|where\b.*\bfrom)\b|数据来源|从哪', clause, re.I):
            return True
        for question in re.finditer(r'\b(?:which|what)\b|哪(?:一|些|种|个|张|份)?|什么', clause, re.I):
            following = clause[question.end():]
            data = _DATA_OBJECT.search(following)
            other = _QUESTION_NONDATA_HEAD.search(following)
            if data and (not other or data.start() < other.start()):
                return True
    return False


def relation_text(text):
    """Identifier word boundaries are navigation, never evidence of an API call."""
    return re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text).replace('_', ' ')


_DATA_IDENTIFIER = re.compile(
    r'\b(?:[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+|[A-Za-z_]\w*_[A-Za-z_]\w*'
    r'|[A-Za-z_]*[a-z0-9][A-Z][A-Za-z0-9_]*)\b', re.ASCII)
_READ_SELECTION_CONTEXTS = {
    'frontend': _pattern(r'\bfront[ -]?end\b|前端'),
    'worldgen': _pattern(r'\bworldgen\b|世界生成'),
    'listen_host': _pattern(r'\blisten[ -]+host\b|监听主机|本地主机'),
    'dedicated': _pattern(r'\bdedicated\b|专服'),
    'temporary_enabled': _pattern(
        r'(?<![A-Za-z0-9_])temp(?:orarily)?[ _-]+enabled(?![A-Za-z0-9_])|临时启用'),
}


def _data_quote_view(text, literal_names=False, *, apostrophes_are_quotes=False):
    """String parameters may name data, but their contents do not execute verbs."""
    result, index = list(text), 0
    quotes = {'"': '"', "'": "'", '`': '`', '“': '”', '‘': '’'}
    while index < len(text):
        long_string = re.match(r'\[(=*)\[', text[index:]) if text[index] == '[' else None
        quote = text[index]
        if long_string:
            closing = ']' + long_string.group(1) + ']'
            end = text.find(closing, index + long_string.end())
            stop = len(text) if end == -1 else end + len(closing)
        elif quote in quotes and (apostrophes_are_quotes or not (
                quote in ("'", '‘') and index and text[index - 1].isalnum())):
            end = index + 1
            while end < len(text):
                if text[end] == '\\':
                    end += 2
                elif text[end] == quotes[quote]:
                    break
                else:
                    end += 1
            stop = min(end + 1, len(text))
            if literal_names and end < len(text) and re.fullmatch(
                    r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*', text[index + 1:end], re.ASCII):
                index = stop
                continue
        else:
            index += 1
            continue
        result[index:stop] = ' ' * (stop - index)
        index = stop
    return ''.join(result)


def literal_data_prose(text, preserved=(), *, literal_names=True):
    """Only original prose and literal data names supply content anchors."""
    text = _data_quote_view(text, literal_names)
    names = {value.lower().replace('.', ':') for value in preserved}
    return _DATA_IDENTIFIER.sub(lambda match: match.group() if
        match.group().lower().replace('.', ':') in names else ' ' * len(match.group()), text)


_CALLBACK_SCOPE_NAME = r'[A-Za-z_][A-Za-z0-9_]*(?:[.:][A-Za-z_][A-Za-z0-9_]*)*'
_FIELD_CALLBACK_SCOPE = re.compile(
    r'(?<![A-Za-z0-9_])(?P<before>' + _CALLBACK_SCOPE_NAME + r')\s*(?:的\s*)?'
    r'(?:(?:属性|字段)\s*(?:的\s*)?(?:变更|变化|赋值|更新)?\s*(?:回调|callbacks?\b)'
    r'|(?:property|field)\s+(?:(?:change|changed|update)\s+)?callbacks?\b)'
    r'|\bcallbacks?\s+(?:for|of)\s+(?:the\s+)?(?P<after>' + _CALLBACK_SCOPE_NAME + r')'
    r'\s+(?:property|field)\b', re.I | re.ASCII)
_NAMED_CALLBACK_SCOPE = re.compile(
    r'(?<![A-Za-z0-9_])(?P<name>' + _CALLBACK_SCOPE_NAME + r')\s*'
    r'(?:(?:/|、|和|与|\band\b)\s*[^，,。；;！？!?\n]{1,24}?)?\s*'
    r'(?:回调|callbacks?\b)', re.I | re.ASCII)
_GENERIC_CALLBACK_WORDS = frozenset(('a', 'an', 'the', 'this', 'that', 'its',
    'callback', 'callbacks', 'function', 'functions', 'existing', 'ordinary',
    'custom', 'property', 'field', 'change', 'changed', 'update', 'all', 'any',
    'every', 'each', 'both', 'some', 'these', 'those', 'review', 'explain',
    'check', 'debug', 'compare', 'inspect', 'describe', 'register', 'invoke',
    'call', 'execute', 'remove'))


def _callback_scope_view(text):
    # An isolated quoted identifier may name an object; quoted prose cannot
    # introduce a callback attachment or a request for one.
    return re.sub(r"[`'\"“”‘’]", ' ', _data_quote_view(text, literal_names=True))


@lru_cache(maxsize=4096)
def callback_property_scopes(text):
    """Literal field attachments, preserving Lua identifier spelling."""
    value = _callback_scope_view(text)
    return frozenset(match.group('before') or match.group('after')
                     for match in _FIELD_CALLBACK_SCOPE.finditer(value))


def callback_object_scope_conflict(request, statement, context=None):
    """Reject a different field callback as a named callback's only witness.

    This is a negative relevance guard, never a new contract or task seed.
    Callers supply their existing positive request text and original source
    text. Unspecified callback ownership remains with their existing checks.
    """
    fields = callback_property_scopes(statement)
    if not fields:
        return False
    wanted, source = _callback_scope_view(request), _callback_scope_view(statement)
    field_leaves = {name.rsplit('.', 1)[-1].rsplit(':', 1)[-1] for name in fields}
    # CanEat is a method spelling, caneat a different Lua field. Case folding
    # here would silently turn the former into authorization for the latter.
    request_names = set(re.findall(_CALLBACK_SCOPE_NAME, wanted, re.ASCII))
    request_leaves = {name.rsplit('.', 1)[-1].rsplit(':', 1)[-1] for name in request_names}
    if field_leaves & request_leaves:
        return False
    explicit_field_kind = re.search(
        r'(?:属性|字段)\s*(?:的\s*)?(?:变更|变化|赋值|更新)?\s*(?:回调|callbacks?\b)'
        r'|\b(?:property|field)\s+(?:(?:change|changed|update)\s+)?callbacks?\b'
        r'|\bsetters?\b', wanted, re.I | re.ASCII)
    if explicit_field_kind:
        return False
    targets = {match.group('name') for match in _NAMED_CALLBACK_SCOPE.finditer(wanted)
               if match.group('name').lower() not in _GENERIC_CALLBACK_WORDS}
    if not targets:
        return False
    target_leaves = {name.rsplit('.', 1)[-1].rsplit(':', 1)[-1] for name in targets}
    source_names = set(re.findall(_CALLBACK_SCOPE_NAME, source, re.ASCII))
    source_leaves = {name.rsplit('.', 1)[-1].rsplit(':', 1)[-1] for name in source_names}
    if target_leaves & source_leaves:
        return False
    # An independently requested literal method remains relevant on its own.
    # Neither a record owner nor a field name is a method identity.
    methods = set(re.findall(r'(?<![A-Za-z0-9_])(' + _CALLBACK_SCOPE_NAME + r')\s*\(', source, re.ASCII))
    if isinstance(context, dict):
        methods.update(binding['symbol'] for binding in context.get('role_bindings', [])
            if isinstance(binding, dict) and binding.get('role') == 'METHOD_SUBJECT'
            and isinstance(binding.get('symbol'), str) and re.fullmatch(_CALLBACK_SCOPE_NAME, binding['symbol'], re.ASCII)
            and (':' in binding['symbol'] or '.' in binding['symbol'])
            and binding['symbol'].rsplit('.', 1)[-1].rsplit(':', 1)[-1] in source_leaves)
    method_leaves = {name.rsplit('.', 1)[-1].rsplit(':', 1)[-1] for name in methods}
    return not bool(method_leaves & request_leaves)


@lru_cache(maxsize=2048)
def read_selection_contexts(text):
    # temp_enabled 是明确消费的状态条件；名字内部的 TempEnabled 不建立执行场景。
    value = literal_data_prose(text, ('temp_enabled',), literal_names=False)
    return frozenset(name for name, pattern in _READ_SELECTION_CONTEXTS.items() if pattern.search(value))


@lru_cache(maxsize=2048)
def data_consumption(text):
    value = relation_text(text)
    return bool(_CONSUME.search(value) and (_DECLARATIVE_DATA.search(value) or _RETURN_DATA.search(value)
                or re.search(r'\b(?:data|events?|messages?|payloads?)\b|数据|事件|消息', value, re.I))
                and not _MATERIAL_OPERAND.search(value))


_RESULT_NOUN = _pattern(r'\b(?:results?|outcomes?|success|failure|false|true)\b|结果|成败|成功|失败')
_RESULT_QUESTION = _pattern(
    r'\b(?:produc\w*|interpret\w*|identif\w*|recogni\w*|determin\w*|consum\w*|return\w*|handl\w*|production|consumption)\b'
    r'|识别|判定|解释|产生|返回|处理|消费|成败')
_RESULT_ACTION = _pattern(r'\bactions?\b|动作')
_EXPLICIT_RESULT = _pattern(
    r'\b(?:actual|real|final|business|authoritative)\s+(?:results?|outcomes?)\b'
    r'|\b(?:results?|outcomes?)\s+(?:production|consumption|handling|interpretation)\b'
    r'|(?:实际|最终|业务|权威)(?:结果|成败)|结果(?:产生|生产|消费|处理|判定)')
_RESULT_EPISTEMIC = _pattern(
    r'\b(?:evidence|proof|unknown|unverified|unproven|uncertain|assum\w*|suppos\w*|hypothes\w*|premise)\b'
    r'|证据|未知|未验证|未证明|不确定|假设|假定|设想|前提')
_RESULT_RETURN = _pattern(
    r'\b(?:return|returns|returned|returning)\s+(?:its\s+|the\s+|a\s+)?(?:success|failure|false|true|nil|result|outcome|reason)\b'
    r'|返回(?:的|其|该)?\s*(?:success|reason|false|true|nil|成功|失败|结果|成败)')
_RESULT_VALUE_RETURN = _pattern(
    r'\b(?:return|returns|returned|returning)\s+(?:its\s+|the\s+|a\s+)?(?:success|failure|result|outcome|reason)\b'
    r'|返回(?:的|其|该)?\s*(?:success|reason|成功|失败|结果|成败)')
_RESULT_VALIDATION = _pattern(r'\b(?:validat\w*|invalid|validity)\b|验证|校验|无效|为假')
_RESULT_USE = _pattern(
    r'\b(?:uses?|checks?|consumes?|tests?|interprets?)\s+(?:the\s+|its\s+)?(?:returned\s+)?(?:success|failure|result|outcome)(?:\s+value)?\b'
    r'.{0,70}\b(?:choos\w*|select\w*|callback\w*|branch\w*|effect\w*|state\w*)\b'
    r'|(?:根据|以其|按|使用|检查)(?:返回的)?[^。；;！？!?\n]{0,35}(?:success|reason|成功|失败|结果)'
    r'[^。；;！？!?\n]{0,35}(?:调用|执行|回调|分支|状态|生效)')
_RESULT_ACTION_HEAD = _pattern(
    r'^\s*(?:(?:the|an?)\s+)?(?:actions?(?:\s+(?:caller|executor))?\b|BufferedAction(?:[.:]\w+)?\b|动作)')


def result_input_scenario(text):
    """An explicit input-to-authority question, not input as a new API owner."""
    value = literal_data_prose(text, literal_names=False)
    return bool(re.search(r'\b(?:input|controllers?|buttons?|click\w*)\b|点击|控制器|按钮|输入', value, re.I)
        and re.search(r'\brequests?\b|请求', value, re.I)
        and re.search(r'\b(?:authorit\w*)\b|权威', value, re.I)
        and re.search(r'\b(?:actions?|effects?|execution)\b|效果|执行|动作', value, re.I))


def result_action_reference(text):
    return bool(_RESULT_ACTION.search(literal_data_prose(text, literal_names=False)))


def result_action_subject(unit):
    """Literal source head supplies only a domain hint, never a method role."""
    return bool(_RESULT_ACTION_HEAD.search(_data_quote_view(unit, literal_names=False)))


def result_contract_request(text):
    value = literal_data_prose(text, literal_names=False)
    return bool(_EXPLICIT_RESULT.search(value) or
        _RESULT_NOUN.search(value) and _RESULT_QUESTION.search(value)
        and (result_action_reference(text) or result_input_scenario(text)))


def literal_result_return(unit):
    value = literal_data_prose(unit, literal_names=False)
    return bool(_RESULT_RETURN.search(value) and not _RESULT_EPISTEMIC.search(value)
        and not re.match(r'^\s*(?:metadata|title|labels?|keywords?|topics?|navigation|scope|元数据|标题|标签|导航)\s*[:：]', value, re.I))


@lru_cache(maxsize=8192)
def result_source_relations(unit):
    """Local result production/consumption, including explicit negative exits."""
    value = literal_data_prose(unit, literal_names=False)
    if (_RESULT_EPISTEMIC.search(value) or re.match(
            r'^\s*(?:metadata|title|labels?|keywords?|topics?|navigation|scope|元数据|标题|标签|导航)\s*[:：]', value, re.I)):
        return frozenset()
    found = set()
    # 普通布尔/坐标返回不是执行结果；校验早退仍按原否定条件保留。
    if (_RESULT_VALUE_RETURN.search(value) or
            _RESULT_RETURN.search(value) and _RESULT_VALIDATION.search(value)):
        found.add('result_production')
    if _RESULT_USE.search(value):
        found.add('result_consumption')
    if found and re.search(r'\b(?:false|failure|fails?|invalid|without|not)\b|失败|无效|为假|不调用|不执行', value, re.I):
        found.add('result_failure_path')
    return frozenset(found)


def result_dispatch_senders(unit):
    """Bind a literal send/call to its following transport operand in one clause."""
    value = literal_data_prose(unit, literal_names=False)
    objects = _data_quote_view(unit, literal_names=False)
    if _RESULT_EPISTEMIC.search(value):
        return ()
    senders = []
    for verb in re.finditer(r'\b(?:sends?|sent|dispatch\w*|calls?|invokes?)\b|发送|调用|分派', value, re.I):
        tail = re.split(r'[。；;!?！？\n]|\b(?:and|but)\b', objects[verb.end():], maxsplit=1, flags=re.I)[0]
        if re.match(r'\s*(?:(?:the|an?|its|action|input)\s+)*(?:requests?\b|RPC(?:\b|[.:])|preview_cb\b)'
                    r'|\s*(?:动作|输入|预演)?请求|\s*buffered\s+action\s*(?:的|[\x27’]s)\s*preview_cb\b', tail, re.I):
            prefix = re.split(r'[。；;!?！？\n]|\b(?:and|but)\b', objects[:verb.start()], flags=re.I)[-1]
            senders.append(prefix)
    return tuple(senders)


def result_request_dispatch(unit):
    """A routing fact can answer the routing half, without result credit."""
    return bool(result_dispatch_senders(unit))


_ROUTE_NAME = r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*'
_ROUTE_HEAD = _pattern(r'^\s*(?:(?:the|a|an|server|client|authoritative|controller|input|request|handler)\s+)*'
    r'(?P<actor>' + _ROUTE_NAME + r')(?=\s|的|在|只|先|会|：|:|\(|$)')
_ROUTE_META = _pattern(r'^\s*(?:metadata|labels?|titles?|navigation|keywords?|API names|lists?|'
    r'元数据|标签|标题|导航|列表)\s*[:：]|\b(?:quotes?|quoted|mentions?|lists?)\b|引用文本|仅提及')
_ROUTE_INPUT = _pattern(r'\b(?:input|controllers?|click|pointer|buttons?|requests?)\b|点击|控制器|按钮|输入|请求')
_ROUTE_CANDIDATE = _pattern(r'\b(?:candidates?|lmb|rmb)\b|候选')
_ROUTE_RESELECT = _pattern(r'\b(?:rebuilds?|regenerates?|reselects?|re-obtains?|recomputes?)\b|重新(?:生成|选择|取得|获取)|重选')
_ROUTE_VALIDATE = _pattern(r'\b(?:accepts?|validates?|matches?)\b|接受|匹配|校验')
_ROUTE_HANDOFF = _pattern(r'\b(?:dispatches?|delegates?|hands?\s+off|routes?|pushes?)\b|分发|分流|交给|转交|移交')
_ROUTE_CLAUSES = re.compile(r'[，,。；;!?！？\n]|\.\s+|\b(?:and|but|then|while|whereas)\b|然后|随后|接着|同时|但是|但|而|并', re.I)


def _route_quote_view(text):
    """Route prose uses the existing quotes plus CJK corner-quote payloads."""
    visible = list(_data_quote_view(text, literal_names=False))
    pairs, stack, start = {'「': '」', '『': '』'}, [], None
    for index, char in enumerate(visible):
        if char in pairs:
            if not stack:
                start = index
            stack.append(pairs[char])
        elif stack and char == stack[-1]:
            stack.pop()
            if not stack:
                visible[start:index + 1] = ' ' * (index + 1 - start)
    if stack:
        visible[start:] = ' ' * (len(visible) - start)
    return ''.join(visible)


def _route_actor_at(text, offset, actor):
    """Carry only a local original actor through recognizable continuations."""
    bound = False
    for clause in _ROUTE_CLAUSES.split(text[:offset]):
        clause = clause.strip()
        if not clause:
            continue
        head = _ROUTE_HEAD.match(clause)
        if head and actor and head['actor'].casefold() == actor.casefold():
            bound = True
        elif re.match(r'^(?:此函数|该函数|该方法|this\s+(?:function|method)\b)', clause, re.I) and actor is None:
            bound = True
        elif not re.match(r'^(?:它|其(?!他|余)|该回调|此回调|再|还|并|且|随后|接着|同时|然后|只|'
                r'有\s|无\s|非\s|仅对|仅在|只在|在\s|真时|否则|先|调用|重新|接受|匹配|配置|分流|分发|'
                r'(?:it|its|then|also|only|when|if|otherwise|calls?|invokes?|rebuilds?|regenerates?|'
                r'reselects?|accepts?|validates?|dispatches?|delegates?|routes?|pushes?)\b)', clause, re.I):
            # An unfamiliar/new subject is a binding barrier. Its later zero
            # subject clauses cannot borrow the earlier named function.
            bound = False
    return bound


def _positive_route_predicate(pattern, text, actor, binding_text=None):
    # Identifier masking preserves offsets, but it removes the very head that
    # binds this predicate. Read the actor from the unquoted original view.
    binding_text = text if binding_text is None else binding_text
    for match in pattern.finditer(text):
        if not _route_actor_at(binding_text, match.start(), actor):
            continue
        prefix = _ROUTE_CLAUSES.split(text[:match.start()])[-1]
        if re.search(r"\b(?:not|never|no|without|may|might|could|would|should|must|can|cannot|hypothetical|"
                     r"(?:does|do|did|is|are|was|were|has|have|had|wo|ca)n['’]t)\b"
                     r'|不(?!仅|但|同|是)|没(?:有)?|未|无(?:法|需)'
                     r'|禁止|不可|不得|假设|可能|应该|应当|需要|的主\s*$', prefix, re.I):
            continue
        yield match


def input_route_stage_request(text):
    """An input route question earns stage relevance, never completion credit."""
    if result_input_scenario(text):
        return True
    prose = literal_data_prose(text, literal_names=False)
    if (_ROUTE_INPUT.search(prose) and re.search(r'\brequests?\b|请求', prose, re.I)
            and re.search(r'\bauthorit\w*\b|权威', prose, re.I)
            and re.search(r'\b(?:to|through|reach\w*|rout\w*)\b|到|路由', prose, re.I)):
        return True
    return bool(_ROUTE_INPUT.search(prose) and
        (_ROUTE_RESELECT.search(prose) or _ROUTE_CANDIDATE.search(prose) and _ROUTE_VALIDATE.search(prose)
         or _ROUTE_HANDOFF.search(prose) or re.search(r'路由|中间阶段|\b(?:routing|intermediate\s+stages?)\b', prose, re.I)))


def input_route_stage_witness(unit):
    """Original behavior plus a named path; Source must independently bind actor.

    A local demonstrative is deliberately unresolved here. A caller may resolve
    only its own exact Source component, never another atom or a method role.
    """
    if not isinstance(unit, str) or not unit.strip():
        return None
    visible = _route_quote_view(unit)
    prose = literal_data_prose(visible, literal_names=False)
    if _ROUTE_META.search(visible) or _RESULT_EPISTEMIC.search(prose):
        return None
    head = _ROUTE_HEAD.match(visible)
    actor = head.group('actor') if head else None
    if actor and not (re.search(r'[.:_]|[a-z][A-Z]', actor) or actor[0].isupper()):
        actor = None
    local_function = bool(re.match(r'^\s*(?:此函数|该函数|该方法|this\s+(?:function|method)\b)', visible, re.I))
    # No receiver/object elsewhere in a body can lend the source head an actor.
    if not actor and not local_function:
        return None
    for clause in re.split(r'[。；;!?！？\n]|\.\s+', visible):
        other = _ROUTE_HEAD.match(clause)
        if other:
            name = other.group('actor')
            if (re.search(r'[.:_]|[a-z][A-Z]', name) or name[0].isupper()) and name.casefold() not in {
                    (actor or '').casefold(), 'it', 'this'}:
                return None
    names = list(dict.fromkeys(re.findall(r'\b[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)+\b|'
        r'\b[A-Za-z_]*[a-z][A-Z][A-Za-z0-9_]*\b', visible, re.ASCII)))
    names = [name for name in names if not name.startswith(('action.', 'self.', 'buffaction.', 'inst.'))
             or ':' in name]
    if not names:
        return None
    source_input = bool(_ROUTE_INPUT.search(prose) or re.search(r'\b(?:lmb|rmb|double-click)\b', visible, re.I))
    kinds = []
    if (any(not prose[match.end():].startswith('的') for match in _positive_route_predicate(_ROUTE_RESELECT, prose, actor, visible))
            and source_input and _ROUTE_CANDIDATE.search(visible)):
        kinds.append('CANDIDATE_RESELECTION')
    if (source_input and _ROUTE_CANDIDATE.search(visible) and any(_positive_route_predicate(_ROUTE_VALIDATE, prose, actor, visible))
            and re.search(r'\bcode\b', visible) and re.search(r'\bmod_?name\b', visible, re.I)):
        kinds.append('CANDIDATE_VALIDATION')
    if (any(_positive_route_predicate(_pattern(r'配置|安装|绑定|\b(?:configures?|installs?|binds?)\b'), prose, actor, visible))
            and re.search(r'回调|\bcallbacks?\b|\b(?:non_preview_cb|preview_cb)\b', visible, re.I)
            and _ROUTE_INPUT.search(prose)):
        kinds.append('REQUEST_CALLBACK_CONFIGURATION')
    if ((any(_positive_route_predicate(_pattern(r'调用\s*(?:self\.locomotor:|locomotor:)?(?:PushAction|PreviewAction)\b'), visible, actor))
            or any(_positive_route_predicate(_ROUTE_HANDOFF, prose, actor, visible)) and re.search(r'\b(?:locomotor|PushAction|PreviewAction)\b', visible, re.I))
            and re.search(r'\b(?:master|mastersim|ismastersim|server|client|authoritative)\b|权威|服务端|客户端|主分发', visible, re.I)):
        kinds.append('ACTION_LOCOMOTOR_DISPATCH')
    if not kinds:
        return None
    return {'stage_kinds': kinds, 'named_paths': names, 'actual_subject': actor,
        'subject_binding': 'ORIGINAL_LITERAL_HEAD' if actor else 'UNRESOLVED_LOCAL_FUNCTION',
        'source_unit': unit, 'reference_only': True, 'final_outcome_proven': False,
        'request_transport_proven': False, 'execution_acceptance_proven': False,
        'generic_contract_complete': False, 'full_method_contract_verified': False,
        'proof_limit': 'ORIGINAL_INTERMEDIATE_ROUTE_STAGE_ONLY',
        'gaps': ['REQUEST_TRANSPORT_NOT_ESTABLISHED_BY_STAGE', 'EXECUTION_ACCEPTANCE_NOT_ESTABLISHED_BY_STAGE',
                 'FINAL_BUSINESS_OUTCOME_NOT_ESTABLISHED_BY_STAGE', 'GENERIC_CHAIN_AND_METHOD_COMPLETENESS_NOT_ESTABLISHED_BY_STAGE']}


@lru_cache(maxsize=2048)
def resource_topics(text):
    value = relation_text(text)
    groups = {
        'task': r'\b(?:tasks?|pendingtasks)\b|任务|延迟效果',
        'subscription': r'\b(?:callbacks?|listeners?|subscriptions?|observers?|watchers?)\b|回调|监听|订阅|观察器',
        'input': r'\b(?:input|focus|handlers?)\b|输入|焦点',
    }
    return frozenset(name for name, pattern in groups.items() if re.search(pattern, value, re.I | re.ASCII))


_RECIPIENT_IDENTIFIER = r'[A-Za-z_]\w*(?:[.:][A-Za-z_]\w*)*'
_RECIPIENT_NAMED_OPERAND = (r'(?:[A-Za-z_]\w*|`[A-Za-z_]\w*`|"[A-Za-z_]\w*"'
                            r"|'[A-Za-z_]\w*'|“[A-Za-z_]\w*”|‘[A-Za-z_]\w*’)")
_LITERAL_RECIPIENT_DELIVERY = _pattern(
    r'(?:(?:而|但|同时|并|随后|然后)[ \t]*)?'
    r'(?:(?P<subject>[A-Za-z_]\w*|它|其|该(?:方法|函数|对象|组件|实体))'
    r'(?:[ \t]+(?:component|object)|组件)?[ \t]*)?'
    r'(?:(?:有效时|在[^，,。；;:：!?！？\n]{1,80}时)[ \t]*)?'
    r'(?:向|对)[ \t]*(?P<recipient>' + _RECIPIENT_IDENTIFIER + r')[ \t]*'
    r'(?:发|派发)[ \t]*(?P<operand>' + _RECIPIENT_NAMED_OPERAND + r')')
_RECIPIENT_CLAUSES = re.compile(
    r'[，,。；;!?！？\n]+|(?<=[.!?])\s+|\s+(?:and|while|but|whereas)\s+', re.I)


def _literal_recipient_clause(unit):
    if not isinstance(unit, str):
        return None
    visible = _data_quote_view(unit, literal_names=True, apostrophes_are_quotes=True)
    match = _LITERAL_RECIPIENT_DELIVERY.fullmatch(visible.strip(' \t\r\n。.!?！？'))
    return match.groupdict() if match else None


def literal_recipient_subject(unit):
    """The literal subject of one complete predicate, never its recipient."""
    predicate = _literal_recipient_clause(unit)
    return predicate['subject'] if predicate else None


def literal_recipient_delivery(unit):
    """One affirmative local delivery predicate, without owner or API proof."""
    if not isinstance(unit, str):
        return False
    # 完整局部谓词才是见证；参数/标签正文、意向前缀和猜测后缀不能借中间的“向…发”补票。
    visible = _data_quote_view(unit, literal_names=True, apostrophes_are_quotes=True)
    return any(_literal_recipient_clause(clause) for clause in _RECIPIENT_CLAUSES.split(visible))


def _recipient_relation(value):
    return bool((_DELIVERY.search(value) and _RECIPIENT_SOURCE.search(value))
                or _CLASSIFIED_TARGET.search(value)
                or _LOCAL_RENDER.search(value) and _RENDER_RELATION.search(value)
                   and re.search(r'\b(?:fx|visual|sound|animation)\b|视觉|音效|动画', value, re.I)
                or _RECEIVED_PROXY.search(value)
                or _CHANNEL.search(value) and (_AUDIENCE.search(value) or _LOCAL_RENDER.search(value))
                   and (_ROUTE_CHOICE.search(value) or _ROUTE_RELATION.search(value)))


@lru_cache(maxsize=8192)
def literal_source_relations(unit):
    """Explicit prose relations, not predicates inferred from identifier names."""
    value = relation_text(unit)
    found = set()
    route_predicate = re.search(
        r'\b(?:sets?|receives?|belongs?|owned|creates?|builds?|renders?|plays?|uses?|follows?)\b'
        r'|设置|为|收到|归|创建|建立|采用|走|播放', unit, re.I)
    if _recipient_relation(value) and route_predicate:
        found.add('audience_scope')
    data_prose = relation_text(_data_quote_view(unit, literal_names=True))
    data_behavior = literal_data_prose(unit, literal_names=False)
    if (_DATA_OBJECT.search(data_prose) and re.search(
            r'\b(?:reads?|loads?|returns?|selects?|chooses?|parses?|processes?|exports?)\b'
            r'|读取|加载|返回|选择|解析|处理|导出', data_behavior, re.I)):
        found.add('data_source_relation')
    if _RETURN_VALUE_USE.search(unit):
        found.add('return_value_consumption')
    return frozenset(found)


def engineering_relations(text, source=False):
    """Original engineering predicates, shared across record families/languages."""
    value = _data_quote_view(text, literal_names=True)
    found = set()
    event = re.search(r'\b(?:events?|listeners?|callbacks?|[A-Za-z_]\w*dirty)\b|事件|监听|回调', value, re.I | re.ASCII)
    if source:
        bridge = (re.search(r'\b(?:PushEvent|dispatch\w*|emits?|forwards?)\b|推送|派发|转发', value, re.I | re.ASCII)
                  and re.search(r'\b(?:parent|owner|consumer|recipient|target)\b|父实体|消费方|接收方', value, re.I | re.ASCII)
                  and re.search(r'\b(?:netvar|classif\w*|payload|calculat\w*|transform\w*|converts?)\b|计算|转换|从.{0,20}(?:读取|取得)', value, re.I | re.ASCII))
        initial = re.search(
            r'(?:初始|默认)(?:值)?\s*(?:为|是|设为|设置为)?\s*(?:[-+]?\d+(?:\.\d+)?|true|false|nil)'
            r'|\b(?:initial|default)\s+(?:values?\s+)?(?:is\s+|of\s+|=\s*)?(?:[-+]?\d+(?:\.\d+)?|true|false|nil)\b', value, re.I | re.ASCII)
    else:
        bridge = re.search(r'\b(?:bridg\w*|forward\w*|rout\w*)\b|桥接|转发|转接', value, re.I | re.ASCII)
        initial_mention = re.search(r'\b(?:initial|first)\s+(?:values?|states?|reads?|renders?|snapshots?)\b|初值|初始(?:值|数值|状态|显示)|初读|首次(?:读|显示|渲染)', value, re.I | re.ASCII)
        default_mention = re.search(r'\bdefault\s+(?:values?|states?)\b|默认(?:值|数值|状态)', value, re.I | re.ASCII)
        default_selection = re.search(r'\b(?:overrid\w*|overwrit\w*|mask\w*|replac\w*|fallback|coalesc\w*)\b|盖掉|覆盖|回退|兜底|替代', value, re.I | re.ASCII)
        initial = initial_mention or default_mention and not default_selection
        literal_declaration = bool(default_mention and not default_selection or initial_mention and re.search(
            r'\b(?:constructor|declar\w*|literal|scalar|numeric)\b|构造|声明|字面|默认数值|初始数值', value, re.I | re.ASCII))
    if event and bridge:
        found.add('event_data_bridge')
    if initial:
        found.add('declared_initial_value')
    if ((not source and initial and not literal_declaration) or source and re.search(
            r'等初值反序列化|\bOnInitialDirtyStates\b|(?:建立|刷新|渲染|读取).{0,12}初始(?:显示|状态|值)'
            r'|(?:初值|初始值).{0,18}(?:显式记录|明确记录)|初始化|\b(?:(?:re)?initializ\w*|initial\s+(?:render|snapshot))\b', value, re.I | re.ASCII)):
        found.add('initial_state_arrangement')
    if ((not source and initial and not literal_declaration) or source and _READ.search(value) and _CURRENT_DATA.search(value) and re.search(
            r'\b(?:initial|first)\b|初读|首次|初次|初始|(?:读(?:取)?|获取|取得|获得|显示|展示|渲染)\s*(?:其|该|的)?初值|\bbefore\b.{0,45}\b(?:subscrib\w*|display\w*|show\w*|render\w*)\b'
            r'|(?:订阅|监听|显示|渲染).{0,8}(?:之前|前).{0,20}(?:读|取得)|(?:读|取得).{0,20}(?:之后|后).{0,10}(?:订阅|显示|渲染)', value, re.I | re.ASCII)):
        found.add('initial_observation')
    resource = re.search(r'\b(?:resources?|providers?|stacks?|budgets?|entity.amount)\b|资源|预算|实体身份|每实体', value, re.I | re.ASCII)
    allocation = re.search(r'\b(?:allocat\w*|count\w*.{0,25}twice|same\s+(?:stack|entity)|remaining\s+budget\w*)\b'
                           r'|分配|按实体身份|剩余预算|重复预算|已分配|去重|组合', value, re.I | re.ASCII)
    allocation_predicate = re.search(r'必须|按实体身份|剩余预算|重复预算|已分配|去重|组合|分配|扣除|记录每实体'
        r'|\b(?:allocates?|allocated|allocating|counts?|counted|deduplicat\w*|remaining\s+budgets?)\b', value, re.I | re.ASCII)
    if resource and allocation and (not source or allocation_predicate):
        found.add('resource_budget_identity')
    query = re.search(r'\b(?:query|queries|plans?|allocation)\b|查询|分配建议|计划', value, re.I | re.ASCII)
    commitment = re.search(r'\b(?:reserv\w*|commit\w*|deduct\w*|payment)\b|预留|占用|扣款|承诺', value, re.I | re.ASCII)
    if query and commitment and (not source or re.search(r'不等于|不是|不能|\b(?:not|never|without)\b', value, re.I | re.ASCII)):
        found.add('query_commitment_boundary')
    registry = re.search(r'\b(?:manager|registry|registries|candidate\s+cache)\b|管理器|注册表|候选缓存', value, re.I | re.ASCII)
    ownership = re.search(r'\b(?:items?|ledger|authoritative|registration|candidates?|state|real)\b|真实物品|真实状态|数量总账|候选|注册|归', value, re.I | re.ASCII)
    ownership_predicate = re.search(r'持有|仍在|归|留给|不是|不等于|(?:仍|并)?有|集中|维护|[→]|->'
        r'|\b(?:holds?|owns?|retains?|belongs?|maintains?|is|are|not)\b', value, re.I | re.ASCII)
    if registry and ownership and (not source or ownership_predicate):
        found.add('registry_state_ownership')
    index_boundary = re.search(
        r'\b(?:scans?|performance|(?:quantity|count|amount)\s+(?:index|ledger)|constant\s+time|linear\s+(?:cost|time))\b'
        r'|扫描|遍历|性能|数量(?:总账|索引)|恒定时间|实际工作量|分批处理|活跃集合', value, re.I | re.ASCII)
    # A cache name alone does not say anything about scan cost or quantity
    # indexing. Persistence, ownership and index limits are separate relations.
    if registry and (index_boundary or not source and re.search(
            r'\b(?:limits?|limitations?|cache|ledger)\b|不等于|不是', value, re.I | re.ASCII)):
        found.add('registry_index_boundary')
    capture_text = text if not source and re.search(r'推出|\b(?:claims?|concludes?|implies)\b', value, re.I | re.ASCII) else value
    capture = re.search(r'\b(?:captur\w*|assign\w*|unused|not\s+used|never\s+used)\b|捕获|赋值|未(?:被)?使用|未被使用', capture_text, re.I | re.ASCII)
    dependency = re.search(r'\b(?:depend\w*|initializ\w*|prerequisite\w*)\b|依赖|初始化|必须有值', value, re.I | re.ASCII)
    if capture and dependency:
        found.add('causal_dependency_evidence')
    revision = re.search(r'\b(?:corrections?|corrected|retract\w*|withdraw\w*|supersed\w*)\b|修正|更正|撤回', value, re.I | re.ASCII)
    if revision and (not source or re.search(r'\b(?:claims?|conclusions?|dependencies|assertions?)\b|判断|主张|结论|依赖|故障', text, re.I | re.ASCII)):
        found.add('claim_revision')
    if ((not source and re.search(r'\b(?:limitations?|evidence|verification|runtime|dedicated)\b|边界|证据|等级|静态|验收', value, re.I | re.ASCII)) or
            source and re.search(r'\b(?:static|untested|unverified|not\s+(?:run|tested|verified))\b|静态|未验证|未测试|尚无|未测', value, re.I | re.ASCII)):
        found.add('record_evidence_limit')
    return frozenset(found)


@lru_cache(maxsize=2048)
def request_relations(text):
    """Question predicates identify concerns, not a proposed cause or remedy."""
    original_text = text
    text = relation_text(text)
    found = set()
    if observer_registration_identity_request(original_text):
        found.add('observer_registration_identity')
    if registration_state_request(original_text):
        found.add('registration_state')
    if readiness_dependency_request(original_text):
        found.add('readiness_dependency')
    if input_route_stage_request(original_text):
        found.add('input_route_stage')
    if result_contract_request(original_text):
        found.add('result_contract')
        if result_input_scenario(original_text):
            found.add('input_request_dispatch')
    if (_VALUE_PHASE.search(text) and _VALUE_CONTENT.search(text) and _VALUE_EVALUATION.search(text)
            or not _REFERENCE_METADATA.search(original_text)
               and _VALUE_TIMING_NOMINAL.search(literal_data_prose(original_text, literal_names=False))):
        found.add('value_evaluation_phase')
    if (not _REFERENCE_METADATA.search(original_text)
            and _OWNER_REQUEST.search(literal_data_prose(original_text, literal_names=False))):
        found.add('ownership_state')
    if _reference_phase_request(original_text):
        found.add('reference_binding_phase')
    if operation_order_request(original_text):
        found.add('operation_order')
    if (_DISTINCTION_REQUEST.search(original_text)
            and 'cancel_task' in _predicate_module.refine_operations(original_text, set())):
        found.add('mechanism_distinction')
    if _READ.search(text) and _CURRENT_DATA.search(text):
        found.add('current_observation')
    if (_EXIT.search(text) and _CONTINUES.search(text) or
            _RESOURCE.search(text) and _RESOURCE_QUESTION.search(text) or
            'cancel_task' in _predicate_module.refine_operations(text, set())):
        found.add('resource_lifetime')
    if _DELIVERY.search(text) and _RECIPIENT_REQUEST.search(text):
        found.add('recipient_routing')
    if _DATA_READ.search(text) and _DATA_OBJECT.search(text) and _asks_data_source(text):
        found.add('data_source')
    if (_RETURN_DATA.search(text) and (_CONSUME.search(text) or _RETURN_VALUE_USE.search(text))
            and not _MATERIAL_OPERAND.search(text)):
        found.add('return_value_flow')
    elif data_consumption(text):
        found.add('data_flow')
    found.update(engineering_relations(original_text, source=False))
    return frozenset(found)


@lru_cache(maxsize=8192)
def source_relations(unit):
    """Every witness is local to the original source unit supplied by the caller."""
    original_unit = unit
    unit = relation_text(unit)
    found = set()
    if _literal_observer_registration_identity(original_unit):
        found.add('observer_registration_identity')
    if _literal_registration_state(original_unit):
        found.add('registration_state')
    if _literal_readiness_dependency(original_unit):
        found.add('readiness_dependency')
    if input_route_stage_witness(original_unit):
        found.add('input_route_stage')
    if result_source_relations(original_unit):
        found.add('result_contract')
    if result_request_dispatch(original_unit):
        found.add('input_request_dispatch')
    if _literal_value_phase(original_unit):
        found.add('value_evaluation_phase')
    if _literal_owner_state(original_unit):
        found.add('ownership_state')
    if _literal_reference_phase(original_unit):
        found.add('reference_binding_phase')
    if _literal_operation_order(original_unit):
        found.add('operation_order')
    if _literal_mechanism_distinction(original_unit):
        found.add('mechanism_distinction')
    if _READ.search(unit) and _CURRENT_DATA.search(unit):
        found.add('current_observation')
    if _RESOURCE.search(unit) and _RESOURCE_CONTROL.search(unit):
        found.add('resource_lifetime')
    if _recipient_relation(unit) or literal_recipient_delivery(original_unit):
        found.add('recipient_routing')
    data_behavior = literal_data_prose(original_unit, literal_names=False)
    data_objects = relation_text(_data_quote_view(original_unit, literal_names=True))
    if _DATA_READ.search(data_behavior) and _DATA_OBJECT.search(data_objects):
        found.add('data_flow')
        if _DATA_SELECTION.search(data_behavior) or read_selection_contexts(original_unit):
            found.add('data_source')
    # 返回值必须是同句消费动作的宾语；普通读取/返回表不能补足消费者关系。
    if _RETURN_VALUE_USE.search(original_unit):
        found.add('return_value_flow')
    found.update(engineering_relations(original_unit, source=True))
    return frozenset(found)
